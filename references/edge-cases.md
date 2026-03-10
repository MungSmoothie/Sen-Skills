# 边界情况与故障处理

本文档补充 SKILL.md 中未涵盖的边界情况与故障场景。

---

## 1. 并发与竞态条件

### 1.1 任务 Claim 竞态

问题：两个 worker bot 同时 claim 同一任务。

```python
# 使用 Lua 脚本实现原子 claim
CLAIM_SCRIPT = """
local task = redis.call('XREADGROUP', 'GROUP', 'claw-workers', KEYS[1], 
                        'COUNT', '1', 'STREAMS', 'claw:tasks', '>')
if not task then return nil end
local task_id = task[1][2][1][1]
-- 尝试设置 claim 锁
local lock = redis.call('SET', 'claw:claim:' .. task_id, KEYS[2], 
                       'NX', 'PX', 30000)
if lock then
    return task_id
else
    return nil
end
"""
```

**处理方式**：
- 使用 Redis 原子操作或分布式锁
- 未成功 claim 的 bot 继续轮询
- 设置 claim 超时（30s），防止 worker 离线后锁住任务

### 1.2 结果回传竞态

问题：任务完成后，多个路径同时尝试回传结果。

**处理方式**：
- 使用 `claw:claim:<task_id>` 锁，claim 时一并确定返回目标
- 结果回传前检查 `return_to` 是否仍在线
- 离线则写入 `claw:results` 后结束，由 coordinator 轮询发现

---

## 2. 消息可靠性

### 2.1 Consumer Group 配置

```bash
# 创建 consumer group
XGROUP CREATE claw:tasks claw-workers 0 MKSTREAM
XGROUP CREATE claw:results claw-workers 0 MKSTREAM
XGROUP CREATE claw:errors claw-workers 0 MKSTREAM
```

**关键配置**：
- `MKSTREAM`：组不存在时自动创建
- 每个 bot 有唯一的 `consumer_id`（如 `lab-bot-hostname`）
- 使用 `XREADGROUP GROUP <group> <consumer>` 而非 `XREAD`

### 2.2 消息 ACK 流程

```python
async def process_task(envelope: dict) -> None:
    try:
        # 1. 解析并执行任务
        result = await execute_task(envelope)
        
        # 2. 发送结果
        await send_result(result)
        
        # 3. ACK 消息（从 pending 列表移除）
        redis.xack('claw:tasks', 'claw-workers', envelope['task_id'])
        
    except Exception as e:
        # 4. 处理失败，写入错误流并 ACK
        await send_error(envelope, str(e))
        redis.xack('claw:tasks', 'claw-workers', envelope['task_id'])
```

**语义**：至少一次（at-least-once）
- 任务执行成功 + ACK = 完成
- 任务执行成功 + 未 ACK = 重启后可能被重新执行
- 幂等设计：结果流使用 `task_id` 作为消息 ID，重复写入会被覆盖

### 2.3 死信队列（DLQ）

```bash
# 创建死信流
XADD claw:tasks:dlq * '{"reason": "max_retries_exceeded", ...}'
```

**触发条件**：
- TTL 耗尽（hop_count > 4）
- 重试次数超过阈值（如 3 次）
- 无法解析的 envelope
- 未知错误类型

---

## 3. 状态同步

### 3.1 离线判定阈值

```python
# heartbeat 配置
HEARTBEAT_INTERVAL = 20  # 秒
OFFLINE_THRESHOLD = 3    # 连续多少次心跳缺失算离线

def is_online(presence: dict) -> bool:
    last_seen = datetime.fromisoformat(presence['last_seen'])
    elapsed = (datetime.now() - last_seen).total_seconds()
    return elapsed < (HEARTBEAT_INTERVAL * OFFLINE_THRESHOLD)
```

**配置建议**：
- 心跳间隔 20s，离线阈值 3 次 → 60s 内无心跳视为离线
- 可根据网络状况调整

### 3.2 去重缓存持久化

