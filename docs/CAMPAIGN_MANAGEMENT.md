# Campaign Management Guide

## Overview

This guide explains how to create new campaigns and switch between campaigns in the D&D Cursor system. All campaigns use the same mechanic card creation system that automatically extracts DC checks, saving throws, and location/section cards from chapter text files.

## Campaign Structure

Each campaign is stored in `C:\DnD\Campaigns\<campaign_name>\` with the following structure:

```
<campaign_name>/
├── chapters/          # Chapter text files (chapter_1.txt, chapter_2.txt, etc.)
├── packs/             # Compiled JSON packs (chapter_pack_*.json, etc.)
│   └── logs/         # Build logs
├── characters/        # Character JSON files
├── saves/            # Game state files
│   ├── CURRENT_STATE.json
│   └── CAMPAIGN_EVENTS.json
├── players/           # Original character text dumps
├── exports/          # Export files
└── logs/             # Session logs
```

## Creating a New Campaign

### Step 1: Create Campaign Structure

Use the `create_new_campaign.ps1` script:

```powershell
cd C:\DnD\DnD_Cursor
.\scripts\create_new_campaign.ps1 -CampaignName "YourCampaignName" -SourceName "Your Source Book Name"
```

**Parameters:**
- `-CampaignName` (required): Campaign directory name (alphanumeric, underscores/hyphens only, no spaces)
- `-SourceName` (optional): Source book name (e.g., "Curse of Strahd", "Dragon Heist"). If omitted, uses campaign name.

**Example:**
```powershell
.\scripts\create_new_campaign.ps1 -CampaignName "Strahd" -SourceName "Curse of Strahd"
```

This will:
- Create the campaign directory structure
- Create initial save files (CURRENT_STATE.json, CAMPAIGN_EVENTS.json)
- Create initial pack files (session_preload.json, encounter_pack.json)
- Update `paths.json` to point to the new campaign

### Step 2: Add Chapter Text Files

Place your chapter text files in `C:\DnD\Campaigns\<campaign_name>\chapters\`:

- `chapter_1.txt`
- `chapter_2.txt`
- `chapter_3.txt`
- etc.

**File naming:** The build script accepts various formats:
- `chapter_1.txt` or `chapter_01.txt`
- `Chapter_1.txt` or `Chapter_01.txt`
- Case-insensitive matching

### Step 3: Build Chapter Packs

Build chapter packs using the Python script:

```powershell
python C:\DnD\DnD_Cursor\scripts\build_chapter_pack.py --chapter 1
python C:\DnD\DnD_Cursor\scripts\build_chapter_pack.py --chapter 2
# etc.
```

Or use the PowerShell wrapper (if available):

```powershell
.\scripts\build_chapter_pack.ps1 -Chapter 1
```

**What the build script does:**
1. Reads your chapter text file
2. Splits text into sections based on heading patterns:
   - Location headers (e.g., "H1: Cave Mouth", "A3: Storage Room")
   - Section headers (e.g., "Running This Chapter", "Development", "Treasure")
3. Extracts mechanic cards (gates):
   - DC checks: `DC 10 Wisdom (Survival) check`
   - Saving throws: `DC 15 Constitution saving throw`
4. Creates cards with:
   - Unique IDs (e.g., `ch01_cave_mouth_001`)
   - Type (location or section)
   - Title and content
   - Mechanics (gates) as JSON
   - References

**Output:** `C:\DnD\Campaigns\<campaign_name>\packs\chapter_pack_<n>.json`

## Switching Between Campaigns

### Method 1: Update paths.json Manually

Edit `C:\DnD\DnD_Cursor\config\paths.json`:

```json
{
  "default_campaign": "YourCampaignName",
  "default_campaign_dir": "C:\\DnD\\Campaigns\\YourCampaignName",
  "chapters_dir": "C:\\DnD\\Campaigns\\YourCampaignName\\chapters",
  "packs_dir": "C:\\DnD\\Campaigns\\YourCampaignName\\packs",
  "state_file": "C:\\DnD\\Campaigns\\YourCampaignName\\saves\\CURRENT_STATE.json",
  "source_name": "Your Source Book Name"
}
```

### Method 2: Use create_new_campaign.ps1 (Updates paths.json)

If you run `create_new_campaign.ps1` for an existing campaign, it will update `paths.json` to point to that campaign (after prompting for confirmation).

## Mechanic Card System

The mechanic card system automatically extracts game mechanics from your chapter text files:

### Supported Patterns

**DC Checks:**
- `DC 10 Wisdom (Survival) check`
- `DC 15 Dexterity (Stealth) check`
- Any format: `DC <number> <Ability> (<Skill>) check`

**Saving Throws:**
- `DC 15 Constitution saving throw`
- `DC 12 Wisdom saving throw`
- Any format: `DC <number> <Ability> saving throw`

### Card Types

**Location Cards:**
- Detected when title matches pattern: `[A-Z]{1,3}\d{1,3}:` (e.g., "H1:", "A3:", "W12:")
- Example: "H1: Cave Mouth" → location card

**Section Cards:**
- All other headings become section cards
- Examples: "Running This Chapter", "Development", "Treasure", "Tactics"

### Card Structure

Each card contains:
- `id`: Unique identifier (e.g., `ch01_cave_mouth_001`)
- `type`: "location" or "section"
- `title`: Section title
- `boxed_text`: Content (limited to 4000 characters)
- `mechanics`: JSON string of gates (DC checks/saves)
- `references`: Chapter and title reference

### Gates (Mechanics)

Gates are extracted automatically and stored in the `mechanics` field:

```json
[
  {
    "type": "check",
    "dc": 10,
    "ability": "Wisdom",
    "skill": "Survival",
    "note": ""
  },
  {
    "type": "save",
    "dc": 15,
    "ability": "Constitution",
    "skill": "",
    "note": ""
  }
]
```

## Building All Chapters

To build all chapters for a campaign, you can use a simple loop:

**PowerShell:**
```powershell
for ($i = 1; $i -le 8; $i++) {
    python C:\DnD\DnD_Cursor\scripts\build_chapter_pack.py --chapter $i
}
```

**Bash:**
```bash
for i in {1..8}; do
    python C:\DnD\DnD_Cursor\scripts\build_chapter_pack.py --chapter $i
