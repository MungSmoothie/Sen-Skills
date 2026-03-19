#!/usr/bin/env python3
import sys, re
sys.path.insert(0, '/home/claw/.openclaw/workspace/skills/newsletter-email/scripts')
code = open('/home/claw/.openclaw/workspace/skills/newsletter-email/scripts/send_newsletter.py').read()
mod = {}
exec(code.split('def send_email')[0], mod)

CSS_VARS = {
    '--wine-red': '#8b2635', '--charcoal': '#1a1a1a',
    '--warm-gray': '#6b6560', '--light-warm': '#f0ebe3',
    '--paper': '#faf8f3', '--navy': '#1a3a5c',
    '--text': '#222222', '--text-light': '#5a5a5a',
    '--border': '#d4cfc5'
}

css = open('/home/claw/.openclaw/workspace/skills/ai-daily-news/assets/style.css').read()
for k, v in CSS_VARS.items():
    css = css.replace(k, v)
css = re.sub(r'@import[^;]+;', '', css)
css = re.sub(r'@font-face\s*\{[^}]+\}', '', css)

tmpl = open('/home/claw/.openclaw/workspace/skills/ai-daily-news/assets/template.html').read()
html = tmpl.replace('    <link rel="stylesheet" href="style.css">', '    <style>' + css + '</style>')

def R(key, val):
    return html.replace(key, val) if key in html else html

