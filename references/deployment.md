# 部署清单

## 1. 实例隔离
保持每个 OpenClaw 实例完全独立。

- 独立 gateway 端口
- 独立 state 目录
- 独立 workspace
- 独立 Telegram bot token
- 共用同一个 Telegram 群
- 共用同一个 Redis 地址

## 2. 三机环境的推荐角色
除非从机器的实际用途能明显看出更好的划分，否则默认使用：

- 云服务器 -> coordinator
- NAS 宿主机 -> ops
- NAS 虚拟机 -> lab

## 3. Redis 建议
任务流默认使用 Redis Streams：

- `claw:tasks`：任务请求
- `claw:results`：成功结果
- `claw:errors`：失败结果

presence 使用带过期时间的哈希或键：

- `claw:presence:<bot_id>`

## 4. 最小运行时检查表
每台机器都要满足：

1. 安装相同的 skill
2. bot 能识别自己的角色和 bot id
3. 能连通 Redis
4. 按固定间隔发布 heartbeat
5. 能订阅或轮询 task claim
6. 处理前先校验 envelope
7. 在 Telegram 群里输出简短状态

## 5. 路由检查表
在委派任务前：

1. 检查当前 live presence
2. 按能力做过滤
3. 去掉不健康或离线的 bot
4. 优先选择 busy 分数最低者
5. 除非已有更适合的协调者绑定了当前对话，否则让当前 bot 继续担任 coordinator

## 6. Telegram 检查表
把群当作可见控制台。

适合发到群里的消息：
- 简短接单确认
- 哪个 bot 接走了任务
- 精简进度更新
- 最终结果摘要

不适合发到群里的内容：
- 原始队列 payload
- 重复的内部重试信息
- 高频心跳

## 7. 恢复清单
如果 Redis 故障：
- 停止发起依赖可靠路由的新委派
- 明确说明协作已降级
- 继续把面向用户的进度发在 Telegram 里
- 在安全时优先本地执行
