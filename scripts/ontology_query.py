#!/usr/bin/env python3
"""
Ontology Query — 展示记忆图谱内容
"""
import json, sys
from collections import defaultdict
from pathlib import Path

GRAPH_FILE = Path(__file__).parent.parent / "memory" / "ontology" / "graph.jsonl"

def load():
    entities = {}
    relations = []
    with open(GRAPH_FILE) as f:
        for line in f:
            rec = json.loads(line)
            if rec["op"] == "create":
                entities[rec["entity"]["id"]] = rec["entity"]
            else:
                relations.append(rec)
    return entities, relations

def query(keyword):
    entities, relations = load()
    keyword = keyword.lower()
    
    print(f"\n🔍 搜索: 「{keyword}」")
    print("=" * 50)
    
    # 找实体
    matched = []
    for id, e in entities.items():
        text = json.dumps(e, ensure_ascii=False).lower()
        if keyword in text:
            matched.append((id, e))
    
    if not matched:
        print("  没找到任何相关记录 😢")
        return
    
    for id, e in matched:
        print(f"\n📌 [{e['type']}] {id}")
        for k, v in e.get("properties", {}).items():
            if v:
                print(f"   {k}: {v}")
    
    # 找关系
    print(f"\n🔗 相关关系:")
    for r in relations:
        if keyword in r.get("from","").lower() or keyword in r.get("to","").lower() or keyword in r.get("rel","").lower():
            print(f"   {r['from']} ──({r['rel']})──→ {r['to']}")

def show_all():
    entities, relations = load()
    
    print(f"\n📊 记忆图谱总览")
    print(f"   实体总数: {len(entities)}")
    print(f"   关系总数: {len(relations)}")
    
    by_type = defaultdict(list)
    for id, e in entities.items():
        by_type[e["type"]].append(id)
    
    for type_, ids in sorted(by_type.items()):
        print(f"\n【{type_}】({len(ids)}个)")
        for id in ids:
            e = entities[id]
            name = e["properties"].get("name") or e["properties"].get("title") or id
            desc = e["properties"].get("description") or e["properties"].get("topic", "")
            if desc and len(desc) > 40:
                desc = desc[:40] + "..."
            print(f"   • {id}")
            if desc:
                print(f"     └─ {desc}")
    
    print(f"\n🔗 关系一览 ({len(relations)}条)")
    for r in relations:
        print(f"   {r['from']} ──({r['rel']})──→ {r['to']}")

def show_who(entity_id):
    entities, relations = load()
    print(f"\n👤 {entity_id} 的关系网络")
    print("=" * 50)
    
    # 这个实体发出的关系
    outgoing = [r for r in relations if r["from"] == entity_id]
    # 指向这个实体的关系
    incoming = [r for r in relations if r["to"] == entity_id]
    
    if entity_id in entities:
        e = entities[entity_id]
        print(f"\n📌 实体信息:")
        for k, v in e.get("properties", {}).items():
            if v:
                print(f"   {k}: {v}")
    
    if outgoing:
        print(f"\n🔶 主动关系 ({len(outgoing)}条):")
        for r in outgoing:
            target = entities.get(r["to"], {})
            target_name = target.get("properties", {}).get("name", r["to"])
            print(f"   → {r['rel']} → {r['to']} ({target_name})")
    
    if incoming:
        print(f"\n🔷 被动关系 ({len(incoming)}条):")
        for r in incoming:
            source = entities.get(r["from"], {})
            source_name = source.get("properties", {}).get("name", r["from"])
            print(f"   ← {r['from']} ({source_name}) ──{r['rel']}──")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    arg = sys.argv[2] if len(sys.argv) > 2 else ""
    
    if cmd == "all":
        show_all()
    elif cmd == "who":
        show_who(arg)
    elif cmd == "search":
        query(arg)
    else:
        print("用法: ontology_query.py [all|who <id>|search <keyword>]")
