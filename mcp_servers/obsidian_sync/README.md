# Obsidian Sync MCP Server

**Real-time synchronization service for D&D campaign data in Obsidian vault**

---

## Purpose

The Obsidian Sync MCP is the **central data layer** for the entire D&D system. It:
- Makes Obsidian the **single source of truth** for all campaign data
- Provides real-time character data updates during combat
- Watches for file changes and syncs to other systems
- Converts enemy HP to descriptive status for players
- Integrates with Combat Engine, Session Recorder, and Campaign Wiki

---

## Architecture

```
┌─────────────────────────────────────────┐
│    OBSIDIAN VAULT (Source of Truth)    │
│  - Player Characters/*.md               │
│  - NPCs/*.md                            │
│  - Encounters/*.md                      │
│  - Sessions/*.md                        │
└─────────────────────────────────────────┘
                  ▲
                  │
        ┌─────────┴─────────┐
        │ Obsidian Sync MCP │
        │  (File Watcher)   │
        └─────────┬─────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼────┐  ┌────▼─────┐  ┌───▼────┐
│ Combat │  │ Campaign │  │Session │
│ Engine │  │   Wiki   │  │Recorder│
└────────┘  └──────────┘  └────────┘
```

---

## Phase 1: Core Infrastructure ✅

### Tools

#### Character Data Operations
```python
get_character_data(character_name)        # Read character from Obsidian
get_all_characters()                       # Get all PCs
update_character_hp(name, current, max, temp)  # Real-time HP updates
update_character_resources(name, resources)    # Spell slots, rage, etc.
add_condition(name, condition)             # Add status condition
remove_condition(name, condition)          # Remove status condition
toggle_rage(name, activate)                # Activate/end Barbarian rage
use_spell_slot(name, spell_level, long_rest)  # Use/recover spell slots
```

#### Character Progression & Equipment
```python
update_character_xp(name, xp)              # Update XP (auto-calculates next level)
update_character_currency(name, gp, sp, cp, ep, pp)  # Update currency
update_character_ac(name, ac, ac_note)     # Update AC with optional note
add_inventory_item(name, item_name, qty, type, notes)  # Add item to inventory
remove_inventory_item(name, item_name)     # Remove item from inventory
```

#### Health Status Converter
```python
convert_hp_to_status(current_hp, max_hp)  # For enemy health display
# Returns: "Healthy" | "Hurt" | "Bloodied" | "Critical" | "Near Death" | "Unconscious" | "Dead"
```

#### File Watcher
```python
start_vault_watch()   # Monitor Obsidian for changes
stop_vault_watch()    # Stop monitoring
```

---

## Phase 2: Combat Engine Integration (Next)

**Remove Google Sheets dependencies:**
- Combat Engine reads PC stats from Obsidian
- Combat Engine writes HP/resource updates to Obsidian
- Enemy health displayed as descriptive status

**Integration:**
```python
# Combat Engine will call:
obsidian_sync.update_character_hp("Eglath Bearkiller", 58, 65)
obsidian_sync.convert_hp_to_status(25, 50)  # Returns "Bloodied"
```

---

## Phase 3: Real-Time Sync (Planned)

**Features:**
- Batch update system (debounce multiple rapid changes)
- Conflict resolution (last-write-wins with backup)
- Auto-sync every 30 seconds during active session
- Change propagation to other MCPs

---

## Phase 4: Session Integration (Planned)

**Features:**
- Session Recorder logs → Obsidian session notes
- Campaign Events → Timeline in Obsidian
- Quest progress tracking
- Encounter history

---

## Health Status Conversion

### Status Thresholds

| HP Percentage | Status | Description |
|--------------|--------|-------------|
| 90-100% | **Healthy** | Unharmed or minor scratches |
| 70-89% | **Hurt** | Visible injuries, still strong |
| 50-69% | **Bloodied** | Bleeding, favoring limbs |
| 25-49% | **Critical** | Severe wounds, struggling |
| 1-24% | **Near Death** | On the brink of collapse |
| 0% | **Unconscious** | Down but stable |
| < 0% | **Dead** | Killed |

**Example:**
```python
# Goblin has 15/30 HP → "Bloodied"
convert_hp_to_status(15, 30)
```

Players see: **"Goblin 1: Bloodied"** (no exact HP)

---

## Character Data Format

### Obsidian Markdown

```markdown
---
type: player_character
class: Barbarian
level: 5
hp_current: 58
hp_max: 65
hp_temp: 0
ac: 20
initiative_bonus: 3
proficiency_bonus: 3
conditions: []
resources:
  rage:
    current: 2
    max: 3
last_updated: 2026-01-13T15:30:00
---

# Eglath Bearkiller

**HP:** 58/65
**AC:** 20
...
```

---

## Usage Examples

### Get Character Data
```python
get_character_data("Eglath Bearkiller")
```

Returns full character sheet with stats, HP, resources, conditions.

### Update HP During Combat
```python
update_character_hp(
    character_name="Eglath Bearkiller",
    current_hp=58,
    max_hp=65,
    temp_hp=0
)
```

Obsidian file updates **instantly** (if open, auto-reloads).

### Add Condition
```python
add_condition("Torgga Brawnanvil", "Poisoned")
```

### Enemy Health Display
```python
convert_hp_to_status(current_hp=12, max_hp=50)
# Returns: "Critical"
```

DM sees: `Goblin: 12/50 HP`  
Players see: `Goblin: Critical`

### Update Character XP
```python
update_character_xp("Eglath Bearkiller", 8290)
```

Updates XP to 8,290 and auto-calculates "5,710 XP needed for Level 6"

### Update Currency
```python
update_character_currency(
    character_name="Brevin",
    gp=4807,
    sp=7,
    cp=5
)
```

### Update AC
```python
update_character_ac(
    character_name="Brevin",
    ac=16,
    ac_note="Studded Leather +1"
)
```

### Add Inventory Item
```python
add_inventory_item(
    character_name="Brevin",
    item_name="Psionic Disruptor Wand",
    quantity=1,
    item_type="Magic Item",
    notes="3 charges, 30 ft range, suppresses psionic abilities"
)
```

### Remove Inventory Item
```python
remove_inventory_item("Brevin", "Potion of Healing")
```

---

## Installation

```bash
cd mcp_servers/obsidian_sync
pip install -r requirements.txt
```

---

## Configuration

Update `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "obsidian-sync": {
      "command": "C:\\Users\\ksist\\AppData\\Local\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\\python.exe",
      "args": ["obsidian_sync_server.py"],
      "cwd": "C:\\DnD\\DnD_Cursor\\mcp_servers\\obsidian_sync"
    }
  }
}
```

---

## Next Steps

**Phase 2: Combat Engine Integration**
1. Update Combat Engine to read from Obsidian
2. Remove Google Sheets dependencies
3. Add enemy health status display
4. Test real-time combat sync

**Phase 3: Real-Time Sync**
1. Implement batch update queue
2. Add conflict resolution
3. Create auto-sync timer
4. Broadcast changes to other MCPs

**Phase 4: Session Integration**
1. Connect Session Recorder to Obsidian
2. Auto-create encounter logs
3. Generate session summaries
4. Update quest progress

---

**Obsidian is now your campaign's living, breathing database!** 📚✨




