#!/usr/bin/env python3
"""
配置加载模块
"""
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class BotConfig:
    """单个 Bot 配置"""
    bot_id: str
    machine: str
    role: str
    capabilities: List[str]
    presence_key: str


@dataclass
class RedisConfig:
    """Redis 连接配置"""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    ssl: bool = False
    
    @property
    def url(self) -> str:
        auth = f":{self.password}@" if self.password else ""
        scheme = "rediss" if self.ssl else "redis"
        return f"{scheme}://{auth}{self.host}:{self.port}/{self.db}"


@dataclass
class TelegramConfig:
    """Telegram 配置"""
    bot_token: str
    chat_id: str
    allowed_chat_ids: List[str] = field(default_factory=list)
    fallback_coordinator: Optional[str] = None  # 当 Telegram 不可用时，结果由此 bot 代发


@dataclass
class FederationConfig:
    """联邦配置"""
    bot_config: BotConfig
    redis: RedisConfig
    telegram: TelegramConfig
    streams: Dict[str, str] = field(default_factory=lambda: {
        "tasks": "claw:tasks",
        "results": "claw:results",
        "errors": "claw:errors",
        "presence_prefix": "claw:presence:",
    })
    heartbeat_interval: int = 20
    offline_threshold: int = 3
    consumer_group: str = "claw-workers"
    
    @property
    def presence_key(self) -> str:
        return f"{self.streams['presence_prefix']}{self.bot_config.bot_id}"


def load_config(config_path: str = "federation_config.json") -> FederationConfig:
    """从 JSON 文件加载配置"""
    path = Path(config_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Bot 配置
    bot_data = data.get("bot", {})
    bot_config = BotConfig(
        bot_id=bot_data.get("bot_id", "unknown-bot"),
        machine=bot_data.get("machine", "unknown"),
        role=bot_data.get("role", "coordinator"),
        capabilities=bot_data.get("capabilities", []),
        presence_key=f"claw:presence:{bot_data.get('bot_id', 'unknown')}",
    )
    
    # Redis 配置
    redis_data = data.get("redis", {})
    redis_config = RedisConfig(
        host=redis_data.get("host", "localhost"),
        port=redis_data.get("port", 6379),
        password=redis_data.get("password"),
        db=redis_data.get("db", 0),
        ssl=redis_data.get("ssl", False),
    )
    
    # Telegram 配置
    telegram_data = data.get("telegram", {})
    telegram_config = TelegramConfig(
        bot_token=telegram_data.get("bot_token", ""),
        chat_id=telegram_data.get("chat_id", ""),
        allowed_chat_ids=telegram_data.get("allowed_chat_ids", []),
        fallback_coordinator=telegram_data.get("fallback_coordinator"),
    )
    
    # Streams 配置
    streams = data.get("streams", {
        "tasks": "claw:tasks",
        "results": "claw:results",
        "errors": "claw:errors",
        "presence_prefix": "claw:presence:",
    })
    
    # 其他配置
    heartbeat_interval = data.get("heartbeat_interval", 20)
    offline_threshold = data.get("offline_threshold", 3)
    consumer_group = data.get("consumer_group", "claw-workers")
    
    return FederationConfig(
        bot_config=bot_config,
        redis=redis_config,
        telegram=telegram_config,
        streams=streams,
        heartbeat_interval=heartbeat_interval,
        offline_threshold=offline_threshold,
        consumer_group=consumer_group,
    )


def load_config_from_env() -> FederationConfig:
    """从环境变量加载配置（用于容器/云环境）"""
    bot_id = os.environ.get("BOT_ID")
    if not bot_id:
        raise ValueError("BOT_ID environment variable is required")
    
    bot_config = BotConfig(
        bot_id=bot_id,
        machine=os.environ.get("MACHINE_NAME", "unknown"),
        role=os.environ.get("BOT_ROLE", "coordinator"),
        capabilities=os.environ.get("BOT_CAPABILITIES", "").split(","),
        presence_key=f"claw:presence:{bot_id}",
    )
    
    redis_config = RedisConfig(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", "6379")),
        password=os.environ.get("REDIS_PASSWORD"),
        db=int(os.environ.get("REDIS_DB", "0")),
        ssl=os.environ.get("REDIS_SSL", "false").lower() == "true",
    )
    
    telegram_config = TelegramConfig(
        bot_token=os.environ.get("TELEGRAM_BOT_TOKEN", ""),
        chat_id=os.environ.get("TELEGRAM_CHAT_ID", ""),
        allowed_chat_ids=os.environ.get("TELEGRAM_ALLOWED_CHATS", "").split(","),
    )
    
    return FederationConfig(
        bot_config=bot_config,
        redis=redis_config,
        telegram=telegram_config,
        heartbeat_interval=int(os.environ.get("HEARTBEAT_INTERVAL", "20")),
        offline_threshold=int(os.environ.get("OFFLINE_THRESHOLD", "3")),
    )
