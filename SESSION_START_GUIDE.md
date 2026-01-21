# Session Start Guide for AI DM

## Quick Resume Command

**If continuing an existing campaign, the user may say:**
- "Continue Chapter 5 - Phandelver investigation"
- "Continue Phandelver"
- "Resume campaign"

**When triggered, check:** `C:\DnD\Campaigns\Phandelver\saves\SESSION_CONTINUE_TRIGGER.md` for current state and next steps.

## Quick Start Checklist

**⚠️ NEW: Use Unified Workflow System (AUTOMATIC)**

When starting a new session, **AUTOMATICALLY** run:
```bash
python scripts/dm_workflow.py session_start
```

This workflow **AUTOMATICALLY** handles ALL initialization steps:
1. ✅ Validates checklist (pre_session_check.py)
2. ✅ Reads MECHANICS_AUTOMATION_CHECKLIST.md
3. ✅ Loads CURRENT_STATE.json
4. ✅ Loads CAMPAIGN_EVENTS.json
5. ✅ Determines current chapter from state
6. ✅ Loads chapter_pack_<n>.json automatically
7. ✅ Verifies MCP servers
8. ✅ Creates workflow state tracker

**The workflow BLOCKS until all steps complete. You cannot proceed without it.**

---

## Manual Steps (If Not Using Workflow)

If you need to do steps manually (not recommended):

### 0. Read Mechanics Checklist (MANDATORY)
- **ALWAYS read first:** `C:\DnD\DnD_Cursor\MECHANICS_AUTOMATION_CHECKLIST.md`
- This ensures you remember ALL mandatory procedures:
  - Post-combat XP/currency/item distribution
  - Real-time Obsidian sync requirements
  - NPC status update automation
  - Quest management procedures
  - Faction reputation tracking
  - Spell slot/resource deduction
  - Inventory management
  - Dice rolling procedures
  - Rules/spells/monsters lookups

### 1. Read Current State
- **Always start by reading:** `C:\DnD\Campaigns\Phandelver\saves\CURRENT_STATE.json`
- This tells you:
  - Current location/area
  - Combat status
  - Completed encounters
  - Revealed information (gates)
  - Party composition

### 1b. Read Campaign Events (CRITICAL - Story Continuity)
- **Always read:** `C:\DnD\Campaigns\Phandelver\saves\CAMPAIGN_EVENTS.json`
- This tells you:
  - Past choices made by the party
  - Active consequences from past choices
  - NPC relationship history
  - Quest status and progress
  - Faction relationships
  - Cross-campaign effects
- **This file tracks everything that happens, choices made, and their long-lasting effects on the campaign and beyond.**

### 2. Verify Character Files
- Check that character JSON files exist: `C:\DnD\Campaigns\Phandelver\characters\*.json`
- Required characters: Brevin, Ergath (Eglath), Torgga, Vandross
- Verify files contain: name, class, level, ac, hp, stats

### 3. Load Relevant Chapter Pack
- Check `CURRENT_STATE.json` for current chapter/scene
- Load appropriate `chapter_pack_<n>.json` from `C:\DnD\Campaigns\Phandelver\packs\`
- Load `encounter_pack.json` if in combat or preparing encounters

### 4. Verify MCP Servers (CRITICAL - MANDATORY)
- **MCP servers provide instant lookups for D&D mechanics - ALWAYS use them.**
- **MANDATORY tools:**
  - `rules-database` MCP - Spells, monsters, conditions, rules, actions (391 spells, 499 monsters, 15 conditions)
  - `sourcebooks` MCP - Full sourcebook text (DMG 2024, PHB 2024, MM 2024)
  - `dice-roller` MCP - Cryptographically secure random dice rolls (for NPC/system rolls)
  - `music-ambience` MCP - Ambient music and sound effects for immersion
  - `session-recorder` MCP - Session logging, event tracking, and automatic CAMPAIGN_EVENTS.json updates
- **NEVER guess or invent D&D mechanics - use MCP servers.**
- **Examples:**
  - Player asks about spell → `lookup_spell("Fireball")`
  - Running encounter → `lookup_monster("Goblin")`
  - Applying condition → `lookup_condition("Exhaustion")`
  - Need rule clarification → `lookup_rule("Grapple")`
  - Session logging → `start_session_log("Campaign")` then `log_event(type, content)` (optional, for session tracking)
- **See `.cursorrules` MCP SERVERS section for complete usage guide.**

### 5. Review Key Rules (in .cursorrules)
- PLAY MODE rules (use MCP servers + packs, don't read raw text files)
- Gates system (check state before revealing information)
- Combat rules (initiative, attacks, damage)
- Skill check rules (wait for player rolls, calculate DCs properly)
- **MCP Server usage (MANDATORY - always use for rules/spells/monsters/conditions)**
- **Choices and Consequences system (track all significant choices, create consequences, ensure long-lasting effects)**

### 6. Common Commands/Workflows

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
- **Campaign Events: `C:\DnD\Campaigns\Phandelver\saves\CAMPAIGN_EVENTS.json` (tracks choices, consequences, NPC relationships)**

### System Files
- Rules: `C:\DnD\DnD_Cursor\.cursorrules`
- Config: `C:\DnD\DnD_Cursor\config\paths.json`
- Scripts: `C:\DnD\DnD_Cursor\scripts\`
- Keys: `C:\DnD\keys\google_sheets_key.json`

## Important Reminders

1. **Always check CURRENT_STATE.json first** - it tells you where you are
2. **Always check CAMPAIGN_EVENTS.json** - it tells you past choices, consequences, and NPC relationships
3. **ALWAYS use MCP servers for rules/spells/monsters/conditions** - NEVER guess or invent mechanics
4. **Never read raw .txt files in PLAY mode** - use MCP servers for mechanics, JSON packs for story
5. **Always load character files before combat** - don't guess stats
6. **Check gates/discoveries in state** before revealing information
7. **Wait for player roll results** before describing outcomes
8. **Calculate DCs properly** - use opponent stats or standard DCs, not arbitrary numbers
9. **Enemy turns are automatic** - don't ask players what enemies do
10. **Use Google Sheets scripts** for XP/currency updates - don't edit JSON manually
11. **Track significant choices** - log all important player decisions in CAMPAIGN_EVENTS.json
12. **Create consequences** - ensure choices have long-lasting effects that manifest appropriately

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

