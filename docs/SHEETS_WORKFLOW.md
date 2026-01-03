# Google Sheets Integration Workflow

## Overview

The Google Sheets integration provides bidirectional sync between local character JSON files and Google Sheets for tracking:
- **XP** (experience points)
- **Currency** (cp, sp, ep, gp, pp)
- **Resources** (rage, superiority_dice, spell slots, etc.)
- **HP** (read-only from sheets, managed in sheets)
- **Inventory** (read-only from sheets, managed in sheets)

## Two-Way Sync

### Pull FROM Sheets → Local JSON
**Script:** `sync_characters_from_sheets.py`

Reads all character data from Google Sheets and updates local JSON files:
- HP (current/max)
- AC
- XP
- Resources
- Spell slots
- Inventory
- Currency

**Usage:**
```powershell
python C:\DnD\DnD_Cursor\scripts\sync_characters_from_sheets.py
```

### Push TO Sheets ← Local JSON
**Script:** `update_sheets_data.py`

Updates Google Sheets with data from local JSON files or direct commands:
- XP updates
- Currency updates
- Resource updates

**Usage:**
```powershell
# Update XP
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py xp "Ergath" 3000

# Update currency
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py currency "Brevin" --gp 200

# Update resource
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py resource "Ergath" rage --remaining 1

# Full sync from JSON
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py sync "C:\DnD\Campaigns\Phandelver\characters\Ergath.json"
```

## Typical Workflow

### Session Start
1. **Pull latest data from sheets:**
   ```powershell
   python C:\DnD\DnD_Cursor\scripts\sync_characters_from_sheets.py
   ```
   This ensures local JSON files have current HP, XP, currency, resources.

### During Combat
1. **Track resource usage:**
   ```powershell
   # Use rage
   python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py resource "Ergath" rage --remaining 1 --active
   
   # Use spell slot
   python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py resource "Torgga" "1st" --remaining 3
   ```

2. **Update HP in sheets directly** (or use sync to pull after manual update)

### After Combat
1. **Award XP:**
   ```powershell
   python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py xp "Brevin" 3100
   python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py xp "Ergath" 3000
   ```

2. **Distribute loot:**
   ```powershell
   python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py currency "Brevin" --gp 50
   python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py currency "Ergath" --gp 50
   ```

3. **Update inventory in sheets directly** (CSV_Inventory tab)

### After Rest
1. **Restore resources:**
   ```powershell
   # Long rest - restore all resources
   python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py resource "Ergath" rage --max 3 --remaining 3
   python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py resource "Vandross" superiority_dice --max 4 --remaining 4
   ```

2. **Pull updated HP from sheets:**
   ```powershell
   python C:\DnD\DnD_Cursor\scripts\sync_characters_from_sheets.py
   ```

## Sheet Structure

### CSV_Characters
- `character_id` - Unique identifier
- `name` - Character name
- `class_level` - "Class Level" format
- `level` - Numeric level
- `hp_current` - Current HP
- `hp_max` - Maximum HP
- `ac` - Armor Class
- `xp` - Experience points
- `speed_override` - Movement speed
- `condition_notes` - Features/abilities

### CSV_Currency
- `character_id` - Links to character
- `name` - Character name
- `cp`, `sp`, `ep`, `gp`, `pp` - Currency amounts

### CSV_Resources
- `character_id` - Links to character
- `name` - Character name
- `resource` - Resource name (rage, superiority_dice, 1st, 2nd, etc.)
- `max` - Maximum uses
- `remaining` - Remaining uses
- `active` - Yes/No for active resources

### CSV_Inventory
- `character_id` - Links to character
- `name` - Character name
- `Now ` - Item name (note the trailing space)
- `quantity` - Item quantity
- `weight_lbs` - Item weight
- `type` - Item type
- `equipped` - Yes/No
- `notes` - Item notes

## Character Name Mapping

The scripts handle these name variations:
- `Brevin` / `Brovin` → `Halfling Rogue` (in sheet)
- `Ergath` → `Eglath Bearkiller` (in sheet)

## Best Practices

1. **HP Management**: Update HP directly in sheets, then sync to pull to local JSON
2. **XP Tracking**: Use `update_sheets_data.py xp` after each encounter
3. **Resource Tracking**: Update resources immediately when used
4. **Currency**: Update currency after loot distribution
5. **Regular Sync**: Pull from sheets at session start and after major updates

## Integration with Combat System

The combat system can:
- Read character stats from local JSON files (synced from sheets)
- Update XP after encounters
- Update resources during combat
- Update currency after loot
- Pull updated HP from sheets after rest

## Troubleshooting

### Character not found
- Check name mapping (Brevin → Halfling Rogue, Ergath → Eglath Bearkiller)
- Verify character exists in CSV_Characters sheet

### Resource not found
- Verify resource name matches exactly (case-sensitive)
- Check CSV_Resources sheet for exact resource names

### Update failed
- Verify service account has edit permissions on the sheet
- Check spreadsheet ID is correct
- Verify credentials file path



