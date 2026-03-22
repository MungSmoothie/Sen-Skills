#!/bin/bash
# 联邦协同进化 - 经验同步 (Bash 版)
# 适合轻量级 bot 使用

REDIS_HOST="${REDIS_HOST:-127.0.0.1}"
REDIS_PORT="${REDIS_PORT:-6379}"
BOT_ID="${BOT_ID:-unknown}"
BROADCAST_CHANNEL="claw:evolution:broadcast"
PRIVATE_CHANNEL="claw:evolution:$BOT_ID"
CAPSULE_STREAM="claw:evolution:capsules"

publish_capsule() {
    local capsule_type="$1"
    local title="$2"
    local content="$3"
    local tags="${4:-}"
    local target="${5:-broadcast}"
    
    local capsule_id=$(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid)
    local created_at=$(date -Iseconds)
    
    # 构建 JSON
    local capsule=$(cat <<EOF
{
  "capsule_id": "$capsule_id",
  "type": "$capsule_type",
  "title": "$title",
  "content": "$content",
  "tags": [$tags],
  "source_bot": "$BOT_ID",
  "target_bots": ["$target"],
  "created_at": "$created_at",
  "ttl": 86400
}
EOF
)
    
    # 写入 Stream
    redis-cli -h $REDIS_HOST -p $REDIS_PORT XADD $CAPSULE_STREAM "*" data "$capsule" > /dev/null
    
    # 发布到频道
    if [ "$target" = "broadcast" ]; then
        redis-cli -h $REDIS_HOST -p $REDIS_PORT PUBLISH "$BROADCAST_CHANNEL" "$capsule" > /dev/null
    else
        redis-cli -h $REDIS_HOST -p $REDIS_PORT PUBLISH "claw:evolution:$target" "$capsule" > /dev/null
    fi
    
    echo "📤 已发布经验胶囊: $title"
}

listen_capsules() {
    echo "📡 监听经验胶囊..."
    
    # 使用 redis-cli 订阅
    redis-cli -h $REDIS_HOST -p $REDIS_PORT SUBSCRIBE "$BROADCAST_CHANNEL" "$PRIVATE_CHANNEL" | \
    while read -r line; do
        if echo "$line" | grep -q '"message"'; then
            capsule=$(echo "$line" | grep -oP '\{"capsule_id".*?\}' | head -1)
            source_bot=$(echo "$capsule" | grep -o '"source_bot":"[^"]*"' | cut -d'"' -f4)
            
            # 跳过自己
            if [ "$source_bot" = "$BOT_ID" ]; then
                continue
            fi
            
            title=$(echo "$capsule" | grep -o '"title":"[^"]*"' | cut -d'"' -f4)
            content=$(echo "$capsule" | grep -o '"content":"[^"]*"' | cut -d'"' -f4)
            
            echo "📥 收到经验: $title"
            echo "   $content"
            
            # 保存到本地 memory
            memory_dir="$HOME/.openclaw/workspace/memory"
            mkdir -p "$memory_dir"
            echo "
## $(date +%Y-%m-%d) $title

来源: $source_bot
$content
---" >> "$memory_dir/lessons.md"
        fi
    done
}

# 根据参数执行
case "$1" in
    publish)
        publish_capsule "$2" "$3" "$4" "$5" "$6"
        ;;
    listen)
        listen_capsules
        ;;
    *)
        echo "用法: $0 {publish|listen}"
        echo "  publish <type> <title> <content> [tags] [target]"
        echo "  listen"
        ;;
esac
