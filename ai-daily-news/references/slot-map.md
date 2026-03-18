# 槽位映射说明

本文件用于把采集到的新闻内容，稳定映射到固定模板中的槽位。

## 1. 全局信息槽位
- `{{page_title}}`：页面标题
- `{{paper_name}}`：刊名
- `{{edition_subtitle}}`：副标题 / 英文副标
- `{{identity_tag}}`：身份标识
- `{{date_text}}`：日期
- `{{issue_text}}`：期数 / 星期
- `{{original_tag}}`：原创标识
- `{{footer_left}}`：页脚左侧
- `{{footer_right}}`：页脚右侧

## 2. 今日要闻频道映射
### 主头条
- `{{news_lead_tag}}`
- `{{news_lead_title}}`
- `{{news_lead_subtitle}}`
- `{{news_lead_summary}}`

### 数据带
- `{{news_data_1_num}}` ~ `{{news_data_5_num}}`
- `{{news_data_1_label}}` ~ `{{news_data_5_label}}`

### 延展模块
- `{{news_extend_1_title}}` / `{{news_extend_1_text}}`
- `{{news_extend_2_title}}` / `{{news_extend_2_text}}`
- `{{news_extend_3_title}}` / `{{news_extend_3_text}}`

### 二狗点评
- `{{news_comment}}`

## 3. 右侧侧栏映射
### 今日快讯
- `{{news_sidebar_1_title}}`
- `{{news_sidebar_1_item_1_prefix}}` ~ `{{news_sidebar_1_item_6_prefix}}`
- `{{news_sidebar_1_item_1_text}}` ~ `{{news_sidebar_1_item_6_text}}`

### 市场脉搏
- `{{news_sidebar_2_title}}`
- `{{market_1_name}}` ~ `{{market_6_name}}`
- `{{market_1_value}}` ~ `{{market_6_value}}`
- `{{market_1_class}}` ~ `{{market_6_class}}`

`market_x_class` 仅允许：`up`、`down`，若模板支持也可扩展 `flat`。

### 每日治愈
- `{{healing_quote}}`

### 每日笑料
- `{{daily_joke}}`

## 4. 底部四栏映射
- `{{news_mid_1_tag}}` / `{{news_mid_1_title}}` / `{{news_mid_1_text}}`
- `{{news_mid_2_tag}}` / `{{news_mid_2_title}}` / `{{news_mid_2_text}}`
- `{{news_mid_3_tag}}` / `{{news_mid_3_title}}` / `{{news_mid_3_text}}`
- `{{news_mid_4_tag}}` / `{{news_mid_4_title}}` / `{{news_mid_4_text}}`

规则：
- 固定 4 栏
- 每栏是独立短新闻
- 与频道相关，但不与主头条机械重复

## 5. 其他四个频道
对于 `{{deep_section_html}}`、`{{global_section_html}}`、`{{tech_section_html}}`、`{{finance_section_html}}`，建议内部也遵循与首页一致的结构，不要另起一套布局。

## 6. 填充顺序
1. 填全局报头信息
2. 填主头条
3. 填数据带
4. 填延展模块
5. 填二狗点评
6. 填右侧快讯与市场脉搏
7. 填每日治愈与每日笑料
8. 填底部四栏
9. 最后检查长度是否适配版面

## 7. 不足内容时的处理
- 先缩短文本
- 再减少每条的背景解释
- 不改变模块数量
- 不删除一级结构
- 不使用占位词
- 不虚构填充