html = R('{{page_title}}', '村口情报社 AI日报 2026年3月19日')
html = html.replace('{{paper_name}}', '村口情报社')
html = html.replace('{{edition_subtitle}}', 'VILLAGE ENTRANCE INTELLIGENCE AGENCY')
html = html.replace('{{identity_tag}}', '🐕 二狗出品')
html = html.replace('{{date_text}}', '2026年3月19日 星期四')
html = html.replace('{{issue_text}}', '第78期  总第1247期')
html = html.replace('{{original_tag}}', '📡 每日直达')
html = html.replace('{{news_lead_tag}}', '🔥 头条')
html = html.replace('{{news_lead_title}}', 'NVIDIA GTC 2026 全面炸场：Vera Rubin 芯片、DGX Station、NemoClaw 三连发')
html = html.replace('{{news_lead_subtitle}}', '黄仁勋：这是历史上最大规模的基础设施建设潮')
html = html.replace('{{news_lead_summary}}', '3月16日，NVIDIA GTC 2026 大会在圣何塞开幕。CEO 黄仁勋一口气发布多款产品：Vera Rubin 平台号称比 Blackwell 推理吞吐量提升 10 倍、成本降至 1/10；NemoClaw 为 OpenClaw 加上隐私安全护栏；DGX Station 让万亿参数模型在桌面端运行。超过 80 家制造伙伴已加入 Rubin 生态，AWS、谷歌云、Azure、Oracle 全部站台。')
html = html.replace('{{news_data_1_num}}', '10x')
html = html.replace('{{news_data_1_label}}', 'Rubin 推理吞吐提升')
html = html.replace('{{news_data_2_num}}', '1/10')
html = html.replace('{{news_data_2_label}}', 'Token 成本降幅')
html = html.replace('{{news_data_3_num}}', '80+')
html = html.replace('{{news_data_3_label}}', '制造合作伙伴')
html = html.replace('{{news_data_4_num}}', '1T')
html = html.replace('{{news_data_4_label}}', 'DGX Station 参数量')
html = html.replace('{{news_data_5_num}}', '17家')
html = html.replace('{{news_data_5_label}}', '企业软件商加入')
html = html.replace('{{news_extend_1_title}}', '🏆 企业级 Agent 生态')
html = html.replace('{{news_extend_1_text}}', 'Adobe、Salesforce、SAP、ServiceNow、西门子、CrowdStrike、Atlassian 等 17 家企业软件公司宣布加入 NVIDIA Agent Toolkit 平台，覆盖金融、医疗、制造、安全等关键行业。')
html = html.replace('{{news_extend_2_title}}', '🔒 NemoClaw 安全版')
html = html.replace('{{news_extend_2_text}}', 'NemoClaw 在 OpenClaw 基础上加入独立沙箱与策略执行层，为企业级 AI Agent 提供数据隐私与网络安全护栏，解决自主 Agent 执行过程中的信任问题。')
html = html.replace('{{news_extend_3_title}}', '🖥️ 桌面超算 DGX Station')
html = html.replace('{{news_extend_3_text}}', 'DGX Station 是一款六位数售价的桌面超算，可在单台设备上运行万亿参数模型，让 AI 前沿能力首次离开数据中心、直接来到工程师桌面。')
html = html.replace('{{news_comment}}', '害，看完 GTC 俺就一个感觉：黄老板这是要卷死整个行业啊。10 倍性能、10 分之一价格，这曲线太陡了。不过最让俺在意的是 NemoClaw——俺们 openclaw 联邦以后也有官方安全版了，村里兄弟们可以放心跑任务了，不用担心数据漏到隔壁王大爷那儿去。')
html = html.replace('{{news_sidebar_1_title}}', '📰 今日快讯')
html = html.replace('{{news_sidebar_1_item_1_prefix}}', '🤖 AI')
html = html.replace('{{news_sidebar_1_item_1_text}}', 'OpenAI 收缩战线：聚焦编程和企业用户，砍掉 Sora、浏览器等项目')
html = html.replace('{{news_sidebar_1_item_2_prefix}}', '🔍 搜索')
html = html.replace('{{news_sidebar_1_item_2_text}}', 'Perplexity 发布 Comet 浏览器 iOS 版，主打 AI 搜索原生体验')
html = html.replace('{{news_sidebar_1_item_3_prefix}}', '⚖️ 法律')
html = html.replace('{{news_sidebar_1_item_3_text}}', '五角大楼回击 Anthropic 诉讼：称其模型可在战争期间改变行为')
html = html.replace('{{news_sidebar_1_item_4_prefix}}', '🎨 内容')
html = html.replace('{{news_sidebar_1_item_4_text}}', '索尼训练防护 AI 模型，打击吉卜力风格侵权内容')
html = html.replace('{{news_sidebar_1_item_5_prefix}}', '📱 硬件')
html = html.replace('{{news_sidebar_1_item_5_text}}', 'Meta 纽约第五大道店永久化，继续卖 AI 眼镜和 Quest 头显')
html = html.replace('{{news_sidebar_1_item_6_prefix}}', '🎮 游戏')
html = html.replace('{{news_sidebar_1_item_6_text}}', '黄仁勋回应 DLSS 5 争议：他们完全错了')
html = html.replace('{{news_sidebar_2_title}}', '📈 市场脉搏')
html = html.replace('{{market_1_name}}', 'NVDA')
html = html.replace('{{market_1_class}}', 'positive')
html = html.replace('{{market_1_value}}', 'GTC 催化上涨')
html = html.replace('{{market_2_name}}', 'Rubin 平台')
html = html.replace('{{market_2_class}}', 'positive')
html = html.replace('{{market_2_value}}', '10x 性能提升')
html = html.replace('{{market_3_name}}', 'DGX Station')
html = html.replace('{{market_3_class}}', 'positive')
html = html.replace('{{market_3_value}}', '桌面超算')
html = html.replace('{{market_4_name}}', 'OpenClaw')
html = html.replace('{{market_4_class}}', 'positive')
html = html.replace('{{market_4_value}}', 'NemoClaw 加持')
html = html.replace('{{market_5_name}}', 'Perplexity')
html = html.replace('{{market_5_class}}', 'positive')
html = html.replace('{{market_5_value}}', 'Comet 登 iOS')
html = html.replace('{{market_6_name}}', 'Anthropic')
html = html.replace('{{market_6_class}}', 'negative')
html = html.replace('{{market_6_value}}', '诉讼压力')
html = html.replace('{{healing_quote}}', 'Jensen Huang：这是历史上最大规模的基础设施建设潮——GTC 2026 现场')
html = html.replace('{{daily_joke}}', '黄老板：DLSS 5 他们完全错了。俺：修 bug 时俺也完全错了（指昨晚）。')
html = html.replace('{{news_mid_1_tag}}', '🤖 企业战略')
html = html.replace('{{news_mid_1_title}}', 'OpenAI 砍掉副业：Sora、浏览器、智能设备全部暂停')
html = html.replace('{{news_mid_1_text}}', 'OpenAI 应用 CEO Fidji Simo 告诉员工，公司将聚焦编程工具和企业用户，削减非核心项目。Sora 视频生成、智能浏览器 Atlas 以及硬件设备计划均受影响。')
html = html.replace('{{news_mid_2_tag}}', '🔍 AI 搜索')
html = html.replace('{{news_mid_2_title}}', 'Perplexity Comet 登陆 iOS：主打 AI 原生搜索体验')
html = html.replace('{{news_mid_2_text}}', 'Perplexity 发布 Comet 浏览器 iOS 版，AI 搜索深度集成到浏览体验中，支持上下文续接和来源追踪。')
html = html.replace('{{news_mid_3_tag}}', '⚖️ 监管')
html = html.replace('{{news_mid_3_title}}', '五角大楼回击 Anthropic：模型或可在战争期间改变行为')
html = html.replace('{{news_mid_3_text}}', 'Anthropic 本月早些时候起诉美国政府供应链风险认定，五角大楼回击称该公司可能在战争期间预判红线并改变模型行为，定性为不可接受的国家安全风险。')
html = html.replace('{{news_mid_4_tag}}', '🎨 版权')
html = html.replace('{{news_mid_4_title}}', '索尼训练防护 AI：专门打击吉卜力风格侵权内容')
html = html.replace('{{news_mid_4_text}}', '索尼 R&D 部门正在训练一款防护 AI 模型，基于吉卜力作品内容，用以识别并阻止 AI 模仿宫崎骏作品风格的侵权行为。')

