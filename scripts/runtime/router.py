#!/usr/bin/env python3
"""
路由器
根据能力、健康状态、负载选择最合适的 bot 执行任务
"""
import json
import logging
from typing import Any, Dict, List, Optional

import redis.asyncio as redis

from ..config import FederationConfig
from .presence import BotPresence, PresenceManager

logger = logging.getLogger(__name__)


class Router:
    """任务路由器"""
    
    def __init__(self, config: FederationConfig):
        self.config = config
        self.redis: Optional[redis.Redis] = None
        self.presence = PresenceManager(config)
    
    async def connect(self) -> None:
        """连接到 Redis"""
        self.redis = redis.Redis(
            host=self.config.redis.host,
            port=self.config.redis.port,
            password=self.config.redis.password,
            db=self.config.redis.db,
            decode_responses=True,
        )
        await self.presence.connect()
        logger.info("Router connected")
    
    async def close(self) -> None:
        """关闭连接"""
        if self.redis:
            await self.redis.close()
        await self.presence.close()
    
    async def can_local_execute(self, request: Dict) -> bool:
        """判断当前 bot 是否可以本地执行"""
        bot = self.config.bot_config
        
        # 检查能力匹配
        capability_hint = request.get("capability_hint")
        if capability_hint and capability_hint not in bot.capabilities:
            return False
        
        # 检查角色匹配
        role_hint = request.get("role_hint")
        if role_hint and bot.role != role_hint:
            return False
        
        # 检查负载
        # TODO: 读取当前负载状态
        # return current_load < 0.9
        
        return True
    
    async def select_target(
        self,
        capability_hint: Optional[str] = None,
        role_hint: Optional[str] = None,
        exclude_bot: Optional[str] = None,
    ) -> Optional[str]:
        """选择最合适的目标 bot
        
        策略：
        1. 优先选择匹配能力的在线 bot
        2. 选择负载最低的
        3. 排除指定的 bot
        4. 如果没有合适的远端 bot，返回 None（表示本地执行）
        """
        # 获取最佳 worker
        best = await self.presence.get_best_worker(
            capability_hint=capability_hint,
            role_hint=role_hint,
        )
        
        if not best:
            logger.info("No suitable remote bot found")
            return None
        
        # 排除指定 bot
        if exclude_bot and best.bot_id == exclude_bot:
            logger.info(f"Best bot {best.bot_id} is excluded")
            return None
        
        logger.info(f"Selected target: {best.bot_id} (role={best.role}, load={best.load})")
        return best.bot_id
    
    async def delegate_task(self, envelope: Dict, target_bot: str) -> bool:
        """委派任务到目标 bot
        
        将任务写入任务流，并设置 target_bot 为具体 bot id
        """
        streams = self.config.streams
        task_stream = streams.get("tasks", "claw:tasks")
        
        # 更新 envelope
        delegated = envelope.copy()
        delegated["target_bot"] = target_bot
        delegated["assigned_by"] = self.config.bot_config.bot_id
        delegated["hop_count"] = envelope.get("hop_count", 0) + 1
        
        # TTL 检查
        ttl = envelope.get("ttl", 4)
        if delegated["hop_count"] >= ttl:
            logger.warning(f"Task {envelope.get('task_id')} TTL exhausted")
            return False
        
        # 生成唯一消息 ID（包含 hop_count 实现幂等）
        task_id = envelope.get("task_id")
        message_id = f"{task_id}-{delegated['hop_count']}"
        
        # 写入任务流
        await self.redis.xadd(
            task_stream,
            {"data": json.dumps(delegated, ensure_ascii=False)},
            id=message_id,
        )
        
        logger.info(f"Task delegated to {target_bot}: {task_id}")
        return True
    
    async def route_and_delegate(self, envelope: Dict) -> str:
        """路由并委派任务
        
        返回：
        - 'local': 本地执行
        - 'delegated': 已委派给远端
        - 'failed': 委派失败
        """
        request = envelope.get("request", {})
        origin_bot = envelope.get("origin_bot")
        assigned_by = envelope.get("assigned_by", origin_bot)
        
        # 1. 检查是否可以本地完成
        can_local = await self.can_local_execute(request)
        
        # 2. 获取远端候选
        target = await self.select_target(
            capability_hint=request.get("capability_hint"),
            role_hint=envelope.get("role_hint"),
            exclude_bot=origin_bot,  # 不委派回发送方
        )
        
        # 3. 决策
        if target and not can_local:
            # 必须委派
            success = await self.delegate_task(envelope, target)
            return "delegated" if success else "failed"
        
        elif target and can_local:
            # 比较本地和远端
            # TODO: 获取本地负载进行比较
            # 如果远端明显更合适，委派
            
            # 默认本地优先
            return "local"
        
        elif not target and can_local:
            # 没有远端 bot，本地执行
            return "local"
        
        else:
            # 没有合适的 bot
            logger.warning("No suitable bot available")
            return "failed"
    
    async def is_healthy_federation(self) -> bool:
        """检查联邦是否健康（至少有 coordinator 在线）"""
        online = await self.presence.get_online_bots()
        
        if not online:
            return False
        
        # 至少有一个 coordinator
        has_coordinator = any(bot.role == "coordinator" for bot in online)
        
        return has_coordinator


async def create_task_envelope(
    config: FederationConfig,
    goal: str,
    constraints: List[str] = None,
    expected_output: str = None,
    role_hint: str = None,
    capability_hint: List[str] = None,
    priority: str = "normal",
    parent_task_id: str = None,
) -> Dict:
    """创建任务 envelope"""
    import uuid
    from datetime import datetime, timezone
    
    return {
        "type": "task",
        "task_id": str(uuid.uuid4()),
        "parent_task_id": parent_task_id,
        "origin_bot": config.bot_config.bot_id,
        "assigned_by": config.bot_config.bot_id,
        "target_bot": "auto",
        "role_hint": role_hint,
        "capability_hint": capability_hint or [],
        "hop_count": 0,
        "ttl": 4,
        "priority": priority,
        "telegram": {
            "chat_id": config.telegram.chat_id,
            "thread_id": None,
            "reply_to": None,
        },
        "request": {
            "goal": goal,
            "constraints": constraints or [],
            "expected_output": expected_output,
        },
        "timestamps": {
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    }


async def test_router(config: FederationConfig) -> None:
    """测试路由器"""
    router = Router(config)
    await router.connect()
    
    try:
        # 测试选择
        target = await router.select_target(role_hint="ops")
        print(f"Selected ops bot: {target}")
        
        # 测试健康检查
        healthy = await router.is_healthy_federation()
        print(f"Federation healthy: {healthy}")
        
    finally:
        await router.close()


if __name__ == "__main__":
    import asyncio
    import sys
    from ..config import load_config
    
    logging.basicConfig(level=logging.INFO)
    
    config_path = sys.argv[1] if len(sys.argv) > 1 else "federation_config.json"
    config = load_config(config_path)
    asyncio.run(test_router(config))
