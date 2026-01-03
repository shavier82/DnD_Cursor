# Conditions System

## Overview

The conditions system uses two Google Sheets:
- **CSV_Conditions** - Static dictionary of condition definitions
- **CSV_ConditionReference** - Dynamic runtime ledger of active conditions

## Sheet Structure

### CSV_Conditions (Static Dictionary)

**Never edited during play** - Used for:
- Validating condition names
- Default mechanics lookup

**Columns:**
- `condition_name` - Name of the condition (e.g., "poisoned", "blessed", "prone")
- `mechanical_effects` - JSON string with mechanical effects

**Example row:**
```
condition_name: poisoned
mechanical_effects: {"attack_disadvantage": true, "skill_disadvantage": ["Perception", "Investigation"]}
```

### CSV_ConditionReference (Runtime Ledger)

**Edited during play** - One row = one active condition instance

**Columns:**
- `character_id` - Links to character
- `name` - Character name
- `condition` - Condition name (must exist in CSV_Conditions)
- `duration_type` - Enum: `rounds`, `turns`, `minutes`, `hours`, `until_removed`, `save_ends`, `concentration`
- `duration_value` - Number (e.g., 3 for "3 rounds")
- `duration` - Display string (e.g., "3 rounds", "until removed")
- `ticks_remaining` - Runtime counter (decremented per tick)
- `source` - Source of condition (e.g., "goblin_arrow", "spell_bless")
- `mechanical_effects` - JSON string (blank = inherit from CSV_Conditions)

**Rule:** If `mechanical_effects` is blank → inherit from `CSV_Conditions.mechanical_effects`

## Duration Types

### `rounds`
- Decrements once per round
- Example: "3 rounds" = lasts 3 rounds of combat

### `turns`
- Decrements on the affected character's turn
- Example: "2 turns" = lasts 2 of the character's turns

### `minutes` / `hours`
- Don't tick in combat
- Can convert to end timestamps for out-of-combat tracking

### `until_removed`
- No ticking
- Removed manually or by specific effect

### `save_ends`
- No ticking
- Removed when character makes successful save

### `concentration`
- No ticking
- Removed when caster loses concentration

## Mechanical Effects Format

**JSON format (recommended):**

```json
{
  "ac_mod": 2,
  "attack_advantage": true,
  "attack_disadvantage": false,
  "skill_advantage": ["Perception"],
  "skill_disadvantage": ["Stealth"],
  "save_advantage": ["Dexterity"],
  "save_disadvantage": ["Constitution"],
  "speed_mod": -10,
  "damage_resistance": ["poison"],
  "damage_immunity": ["fire"],
  "condition_immunity": ["frightened"]
}
```

**Fields:**
- `ac_mod` - AC modifier (can be negative)
- `attack_advantage` - Boolean, grants advantage on attack rolls
- `attack_disadvantage` - Boolean, grants disadvantage on attack rolls
- `skill_advantage` - Array of skill names
- `skill_disadvantage` - Array of skill names
- `save_advantage` - Array of ability names
- `save_disadvantage` - Array of ability names
- `speed_mod` - Speed modifier in feet (can be negative)
- `damage_resistance` - Array of damage types
- `damage_immunity` - Array of damage types
- `condition_immunity` - Array of condition names

## Commands

### Add Condition

```powershell
python C:\DnD\DnD_Cursor\scripts\manage_conditions.py add "Ergath" "poisoned" "goblin_arrow" --duration-type rounds --duration-value 3
```

**With custom mechanical effects:**
```powershell
python C:\DnD\DnD_Cursor\scripts\manage_conditions.py add "Brevin" "blessed" "spell_bless" --duration-type concentration --mechanical-effects '{"attack_advantage": true, "save_advantage": ["Dexterity"]}'
```

### Remove Condition

```powershell
# Remove all instances of condition
python C:\DnD\DnD_Cursor\scripts\manage_conditions.py remove "Ergath" "poisoned"

# Remove specific instance by source
python C:\DnD\DnD_Cursor\scripts\manage_conditions.py remove "Ergath" "poisoned" --source "goblin_arrow"
```

### Tick Conditions

