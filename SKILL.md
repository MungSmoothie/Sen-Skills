---
name: openclaw-federation
description: 构建并维护由多个独立 openclaw gateway 组成的联邦协作体系，这些实例在同一个 telegram 群中协作，并通过 redis 进行可靠协调。用于 chatgpt 需要搭建、配置或排查多 bot openclaw 团队协作时，尤其适合每台机器各自运行独立 bot、bot 之间需要感知彼此存在、在不要求用户手动指定目标 bot 的情况下自动路由任务、使用心跳与任务队列、防止 bot 间循环触发，并保持 telegram 作为可见聊天界面、redis 作为可靠控制通道的场景。
---

构建由多个独立 OpenClaw 实例组成的联邦。把每台机器都视为独立的 gateway、bot、workspace 和 state 目录。不要合并状态。

## 默认架构
除非用户明确要求别的方案，否则使用下面这套：

- 所有 OpenClaw bot 共用一个 Telegram 群。
- 所有机器都能通过 tailnet 访问同一个 Redis。
- 三台机器安装相同的 federation skill。
- 每个任务都会有一个协调 bot，但协调者由上下文动态决定，不是永久写死。
- Telegram 是展示层。
- Redis 是控制面。

## 需要同时实现的能力
必须一并实现以下五类行为：

1. 允许所有 bot 在同一个 Telegram 群中共存。
2. 允许 bot 在群里发送人类可见的协作消息。
3. 允许 bot 通过 Redis 交换可靠的任务消息。
4. 允许 bot 发布心跳和能力摘要。
5. 防止 bot 之间出现失控循环。

## 推荐队列选择
默认优先选 Redis。

优先使用 Redis 的场景：
- 机器数量不多
- 更看重部署简单，而不是最理想的队列语义
- 用户已经在跑 Docker、NAS 或家庭实验环境

只有在用户明确更看重更轻量的 pub/sub、天然的 fan-out，或者计划把小型家庭实验联邦继续扩展时，再推荐 NATS 代替 Redis。

除非用户另有要求，任务消息使用 Redis Streams，心跳与 presence 使用 Redis 键、哈希或 pub/sub。

## 部署流程
按下面顺序推进。

1. 检查当前拓扑。
   - 识别机器名、Telegram bot 身份，以及一个共享的 Redis 地址。
   - 确认所有 bot 都在同一个 Telegram 群。
   - 确认每个 OpenClaw 实例仍然是独立 gateway，拥有独立 state。

2. 分配运行时角色。
   - 根据机器上下文推断每个 bot 的角色。
   - 默认优先使用 `coordinator`、`ops`、`lab` 这类合理角色。
   - 正常任务下不要要求用户手动点名目标 bot。

3. 建立 presence。
   - 每个 bot 每 15 到 30 秒发布一次心跳。
   - 心跳内容至少包含 bot id、角色、能力、busy 标记、last_seen 和健康摘要。
   - 连续错过多个心跳周期后，把 bot 视为离线。

4. 建立路由。
   - 根据能力匹配、健康状态、busy 状态和最近活跃度选择最合适的 bot。
   - 默认优先选择当前最空闲且能力匹配的 bot。
   - 如果没有健康的远端 bot，保留本地回退路径。

5. 建立任务消息封装。
   - 对每个 task、result、error 和 heartbeat 使用稳定的结构化消息。
   - 每个被委派的任务都必须生成 `task_id`。
   - 消息中要携带原始用户请求、约束和期望结果形态。

6. 建立防循环保护。
   - 增加 `task_id`、`parent_task_id`、`origin_bot`、`assigned_by`、`hop_count` 和 `ttl`。
   - 拒绝处理 ttl 已耗尽、重复 task id，或在没有状态变化的情况下回弹到同一个 bot 的消息。

7. 建立 Telegram 行为规则。
   - 群里优先发送接单确认、进度摘要、求助信息和最终结果。
   - 机器间的详细 payload 不要直接发到 Telegram。
   - 只输出对人类有帮助的可见群消息。

8. 测试联邦行为。
   - 验证所有 bot 的 presence 都能出现。
   - 验证在不显式指定 bot 的情况下可以自动选择合适执行者。
   - 验证结果回传、超时处理和防循环是否生效。

## 路由策略
除非用户另行提供规则，否则默认采用下面这套。

### 能力分桶
根据机器角色和机器上的工具来推断能力。

- `ops`：docker、compose、文件、存储、服务状态、媒体、宿主机维护
- `lab`：浏览器、编码、实验、抓取、临时任务
- `coordinator`：任务拆解、路由、结果综合、面向人类的回复

一个 bot 可以同时声明多个能力。

### 选择规则
对每个进入系统的请求执行下面流程：

1. 先判断当前 bot 是否可以本地完成。
2. 如果本地完成是合理的，再把本地适配度和远端候选 bot 做比较。
3. 只有当另一个 bot 明显更合适、更健康或更空闲时，才进行委派。
4. 当前 bot 继续担任面向用户的协调者，负责可见更新。
5. 结果先回给协调者，再由协调者在 Telegram 中汇总。

除非联邦内没有健康且有能力的候选 bot，否则不要让用户手动选择 bot。

