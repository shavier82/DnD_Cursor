# Add Project Commands to Cursor - Step by Step

## ✅ Scripts Created (Ready to Use)
- `scripts/dnd_state_check.ps1` - Quick state overview
- `scripts/dnd_backup.ps1` - Backup campaign saves
- `scripts/dnd_validate.ps1` - Validate JSON files
- `scripts/dnd_mcp_test.ps1` - Test MCP servers

---

## 📋 How to Add Commands to Cursor

### Method 1: Via Cursor UI (Recommended)

1. **Open Cursor Settings:**
   - Press `Ctrl+,`

2. **Navigate to:**
   - **Features** → **Project Commands**

3. **For each command below, click "+ Add Command":**

---

#### Command 1: State Check
- **Name:** `dnd_state_check`
- **Command:**
```powershell
powershell -ExecutionPolicy Bypass -File "C:\DnD\DnD_Cursor\scripts\dnd_state_check.ps1" -Campaign "Phandelver"
```
- **Description:** Quick campaign state overview

---

#### Command 2: Backup
- **Name:** `dnd_backup`
- **Command:**
```powershell
powershell -ExecutionPolicy Bypass -File "C:\DnD\DnD_Cursor\scripts\dnd_backup.ps1" -Campaign "Phandelver"
```
- **Description:** Create timestamped backup of campaign saves

---

#### Command 3: Validate
- **Name:** `dnd_validate`
- **Command:**
```powershell
powershell -ExecutionPolicy Bypass -File "C:\DnD\DnD_Cursor\scripts\dnd_validate.ps1" -Campaign "Phandelver"
```
- **Description:** Validate state file integrity

---

#### Command 4: MCP Test
- **Name:** `dnd_mcp_test`
- **Command:**
```powershell
powershell -ExecutionPolicy Bypass -File "C:\DnD\DnD_Cursor\scripts\dnd_mcp_test.ps1"
```
- **Description:** Show MCP server test commands

---

### Method 2: Via .vscode/settings.json (Advanced)

Create or edit `.vscode/settings.json` in your workspace:

```json
{
  "cursor.commands": {
    "dnd_state_check": {
      "command": "powershell -ExecutionPolicy Bypass -File \"C:\\DnD\\DnD_Cursor\\scripts\\dnd_state_check.ps1\" -Campaign \"Phandelver\"",
      "description": "Quick campaign state overview"
    },
    "dnd_backup": {
      "command": "powershell -ExecutionPolicy Bypass -File \"C:\\DnD\\DnD_Cursor\\scripts\\dnd_backup.ps1\" -Campaign \"Phandelver\"",
      "description": "Create timestamped backup"
    },
    "dnd_validate": {
      "command": "powershell -ExecutionPolicy Bypass -File \"C:\\DnD\\DnD_Cursor\\scripts\\dnd_validate.ps1\" -Campaign \"Phandelver\"",
      "description": "Validate state files"
    },
    "dnd_mcp_test": {
      "command": "powershell -ExecutionPolicy Bypass -File \"C:\\DnD\\DnD_Cursor\\scripts\\dnd_mcp_test.ps1\"",
      "description": "Test MCP servers"
    }
  }
}
```

---

## 🧪 Test Commands

After adding, test each command:

1. Press `Ctrl+Shift+P` (Command Palette)
2. Type the command name (e.g., `dnd_state_check`)
3. Press Enter

**Expected Results:**

### `dnd_state_check`
```
=== CURRENT STATE ===
Location: Phandalin - Stonehill Inn
Chapter: 5
Combat Active: False
Current Turn: 0

=== RECENT EVENTS (Last 5) ===
[2026-01-13T10:15:00] Party arrived in Phandalin
[2026-01-13T10:20:00] Spoke with Toblen Stonehill
...
```

### `dnd_backup`
```
✅ Backed up: CURRENT_STATE_20260113_104500.json
✅ Backed up: CAMPAIGN_EVENTS_20260113_104500.json

✅ Backup complete: 20260113_104500
Location: C:\DnD\Campaigns\Phandelver\backups
```

### `dnd_validate`
```
=== VALIDATING STATE FILES ===

Checking: CURRENT_STATE.json
  ✅ Valid JSON
  📊 Size: 12.5 KB
  🕒 Last modified: 1/13/2026 10:30:00 AM

Checking: CAMPAIGN_EVENTS.json
  ✅ Valid JSON
  📊 Size: 45.2 KB
  🕒 Last modified: 1/13/2026 10:30:00 AM

✅ All state files valid!
```

### `dnd_mcp_test`
```
=== MCP SERVER TEST ===
Copy/paste these commands into the AI chat:

1️⃣ DICE ROLLER:
   roll_dice("2d6+3", "Test roll")

2️⃣ MONSTER LOOKUP:
   lookup_monster("Goblin")
...
```

---

## 🎯 When to Use Each Command

| Command | Use Case | Frequency |
|---------|----------|-----------|
| `dnd_state_check` | Before starting session | Every session |
| `dnd_backup` | Before major story decisions | Every session |
| `dnd_validate` | After manual state edits | As needed |
| `dnd_mcp_test` | After Cursor restart | As needed |
| `dnd_session_init` | Start new session (existing) | Every session |
| `dnd_turn_parallel` | Run combat turn (existing) | Every combat turn |
| `dnd_turn_merge` | Merge agent outputs (existing) | Every combat turn |

---

## 🚀 Recommended Workflow

### Session Start:
1. `dnd_backup` - Create safety backup
2. `dnd_validate` - Ensure files are valid
3. `dnd_state_check` - Review current state
4. `dnd_session_init` - Initialize session (if using manual mode)
5. Start DMing in chat

### During Combat:
1. `dnd_turn_parallel` - Process turn
2. `dnd_turn_merge` - Apply changes
3. Repeat for each turn

### After Session:
1. `dnd_backup` - Save final state
2. `dnd_validate` - Verify integrity

---

## 💡 Future Command Ideas

Consider adding these later:
- `dnd_chapter_load` - Load specific chapter pack
- `dnd_npc_lookup` - Quick NPC info
- `dnd_quest_status` - Show active quests
- `dnd_inventory_sync` - Update character inventories
- `dnd_hp_check` - Quick HP status for party
- `dnd_conditions_list` - Show active conditions

---

## ✅ Setup Checklist

- [ ] Add User Rule (delete old "check text documents" rule)
- [ ] Add Project Rule
- [ ] Add `dnd_state_check` command
- [ ] Add `dnd_backup` command
- [ ] Add `dnd_validate` command
- [ ] Add `dnd_mcp_test` command
- [ ] Test all commands
- [ ] Restart Cursor

**Once complete, your Cursor DM setup will be fully optimized!** 🎉










