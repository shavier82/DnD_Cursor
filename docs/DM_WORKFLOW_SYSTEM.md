# Unified DM Workflow System

**Complete documentation for the automated workflow orchestrator that prevents forgetting critical DM steps.**

---

## Overview

The Unified DM Workflow System is a master orchestrator that automates and enforces all critical DM operations. It prevents the AI DM from forgetting essential steps like post-combat procedures, spell slot deduction, chapter pack loading, and more.

### Key Features

- **Automatic Execution** - Workflows run automatically at key moments
- **Blocking Enforcement** - Cannot proceed until required steps complete
- **State Tracking** - Tracks what's been done in the current session
- **Context Awareness** - Right reminders at the right time
- **Integration** - All systems work together seamlessly

---

## Architecture

### Core Components

1. **Master Workflow Script** (`scripts/dm_workflow.py`)
   - Single entry point for all DM operations
   - Orchestrates all sub-processes
   - Tracks completion state
   - Blocks progression until requirements met

2. **Workflow State Tracker** (`.dm_workflow_state.json`)
   - Tracks what's been completed in current session
   - Validates prerequisites before operations
   - Prevents duplicate work

3. **Automatic Triggers**
   - Integrated into `.cursorrules`
   - Cannot be bypassed
   - Run automatically at key moments

---

## Available Workflows

### 1. Session Start Workflow

**Trigger:** Automatically when user says "Continue campaign", "Start session", or similar

**Command:**
```bash
python scripts/dm_workflow.py session_start
```

**What It Does:**
1. ✅ Validates checklist (pre_session_check.py)
2. ✅ Reads MECHANICS_AUTOMATION_CHECKLIST.md
3. ✅ Loads CURRENT_STATE.json
4. ✅ Loads CAMPAIGN_EVENTS.json
5. ✅ Determines current chapter from state
6. ✅ Loads chapter_pack_<n>.json automatically
7. ✅ Verifies MCP servers
8. ✅ Creates workflow state tracker

**Output:**
```json
{
  "status": "ready",
  "chapter": 6,
  "chapter_pack_loaded": true,
  "mcp_servers_verified": true,
  "state_loaded": true,
  "workflow_state": {...}
}
```

**Blocking:** Yes - Cannot proceed until workflow completes

---

### 2. Pre-Combat Workflow

**Trigger:** Automatically when combat is about to start

**Command:**
```bash
python scripts/dm_workflow.py pre_combat
```

**What It Does:**
1. ✅ Shows pre-combat reminder
2. ✅ Validates combat readiness
3. ✅ Checks prerequisites

**Output:**
- Shows reminder output
- Validates readiness

**Blocking:** No - Advisory only

---

### 3. Post-Combat Workflow

**Trigger:** Automatically when combat ends (end_combat_tool called or combat state cleared)

**Command:**
```bash
python scripts/dm_workflow.py post_combat --combat-id <id>
```

**What It Does:**
1. ✅ Shows post-combat reminder
2. ✅ Reminds to execute ALL post-combat procedures:
   - end_combat_tool(combat_id)
   - Calculate XP from defeated enemies
   - update_character_xp() for EACH PC
   - Roll currency loot
   - update_character_currency() for EACH PC
   - List item loot (with quantity + weight)
   - ASK players what items to take
   - add_inventory_item() for chosen items
   - Show post-combat summary
   - Ask "What do you do next?"

**Output:**
```json
{
  "status": "pending",
  "combat_id": "...",
  "message": "Post-combat procedures must be completed manually via MCP tools"
}
```

**Blocking:** Yes - **BLOCKS** progression until ALL procedures complete

---

### 4. Spell Cast Workflow

**Trigger:** Automatically when spell is cast or spell slot used

**Command:**
```bash
python scripts/dm_workflow.py spell_cast --character <name> --level <level>
```

**What It Does:**
1. ✅ Shows spell cast reminder
2. ✅ **IMMEDIATELY** reminds to call use_spell_slot()
3. ✅ Logs in workflow state

**Output:**
```json
{
  "status": "pending",
  "character_name": "Zephyr",
  "spell_level": 3,
  "message": "⚠️  MUST call use_spell_slot('Zephyr', 3) IMMEDIATELY"
}
```

**Blocking:** Yes - Cannot proceed without calling use_spell_slot()

---

### 5. NPC Status Change Workflow

**Trigger:** Automatically when NPC dies/changes

**Command:**
```bash
python scripts/dm_workflow.py npc_status_change --npc <name> --change-type <type>
```

**What It Does:**
1. ✅ Shows NPC status reminder
2. ✅ Reminds to call update_npc() tool
3. ✅ Logs in workflow state