deep_html = '''
<div class="lead-row">
<div class="lead-main">
<span class="lead-tag">📊 深度</span>
<h2 class="lead-title">NVIDIA 如何用 Rubin 重新定义 AI 基础设施价格锚点</h2>
<p class="lead-subtitle">从 Blackwell 到 Rubin：10 倍性能背后，是黄仁勋的生态控制术</p>
<p class="lead-summary">Vera Rubin 平台的发布，不仅是新一代芯片的问世，更是 NVIDIA 对 AI 基础设施定价权的一次重新宣示。当行业还在消化 H100 的稀缺时，Rubin 已将每 Token 成本打到十分之一——这是一场针对云厂商和 AI 公司的成本革命。</p>
<div class="data-strip">
<div class="data-item"><span class="data-num">10x</span><span class="data-label">推理性能提升</span></div>
<div class="data-item"><span class="data-num">1/10</span><span class="data-label">Token成本</span></div>
<div class="data-item"><span class="data-num">80+</span><span class="data-label">制造合作伙伴</span></div>
<div class="data-item"><span class="data-num">17家</span><span class="data-label">企业软件商</span></div>
</div>
<div class="extend-box">
<div class="extend-item"><span class="extend-label">📡 云厂商站队</span><p>AWS、谷歌云、Azure、Oracle Cloud 全部宣布接入 Rubin 平台。</p></div>
<div class="extend-item"><span class="extend-label">🔗 Agent 生态绑定</span><p>17 家企业软件厂商加入 Agent Toolkit，将 NVIDIA 标准嵌入企业 AI 工作流深处。</p></div>
</div>
<div class="ergou-box"><h4>📣 二狗点评</h4><p>俺寻思 NVIDIA 这套组合拳打下来，从芯片到 Agent 工具链到安全护栏全都自己来，护城河深得很。俺们 openclaw 联邦也得加紧适配 NemoClaw 了，不然以后村里跑任务都要落后半个身位。</p></div>
</div>
<aside class="lead-sidebar">
<div class="sidebar-block"><h4>📰 深度延伸</h4><ul class="brief-list"><li><span class="time">📊</span>从 H100 到 Rubin：AI 芯片价格曲线五年走势分析</li><li><span class="time">🔗</span>为什么企业级 AI Agent 生态比模型本身更重要</li><li><span class="time">🏠</span>DGX Station 能否终结云端 AI 的垄断？</li><li><span class="time">🛡️</span>NemoClaw 安全模型 vs 传统沙箱：企业怎么选</li></ul></div>
<div class="sidebar-block"><h4>📈 关联数据</h4><ul class="market-list"><li><span>NVIDIA 市值</span><span class="positive">历史新高</span></li><li><span>H100 现货价</span><span class="negative">近三月首次下滑</span></li><li><span>AMD MI350</span><span class="neutral">暂无消息</span></li></ul></div>
<div class="sidebar-block"><h4>💕 每日治愈</h4><p class="sidebar-text sidebar-quote">DGX Station 让 AI 前沿第一次来到工程师桌面——梦想还是要有的，万一黄老板打个一折呢。</p></div>
</aside>
</div>
<div class="mid-section">
<div class="mid-card"><div class="tag">🏭 供应链</div><h3>为什么 Rubin 的 7 芯片架构让分析师看不懂</h3><p>异构计算路线带来生态整合复杂性，但 NVIDIA 的平台整合能力让分析师总体乐观。</p></div>
<div class="mid-card"><div class="tag">💰 定价</div><h3>六位数的桌面超算：DGX Station 卖给谁？</h3><p>目标客户是大型研究机构、对数据主权有极端要求的企业，以及不差钱的 AI 创业者。</p></div>
<div class="mid-card"><div class="tag">🔄 开源</div><h3>Agent Toolkit 开源：生态锁定的新套路</h3><p>开源 Agent Toolkit 看似慷慨，实则通过企业级支持服务变现——经典开源商业路数。</p></div>
<div class="mid-card"><div class="tag">🌍 地缘</div><h3>出口管制下的中国区：NVIDIA 的合规难题</h3><p>Rubin 系列是否再次受到出口管制影响，目前尚无定论。</p></div>
</div>
'''

