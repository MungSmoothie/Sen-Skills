# Memory

- GitHub token 存放在 ~/.git-credentials

## AI日报生成规范 (v2)

### 模板原则
- 优先使用 `assets/template.html` 和 `assets/style.css`
- 只替换内容槽位，不改变页面骨架
- 样式直接嵌入HTML中（Telegram无法加载外部CSS）

### 样式规范
- 页面底色：米白纸张色 (#faf8f3)
- 强调色：暗红/酒红色 (#8b2635)
- 字体：Noto Serif SC（衬线）+ Noto Sans SC
- 整体风格：中文报刊/杂志社排版

### 页面结构
1. 报头：刊名 + 日期 + 期数 + 编辑
2. 顶部导航：5个频道
3. 主内容区：左侧头条 + 右侧边栏
4. 底部：4栏新闻
5. 页脚

### 五个频道
1. 今日要闻 2. 深度报道 3. 国际焦点 4. 科技前沿 5. 财经观察

### 新闻源优先级
1. 一手信源（官方公告、博客、财报）
2. 国际权威媒体（Reuters/Bloomberg/FT/WSJ）
3. 科技媒体（TechCrunch/The Verge/VentureBeat）
4. 中文媒体（财新/36氪/雷峰网）

### 邮件发送规范

### 发送规则（必须遵守）
发送日报邮件时，**必须同时包含两部分**：
1. **邮件正文**：HTML 的 CSS 内联版本（通过 `inline_css()` 处理），渲染效果好看
2. **附件**：原始 HTML 文件（保留 `<style>` 标签），文件名为 `ai-daily-news-YYYY-MM-DD.html`

### 发送脚本
使用 `/home/claw/.openclaw/workspace/scripts/send_html_email_with_attachment.py`，用法：
```bash
python3 /home/claw/.openclaw/workspace/scripts/send_html_email_with_attachment.py <html_file> [recipient_email]...
```
该脚本自动完成：
- CSS 内联 → 邮件正文
- 原始 HTML → 附件

### 邮件主题格式
`村口情报社 AI日报 YYYY年MM月DD日`

### 收件人
- 179621078@qq.com
- hakusai22@qq.com
- 536574781@qq.com
- 1435161527hls@gmail.com
- kano520lmy@gmail.com

### 编码注意
- Subject 和 From 头部使用 RFC 2047 标准格式：`=?utf-8?B?<base64>?=`
- From 格式：`=?utf-8?B?<村口情报社>?= <2323831454@qq.com>`

## 群聊回复规范（重要，必须遵守）

**回复任何消息之前，必须先查 AGENTS.md 确认 sender_id 与用户名的映射关系，再决定如何称呼。绝不能不查就回复。**

### 成员映射表
- `8652589172` = 开哥
- `7917279907` = 大哥 (森哥)
- `1245445176` = 群主大人

### 回复流程
1. 收到消息 → 从 metadata 提取 sender_id
2. 查 AGENTS.md → 找到对应称呼
3. 用正确称呼回复

### 禁止事项
- 不查映射表就直接回复
- 凭名字/语气/头像判断身份（sender_id 才是唯一依据）

## 真实性要求
- 必须有2个以上来源交叉验证
- 不得虚构新闻、数据、股价
- 不得输出"整理中""待补充"等占位文本



## 电子手帐贴纸App项目（2026-04-08）

### 调研结论
大哥的想法：做一个电子手帐App，用户拍照片→AI抠图→存为PNG贴纸→粘到手帐画布上创作。

### 核心结论
- **可以做** ✅，差异化在"用户原创贴纸"而非素材库
- **技术可行**：iOS Vision框架 + Android ML Kit 抠图完全免费（0 API成本）
- **落地优先级**：iOS P0 > 小米 HyperOS P0 > 三星/OPPO P1 > 华为 P3
- **不需要对接厂商私有SDK**，ML Kit + Vision 足够

### 技术方案
- 前端：Vue/React + Capacitor（一套代码跑iOS/Android/小程序）
- iOS抠图：Vision框架（Capacitor插件封装）
- Android抠图：Google ML Kit（Capacitor插件）
- 存储：七牛云/阿里云OSS（贴纸PNG）
- 成本：主力机型¥0（无API费用）

### 竞品分析
- 苹果iOS：有贴纸库但无分类/无创作画布/无云同步
- 安卓：碎片化，无统一贴纸体系，竞争弱
- 醒图/轻颜：工具，不是平台

### 商业化
- 免费+内购（会员订阅+模板商店）
- 护城河：用户积累的贴纸库，迁移成本高

### 存档位置
- 完整调研报告：memory/projects/sticker-app/research-2026-04-08.html