**Output:**
```json
{
  "status": "pending",
  "npc_name": "Vrek",
  "change_type": "executed",
  "message": "⚠️  MUST call update_npc() for 'Vrek' with change type 'executed'"
}
```

**Blocking:** No - Advisory only

---

### 6. NPC Faction Interaction Workflow

**Trigger:** Automatically when helping or angering NPCs with faction affiliations

**Command:**
```bash
python scripts/dm_workflow.py npc_faction_interaction --npc <name> --action-type <helped|angered> [--reputation-change <amount>]
```

**What It Does:**
1. ✅ Shows faction reputation reminder
2. ✅ Reminds to check if NPC has a faction
3. ✅ Reminds to call update_faction_reputation() tool
4. ✅ Provides default reputation change guidance (+5 to +25 for helping, -5 to -25 for angering)
5. ✅ Logs in workflow state

**Output:**
```json
{
  "status": "pending",
  "npc_name": "Sildar Hallwinter",
  "action_type": "helped",
  "reputation_change": 15,
  "message": "⚠️  Check if 'Sildar Hallwinter' has a faction and update reputation accordingly"
}
```

**Blocking:** Yes - **BLOCKS** progression until faction reputation is updated

**Required MCP Tool Calls:**
1. Check if NPC has faction (via `get_npc_data` or campaign wiki)
2. If NPC has faction: `mcp_campaign-wiki_update_faction_reputation(campaign_name, faction_id, "Party", amount)`
3. Auto-syncs to Obsidian

---

### 7. Travel Start Workflow

**Trigger:** Automatically when travel begins (user says "We travel to...", "Head to...", etc.)

**Command:**
```bash
python scripts/dm_workflow.py travel_start --party-members <list> --days <n> --travel-type <type> [--destination <location>] [--biome <biome>] [--terrain <terrain>]
```

**What It Does:**
1. ✅ Shows travel reminder
2. ✅ Reminds to check character rations
3. ✅ Reminds to check Party Wagon if needed
4. ✅ Reminds to call process_travel() MCP tool
5. ✅ Reminds to check for random encounters (per day/night)
6. ✅ Reminds to update CURRENT_STATE.json with new location
7. ✅ Reminds to handle long rests after travel days
8. ✅ Logs in workflow state

**Output:**
```json
{
  "status": "pending",
  "party_members": ["Torgga_Brawnanvil", "Eglath_Bearkiller"],
  "days": 2,
  "travel_type": "overland",
  "destination": "Talhundereth",
  "biome": "plains",
  "terrain": "overland",
  "message": "⚠️  TRAVEL PROCEDURES REQUIRED:"
}
```

**Blocking:** Yes - **BLOCKS** progression until ALL travel procedures complete

**Required MCP Tool Calls:**
1. Check rations (read character files)
2. If needed: Transfer from wagon (add_inventory_item/remove_inventory_item)
3. `mcp_travel-manager_process_travel(party_members, days, travel_type)` - Deducts rations
4. For each day: `mcp_travel-manager_check_random_encounter(biome, terrain, time_of_day)`
5. Update CURRENT_STATE.json with new location
6. After long rest: Restore HP/spell slots/resources via Obsidian sync

---

### 8. Campaign Events Export Workflow

**Trigger:** Automatically when:
- Quest is completed
- Major story event occurs
- At session end (optional)
- Manually when needed

**Command:**
```bash
python scripts/dm_workflow.py export_campaign_events
```

**What It Does:**
1. ✅ Reads CAMPAIGN_EVENTS.json
2. ✅ Exports all events to Obsidian/Campaign_Events/ folder (individual files with dates)
3. ✅ Exports all consequences to Obsidian/Consequences/ folder (grouped by status)
4. ✅ Exports all choices to Obsidian/Choices/ folder (with alternatives and impacts)
5. ✅ Creates index files for easy navigation
6. ✅ Links participants, NPCs, locations, and quests

**Output:**
```json
{
  "status": "success",
  "exported": true,
  "message": "Campaign events exported to Obsidian successfully"
}
```

**Blocking:** No - Runs in background, doesn't block progression

**Obsidian Structure Created:**
- `Campaign_Events/` - Individual event files with frontmatter metadata
- `Consequences/` - Active consequences tracker (grouped by status)
- `Choices/` - Player choices log with alternatives and long-term impacts
- Index files for chronological browsing

**Integration:**
- Automatically triggered after quest completion
- Can be run manually anytime: `python scripts/dm_workflow.py export_campaign_events`
- Keeps Obsidian vault synchronized with campaign events
- All files include cross-links to NPCs, locations, and quests

---

### 9. Persistent Data Export Workflow

**Trigger:** Automatically when:
- PARTY_PERSISTENT_DATA.json is updated
- Cross-campaign benefits are added
- At session end (optional)
- Manually when needed