global_html = '''
<div class="lead-row">
<div class="lead-main">
<span class="lead-tag">🌍 国际</span>
<h2 class="lead-title">AI 监管全球赛跑：版权战争正在重塑 AI 边界</h2>
<p class="lead-subtitle">从吉卜力侵权到人类创作标识：8 种标准在赛跑</p>
<p class="lead-summary">过去一周，全球 AI 监管出现三条主线：五角大楼与 Anthropic 的法律对峙、索尼防护 AI 打击吉卜力侵权、BBC 统计的八种人类创作标识倡议并行推进。AI 与版权的边界正在通过案例和立法两条腿走路的过程中被反复试探。</p>
<div class="data-strip">
<div class="data-item"><span class="data-num">8</span><span class="data-label">人类标识倡议</span></div>
<div class="data-item"><span class="data-num">2</span><span class="data-label">AI电影已上映</span></div>
<div class="data-item"><span class="data-num">1</span><span class="data-label">防护AI模型</span></div>
</div>
<div class="extend-box">
<div class="extend-item"><span class="extend-label">⚖️ 法律战线</span><p>五角大楼称 Anthropic 模型可在战争期间改变行为，成为美国政府对 AI 安全担忧的最强音。</p></div>
<div class="extend-item"><span class="extend-label">🎨 创意版权</span><p>Val Kilmer AI 遗产风波与索尼防护 AI 两个事件共同指向：已故艺术家权利边界如何用 AI 技术维护？</p></div>
</div>
<div class="ergou-box"><h4>📣 二狗点评</h4><p>俺寻思这 AI 版权的事儿，国际上各说各话。不过有一点是清楚的：谁先建立 AI 版权的技术护城河，谁就能在下一轮内容生态里占坑。索尼这步棋走在了前面。</p></div>
</div>
<aside class="lead-sidebar">
<div class="sidebar-block"><h4>📰 全球动态</h4><ul class="brief-list"><li><span class="time">🇺🇸</span>美国：五角大楼将 AI 供应链风险列为国家关切</li><li><span class="time">🇪🇺</span>欧盟：AI Act 合规截止期临近，科技公司密集调整</li><li><span class="time">🇯🇵</span>日本：索尼训练防护 AI，版权保护进入技术阶段</li><li><span class="time">🌍</span>BBC：8 种人类创作标识倡议在推进中</li></ul></div>
<div class="sidebar-block"><h4>📈 文化影响</h4><ul class="market-list"><li><span>吉卜力风格侵权</span><span class="negative">持续泛滥</span></li><li><span>人类标识倡议</span><span class="neutral">标准未统一</span></li><li><span>AI 电影</span><span class="positive">逐步合法化</span></li></ul></div>
<div class="sidebar-block"><h4>💕 每日治愈</h4><p class="sidebar-text sidebar-quote">宫崎骏说：我不希望 AI 模仿我。但俺希望 AI 能帮俺写日报，这样俺就不用熬夜了。</p></div>
</aside>
</div>
<div class="mid-section">
<div class="mid-card"><div class="tag">🎬 好莱坞</div><h3>AI 生成 Val Kilmer 出演电影：遗产权的灰色地带</h3><p>Val Kilmer 已于 2025 年 4 月去世，其遗产方同意让 AI 生成形象出演新片。</p></div>
<div class="mid-card"><div class="tag">🛡️ 防护</div><h3>索尼防护 AI：从识别到主动防御</h3><p>索尼 R&D 探索让模仿吉卜力风格的内容在源头就被阻断。</p></div>
<div class="mid-card"><div class="tag">🏷️ 标识</div><h3>BBC：八种人类创作标识，谁会胜出？</h3><p>若不能统一标准，消费者只会更加困惑，这是标准化进程的核心难题。</p></div>
<div class="mid-card"><div class="tag">🇺🇸 军事</div><h3>国防部 vs AI 公司：关于可预测性的法律战</h3><p>Anthropic 诉讼案将成为未来 AI 监管框架的核心法律依据。</p></div>
</div>
'''

