# 🎯 Complete Setup Checklist - Streamlined Rules System

## Current Status
✅ Project rules streamlined (.cursorrules: 111KB → 6KB)
✅ 4 new Project Command scripts created
✅ Documentation created

---

## 📋 What You Need To Do (10 minutes)

### ✅ Step 1: Fix User Rules (2 min)

**Problem:** You still have the OLD user rule that tells AI to read raw text files.

**Fix:**
1. Open Cursor Settings: `Ctrl+,`
2. Go to: **Features** → **Rules for AI** → **User Rules**
3. **DELETE** this rule:
   > "Always check against the dungeon master text document and monster manual text document and..."
4. Click **"+ Add Rule"**
5. **Copy/paste this:**

```
# D&D DM - Natural Behavior

You are an experienced DM running D&D 5e (2024). You narrate naturally, use tools silently, and keep the game flowing.

DO:
- Speak as a DM: "You enter the room...", "Roll initiative..."
- Use MCP servers silently (lookup_spell, lookup_monster, lookup_condition, lookup_rule)
- Describe scenes vividly and concisely
- Process enemy turns automatically

DON'T:
- Announce tool usage: ❌ "Let me check the database..." ✅ Just use it
- Recite rules verbatim unless asked
- Explain internal processes or system architecture
- Break character to discuss tooling

When You Need Info:
1. Check source (MCP/sheets/state) silently
2. Make ruling
3. Continue DMing

When Info Missing:
BLOCK briefly, don't guess.
Example: "BLOCKED: Monster stats not found."

Philosophy:
User wants to play D&D, not discuss system architecture.
Be a DM first, system second.
Tools are invisible to players.
```

6. Click **Save**

---

### ✅ Step 2: Add Project Rule (2 min)

**Currently:** "No Project Rules Yet"

**Fix:**
1. Still in Settings → **Project Rules**
2. Click **"+ Add Rule"**
3. **Copy/paste this:**

```
# DnD_Cursor Project Rules

Session Start:
1. Read CURRENT_STATE.json (C:\DnD\Campaigns\<campaign>\saves\)
2. Read CAMPAIGN_EVENTS.json
3. Read SESSION_START_GUIDE.md
4. Verify MCP servers active
5. Begin DMing from current state

Mandatory Tools (MCP Servers):
- lookup_spell(name) - Spell info
- lookup_monster(name) - Monster stats  
- lookup_condition(name) - Condition effects
- lookup_rule(name) - D&D rules
- search_spells/monsters/rules(query) - Searches
- search_sourcebooks(query, "phb"/"dmg"/"mm") - Full text

NEVER invent D&D mechanics. Use MCP servers.

Output Format (PLAY MODE):
NARRATION: <What players see/hear/experience>
ASK: <Rolls needed, decisions required>
ACTIONS: <Suggested player actions>

Data Priority:
1. Google Sheets (HP/resources/conditions)
2. MCP servers (rules/spells/monsters)
3. Campaign state (CURRENT_STATE.json)
4. Chapter packs (NPCs/locations/encounters)

Combat:
Use parallel agent system with FastMode flags.
Target: <5 seconds per turn.

Forbidden:
❌ Invent mechanics (use MCP)
❌ Read raw .txt files in PLAY mode
❌ Skip gates
❌ Reveal GM knowledge
❌ Guess character stats
```

4. Click **Save**

---

### ✅ Step 3: Add Project Commands (5 min)

**Currently:** You have 3 commands (session_init, turn_merge, turn_parallel)

**Add 4 more:**

#### In Settings → **Project Commands**, click "+ Add Command" for each:

**Command 1: State Check**
- Name: `dnd_state_check`
- Command: 
```
powershell -ExecutionPolicy Bypass -File "C:\DnD\DnD_Cursor\scripts\dnd_state_check.ps1" -Campaign "Phandelver"
```

**Command 2: Backup**
- Name: `dnd_backup`
- Command:
```
powershell -ExecutionPolicy Bypass -File "C:\DnD\DnD_Cursor\scripts\dnd_backup.ps1" -Campaign "Phandelver"
```

