#!/bin/bash
# cron-send-newsletter.sh — 每天早上9点发送日报邮件
# 用法: 放在 cron 里，每天 9:00 执行
cd /home/claw/.openclaw/workspace
LATEST=$(ls -t ai-daily-news-*.html 2>/dev/null | head -1)
if [ -z "$LATEST" ]; then
    echo "[$(date)] 错误：未找到日报 HTML 文件" >> /home/claw/.openclaw/workspace/cron-newsletter.log
    exit 1
fi
python3 /home/claw/.openclaw/workspace/skills/newsletter-email/scripts/send_newsletter.py "$LATEST"
echo "[$(date)] 已发送: $LATEST" >> /home/claw/.openclaw/workspace/cron-newsletter.log