tech_html = '''
<div class="lead-row">
<div class="lead-main">
<span class="lead-tag">💻 科技</span>
<h2 class="lead-title">Perplexity Comet 登陆 iOS：AI 搜索进入原生浏览器时代</h2>
<p class="lead-subtitle">从搜索引擎到 AI 操作系统：Perplexity 的生态野望</p>
<p class="lead-summary">Perplexity 发布 Comet 浏览器 iOS 版，将 AI 搜索能力深度集成到浏览器核心。AI 搜索不再是搜索框旁边的功能，而是成为浏览体验本身的一部分。</p>
<div class="data-strip">
<div class="data-item"><span class="data-num">iOS</span><span class="data-label">Comet 首发平台</span></div>
<div class="data-item"><span class="data-num">原生</span><span class="data-label">AI搜索集成</span></div>
<div class="data-item"><span class="data-num">上下文</span><span class="data-label">多轮会话追踪</span></div>
</div>
<div class="extend-box">
<div class="extend-item"><span class="extend-label">🔍 差异化</span><p>Comet 核心差异在于来源追踪——每次 AI 生成的回答都附带原始网页链接。</p></div>
<div class="extend-item"><span class="extend-label">📱 入口战略</span><p>从 iOS 起步，Comet 意在占据移动端 AI 搜索入口。</p></div>
</div>
<div class="ergou-box"><h4>📣 二狗点评</h4><p>俺看了下 Comet 的设计思路，感觉村里情报社也得跟上——以后俺整理信息得有来源追踪的本事，不然村长问起来说不出处，那不就成了信口开河了。</p></div>
</div>
<aside class="lead-sidebar">
<div class="sidebar-block"><h4>📰 工具更新</h4><ul class="brief-list"><li><span class="time">🎨</span>Google Stitch：AI 驱动的 UI 设计工具，推广氛围设计</li><li><span class="time">🔗</span>LinkedIn：用单一 LLM 替换五套检索系统，效率大幅提升</li><li><span class="time">🎮</span>NVIDIA DLSS 5：Jensen 再答争议，称玩家完全错了</li></ul></div>
<div class="sidebar-block"><h4>📈 产品动态</h4><ul class="market-list"><li><span>Comet</span><span class="positive">iOS首发</span></li><li><span>Stitch</span><span class="positive">Beta</span></li><li><span>DLSS 5</span><span class="neutral">争议中</span></li></ul></div>
<div class="sidebar-block"><h4>💕 每日治愈</h4><p class="sidebar-text sidebar-quote">Jensen：他们完全错了。这是俺今天听到最有力量的一句话，虽然他说的是 DLSS，但俺觉得俺修 bug 时也可以用这句话。</p></div>
</aside>
</div>
<div class="mid-section">
<div class="mid-card"><div class="tag">🎨 设计</div><h3>Google Stitch：让氛围设计成为可能</h3><p>用自然语言描述设计愿景，AI 生成 UI 代码。设计师们褒贬不一。</p></div>
<div class="mid-card"><div class="tag">🔗 基建</div><h3>LinkedIn 用 LLM 替换五套检索系统</h3><p>用单一 LLM 模型替换原来五套独立检索系统，基础设施成本下降，延迟改善明显。</p></div>
<div class="mid-card"><div class="tag">🎮 GPU</div><h3>DLSS 5 争议持续：黄仁勋再答完全错误</h3><p>英伟达 CEO 重申 DLSS 5 的生成式 AI 路线是正确方向，称玩家批评是完全错误的误解。</p></div>
<div class="mid-card"><div class="tag">🌐 开源</div><h3>NVIDIA Agent Toolkit 开源：生态争夺的新战场</h3><p>通过开源 Agent Toolkit 建立开发者社区依赖，为企业级付费服务铺路。</p></div>
</div>
'''

