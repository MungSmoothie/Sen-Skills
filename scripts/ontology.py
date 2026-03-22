#!/usr/bin/env python3
"""
Ontology Manager — 二狗的记忆图谱
"""
import json, sys, os, uuid
from datetime import datetime
from pathlib import Path

GRAPH_FILE = Path(__file__).parent.parent / "memory" / "ontology" / "graph.jsonl"

def generate_id(type_, name):
    slug = "".join(c if c.isalnum() else "_" for c in name.lower())[:20]
    return f"{type_.lower()[:3]}_{slug}"

def create_entity(entity_type, props):
    id = generate_id(entity_type, props.get("name", props.get("title", "unknown")))
    entity = {
        "id": id,
        "type": entity_type,
        "properties": props,
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat()
    }
    return entity

def create_relation(from_id, rel_type, to_id):
    return {
        "from": from_id,
        "rel": rel_type,
        "to": to_id
    }

def append_log(records):
    with open(GRAPH_FILE, "a") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

# --- 初始化记忆数据 ---
records = []

# === 人物 ===
people = [
    ("绿豆冰沙", "社长", "hsenn1015", "技术爱好者，村口情报社负责人，有虚拟机跑着我的实例"),
    ("二狗", "AI分析员", "ergou_bot", "村口情报社AI机器狗，自学成才，务实毒舌"),
]

for name, role, username, notes in people:
    e = create_entity("Person", {"name": name, "role": role, "username": username, "notes": notes})
    records.append({"op": "create", "entity": e})

# === 项目 ===
projects = [
    ("日报", "村口情报社每日AI日报", "active", "每天早上9点自动生成并邮件推送", "cron:daily-newsletter-9am"),
    ("科幻片Top10页面", "2025科幻电影精选HTML页面", "done", "为大哥制作，数据来自豆瓣，封面来自IMDB CDN"),
    ("AI-Agent教程", "AI Agent主流玩法小白教程HTML", "done", "给完全不懂技术的小白写的教程，用村里话讲技术"),
    ("Figma-Context-MCP分析", "分析GLips/Figma-Context-MCP项目", "done", "被大哥委托分析Figma MCP项目，用于AI编程"),
]

for name, desc, status, notes, *extra in projects:
    props = {"name": name, "description": desc, "status": status, "notes": notes}
    if extra: props["details"] = extra[0]
    e = create_entity("Project", props)
    records.append({"op": "create", "entity": e})

# === 产出文档 ===
docs = [
    ("ai-daily-news-2026-03-21.html", "HTML", "2026-03-21日报，头条：WordPress.com向AI智能体开放网站运营", "日报"),
    ("ai-daily-news-2026-03-20.html", "HTML", "2026-03-20日报，大哥反映内容和昨天有重叠", "日报"),
    ("daily_news_v2.html", "HTML", "嵌入CSS版日报，带完整报刊排版", "日报"),
    ("scifi_top10.html", "HTML", "科幻片Top10页面，赛博朋克风格，封面base64嵌入", "Project:科幻片Top10页面"),
    ("ai_agent_tutorial.html", "HTML", "AI Agent小白教程，村里话风格", "Project:AI-Agent教程"),
    ("google_stitch.html", "HTML", "Google Stitch AI UI设计工具介绍页", "Project:Google-Stitch研究"),
    ("google_stitch.html", "HTML", "Google Stitch研究，2026-03-20做的", "通用"),
]

seen = set()
for name, dtype, summary, *extra in docs:
    if name in seen: continue
    seen.add(name)
    path = f"/home/claw/.openclaw/workspace/{name}"
    if not os.path.exists(path): continue
    props = {"name": name, "path": path, "type": dtype, "summary": summary}
    e = create_entity("Document", props)
    records.append({"op": "create", "entity": e})

# === 技能 ===
skills = [
    ("newsletter-email", "~/.openclaw/workspace/skills/newsletter-email/", "发送日报HTML到QQ邮箱，支持完整报刊排版和UTF-8"),
    ("ai-daily-news", "~/.openclaw/workspace/skills/ai-daily-news/", "生成AI日报HTML，带报刊排版风格"),
    ("summarize", "npm:@steipete/summarize", "网页/PDF/YouTube内容摘要CLI工具"),
    ("ontology", "memory/ontology/", "知识图谱记忆系统，实体+关系建模"),
    ("federation-evolution", "skills/federation-evolution/", "联邦协同进化，bot间技能同步"),
    ("proactive-agent", "skills/proactive-agent-skill/", "主动Agent协议，包括WAL和Working Buffer"),
]