**Command:**
```bash
python scripts/dm_workflow.py export_persistent_data
```

**What It Does:**
1. ✅ Reads PARTY_PERSISTENT_DATA.json
2. ✅ Exports all recurring income to Obsidian/Party_Persistent_Data/Recurring_Income/ folder
3. ✅ Exports all boons to Obsidian/Party_Persistent_Data/Boons/ folder
4. ✅ Exports all permanent benefits to Obsidian/Party_Persistent_Data/Permanent_Benefits/ folder
5. ✅ Exports all cross-campaign relationships to Obsidian/Party_Persistent_Data/Cross_Campaign_Relationships/ folder
6. ✅ Creates index files for easy navigation

**Output:**
```json
{
  "status": "success",
  "exported": true,
  "message": "Party persistent data exported to Obsidian successfully"
}
```

**Blocking:** No - Runs in background, doesn't block progression

**Obsidian Structure Created:**
- `Recurring_Income/` - Cross-campaign income sources (e.g., mine profit shares)
- `Boons/` - Permanent boons that persist across campaigns
- `Permanent_Benefits/` - Titles, memberships, faction ranks, etc.
- `Cross_Campaign_Relationships/` - NPCs/contacts that carry over to future campaigns
- Index file for easy navigation

**Integration:**
- Automatically triggered when PARTY_PERSISTENT_DATA.json is updated
- Can be run manually anytime: `python scripts/dm_workflow.py export_persistent_data`
- Keeps Obsidian vault synchronized with cross-campaign benefits
- All files include frontmatter metadata and cross-links

---

## Workflow State Tracker

The workflow state tracker (`.dm_workflow_state.json`) tracks:

- **Session Start:**
  - Completed (boolean)
  - Timestamp
  - Checklist validated
  - State files loaded
  - Chapter pack loaded
  - MCP servers verified

- **Last Combat:**
  - Combat ID
  - Post-combat completed
  - Timestamp

- **Travel:**
  - Party members
  - Days traveled
  - Travel type
  - Destination
  - Biome/terrain
  - Completed
  - Timestamp

- **Spell Slots Used:**
  - Character name
  - Spell level
  - Timestamp

- **NPC Status Changes:**
  - NPC name
  - Change type
  - Timestamp

- **Faction Reputation Changes:**
  - NPC name
  - Action type (helped/angered)
  - Reputation change amount
  - Timestamp

- **Quests Completed:**
  - Quest ID
  - Completion timestamp

---

## Integration with Existing Systems

### MCP Tools
- Workflow validates MCP servers before use
- Workflow enforces MCP lookups for rules/spells/monsters
- Workflow tracks MCP tool usage

### Chapter Packs
- Workflow automatically loads correct pack based on state
- Workflow verifies pack exists before loading
- Workflow caches loaded pack for session

### State Files
- Workflow validates state file integrity
- Workflow ensures state is read before session
- Workflow tracks state modifications

### Checklist System
- Workflow enforces checklist validation
- Workflow provides context reminders
- Workflow tracks checklist completion

---

## Automatic Triggers

The workflow system is integrated into `.cursorrules` with automatic triggers:

### Session Start Trigger
```
User: "Continue campaign"
↓
AI automatically runs: python scripts/dm_workflow.py session_start
↓
Workflow executes all steps
↓
AI proceeds with DM narration
```

### Post-Combat Trigger
```
Combat ends
↓
AI automatically runs: python scripts/dm_workflow.py post_combat --combat-id <id>
↓
Workflow shows reminder and BLOCKS until procedures complete
↓
AI shows summary and asks "What next?"
```

### Spell Cast Trigger
```
Player casts spell
↓
AI automatically runs: python scripts/dm_workflow.py spell_cast --character <name> --level <level>
↓
Workflow reminds to call use_spell_slot() IMMEDIATELY
↓
AI calls use_spell_slot() and proceeds
```

### NPC Faction Interaction Trigger
```
User: "We help [NPC name]" or "We anger [NPC name]"
↓
AI automatically runs: python scripts/dm_workflow.py npc_faction_interaction --npc <name> --action-type <helped|angered>
↓
Workflow shows reminder and BLOCKS until faction reputation updated
↓
AI IMMEDIATELY:
  1. Checks if NPC has faction (via get_npc_data or campaign wiki)
  2. Determines reputation change (+5 to +25 for helping, -5 to -25 for angering)
  3. Calls update_faction_reputation(campaign_name, faction_id, "Party", amount)
↓
AI proceeds with narration
```

