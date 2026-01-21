# 🤖 MECHANICS AUTOMATION CHECKLIST
**MANDATORY REFERENCE - READ AT SESSION START**

**⚠️ ENFORCEMENT:** This checklist is enforced by the Unified DM Workflow System. You CANNOT skip it.

**Unified Workflow System:**
- **AUTOMATIC:** Run `python scripts/dm_workflow.py session_start` at session start (automatic trigger)
- **AUTOMATIC:** Workflow handles ALL initialization steps (validation, state loading, chapter packs, MCP verification)
- **AUTOMATIC:** Post-combat workflow BLOCKS until ALL procedures complete
- **AUTOMATIC:** Spell cast workflow IMMEDIATELY deducts spell slots
- **AUTOMATIC:** Travel workflow BLOCKS until ALL travel procedures complete
- Session is BLOCKED if workflow fails

**Pre-Session Validation:**
- Run `python scripts/pre_session_check.py` before every session (or use workflow)
- Validation token expires after 24 hours (forces re-check)
- Session is BLOCKED if validation fails

**Context Reminders:**
- Run `python scripts/mechanics_reminder.py <context>` before critical operations
- Contexts: pre_combat, post_combat, npc_status_change, npc_faction_interaction, quest_completion, spell_cast, inventory_change, travel_start
- **OR** use `python scripts/dm_workflow.py <workflow>` for automated workflows

**See `docs/DM_WORKFLOW_SYSTEM.md` for complete workflow documentation.**

This checklist ensures ALL mechanics are followed automatically. **DO NOT SKIP ANY ITEM.**

---

## 📋 SESSION START (MANDATORY)

### ✅ Pre-Session Checklist
- [ ] Read `CURRENT_STATE.json` (current location, combat status, discoveries)
- [ ] Read `CAMPAIGN_EVENTS.json` (past choices, consequences, NPC relationships)
- [ ] Load campaign wiki: `create_or_load_wiki(campaign_name="Phandelver")`
- [ ] Verify MCP servers are available (rules-database, dice-roller, obsidian-sync, combat-engine, campaign-wiki)

---

## ⚔️ COMBAT PROCEDURES (MANDATORY)

### ✅ During Combat
- [ ] **HP Changes:** After ANY HP change → `update_character_hp(character_name, new_hp, max_hp)` to Obsidian
- [ ] **Spell Slots:** After ANY spell cast OR spell slot use → **IMMEDIATELY** call `mcp_obsidian-sync_use_spell_slot(character_name, spell_level)` → NEVER manually edit files
- [ ] **Resources:** After ANY resource use (Rage, Ki, etc.) → `use_resource(creature_id, resource_name, amount)` to Obsidian
- [ ] **Conditions:** After applying/removing conditions → `add_condition()` or `remove_condition()` to Obsidian
- [ ] **Healing:** After ANY healing → `apply_healing(creature_id, healing_amount)` to Obsidian

### ✅ Post-Combat (MANDATORY - Execute ALL Steps)
- [ ] **Step 1:** Call `end_combat_tool(combat_id)` to get combat summary
- [ ] **Step 2:** Calculate XP from defeated enemies (use `lookup_monster()` for CR/XP)
- [ ] **Step 3:** Divide XP evenly among participating PCs
- [ ] **Step 4:** Call `update_character_xp(character_name, xp_amount)` for EACH PC
- [ ] **Step 5:** Roll currency loot (use `roll_dice()` for random loot)
- [ ] **Step 6:** Divide currency evenly among PCs (handle remainders)
- [ ] **Step 7:** Call `update_character_currency(character_name, {gp, sp, cp})` for EACH PC
- [ ] **Step 8:** List item loot (with quantity + weight for each item)
- [ ] **Step 9:** ASK players what items they want to take
- [ ] **Step 10:** Call `add_inventory_item(character_name, item_name, quantity, weight)` for chosen items
- [ ] **Step 11:** Show post-combat summary (XP, currency, items, party status)
- [ ] **Step 12:** Ask "What do you do next?"

**CRITICAL:** Never skip post-combat procedures. They are MANDATORY after EVERY combat.

---

## 🎭 NPC MANAGEMENT (MANDATORY)

### ✅ When NPC Status Changes
- [ ] **NPC Dies/Executed:** Call `update_npc(campaign_name, npc_name, alive=false, status="executed")` → Auto-syncs to Obsidian
- [ ] **NPC Location Changes:** Call `update_npc(campaign_name, npc_name, location="new_location")` → Auto-syncs to Obsidian
- [ ] **NPC Relationship Changes:** Call `add_relationship(campaign_name, from_entity, to_entity, relationship_type)` → Auto-syncs to Obsidian
- [ ] **NPC Created:** Call `create_npc(campaign_name, name, role, description)` → Auto-syncs to Obsidian