## Redis 模型
使用下面这些逻辑通道和存储。

### Streams
- `claw:tasks`
- `claw:results`
- `claw:errors`

### Presence
- `claw:presence:<bot_id>` 使用带过期时间的键或哈希
- 可选 pub/sub 主题：`claw:presence-events`

### 可选锁
- `claw:locks:<task_id>` 用于 claim 或去重

## 消息模板
默认使用下面这些 schema。

### Task envelope
```json
{
  "type": "task",
  "task_id": "uuid",
  "parent_task_id": null,
  "origin_bot": "cloud-bot",
  "assigned_by": "cloud-bot",
  "target_bot": "auto",
  "role_hint": "ops",
  "capability_hint": ["docker", "storage"],
  "hop_count": 0,
  "ttl": 4,
  "priority": "normal",
  "telegram": {
    "chat_id": "shared-group-id",
    "thread_id": null,
    "reply_to": null
  },
  "request": {
    "goal": "check plex playback lag",
    "constraints": ["do not restart services unless needed"],
    "expected_output": "brief diagnosis with next action"
  },
  "timestamps": {
    "created_at": "iso8601"
  }
}
```

### Result envelope
```json
{
  "type": "result",
  "task_id": "uuid",
  "parent_task_id": null,
  "origin_bot": "nas-bot",
  "return_to": "cloud-bot",
  "status": "ok",
  "summary": "disk latency is high on volume2",
  "details": {
    "findings": [],
    "next_action": "inspect the download container"
  },
  "timestamps": {
    "completed_at": "iso8601"
  }
}
```

### Heartbeat envelope
```json
{
  "type": "heartbeat",
  "bot_id": "lab-bot",
  "role": "lab",
  "capabilities": ["browser", "code", "scrape"],
  "busy": false,
  "health": "ok",
  "load": 0.2,
  "last_seen": "iso8601"
}
```

## Telegram 行为规则
始终一致地应用下面规则。

- 只有在群回复受 mention 控制，或有其他明确约束时，才让所有 bot 共同待在一个群里。
- 用户发起请求时，优先让一个协调 bot 先开口。
- worker bot 只发简短确认和精炼结论。
- 永远不要把原始 Redis payload 直接转发到 Telegram。
- Telegram 用于增强可见性，不是路由状态的唯一事实来源。

## 防循环规则
始终启用下面这些保护。

- 拒绝处理 `ttl` 已耗尽的 envelope。
- 每发生一次委派，都增加 `hop_count`。
- 对已经完成、正在运行或最近刚见过的 `task_id` 忽略重复消息。
- 除返回结果外，避免立即把任务弹回给发送方。
- 同一个任务如果没有状态迁移，不要重复委派。
- 每个 bot 都维护一个短生命周期的去重缓存。

## 故障处理
明确处理故障。

- 如果没有有能力且在线的 bot，在安全且合理时优先本地执行。
- 如果委派任务超时，在 Telegram 里发一条简短更新，然后重试一次或本地做更小范围的兜底检查。
- 如果 Redis 不可用，优雅降级为仅靠 Telegram 的可见协作，并明确说明当前路由置信度下降。
- 如果 Telegram 可用但 Redis presence 已过期，把远端 bot 视为未知状态，而不是健康状态。

## 输出要求
当使用这个 skill 来实现或修改联邦时，至少产出下面这些内容：

1. 所有 bot 的简短角色映射。
2. 选定的路由策略。
3. Redis 的 key 和 stream 布局。
4. 每台机器需要做的配置变更。
5. 一个简短测试计划，至少包含一次委派场景、一次超时场景和一次防循环场景。

## 使用附带资源
按需查阅这些文件：

- `references/deployment.md`：部署步骤和配置清单
- `references/message-schemas.md`：消息格式和路由规则
- `references/examples.md`：具体行为示例
- `references/edge-cases.md`：边界情况与故障处理（并发、可靠性、恢复）
- `scripts/render_federation_defaults.py`：生成统一的 bot id、角色、stream 名称和入门 JSON 配置
- `scripts/validate_envelope.py`：校验 task、result 和 heartbeat payload
- `scripts/runtime/`: Python 运行时实现（包含心跳、任务 worker、路由）

需要稳定脚手架或确定性校验时调用脚本；否则优先直接推理处理。

## 快速启动
```bash
# 1. 安装依赖
pip install -r scripts/runtime/requirements.txt

# 2. 复制配置模板
cp scripts/runtime/example_config.json federation_config.json

# 3. 修改配置（填写自己的 bot token、redis 地址等）
vim federation_config.json

# 4. 启动
python -m scripts.runtime federation_config.json
```

## 故障处理补充
### Telegram 不可达 Fallback
如果 bot 无法直接访问 Telegram API（如被墙），可以配置 `fallback_coordinator`：
```json
{
  "telegram": {
    "bot_token": "xxx",
    "chat_id": "-100xxx",
    "fallback_coordinator": "cloud-coordinator"
  }
}
```
当 worker 完成任务但无法发送 Telegram 时，结果会写入 `claw:results` 流，由 coordinator 代发消息。
