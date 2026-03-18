# Slot Map

使用 `assets/template.html` 时，按以下槽位填充内容。原则：**只填内容，不改结构**。

## 顶部报头
- `{{page_title}}`: 页面 title，例如 `村口情报社 - 2026年3月18日`
- `{{paper_name}}`: 报头名，默认 `村口情报社`
- `{{edition_subtitle}}`: 英文副标，例如 `AI DAILY · 智能时代前沿观察`
- `{{identity_tag}}`: 身份说明，例如 `📱 AI资讯整理 · 行业信息速览`
- `{{date_text}}`: 中文完整日期
- `{{issue_text}}`: 期数与编辑信息
- `{{original_tag}}`: 原创署名

## 今日要闻频道
- `{{news_lead_tag}}`: 英文小标签，例如 `HEADLINE`
- `{{news_lead_title}}`: 头条标题，可用 `<br>` 控制断行
- `{{news_lead_subtitle}}`: 副标题
- `{{news_lead_summary}}`: 摘要正文
- `{{news_data_1_num}}` ~ `{{news_data_5_label}}`: 数据带 5 组
- `{{news_extend_1_title}}` / `{{news_extend_1_text}}`: 延展块 1
- `{{news_extend_2_title}}` / `{{news_extend_2_text}}`: 延展块 2
- `{{news_extend_3_title}}` / `{{news_extend_3_text}}`: 延展块 3
- `{{news_comment}}`: 二狗点评
- `{{news_sidebar_1_title}}`: 右侧快讯标题
- `{{news_sidebar_1_item_1_prefix}}` / `{{news_sidebar_1_item_1_text}}`: 快讯条目 1
- 其余条目同理到 6
- `{{news_sidebar_2_title}}`: 市场脉搏标题
- `{{market_1_name}}` / `{{market_1_value}}` / `{{market_1_class}}`: 市场条目 1
- `market_*_class` 仅用 `up` 或 `down`
- `{{healing_quote}}`: 每日治愈
- `{{daily_joke}}`: 每日笑料
- `{{news_mid_1_tag}}` / `{{news_mid_1_title}}` / `{{news_mid_1_text}}`: 底部四栏新闻块 1
- 其余条目同理到 4

## 其余频道
`{{deep_section_html}}`、`{{global_section_html}}`、`{{tech_section_html}}`、`{{finance_section_html}}`

推荐做法：这四个频道复用“今日要闻”的内部结构，替换标题、摘要、数据带、点评与底部四栏内容，保持类名与布局不变。

## 填充原则
1. 优先填满所有槽位。
2. 新闻不足时缩短文案，不删除块。
3. 保持 `<div class="lead-row">`、`<aside class="lead-sidebar">`、`<div class="mid-section">` 等关键结构不变。
4. 保持右栏四模块都存在。
