# 消息结构

## 通用必填字段
每个 envelope 都要携带足够的信息，以便追踪、去重和路由。

- `type`
- `task_id`
- `origin_bot`
- `hop_count`
- `ttl`
- `timestamps` 对象

## Task 路由说明
默认使用 `target_bot: "auto"`。只有在读取 live presence 和 capability 数据后，才把它解析成具体 bot。

可选提示字段：
- `role_hint`
- `capability_hint`
- `priority`
- `telegram.chat_id`

## Result 路由说明
结果消息必须始终包含返回目标。

- `return_to`
- `status`
- `summary`
- 可选 `details`

## Heartbeat 说明
Heartbeat 要足够轻量而且频率稳定。

推荐字段：
- `bot_id`
- `role`
- `capabilities`
- `busy`
- `health`
- `load`
- `last_seen`

## 去重规则
满足下面全部条件时，把任务视为重复：
- 相同的 `task_id`
- 相同的 `origin_bot`
- 任务仍在运行，或刚刚完成不久

建议的最近窗口：
- running cache：持续到任务完成
- completion cache：5 到 15 分钟

## TTL 规则
每次发生委派，都递减 `ttl`。当 `ttl <= 0` 时，拒绝继续委派。
