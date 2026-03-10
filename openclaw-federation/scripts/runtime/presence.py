#!/usr/bin/env python3
"""
Presence 管理器
读取和管理其他 bot 的在线状态
"""
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

import redis.asyncio as redis

from ..config import FederationConfig, BotConfig

logger = logging.getLogger(__name__)


@dataclass
class BotPresence:
    """Bot 在线状态"""
    bot_id: str
    role: str
    capabilities: List[str]
    busy: bool
    health: str
    load: float
    last_seen: datetime
    is_online: bool = True


class PresenceManager:
    """Presence 管理器"""
    
    def __init__(self, config: FederationConfig):
        self.config = config
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self) -> None:
        """连接到 Redis"""
        self.redis = redis.Redis(
            host=self.config.redis.host,
            port=self.config.redis.port,
            password=self.config.redis.password,
            db=self.config.redis.db,
            decode_responses=True,
        )
        await self.redis.ping()
        logger.info("Presence manager connected to Redis")
    
    async def close(self) -> None:
        """关闭连接"""
        if self.redis:
            await self.redis.close()
    
    async def get_all_presences(self) -> Dict[str, BotPresence]:
        """获取所有 bot 的在线状态"""
        if not self.redis:
            return {}
        
        prefix = self.config.streams["presence_prefix"]
        pattern = f"{prefix}*"
        
        try:
            keys = await self.redis.keys(pattern)
            presences = {}
            
            for key in keys:
                data = await self.redis.hgetall(key)
                if not data:
                    continue
                
                bot_id = data.get("bot_id", key.replace(prefix, ""))
                last_seen = datetime.fromisoformat(data.get("last_seen", datetime.now(timezone.utc).isoformat()))
                
                # 检查是否离线
                elapsed = (datetime.now(timezone.utc) - last_seen).total_seconds()
                threshold = self.config.heartbeat_interval * self.config.offline_threshold
                is_online = elapsed < threshold
                
                presence = BotPresence(
                    bot_id=bot_id,
                    role=data.get("role", "unknown"),
                    capabilities=json.loads(data.get("capabilities", "[]")),
                    busy=data.get("busy", "false") == "true",
                    health=data.get("health", "unknown"),
                    load=float(data.get("load", "0.0")),
                    last_seen=last_seen,
                    is_online=is_online,
                )
                presences[bot_id] = presence
            
            return presences
        except Exception as e:
            logger.error(f"Failed to get presences: {e}")
            return {}
    
    async def get_online_bots(self, exclude_self: bool = True) -> List[BotPresence]:
        """获取所有在线 bot"""
        all_presences = await self.get_all_presences()
        
        online = [
            p for p in all_presences.values()
            if p.is_online and (not exclude_self or p.bot_id != self.config.bot_config.bot_id)
        ]
        
        return online
    
    async def get_bots_by_capability(
        self, 
        capability: str,
        only_online: bool = True,
        exclude_busy: bool = False,
    ) -> List[BotPresence]:
        """根据能力筛选 bot"""
        bots = await self.get_all_presences()
        
        filtered = []
        for bot in bots.values():
            # 排除自己
            if exclude_self and bot.bot_id == self.config.bot_config.bot_id:
                continue
            
            # 在线检查
            if only_online and not bot.is_online:
                continue
            
            # 能力匹配
            if capability in bot.capabilities:
                # 忙碌检查
                if exclude_busy and bot.busy:
                    continue
                filtered.append(bot)
        
        return filtered
    
    async def get_bots_by_role(
        self,
        role: str,
        only_online: bool = True,
        exclude_busy: bool = False,
    ) -> List[BotPresence]:
        """根据角色筛选 bot"""
        bots = await self.get_all_presences()
        
        filtered = []
        for bot in bots.values():
            if exclude_self and bot.bot_id == self.config.bot_config.bot_id:
                continue
            
            if only_online and not bot.is_online:
                continue
            
            if bot.role == role:
                if exclude_busy and bot.busy:
                    continue
                filtered.append(bot)
        
        return filtered
    
    async def get_best_worker(
        self,
        capability_hint: Optional[str] = None,
        role_hint: Optional[str] = None,
    ) -> Optional[BotPresence]:
        """获取最合适的 worker bot
        
        优先级：
        1. 在线 + 健康
        2. 匹配 capability_hint 或 role_hint
        3. 负载最低
        4. 排除自己
        """
        all_bots = await self.get_all_presences()
        
        candidates = []
        for bot in all_bots.values():
            # 排除自己
            if bot.bot_id == self.config.bot_config.bot_id:
                continue
            
            # 必须在线且健康
            if not bot.is_online or bot.health != "ok":
                continue
            
            # 匹配提示
            if capability_hint and capability_hint not in bot.capabilities:
                continue
            if role_hint and bot.role != role_hint:
                continue
            
            # 不超过负载阈值
            if bot.load >= 1.0:
                continue
            
            candidates.append(bot)
        
        if not candidates:
            return None
        
        # 选择负载最低的
        candidates.sort(key=lambda b: b.load)
        return candidates[0]
    
    async def is_self_online(self) -> bool:
        """检查自己是否在线"""
        if not self.redis:
            return False
        
        key = self.config.presence_key
        data = await self.redis.hgetall(key)
        
        if not data:
            return False
        
        last_seen = datetime.fromisoformat(data.get("last_seen", ""))
        elapsed = (datetime.now(timezone.utc) - last_seen).total_seconds()
        threshold = self.config.heartbeat_interval * self.config.offline_threshold
        
        return elapsed < threshold


async def test_presence(config: FederationConfig) -> None:
    """测试 presence 功能"""
    manager = PresenceManager(config)
    await manager.connect()
    
    try:
        # 获取所有 bot
        all_bots = await manager.get_all_presences()
        print(f"Total bots: {len(all_bots)}")
        
        for bot_id, presence in all_bots.items():
            print(f"  {bot_id}: {presence.role} - {'online' if presence.is_online else 'offline'}")
        
        # 获取在线 bot
        online = await manager.get_online_bots()
        print(f"Online bots: {len(online)}")
        
        # 测试能力筛选
        if online:
            first = online[0]
            capability = first.capabilities[0] if first.capabilities else None
            if capability:
                by_cap = await manager.get_bots_by_capability(capability)
                print(f"Bots with capability '{capability}': {len(by_cap)}")
        
    finally:
        await manager.close()


if __name__ == "__main__":
    import asyncio
    import sys
    from ..config import load_config
    
    logging.basicConfig(level=logging.INFO)
    
    config_path = sys.argv[1] if len(sys.argv) > 1 else "federation_config.json"
    config = load_config(config_path)
    asyncio.run(test_presence(config))
