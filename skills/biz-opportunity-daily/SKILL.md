---
name: biz-opportunity-daily
description: 生成AI超级个体商机洞察日报HTML。基于油管超级个体大佬动态分析，输出固定报刊排版的商机洞察报告。适用于：(1) 每日商机洞察推送 (2) 超级个体赚钱路径拆解 (3) 蓝海赛道+红海避坑分析。村口情报社风格，强调色金色（#d4a017）、深色header（#1a1a1a）。
---

# AI超体风向 · 商机洞察日报

基于油管超级个体大佬（Ali Abdaal / Thomas Frank / Wrishir 等）动态分析，生成固定报刊排版的商机洞察日报。

核心目标：**在固定模板中稳定填充当日真实内容，保持高度一致的版式、结构和视觉风格。**

## 最高优先级原则

### 模板优先原则
- 若存在 `assets/template.html`，必须基于该文件生成结果。
- 默认行为是：**只替换内容，不重写布局，不改写视觉风格，不重新设计页面。**
- 除非用户明确要求"改版 / 换风格 / 重做样式"，否则不得修改页面骨架。

### 搜索工具选择
1. 优先用 `web_search`（Brave Search）
2. 如果 Brave Search 不可用，用 Tavily：
   ```
   python3 /home/claw/.openclaw/workspace/skills/openclaw-tavily-search/scripts/tavily_search.py --query "..." --max-results 5 --include-answer --format brave
   ```

## 模板结构（固定五大频道）

每个频道均使用相同的 `lead-row` 双栏布局（左侧主内容+右侧侧栏），内容按槽位填充：

### 频道一：🌏 市场洞察（id="insight"）
- `{{insight_lead_tag}}` — 频道标签
- `{{insight_title}}` — 主标题
- `{{insight_subtitle}}` — 副标题
- `{{insight_summary}}` — 正文摘要
- `{{insight_data_1-5}}` — 数据条（数字+标签）
- `{{insight_extend_1-3}}` — 延展模块（标题+内容）
- `{{insight_comment}}` — 二狗点评
- `{{insight_sidebar_quicknews}}` — 今日快讯（6条）
- `{{insight_sidebar_marketdata}}` — 市场数据（5条）
- `{{insight_sidebar_healing}}` — 每日治愈
- `{{insight_sidebar_joke}}` — 每日笑料
- `{{insight_mid_1-4}}` — 底部四栏（tag+标题+正文）

### 频道二：💰 蓝海机会（id="opportunity"）
- `{{opp_lead_tag}}` — 频道标签
- `{{opp_title}}` — 主标题
- `{{opp_subtitle}}` — 副标题
- `{{opp_summary}}` — 正文摘要
- `{{opp_data_1-4}}` — 数据条
- `{{opp_extend_1-3}}` — 延展模块
- `{{opp_comment}}` — 底线声明
- `{{opp_card_P0-P3}}` — 4个机会卡片（P0/P1/P2/P3）
- `{{opp_sidebar_tools}}` — 工具清单
- `{{opp_sidebar_priority}}` — 优先级推荐（P0-P3盒子）
- `{{opp_sidebar_healing}}` — 每日治愈
- `{{opp_sidebar_joke}}` — 每日笑料

### 频道三：🎯 大佬怎么做（id="howto"）
- `{{howto_lead_tag}}` — 频道标签
- `{{howto_title}}` — 主标题
- `{{howto_subtitle}}` — 副标题
- `{{howto_summary}}` — 正文摘要
- `{{howto_data_1-4}}` — 数据条
- `{{howto_extend_1-3}}` — 共同逻辑
- `{{howto_comment}}` — 二狗点评
- `{{howto_sidebar_tools}}` — 工具清单
- `{{howto_sidebar_healing}}` — 每日治愈
- `{{howto_sidebar_joke}}` — 每日笑料
- `{{howto_method_1-3}}` — 三位大佬路径卡片（序号+标题+正文+操作步骤）