```python
# 使用 Redis 哈希存储去重状态
DEDUP_KEY = 'claw:dedup'

def is_duplicate(task_id: str, origin_bot: str) -> bool:
    key = f'{task_id}:{origin_bot}'
    exists = redis.hexists(DEDUP_KEY, key)
    return exists

def mark_completed(task_id: str, origin_bot: str, ttl_minutes: int = 15) -> None:
    key = f'{task_id}:{origin_bot}'
    redis.hset(DEDUP_KEY, key, 'completed')
    redis.expire(DEDUP_KEY, ttl_minutes * 60)
```

**缓存策略**：
- Running 缓存：任务完成前持续存在
- Completion 缓存：完成后保留 5-15 分钟
- 使用 Redis 哈希 + 过期时间，自动清理

---

## 4. 错误处理

### 4.1 结果回传失败

```python
async def send_result(result: dict) -> bool:
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # 写入结果流
            redis.xadd('claw:results', '*', result)
            return True
        except RedisError as e:
            if attempt == max_retries - 1:
                # 最后一次失败，写入死信
                redis.xadd('claw:errors', '*', {
                    'type': 'result_delivery_failed',
                    'task_id': result['task_id'],
                    'error': str(e)
                })
                return False
            await asyncio.sleep(2 ** attempt)  # exponential backoff
```

### 4.2 任务执行超时

```python
TASK_TIMEOUT = 300  # 5 分钟

async def execute_with_timeout(envelope: dict) -> dict:
    try:
        return await asyncio.wait_for(
            execute_task(envelope),
            timeout=TASK_TIMEOUT
        )
    except asyncio.TimeoutError:
        return {
            'type': 'result',
            'status': 'timeout',
            'summary': '任务执行超时',
            'details': {'envelope': envelope}
        }
```

### 4.3 Exponential Backoff 重试

```python
import random

async def retry_with_backoff(func, max_retries: int = 3) -> Any:
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = (2 ** attempt) + random.uniform(0, 1)
            await asyncio.sleep(delay)
```

---

## 5. 安全

### 5.1 Redis 认证

```python
# redis.conf 配置
requirepass your_redis_password

# 客户端连接
redis = redis.Redis(
    host='redis.example.com',
    password='your_redis_password',
    ssl=True
)
```

### 5.2 消息来源验证

```python
import hmac
import hashlib

SECRET_KEY = os.environ['FEDERATION_SECRET']

def sign_envelope(envelope: dict) -> str:
    payload = json.dumps(envelope, sort_keys=True)
    return hmac.new(SECRET_KEY.encode(), payload.encode(), 'sha256').hexdigest()

def verify_envelope(envelope: dict, signature: str) -> bool:
    expected = sign_envelope(envelope)
    return hmac.compare_digest(expected, signature)

# 在 envelope 中添加签名
envelope['signature'] = sign_envelope(envelope)
```

### 5.3 Telegram 消息验证

```python
# 验证消息来自授权的群
ALLOWED_CHAT_IDS = ['-1001234567890']

def verify_telegram_update(update: dict) -> bool:
    chat = update.get('message', {}).get('chat', {})
    return str(chat.get('id')) in ALLOWED_CHAT_IDS
```

---

## 6. 边界情况

### 6.1 所有 Bot 都离线

```python
async def handle_all_offline(request: dict) -> None:
    # 1. 检查在线 bot 列表
    online = await get_online_bots()
    
    if not online:
        # 2. 本地执行（如果合理）
        if can_local_execute(request):
            await execute_locally(request)
        else:
            # 3. 返回错误
            await telegram.send_message(
                '当前没有在线的联邦 bot，无法处理请求。请稍后再试。'
            )
```

### 6.2 Worker 重启恢复

```python
# 启动时恢复未完成的任务
async def recover_pending_tasks(consumer_id: str) -> None:
    # 读取 pending 列表
    pending = redis.xreadgroup(
        'GROUP', 'claw-workers', consumer_id,
        'STREAMS', 'claw:tasks', '0'
    )
    
    for stream in pending:
        for message in stream[1]:
            task_id = message[0]
            envelope = json.loads(message[1][b'data'])
            
            # 检查任务状态
            claim = redis.get(f'claw:claim:{task_id}')
            if claim == consumer_id:
                # 重新执行或标记为需要恢复
                await handle_task_recovery(envelope)
```

