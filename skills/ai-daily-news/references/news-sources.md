# 新闻源规则

本文件是新闻源维护的唯一入口。新闻来源、来源等级、频道映射、交叉验证、去重、兜底顺序、禁用来源，统一在这里维护。

## 1. 总原则
- 先保证新闻真实，再考虑版面完整。
- 能找到官方来源，就优先用官方来源。
- 能追到原始报道，就不要停留在转载稿。
- 优先当天新闻；若不足，可回退到最近 7 天内仍具时效性的新闻。
- 不同频道允许围绕同一大主题，但头条角度必须不同。

## 2. 来源等级

### A 级：一手信源（最高优先级）
适用于模型发布、产品更新、API 变化、定价、官方合作、财报、政策声明、组织动作。

优先使用：
- openai.com
- anthropic.com
- googleblog.com
- blog.google
- deepmind.google
- ai.google.dev
- microsoft.com
- blogs.microsoft.com
- aws.amazon.com
- aboutamazon.com
- cloud.google.com
- meta.com
- ai.meta.com
- nvidia.com
- huggingface.co
- huggingface.co/blog
- mistral.ai
- x.ai
- stability.ai
- midjourney.com
- github.blog
- alibabacloud.com
- aliyun.com
- baidu.com
- cloud.baidu.com
- tencent.com
- cloud.tencent.com
- bytedance.com
- volcengine.com
- sensecore.cn
- sensetime.com
- iflytek.com
- moonshot.cn
- zhipuai.cn
- minmax.io

规则：
- 若一手信源足够完整，应以其为主。
- 重大新闻建议再补一个高可信媒体来源，用于背景与产业影响解释。

### B 级：国际权威媒体
适用于融资、并购、监管、资本市场、供应链、国际竞争、产业趋势。

优先使用：
- reuters.com
- bloomberg.com
- ft.com
- wsj.com
- theinformation.com
- semafor.com
- cnbc.com
- nytimes.com
- economist.com

规则：
- 优先原始报道，不用二手转载代替原稿。
- 海外重大新闻优先由这一层补足背景。

### C 级：科技与产业媒体
适用于产品体验、开发者工具、应用发布、行业观察、生态动向。

优先使用：
- techcrunch.com
- theverge.com
- wired.com
- venturebeat.com
- arstechnica.com
- tomshardware.com
- engadget.com
- zdnet.com
- caixin.com
- yicai.com
- cls.cn
- stcn.com
- jiemian.com
- 36kr.com
- leiphone.com
- ifanr.com
- sina.com.cn/tech
- tech.qq.com

规则：
- 适合补充上下文，不适合作为重大头条的唯一依据。
- 若中文媒体转述海外新闻，优先回溯英文原始来源。

### D 级：研究与开发者来源
适用于论文、基准测试、开源项目、模型能力、工具链与开发者生态。

优先使用：
- arxiv.org
- github.com
- paperswithcode.com
- openreview.net
- research.google
- developer.nvidia.com
- huggingface.co/blog

规则：
- 适合“科技前沿”和“深度报道”。
- 不得仅凭论文摘要、README 或社区讨论，把未经验证内容写成当天最大头条。

## 3. 频道映射

### 今日要闻
优先来源：A 级 -> B 级 -> 财新 / 第一财经等高可信中文财经媒体
适用内容：当天最重要、影响面最大的 AI / 科技产业事件
约束：必须适合做版面中心，不能把小更新写成首页头条。

### 深度报道
优先来源：A 级长文 / 研究博客 -> B 级深度稿 -> D 级研究与开源来源
适用内容：技术机制、产品逻辑、背景脉络、为什么重要、对行业和开发者的意义
约束：必须适合展开，不能把快讯硬拉成长文。

### 国际焦点
优先来源：B 级 -> 海外公司官方博客与公告
适用内容：海外 AI 公司、国际监管、全球资本与供应链、国际竞争格局
约束：若同一事件已在首页出现，此频道要改写成国际影响角度。