### 频道四：🚫 红海避坑（id="avoid"）
- `{{avoid_lead_tag}}` — 频道标签
- `{{avoid_title}}` — 主标题
- `{{avoid_subtitle}}` — 副标题
- `{{avoid_summary}}` — 正文摘要
- `{{avoid_data_1-5}}` — 数据条
- `{{avoid_extend_1-3}}` — 坑位分析
- `{{avoid_comment}}` — 二狗点评
- `{{avoid_sidebar_red}}` — 已确认红海列表（6条）
- `{{avoid_sidebar_green}}` — 替代方向蓝海列表（6条）
- `{{avoid_sidebar_healing}}` — 每日治愈
- `{{avoid_sidebar_joke}}` — 每日笑料
- `{{avoid_mid_1-4}}` — 底部四栏坑位详解

### 频道五：📌 二狗点评（id="ergou"）
- `{{ergou_lead_tag}}` — 频道标签
- `{{ergou_title}}` — 主标题
- `{{ergou_subtitle}}` — 副标题
- `{{ergou_summary}}` — 正文摘要
- `{{ergou_data_1-5}}` — 数据条
- `{{ergou_extend_1-3}}` — 核心判断/时机判断/路线建议
- `{{ergou_final_comment}}` — 最终判断（可含多段落）
- `{{ergou_sidebar_quicknews}}` — 今日快讯
- `{{ergou_sidebar_marketdata}}` — 市场数据
- `{{ergou_sidebar_healing}}` — 每日治愈
- `{{ergou_sidebar_joke}}` — 每日笑料
- `{{ergou_mid_1-4}}` — 底部四栏（毒舌/务实/反直觉/最终）

## 固定视觉规范

- 页面底色：米白纸张色 `#faf8f3`
- 强调色：金色 `#d4a017`（标题、数据、标签）
- Header背景：`#1a1a1a`（黑底金字）
- 主色：暗红 `#8b2635`（opp-tag、mid-card tag）
- 字体：Noto Serif SC（衬线）+ Noto Sans SC
- 导航栏：`position: sticky; top: 0; z-index: 100`
- 频道切换 JS：内联 `onclick` 调用 `showSection(id)`，`window.onload` 默认显示 insight
- 频道锚点：`scroll-margin-top: 70px`

## 超级个体大佬搜索范围

### 重点大佬
- Ali Abdaal（医生→知识IP）
- Thomas Frank（Notion/生产力专家）
- Patrick Bet-David / Valuetainment
- Iman Gabrani（Gumroad高手）
- Wrishir（AI side hustle实战派）
- Y Combinator 创业者vlog
- 国内：何加盐、打工诗人小北、生财有术、亦仁、曹政

### 搜索关键词（site:youtube.com）
- "AI side hustle 2026"
- "I made $X with AI"
- "AI business solo founder"
- "make money online AI 2026"
- "AI数字产品变现"
- "AI副业 2026"
- "Gumroad AI product"
- "superhuman AI productivity"

## 执行闭环

1. **搜索**：用 web_search / Tavily 搜集大佬最新动态
2. **分析**：提取具体赚钱路径、工具、数据、避坑经验
3. **填充**：按 template.html 槽位填写内容（只替换，不改结构）
4. **保存**：`/home/claw/.openclaw/workspace/biz-opportunity-daily-TODAY.html`
5. **发送**：使用 message 工具发送至 Telegram 群
   - `channel: telegram`
   - `target: -1003839027437`
   - `filePath: /home/claw/.openclaw/workspace/biz-opportunity-daily-TODAY.html`
   - `caption: 🌊 AI超体风向 · 商机洞察 · 今日刊`

## 禁止行为
- 不得修改 template.html 的结构、布局、CSS
- 不得虚构大佬案例数据
- 不得输出"整理中""待补充"等占位文本
- 不得生成 dashboard / 卡片流 / 科技门户风格页面

## 输出要求
- 最终只输出完整 HTML 代码文件路径
- 不先给提纲再给 HTML
- 完成后简单报告结果（发送状态、内容摘要）
