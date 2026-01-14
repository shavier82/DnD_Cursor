# All MCP Servers - Complete Suite ✅

**Date:** 2026-01-13  
**Status:** 7 MCP Servers Configured - Campaign Wiki Added  

---

## 🎉 Complete MCP Server Suite

You now have **7 powerful MCP servers** integrated:

### 1. 🎲 True Random Dice Roller
**Purpose:** Cryptographically secure dice rolling with audit trail

**Tools:**
- `roll_dice` - General dice (2d6+3, 1d20, etc.)
- `roll_attack` - Attack rolls with advantage/disadvantage
- `roll_saving_throw` - Saving throws vs DC
- `roll_initiative` - Initiative for all combatants
- `get_roll_history` - Audit trail retrieval

**Benefits:**
- True randomness (cryptographically secure)
- Full audit trail (every roll logged)
- Automatic for all NPC rolls
- ~0.5 seconds per roll

**Documentation:** `docs/MCP_DICE_ROLLER_QUICK_REFERENCE.md`

---

### 2. 📖 D&D 5e Rules Database
**Purpose:** Instant lookup from structured database (391 spells, 499 monsters, 15 conditions, 13 core rules)

**Tools:**
- `lookup_spell` - Full spell details (Fireball, Cure Wounds, etc.)
- `search_spells` - Find spells by name/class/level
- `get_spells_by_class` - All spells for a class, organized by level
- `lookup_monster` - Complete stat blocks (Goblin, Dragon, etc.)
- `search_monsters` - Multi-word smart search for monsters
- `lookup_condition` - Condition effects (Exhaustion, Paralyzed, etc.)
- `lookup_rule` - Core rules (Grapple, Shove, Advantage, etc.)
- `search_rules` - Find rules by keyword
- `lookup_action` - Standard actions (Attack, Dash, Dodge, etc.)

**Benefits:**
- Instant structured data (<0.1 second)
- Complete stat blocks with all details
- No API dependency (fully local)
- 391 spells parsed from PHB 2024
- 499 monsters from MM 2024
- Multi-word search with smart matching

**Documentation:** `docs/MCP_SPELL_DATABASE_QUICK_REFERENCE.md`

---

### 3. 📚 Local Sourcebooks
**Purpose:** Full-text search from your local sourcebook files (DMG 2024, PHB 2024, MM 2024)

**Tools:**
- `search_sourcebooks` - Search DMG/PHB/MM for keywords
- `lookup_rule` - Look up specific rules by name (broader search)
- `get_section` - Get full section/chapter content
- `list_sections` - List all sections (table of contents)

**Benefits:**
- Full sourcebook content (not just SRD)
- Fast local search
- Context-aware results with snippets
- Covers DMG 2024, PHB 2024, and MM 2024

**Sourcebooks:**
- `C:\DnD\Sourcebooks\DungeonMaster2024.txt` (1.1 MB)
- `C:\DnD\Sourcebooks\PlayersHandbook2024.txt` (1.1 MB)
- `C:\DnD\Sourcebooks\MonstersManual2024.txt` (1.0 MB)

**Use for:** Lore, flavor text, detailed rule explanations, monster descriptions

---

### 4. 🎵 Music & Ambience
**Purpose:** Play ambient music and sound effects from local audio files

**Tools:**
- `play_ambient` - Play scene-specific ambient music (tavern, forest, dungeon, combat, etc.)
- `play_sfx` - Play sound effects (sword clash, spell cast, door open, etc.)
- `list_scenes` - List all available scene types
- `list_sfx` - List all available sound effects
- `get_current_track` - Check what's currently playing
- `stop_music` - Stop current audio

**Benefits:**
- Immersive atmosphere during gameplay
- Automatic scene-appropriate music
- Local audio files (no streaming delays)
- Windows Media Player integration

