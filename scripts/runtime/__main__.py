#!/usr/bin/env python3
"""
OpenClaw Federation 运行时
整合所有组件的主入口
"""
import asyncio
import logging
import signal
import sys
from typing import Optional

from .config import FederationConfig, load_config
from .heartbeat import HeartbeatPublisher
from .presence import PresenceManager
from .router import Router
from .task_worker import TaskWorker
from .telegram_client import TelegramClient, TelegramWebhookHandler

logger = logging.getLogger(__name__)


class FederationRuntime:
    """联邦运行时（整合所有组件）"""
    
    def __init__(self, config: FederationConfig):
        self.config = config
        
        # 组件
        self.heartbeat: Optional[HeartbeatPublisher] = None
        self.presence: Optional[PresenceManager] = None
        self.router: Optional[Router] = None
        self.worker: Optional[TaskWorker] = None
        self.telegram: Optional[TelegramClient] = None
        self.webhook_handler: Optional[TelegramWebhookHandler] = None
        
        # 状态
        self.running = False
    
    async def start(self) -> None:
        """启动所有组件"""
        logger.info(f"Starting federation runtime: {self.config.bot_config.bot_id}")
        
        # 初始化各组件
        self.heartbeat = HeartbeatPublisher(self.config)
        self.presence = PresenceManager(self.config)
        self.router = Router(self.config)
        
        # 连接
        await self.heartbeat.connect()
        await self.presence.connect()
        await self.router.connect()
        
        # Telegram（如果配置了）
        if self.config.telegram.bot_token:
            self.telegram = TelegramClient(self.config.telegram)
            await self.telegram.connect()
            self.webhook_handler = TelegramWebhookHandler(self.telegram)
        
        # Task Worker
        self.worker = TaskWorker(self.config)
        await self.worker.connect()
        
        self.running = True
        logger.info("All components started")
    
    async def stop(self) -> None:
        """停止所有组件"""
        logger.info("Stopping federation runtime...")
        self.running = False
        
        if self.worker:
            self.worker.stop()
            await self.worker.close()
        
        if self.heartbeat:
            self.heartbeat.stop()
            await self.heartbeat.close()
        
        if self.telegram:
            await self.telegram.close()
        
        if self.router:
            await self.router.close()
        
        if self.presence:
            await self.presence.close()
        
        logger.info("All components stopped")
    
    async def run_forever(self) -> None:
        """运行主循环"""
        # 启动所有组件
        await self.start()
        
        # 保持运行
        while self.running:
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
        
        # 清理
        await self.stop()
    
    def handle_telegram_webhook(self, update: dict) -> None:
        """处理 Telegram webhook 更新"""
        if not self.webhook_handler:
            return
        
        # 异步处理
        asyncio.create_task(self._process_telegram_update(update))
    
    async def _process_telegram_update(self, update: dict) -> None:
        """处理 Telegram 更新"""
        result = await self.webhook_handler.handle_update(update)
        
        if not result:
            return
        
        if result["type"] == "command":
            await self._handle_command(result)
        elif result["type"] == "message":
            await self._handle_message(result)
    
    async def _handle_command(self, result: dict) -> None:
        """处理命令"""
        command = result["command"]
        args = result["args"]
        message = result["message"]
        
        chat_id = str(message["chat"]["id"])
        
        # 处理 /status 命令
        if command == "/status":
            online = await self.presence.get_online_bots()
            status = f"🤖 *Status Report*\n\n"
            status += f"*Bot*: {self.config.bot_config.bot_id}\n"
            status += f"*Role*: {self.config.bot_config.role}\n"
            status += f"*Online bots*: {len(online)}\n"
            
            for bot in online:
                status += f"  - {bot.bot_id} ({bot.role}, load: {bot.load:.0%})\n"
            
            await self.telegram.send_message(status, chat_id=chat_id)
        
        # 处理 /delegate 命令
        elif command == "/delegate":
            if not args:
                await self.telegram.send_message(
                    "用法: /delegate <目标角色> <任务描述>",
                    chat_id=chat_id
                )
                return
            
            role = args[0]
            goal = " ".join(args[1:])
            
            # 创建任务
            from .router import create_task_envelope
            envelope = await create_task_envelope(
                self.config,
                goal=goal,
                role_hint=role,
            )
            
            # 路由
            decision = await self.router.route_and_delegate(envelope)
            
            if decision == "delegated":
                await self.telegram.send_message(
                    f"✅ 任务已委派给 {role} bot",
                    chat_id=chat_id
                )
            else:
                await self.telegram.send_message(
                    f"📍 将在本地执行任务",
                    chat_id=chat_id
                )
        
        # 处理 /help 命令
        elif command == "/help":
            help_text = """
*Available Commands*

/status - 显示联邦状态
/delegate <role> <task> - 委派任务
/health - 健康检查
/help - 显示帮助
"""
            await self.telegram.send_message(help_text, chat_id=chat_id)
    
    async def _handle_message(self, result: dict) -> None:
        """处理普通消息"""
        # TODO: 实现基于消息内容自动创建任务
        pass


def create_runtime_from_env() -> FederationRuntime:
    """从环境变量创建运行时"""
    config = load_config_from_env()
    return FederationRuntime(config)


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw Federation Runtime")
    parser.add_argument("--config", default="federation_config.json", help="Config file path")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()
    
    # 设置日志
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # 加载配置
    config = load_config(args.config)
    
    # 创建并运行
    runtime = FederationRuntime(config)
    
    # 信号处理
    loop = asyncio.get_event_loop()
    
    def signal_handler(sig, frame):
        logger.info("Received signal, shutting down...")
        runtime.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        loop.run_until_complete(runtime.run_forever())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
