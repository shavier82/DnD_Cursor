# Spell Slot Tracking System

**Automatic spell slot management for spellcasters in Obsidian**

---

## Overview

Torgga (Cleric) and Zephyr (Wizard) now have **spell slot tracking** with:
- ✅ Individual checkboxes for each spell slot
- ✅ Spell Save DC and Spell Attack Bonus displayed
- ✅ Automatic slot usage via MCP tool
- ✅ Long rest recovery (uncheck all slots)

---

## Character Sheets

### ⚒️ **Torgga Brawnanvil** (Cleric 5)
**Spell Save DC:** 14 | **Spell Attack Bonus:** +6

**Level 1 (4 slots)**
- [ ] Slot 1
- [ ] Slot 2
- [ ] Slot 3
- [ ] Slot 4

**Level 2 (3 slots)**
- [ ] Slot 1
- [ ] Slot 2
- [ ] Slot 3

**Level 3 (2 slots)**
- [ ] Slot 1
- [ ] Slot 2

---

### ✨ **Zephyr Sparkwhistle** (Wizard 5)
**Spell Save DC:** 14 | **Spell Attack Bonus:** +6

**Level 1 (4 slots)**
- [ ] Slot 1
- [ ] Slot 2
- [ ] Slot 3
- [ ] Slot 4

**Level 2 (3 slots)**
- [ ] Slot 1
- [ ] Slot 2
- [ ] Slot 3

**Level 3 (2 slots)**
- [ ] Slot 1
- [ ] Slot 2

---

## How It Works

### Manual Method (In Obsidian)

1. **Open character sheet** in Obsidian
2. **Check a box** when you cast a spell: `- [x] Slot 1`
3. **On long rest:** Uncheck all boxes manually

### Automatic Method (Using MCP Tool)

#### Use a Spell Slot

```python
# Torgga casts Cure Wounds (1st level spell)
use_spell_slot("Torgga Brawnanvil", spell_level=1)

# Returns:
{
  "success": true,
  "message": "Torgga Brawnanvil used a level 1 spell slot",
  "slots_remaining": 3,
  "total_slots": 4
}

# Automatically checks the first unchecked slot:
# - [x] Slot 1
# - [ ] Slot 2
# - [ ] Slot 3
# - [ ] Slot 4
```

#### Cast Multiple Spells

```python
# Zephyr casts Magic Missile (1st level)
use_spell_slot("Zephyr Sparkwhistle", spell_level=1)

# Zephyr casts Fireball (3rd level)
use_spell_slot("Zephyr Sparkwhistle", spell_level=3)

# Level 1: - [x] Slot 1, - [ ] Slot 2, - [ ] Slot 3, - [ ] Slot 4
# Level 3: - [x] Slot 1, - [ ] Slot 2
```

#### Long Rest Recovery

```python
# Party takes a long rest
use_spell_slot("Torgga Brawnanvil", long_rest=True)
use_spell_slot("Zephyr Sparkwhistle", long_rest=True)

# Returns:
{
  "success": true,
  "message": "Torgga Brawnanvil took a long rest - all spell slots recovered!"
}

# Automatically unchecks ALL spell slot boxes
```

#### Out of Slots

```python
# Try to use a slot when all are used
use_spell_slot("Zephyr Sparkwhistle", spell_level=3)

# If all level 3 slots are used:
{
  "error": "No level 3 spell slots remaining!"
}
```

---

## Spell Save DC & Attack Bonus

Both characters have their spell stats displayed at the top of the Spell Slots section:

**Spell Save DC:** 14  
**Spell Attack Bonus:** +6

### Calculations:
- **Spell Save DC** = 8 + Proficiency Bonus (+3) + Spellcasting Modifier (+3) = **14**
- **Spell Attack Bonus** = Proficiency Bonus (+3) + Spellcasting Modifier (+3) = **+6**

**Spellcasting Modifier:**
- **Torgga (Cleric):** WIS +3
- **Zephyr (Wizard):** INT +3

---

## Spell Slot Progression (Level 5)

| Level | Slots | Both Characters |
|-------|-------|-----------------|
| 1st | 4 | ✓ |
| 2nd | 3 | ✓ |
| 3rd | 2 | ✓ |
| 4th+ | 0 | (Level 7+) |

---

## Usage Examples

### Example 1: Combat Round

```python
# Round 1: Torgga casts Spiritual Weapon (2nd level)
use_spell_slot("Torgga Brawnanvil", spell_level=2)
# Level 2: [x][ ][ ] - 2 slots remaining

# Round 2: Zephyr casts Fireball (3rd level)
use_spell_slot("Zephyr Sparkwhistle", spell_level=3)
# Level 3: [x][ ] - 1 slot remaining

# Round 3: Torgga casts Cure Wounds (1st level)
use_spell_slot("Torgga Brawnanvil", spell_level=1)
# Level 1: [x][ ][ ][ ] - 3 slots remaining
```

### Example 2: After Adventure

```python
# Party camps for the night
use_spell_slot("Torgga Brawnanvil", long_rest=True)
use_spell_slot("Zephyr Sparkwhistle", long_rest=True)

# All slots recovered:
# Level 1: [ ][ ][ ][ ]
# Level 2: [ ][ ][ ]
# Level 3: [ ][ ]
```

---

## Integration with Combat Engine (Phase 2)

**When Combat Engine is integrated:**
1. Combat Engine reads `spell_slots` from metadata
2. Automatically calls `use_spell_slot()` when a spell is cast
3. Displays remaining slots in combat UI
4. Warns if trying to cast without available slots

---

## Character Sheet Metadata

### Frontmatter Structure

```yaml
---
class: Cleric
spell_slots:
  level_1: 4
  level_2: 3
  level_3: 2
spell_save_dc: 14
spell_attack_bonus: 6
---
```

### Markdown Content

```markdown
## Spell Slots

**Spell Save DC:** 14 | **Spell Attack Bonus:** +6

### Level 1 (4 slots)
- [ ] Slot 1
- [ ] Slot 2
- [ ] Slot 3
- [ ] Slot 4

*Check boxes as you use spell slots. Uncheck all on long rest.*
```

---

## Common Spells

### Torgga (Cleric)
- **Cantrips (unlimited):** Sacred Flame, Light, Thaumaturgy
- **1st Level:** Cure Wounds, Healing Word, Bless, Shield of Faith
- **2nd Level:** Spiritual Weapon, Aid, Lesser Restoration
- **3rd Level:** Spirit Guardians, Revivify, Mass Healing Word

### Zephyr (Wizard)
- **Cantrips (unlimited):** Fire Bolt, Mage Hand, Prestidigitation
- **1st Level:** Magic Missile, Shield, Detect Magic, Identify
- **2nd Level:** Misty Step, Mirror Image, Scorching Ray
- **3rd Level:** Fireball, Counterspell, Fly

---

## Notes

- **Cantrips** (0-level spells) are unlimited - no tracking needed
- **Spell slots recover on long rest** (8+ hours of rest)
- **Short rest** does NOT recover spell slots (except for Wizards with Arcane Recovery)
- **Arcane Recovery** (Wizard): Once per day after short rest, recover spell slots totaling half wizard level (rounded up)

---

**Spell slot tracking is now fully automated in Obsidian!** 📚✨




