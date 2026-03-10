#!/usr/bin/env python3
"""
任务 Worker
从 Redis Streams 消费任务、claim、执行、返回结果
"""
import asyncio
import json
import logging
import signal
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

import redis.asyncio as redis

from ..config import FederationConfig
from .presence import PresenceManager
from .telegram_client import TelegramClient

logger = logging.getLogger(__name__)


# Lua 脚本：原子 claim 任务
CLAIM_TASK_SCRIPT = """
local task_stream = KEYS[1]
local lock_prefix = KEYS[2]
local consumer_id = KEYS[3]
local task_id = ARGV[1]

-- 检查任务是否存在
local exists = redis.call('EXISTS', task_stream)
if not exists or exists == 0 then
    return {err = 'stream_not_found'}
end

-- 尝试获取任务（使用 XRANGE 获取任务详情）
local task = redis.call('XRANGE', task_stream, task_id, task_id, 'COUNT', 1)
if not task or #task == 0 then
    return {err = 'task_not_found'}
end

-- 检查是否已被 claim
local lock_key = lock_prefix .. task_id
local lock = redis.call('SET', lock_key, consumer_id, 'NX', 'PX', 30000)
if not lock then
    return {err = 'already_claimed'}
end

-- 返回任务数据
return task[1]
"""


