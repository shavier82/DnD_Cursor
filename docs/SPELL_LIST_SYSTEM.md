# Spell List System

**Complete spell lists for spellcasters with preparation tracking**

---

## Overview

Torgga and Zephyr now have **dedicated spell list files** with:
- ✅ All available spells for their class and level (0-3rd level)
- ✅ Checkboxes to mark prepared/known spells
- ✅ Spell schools and properties (Concentration, Ritual)
- ✅ Linked from main character sheets
- ✅ Spell slot counts match their level (4/3/2 for level 5)

---

## Spell List Files

### ⚒️ **Torgga Brawnanvil** (Cleric 5)
**File:** `Torgga_Brawnanvil_Spells.md`  
**Total Spells:** 62 Cleric spells (levels 0-3)

**Breakdown:**
- **Cantrips (Level 0):** 9 spells
- **Level 1:** 15 spells
- **Level 2:** 17 spells
- **Level 3:** 21 spells

**Prepared Spells:** 8 (WIS +3 + Level 5)

---

### ✨ **Zephyr Sparkwhistle** (Wizard 5)
**File:** `Zephyr_Sparkwhistle_Spells.md`  
**Total Spells:** 122 Wizard spells (levels 0-3)

**Breakdown:**
- **Cantrips (Level 0):** 20 spells
- **Level 1:** 31 spells
- **Level 2:** 39 spells
- **Level 3:** 32 spells

**Prepared Spells:** 8 (INT +3 + Level 5)

---

## How to Use

### 1. **Access Spell Lists**

From the main character sheet, click the link:
```markdown
📖 **[[Torgga_Brawnanvil_Spells|View Full Spell List]]** (62 Cleric spells available)
```

Or open directly:
- `Torgga_Brawnanvil_Spells.md`
- `Zephyr_Sparkwhistle_Spells.md`

### 2. **Mark Prepared Spells**

Check the box next to spells you have prepared:

```markdown
## Level 1 Spells

- [x] **Cure Wounds** - Abjuration
- [x] **Healing Word** - Abjuration
- [x] **Bless** - Enchantment (C)
- [ ] **Guiding Bolt** - Evocation
- [ ] **Shield of Faith** - Abjuration (C)
```

### 3. **Update After Long Rest**

Clerics and Wizards can change their prepared spells after a long rest:
1. Uncheck old prepared spells
2. Check new prepared spells (up to 8 total)
3. Cantrips are always prepared

---

## Spell Properties

### Legend

- **(C)** = **Concentration** - Requires concentration, can't cast another concentration spell
- **(R)** = **Ritual** - Can be cast as a ritual (adds 10 minutes, no spell slot required)

### Examples

```markdown
- [ ] **Bless** - Enchantment (C)
      ↑ Requires concentration

- [ ] **Detect Magic** - Divination (C) (R)
      ↑ Concentration AND can be cast as ritual

- [ ] **Cure Wounds** - Abjuration
      ↑ No special properties
```

---

## Spell Preparation Rules

### Cleric (Torgga)

**Cantrips:** All cantrips are always prepared (no limit)

**Prepared Spells:**
- Can prepare **WIS modifier + Cleric level** spells
- Torgga: **3 (WIS) + 5 (Level) = 8 spells**
- Can change prepared spells after a long rest
- Has access to **entire Cleric spell list** (62 spells for levels 0-3)

**Spell Slots (Level 5):**
- 1st Level: **4 slots**
- 2nd Level: **3 slots**
- 3rd Level: **2 slots**

---

### Wizard (Zephyr)

**Cantrips:** All cantrips are always prepared (no limit)

**Spellbook:**
- Knows spells in spellbook
- Starts with **6 spells** at level 1
- Gains **2 spells per level** when leveling up
- Can copy spells from scrolls/other spellbooks (50 gp + 2 hours per spell level)

**Prepared Spells:**
- Can prepare **INT modifier + Wizard level** spells
- Zephyr: **3 (INT) + 5 (Level) = 8 spells**
- Can change prepared spells after a long rest
- Can only prepare spells from spellbook

**Spell Slots (Level 5):**
- 1st Level: **4 slots**
- 2nd Level: **3 slots**
- 3rd Level: **2 slots**

---

## Example Spell Lists

### Torgga's Typical Prepared Spells (8 total)

**Cantrips (Always Prepared):**
- Sacred Flame
- Light
- Thaumaturgy

