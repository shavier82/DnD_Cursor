# Campaign Paths

## Party Persistent Data (Cross-Campaign)
- **File:** `C:\DnD\PARTY_PERSISTENT_DATA.json`
- **Purpose:** Tracks benefits, rewards, and advantages that persist across ALL campaigns
- **Contains:**
  - Recurring income (e.g., mine profit shares)
  - Boons (permanent benefits from quests or events)
  - Permanent benefits (items, titles, relationships that carry over)
  - Cross-campaign relationships (NPCs who know the party from previous campaigns)
- **Usage:** This file is read and updated when the party earns rewards or benefits that should persist beyond a single campaign

## Campaign-Specific Data Reference

### Campaign Events (Choices and Consequences)
- **File:** `C:\DnD\Campaigns\<campaign>\saves\CAMPAIGN_EVENTS.json`
- **Purpose:** Static JSON file that tracks everything that happens, choices made, and their long-lasting effects on the campaign and beyond
- **Contains:**
  - Events (story events, encounters, quests)
  - Choices log (all significant player decisions with alternatives, impact, and consequences)
  - Consequences (active and resolved long-term effects from choices)
  - NPC relationships (history, interactions, how choices affected them)
  - Quest status and progress
  - Faction relationships
  - Cross-campaign effects (choices that affect future campaigns)
- **Usage:** 
  - Read at session start to understand story context
  - Check before NPC interactions to reference past choices
  - Update when significant choices are made
  - Create consequences when choices have long-term effects
  - Reference when determining outcomes to ensure past choices matter
- **Critical:** This file ensures choices have long-lasting effects and that past decisions impact future events

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
    ├── CURRENT_STATE.json      ← Current game state (location, combat, gates)
    └── CAMPAIGN_EVENTS.json    ← Choices, consequences, NPC relationships, story continuity
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




   - Verify files exist: `Get-ChildItem "C:\DnD\Campaigns\Phandelver\characters\*.json"`

## Current Session Status

**Last Saved**: 2026-01-02 21:55:17
**Location**: Goblin trail, scouting for goblin guards
**Party**: Brevin, Ergath, Torgga, Vandross
**Next Action**: Awaiting Stealth/Perception rolls for scouting




   - Verify files exist: `Get-ChildItem "C:\DnD\Campaigns\Phandelver\characters\*.json"`

## Current Session Status

**Last Saved**: 2026-01-02 21:55:17
**Location**: Goblin trail, scouting for goblin guards
**Party**: Brevin, Ergath, Torgga, Vandross
**Next Action**: Awaiting Stealth/Perception rolls for scouting




   - Verify files exist: `Get-ChildItem "C:\DnD\Campaigns\Phandelver\characters\*.json"`

## Current Session Status

**Last Saved**: 2026-01-02 21:55:17
**Location**: Goblin trail, scouting for goblin guards
**Party**: Brevin, Ergath, Torgga, Vandross
**Next Action**: Awaiting Stealth/Perception rolls for scouting




   - Verify files exist: `Get-ChildItem "C:\DnD\Campaigns\Phandelver\characters\*.json"`

## Current Session Status

**Last Saved**: 2026-01-02 21:55:17
**Location**: Goblin trail, scouting for goblin guards
**Party**: Brevin, Ergath, Torgga, Vandross
**Next Action**: Awaiting Stealth/Perception rolls for scouting




   - Verify files exist: `Get-ChildItem "C:\DnD\Campaigns\Phandelver\characters\*.json"`

## Current Session Status

**Last Saved**: 2026-01-02 21:55:17
**Location**: Goblin trail, scouting for goblin guards
**Party**: Brevin, Ergath, Torgga, Vandross
**Next Action**: Awaiting Stealth/Perception rolls for scouting




   - Verify files exist: `Get-ChildItem "C:\DnD\Campaigns\Phandelver\characters\*.json"`

## Current Session Status

**Last Saved**: 2026-01-02 21:55:17
**Location**: Goblin trail, scouting for goblin guards
**Party**: Brevin, Ergath, Torgga, Vandross
**Next Action**: Awaiting Stealth/Perception rolls for scouting




   - Verify files exist: `Get-ChildItem "C:\DnD\Campaigns\Phandelver\characters\*.json"`

## Current Session Status

**Last Saved**: 2026-01-02 21:55:17
**Location**: Goblin trail, scouting for goblin guards
**Party**: Brevin, Ergath, Torgga, Vandross
**Next Action**: Awaiting Stealth/Perception rolls for scouting




   - Verify files exist: `Get-ChildItem "C:\DnD\Campaigns\Phandelver\characters\*.json"`

## Current Session Status

**Last Saved**: 2026-01-02 21:55:17
**Location**: Goblin trail, scouting for goblin guards
**Party**: Brevin, Ergath, Torgga, Vandross
**Next Action**: Awaiting Stealth/Perception rolls for scouting