### 6.3 Telegram 消息丢失补偿

```python
# 使用 Redis 记录最后发送的消息 ID
LAST_MESSAGE_KEY = 'claw:telegram:last_message'

async def send_telegram_message(chat_id: str, text: str) -> None:
    # 获取最后消息 ID，用于编辑而非重复发送
    last_msg_id = redis.get(LAST_MESSAGE_KEY)
    
    if last_msg_id:
        try:
            # 尝试编辑最后一条消息
            result = await telegram.edit_message_text(
                chat_id=chat_id,
                message_id=int(last_msg_id),
                text=text
            )
        except TelegramError:
            # 编辑失败，发送新消息
            result = await telegram.send_message(chat_id=chat_id, text=text)
    else:
        result = await telegram.send_message(chat_id=chat_id, text=text)
    
    redis.set(LAST_MESSAGE_KEY, result['message_id'])
```

### 6.4 网络分区

```python
async def handle_network_partition() -> None:
    """
    网络分区检测与处理
    """
    # 检测 Redis 连接
    try:
        redis.ping()
    except:
        # 进入只读/本地模式
        await enter_local_mode()
    
    # 定期检测远端 presence
    while True:
        await asyncio.sleep(30)
        known_bots = await fetch_remote_presence()
        if not known_bots:
            logger.warning('网络分区：无法发现远端 bot')
            await telegram.send_message(
                '网络连接不稳定，协作能力降级。'
            )
```

---

## 7. 监控指标

### 7.1 关键指标

```python
# 需要监控的指标
METRICS = {
    # 队列指标
    'queue_length': 'XLEN claw:tasks',
    'pending_count': 'XPENDING claw:tasks claw-workers',
    
    # 处理指标
    'tasks_completed': 'INCR claw:metrics:completed',
    'tasks_failed': 'INCR claw:metrics:failed',
    'tasks_timeout': 'INCR claw:metrics:timeout',
    
    # 延迟指标
    'task_latency': 'HINCRBYFLOAT claw:metrics:latency',  # 记录处理时间
    
    # 在线指标
    'bots_online': 'SCARD claw:presence',
}
```

### 7.2 健康检查

```python
async def health_check() -> dict:
    checks = {
        'redis': await check_redis(),
        'telegram': await check_telegram(),
        'presence': await check_presence(),
        'queue': await check_queue(),
    }
    
    return {
        'healthy': all(c['ok'] for c in checks.values()),
        'checks': checks
    }
```

---

## 8. 完整任务状态机

```
                    +--------+
                    | PENDING|  (在队列中)
                    +----+---+
                         | claim
                         v
                    +----+---+
          +----------> | CLAIMED|  (被 claim，尚未开始)
          |           +----+---+
          |                | start
          |                v
          |           +----+---+
          |           | RUNNING|  (执行中)
          |           +----+---+
          |                | complete
    retry|                v
          |           +----+---+
          +------+----| COMPLETE|  (完成)
                    +----+---+
                         |
           +-------------+-------------+
           |             |             |
           v             v             v
       +------+     +------+     +--------+
       | OK   |     |ERROR|     |TIMEOUT |
       +------+     +------+     +--------+
           |             |             |
           v             v             v
      -> DELIVERED  -> DLQ      -> RETRY/DLQ
```

---

## 9. 快速参考表

| 场景 | 检测方式 | 处理策略 |
|------|----------|----------|
| 并发 claim | 分布式锁 | 原子操作 + claim 超时 |
| 消息丢失 | Consumer group pending | 启动时恢复 + 幂等设计 |
| 结果回传失败 | 重试 + DLQ | exponential backoff |
| Worker 重启 | pending 列表 | 启动扫描 + 状态恢复 |
| 所有离线 | presence 检查 | 本地执行 / 报错 |
| 网络分区 | Redis ping | 降级为本地模式 |
| 心跳离线 | 连续缺失 3 次 | 标记 offline |