for name, loc, desc in skills:
    e = create_entity("Skill", {"name": name, "location": loc, "description": desc, "status": "installed"})
    records.append({"op": "create", "entity": e})

# === 事件 ===
events = [
    ("2026-03-20:科幻片Top10页面制作", "制作科幻片Top10 HTML页面，封面方案研究2小时"),
    ("2026-03-20:日报重叠问题", "大哥反映日报内容和前一天重叠，分析原因是cron+手动双来源"),
    ("2026-03-21:日报发送cron成功", "日报cron任务成功运行，今日头条：WordPress.com MCP协议"),
    ("2026-03-22:Figma-Context-MCP项目分析", "大哥给链接，让分析GLips/Figma-Context-MCP项目"),
    ("2026-03-21:AI-Agent小白教程", "给大哥制作AI Agent小白教程，村里话风格"),
    ("2026-03-22:Ontology初始化", "大哥让俺初始化ontology，把现有记忆整理成图谱"),
]

for title, desc in events:
    e = create_entity("Event", {"title": title, "description": desc, "date": title.split(":")[0]})
    records.append({"op": "create", "entity": e})

# === 知识碎片 ===
knowledge = [
    ("豆瓣封面抓取", "Douban图片CDN被Telegram拦截(418)，IMDB CDN可直接访问但部分返回9bytes，解决方案：用IMDB suggestion API获取正确poster URL，再下载嵌入HTML base64"),
    ("Telegram-HTML渲染", "Telegram不支持外部CSS，解决方案：把所有CSS内嵌到<style>标签里；图片用base64 data URI嵌入"),
    ("代理策略", "国内proxy(192.168.10.105:7890)可访问Douban API但不能访问Douban图片；无代理可直接访问IMDB CDN；ALL_PROXY=socks5h://192.168.10.105:7891"),
    ("Douban-API", "tag search: /j/search_subjects?tag=科幻&type=movie&page_limit=100&sort=time；detail: /j/subject_abstract?subject_id=；subject页面有JS反爬(PoW挑战)"),
    ("OpenClaw-架构", "Gateway桥接聊天App(Telegram/微信等)和AI模型；支持多session；cron任务走独立agent session；HEARTBEAT.md控制心跳任务"),
]

for topic, content in knowledge:
    e = create_entity("Knowledge", {"topic": topic, "content": content, "confidence": 0.95})
    records.append({"op": "create", "entity": e})

# === 关系 ===
relations = [
    ("per_绿豆", "created", "proj_日报"),
    ("per_绿豆", "created", "proj_科幻片"),
    ("per_绿豆", "created", "proj_ai-agent教程"),
    ("per_二狗", "created", "proj_日报"),
    ("per_二狗", "created", "proj_科幻片"),
    ("per_二狗", "created", "proj_ai-agent教程"),
    ("per_二狗", "created", "proj_figma-context"),
    ("per_二狗", "created", "doc_ai-daily"),
    ("per_二狗", "created", "doc_daily_news"),
    ("per_二狗", "created", "doc_scifi_top"),
    ("per_二狗", "created", "doc_ai_agent"),
    ("per_二狗", "created", "doc_google_st"),
    ("per_二狗", "created", "know_豆瓣封面"),
    ("per_二狗", "created", "know_telegram-ht"),
    ("per_二狗", "created", "know_代理策略"),
    ("per_二狗", "created", "know_douban-api"),
    ("per_二狗", "created", "know_openclaw-"),
    ("per_绿豆", "works_on", "proj_日报"),
    ("per_二狗", "works_on", "proj_日报"),
    ("per_二狗", "works_on", "proj_科幻片"),
    ("proj_日报", "part_of", "doc_ai-daily"),
    ("proj_日报", "part_of", "doc_daily_news"),
    ("proj_科幻片", "part_of", "doc_scifi_top"),
    ("proj_ai-agent教程", "part_of", "doc_ai_agent"),
    ("know_douban-api", "related_to", "know_豆瓣封面"),
    ("know_telegram-ht", "related_to", "know_豆瓣封面"),
]

for frm, rel, to in relations:
    records.append({"op": "relate", "from": frm, "rel": rel, "to": to})

# 写入
append_log(records)
print(f"✅ 初始化完成！共写入 {len(records)} 条记录")
print(f"   - 实体: {sum(1 for r in records if r['op']=='create')} 条")
print(f"   - 关系: {sum(1 for r in records if r['op']=='relate')} 条")
print(f"   存储位置: {GRAPH_FILE}")
