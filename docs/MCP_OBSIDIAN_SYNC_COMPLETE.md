# Obsidian Sync MCP - Complete Documentation

**MCP Server:** `obsidian-sync`  
**Status:** Phase 1 Complete ✅

---

## Overview

The Obsidian Sync MCP makes Obsidian the **single source of truth** for your entire D&D campaign. It replaces Google Sheets and provides real-time character data updates, combat state synchronization, and session integration.

---

## Tools (9 total)

### Character Data Operations

#### `get_character_data(character_name)`
Read complete character data from Obsidian.

**Parameters:**
- `character_name` (string) - Character name (e.g., "Eglath Bearkiller")

**Returns:**
```json
{
  "metadata": {
    "type": "player_character",
    "class": "Barbarian",
    "level": 5,
    "hp_current": 65,
    "hp_max": 65,
    "ac": 20,
    "conditions": []
  },
  "content": "# Eglath Bearkiller\n\n...",
  "file_path": "C:/DnD/Obsidian_Vault/Player Characters/Eglath_Bearkiller.md"
}
```

---

#### `get_all_characters()`
Get summary of all player characters.

**Returns:**
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
    }
  ]
}
```

---

#### `update_character_hp(character_name, current_hp, max_hp, temp_hp)`
Update character HP in real-time (for combat).

**Parameters:**
- `character_name` (string) - Character name
- `current_hp` (integer) - Current HP
- `max_hp` (integer, optional) - Maximum HP (if changed)
- `temp_hp` (integer, default 0) - Temporary HP

**Updates:**
- Metadata: `hp_current`, `hp_max`, `hp_temp`, `last_updated`
- Content: HP line in markdown

**Example:**
```python
update_character_hp("Eglath Bearkiller", 58, 65, temp_hp=5)
```

---

#### `update_character_resources(character_name, resources)`
Update character resources (spell slots, rage, ki, etc.).

**Parameters:**
- `character_name` (string) - Character name
- `resources` (object) - Resource updates

**Example:**
```python
update_character_resources("Torgga Brawnanvil", {
  "spell_slots_1": {"current": 2, "max": 4},
  "channel_divinity": {"current": 0, "max": 1}
})
```

---

#### `add_condition(character_name, condition)`
Add status condition to character.

**Parameters:**
- `character_name` (string) - Character name
- `condition` (string) - Condition name (e.g., "Poisoned", "Stunned")

**Example:**
```python
add_condition("Brevin", "Frightened")
```

---

#### `remove_condition(character_name, condition)`
Remove status condition from character.

**Parameters:**
- `character_name` (string) - Character name
- `condition` (string) - Condition name

**Example:**
```python
remove_condition("Brevin", "Frightened")
```

---

### Health Status Converter

#### `convert_hp_to_status(current_hp, max_hp)`
Convert enemy HP to descriptive status (players don't see exact numbers).

**Parameters:**
- `current_hp` (integer) - Current HP
- `max_hp` (integer) - Maximum HP

**Returns:**
```json
{
  "current_hp": 15,
  "max_hp": 30,
  "status": "Bloodied"
}
```

**Status Mapping:**
- **90-100%** → `"Healthy"`
- **70-89%** → `"Hurt"`
- **50-69%** → `"Bloodied"`
- **25-49%** → `"Critical"`
- **1-24%** → `"Near Death"`
- **0%** → `"Unconscious"`
- **<0%** → `"Dead"`

---

### File Watcher

#### `start_vault_watch()`
Start monitoring Obsidian vault for file changes (real-time sync).

**Returns:**
```json
{
  "success": true,
  "message": "Watching Obsidian vault: C:/DnD/Obsidian_Vault"
}
```

**Features:**
- Monitors all files in vault
- Debounces rapid changes (2-second window)
- Logs file modifications
- Can trigger syncs to other MCPs (Phase 3)

---

#### `stop_vault_watch()`
Stop monitoring Obsidian vault.

**Returns:**
```json
{
  "success": true,
  "message": "Stopped watching Obsidian vault"
}
```

---

## Data Flow

### Write to Obsidian (Combat → Obsidian)

```
Combat Engine
    ↓
    ↓ update_character_hp()
    ↓
Obsidian Sync MCP
    ↓
    ↓ Write to .md file
    ↓
