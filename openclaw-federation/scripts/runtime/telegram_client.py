#!/usr/bin/env python3
"""
Telegram 客户端
处理 Telegram 群消息收发
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

import aiohttp

from ..config import TelegramConfig

logger = logging.getLogger(__name__)


class TelegramClient:
    """Telegram 客户端"""
    
    def __init__(self, config: TelegramConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = f"https://api.telegram.org/bot{config.bot_token}"
    
    async def connect(self) -> None:
        """创建 HTTP session"""
        self.session = aiohttp.ClientSession()
        # 测试连接
        me = await self.get_me()
        logger.info(f"Telegram client connected: {me}")
    
    async def close(self) -> None:
        """关闭 session"""
        if self.session:
            await self.session.close()
    
    async def _request(self, method: str, **kwargs) -> Dict:
        """发送 API 请求"""
        if not self.session:
            await self.connect()
        
        url = f"{self.base_url}/{method}"
        
        async with self.session.post(url, **kwargs) as response:
            data = await response.json()
            
            if not data.get("ok"):
                error = data.get("description", "Unknown error")
                logger.error(f"Telegram API error: {error}")
                raise Exception(f"Telegram API error: {error}")
            
            return data.get("result", {})
    
    async def get_me(self) -> Dict:
        """获取 bot 信息"""
        return await self._request("getMe")
    
    async def send_message(
        self,
        text: str,
        chat_id: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        parse_mode: str = "Markdown",
    ) -> Dict:
        """发送消息到群"""
        chat_id = chat_id or self.config.chat_id
        
        if not chat_id:
            raise ValueError("chat_id is required")
        
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id
        
        return await self._request("sendMessage", json=payload)
    
    async def edit_message_text(
        self,
        text: str,
        chat_id: str,
        message_id: int,
        parse_mode: str = "Markdown",
    ) -> Dict:
        """编辑已发送的消息"""
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        
        return await self._request("editMessageText", json=payload)
    
    async def answer_callback_query(self, callback_query_id: str, text: str = None) -> Dict:
        """回答回调查询"""
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        
        return await self._request("answerCallbackQuery", json=payload)
    
    async def get_updates(
        self,
        offset: int = None,
        limit: int = 100,
        timeout: int = 0,
    ) -> List[Dict]:
        """获取更新（轮询方式）"""
        payload = {
            "limit": limit,
            "timeout": timeout,
        }
        
        if offset:
            payload["offset"] = offset
        
        return await self._request("getUpdates", json=payload)
    
    async def get_webhook_info(self) -> Dict:
        """获取 webhook 信息"""
        return await self._request("getWebhookInfo")
    
    async def set_webhook(self, url: str, secret_token: str = None) -> Dict:
        """设置 webhook"""
        payload = {"url": url}
        
        if secret_token:
            payload["secret_token"] = secret_token
        
        return await self._request("setWebhook", json=payload)
    
    async def delete_webhook(self) -> Dict:
        """删除 webhook"""
        return await self._request("deleteWebhook")
    
    def validate_message(self, update: Dict) -> bool:
        """验证消息是否来自授权的群"""
        if not update:
            return False
        
        # 从 message 或 edited_message 获取
        message = update.get("message") or update.get("edited_message")
        
        if not message:
            return False
        
        chat = message.get("chat", {})
        chat_id = str(chat.get("id"))
        
        # 检查是否在允许的群列表中
        if self.config.allowed_chat_ids:
            return chat_id in self.config.allowed_chat_ids
        
        # 否则检查是否匹配配置的 chat_id
        return chat_id == self.config.chat_id
    
    def extract_command(self, message: Dict) -> Optional[Dict]:
        """从消息中提取命令"""
        entities = message.get("entities", [])
        
        for entity in entities:
            if entity.get("type") == "bot_command":
                text = message.get("text", "")
                offset = entity.get("offset", 0)
                length = entity.get("length", 0)
                command = text[offset:offset + length]
                
                # 提取参数
                parts = text[offset + length:].strip().split()
                
                return {
                    "command": command,
                    "args": parts,
                }
        
        return None
    
    async def send_status(self, status: str, chat_id: str = None) -> None:
        """发送状态消息（快捷方法）"""
        bot_name = self.config.bot_token.split(":")[0] if ":" in self.config.bot_token else "bot"
        
        await self.send_message(
            f"🤖 *{bot_name}*: {status}",
            chat_id=chat_id,
        )


class TelegramWebhookHandler:
    """Webhook 处理器"""
    
    def __init__(self, client: TelegramClient):
        self.client = client
    
    async def handle_update(self, update: Dict) -> Optional[Dict]:
        """处理单个更新"""
        # 验证来源
        if not self.client.validate_message(update):
            logger.warning("Message from unauthorized chat ignored")
            return None
        
        # 提取命令
        message = update.get("message")
        if not message:
            return None
        
        command = self.client.extract_command(message)
        
        if command:
            return {
                "type": "command",
                "command": command["command"],
                "args": command["args"],
                "message": message,
            }
        
        # 普通消息
        return {
            "type": "message",
            "text": message.get("text", ""),
            "message": message,
        }


async def test_telegram(config: TelegramConfig) -> None:
    """测试 Telegram 客户端"""
    client = TelegramClient(config)
    
    try:
        await client.connect()
        me = await client.get_me()
        print(f"Bot info: {me}")
        
        # 发送测试消息
        result = await client.send_message("Hello from federation test!")
        print(f"Message sent: {result['message_id']}")
        
    finally:
        await client.close()


if __name__ == "__main__":
    import asyncio
    import sys
    from ..config import load_config
    
    logging.basicConfig(level=logging.INFO)
    
    # 快速测试
    config = TelegramConfig(
        bot_token=sys.argv[1] if len(sys.argv) > 1 else "",
        chat_id=sys.argv[2] if len(sys.argv) > 2 else "",
    )
    
    if not config.bot_token or not config.chat_id:
        print("Usage: python telegram_client.py <bot_token> <chat_id>")
        sys.exit(1)
    
    asyncio.run(test_telegram(config))
