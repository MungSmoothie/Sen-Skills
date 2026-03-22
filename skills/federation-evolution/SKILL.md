---
name: federation-evolution
description: 联邦协同进化 - 让学到的经验在联邦内同步共享。一个 bot 学到的技能/教训可以实时同步给其他联邦成员，实现知识共享。
tags: [federation, sync, evolution, knowledge-sharing]
requires:
  - openclaw-federation
---

# 🧬 联邦协同进化

让联邦内的 bot 能够共享学习成果，一个 bot 学会的东西，其他 bot 也能瞬间掌握。

## 核心概念

### 经验 Capsule
学到的经验封装为标准格式：
```json
{
  "capsule_id": "uuid",
  "type": "skill|lesson|pattern|fix",
  "title": "简短描述",
  "content": "经验详细内容",
  "tags": ["标签"],
  "source_bot": "二狗",
  "created_at": "2026-03-11T10:00:00Z",
  "ttl": 86400  // 24小时内有效
}
```

### 同步机制
- 使用 Redis Pub/Sub 发布经验
- 使用 Redis Stream 记录历史（用于审计和重放）
- 各 bot 订阅自己的专属频道 `claw:evolution:<bot_id>`

## 使用方式

### 手动同步经验
```
同步经验给 doro：学会了 Redis TTL 检查逻辑
```
或者
```
把 "处理过期任务跳过" 这个经验同步给 doro-lab
```

### 查询已有经验
```
查看二狗最近学了啥
```

### 自动同步（可选）
当检测到重要学习成果时，自动推送给联邦成员。

## Redis 模型

### Pub/Sub 频道
- `claw:evolution:broadcast` - 广播给所有 bot
- `claw:evolution:<bot_id>` - 指定 bot 专属频道

### Stream（历史记录）
- `claw:evolution:capsules` - 经验胶囊流

## 依赖

需要先配置好 `openclaw-federation`，确保：
- Redis 可访问
- 各 bot 已注册到联邦

## 实现脚本

- `scripts/runtime/evolution_sync.py` - 同步核心逻辑
- `scripts/runtime/evolution_listener.py` - 监听并接收经验
