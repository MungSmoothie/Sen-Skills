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

### 真实性要求
- 必须有2个以上来源交叉验证
- 不得虚构新闻、数据、股价
- 不得输出"整理中""待补充"等占位文本
