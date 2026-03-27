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

### 编码注意
- Subject 和 From 头部使用 RFC 2047 标准格式：`=?utf-8?B?<base64>?=`
- From 格式：`=?utf-8?B?<村口情报社>?= <2323831454@qq.com>`

## 真实性要求
- 必须有2个以上来源交叉验证
- 不得虚构新闻、数据、股价
- 不得输出"整理中""待补充"等占位文本

---

## 小动物科研培训平台（2026-03-27）

### 知识库
- GitHub repo: `MungSmoothie/xkjt-knowledge`
- GitHub Pages: `https://mungsmoothie.github.io/xkjt-knowledge/`
- 知识库根目录: `/home/claw/.openclaw/workspace/knowledge-base/`
- 16个HTML页面，涵盖12个调研模块

### 关键文档
- 功能树状图 v4: `tree.html`
- 概要设计: `概要设计.html`（10章节，系统架构/技术选型/功能/数据库/接口/安全/部署/计划/成本）
- Phase 1 详细设计: `一期功能详细设计.html`（8章节，含设备码管理详细规则）
- 三期开发规划 Excel: `小动物科研培训平台_三期开发规划.xlsx`
- 全流程开发规划 Excel: `小动物科研培训平台_全流程开发规划.xlsx`

### 核心业务规则（袁开琳确认）
- **设备码仅支持手动单个添加 + Excel批量导入，不提供自动生成功能**
- 设备码格式：`XK-{类型}-{日期(YYYYMMDD)}-{序号(4位)}`，如 `XK-US-20260327-0001`
- 设备码类型：US（超声类）、IC（设备操作类）、MX（混合全解锁）
- Phase 1 先不做自动生成

### 技术栈
- 前端: Next.js + 微信小程序（Phase 2）
- 后端: NestJS / Go
- 数据库: MySQL + Redis
- 视频: 腾讯云VOD + flv.js/HLS
- 直播: 腾讯云CSS（Phase 2）
- CDN: Cloudflare + 腾讯云
- 支付: 微信/支付宝聚合支付

### 开发计划
- 调研准备: 15天 ¥17,600
- Phase 1: 26天 ¥30,400（核心功能：视频点播+会员+支付+设备码管理）
- Phase 2: 30天 ¥24,000（直播+社区+B端+CMS）
- Phase 3: 23天 ¥18,400（搜索+设备SDK+报表）
- 上线发布: 6天 ¥4,800
- 合计: ~100天 ¥95,200

### 联系人
- 袁开琳 (8652589172): 产品/需求方
- 绿豆冰沙/大哥 (7917279907): 社长
