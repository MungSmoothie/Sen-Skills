---
name: newsletter-email
description: 将生成的 AI 日报 HTML 发送至 QQ 邮箱，支持完整报刊排版、UTF-8 规范编码。触发场景：(1) 用户要求"发邮件"、"发送日报" (2) 日报生成完毕后自动推送 (3) 重新发送或修订版邮件。
---

# Newsletter Email Skill

将村口情报社日报 HTML 发送至 QQ 邮箱，**正文内嵌样式 + HTML 附件**。

## 发送规则（必须遵守）

每次发送邮件必须同时包含：
1. **邮件正文**：HTML 的 CSS 内联版本，渲染效果好看
2. **附件**：原始 HTML 文件（保留 `<style>` 标签），下载后浏览器打开样式完整

## 发送脚本

调用 `send_email_with_attachment.py`，用法：

```bash
python3 skills/newsletter-email/scripts/send_email_with_attachment.py <html_file> [recipient_email]...
```

- `html_file`: 日报 HTML 文件路径
- `recipient_email`（可选）: 收件人，默认使用配置中的三个邮箱

## 邮件配置

- SMTP: smtp.qq.com:587 (STARTTLS)
- 发件人: 村口情报社 \<2323831454@qq.com\>
- 收件人: 179621078@qq.com / hakusai22@qq.com / 536574781@qq.com
- 编码: RFC 2047 标准（=?utf-8?B?...?=）

## 邮件处理规则

### 正文处理
- CSS 内联：通过 `inline_css()` 将 `<style>` 中的样式应用到各元素的 `style=""` 属性
- 移除 `<script>` 标签（邮件不支持 JS）
- 移除 Google Fonts `@import`（邮件客户端不支持）
- 移除外部 `<link>` CSS 引用

### 附件处理
- 自动嵌入 `style.css` 到 `<style>` 标签（替换外部引用）
- 移除 `@import` 确保附件 HTML 完全自包含
- 文件名：`ai-daily-news-YYYY-MM-DD.html`

## 主题格式

```
村口情报社 AI日报 YYYY年MM月DD日
```

## 注意事项

- 邮件正文和附件是两套不同的 HTML：正文是内联版，附件是嵌入 CSS 版
- Subject 和 From 头部使用 RFC 2047 编码，不使用 `=?UTF-8?B?...?=`
- 正文 HTML 很长（~80KB），这是正常的（CSS 内联后体积变大）