done
```

## Verifying Campaign Setup

After creating a campaign and building packs, verify the setup:

1. **Check directory structure:**
   ```powershell
   Get-ChildItem -Path "C:\DnD\Campaigns\<campaign_name>" -Recurse -Directory
   ```

2. **Check pack files:**
   ```powershell
   Get-ChildItem -Path "C:\DnD\Campaigns\<campaign_name>\packs\*.json"
   ```

3. **Validate packs:**
   ```powershell
   .\scripts\validate_packs.ps1
   ```

## Tips

1. **Chapter Text Formatting:**
   - Use clear headings for locations (e.g., "H1: Cave Mouth")
   - Use section headers for organization (e.g., "Development", "Treasure")
   - Include DC checks in natural language (e.g., "DC 10 Wisdom (Survival) check")

2. **Source Name:**
   - Set `source_name` in `paths.json` to match your source book
   - This appears in all pack files for reference

3. **Campaign Names:**
   - Use alphanumeric names with underscores/hyphens (no spaces)
   - Examples: "Strahd", "DragonHeist", "Tomb_Of_Annhilation"

4. **Multiple Campaigns:**
   - You can have multiple campaigns in `C:\DnD\Campaigns\`
   - Switch between them by updating `paths.json`
   - Each campaign maintains its own state and character files

## Troubleshooting

**"Campaign directory not found":**
- Verify the campaign exists in `C:\DnD\Campaigns\<campaign_name>\`
- Check `paths.json` for correct paths

**"Chapter file not found":**
- Verify chapter files are in `chapters/` directory
- Check file naming (chapter_1.txt, chapter_01.txt, etc.)

**"No cards extracted":**
- Check that your chapter text has headings
- Verify text file encoding is UTF-8
- Check build logs in `packs/logs/`

**"Source name wrong in packs":**
- Update `source_name` in `paths.json`
- Rebuild packs (they will use the new source name)
































