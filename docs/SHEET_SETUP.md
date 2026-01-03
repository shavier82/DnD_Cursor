# Google Sheets Setup Guide

## Required Sheet Structure

### CSV_Conditions (Static Dictionary)

**Purpose:** Define condition mechanics (never edited during play)

**Columns:**
1. `condition_name` - Name of condition (e.g., "poisoned", "blessed", "prone")
2. `mechanical_effects` - JSON string with mechanical effects

**Example rows:**
```
condition_name: poisoned
mechanical_effects: {"attack_disadvantage": true, "skill_disadvantage": ["Perception", "Investigation"]}

condition_name: blessed
mechanical_effects: {"attack_advantage": true, "save_advantage": ["Dexterity", "Strength", "Constitution"]}

condition_name: prone
mechanical_effects: {"attack_disadvantage": true, "skill_disadvantage": ["Stealth"]}
```

### CSV_ConditionReference (Runtime Ledger)

**Purpose:** Track active conditions on characters (edited during play)

**Columns:**
1. `character_id` - Links to CSV_Characters (e.g., "eglath_bearkiller")
2. `name` - Character name (for display)
3. `condition` - Condition name (must exist in CSV_Conditions)
4. `duration_type` - Enum: `rounds`, `turns`, `minutes`, `hours`, `until_removed`, `save_ends`, `concentration`
5. `duration_value` - Number (e.g., 3 for "3 rounds")
6. `duration` - Display string (e.g., "3 rounds", "until removed")
7. `ticks_remaining` - Runtime counter (decremented per tick, blank for until_removed/save_ends/concentration)
8. `source` - Source of condition (e.g., "goblin_arrow", "spell_bless")
9. `mechanical_effects` - JSON string (blank = inherit from CSV_Conditions)

**Example row:**
```
character_id: eglath_bearkiller
name: Eglath Bearkiller
condition: poisoned
duration_type: rounds
duration_value: 3
duration: 3 rounds
ticks_remaining: 3
source: goblin_arrow
mechanical_effects: 
```

## Setting Up the Sheets

### Step 1: Create CSV_ConditionReference Structure

If the sheet doesn't have the runtime columns yet, add them:

1. Open your Google Sheet
2. Go to `CSV_ConditionReference` tab
3. Add these column headers in row 1:
   - `character_id`
   - `name`
   - `condition`
   - `duration_type`
   - `duration_value`
   - `duration`
   - `ticks_remaining`
   - `source`
   - `mechanical_effects`

### Step 2: Populate CSV_Conditions

Add common conditions with their mechanical effects:

**Poisoned:**
```json
{"attack_disadvantage": true, "skill_disadvantage": ["Perception", "Investigation"]}
```

**Blessed:**
```json
{"attack_advantage": true, "save_advantage": ["Dexterity", "Strength", "Constitution"]}
```

**Prone:**
```json
{"attack_disadvantage": true, "skill_disadvantage": ["Stealth"]}
```

**Grappled:**
```json
{"speed_mod": 0, "condition_immunity": ["prone"]}
```

**Frightened:**
```json
{"attack_disadvantage": true, "skill_disadvantage": ["Perception"], "save_disadvantage": ["Wisdom"]}
```

**Haste:**
```json
{"ac_mod": 2, "speed_mod": 30, "attack_advantage": true}
```

**Slow:**
```json
{"speed_mod": -30, "attack_disadvantage": true, "save_disadvantage": ["Dexterity"]}
```

### Step 3: Verify Existing Sheets

Ensure these sheets exist and have correct structure:

- **CSV_Characters** - Character stats
- **CSV_Currency** - Character currency
- **CSV_Resources** - Character resources (rage, spell slots, etc.)
- **CSV_Inventory** - Character inventory
- **CSV_Conditions** - Condition definitions
- **CSV_ConditionReference** - Active conditions ledger

## Testing the Setup

### Test 1: Add a Condition

```powershell
python C:\DnD\DnD_Cursor\scripts\manage_conditions.py add "Ergath" "poisoned" "test_arrow" --duration-type rounds --duration-value 3
```

**Expected:** New row added to CSV_ConditionReference

### Test 2: List Conditions

```powershell
python C:\DnD\DnD_Cursor\scripts\manage_conditions.py list "Ergath"
```

**Expected:** Shows the condition you just added

### Test 3: Tick Conditions

```powershell
python C:\DnD\DnD_Cursor\scripts\manage_conditions.py tick --mode round
```

**Expected:** `ticks_remaining` decrements from 3 → 2

### Test 4: Get Effects

```powershell
python C:\DnD\DnD_Cursor\scripts\manage_conditions.py effects "Ergath"
```

**Expected:** Returns JSON with combined mechanical effects

### Test 5: Remove Condition

```powershell
python C:\DnD\DnD_Cursor\scripts\manage_conditions.py remove "Ergath" "poisoned" --source "test_arrow"
```

**Expected:** Condition removed from CSV_ConditionReference

## Troubleshooting

### "ticks_remaining column not found"
- Verify CSV_ConditionReference has all 9 columns
- Check column names match exactly (case-sensitive)

### "Character not found"
- Verify character exists in CSV_Characters
- Check character_id matches exactly

### "Condition not found in CSV_Conditions"
- Add condition definition to CSV_Conditions first
- Or provide `--mechanical-effects` when adding condition

### Condition not appearing in list
- Check character_id matches
- Verify row was actually added (check sheet directly)
- Check for typos in condition name



