# D&D Character Sheet Template (Obsidian)

This is the **standard structure** for all D&D character sheets in Obsidian. All character files MUST follow this format for MCP tools to work correctly.

---

## Template Structure

```markdown
---
class: [Class Name]
level: [Number]
player: [Player Name]
race: [Race]
hp_current: [Number]
hp_max: [Number]
ac: [Number]
spell_slots:
  level_1: [Number]
  level_2: [Number]
  level_3: [Number]
  level_4: [Number]
  level_5: [Number]
  level_6: [Number]
  level_7: [Number]
  level_8: [Number]
  level_9: [Number]
spell_save_dc: [Number]
spell_attack_bonus: [Number]
tags:
- pc
- character
type: player_character
xp: [Number]
---

# [Character Name]

## Quick Stats

**Class:** [Class] [Level]
**Race:** [Race]

## Party Relationships

**Party Members:**
- [[Character1]] - Description
- [[Character2]] - Description
- [[Character3]] - Description
- [[Character4]] - Description

## Combat Stats

**HP:** [Current]/[Max]
**AC:** [Number]
**Initiative:** [Modifier]
**Speed:** [Number] ft
**Proficiency Bonus:** +[Number]

## Ability Scores

| Stat | Score | Modifier |
|------|-------|----------|
| STR  | XX | +X |
| DEX  | XX | +X |
| CON  | XX | +X |
| INT  | XX | +X |
| WIS  | XX | +X |
| CHA  | XX | +X |

## Progression

**XP:** X,XXX / XX,XXX
**Next Level:** X,XXX XP needed

## Equipment & Inventory

### Weapons

| Weapon | Equipped | Attack | Damage | Properties | Special Effects |
|--------|----------|--------|--------|------------|-----------------|
| [Weapon Name] | Yes/No | +X | XdX+X [type] | [Properties] | [Effects] |

**Important:**
- `Equipped`: Must be `Yes` or `No` (ASCII only)
- `Attack`: Include + sign (e.g., `+6`)
- `Damage`: Full dice notation + type (e.g., `1d8+3 slashing`)
- `Properties`: `-` for none, or list (e.g., `Versatile, Two-Handed`)
- `Special Effects`: `-` for none, or description

### Armor & Shields

| Armor/Shield | Equipped | AC Bonus | Type | Properties | Special Effects |
|--------------|----------|----------|------|------------|-----------------|
| [Armor Name] | Yes/No | +X or XX | [Type] | [Properties] | [Effects] |

**Important:**
- `Equipped`: Must be `Yes` or `No` (ASCII only)
- `AC Bonus`: `+X` for shields/modifiers, or base AC for armor (e.g., `16` for Chain Mail, `+2` for shield)
- `Type`: `Heavy`, `Medium`, `Light`, or `Shield`
- `Properties`: `-` for none, or list
- `Special Effects`: `-` for none, or description

**Current AC: XX** (Calculation shown)

### Magic Items

| Item | Equipped/Attuned | Properties | Charges/Uses | Notes |
|------|------------------|------------|--------------|-------|
| [Item Name] | Yes/No | [Properties] | X/X | [Notes] |

**Important:**
- `Equipped/Attuned`: `Yes` if attuned/equipped, `No` otherwise
- `Properties`: Brief description
- `Charges/Uses`: `X/X` format, or `-` for none
- `Notes`: Additional info

### General Inventory

| Item | Quantity | Weight (lb) | Notes |
|------|----------|-------------|-------|
| [Item Name] | X | X.X | [Notes] |

**Important:**
- `Quantity`: Integer (e.g., `10`)
- `Weight (lb)`: Decimal (e.g., `2.5`)
- `Notes`: Optional description, can be empty

**Total Weight:** ~XX lb / XXX lb capacity (STR XX × 15)

### Currency

| Type | Amount |
|------|--------|
| Gold (gp) | X,XXX |
| Silver (sp) | X,XXX |
| Copper (cp) | X,XXX |
| Platinum (pp) | X,XXX |

**Total Value:** X,XXX gp, XXX sp, XXX cp

```

---

## ✅ Critical Formatting Rules

### 1. **ASCII Characters Only**
- ❌ **Never use:** `✓`, `—`, `–`, `•`, or other Unicode
- ✅ **Always use:** `Yes`/`No`, `-`, `+`, standard ASCII

### 2. **Single Pipes for Tables**
- ❌ **Wrong:** `||` (double pipe)
- ✅ **Correct:** `|` (single pipe)

### 3. **Table Structure**
Every table MUST have:
1. Header row with `|` delimiters
2. Separator row with `|---|---|` format
3. Data rows with `|` delimiters
4. Blank line after table

### 4. **Section Headers**
- Level 1: `# [Character Name]`
- Level 2: `## [Section Name]`
- Level 3: `### [Subsection Name]`

### 5. **Equipped/Attuned Status**
- Must be `Yes` or `No` (exact spelling, title case)
- Used in Weapons, Armor, and Magic Items tables

### 6. **Numeric Formats**
- **Attack Bonus:** `+6` (with + sign)
- **Damage:** `1d8+3 slashing` (dice + modifier + type)
- **AC:** `16` or `+2` (base or modifier)
- **Weight:** `2.5` (decimal allowed)
- **Quantity:** `10` (integer)
- **XP:** `8,290` (comma separator for thousands)
- **Currency:** `4,807` (comma separator)

---

## 🔧 MCP Tool Compatibility

This structure is designed to work with these Obsidian MCP tools:

### Inventory Management
- `add_inventory_item(character_name, item_name, quantity, weight)`
- `remove_inventory_item(character_name, item_name, quantity)`

### Weapon Management
- `add_weapon(character_name, weapon_name, attack_bonus, damage, properties, special_effects, equipped)`
- `remove_weapon(character_name, weapon_name)`
- `equip_weapon(character_name, weapon_name, equipped)`

### Armor Management
- `add_armor(character_name, armor_name, ac_bonus, armor_type, properties, special_effects, equipped)`
- `remove_armor(character_name, armor_name)`
- `equip_armor(character_name, armor_name, equipped)`

### Magic Item Management
- `add_magic_item(character_name, item_name, properties, charges, notes, attuned)`
- `remove_magic_item(character_name, item_name)`
- `attune_item(character_name, item_name, attuned)`

### Character Stats
- `update_character_hp(character_name, new_hp, max_hp)`
- `update_character_xp(character_name, xp_to_add)`
- `update_character_currency(character_name, cp, sp, gp, pp)`
- `get_character_combat_stats(character_name)`

---

## 📝 Example: Complete Character Sheet

See `Torgga_Brawnanvil.md` for a complete working example that follows this template.

---

## 🚨 Common Mistakes to Avoid

1. **Using Unicode characters** → They cause encoding issues
2. **Double pipes (`||`)** → Breaks table parsing
3. **Inconsistent `Equipped` values** → Must be exactly `Yes` or `No`
4. **Missing table sections** → All sections must exist (even if empty)
5. **Incorrect numeric formats** → Must match specified formats above

---

## 🔄 Validation

To validate a character sheet:
1. Check all tables have single pipes `|`
2. Check all `Equipped`/`Attuned` fields are `Yes` or `No`
3. Check no Unicode characters exist
4. Check all required sections exist
5. Check numeric formats are correct

**Use `scripts/fix_all_characters.py` to automatically fix common issues.**

---

*Template Version: 1.0*  
*Last Updated: 2026-01-14*
