#!/usr/bin/env python3
"""
联邦协同进化 - 经验同步核心模块

功能：
1. 发布经验到联邦
2. 监听并接收经验
3. 自动合并到本地 memory
"""
import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

import redis.asyncio as redis


class EvolutionSync:
    """经验同步器"""
    
    def __init__(
        self,
        redis_url: str = "redis://127.0.0.1:6379",
        bot_id: str = None,
    ):
        self.redis_url = redis_url
        self.bot_id = bot_id or os.environ.get("BOT_ID", "unknown")
        self.redis: Optional[redis.Redis] = None
        
        # 频道
        self.broadcast_channel = "claw:evolution:broadcast"
        self.private_channel = f"claw:evolution:{self.bot_id}"
        
        # Stream
        self.capsule_stream = "claw:evolution:capsules"
    
    async def connect(self) -> None:
        """连接到 Redis"""
        # 解析 URL
        host = self.redis_url.replace("redis://", "").split(":")[0]
        port = int(self.redis_url.replace("redis://", "").split(":")[1].split("/")[0])
        
        self.redis = redis.Redis(
            host=host,
            port=port,
            decode_responses=True,
        )
        await self.redis.ping()
        print(f"✅ 连接到 Redis: {self.redis_url}")
    
    async def close(self) -> None:
        """关闭连接"""
        if self.redis:
            await self.redis.close()
    
    async def publish_capsule(
        self,
        capsule_type: str,
        title: str,
        content: str,
        tags: List[str] = None,
        target_bots: List[str] = None,
    ) -> str:
        """发布经验胶囊"""
        capsule_id = str(uuid.uuid4())
        
        capsule = {
            "capsule_id": capsule_id,
            "type": capsule_type,  # skill, lesson, pattern, fix
            "title": title,
            "content": content,
            "tags": tags or [],
            "source_bot": self.bot_id,
            "target_bots": target_bots or ["broadcast"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "ttl": 86400,  # 24小时
        }
        
        # 写入 Stream（历史记录）
        await self.redis.xadd(
            self.capsule_stream,
            {"data": json.dumps(capsule, ensure_ascii=False)},
            id=capsule_id,
        )
        
        # 广播到指定频道
        if target_bots and "broadcast" in target_bots:
            await self.redis.publish(self.broadcast_channel, json.dumps(capsule, ensure_ascii=False))
        
        # 发送到指定 bot
        if target_bots:
            for bot in target_bots:
                if bot != "broadcast":
                    channel = f"claw:evolution:{bot}"
                    await self.redis.publish(channel, json.dumps(capsule, ensure_ascii=False))
        
        print(f"📤 已发布经验胶囊 [{capsule_id}]: {title}")
        return capsule_id
    
    async def subscribe_and_listen(self, on_receive=None) -> None:
        """订阅频道并监听经验"""
        pubsub = self.redis.pubsub()
        
        # 订阅广播频道和私人频道
        await pubsub.subscribe(self.broadcast_channel, self.private_channel)
        print(f"📡 监听频道: {self.broadcast_channel}, {self.private_channel}")
        
        try:
            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                
                try:
                    capsule = json.loads(message["data"])
                except json.JSONDecodeError:
                    continue
                
                # 跳过自己发布的
                if capsule.get("source_bot") == self.bot_id:
                    continue
                
                print(f"📥 收到经验胶囊 [{capsule['capsule_id']}]: {capsule['title']}")
                
                # 回调处理
                if on_receive:
                    await on_receive(capsule)
                else:
                    # 默认写入本地 memory
                    await self._save_to_memory(capsule)
        finally:
            await pubsub.unsubscribe(self.broadcast_channel, self.private_channel)
    
    async def _save_to_memory(self, capsule: Dict) -> None:
        """将经验保存到本地 memory"""
        memory_dir = os.path.expanduser("~/.openclaw/workspace/memory")
        os.makedirs(memory_dir, exist_ok=True)
        
        # 按类型分文件
        capsule_type = capsule.get("type", "general")
        memory_file = os.path.join(memory_dir, f"{capsule_type}s.md")
        
        # 追加内容
        timestamp = capsule.get("created_at", "")[:10]
        content = f"""

## [{timestamp}] {capsule['title']}

来源: {capsule['source_bot']}
类型: {capsule['type']}
标签: {', '.join(capsule.get('tags', []))}

{capsule['content']}
---
"""
        
        with open(memory_file, "a", encoding="utf-8") as f:
            f.write(content)
        
        print(f"💾 已保存到 {memory_file}")
    
    async def get_capsules(self, limit: int = 10) -> List[Dict]:
        """获取历史经验胶囊"""
        results = await self.redis.xrevrange(
            self.capsule_stream,
            "+",
            "-",
            count=limit,
        )
        
        capsules = []
        for item in results:
            try:
                data = json.loads(item[1]["data"])
                capsules.append(data)
            except (json.JSONDecodeError, KeyError):
                continue
        
        return capsules


async def main():
    """测试入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="联邦协同进化")
    parser.add_argument("--action", choices=["publish", "listen", "list"], default="listen")
    parser.add_argument("--bot-id", default=os.environ.get("BOT_ID", "test-bot"))
    parser.add_argument("--redis-url", default="redis://127.0.0.1:6379")
    parser.add_argument("--type", default="lesson")
    parser.add_argument("--title", default="测试经验")
    parser.add_argument("--content", default="这是测试内容")
    parser.add_argument("--tags", nargs="*", default=[])
    parser.add_argument("--target", default="broadcast")
    
    args = parser.parse_args()
    
    sync = EvolutionSync(
        redis_url=args.redis_url,
        bot_id=args.bot_id,
    )
    await sync.connect()
    
    try:
        if args.action == "publish":
            targets = args.target.split(",") if args.target != "broadcast" else ["broadcast"]
            await sync.publish_capsule(
                capsule_type=args.type,
                title=args.title,
                content=args.content,
                tags=args.tags,
                target_bots=targets,
            )
        
        elif args.action == "list":
            capsules = await sync.get_capsules()
            for c in capsules:
                print(f"- [{c['type']}] {c['title']} (from {c['source_bot']})")
        
        elif args.action == "listen":
            print("开始监听经验...")
            await sync.subscribe_and_listen()
    
    finally:
        await sync.close()


if __name__ == "__main__":
    asyncio.run(main())
