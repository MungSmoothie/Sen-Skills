#!/usr/bin/env python3
"""
心跳发布器
定时向 Redis 发送心跳，让其他 bot 感知到自己在线
"""
import asyncio
import json
import logging
import signal
import sys
import time
from datetime import datetime, timezone
from typing import Optional

import redis.asyncio as redis

from ..config import FederationConfig

logger = logging.getLogger(__name__)


class HeartbeatPublisher:
    """心跳发布器"""
    
    def __init__(self, config: FederationConfig):
        self.config = config
        self.redis: Optional[redis.Redis] = None
        self.running = False
        self._health = "ok"
        self._load = 0.0
    
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
        logger.info(f"Heartbeat publisher connected to Redis")
    
    async def close(self) -> None:
        """关闭连接"""
        if self.redis:
            await self.redis.close()
    
    def set_health(self, health: str) -> None:
        """设置健康状态"""
        self._health = health
    
    def set_load(self, load: float) -> None:
        """设置负载 (0.0 - 1.0)"""
        self._load = max(0.0, min(1.0, load))
    
    async def publish_heartbeat(self) -> bool:
        """发布一次心跳"""
        if not self.redis:
            return False
        
        bot = self.config.bot_config
        now = datetime.now(timezone.utc).isoformat()
        
        heartbeat = {
            "type": "heartbeat",
            "bot_id": bot.bot_id,
            "role": bot.role,
            "capabilities": bot.capabilities,
            "busy": self._load > 0.7,
            "health": self._health,
            "load": self._load,
            "last_seen": now,
        }
        
        # 使用哈希存储 presence，过期时间 = 3 * heartbeat_interval
        key = self.config.presence_key
        ttl = self.config.heartbeat_interval * self.config.offline_threshold + 10
        
        try:
            # 写入哈希
            await self.redis.hset(key, mapping=heartbeat)
            # 设置过期时间
            await self.redis.expire(key, ttl)
            # 可选：发布 presence 事件
            await self.redis.publish(
                "claw:presence-events",
                json.dumps({"event": "heartbeat", **heartbeat})
            )
            logger.debug(f"Published heartbeat: {bot.bot_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish heartbeat: {e}")
            return False
    
    async def run(self) -> None:
        """运行心跳发布循环"""
        self.running = True
        
        # 初始发布
        await self.publish_heartbeat()
        
        while self.running:
            await asyncio.sleep(self.config.heartbeat_interval)
            if self.running:
                await self.publish_heartbeat()
    
    def stop(self) -> None:
        """停止心跳"""
        self.running = False
        logger.info("Heartbeat publisher stopped")


async def run_heartbeat(config: FederationConfig) -> None:
    """运行心跳发布器（独立进程入口）"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    publisher = HeartbeatPublisher(config)
    
    # 信号处理
    def signal_handler(sig, frame):
        logger.info("Received signal, shutting down...")
        publisher.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await publisher.connect()
        logger.info(f"Starting heartbeat publisher for {config.bot_config.bot_id}")
        await publisher.run()
    except Exception as e:
        logger.error(f"Heartbeat publisher error: {e}")
        sys.exit(1)
    finally:
        await publisher.close()


if __name__ == "__main__":
    from ..config import load_config
    import sys
    
    config_path = sys.argv[1] if len(sys.argv) > 1 else "federation_config.json"
    config = load_config(config_path)
    asyncio.run(run_heartbeat(config))