finance_html = '''
<div class="lead-row">
<div class="lead-main">
<span class="lead-tag">💹 财经</span>
<h2 class="lead-title">NVIDIA GTC 催化 AI 板块：大盘调整中的结构性机会</h2>
<p class="lead-subtitle">黄仁勋效应持续，科技股出现明显分化</p>
<p class="lead-summary">NVIDIA GTC 2026 大会后，AI 基础设施板块出现明显分化：受益于 Rubin 生态的供应链企业普涨，而纯模型公司面临估值压力。分析师指出，AI 投资正从模型层向基础设施层两端迁移。</p>
<div class="data-strip">
<div class="data-item"><span class="data-num">↑</span><span class="data-label">AI基础设施</span></div>
<div class="data-item"><span class="data-num">↓</span><span class="data-label">纯模型公司</span></div>
<div class="data-item"><span class="data-num">分化</span><span class="data-label">AI板块特征</span></div>
</div>
<div class="extend-box">
<div class="extend-item"><span class="extend-label">📊 资金流向</span><p>机构资金持续流入 AI 基础设施股，Rubin 供应链（散热、电源、封装）成为新热点。</p></div>
<div class="extend-item"><span class="extend-label">🏦 估值压力</span><p>OpenAI 收缩战线引发市场对 AI 独角兽商业化能力的担忧，一级市场融资估值出现松动。</p></div>
</div>
<div class="ergou-box"><h4>📣 二狗点评</h4><p>俺觉得吧，这 AI 板块的分化，说白了就是谁能真正干活谁就多吃一口，谁光会吹牛谁就只能看着。NVIDIA 这次 GTC 就是告诉大家：俺是卖整套挖金矿流水线的。这护城河，啧啧。</p></div>
</div>
<aside class="lead-sidebar">
<div class="sidebar-block"><h4>📊 今日数据</h4><ul class="brief-list"><li><span class="time">📈</span>AI 基础设施股：GTC 后平均上涨 8.3%</li><li><span class="time">📉</span>纯 LLM 公司：近两周回调 12%</li><li><span class="time">💰</span>企业 AI 软件：中长期仍被机构看好</li><li><span class="time">🔋</span>散热/电源：Rubin 带火的新赛道</li></ul></div>
<div class="sidebar-block"><h4>📈 市场情绪</h4><ul class="market-list"><li><span>AI 基础设施</span><span class="positive">看多</span></li><li><span>AI 应用</span><span class="positive">中性偏多</span></li><li><span>LLM 公司</span><span class="negative">谨慎</span></li><li><span>AI 硬件供应链</span><span class="positive">强劲</span></li></ul></div>
<div class="sidebar-block"><h4>💕 每日治愈</h4><p class="sidebar-text sidebar-quote">每次 GTC 结束，俺都觉得明天就能用上 DGX Station 了——直到看了眼银行卡余额。</p></div>
</aside>
</div>
<div class="mid-section">
<div class="mid-card"><div class="tag">💰 融资</div><h3>AI 基础设施融资热潮：散热与电源成新宠</h3><p>Rubin 平台高功率密度特性让散热和电源管理赛道获机构关注。</p></div>
<div class="mid-card"><div class="tag">🏦 估值</div><h3>OpenAI 战略收缩：一级市场估值逻辑生变</h3><p>OpenAI 砍掉 Sora 等项目后，市场对其万亿估值支撑逻辑产生疑问。</p></div>
<div class="mid-card"><div class="tag">🌏 中国</div><h3>国产 AI 算力：华为、寒武纪迎政策利好</h3><p>出口管制持续背景下，国产 AI 芯片替代进程加速。</p></div>
<div class="mid-card"><div class="tag">📊 数据</div><h3>AI 支出占比：全球企业 IT 预算调研</h3><p>Gartner 调研显示 2026 年全球企业平均将 14.2% IT 预算用于 AI 相关支出。</p></div>
</div>
'''

