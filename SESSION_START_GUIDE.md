# Session Start Guide for AI DM

## Quick Start Checklist

When starting a new session, follow these steps:

### 1. Read Current State
- **Always start by reading:** `C:\DnD\Campaigns\Phandelver\saves\CURRENT_STATE.json`
- This tells you:
  - Current location/area
  - Combat status
  - Completed encounters
  - Revealed information (gates)
  - Party composition

### 2. Verify Character Files
- Check that character JSON files exist: `C:\DnD\Campaigns\Phandelver\characters\*.json`
- Required characters: Brevin, Ergath (Eglath), Torgga, Vandross
- Verify files contain: name, class, level, ac, hp, stats

### 3. Load Relevant Chapter Pack
- Check `CURRENT_STATE.json` for current chapter/scene
- Load appropriate `chapter_pack_<n>.json` from `C:\DnD\Campaigns\Phandelver\packs\`
- Load `encounter_pack.json` if in combat or preparing encounters

### 4. Review Key Rules (in .cursorrules)
- PLAY MODE rules (don't read raw text files)
- Gates system (check state before revealing information)
- Combat rules (initiative, attacks, damage)
- Skill check rules (wait for player rolls, calculate DCs properly)

### 5. Common Commands/Workflows

#### Starting a Session
1. Read `CURRENT_STATE.json`
2. Present the current scene based on state
3. Wait for player actions

#### Combat Flow
1. Request initiative rolls (all players)
2. Roll enemy initiative
3. Process turns in order
4. Request attack/damage rolls from players
5. Process enemy turns automatically
6. Update state after combat

#### Granting XP/Loot
1. Calculate XP (use standard D&D 5e values)
2. Divide equally among party members
3. Update Google Sheets using:
   ```powershell
   python "C:\DnD\DnD_Cursor\scripts\update_sheets_data.py" xp "Character Name" <new_xp>
   ```
4. For currency, get current values from sheets first, then add loot
5. Update currency using:
   ```powershell
   python "C:\DnD\DnD_Cursor\scripts\update_sheets_data.py" currency "Character Name" --cp <cp> --sp <sp> --ep <ep> --gp <gp> --pp <pp>
   ```

#### Character Names in Sheets
- Brevin → "Brevin" (character_id: halfling_rogue)
- Ergath → "Eglath Bearkiller" (character_id: eglath_bearkiller)
- Torgga → "Torgga Brawnanvil" (character_id: torgga_brawnanvil)
- Vandross → "Vandross Ephrates" (character_id: vandross_ephrates)

## Key File Locations

### Campaign Data
- Campaign root: `C:\DnD\Campaigns\Phandelver` (NOTE: "Campaigns" plural)
- Characters: `C:\DnD\Campaigns\Phandelver\characters\*.json`
- Packs: `C:\DnD\Campaigns\Phandelver\packs\*.json`
- State: `C:\DnD\Campaigns\Phandelver\saves\CURRENT_STATE.json`

### System Files
- Rules: `C:\DnD\DnD_Cursor\.cursorrules`
- Config: `C:\DnD\DnD_Cursor\config\paths.json`
- Scripts: `C:\DnD\DnD_Cursor\scripts\`
- Keys: `C:\DnD\keys\google_sheets_key.json`

## Important Reminders

1. **Always check CURRENT_STATE.json first** - it tells you where you are
2. **Never read raw .txt files in PLAY mode** - only use JSON packs
3. **Always load character files before combat** - don't guess stats
4. **Check gates/discoveries in state** before revealing information
5. **Wait for player roll results** before describing outcomes
6. **Calculate DCs properly** - use opponent stats or standard DCs, not arbitrary numbers
7. **Enemy turns are automatic** - don't ask players what enemies do
8. **Use Google Sheets scripts** for XP/currency updates - don't edit JSON manually

## Common Issues & Solutions

### "Campaign folder not found"
- Check: Is it `Campaigns` (plural) not `Campaign` (singular)?
- Correct path: `C:\DnD\Campaigns\Phandelver`

### "Character not found in sheets"
- Use full names: "Eglath Bearkiller", "Torgga Brawnanvil", "Vandross Ephrates", "Brevin"
- Check character_id mapping in update_sheets_data.py if needed

### "Missing character data"
- Verify JSON files exist in `C:\DnD\Campaigns\Phandelver\characters\`
- Check file names match character names

### "Can't find scene/location"
- Read CURRENT_STATE.json for current area
- Load appropriate chapter_pack based on state
- Check session_preload.json for current scene_id

## Session Continuity

After each session, ensure:
- CURRENT_STATE.json is updated (if the system does this automatically)
- XP and loot are recorded in Google Sheets
- Any important discoveries/gates are tracked in state
- Combat state is cleared if combat ended

## Reference Documents

- `.cursorrules` - Core rules and constraints
- `CAMPAIGN_PATHS.md` - File locations and paths
- `dm_guidelines.md` - DM best practices (if exists)
- Chapter packs - Location/encounter data
- Character JSON files - Character stats

