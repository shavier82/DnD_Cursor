# Real-Time Obsidian Sync During Combat

## Overview

The combat-engine now **automatically syncs** combat data to Obsidian character sheets in real-time, ensuring that HP, conditions, spell slots, and resources are always up-to-date.

## How It Works

### **1. Real-Time HP Sync (Automatic)**

When a player character takes damage:

```
1. attack_tool → Damage dealt → HP reduced in combat state
2. AUTOMATICALLY → sync_hp_to_obsidian() → Obsidian file updated
3. Result includes "obsidian_synced": true
```

**Example:**
- Torgga takes 17 damage (52 → 35 HP)
- Obsidian file `Torgga_Brawnanvil.md` is instantly updated: `**HP: 35/52`
- Player/DM can see current HP in Obsidian during play

### **2. End-of-Combat Batch Sync**

When combat ends via `end_combat_tool`:

```
- All player HP synced to Obsidian
- Spell slots synced (TODO)
- Conditions synced (TODO)
- Resources synced (TODO)
```

## Synced Data

### ✅ **Currently Synced:**
- **HP**: Updated in real-time after every attack
- **Max HP**: Tracked for leveling/temp HP changes

### 🚧 **Coming Soon:**
- **Conditions**: Grappled, Prone, Stunned, etc.
- **Spell Slots**: Track usage per level (1-9)
- **Class Resources**:
  - Barbarian: Rage uses
  - Monk: Ki points
  - Cleric: Channel Divinity
  - Fighter: Action Surge, Second Wind
  - Warlock: Pact slots

## File Format

Obsidian character sheets are updated via regex pattern matching:

### **HP Update:**
```markdown
**HP: 35/52     ← Updated in real-time
```

### **Conditions (Planned):**
```markdown
## Active Conditions
- **Grappled** (by Goblin 1)
- **Blessed** (3 rounds remaining)
```

### **Spell Slots (Planned):**
```yaml
---
spell_slots:
  level_1: 3  ← Updated when spells cast
  level_2: 2
  level_3: 1
---
```

### **Resources (Planned):**
```markdown
**Rage:** 2/3
**Ki Points:** 5/5
**Channel Divinity:** 1/1
```

## Migration from Google Sheets

**Before:**
- Combat-engine synced to Google Sheets via API
- Required OAuth credentials
- Network-dependent

**Now:**
- Combat-engine writes directly to Obsidian `.md` files
- No API calls needed
- Works offline
- Git-friendly (can commit character changes)

## Architecture

```
combat-engine/utils/obsidian_sync.py
├── ObsidianSync class
│   ├── update_hp()              ✅ Active
│   ├── add_condition()          🚧 Ready
│   ├── remove_condition()       🚧 Ready
│   ├── update_spell_slots()     🚧 Ready
│   └── update_resource()        🚧 Ready
│
└── Convenience functions:
    ├── sync_hp_to_obsidian()
    ├── sync_condition_to_obsidian()
    ├── sync_spell_slots_to_obsidian()
    └── sync_resource_to_obsidian()
```

## Usage in Combat

### **DM Perspective:**
1. Start combat → Characters loaded
2. Attacks happen → HP updates automatically in Obsidian
3. Player checks their sheet in Obsidian → sees current HP
4. End combat → Final sync ensures everything is saved

### **Player Perspective:**
- Open Obsidian during play
- Watch HP change in real-time as combat progresses
- See conditions applied/removed
- Track resources used

## Benefits

✅ **Real-time visibility**: Players can see their HP in Obsidian during combat  
✅ **Automatic tracking**: No manual HP updates needed  
✅ **Persistent state**: Character state saved between sessions  
✅ **Version control**: Commit character changes to Git  
✅ **No API calls**: Fast, local file writes  
✅ **Human-readable**: Markdown format, easy to edit manually  

## Future Enhancements

### **Condition Tracking:**
```python
# When condition applied:
sync_condition_to_obsidian("Torgga_Brawnanvil", "Stunned", "1 round")

# When condition removed:
remove_condition_from_obsidian("Torgga_Brawnanvil", "Stunned")
```

### **Spell Slot Tracking:**
```python
# When spell cast:
sync_spell_slots_to_obsidian("Torgga_Brawnanvil", level=2, slots_remaining=1)
```

### **Resource Tracking:**
```python
# When rage used:
sync_resource_to_obsidian("Eglath_Bearkiller", "Rage", current=2, maximum=3)
```

## Configuration

**Vault Path**: `C:/Users/ksist/Documents/Obsidian`  
**Characters Path**: `DnD/Player Characters/`  
**Character Name Format**: `FirstName_LastName.md`

To change vault path, edit:
```python
# mcp_servers/combat_engine/utils/obsidian_sync.py
def __init__(self, vault_path: str = "C:/YOUR/PATH/HERE"):
```

## Testing

To test the sync:
1. Start a combat encounter
2. Attack a player character
3. Check their `.md` file in Obsidian → HP should be updated
4. End combat → Verify final HP is correct

## Summary

**Real-time Obsidian sync ensures that combat changes are immediately reflected in character sheets, providing live visibility during play and automatic persistence between sessions.**

🎯 **Your character sheets are always up-to-date!**