Obsidian Vault (C:\DnD\Obsidian_Vault\)
```

### Read from Obsidian (Obsidian → Combat)

```
Obsidian Vault (user edits character sheet)
    ↓
    ↓ File watcher detects change
    ↓
Obsidian Sync MCP
    ↓
    ↓ get_character_data()
    ↓
Combat Engine / Campaign Wiki
```

---

## Character Sheet Structure

### Frontmatter (Metadata)

```yaml
---
type: player_character
class: Barbarian
level: 5
race: Goliath
player: Player Name
xp: 7260
hp_current: 65
hp_max: 65
hp_temp: 0
ac: 20
initiative_bonus: 3
proficiency_bonus: 3
speed: 40
conditions: []
resources:
  rage:
    current: 3
    max: 3
last_updated: "2026-01-13T15:30:00"
tags:
  - pc
  - character
---
```

### Markdown Content

```markdown
# Eglath Bearkiller

## Quick Stats

**Class:** Barbarian 5
**Race:** Goliath

## Combat Stats

**HP:** 65/65
**AC:** 20
**Initiative:** +3
**Speed:** 40 ft
**Proficiency Bonus:** +3

## Ability Scores

| Stat | Score | Modifier |
|------|-------|----------|
| STR  | 19 | +4 |
| DEX  | 16 | +3 |
| CON  | 15 | +2 |
| INT  | 12 | +1 |
| WIS  | 10 | +0 |
| CHA  | 8 | -1 |

## Class Resources

**Rage:** ●●● (3/3)

## Features

- Rage (3/day)
- Unarmored Defense
- Reckless Attack
- Danger Sense
- Primal Path
- Extra Attack
- Fast Movement
```

---

## Integration with Other MCPs

### Combat Engine (Phase 2)

**Combat Engine will:**
1. Read PC stats from Obsidian at combat start
2. Update HP/resources in Obsidian during combat
3. Display enemy health as descriptive status
4. Remove all Google Sheets dependencies

---

### Session Recorder (Phase 4)

**Session Recorder will:**
1. Create session notes in `Obsidian_Vault/Sessions/`
2. Link encounters, NPCs, locations
3. Update timeline events
4. Track quest progress

---

### Campaign Wiki (Phase 4)

**Campaign Wiki will:**
1. Sync NPCs, locations, quests to Obsidian
2. Read from Obsidian for relationship graphs
3. Generate Obsidian Graph View connections

---

## Error Handling

### Character Not Found
```json
{
  "error": "Character 'Unknown Name' not found"
}
```

### File System Error
```json
{
  "error": "Permission denied: C:/DnD/Obsidian_Vault/..."
}
```

### Watchdog Not Installed
```json
{
  "error": "Watchdog library not installed. Run: pip install watchdog"
}
```

---

## Performance

- **Read Operations:** <10ms (markdown parsing)
- **Write Operations:** <50ms (file I/O)
- **File Watcher:** Real-time (2-second debounce)
- **Batch Updates:** Planned for Phase 3

---

## Roadmap

### ✅ Phase 1: Core Infrastructure (COMPLETE)
- File watcher
- Markdown parser/writer
- Character data CRUD
- Health status converter

### 🔄 Phase 2: Combat Engine Integration (NEXT)
- Remove Google Sheets from Combat Engine
- Read PC stats from Obsidian
- Write combat updates to Obsidian
- Enemy health as descriptive status

### 📋 Phase 3: Real-Time Sync (PLANNED)
- Batch update system
- Conflict resolution
- Auto-sync on interval (30s)
- Change propagation to other MCPs

### 📋 Phase 4: Session Integration (PLANNED)
- Session Recorder → Obsidian
- Campaign Events → Timeline
- Encounter logging
- Quest progress tracking

---

## Testing

See `docs/OBSIDIAN_SYNC_QUICK_START.md` for test scenarios.

**Basic Test:**
1. `get_all_characters()` - Verify 5 PCs loaded
2. `update_character_hp("Eglath Bearkiller", 58, 65)` - Verify HP updates
3. Check Obsidian file - Verify markdown updated
4. `add_condition("Brevin", "Poisoned")` - Verify condition added
5. `convert_hp_to_status(15, 30)` - Verify returns "Bloodied"

---

**Obsidian is now your campaign's living database!** 📚✨

**Total MCP Tools:** 9  
**Next:** Phase 2 - Combat Engine Integration