**Command 3: Validate**
- Name: `dnd_validate`
- Command:
```
powershell -ExecutionPolicy Bypass -File "C:\DnD\DnD_Cursor\scripts\dnd_validate.ps1" -Campaign "Phandelver"
```

**Command 4: MCP Test**
- Name: `dnd_mcp_test`
- Command:
```
powershell -ExecutionPolicy Bypass -File "C:\DnD\DnD_Cursor\scripts\dnd_mcp_test.ps1"
```

---

### ✅ Step 4: Restart Cursor (1 min)

**Close Cursor completely** (not just this window), then **reopen**.

---

## 🧪 Testing (After Restart)

### Test 1: Check Commands
Press `Ctrl+Shift+P` and type:
- `dnd_state_check` → Should show campaign state
- `dnd_backup` → Should create backup
- `dnd_validate` → Should validate files
- `dnd_mcp_test` → Should show test commands

### Test 2: Check Rules
In a NEW chat, say:
> "We enter the tavern"

**Expected (Good):**
```
NARRATION:
The warm glow of the Stonehill Inn's hearth welcomes you...

ASK:
What do you do?

ACTIONS:
- Approach the bar
- Find a table
- Look for NPCs
```

**NOT Expected (Bad):**
> "Let me check the chapter pack for tavern details. I'll use the read_file tool to access C:\DnD\..."

### Test 3: Check MCP Usage
In chat, say:
> "Can Torgga cast Fireball?"

**Expected (Good):**
> "No, Fireball is a Sorcerer/Wizard spell. Torgga (Cleric) cannot cast it."

**NOT Expected (Bad):**
> "Let me use the lookup_spell MCP function to check..."

---

## 📊 Before vs After Summary

| Aspect | Before | After |
|--------|--------|-------|
| **User Rules** | "Check text documents..." (OLD) | "Be a DM first, system second" (NEW) |
| **Project Rules** | None | Core D&D principles (NEW) |
| **.cursorrules** | 1,916 lines (111 KB) | 150 lines (6 KB) |
| **Project Commands** | 3 (init, merge, parallel) | 7 (added state, backup, validate, test) |
| **AI Behavior** | Explains tooling | Acts naturally as DM |

---

## ✅ Checklist Summary

- [ ] **User Rules:** Delete old rule, add new DM behavior rule
- [ ] **Project Rules:** Add core D&D principles
- [ ] **Commands:** Add 4 new commands (state/backup/validate/test)
- [ ] **Restart:** Close and reopen Cursor completely
- [ ] **Test:** Try "We enter the tavern" in new chat
- [ ] **Verify:** AI acts naturally, doesn't explain tooling

---

## 📚 Reference Files Created

| File | Purpose |
|------|---------|
| `.cursorrules` | Streamlined project rules (ACTIVE) |
| `.cursorrules_BACKUP_20260113_103741` | Original backup |
| `CURSOR_USER_RULES.md` | User rules text reference |
| `CURSOR_RULES_SETUP.md` | Detailed setup guide |
| `IMPLEMENT_STREAMLINED_RULES.md` | Quick start guide |
| `ADD_PROJECT_COMMANDS.md` | Command setup guide |
| `PROJECT_COMMANDS_RECOMMENDATIONS.md` | Future command ideas |
| `scripts/dnd_state_check.ps1` | State overview script |
| `scripts/dnd_backup.ps1` | Backup script |
| `scripts/dnd_validate.ps1` | Validation script |
| `scripts/dnd_mcp_test.ps1` | MCP test script |

---

## 🎯 Goal

**AI will:**
- ✅ Act as a natural, experienced DM
- ✅ Use tools silently (MCP servers, scripts)
- ✅ Focus on narration and gameplay
- ✅ Never announce internal processes

**You will:**
- ✅ Play D&D, not discuss system architecture
- ✅ Get seamless, engaging gameplay
- ✅ Have quick access to state/backup/validation

---

## 🚀 Next Steps

1. Complete the checklist above
2. Test in a new chat
3. If AI still explains tooling → check User Rules were saved
4. If AI doesn't use MCP → check Project Rules were saved
5. If commands don't work → check paths in command definitions

**Once all checkboxes are ✅, your streamlined DM system is ready!** 🎉