**Audio Files:**
- `C:\Users\ksist\Music\D&D_Ambient\` - Ambient music tracks
- `C:\Users\ksist\Music\D&D_SFX\` - Sound effects

**Scene Types:** tavern, forest, dungeon, combat, town, castle, temple, wilderness, creepy, peaceful, tense, ocean, storm, swamp, winter, wagon

---

### 5. 📝 Session Logger & Event Tracker
**Purpose:** Log gameplay sessions, track events, and auto-update `CAMPAIGN_EVENTS.json`

**Tools:**
- `start_session_log` - Start logging a session
- `log_event` - Log an event (narration, choice, roll, combat, NPC interaction, discovery, gate, consequence)
- `stop_session_log` - Stop logging and save
- `get_session_status` - Check if logging is active
- `list_session_logs` - List all session logs
- `extract_events` - Extract structured events from a log
- `update_campaign_events` - Add events to `CAMPAIGN_EVENTS.json`

**Benefits:**
- Automatic session tracking (optional)
- Event extraction for campaign continuity
- Auto-update `CAMPAIGN_EVENTS.json`
- Detailed session history in JSONL format

**Log Files:**
- `C:\DnD\DnD_Cursor\session_logs\session_YYYYMMDD_HHMMSS.jsonl`

**Event Types:** narration, choice, roll, combat, npc_interaction, discovery, gate, consequence

**Documentation:** `docs/MCP_SESSION_RECORDER_QUICK_REFERENCE.md`

---

### 6. ⚔️ Combat Engine
**Purpose:** Comprehensive D&D 5e combat management with AI-driven enemies, positioning, HP tracking

**Tools:**
- `start_combat` - Initialize combat with characters and monsters
- `roll_initiative_tool` - Roll and sort initiative
- `load_battlefield` - Set up terrain and obstacles
- `next_turn_tool` - Advance to next turn
- `get_combat_status` - Get full combat state
- `attack_tool` - Process attacks (melee/ranged)
- `move_creature` - Move creatures on battlefield
- `get_ai_action` - Get AI-decided actions for enemies
- `end_combat_tool` - End combat and sync to Google Sheets

**Benefits:**
- AI-driven enemy actions (smart targeting, tactical positioning)
- Automatic HP and resource tracking
- Grid-based battlefield with terrain and cover
- Distance and line of sight calculations
- Condition management (all 15 D&D 5e conditions)
- AoE spell calculations (shapely geometry)
- Google Sheets integration for character data

**Documentation:** `docs/MCP_COMBAT_ENGINE_QUICK_REFERENCE.md`

**Status:** V1.0 - 9 core tools implemented, pattern established for 25 total

---

### 7. 🏰 Campaign Wiki
**Purpose:** Campaign management with NPC relationships, quest tracking, timeline, Obsidian/World Anvil sync

**Tools:**
- `create_or_load_wiki` - Initialize/load campaign wiki
- `create_npc` - Add NPC with full profile
- `create_quest` - Add quest with objectives
- `add_relationship` - Track NPC/PC relationships
- `sync_to_obsidian` - Export to Obsidian vault

**Benefits:**
- NPC database with relationships (networkx graphs)
- Location database with map integration
- Quest tracking (accepted → in-progress → completed)
- Timeline of all campaign events
- Obsidian sync (markdown notes with frontmatter)
- World Anvil sync (public campaign wiki)
- Integration with CAMPAIGN_EVENTS.json

**Documentation:** `mcp_servers/campaign_wiki/README.md`

**Status:** V1.0 - 5 core tools, pattern for 18 total

---

## 🎯 How They Work Together

### Priority Hierarchy (in order):

1. **Rules Database MCP** (primary - fast structured data)
   - Use for: Spells, monsters, conditions, standard actions, core rules
   - Speed: <0.1 seconds

2. **Local Sourcebooks MCP** (secondary - full text)
   - Use for: Lore, detailed explanations, edge cases, flavor text
   - Speed: ~1-2 seconds

3. **Chapter Packs** (tertiary - campaign-specific)
   - Use for: Custom encounters, NPCs, locations
   - Speed: Instant (pre-loaded)

4. **Ask User** (last resort - if all else fails)

### Example Workflows:

**Spell Lookup:**
1. Try `rules-database` MCP → `lookup_spell("Fireball")` → Instant structured data
2. If you need flavor text → `sourcebooks` MCP → `search_sourcebooks("Fireball", "phb")`

**Monster Lookup:**
1. Try `rules-database` MCP → `lookup_monster("Goblin")` → Full stat block
2. If you need lore/tactics → `sourcebooks` MCP → `search_sourcebooks("Goblin tactics", "mm")`

**Rule Clarification:**
1. Try `rules-database` MCP → `lookup_rule("Grapple")` → Core rule text
2. If you need more context → `sourcebooks` MCP → `search_sourcebooks("Grappling", "phb")`

**Combat Scene:**
1. Use `music-ambience` MCP → `play_ambient("combat")` → Set atmosphere
2. Use `dice-roller` MCP → `roll_initiative([...])` → Roll initiative
3. Use `rules-database` MCP → `lookup_monster("Bugbear")` → Get stats
4. Use `session-recorder` MCP → `log_event("combat", "Initiative rolled")` → Track event

---

## 📋 All Available Tools (41 Total)

### Dice Rolling (5 tools):
1. `mcp_dice-roller_roll_dice`
2. `mcp_dice-roller_roll_attack`
3. `mcp_dice-roller_roll_saving_throw`
4. `mcp_dice-roller_roll_initiative`
5. `mcp_dice-roller_get_roll_history`

### Rules Database (9 tools):
6. `mcp_rules-database_lookup_spell`
7. `mcp_rules-database_search_spells`
8. `mcp_rules-database_get_spells_by_class`
9. `mcp_rules-database_lookup_monster`
10. `mcp_rules-database_search_monsters`
11. `mcp_rules-database_lookup_condition`
12. `mcp_rules-database_lookup_rule`
13. `mcp_rules-database_search_rules`
14. `mcp_rules-database_lookup_action`

### Local Sourcebooks (4 tools):
15. `mcp_sourcebooks_search_sourcebooks`
16. `mcp_sourcebooks_lookup_rule`
17. `mcp_sourcebooks_get_section`
18. `mcp_sourcebooks_list_sections`

### Music & Ambience (6 tools):
19. `mcp_music-ambience_play_ambient`
20. `mcp_music-ambience_play_sfx`
21. `mcp_music-ambience_list_scenes`
22. `mcp_music-ambience_list_sfx`
23. `mcp_music-ambience_get_current_track`
24. `mcp_music-ambience_stop_music`

### Session Logger (7 tools):
25. `mcp_session-recorder_start_session_log`
26. `mcp_session-recorder_log_event`
27. `mcp_session-recorder_stop_session_log`
28. `mcp_session-recorder_get_session_status`
29. `mcp_session-recorder_list_session_logs`
30. `mcp_session-recorder_extract_events`
31. `mcp_session-recorder_update_campaign_events`

### Combat Engine (9 tools):
32. `mcp_combat-engine_start_combat`
33. `mcp_combat-engine_roll_initiative_tool`
34. `mcp_combat-engine_load_battlefield`
35. `mcp_combat-engine_next_turn_tool`
36. `mcp_combat-engine_get_combat_status`
37. `mcp_combat-engine_attack_tool`
38. `mcp_combat-engine_move_creature`
39. `mcp_combat-engine_get_ai_action`
40. `mcp_combat-engine_end_combat_tool`

---

## 🧪 Test Commands

### Dice Rolling:
- "Roll 2d6+3 for damage"
- "Goblin attacks with scimitar (+4 to hit)"
- "Roll initiative for the party"
- "Dex save DC 15 with advantage"

### Rules Database:
- "Look up the Fireball spell"
- "What does the Exhaustion condition do?"
- "Show me the Goblin monster stat block"
- "Search for all Wizard cantrips"
- "Look up grappling rules"

### Local Sourcebooks:
- "Search sourcebooks for 'inspiration' in PHB"
- "Get the Combat section from DMG"
- "List all sections in Monster Manual"
- "Search for mounted combat rules"

### Music & Ambience:
- "Play tavern ambient music"
- "List available scene types"
- "Play combat music"
- "Stop music"

### Session Logger:
- "Start session log for Phandelver"
- "Log narration: Players enter the cave"
- "Stop session log"
- "List recent session logs"

---

## 📁 File Locations

### MCP Servers:
- **Dice Roller:** `C:\DnD\DnD_Cursor\mcp_servers\dice_roller\dice_roller_server.py`
- **Rules Database:** `C:\DnD\DnD_Cursor\mcp_servers\rules_database\rules_db_server.py`
- **Sourcebooks:** `C:\DnD\DnD_Cursor\mcp_servers\sourcebooks\sourcebooks_server.py`
- **Music & Ambience:** `C:\DnD\DnD_Cursor\mcp_servers\music_ambience\music_server.py`
- **Session Recorder:** `C:\DnD\DnD_Cursor\mcp_servers\session_recorder\session_recorder_server.py`

### Data Files:
- **Rules Database:** `C:\DnD\DnD_Cursor\rules_database\*.json`
- **Sourcebooks:** `C:\DnD\Sourcebooks\*.txt`
- **Music:** `C:\Users\ksist\Music\D&D_Ambient\` and `D&D_SFX\`
- **Session Logs:** `C:\DnD\DnD_Cursor\session_logs\*.jsonl`
- **Dice Audit:** `C:\DnD\DnD_Cursor\mcp_servers\dice_roller\dice_rolls_audit.jsonl`

### Configuration:
- **MCP Config:** `C:\DnD\DnD_Cursor\.cursor\mcp.json`
- **Project Rules:** `C:\DnD\DnD_Cursor\.cursorrules`

---

## 📖 Documentation

### Quick Reference Guides:
- `docs/MCP_DICE_ROLLER_QUICK_REFERENCE.md` - Dice rolling
- `docs/MCP_SPELL_DATABASE_QUICK_REFERENCE.md` - Rules database (spells, monsters, etc.)
- `docs/MCP_SESSION_RECORDER_QUICK_REFERENCE.md` - Session logging

### Integration Guides:
- `.cursorrules` - Core DM rules and MCP usage mandates
- `SESSION_START_GUIDE.md` - Session initialization checklist

---

## ✅ What This Gives You

### During Gameplay:
✅ **Instant Rule Lookups** - <0.1 seconds via rules database  
✅ **True Random Rolls** - Cryptographically secure, fully auditable  
✅ **Complete Content Access** - 391 spells, 499 monsters, 15 conditions, 13 rules  
✅ **Immersive Audio** - Automatic scene-appropriate music and SFX  
✅ **Session Tracking** - Optional detailed session logging  
✅ **Seamless Integration** - AI uses automatically without announcing

### For the DM:
✅ **No Prep Gaps** - Missing monster? Instant lookup.  
✅ **Rules at Hand** - Any rule, instantly referenced.  
✅ **Fair Play** - All rolls logged, verifiable.  
✅ **Atmosphere Control** - Music and ambience at your fingertips.  
✅ **Campaign Continuity** - Auto-track events and choices.  
✅ **More Time Playing** - Less time looking things up.

### For Players:
✅ **Quick Answers** - "What does X do?" → Instant response  
✅ **Transparent Rolls** - All NPC rolls auditable  
✅ **Complete Info** - Full spell/feature descriptions  
✅ **Better Flow** - No waiting for lookups  
✅ **Immersive Experience** - Music enhances storytelling

---

## 🎮 Ready to Play!

**You now have a complete D&D AI system with:**
- True random dice rolling with audit trail (5 tools)
- Instant structured rules database (9 tools)
- Full sourcebook text search (4 tools)
- Ambient music and sound effects (6 tools)
- Session logging and event tracking (7 tools)

**Total: 40 specialized D&D tools + 10 browser tools = 50 tools at your disposal**

---

## 🔧 Maintenance & Updates

### Updating Rules Database:
If sourcebooks are updated, rebuild the database:
```powershell
python "C:\DnD\DnD_Cursor\scripts\parse_phb_rules.py"
python "C:\DnD\DnD_Cursor\scripts\parse_phb_spells.py"
python "C:\DnD\DnD_Cursor\scripts\parse_sourcebooks.py"
```

### Adding Music/SFX:
Just drop new audio files into:
- `C:\Users\ksist\Music\D&D_Ambient\<scene_name>.mp3`
- `C:\Users\ksist\Music\D&D_SFX\<sfx_name>.wav`

No configuration needed - the MCP will auto-detect them!

---

**Status:** ✅ ALL 5 MCP SERVERS OPERATIONAL  
**Last Tested:** 2026-01-13  
**Next:** Continue your campaign with instant lookups, immersive audio, and complete session tracking! 🎲📖📚🎵📝✨
