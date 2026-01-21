# Battlemap System - Complete Reference

## Overview

The battlemap system provides a visual, drag-and-drop combat map that auto-refreshes when the JSON file changes. It's **semi-automatic** - the viewer auto-updates, but combat actions require manual JSON updates.

## How It Works

### 1. JSON File Structure

Each combat encounter has a JSON file: `scripts/combat_positions_<location>.json`

**Example:** `scripts/combat_positions_t18.json`

```json
{
  "grid_size": 5,
  "map_width_squares": 20,
  "map_height_squares": 20,
  "defeated": [],
  "combatants": {
    "brevin": {
      "x": 4,
      "y": 8,
      "color": "blue",
      "label": "B"
    },
    "ontharyx": {
      "x": 5,
      "y": 7,
      "color": "red",
      "label": "O"
    }
  },
  "terrain": {
    "basin_north_1": {
      "x": 3,
      "y": 2,
      "width": 2,
      "height": 1,
      "color": "gray",
      "type": "basin"
    }
  },
  "combat_status": {
    "combatants": {
      "brevin": {
        "name": "Brevin",
        "hp": "45/45",
        "initiative": 25,
        "is_alive": true
      }
    },
    "initiative_order": ["brevin", "ontharyx", ...],
    "current_turn": {
      "creature_id": "brevin",
      "name": "Brevin"
    },
    "round": 2
  }
}
```

### 2. Launching the Battlemap

**Command:**
```powershell
cd scripts
python view_battlemap.py combat_positions_t18.json
```

**Or from project root:**
```powershell
python scripts/view_battlemap.py scripts/combat_positions_t18.json
```

**Features:**
- Auto-refreshes when JSON file changes (checks modification time)
- Drag-and-drop for blue (player) icons
- Shows HP, initiative order, current turn
- Zoom controls
- Update interval configurable (default: 1 second)

### 3. During Combat - Manual Updates Required

**When combat actions happen, update the JSON file:**

#### A. HP Changes
After damage/healing, update `combat_status.combatants.<id>.hp`:

```json
"harralie": {
  "name": "Harralie",
  "hp": "42/65",  // Updated from 65/65 after taking 23 damage
  "initiative": 17,
  "is_alive": true
}
```

#### B. Position Changes
After movement, update `combatants.<id>.x` and `.y`:

```json
"brevin": {
  "x": 6,  // Moved from (4, 8) to (6, 8)
  "y": 8,
  "color": "blue",
  "label": "B"
}
```

#### C. Turn Advancement
Update `combat_status.current_turn` and `round`:

```json
"current_turn": {
  "creature_id": "ontharyx",
  "name": "Ontharyx"
},
"round": 2
```

#### D. Defeated Creatures
Add to `defeated` array (they won't render):

```json
"defeated": ["chals", "paulam"]
```

### 4. Workflow During Combat

**Step-by-step:**

1. **Launch battlemap** (once per combat):
   ```powershell
   python scripts/view_battlemap.py scripts/combat_positions_t18.json
   ```

2. **When player takes action:**
   - Process attack/damage with MCP tools
   - Update HP in JSON: `combat_status.combatants.<id>.hp`
   - Update position if moved: `combatants.<id>.x` and `.y`
   - Battlemap auto-refreshes (within 1 second)

3. **When enemy takes action:**
   - Process attack/damage
   - Update HP in JSON
   - Update position if moved
   - Battlemap auto-refreshes

4. **End of turn:**
   - Update `current_turn` to next combatant
   - Battlemap shows new turn indicator

### 5. Creating New Battlemap Files

**Template structure:**

```json
{
  "grid_size": 5,
  "map_width_squares": 20,
  "map_height_squares": 20,
  "defeated": [],
  "combatants": {
    // Add all combatants with x, y, color, label
  },
  "terrain": {
    // Add terrain features (basins, walls, etc.)
  },
  "combat_status": {
    "combatants": {
      // HP, initiative, alive status
    },
    "initiative_order": [],
    "current_turn": {},
    "round": 1
  }
}
```

**Color conventions:**
- `"blue"` = Player characters (can drag)
- `"red"` = Enemies
- `"green"` = Allies/NPCs
- `"orange"` = Neutral/unknown

### 6. Integration with Combat Engine

**Current state:** Separate systems
- Combat engine MCP tracks internal state
- Battlemap JSON is visual representation
- Manual sync required

**Why this works:**
- Battlemap is visual aid, not source of truth
- Combat engine handles rules/mechanics
- JSON updates are simple and reliable
- Auto-refresh makes it feel automatic

### 7. Common Operations

#### Update HP after damage:
```python
# In combat_positions_t18.json
"harralie": {
  "hp": "42/65"  # Old: "65/65", took 23 damage
}
```

#### Move creature:
```python
"brevin": {
  "x": 6,  # Was 4
  "y": 8   # Same
}
```

#### Mark defeated:
```json
"defeated": ["chals", "paulam"]
```

#### Advance turn:
```json
"current_turn": {
  "creature_id": "ontharyx",
  "name": "Ontharyx"
}
```

### 8. Troubleshooting

**Battlemap not updating:**
- Check JSON file path is correct
- Verify JSON syntax is valid (no trailing commas)
- Check file permissions (must be writable)
- Try "Refresh Now" button in viewer

**Icons not showing:**
- Check `combatants` section has correct IDs
- Verify `defeated` array doesn't include the creature
- Check x, y coordinates are within map bounds

**HP not displaying:**
- Verify `combat_status.combatants.<id>` exists
- Check HP format is "current/max" (e.g., "42/65")
- Ensure `is_alive` is set correctly

### 9. Best Practices

1. **Always update JSON after combat actions** - HP, positions, turn
2. **Keep JSON file in sync** - Don't let it drift from actual combat state
3. **Use drag-and-drop for player movement** - Faster than manual edits
4. **Update `defeated` array immediately** - Prevents confusion
5. **Save JSON after each update** - Auto-refresh needs file modification time

### 10. File Locations

- **Viewer script:** `scripts/view_battlemap.py`
- **Position files:** `scripts/combat_positions_<location>.json`
- **Example:** `scripts/combat_positions_t18.json`

---

## Quick Reference

**Launch:**
```powershell
python scripts/view_battlemap.py scripts/combat_positions_t18.json
```

**Update HP:**
Edit `combat_status.combatants.<id>.hp` in JSON

**Update Position:**
Edit `combatants.<id>.x` and `.y` in JSON, or drag blue icons

**Advance Turn:**
Edit `combat_status.current_turn` in JSON

**The battlemap auto-refreshes when you save the JSON file!**
