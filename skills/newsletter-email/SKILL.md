---
name: newsletter-email
description: 将生成的 AI 日报 HTML 发送至 QQ 邮箱。支持完整报刊排版、UTF-8 规范编码、内联 CSS，适用于村口情报社日报发布流程。触发场景：(1) 用户要求"发邮件"、"发送日报" (2) 日报生成完毕后自动推送 (3) 重新发送或修订版邮件。
---

# Newsletter Email Skill

将村口情报社日报 HTML 发送至 QQ 邮箱。

## 工作流程

1. 读取 HTML 文件
2. 转换为邮件安全版本（移除 `<style>` 中的外部字体、保留布局结构）
3. 使用 msmtp 发送，UTF-8 Base64 规范编码主题和发件人

## 发送脚本

调用 `scripts/send_newsletter.py`，用法：

```bash
python3 scripts/send_newsletter.py <html_file> [recipient_email]
```

- `html_file`: 日报 HTML 文件路径
- `recipient_email`（可选）: 收件人邮箱，默认使用 `references/config.txt` 中配置

## 邮件配置

- SMTP: smtp.qq.com:587 (STARTTLS)
- 发件人: 2323831454@qq.com
- 收件人: 179621078@qq.com
- 发送工具: msmtp
- 编码: UTF-8 Base64 RFC 2047

## 邮件 HTML 处理规则

- 移除 Google Fonts `@import`（邮件客户端不支持外部字体）
- 移除 `<link>` 字体引用
- 移除 `<script>` 标签
- **保留 `<style>` 内嵌 CSS**（邮件客户端通常支持）
- body 添加基础内联 margin/padding
- 主题和发件人显示名使用 `=?UTF-8?B?...?=` 格式编码

> ⚠️ 邮件不支持 JavaScript，tab 切换频道功能在邮件中无效，内容以五频道平铺形式展示。