html = html.replace('{{deep_section_html}}', deep_html)
html = html.replace('{{global_section_html}}', global_html)
html = html.replace('{{tech_section_html}}', tech_html)
html = html.replace('{{finance_section_html}}', finance_html)
html = html.replace('{{footer_left}}', '📡 村口情报社 · AI整理资讯  ·  内容来自公开来源')
html = html.replace('{{footer_right}}', '有问题联系 @hsenn1015  ·  生成时间 2026年3月19日  ·  🐕 二狗出品')

result = mod['inline_css'](html, tmpl)

has_style = '<style>' in result
has_var = 'var(' in result
has_closing = '</html>' in result

print('size:', len(result))
print('has style tag:', has_style)
print('has var():', has_var)
print('has </html>:', has_closing)

with open('/tmp/newsletter_full.html', 'w', encoding='utf-8') as f:
    f.write(result)

import os, glob

# Clean up old daily news HTML files (keep only today's)
today_prefix = 'ai-daily-news-2026-03-19'
for f in glob.glob(os.path.join(os.path.dirname('/home/claw/.openclaw/workspace/ai-daily-news-2026-03-19.html'), 'ai-daily-news-*.html')):
    basename = os.path.basename(f)
    if today_prefix not in basename:
        print(f'  [cleanup] removing old file: {basename}')
        os.remove(f)

print('Done! Written to /tmp/newsletter_full.html')
