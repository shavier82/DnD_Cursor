# Save State System

## Overview

The save state system automatically tracks campaign progress and saves after encounters and scene transitions. Each campaign has its own unique save file.

## Save File Location

**Campaign-specific save file:**
- `C:\DnD\Campaigns\<campaign>\saves\CURRENT_STATE.json`

**Example:**
- `C:\DnD\Campaigns\Phandelver\saves\CURRENT_STATE.json`

## Save File Structure

```json
{
  "timestamp": "2026-01-02T19:53:42.1234567-05:00",
  "last_saved": "2026-01-02T19:53:42.1234567-05:00",
  "campaign": "Phandelver",
  "scene": {
    "area": "ambush_site",
    "location": "triboar_trail",
    "chapter": 1
  },
  "party": {
    "members": ["Brevin", "Ergath", "Torgga", "Vandross"]
  },
  "combat": {
    "initiated": false,
    "round": 0
  },
  "encounters": [
    {
      "name": "goblin_ambush",
      "completed": true,
      "timestamp": "2026-01-02T18:00:00.0000000-05:00"
    }
  ]
}
```

## Automatic Saving

### When State is Saved

State is automatically saved when STATE_PATCHER emits patches with these paths:
- `/encounter/<name>` - Marks encounter as completed
- `/scene/area` - Updates current area
- `/scene/location` - Updates current location
- `/scene/chapter` - Updates current chapter
- `/combat/ended` - Marks combat as ended

### How It Works

1. **STATE_PATCHER** emits patches with scene/encounter paths
2. **merge_outputs.ps1** detects these patches after merge
3. **State is loaded** from `CURRENT_STATE.json` (or created if missing)
4. **Patches are applied** to the state
5. **State is saved** back to `CURRENT_STATE.json`

## Manual State Management

### Load Current State

```powershell
python C:\DnD\DnD_Cursor\scripts\save_game_state.py load
```

Or:

```powershell
powershell -ExecutionPolicy Bypass -File C:\DnD\DnD_Cursor\scripts\load_game_state.ps1
```

### Save State Manually

```powershell
python C:\DnD\DnD_Cursor\scripts\save_game_state.py save --input "path/to/state.json"
```

## STATE_PATCHER Instructions

### Mark Encounter Complete

```json
{
  "op": "add",
  "path": "/encounter/goblin_ambush",
  "value": true
}
```

### Update Scene

```json
{
  "op": "replace",
  "path": "/scene/area",
  "value": "cragmaw_hideout"
}
```

```json
{
  "op": "replace",
  "path": "/scene/location",
  "value": "goblin_trail"
}
```

### Mark Combat Ended

```json
{
  "op": "replace",
  "path": "/combat/ended",
  "value": true
}
```

## Loading State in Agents

### REFEREE / NARRATOR / STATE_PATCHER

All agents can read the current state from:
- `C:\DnD\Campaigns\Phandelver\saves\CURRENT_STATE.json`

Agents should:
1. Load state at the start of their processing
2. Use state to determine current scene/encounter
3. Emit patches to update state when appropriate

## Best Practices

1. **Save after encounters** - Always emit `/encounter/<name>` patch when encounter completes
2. **Save on scene transitions** - Update `/scene/area` and `/scene/location` when moving
3. **Save after combat** - Mark `/combat/ended` when combat finishes
4. **Load state at session start** - Check `CURRENT_STATE.json` to resume from last save
5. **Unique per campaign** - Each campaign has its own save file

## Example Workflow

### After Goblin Ambush Encounter

**STATE_PATCHER emits:**
```json
{
  "patches": [
    {
      "op": "add",
      "path": "/encounter/goblin_ambush",
      "value": true
    },
    {
      "op": "replace",
      "path": "/scene/area",
      "value": "goblin_trail"
    }
  ]
}
```

**After merge:**
- State is automatically saved
- `encounters` array includes `goblin_ambush` as completed
- `scene.area` is updated to `goblin_trail`

### Resuming Session

1. Load state: `python save_game_state.py load`
2. Check `encounters` array to see what's been completed
3. Check `scene` to see current location
4. Continue from there



