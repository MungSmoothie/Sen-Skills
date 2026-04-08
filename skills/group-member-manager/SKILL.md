---
name: group-member-manager
description: Manage group chat member nicknames and identity mapping. Use when: (1) A new member joins and introduces themselves, (2) Someone tells the bot to call them a specific name, (3) Someone changes their display name or alias in group chat. Triggers on patterns like "我是XXX", "叫我XXX", "以后叫我XXX", "叫XXX就好", "新成员", "加入群", or any request to set/change a nickname.
---

# Group Member Manager

Maintains the group member ID → nickname mapping table in `AGENTS.md`.

## Trigger Patterns

Activate when user says something matching:

- "我是XXX" / "我叫XXX" / "我叫YYY，XXX" → Register new member
- "叫我XXX" / "以后叫我XXX" / "叫XXX就好" → Update own nickname
- "XXX 以后叫XXX" → Rename another member (admin only)
- "新成员" / "加入群" / "进群了" → New member joined

## ⚠️ 重要规则：验证后再修改

**修改映射关系之前，必须先让对方发送 `/whoami`，获得真实的 sender_id 进行比对，确认身份后再修改。不要仅凭名字或语气判断身份。**

---

## Action Rules

### New Member Registration
When a new member is detected (sender_id not in mapping):
1. Extract name from message (parse "我是XXX" or similar)
2. Add entry to AGENTS.md mapping table
3. Reply: "欢迎XXX，记录好了 ✅"

### Nickname Update
When member requests nickname change:
1. Extract new nickname from message
2. Update existing entry in AGENTS.md mapping table
3. Reply: "好的，以后叫你XXX ✅"

### Cross-member Rename (Admin Only)
When renaming someone else (must be kano or 杨):
1. Confirm admin permission
2. Find target by old name or ID
3. Update entry in AGENTS.md
4. Reply: "已将YYY改名为XXX ✅"

## AGENTS.md Update Procedure

1. Read current AGENTS.md
2. Find the mapping table section (between `群口情报社 成员 ID 映射：` and next `###`)
3. Edit using exact text replacement (edit tool)
4. Format: `- \`sender_id\` = 名字 (可选备注)`

## Format Rules

- ID in backticks: \`123456789\`
- Name in plain text
- Optional note in parentheses after name
- One entry per line, bullet list format

## Example

群口情报社 成员 ID 映射：
- \`8652589172\` = 开哥
- \`7917279907\` = 绿豆冰沙 (森哥)
- \`1245445176\` = 杨 (开发者)
