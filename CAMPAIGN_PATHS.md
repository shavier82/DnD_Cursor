# Campaign Paths Reference

## Critical Path Information

**IMPORTANT**: The campaign directory is `C:\DnD\Campaigns` (plural "Campaigns"), NOT `C:\DnD\Campaign`.

## Key Directories

### Root Structure
```
C:\DnD\
├── Campaigns\          ← Campaign data (NOTE: plural "Campaigns")
│   └── Phandelver\      ← Current campaign
├── DnD_Cursor\         ← System scripts and config
├── keys\               ← Google Sheets API keys
└── Sourcebooks\        ← D&D source material
```

### Phandelver Campaign Structure
```
C:\DnD\Campaigns\Phandelver\
├── characters\         ← Character JSON files
│   ├── Brevin.json
│   ├── Ergath.json
│   ├── Torgga.json
│   └── Vandross.json
├── chapters\           ← Chapter content
├── packs\              ← Chapter pack JSON files
│   └── chapter_pack_1.json
├── players\            ← Original character text dumps
└── saves\              ← Game state saves
    └── CURRENT_STATE.json
```

## Configuration File

The system uses `C:\DnD\DnD_Cursor\config\paths.json` for all path references.

**Current paths.json contents:**
```json
{
  "sourcebooks_dir": "C:\\DnD\\Sourcebooks",
  "campaigns_root": "C:\\DnD\\Campaigns",
  "default_campaign": "Phandelver",
  "default_campaign_dir": "C:\\DnD\\Campaigns\\Phandelver",
  "chapters_dir": "C:\\DnD\\Campaigns\\Phandelver\\chapters",
  "packs_dir": "C:\\DnD\\Campaigns\\Phandelver\\packs",
  "state_file": "C:\\DnD\\Campaigns\\Phandelver\\saves\\CURRENT_STATE.json"
}
```

## Quick Verification Commands

### PowerShell - Verify Campaign Directory Exists
```powershell
Test-Path "C:\DnD\Campaigns\Phandelver"
# Should return: True
```

### PowerShell - List Campaign Structure
```powershell
Get-ChildItem -Path "C:\DnD\Campaigns\Phandelver" -Recurse -Directory | Select-Object FullName
```

### PowerShell - Check Current State
```powershell
Get-Content "C:\DnD\Campaigns\Phandelver\saves\CURRENT_STATE.json" | ConvertFrom-Json
```

## Common Issues

1. **"Campaign folder not found"**
   - Check: Is it `Campaigns` (plural) or `Campaign` (singular)?
   - Correct: `C:\DnD\Campaigns\Phandelver`
   - Wrong: `C:\DnD\Campaign\Phandelver`

2. **"paths.json not found"**
   - Location: `C:\DnD\DnD_Cursor\config\paths.json`
   - If missing, create it with the structure above

3. **"Character files not found"**
   - Location: `C:\DnD\Campaigns\Phandelver\characters\*.json`
   - Verify files exist: `Get-ChildItem "C:\DnD\Campaigns\Phandelver\characters\*.json"`

## Current Session Status

**Last Saved**: 2026-01-02 21:55:17
**Location**: Goblin trail, scouting for goblin guards
**Party**: Brevin, Ergath, Torgga, Vandross
**Next Action**: Awaiting Stealth/Perception rolls for scouting