### Travel Start Trigger
```
User: "We travel to [destination] for [X] days"
↓
AI automatically runs: python scripts/dm_workflow.py travel_start --party-members <list> --days <X> --travel-type <type>
↓
Workflow shows reminder and BLOCKS until procedures complete
↓
AI IMMEDIATELY calls:
  - Check rations (read character files)
  - If needed: Transfer from wagon
  - process_travel(party_members, days, travel_type)
  - For each day: check_random_encounter(biome, terrain, time_of_day)
  - Update CURRENT_STATE.json
↓
AI proceeds with travel narration
```

### Campaign Events Export Trigger
```
Quest completed OR major event occurs
↓
AI automatically runs: python scripts/dm_workflow.py export_campaign_events
↓
Workflow exports CAMPAIGN_EVENTS.json to Obsidian
↓
Creates/updates:
  - Campaign_Events/ folder (all events)
  - Consequences/ folder (active consequences)
  - Choices/ folder (player choices)
  - Index files for navigation
↓
AI proceeds (non-blocking)
```

---

## Error Handling

**If workflow fails at any step:**
1. Show clear error message
2. Block progression until fixed
3. Provide specific fix instructions
4. Log error to workflow state

**Common errors:**
- Checklist not validated → Run pre_session_check.py
- Chapter pack missing → Build pack or use fallback
- MCP server unavailable → Check MCP configuration
- State file corrupted → Restore from backup

---

## Usage Examples

### Session Start
```bash
# Automatic (integrated into .cursorrules):
User: "Continue campaign"
→ AI runs: python scripts/dm_workflow.py session_start
→ Workflow completes all steps
→ AI begins DMing
```

### Post-Combat
```bash
# Automatic (triggered when combat ends):
Combat ends
→ AI runs: python scripts/dm_workflow.py post_combat --combat-id <id>
→ Workflow executes ALL post-combat procedures
→ AI shows summary and asks "What next?"
```

### Spell Cast
```bash
# Automatic (triggered when spell cast):
Player casts spell
→ AI runs: python scripts/dm_workflow.py spell_cast --character Zephyr --level 3
→ Workflow reminds to call use_spell_slot()
→ AI calls use_spell_slot('Zephyr', 3) IMMEDIATELY
→ AI proceeds with spell resolution
```

### Manual Override
```bash
# If needed, user can run manually:
python scripts/dm_workflow.py session_start
python scripts/dm_workflow.py post_combat --combat-id <id>
python scripts/dm_workflow.py spell_cast --character Zephyr --level 3
python scripts/dm_workflow.py npc_status_change --npc Vrek --change-type executed
python scripts/dm_workflow.py npc_faction_interaction --npc Sildar_Hallwinter --action-type helped --reputation-change 15
python scripts/dm_workflow.py travel_start --party-members Torgga_Brawnanvil Eglath_Bearkiller --days 2 --travel-type overland --destination Talhundereth
```

---

## Benefits

1. **No More Forgetting** - Workflow enforces all steps
2. **Automatic Execution** - Runs without user intervention
3. **Blocking Enforcement** - Cannot proceed until complete
4. **State Tracking** - Knows what's been done
5. **Context Awareness** - Right reminders at right time
6. **Integration** - All systems work together
7. **Repeatable** - Same workflow every time
8. **Validated** - Checks prerequisites before operations

---

## Success Criteria

**System is successful if:**
- ✅ AI cannot start session without completing workflow
- ✅ Post-combat procedures ALWAYS execute (blocking)
- ✅ Spell slots ALWAYS deducted immediately
- ✅ Faction reputation ALWAYS updated when helping/angering NPCs (blocking)
- ✅ Travel procedures ALWAYS execute (blocking)
- ✅ Chapter packs ALWAYS loaded automatically
- ✅ MCP lookups ALWAYS used for rules/spells/monsters
- ✅ No manual reminders needed from user
- ✅ Workflow state tracks all operations
- ✅ Validation prevents skipping steps

---

## Future Enhancements

1. **Workflow Visualization** - Show progress in real-time
2. **Recovery Mode** - Resume interrupted workflows
3. **Workflow Templates** - Custom workflows for specific scenarios
4. **Analytics** - Track which steps are most often skipped
5. **Auto-Fix** - Automatically fix common errors
6. **Workflow History** - Log all workflow executions
7. **Multi-Campaign Support** - Workflow adapts to campaign type

---

## Reference

- **Master Script:** `scripts/dm_workflow.py`
- **Workflow State:** `.dm_workflow_state.json` (git-ignored)
- **Integration:** `.cursorrules` (automatic triggers)
- **Checklist:** `MECHANICS_AUTOMATION_CHECKLIST.md`
- **Session Guide:** `SESSION_START_GUIDE.md`

---

**Last Updated:** 2026-01-14  
**Status:** ✅ Implemented and Active