```powershell
# Tick all conditions (decrement by 1 round)
python C:\DnD\DnD_Cursor\scripts\manage_conditions.py tick --mode round

# Tick by multiple rounds
python C:\DnD\DnD_Cursor\scripts\manage_conditions.py tick --mode round --amount 2
```

**Ticking rules:**
- `rounds` - Decrements once per round
- `turns` - Decrements on character's turn
- `until_removed`, `save_ends`, `concentration` - Don't tick
- Conditions with `ticks_remaining <= 0` are automatically removed

### List Conditions

```powershell
# List conditions for a character
python C:\DnD\DnD_Cursor\scripts\manage_conditions.py list "Ergath"

# List all active conditions
python C:\DnD\DnD_Cursor\scripts\manage_conditions.py list
```

### Get Combined Effects

```powershell
python C:\DnD\DnD_Cursor\scripts\manage_conditions.py effects "Ergath"
```

Returns combined mechanical effects from all active conditions.

## Sheet Ops Contract

For integration with STATE_PATCHER or combat system:

### Condition Operations

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

```json
{
  "op": "condition_remove",
  "character_id": "eglath_bearkiller",
  "condition": "poisoned",
  "source": "goblin_arrow"
}
```

```json
{
  "op": "condition_tick",
  "mode": "round",
  "amount": 1
}
```

## Using Conditions for Buffs/Debuffs

All status effects use the conditions system:

- **Buffs:** Bless, Haste, Shield of Faith, etc.
- **Debuffs:** Poisoned, Prone, Grappled, etc.
- **Temporary Effects:** "+2 AC until end of next turn", "Disadvantage on Perception while in smoke"

**Example - Bless spell:**
```powershell
python C:\DnD\DnD_Cursor\scripts\manage_conditions.py add "Brevin" "blessed" "spell_bless" --duration-type concentration --mechanical-effects '{"attack_advantage": true, "save_advantage": ["Dexterity", "Strength", "Constitution"]}'
```

**Example - Prone:**
```powershell
python C:\DnD\DnD_Cursor\scripts\manage_conditions.py add "Ergath" "prone" "knocked_down" --duration-type until_removed --mechanical-effects '{"attack_disadvantage": true, "skill_disadvantage": ["Stealth"]}'
```

## Integration with Combat System

1. **Before combat actions:**
   - Check active conditions
   - Apply mechanical effects (AC mods, advantage/disadvantage)
   - REFEREE uses combined effects for rulings

2. **After each round:**
   - Run `condition_tick --mode round`
   - Expired conditions are automatically removed

3. **After character's turn:**
   - Run `condition_tick --mode turn` for that character
   - (Only if using turn-based duration)

4. **When condition is removed:**
   - Use `condition_remove` command
   - Or let it expire naturally via ticking

## Best Practices

1. **Define conditions in CSV_Conditions first** - Provides default mechanics
2. **Use source field** - Helps identify which effect applied the condition
3. **Override mechanics only when needed** - Usually inherit from definition
4. **Tick at end of round** - Consistent timing for all round-based conditions
5. **Check effects before actions** - REFEREE should check `effects` command before processing rolls

## Example Workflow

### Combat: Character gets poisoned

1. **Add condition:**
   ```powershell
   python C:\DnD\DnD_Cursor\scripts\manage_conditions.py add "Ergath" "poisoned" "goblin_arrow" --duration-type rounds --duration-value 3
   ```

2. **Check effects:**
   ```powershell
   python C:\DnD\DnD_Cursor\scripts\manage_conditions.py effects "Ergath"
   ```
   REFEREE sees: `{"attack_disadvantage": true, "skill_disadvantage": ["Perception", "Investigation"]}`

3. **Apply effects during combat:**
   - All attack rolls have disadvantage
   - Perception/Investigation checks have disadvantage

4. **End of round:**
   ```powershell
   python C:\DnD\DnD_Cursor\scripts\manage_conditions.py tick --mode round
   ```
   - `ticks_remaining` decrements from 3 → 2

5. **After 3 rounds:**
   - Condition expires automatically
   - Removed from CSV_ConditionReference



