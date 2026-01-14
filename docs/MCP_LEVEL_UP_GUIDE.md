# Level-Up Guide MCP Tool

**Added to:** `rules-database` MCP Server  
**Tool Name:** `level_up_guide`

---

## Purpose

Provides comprehensive level-up information for D&D 5e characters, including:
- HP gain calculations
- New class features
- Spell slot changes (for casters)
- Proficiency bonus updates
- Step-by-step checklist

---

## Usage

```python
level_up_guide(
    char_class="Fighter",
    current_level=4,
    constitution_modifier=2
)
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `char_class` | string | Character class (Barbarian, Fighter, Cleric, Rogue, Wizard) |
| `current_level` | integer | Current level (1-19) |
| `constitution_modifier` | integer | CON modifier for HP calculation |

---

## Example Output

```json
{
  "class": "Fighter",
  "current_level": 4,
  "new_level": 5,
  "proficiency_bonus": 3,
  "proficiency_bonus_old": 2,
  "xp_required": 6500,
  "hp_gain": {
    "hit_die": "1d10",
    "average": 7,
    "maximum": 12,
    "roll_result": "Roll 1d10 + 2 (CON modifier)"
  },
  "new_features": [
    "Extra Attack"
  ],
  "ability_score_improvement": false,
  "checklist": [
    "1. Roll 1d10 + 2 for HP (or take average: 7)",
    "2. Update max HP in Google Sheets",
    "3. Update level to 5",
    "4. Update proficiency bonus to +3",
    "8. ⚠️ MAJOR POWER SPIKE - Proficiency bonus increases to +3",
    "9. ⚔️ Extra Attack - You can attack multiple times!"
  ]
}
```

---

## Spell Slot Changes (Casters)

For **Cleric** and **Wizard**, the output includes spell slot progression:

```json
{
  "class": "Wizard",
  "new_level": 3,
  "spell_slots": {
    "old": [3, 0, 0, 0, 0, 0, 0, 0, 0],
    "new": [4, 2, 0, 0, 0, 0, 0, 0, 0],
    "changes": [
      "Level 1: 3 → 4 slots (+1)",
      "Level 2: NEW - 2 slots available"
    ]
  }
}
```

---

## Class Features by Level

### Barbarian
- **Level 1:** Rage (2/day), Unarmored Defense
- **Level 2:** Reckless Attack, Danger Sense
- **Level 3:** Primal Path, Primal Knowledge
- **Level 4:** Ability Score Improvement
- **Level 5:** Extra Attack, Fast Movement, Rage (3/day)

### Fighter
- **Level 1:** Fighting Style, Second Wind
- **Level 2:** Action Surge (1/rest)
- **Level 3:** Martial Archetype
- **Level 4:** Ability Score Improvement
- **Level 5:** Extra Attack

### Cleric
- **Level 1:** Spellcasting, Divine Domain
- **Level 2:** Channel Divinity (1/rest)
- **Level 3:** 2nd-level Spells
- **Level 4:** Ability Score Improvement
- **Level 5:** 3rd-level Spells, Destroy Undead (CR 1/2)

### Rogue
- **Level 1:** Expertise, Sneak Attack (1d6), Thieves' Cant
- **Level 2:** Cunning Action
- **Level 3:** Sneak Attack (2d6), Roguish Archetype
- **Level 4:** Ability Score Improvement
- **Level 5:** Sneak Attack (3d6), Uncanny Dodge

### Wizard
- **Level 1:** Spellcasting, Arcane Recovery
- **Level 2:** Arcane Tradition
- **Level 3:** 2nd-level Spells
- **Level 4:** Ability Score Improvement
- **Level 5:** 3rd-level Spells

---

## Ability Score Improvements

Levels with **ASI** (Ability Score Improvement):
- **Fighter:** 4, 6, 8, 12, 14, 16, 19
- **Barbarian:** 4, 8, 12, 16, 19
- **Cleric:** 4, 8, 12, 16, 19
- **Rogue:** 4, 8, 10, 12, 16, 19
- **Wizard:** 4, 8, 12, 16, 19

When leveling to an ASI level, the checklist will highlight:
> ⭐ ABILITY SCORE IMPROVEMENT: +2 to one ability or +1 to two abilities (or take a feat)

---

## Hit Dice by Class

| Class | Hit Die |
|-------|---------|
| Barbarian | d12 |
| Fighter | d10 |
| Cleric | d8 |
| Rogue | d8 |
| Wizard | d6 |

**HP Gain = Hit Die Roll + Constitution Modifier**  
**Average HP Gain = (Hit Die / 2 + 1) + Constitution Modifier**

---

## Example Use Cases

### Level 5 Fighter (Eglath)
```python
level_up_guide(
    char_class="Barbarian",
    current_level=5,
    constitution_modifier=3
)
```

Output will show:
- Roll 1d12 + 3 for HP (average: 10)
- New features: Level 6 features
- Proficiency bonus: +3
- Rage uses: 4/day (from feature progression)

### Level 5 Wizard (Zephyr)
```python
level_up_guide(
    char_class="Wizard",
    current_level=5,
    constitution_modifier=1
)
```

Output will show:
- Roll 1d6 + 1 for HP (average: 5)
- Spell slots: 3rd level spells now available
- Can learn new 3rd-level spells

---

## Integration with Google Sheets

After using this tool, update Google Sheets:

1. **CSV_Characters:**
   - Update `level` column
   - Update `hp_max` column (add HP roll result)
   - Update `proficiency_bonus` if changed

2. **CSV_SpellSlots** (for casters):
   - Add/update rows for new spell levels
   - Update `max` and `remaining` columns

3. **CSV_Resources:**
   - Update resource maximums (Rage, Channel Divinity, etc.)

---

## Checklist Example

For a **Barbarian leveling from 4 → 5**:

```
1. Roll 1d12 + 3 for HP (or take average: 10)
2. Update max HP in Google Sheets
3. Update level to 5
4. Update proficiency bonus to +3
8. ⚠️ MAJOR POWER SPIKE - Proficiency bonus increases to +3
9. ⚔️ Extra Attack - You can attack multiple times!
```

---

**This tool ensures you never miss important level-up changes and provides a clear checklist for updating character data!**