class TaskWorker:
    """任务 Worker"""
    
    def __init__(
        self,
        config: FederationConfig,
        task_handler: Optional[Callable[[Dict], Any]] = None,
    ):
        self.config = config
        self.redis: Optional[redis.Redis] = None
        self.presence = PresenceManager(config)
        self.telegram = TelegramClient(config.telegram) if config.telegram.bot_token else None
        self.task_handler = task_handler or self._default_handler
        self.running = False
        self.consumer_id = f"{config.bot_config.bot_id}-{uuid.uuid4().hex[:8]}"
        
        # Fallback coordinator - 当 Telegram 不可用时，结果由此 bot 代发
        self.fallback_coordinator = getattr(config.telegram, 'fallback_coordinator', None)
        
        # 状态
        self.dedup_cache: Dict[str, str] = {}  # task_id -> status
    
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
        
        # 连接其他组件
        await self.presence.connect()
        if self.telegram:
            await self.telegram.connect()
        
        # 确保 consumer group 存在
        await self._ensure_consumer_group()
        
        logger.info(f"Task worker connected: {self.consumer_id}")
    
    async def close(self) -> None:
        """关闭连接"""
        if self.redis:
            await self.redis.close()
        await self.presence.close()
        if self.telegram:
            await self.telegram.close()
    
    async def _ensure_consumer_group(self) -> None:
        """确保 consumer group 存在"""
        streams = self.config.streams
        for stream_name in ["tasks", "results", "errors"]:
            stream_key = streams.get(stream_name, f"claw:{stream_name}")
            try:
                # 尝试创建 group（MKSTREAM 如果不存在则创建）
                await self.redis.xgroup_create(
                    stream_key,
                    self.config.consumer_group,
                    id="0",
                    mkstream=True,
                )
                logger.debug(f"Consumer group ready for {stream_key}")
            except redis.ResponseError as e:
                if "BUSYGROUP" in str(e):
                    # Group 已存在，继续
                    pass
                else:
                    raise
    
    def _is_duplicate(self, task_id: str, origin_bot: str) -> bool:
        """检查是否重复任务"""
        key = f"{task_id}:{origin_bot}"
        return key in self.dedup_cache
    
    def _mark_running(self, task_id: str, origin_bot: str) -> None:
        """标记任务开始"""
        key = f"{task_id}:{origin_bot}"
        self.dedup_cache[key] = "running"
    
    def _mark_completed(self, task_id: str, origin_bot: str) -> None:
        """标记任务完成"""
        key = f"{task_id}:{origin_bot}"
        self.dedup_cache[key] = "completed"
        
        # 清理运行中的任务
        self.dedup_cache.pop(f"{task_id}:{origin_bot}-running", None)
    
    async def _claim_task(self, task_id: str) -> Optional[Dict]:
        """原子 claim 任务"""
        streams = self.config.streams
        
        try:
            # 使用 Lua 脚本实现原子 claim
            result = await self.redis.eval(
                CLAIM_TASK_SCRIPT,
                3,
                streams["tasks"],
                "claw:claim:",
                self.consumer_id,
                task_id,
            )
            
            if isinstance(result, dict) and result.get("err"):
                logger.debug(f"Failed to claim {task_id}: {result['err']}")
                return None
            
            # 解析任务数据
            if result and len(result) >= 2:
                # result[0] = task_id, result[1] = [field, value, ...]
                data = dict(zip(result[1][::2], result[1][1::2]))
                return json.loads(data.get("data", "{}"))
            
            return None
            
        except Exception as e:
            logger.error(f"Claim error for {task_id}: {e}")
            return None
    
    async def _process_task(self, envelope: Dict) -> Dict:
        """处理单个任务"""
        task_id = envelope.get("task_id")
        origin_bot = envelope.get("origin_bot")
        
        # 去重检查
        if self._is_duplicate(task_id, origin_bot):
            logger.info(f"Duplicate task {task_id}, skipping")
            return None
        
        # 标记运行
        self._mark_running(task_id, origin_bot)
        
        try:
            # 更新负载
            # TODO: 与 heartbeat publisher 集成
            
            # 执行任务
            result = await self.task_handler(envelope)
            
            return result
            
        except Exception as e:
            logger.error(f"Task execution error: {e}")
            return {
                "type": "result",
                "task_id": task_id,
                "origin_bot": origin_bot,
                "return_to": envelope.get("assigned_by", origin_bot),
                "status": "error",
                "summary": f"执行出错: {str(e)}",
                "details": {"error": str(e)},
            }
        finally:
            self._mark_completed(task_id, origin_bot)
    
    async def _send_result(self, result: Dict) -> None:
        """发送结果到结果流"""
        streams = self.config.streams
        result_stream = streams.get("results", "claw:results")
        
        # 添加时间戳
        result["timestamps"] = {
            "completed_at": datetime.now(timezone.utc).isoformat()
        }
        
        # 使用 task_id 作为消息 ID（实现幂等）
        message_id = result.get("task_id", "*")
        
        await self.redis.xadd(
            result_stream,
            {"data": json.dumps(result, ensure_ascii=False)},
            id=message_id,
        )
        
        logger.info(f"Result sent for task {result.get('task_id')}")
        
        # 尝试通知（通过 Telegram 或 fallback）
        await self._notify_result(result)
    
    async def _notify_result(self, result: Dict) -> None:
        """通知结果给用户"""
        task_id = result.get("task_id", "unknown")
        summary = result.get("summary", "任务完成")
        status = result.get("status", "ok")
        
        # 构建消息
        emoji = "✅" if status == "ok" else "❌"
        message = f"{emoji} 任务 [{task_id}] {summary}"
        
        # 尝试直接发送 Telegram
        if self.telegram:
            try:
                await self.telegram.send_message(message)
                return
            except Exception as e:
                logger.warning(f"Failed to send Telegram directly: {e}")
        
        # 如果配置了 fallback coordinator，写入待通知队列
        if self.fallback_coordinator:
            notify_stream = "claw:notifications"
            notify_data = {
                "type": "notification",
                "from_bot": self.config.bot_config.bot_id,
                "target_bot": self.fallback_coordinator,
                "message": message,
                "chat_id": self.config.telegram.chat_id,
                "task_id": task_id,
            }
            await self.redis.xadd(notify_stream, {"data": json.dumps(notify_data, ensure_ascii=False)})
            logger.info(f"Notification queued for fallback coordinator: {self.fallback_coordinator}")
    
    async def _send_error(self, envelope: Dict, error: str) -> None:
        """发送错误到错误流"""
        streams = self.config.streams
        error_stream = streams.get("errors", "claw:errors")
        
        error_envelope = {
            "type": "error",
            "task_id": envelope.get("task_id"),
            "origin_bot": envelope.get("origin_bot"),
            "error": error,
            "envelope": envelope,
            "timestamps": {
                "error_at": datetime.now(timezone.utc).isoformat()
            },
        }
        
        await self.redis.xadd(
            error_stream,
            {"data": json.dumps(error_envelope, ensure_ascii=False)},
        )
    
    async def _default_handler(self, envelope: Dict) -> Dict:
        """默认任务处理器"""
        # 解析请求
        request = envelope.get("request", {})
        goal = request.get("goal", "unknown")
        
        logger.info(f"Processing task: {goal}")
        
        # 这里应该调用实际的 OpenClaw 执行逻辑
        # 目前返回模拟结果
        
        return {
            "type": "result",
            "task_id": envelope.get("task_id"),
            "origin_bot": envelope.get("origin_bot"),
            "return_to": envelope.get("assigned_by", envelope.get("origin_bot")),
            "status": "ok",
            "summary": f"任务已完成: {goal}",
            "details": {
                "executed_by": self.config.bot_config.bot_id,
                "result": "模拟执行结果",
            },
        }
    
    async def _handle_message(self, stream: str, message_id: str, data: Dict) -> None:
        """处理接收到的消息"""
        envelope = data.get("envelope", {})
        
        if not envelope:
            return
        
        # Claim 并处理
        task_id = envelope.get("task_id")
        if not task_id:
            return
        
        claimed = await self._claim_task(task_id)
        if not claimed:
            return
        
        # 处理任务
        result = await self._process_task(claimed)
        
        if result:
            # 发送结果
            await self._send_result(result)
            
            # ACK 消息
            await self.redis.xack(
                stream,
                self.config.consumer_group,
                message_id,
            )
            
            # 可选：在 Telegram 通知
            if self.telegram:
                await self.telegram.send_message(
                    f"✅ 任务完成: {result.get('summary', '')}"
                )
    
    async def run(self) -> None:
        """运行 worker 循环"""
        self.running = True
        streams = self.config.streams
        task_stream = streams.get("tasks", "claw:tasks")
        
        while self.running:
            try:
                # 阻塞读取新任务
                messages = await self.redis.xreadgroup(
                    groupname=self.config.consumer_group,
                    consumername=self.consumer_id,
                    streams={task_stream: ">"},
                    count=1,
                    block=5000,  # 5 秒超时
                )
                
                if not messages:
                    continue
                
                for stream_messages in messages:
                    stream_name = stream_messages[0]
                    for msg in stream_messages[1]:
                        message_id = msg[0]
                        data = json.loads(msg[1].get("data", "{}"))
                        
                        await self._handle_message(stream_name, message_id, data)
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(1)  # 短暂等待后重试
    
    def stop(self) -> None:
        """停止 worker"""
        self.running = False
        logger.info("Task worker stopped")


async def run_worker(config: FederationConfig) -> None:
    """运行任务 worker（独立进程入口）"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    worker = TaskWorker(config)
    
    # 信号处理
    def signal_handler(sig, frame):
        logger.info("Received signal, shutting down...")
        worker.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await worker.connect()
        logger.info(f"Starting task worker: {config.bot_config.bot_id}")
        await worker.run()
    except Exception as e:
        logger.error(f"Worker error: {e}")
    finally:
        await worker.close()


if __name__ == "__main__":
    import sys
    from ..config import load_config
    
    config_path = sys.argv[1] if len(sys.argv) > 1 else "federation_config.json"
    config = load_config(config_path)
    asyncio.run(run_worker(config))