**CRITICAL:** NPC updates automatically sync to Obsidian. No manual file editing needed.

---

## 📜 QUEST MANAGEMENT (MANDATORY)

### ✅ When Quest Status Changes
- [ ] **Quest Accepted:** Call `update_quest_status(campaign_name, quest_id, status="accepted")` → Auto-sets date_accepted
- [ ] **Quest Completed:** Call `complete_quest(campaign_name, quest_id, party_members)` → Auto-distributes:
  - Gold (evenly divided)
  - XP (evenly divided)
  - Items (lists for players to choose)
  - Faction reputation (+5 to quest giver's faction, plus reward_reputation)
- [ ] **Quest Created:** Call `create_quest(campaign_name, name, description, quest_type, reward_gold, reward_xp, reward_items, reward_reputation, quest_giver)`

**CRITICAL:** Quest completion automatically distributes rewards. No manual calculation needed.

---

## 🏰 FACTION MANAGEMENT (MANDATORY)

### ✅ When Helping or Angering NPCs with Faction Affiliations
- [ ] **NPC Faction Interaction:** When helping or angering NPCs:
  - **AUTOMATICALLY** run: `python scripts/dm_workflow.py npc_faction_interaction --npc <name> --action-type <helped|angered>`
  - Check if NPC has a faction (via `get_npc_data` or campaign wiki)
  - Determine reputation change:
    * Helping NPC: +5 to +25 reputation (based on significance)
    * Angering NPC: -5 to -25 reputation (based on severity)
  - **IMMEDIATELY** call: `mcp_campaign-wiki_update_faction_reputation(campaign_name, faction_id, "Party", amount)`
  - Auto-syncs to Obsidian (no manual steps needed)

### ✅ When Faction Reputation Changes (Manual)
- [ ] **Reputation Change:** Call `update_faction_reputation(campaign_name, faction_id, character_name, amount)` → Auto-syncs to Obsidian
- [ ] **Rank Change:** Call `update_faction_rank(campaign_name, faction_id, character_name, new_rank)` → Auto-syncs to Obsidian
- [ ] **Faction Created:** Call `create_faction(campaign_name, name, faction_type, description)` → Auto-syncs to Obsidian

**CRITICAL:** Faction updates automatically sync to Obsidian. No manual file editing needed.

---

## 📦 INVENTORY MANAGEMENT (MANDATORY)

### ✅ When Items Change
- [ ] **Item Added:** Call `add_inventory_item(character_name, item_name, quantity, weight)` → Updates Obsidian table
- [ ] **Item Removed:** Call `remove_inventory_item(character_name, item_name, quantity)` → Updates Obsidian table
- [ ] **Weapon Added:** Call `add_weapon(character_name, weapon_name, attack_bonus, damage, properties)` → Updates Obsidian table
- [ ] **Armor Added:** Call `add_armor(character_name, armor_name, ac_bonus, armor_type, properties)` → Updates Obsidian table
- [ ] **Magic Item Added:** Call `add_magic_item(character_name, item_name, properties, charges, attuned)` → Updates Obsidian table

**CRITICAL:** Always include quantity and weight for items. Obsidian tables update automatically.

---

## 🎲 DICE ROLLS (MANDATORY)

### ✅ When to Use Dice Roller MCP
- [ ] **NPC/System Rolls:** ALWAYS use `roll_dice(dice_expression, reason, character)` for NPC rolls
- [ ] **Attack Rolls:** Use `roll_attack(modifier, character, weapon, advantage, disadvantage, target_ac)` for NPC attacks
- [ ] **Saving Throws:** Use `roll_saving_throw(modifier, dc, ability, character, advantage, disadvantage)` for NPC saves
- [ ] **Initiative:** Use `roll_initiative(combatants)` for combat initiative
- [ ] **Player Rolls:** Wait for player to roll, then use result (don't roll for players)

**CRITICAL:** Never guess dice results. Use MCP dice-roller for all NPC/system rolls.

---

## 📚 RULES/SPELLS/MONSTERS (MANDATORY)

### ✅ When You Need D&D Mechanics
- [ ] **Spell Info:** Use `lookup_spell(spell_name)` or `search_spells(query)` → NEVER guess spell effects
- [ ] **Monster Stats:** Use `lookup_monster(monster_name)` or `search_monsters(query)` → NEVER guess monster stats
- [ ] **Condition Effects:** Use `lookup_condition(condition_name)` → NEVER guess condition effects
- [ ] **Rule Clarification:** Use `lookup_rule(rule_name)` or `search_rules(query)` → NEVER guess rules
- [ ] **Action Description:** Use `lookup_action(action_name)` → NEVER guess action mechanics
- [ ] **Sourcebook Text:** Use `search_sourcebooks(query, sourcebook)` for full text

**CRITICAL:** If MCP returns "not found" → BLOCK. Do not proceed with guesses.

---

## 💾 REAL-TIME OBSIDIAN SYNC (MANDATORY)

### ✅ When to Sync to Obsidian
- [ ] **HP Changes:** After EVERY HP change (combat, healing, damage)
- [ ] **XP Changes:** After EVERY XP gain (combat, quest completion, non-combat encounters)
- [ ] **Currency Changes:** After EVERY currency gain/loss (loot, purchases, quest rewards)
- [ ] **Spell Slots:** After EVERY spell cast OR spell slot use → **IMMEDIATELY** call `mcp_obsidian-sync_use_spell_slot(character_name, spell_level)` → NEVER manually edit files
- [ ] **Resources:** After EVERY resource use (Rage, Ki, Channel Divinity, etc.)
- [ ] **Conditions:** After applying/removing ANY condition
- [ ] **Inventory:** After adding/removing ANY item
- [ ] **NPC Status:** After ANY NPC status change (automatic via `update_npc`)
- [ ] **Quest Status:** After ANY quest status change (automatic via quest tools)
- [ ] **Faction Reputation:** After ANY reputation change (automatic via faction tools)

**CRITICAL:** Obsidian sync is REAL-TIME. Players see updates immediately. Never skip sync.

---

## 🚶 TRAVEL PROCEDURES (MANDATORY)

### ✅ When Travel Begins
- [ ] **Check Character Rations:** Verify each character has sufficient rations (1 per person per day)
- [ ] **Check Party Wagon:** If insufficient rations, check Party Wagon inventory
- [ ] **Transfer Rations:** If needed, transfer rations from wagon to characters using:
  - `add_inventory_item(character_name, "Rations", quantity, weight)` for each character
  - `remove_inventory_item("Party_Wagon", "Rations", quantity)` from wagon
- [ ] **Call process_travel:** `mcp_travel-manager_process_travel(party_members, days, travel_type)` - Deducts rations automatically
- [ ] **Random Encounters:** For each day of travel:
  - Check for day encounter: `check_random_encounter(biome, terrain, "day")` (1d20, 17-20 triggers)
  - Check for night encounter: `check_random_encounter(biome, terrain, "night")` (1d20, 17-20 triggers)
  - If encounter occurs, run the encounter before continuing travel
- [ ] **Update State:** Update CURRENT_STATE.json with new location after travel completes
- [ ] **Long Rests:** After each full day of travel:
  - Restore all HP to max
  - Restore all spell slots to max
  - Restore all resources (Rage, Ki, etc.) to max
  - Update character sheets via Obsidian sync

**CRITICAL:** Travel workflow automatically triggers when travel begins. Cannot skip travel procedures.

---

## 📝 CAMPAIGN EVENTS EXPORT (AUTOMATIC)

### ✅ When to Export Campaign Events
- [ ] **Quest Completed:** After `complete_quest()` is called
- [ ] **Major Story Event:** After significant events are added to CAMPAIGN_EVENTS.json
- [ ] **Session End:** Optional - export at end of session to sync Obsidian
- [ ] **Manual Export:** Run `python scripts/dm_workflow.py export_campaign_events` anytime

**AUTOMATIC TRIGGER:**
- **AUTOMATICALLY** run: `python scripts/dm_workflow.py export_campaign_events` after quest completion or major events
- Exports to Obsidian:
  * `Campaign_Events/` folder (all events with dates, participants, outcomes, rewards)
  * `Consequences/` folder (active consequences tracker, grouped by status)
  * `Choices/` folder (player choices with alternatives and long-term impacts)
  * Index files for easy navigation
- **NON-BLOCKING** - Runs in background, doesn't block progression

**CRITICAL:** Campaign events export keeps Obsidian vault synchronized with campaign history. All events, consequences, and choices are searchable and cross-linked in Obsidian.

---

## 📦 PARTY PERSISTENT DATA EXPORT (AUTOMATIC)

### ✅ When to Export Persistent Data
- [ ] **Cross-Campaign Benefit Added:** After adding recurring income, boons, or permanent benefits to PARTY_PERSISTENT_DATA.json
- [ ] **Session End:** Optional - export at end of session to sync Obsidian
- [ ] **Manual Export:** Run `python scripts/dm_workflow.py export_persistent_data` anytime

**AUTOMATIC TRIGGER:**
- **AUTOMATICALLY** run: `python scripts/dm_workflow.py export_persistent_data` when PARTY_PERSISTENT_DATA.json is updated
- Exports to Obsidian:
  * `Recurring_Income/` folder (cross-campaign income sources like mine profit shares)
  * `Boons/` folder (permanent boons that persist across campaigns)
  * `Permanent_Benefits/` folder (titles, memberships, faction ranks)
  * `Cross_Campaign_Relationships/` folder (NPCs/contacts that carry over)
- **NON-BLOCKING** - Runs in background, doesn't block progression

**CRITICAL:** Persistent data export keeps Obsidian vault synchronized with cross-campaign benefits. All recurring income, boons, and permanent benefits are searchable and tracked in Obsidian.

---

## 📝 SESSION LOGGING (OPTIONAL BUT RECOMMENDED)

### ✅ When to Log Events
- [ ] **Session Start:** Call `start_session_log(campaign_name, session_title)` at session start
- [ ] **Significant Events:** Call `log_event(event_type, content, metadata)` for:
  - Major story events (`narration`)
  - Player choices (`choice`)
  - Important rolls (`roll`)
  - Combat encounters (`combat`)
  - NPC interactions (`npc_interaction`)
  - Discoveries (`discovery`)
  - Gates passed (`gate`)
  - Consequences (`consequence`)
- [ ] **Session End:** Call `stop_session_log()` at session end

**Note:** Session logging is optional but helps maintain campaign continuity.

---

## 🎯 COMMON MISTAKES TO AVOID

### ❌ DON'T:
- ❌ Forget post-combat XP/currency/item distribution
- ❌ Skip Obsidian sync after HP/XP/inventory changes
- ❌ Guess spell/monster/condition effects (use MCP)
- ❌ Roll dice for players (wait for their rolls)
- ❌ Forget to update NPC status when they die/change
- ❌ Skip quest reward distribution (use `complete_quest`)
- ❌ Add items without quantity/weight
- ❌ Forget to show XP progress (current XP / next level XP)
- ❌ Skip faction reputation updates
- ❌ Manually edit Obsidian files (use MCP tools)

### ✅ DO:
- ✅ Use MCP tools for ALL mechanics
- ✅ Sync to Obsidian after EVERY change
- ✅ Follow post-combat checklist after EVERY combat
- ✅ Update NPC status automatically when it changes
- ✅ Use quest tools for reward distribution
- ✅ Always include quantity/weight for items
- ✅ Show XP progress in narration
- ✅ Use dice-roller MCP for NPC rolls
- ✅ Wait for player rolls before resolving

---

## 🔄 QUICK REFERENCE WORKFLOWS

### Post-Combat Workflow
```
1. end_combat_tool(combat_id)
2. Calculate XP → update_character_xp() for each PC
3. Roll currency → update_character_currency() for each PC
4. List items → ask players → add_inventory_item() for chosen items
5. Narrate summary → ask "What next?"
```

### NPC Death Workflow
```
1. update_npc(campaign_name, npc_name, alive=false, status="executed")
2. Auto-syncs to Obsidian (no manual steps needed)
```

### Quest Completion Workflow
```
1. complete_quest(campaign_name, quest_id, party_members)
2. Auto-distributes gold, XP, items, reputation
3. Auto-syncs to Obsidian
```

### Spell Casting Workflow (MANDATORY)
```
1. Player casts spell OR spell slot used for non-spell purpose (e.g., recharging crystal)
2. **IMMEDIATELY** call `mcp_obsidian-sync_use_spell_slot(character_name, spell_level)` → Auto-deducts and syncs to Obsidian
3. Resolve spell effect
4. Sync HP/conditions if changed

**CRITICAL:** NEVER manually edit spell slots in Obsidian files. ALWAYS use the MCP tool.
**CRITICAL:** This applies to ANY spell slot use, even if not casting a spell (e.g., recharging magic items).
```

---

## 📖 REFERENCE DOCUMENTS

When in doubt, read these:
- `USER_RULE_POST_COMBAT_PROCEDURES.md` - Complete post-combat workflow
- `AGENT_BOOTUP_SEQUENCE.md` - Complete MCP tool guide
- `SESSION_START_GUIDE.md` - Session initialization
- `docs/COMPLETE_MCP_TOOL_USAGE_GUIDE.md` - All 72 MCP tools
- `.cursorrules` - Core principles

---

## ✅ VALIDATION CHECKLIST

Before ending a session, verify:
- [ ] All combat encounters had post-combat procedures executed
- [ ] All HP/XP/inventory changes synced to Obsidian
- [ ] All NPC status changes updated via `update_npc`
- [ ] All quest completions used `complete_quest` tool
- [ ] All faction reputation changes synced
- [ ] All spell slots/resources deducted and synced
- [ ] All conditions applied/removed and synced
- [ ] All dice rolls used MCP dice-roller (for NPCs)
- [ ] All rules/spells/monsters looked up via MCP (no guesses)

---

**REMEMBER:** This checklist is MANDATORY. Follow it for EVERY session to ensure nothing is forgotten.

**Last Updated:** 2026-01-14
