# MCP Spell Database - Quick Reference

## Overview
The Spell Database MCP provides instant lookup of D&D 5e 2024 spells from the Player's Handbook.

**Database Size:**
- **391 unique spells**
- **34 cantrips** (Level 0)
- **357 level 1-9 spells**
- Organized by **8 spellcasting classes**
- Categorized by **8 schools of magic**

## Available Functions

### 1. `lookup_spell(spell_name)`
Look up a specific spell by name.

**Returns:**
- Spell name
- Level and school
- Classes that can cast it
- Components (Concentration, Ritual, Material)
- Source

**Example:**
```python
lookup_spell(spell_name="Fireball")
```

**Output:**
```
**Fireball**
Level 3 Evocation

**Classes:** Sorcerer, Wizard
**Special:** Material

**Source:** PHB 2024
```

---

### 2. `search_spells(query, spell_class, spell_level, school, max_results)`
Search for spells with optional filters.

**Parameters:**
- `query` (required): Search term (spell name, keyword, class, school)
- `spell_class` (optional): Filter by class (e.g., "Wizard", "Cleric")
- `spell_level` (optional): Filter by level (0-9, where 0 = cantrip)
- `school` (optional): Filter by school (e.g., "Evocation", "Abjuration")
- `max_results` (optional): Max results to return (default: 10)

**Example:**
```python
search_spells(query="fire", spell_class="Wizard", spell_level=3)
```

**Output:**
```
**Found 2 spell(s) matching 'fire':**

- **Fireball** (L3 Evocation) - Sorcerer, Wizard
- **Flame Arrows** (L3 Transmutation) - Druid, Ranger, Sorcerer, Wizard
```

---

### 3. `get_spells_by_class(spell_class, spell_level)`
Get all spells for a specific class, organized by level.

**Parameters:**
- `spell_class` (required): Class name (e.g., "Wizard", "Cleric", "Bard")
- `spell_level` (optional): Filter by spell level (0-9)

**Example:**
```python
get_spells_by_class(spell_class="Cleric", spell_level=1)
```

**Output:**
```
**Cleric Spells** (Level 1)

Total: 15 spells

**Level 1 Spells** (15 spells):
- Bane (Enchantment)
- Bless (Enchantment)
- Command (Enchantment)
- Create or Destroy Water (Transmutation)
- Cure Wounds (Abjuration)
- Detect Evil and Good (Divination) [C]
- Detect Magic (Divination) [C] [R]
...
```

**Legend:**
- `[C]` = Concentration
- `[R]` = Ritual

---

## Classes with Spell Lists
- **Bard** (140 spells)
- **Cleric** (117 spells)
- **Druid** (135 spells)
- **Paladin** (51 spells)
- **Ranger** (61 spells)
- **Sorcerer** (150 spells)
- **Warlock** (91 spells)
- **Wizard** (242 spells)

---

## Schools of Magic
- **Abjuration** (protection, warding)
- **Conjuration** (summoning, teleportation)
- **Divination** (knowledge, scrying)
- **Enchantment** (charm, mind control)
- **Evocation** (damage, energy)
- **Illusion** (deception, disguise)
- **Necromancy** (death, undead)
- **Transmutation** (alteration, transformation)

---

## Use Cases

### During Gameplay (PLAY Mode)
- **Player asks:** "Can my Cleric cast Fireball?"
  - Use: `lookup_spell("Fireball")` → Shows it's Sorcerer/Wizard only
- **Player asks:** "What healing spells does Torgga know?"
  - Use: `search_spells(query="cure", spell_class="Cleric")`
- **NPC casts spell:** "The cultist casts a 2nd-level divination spell"
  - Use: `search_spells(query="divination", spell_level=2)`

### Character Planning
- **Player leveling up:** "What 3rd-level spells can a Wizard learn?"
  - Use: `get_spells_by_class(spell_class="Wizard", spell_level=3)`
- **Multiclass planning:** "Which classes can cast Revivify?"
  - Use: `lookup_spell("Revivify")`

### World Building
- **Designing a spellcaster NPC:** "What spells would a 5th-level Warlock have?"
  - Use: `get_spells_by_class(spell_class="Warlock", spell_level=1)` (for each level 1-3)
- **Magic item creation:** "What fire spells exist?"
  - Use: `search_spells(query="fire")`

---

## Performance
- **Instant lookups** (in-memory database)
- **~50-100ms response time** (local, no API calls)
- **No network dependency** (works offline)
- **No API quotas or rate limits**

---

## Integration Status
✅ **Parser:** `parse_phb_spells.py` extracts 391 spells from PHB 2024
✅ **Database:** `spells.json` (all spells), `spells_by_class.json` (organized by class)
✅ **MCP Server:** `rules_db_server.py` provides 3 spell lookup functions
✅ **Schema:** Validated against `schema.json`

---

## Notes
- **Spell descriptions** are not included (only metadata: name, level, school, classes, components)
- To get full spell text, use the `sourcebooks` MCP to search the PHB 2024
- Spells are organized by **class and level**, making character planning easy
- **Concentration, Ritual, and Material components** are tracked for quick reference












