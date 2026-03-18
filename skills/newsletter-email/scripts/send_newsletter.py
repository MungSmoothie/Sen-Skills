#!/usr/bin/env python3
"""
send_newsletter.py — 将日报 HTML 发送至 QQ 邮箱
用法: python3 send_newsletter.py <html_file> [recipient_email]...
"""
import sys
import subprocess
import re
import base64
import os

# 默认收件人
DEFAULT_RECIPIENTS = ["179621078@qq.com", "hakusai22@qq.com", "536074781@qq.com"]
SENDER_EMAIL = "2323831454@qq.com"
SENDER_DISPLAY = "村口情报社"

def encode_header(s):
    """RFC 2047 UTF-8 Base64 编码"""
    return "=?UTF-8?B?" + base64.b64encode(s.encode("utf-8")).decode("ascii") + "?="

CSS_VAR_MAP = {
    "--wine-red": "#8b2635", "--charcoal": "#1a1a1a",
    "--warm-gray": "#6b6560", "--light-warm": "#f0ebe3",
    "--paper": "#faf8f3", "--navy": "#1a3a5c",
    "--text": "#222222", "--text-light": "#5a5a5a",
    "--border": "#d4cfc5",
    "--tl": "#5a5a5a", "--t": "#222222",
    "--c": "#1a1a1a", "--wg": "#6b6560",
    "--lw": "#f0ebe3", "--p": "#faf8f3",
    "--wr": "#8b2635", "--n": "#1a3a5c", "--b": "#d4cfc5",
}

def make_email_safe(html):
    """
    Convert HTML to email-safe version:
    - Expand CSS variables (email clients don't support var() syntax)
    - Remove @import / <link> external fonts
    - Remove <script> tags
    - Add body inline style
    """
    for var, val in CSS_VAR_MAP.items():
        html = html.replace(f"var({var})", val)
    html = re.sub(r"@import\s+url\([^)]+\);?\s*", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<link[^>]*fonts[^>]*>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    html = html.replace("<body>", '<body style="margin:0;padding:20px;background:#c9c3b8;">', 1)
    return html

def send_email(html_content, subject, to_email):
    """通过 msmtp 发送邮件"""
    subject_enc = encode_header(subject)
    from_enc = encode_header(SENDER_DISPLAY) + " <" + SENDER_EMAIL + ">"

    headers = "\r\n".join([
        f"From: {from_enc}",
        f"To: {to_email}",
        f"Subject: {subject_enc}",
        "Content-Type: text/html; charset=UTF-8",
        "MIME-Version: 1.0",
        "",
        html_content
    ])

    result = subprocess.run(
        ["msmtp", to_email],
        input=headers.encode("utf-8"),
        capture_output=True,
        timeout=30
    )
    return result

def main():
    if len(sys.argv) < 2:
        print("用法: python3 send_newsletter.py <html_file> [recipient_email]...", file=sys.stderr)
        sys.exit(1)

    html_file = sys.argv[1]
    recipients = sys.argv[2:] if len(sys.argv) > 2 else DEFAULT_RECIPIENTS

    if not os.path.exists(html_file):
        print(f"错误: 文件不存在 {html_file}", file=sys.stderr)
        sys.exit(1)

    with open(html_file, "r", encoding="utf-8") as f:
        raw_html = f.read()

    # 提取日期用于生成主题
    date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', raw_html)
    if date_match:
        subject = f"村口情报社 AI日报 {date_match.group(1)}年{date_match.group(2)}月{date_match.group(3)}日"
    else:
        from datetime import datetime
        today = datetime.now().strftime("%Y年%m月%d日")
        subject = f"村口情报社 AI日报 {today}"

    email_html = make_email_safe(raw_html)
    success = True
    for r in recipients:
        result = send_email(email_html, subject, r)
        if result.returncode == 0:
            print(f"发送成功: {subject} -> {r}")
        else:
            print(f"发送失败 {r}: {result.stderr.decode()}", file=sys.stderr)
            success = False
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
