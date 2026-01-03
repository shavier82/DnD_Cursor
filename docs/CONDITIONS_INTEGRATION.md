# Conditions System Integration

## Overview

The conditions system is now fully integrated with the parallel agent pipeline. REFEREE checks conditions before combat actions, and STATE_PATCHER emits sheet operations to update conditions in Google Sheets.

## REFEREE Integration

### Before Combat Actions

REFEREE **MUST** check active conditions before processing any combat action:

1. **Load character stats** from JSON file
2. **Check active conditions:**
   ```powershell
   python C:\DnD\DnD_Cursor\scripts\manage_conditions.py effects <character_name>
   ```
3. **Apply condition effects:**
   - AC modifiers (ac_mod) - add to base AC
   - Attack advantage/disadvantage - apply to attack rolls
   - Save advantage/disadvantage - apply to saving throws
   - Skill advantage/disadvantage - apply to ability checks
   - Speed modifiers - apply to movement
   - Damage resistance/immunity - apply to damage calculations

### Example REFEREE Workflow

**Before processing an attack:**
1. Load character JSON: `C:\DnD\Campaigns\Phandelver\characters\Ergath.json`
2. Get base AC: 15
3. Check conditions: `python manage_conditions.py effects "Ergath"`
4. Get combined effects: `{"ac_mod": 2, "attack_disadvantage": true}`
5. Calculate final AC: 15 + 2 = 17
6. Apply attack disadvantage to the roll

**Before processing a save:**
1. Load character JSON
2. Check conditions for save modifiers
3. Apply save advantage/disadvantage from conditions
4. Process the save with modified roll

## STATE_PATCHER Integration

### Emitting Sheet Operations

STATE_PATCHER should emit `sheet_ops` array in its output:

```json
{
  "agent_role": "STATE_PATCHER",
  "blocked": false,
  "reason": "",
  "patches": [
    { "op": "replace", "path": "/combat/round", "value": 2 }
  ],
  "sheet_ops": [
    {
      "op": "condition_add",
      "character_id": "eglath_bearkiller",
      "condition": "poisoned",
      "source": "goblin_arrow",
      "duration_type": "rounds",
      "duration_value": 3,
      "ticks_remaining": 3,
      "mechanical_effects": ""
    },
    {
      "op": "currency_add",
      "character_id": "brevin",
      "gp": 50
    },
    {
      "op": "resource_set",
      "character_id": "eglath_bearkiller",
      "resource": "rage",
      "remaining": 1,
      "max": 3,
      "active": true
    }
  ]
}
```

### Executing Sheet Operations

After STATE_PATCHER creates its output, execute sheet operations:

```powershell
python C:\DnD\DnD_Cursor\scripts\execute_sheet_ops.py --input "C:\DnD\.coord-<session-id>\dnd_out_STATE_PATCHER.json"
```

This will:
- Add/remove conditions
- Update currency
- Update resources
- Tick conditions (if condition_tick op is present)

## Workflow Examples

### Example 1: Character Gets Poisoned

**STATE_PATCHER emits:**
```json
{
  "sheet_ops": [
    {
      "op": "condition_add",
      "character_id": "eglath_bearkiller",
      "condition": "poisoned",
      "source": "goblin_arrow",
      "duration_type": "rounds",
      "duration_value": 3,
      "ticks_remaining": 3,
      "mechanical_effects": ""
    }
  ]
}
```

**Execute:**
```powershell
python C:\DnD\DnD_Cursor\scripts\execute_sheet_ops.py --input "dnd_out_STATE_PATCHER.json"
```

**Result:** Condition added to CSV_ConditionReference

**Next turn:** REFEREE checks conditions and applies attack disadvantage

### Example 2: End of Round

**STATE_PATCHER emits:**
```json
{
  "sheet_ops": [
    {
      "op": "condition_tick",
      "mode": "round",
      "amount": 1
    }
  ]
}
```

**Execute:**
```powershell
python C:\DnD\DnD_Cursor\scripts\execute_sheet_ops.py --input "dnd_out_STATE_PATCHER.json"
```

**Result:** All round-based conditions decrement, expired conditions removed

### Example 3: Character Casts Bless

**STATE_PATCHER emits:**
```json
{
  "sheet_ops": [
    {
      "op": "condition_add",
      "character_id": "brevin",
      "condition": "blessed",
      "source": "spell_bless",
      "duration_type": "concentration",
      "duration_value": 0,
      "ticks_remaining": "",
      "mechanical_effects": ""
    }
  ]
}
```

**Execute:** Condition added

**Next attack:** REFEREE checks conditions, applies attack advantage

## Integration with Merge Script

The merge script (`merge_outputs.ps1`) can optionally execute sheet operations after merging:

```powershell
# After merge, execute sheet operations
if (Test-Path (Join-Path $CoordDir "dnd_out_STATE_PATCHER.json")) {
    $statePatcher = Get-Content (Join-Path $CoordDir "dnd_out_STATE_PATCHER.json") -Raw | ConvertFrom-Json
    if ($statePatcher.sheet_ops -and $statePatcher.sheet_ops.Count -gt 0) {
        python C:\DnD\DnD_Cursor\scripts\execute_sheet_ops.py --input (Join-Path $CoordDir "dnd_out_STATE_PATCHER.json")
    }
}
```

## Best Practices

1. **Always check conditions before combat rolls** - REFEREE must run `effects` command
2. **Emit sheet_ops for all condition changes** - STATE_PATCHER should track all condition additions/removals
3. **Tick conditions at end of round** - Include `condition_tick` op in STATE_PATCHER output
4. **Combine effects properly** - Multiple conditions stack (e.g., AC mods add together)
5. **Handle conflicts** - Advantage + Disadvantage = normal roll (D&D 5e rule)

## Testing

### Test Condition Application

1. Add condition:
   ```powershell
   python C:\DnD\DnD_Cursor\scripts\manage_conditions.py add "Ergath" "poisoned" "test" --duration-type rounds --duration-value 3
   ```

2. Check effects:
   ```powershell
   python C:\DnD\DnD_Cursor\scripts\manage_conditions.py effects "Ergath"
   ```

3. Verify REFEREE would see attack disadvantage

### Test Sheet Operations

1. Create test STATE_PATCHER output with sheet_ops
2. Execute:
   ```powershell
   python C:\DnD\DnD_Cursor\scripts\execute_sheet_ops.py --input "test_STATE_PATCHER.json"
   ```
3. Verify conditions updated in Google Sheets