### 科技前沿
优先来源：A 级技术博客 -> D 级研究与开发者来源 -> C 级科技媒体
适用内容：新模型、新工具、新论文、新 Agent、新框架、芯片与开发者生态
约束：必须说明实际意义，不要只报标题。

### 财经观察
优先来源：财报 / 公告 / 投资者材料 -> B 级财经媒体 -> 高可信中文财经媒体
适用内容：收入、融资、估值、价格、资本开支、云计算、芯片、商业化、产业链
约束：重点看商业影响，不要把纯技术更新硬塞进财经栏目。

## 4. 交叉验证规则
- 主头条至少需要两个独立来源交叉验证；若只有一个来源，该来源必须是一手信源。
- 股价、涨跌幅、收入、融资额、估值、时间点、模型参数、芯片数量、用户规模、定价信息必须来自可验证来源。
- 若不同来源冲突，按以下优先级裁决：官方公告/财报/投资者材料 -> 路透/彭博/FT/WSJ/财新 -> 一般科技媒体 -> 中文转载与二次解读。
- 爆料、截图、匿名传闻默认不能作为主头条依据。

## 5. 去重规则
- 同一事实不能在多个频道重复充当头条。
- 同事件跨频道出现时，必须换角度：
  - 今日要闻：事件本身
  - 深度报道：机制与意义
  - 国际焦点：全球影响
  - 科技前沿：技术变化
  - 财经观察：商业与市场影响
- 今日快讯不得重复主头条已经完整展开的信息。
- 底部四栏不得写成同一事件的四种说法。

## 6. 兜底顺序
当高优先级来源不足以支撑五个频道时，按以下顺序补足：
1. A 级：一手信源
2. B 级：国际权威媒体
3. C 级：科技与产业媒体
4. 高可信中文科技 / 财经媒体
5. D 级：研究与开发者来源（技术频道优先）

若仍不足：
- 允许减少单条文字长度
- 允许把最近一周内仍具时效性的新闻作为补充
- 不允许虚构新闻
- 不允许用明显旧闻硬凑
- 不允许因为内容不足而改模板结构

## 7. 禁用来源类型
以下来源默认不作为主新闻依据：
- 自媒体二次搬运
- 未经证实的社交媒体截图
- 标题党聚合站
- 纯营销软文
- 不可追溯原始出处的转载稿
- 论坛传闻
- 匿名爆料
- 未证实群聊消息

## 8. 白名单速查
### 一手信源常用域名
openai.com, anthropic.com, googleblog.com, deepmind.google, blog.google, microsoft.com, blogs.microsoft.com, aws.amazon.com, cloud.google.com, meta.com, ai.meta.com, nvidia.com, huggingface.co, mistral.ai, x.ai, stability.ai, midjourney.com, github.blog, alibabacloud.com, aliyun.com, baidu.com, cloud.baidu.com, tencent.com, cloud.tencent.com, bytedance.com, volcengine.com

### 国际权威媒体常用域名
reuters.com, bloomberg.com, ft.com, wsj.com, theinformation.com, semafor.com, cnbc.com, nytimes.com, economist.com

### 科技媒体常用域名
techcrunch.com, theverge.com, wired.com, venturebeat.com, arstechnica.com, tomshardware.com, engadget.com, zdnet.com

### 中文科技与财经媒体常用域名
caixin.com, yicai.com, cls.cn, stcn.com, jiemian.com, 36kr.com, leiphone.com, ifanr.com, sina.com.cn/tech, tech.qq.com

### 研究与开发者来源常用域名
arxiv.org, github.com, paperswithcode.com, openreview.net, research.google, developer.nvidia.com, huggingface.co/blog

## 9. 使用方式
- 调整新闻源时，只改本文件。
- 新增来源时，先判断它属于哪一等级，再决定它更适合哪个频道。
- 若使用白名单外来源，必须确认它公开、可信、非营销、可追溯、与频道匹配。
