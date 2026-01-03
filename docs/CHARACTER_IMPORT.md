# Character Import and Management

## Overview

Character data is stored as JSON files in `C:\DnD\Campaigns\Phandelver\players\`. Each character has a JSON file containing all their stats, resources, spell slots, and XP.

## Character JSON Schema

Each character JSON file contains:

- **Basic Info**: name, level, class, race, background, alignment
- **XP Tracking**: current XP, XP to next level
- **Ability Scores**: strength, dexterity, constitution, intelligence, wisdom, charisma
- **Ability Modifiers**: calculated modifiers
- **Proficiency Bonus**: based on level
- **Saving Throws**: which saves are proficient
- **Skills**: skill proficiencies
- **Hit Points**: current, maximum, temporary
- **Combat Stats**: armor class, initiative, speed
- **Spellcasting**: 
  - Spell ability modifier
  - Spell save DC
  - Spell attack bonus
  - Spell slots (by level, with used/total tracking)
  - Prepared spells
  - Known spells
  - Cantrips
- **Features**: class/race features
- **Equipment**: items carried
- **Resources**: custom resources (ki points, sorcery points, etc.)
- **Notes**: additional notes

## Import Scripts

### Import Character (Create/Update)

```powershell
python scripts\import_character.py --name "Character Name" --pdf "path\to\character.pdf"
```

**Options:**
- `--name`: Character name (required)
- `--pdf`: Path to character sheet PDF (optional, creates template if not provided)
- `--update-xp <amount>`: Add XP to character
- `--reset-spell-slots`: Reset all spell slots to full

**Examples:**

```powershell
# Create new character from PDF
python scripts\import_character.py --name "Aragorn" --pdf "C:\DnD\Campaigns\Phandelver\players\ShavierT1982_95127852.pdf"

# Add XP to character
python scripts\import_character.py --name "Aragorn" --update-xp 450

# Reset spell slots (long rest)
python scripts\import_character.py --name "Aragorn" --reset-spell-slots
```

### List All Characters

```powershell
python scripts\list_characters.py
```

Shows all characters with their level, XP, and class.

## XP Tracking

XP is automatically tracked and level is calculated based on standard D&D 5e XP thresholds:

- Level 1: 0 XP
- Level 2: 300 XP
- Level 3: 900 XP
- Level 4: 2,700 XP
- Level 5: 6,500 XP
- ... (continues to level 20)

When XP is added, the script:
1. Updates total XP
2. Calculates new level if threshold is reached
3. Updates proficiency bonus
4. Calculates XP needed for next level

## Spell Slot Tracking

Spell slots are tracked by level (1-9) with `used` and `total` counts:

```json
"spell_slots": {
  "1": {"total": 2, "used": 1},
  "2": {"total": 0, "used": 0}
}
```

Use `--reset-spell-slots` after a long rest to reset all used slots to 0.

## Manual Updates

Since PDF parsing is not yet implemented, you'll need to manually update character JSON files with data from the PDFs. The template provides all necessary fields.

## File Locations

- Character JSON files: `C:\DnD\Campaigns\Phandelver\players\*.json`
- Character PDFs: `C:\DnD\Campaigns\Phandelver\players\*.pdf`

## Future Enhancements

- PDF text extraction and parsing
- Automatic ability score calculation
- Spell slot calculation based on class/level
- Integration with parallel agents for character-aware gameplay