**Prepared Spells:**
1. **Cure Wounds** (1st) - Healing
2. **Healing Word** (1st) - Bonus action healing
3. **Bless** (1st) - Party buff
4. **Shield of Faith** (1st) - AC buff
5. **Spiritual Weapon** (2nd) - Bonus action attack
6. **Lesser Restoration** (2nd) - Remove conditions
7. **Aid** (2nd) - Increase max HP
8. **Spirit Guardians** (3rd) - Area damage

---

### Zephyr's Typical Prepared Spells (8 total)

**Cantrips (Always Prepared):**
- Fire Bolt
- Mage Hand
- Prestidigitation

**Prepared Spells:**
1. **Magic Missile** (1st) - Auto-hit damage
2. **Shield** (1st) - Reaction +5 AC
3. **Detect Magic** (1st) - Utility (ritual)
4. **Identify** (1st) - Identify magic items (ritual)
5. **Misty Step** (2nd) - Bonus action teleport
6. **Mirror Image** (2nd) - Defense
7. **Fireball** (3rd) - Area damage
8. **Counterspell** (3rd) - Counter enemy spells

---

## Spell Slot Tracking

Spell slots are tracked in the **main character sheet**, not the spell list file.

**Torgga_Brawnanvil.md:**
```markdown
### Level 1 Slots (4 total)
- [ ] Slot 1
- [ ] Slot 2
- [ ] Slot 3
- [ ] Slot 4
```

**When casting a spell:**
1. Check a slot box in the main character sheet
2. Use MCP tool: `use_spell_slot("Torgga Brawnanvil", spell_level=1)`

---

## Updating Spell Lists

### When Leveling Up

**Cleric:**
- Automatically gains access to higher-level spells
- Can prepare more spells (WIS + new level)
- Run script to regenerate spell list with new max level

**Wizard:**
- Gains 2 new spells in spellbook (any level you can cast)
- Can prepare more spells (INT + new level)
- Manually check 2 new spells in the spell list

### Regenerate Spell Lists

```bash
cd C:\DnD\DnD_Cursor
python scripts\generate_spell_lists.py
```

This will regenerate both spell list files with updated spell levels.

---

## File Structure

```
Player Characters/
├── Torgga_Brawnanvil.md          # Main character sheet
├── Torgga_Brawnanvil_Spells.md   # Spell list (62 spells)
├── Zephyr_Sparkwhistle.md        # Main character sheet
└── Zephyr_Sparkwhistle_Spells.md # Spell list (122 spells)
```

**Main Character Sheet:**
- HP, AC, stats, weapons
- Spell slot tracking (checkboxes)
- Link to spell list

**Spell List File:**
- All available spells for class/level
- Checkboxes to mark prepared spells
- Spell properties (Concentration, Ritual)

---

## Example Workflow

### Preparing Spells After Long Rest

1. **Open spell list file** (`Torgga_Brawnanvil_Spells.md`)
2. **Uncheck old prepared spells** (if changing)
3. **Check new prepared spells** (up to 8 total)
4. **Save file**

### Casting a Spell in Combat

1. **Check main character sheet** - Is spell prepared? (spell list file)
2. **Check spell slots** - Do you have a slot available? (main sheet)
3. **Cast spell** - Use MCP tool or manually check slot box
4. **Apply effects** - Use spell description from rules database

### After Combat

1. **Long rest?** - Uncheck all spell slot boxes
2. **Change prepared spells?** - Update spell list file
3. **Ready for next adventure!**

---

## Integration with MCP

### Get Spell Info

```python
# Look up spell details
lookup_spell("Cure Wounds")

# Returns full spell description, damage, range, etc.
```

### Search Spells

```python
# Find healing spells
search_spells("healing", spell_class="Cleric")

# Find 3rd level wizard spells
search_spells("", spell_class="Wizard", spell_level=3)
```

---

## Summary

✅ **62 Cleric spells** for Torgga (levels 0-3)  
✅ **122 Wizard spells** for Zephyr (levels 0-3)  
✅ **Checkboxes** to mark prepared spells  
✅ **Spell properties** (Concentration, Ritual)  
✅ **Linked** from main character sheets  
✅ **Spell slot tracking** in main sheets (4/3/2 for level 5)  
✅ **Preparation rules** documented  

**Your spellcasters now have complete, organized spell lists!** 📚✨




