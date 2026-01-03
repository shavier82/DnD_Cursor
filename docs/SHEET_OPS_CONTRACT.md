# Sheet Ops Contract

## Overview

This document defines the standardized operations for updating Google Sheets during gameplay. These operations are emitted by STATE_PATCHER (or a dedicated SHEETS_SYNC step) and executed to keep sheets in sync with game state.

## Operation Types

### Condition Operations

#### `condition_add`
Adds a condition to a character.

```json
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
```

**Fields:**
- `character_id` - Character identifier
- `condition` - Condition name (must exist in CSV_Conditions)
- `source` - Source of condition (e.g., "goblin_arrow", "spell_bless")
- `duration_type` - One of: `rounds`, `turns`, `minutes`, `hours`, `until_removed`, `save_ends`, `concentration`
- `duration_value` - Numeric value (not used for `until_removed`, `save_ends`, `concentration`)
- `ticks_remaining` - Initial tick count (blank for `until_removed`, `save_ends`, `concentration`)
- `mechanical_effects` - JSON string (blank = inherit from CSV_Conditions)

**Command:**
```powershell
python C:\DnD\DnD_Cursor\scripts\manage_conditions.py add "Ergath" "poisoned" "goblin_arrow" --duration-type rounds --duration-value 3
```

#### `condition_remove`
Removes a condition from a character.

```json
{
  "op": "condition_remove",
  "character_id": "eglath_bearkiller",
  "condition": "poisoned",
  "source": "goblin_arrow"
}
```

**Fields:**
- `character_id` - Character identifier
- `condition` - Condition name
- `source` - Source (optional, removes all if omitted)

**Command:**
```powershell
python C:\DnD\DnD_Cursor\scripts\manage_conditions.py remove "Ergath" "poisoned" --source "goblin_arrow"
```

#### `condition_tick`
Ticks all conditions (decrements duration).

```json
{
  "op": "condition_tick",
  "mode": "round",
  "amount": 1
}
```

**Fields:**
- `mode` - `round` or `turn`
- `amount` - Number to decrement (default: 1)

**Command:**
```powershell
python C:\DnD\DnD_Cursor\scripts\manage_conditions.py tick --mode round --amount 1
```

### Currency Operations

#### `currency_add`
Adds currency to a character.

```json
{
  "op": "currency_add",
  "character_id": "brevin",
  "gp": 50,
  "sp": 0,
  "cp": 0,
  "ep": 0,
  "pp": 0
}
```

**Fields:**
- `character_id` - Character identifier
- `gp`, `sp`, `cp`, `ep`, `pp` - Currency amounts (all optional, default 0)

**Command:**
```powershell
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py currency "Brevin" --gp 50
```

### Inventory Operations

#### `inventory_add`
Adds an item to character inventory.

```json
{
  "op": "inventory_add",
  "character_id": "brevin",
  "item": "Potion of Healing",
  "qty": 1,
  "equipped": "No",
  "notes": "Loot: Klarg chest"
}
```

**Fields:**
- `character_id` - Character identifier
- `item` - Item name
- `qty` - Quantity (default: 1)
- `equipped` - "Yes" or "No" (default: "No")
- `notes` - Optional notes

**Note:** Inventory operations are currently managed directly in CSV_Inventory sheet. A script can be added if needed.

### Resource Operations

#### `resource_set`
Sets a resource value.

```json
{
  "op": "resource_set",
  "character_id": "eglath_bearkiller",
  "resource": "rage",
  "remaining": 1,
  "max": 3,
  "active": true
}
```

**Fields:**
- `character_id` - Character identifier
- `resource` - Resource name (e.g., "rage", "superiority_dice", "1st")
- `remaining` - Remaining uses
- `max` - Maximum uses (optional)
- `active` - Boolean, whether resource is active (optional)

**Command:**
```powershell
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py resource "Ergath" rage --remaining 1 --max 3 --active
```

## Operation Execution

### STATE_PATCHER Output Format

STATE_PATCHER should emit sheet operations in its patches:

```json
{
  "agent_role": "STATE_PATCHER",
  "blocked": false,
  "reason": "",
  "patches": [
    {
      "op": "replace",
      "path": "/combat/round",
      "value": 2
    }
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
    }
  ]
}
```

### Execution Script

A script can process `sheet_ops` from STATE_PATCHER output:

```powershell
# Process sheet operations from STATE_PATCHER output
python C:\DnD\DnD_Cursor\scripts\execute_sheet_ops.py --input "C:\DnD\.coord-<session-id>\dnd_out_STATE_PATCHER.json"
```

## Integration Points

### After Combat Turn
1. STATE_PATCHER emits `sheet_ops` for:
   - Conditions applied
   - Resources used
   - Currency gained
   - XP awarded

2. Execute sheet operations:
   ```powershell
   python C:\DnD\DnD_Cursor\scripts\execute_sheet_ops.py --input "dnd_out_STATE_PATCHER.json"
   ```

### End of Round
1. Tick all conditions:
   ```powershell
   python C:\DnD\DnD_Cursor\scripts\manage_conditions.py tick --mode round
   ```

### After Rest
1. Restore resources:
   ```powershell
   python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py resource "Ergath" rage --max 3 --remaining 3
   ```

## Best Practices

1. **Batch operations** - Group multiple sheet ops together
2. **Validate before execute** - Check character_id exists, condition exists, etc.
3. **Idempotent operations** - Operations should be safe to retry
4. **Error handling** - Log failures but don't block game flow
5. **Sync after operations** - Pull updated data back to local JSON if needed

## Future Enhancements

- **Batch execution script** - Process multiple sheet_ops at once
- **Validation layer** - Pre-validate operations before execution
- **Rollback support** - Undo operations if needed
- **Audit log** - Track all sheet operations for debugging



