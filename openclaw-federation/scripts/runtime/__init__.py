#!/usr/bin/env python3
"""
OpenClaw Federation Runtime

使用示例：

    from runtime import FederationRuntime
    from config import load_config
    
    config = load_config("config.json")
    runtime = FederationRuntime(config)
    asyncio.run(runtime.run_forever())

或使用命令行：

    python -m runtime --config config.json
"""
from .config import (
    FederationConfig,
    BotConfig,
    RedisConfig,
    TelegramConfig,
    load_config,
    load_config_from_env,
)
from .heartbeat import HeartbeatPublisher, run_heartbeat
from .presence import BotPresence, PresenceManager
from .router import Router, create_task_envelope
from .task_worker import TaskWorker, run_worker
from .telegram_client import TelegramClient, TelegramWebhookHandler

__version__ = "0.1.0"

__all__ = [
    # Config
    "FederationConfig",
    "BotConfig", 
    "RedisConfig",
    "TelegramConfig",
    "load_config",
    "load_config_from_env",
    # Components
    "HeartbeatPublisher",
    "PresenceManager",
    "BotPresence",
    "Router",
    "TaskWorker",
    "TelegramClient",
    "TelegramWebhookHandler",
    # Entry points
    "run_heartbeat",
    "run_worker",
    "create_task_envelope",
]
