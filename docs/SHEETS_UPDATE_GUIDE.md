# Google Sheets Update Guide

This guide explains how to update character data in Google Sheets for XP, currency, inventory, and resources.

## Overview

The `update_sheets_data.py` script allows you to:
- **Update XP** for characters
- **Update currency** (cp, sp, ep, gp, pp)
- **Add inventory items** to CSV_Inventory sheet
- **Update resources** (rage, superiority_dice, spell slots, etc.)
- **Sync from local JSON files** (updates all tracked data)

## Commands

### Update XP

```powershell
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py xp "Ergath" 3000
```

This updates Ergath's XP to 3000 in the `CSV_Characters` sheet.

### Update Currency

```powershell
# Update gold only
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py currency "Brevin" --gp 200

# Update multiple currency types
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py currency "Torgga" --cp 50 --sp 20 --gp 100
```

### Add Inventory Item

```powershell
# Add a basic item
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py inventory "Brevin" "Potion of Healing" --type "Potion" --notes "Loot: Goblin ambush"

# Add a weapon (equipped)
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py inventory "Eglath Bearkiller" "Hew (+1 battleaxe)" --type "Weapon (Battleaxe)" --equipped "Yes" --notes "+1 battleaxe, max damage vs Plant creatures. Loot: Venomfang's hoard"

# Add a spell scroll
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py inventory "Torgga Brawnanvil" "Spell scroll of lightning bolt" --type "Spell Scroll" --notes "Loot: Venomfang's hoard"

# Add treasure with quantity
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py inventory "Vandross Ephrates" "Silver goblet with moonstone" --type "Treasure" --quantity 1 --notes "Value: 60 gp. Loot: Venomfang's hoard"
```

**Inventory Item Parameters:**
- `character` - Character name (required)
- `item` - Item name (required)
- `--type` - Item type (e.g., "Weapon", "Spell Scroll", "Treasure", "Potion")
- `--equipped` - "Yes" or "No" (default: "No")
- `--notes` - Item notes/description
- `--quantity` - Quantity (default: 1)
- `--weight` - Weight in lbs (optional)

### Update Resources

```powershell
# Update rage remaining
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py resource "Ergath" rage --remaining 1

# Update rage max and remaining
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py resource "Ergath" rage --max 3 --remaining 2

# Set resource as active
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py resource "Ergath" rage --active
```

### Sync from JSON File

This syncs XP, currency, and resources from a local character JSON file:

```powershell
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py sync "C:\DnD\Campaigns\Phandelver\characters\Ergath.json"
```

## Character Name Mapping

The script handles these name variations:
- `Brevin` / `Brovin` → `Halfling Rogue` (in sheet)
- `Ergath` → `Eglath Bearkiller` (in sheet)

## What Gets Updated

### CSV_Characters
- `xp` - Experience points

### CSV_Currency
- `cp` - Copper pieces
- `sp` - Silver pieces
- `ep` - Electrum pieces
- `gp` - Gold pieces
- `pp` - Platinum pieces

### CSV_Resources
- `max` - Maximum uses
- `remaining` - Remaining uses
- `active` - Whether the resource is currently active (Yes/No)

Common resources:
- `rage` - Barbarian rage
- `superiority_dice` - Fighter superiority dice
- `second_wind` - Fighter second wind
- `action_surge` - Fighter action surge
- Spell slots (tracked by level: `1st`, `2nd`, etc.)

## Workflow

### After Combat (XP and Loot)

1. **Award XP:**
   ```powershell
   python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py xp "Brevin" 3100
   ```

2. **Distribute Currency:**
   ```powershell
   python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py currency "Brevin" --gp 50
   python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py currency "Ergath" --gp 50
   ```

3. **Add Inventory Items:**
   ```powershell
   python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py inventory "Brevin" "Spell scroll of misty step" --type "Spell Scroll" --notes "Loot: Venomfang's hoard"
   python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py inventory "Eglath Bearkiller" "Hew (+1 battleaxe)" --type "Weapon (Battleaxe)" --equipped "Yes" --notes "Loot: Venomfang's hoard"
   ```

### During Combat (Resources)

1. **Use Rage:**
   ```powershell
   python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py resource "Ergath" rage --remaining 1 --active
   ```

2. **End Rage:**
   ```powershell
   python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py resource "Ergath" rage --active
   ```
   (Remove `--active` flag to set to inactive)

### Full Sync (After Local Updates)

If you've updated character JSON files locally and want to push all changes:

```powershell
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py sync "C:\DnD\Campaigns\Phandelver\characters\Ergath.json"
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py sync "C:\DnD\Campaigns\Phandelver\characters\Brevin.json"
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py sync "C:\DnD\Campaigns\Phandelver\characters\Torgga.json"
python C:\DnD\DnD_Cursor\scripts\update_sheets_data.py sync "C:\DnD\Campaigns\Phandelver\characters\Vandross.json"
```

## Notes

- **HP tracking**: HP is managed in the sheets directly (not updated via this script)
- **Inventory**: Inventory can now be added via `inventory` command, or managed directly in `CSV_Inventory` sheet
- **Read-only sync**: Use `sync_characters_from_sheets.py` to pull data FROM sheets TO local JSON files
- **Write-only updates**: Use `update_sheets_data.py` to push data FROM local JSON TO sheets

## Integration with Combat System

The combat system can call these update functions after:
- XP awards
- Loot distribution
- Resource usage (rage, spell slots, etc.)
- Short/long rest (restore resources)



