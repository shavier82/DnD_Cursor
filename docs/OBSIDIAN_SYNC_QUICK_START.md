# Obsidian Sync MCP - Quick Start Guide

**Real-time D&D campaign data in Obsidian**

---

## ✅ Phase 1: COMPLETE

### What's Working Now

- ✅ **Character Data CRUD** - Read/write character sheets from Obsidian
- ✅ **HP Updates** - Real-time HP tracking during combat
- ✅ **Resource Tracking** - Update spell slots, rage, ki points, etc.
- ✅ **Condition Management** - Add/remove status conditions
- ✅ **Health Status Converter** - Enemy HP → descriptive status
- ✅ **File Watcher** - Monitor Obsidian vault for changes

---

## Quick Test

### 1. Restart Cursor
Close and reopen Cursor to load the new `obsidian-sync` MCP.

### 2. Get All Characters
```python
get_all_characters()
```

**Expected output:**
```json
{
  "total_characters": 5,
  "characters": [
    {
      "name": "Eglath Bearkiller",
      "class": "Barbarian",
      "level": 5,
      "hp_current": 65,
      "hp_max": 65,
      "conditions": []
    },
    ...
  ]
}
```

### 3. Get Character Data
```python
get_character_data("Eglath Bearkiller")
```

Returns full character sheet with metadata and content.

### 4. Update HP (Combat Damage)
```python
update_character_hp(
    character_name="Eglath Bearkiller",
    current_hp=58,
    max_hp=65
)
```

**Check Obsidian** - HP line updates instantly!

### 5. Enemy Health Status
```python
convert_hp_to_status(current_hp=15, max_hp=30)
```

**Returns:** `"Bloodied"`

Players see: **"Goblin: Bloodied"** (not exact HP)

### 6. Add Condition
```python
add_condition("Torgga Brawnanvil", "Poisoned")
```

---

## Character Sheet Format

### File: `C:\DnD\Obsidian_Vault\Player Characters\Eglath_Bearkiller.md`

```markdown
---
type: player_character
class: Barbarian
level: 5
hp_current: 65
hp_max: 65
ac: 20
conditions: []
---

# Eglath Bearkiller

## Combat Stats

**HP:** 65/65
**AC:** 20
**Initiative:** +3

## Ability Scores

| Stat | Score | Modifier |
|------|-------|----------|
| STR  | 19 | +4 |
| DEX  | 16 | +3 |
| CON  | 15 | +2 |
...
```

---

## Health Status Mapping

| HP % | Status | Visual |
|------|--------|--------|
| 90-100% | Healthy | ●●●●● |
| 70-89% | Hurt | ●●●●○ |
| 50-69% | Bloodied | ●●●○○ |
| 25-49% | Critical | ●●○○○ |
| 1-24% | Near Death | ●○○○○ |
| 0% | Unconscious | ○○○○○ |

---

## Integration with Other MCPs

### Combat Engine (Phase 2 - Next)
```python
# Combat Engine will automatically call:
obsidian_sync.update_character_hp("Eglath", 58, 65)
obsidian_sync.convert_hp_to_status(goblin_hp, goblin_max_hp)
```

### Session Recorder (Phase 4 - Future)
```python
# After combat, log to Obsidian:
obsidian_sync.create_encounter_log(encounter_data)
```

---

## File Watcher (Real-time Sync)

### Start Watching
```python
start_vault_watch()
```

Monitors `C:\DnD\Obsidian_Vault` for changes. When you edit a character sheet in Obsidian, changes are detected and can trigger syncs to other systems.

### Stop Watching
```python
stop_vault_watch()
```

---

## Common Workflows

### During Combat

1. Enemy attacks Eglath for 7 damage:
```python
update_character_hp("Eglath Bearkiller", 58, 65)
```

2. Eglath gains temp HP from spell:
```python
update_character_hp("Eglath Bearkiller", 58, 65, temp_hp=10)
```

3. Torgga gets poisoned:
```python
add_condition("Torgga Brawnanvil", "Poisoned")
```

4. Check goblin health status:
```python
convert_hp_to_status(12, 50)  # Returns "Critical"
```

### After Combat

1. Remove conditions:
```python
remove_condition("Torgga Brawnanvil", "Poisoned")
```

2. Check all character status:
```python
get_all_characters()
```

### Between Sessions

1. Update character after level-up:
   - Manually edit Obsidian file (HP, level, features)
   - File watcher detects change
   - Other systems sync automatically (Phase 3)

---

## Next: Phase 2 (Combat Engine Integration)

**Goals:**
1. Remove Google Sheets from Combat Engine
2. Combat Engine reads PC stats from Obsidian
3. Combat Engine writes HP/resource updates to Obsidian
4. Enemy health displayed as descriptive status

**This makes combat updates instant and visible in Obsidian!** ⚔️

---

## Next: Phase 3 (Real-Time Sync)

**Goals:**
1. Batch update system (multiple changes in one write)
2. Conflict resolution (handle concurrent edits)
3. Auto-sync every 30 seconds during session
4. Propagate changes to other MCPs

---

## Next: Phase 4 (Session Integration)

**Goals:**
1. Session Recorder → Obsidian session notes
2. Campaign Events → Timeline
3. Auto-create encounter logs after combat
4. Quest progress tracking

---

**Your campaign now lives in Obsidian with real-time updates!** 📚✨

**Restart Cursor and test it out!** 🚀




