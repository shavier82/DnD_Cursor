# Complete MCP Tool Usage Guide
**Every Tool, Every Use Case**

This document explains how I (the AI DM) will use **every single MCP tool** during gameplay sessions.

---

## 🎲 1. DICE-ROLLER MCP (5 Tools)

### **Tool 1: `mcp_dice-roller_roll_dice`**
**When I use it:**
- **Any dice roll that isn't an attack or saving throw**
- Damage rolls: "Roll 2d6+3 for greataxe damage"
- Skill checks: "Roll 1d20+5 for Perception"
- Ability checks: "Roll 1d20+2 for Strength Athletics"
- Random generation: "Roll 1d100 for random encounter"
- Healing rolls: "Roll 1d4+3 for Healing Word"
- Any custom dice expression: "Roll 4d8+2", "Roll 1d12", "Roll 3d6-1"

**Example usage:**
```
Player: "I attack with my greataxe"
Me: 
  1. Roll attack (using roll_attack tool)
  2. If hit: roll_dice("1d12+4", "Greataxe damage", "Eglath")
  3. Narrate: "The axe bites deep, dealing 9 slashing damage!"
```

**Parameters:**
- `dice_expression`: "2d6+3", "1d20", "4d8-2" (standard D&D notation)
- `reason`: Why the roll is happening ("Fireball damage", "Stealth check")
- `character`: Who is rolling (for audit trail)

---

### **Tool 2: `mcp_dice-roller_roll_attack`**
**When I use it:**
- **Every attack roll in the game** (PCs and NPCs)
- Melee attacks: "Eglath attacks with greataxe"
- Ranged attacks: "Goblin shoots shortbow"
- Spell attacks: "Zephyr casts Fire Bolt"
- Opportunity attacks: "Goblin makes opportunity attack"
- Any attack that needs to hit AC

**Example usage:**
```
Player: "I attack the goblin with my longsword"
Me:
  1. Get character stats: get_character_combat_stats("Torgga_Brawnanvil")
  2. roll_attack(modifier=6, character="Torgga", target_ac=15, weapon="Longsword")
  3. Result: "Hit! 18 vs AC 15"
  4. Then roll damage with roll_dice()
```

**Parameters:**
- `modifier`: Attack bonus (STR/DEX + proficiency + magic)
- `character`: Who is attacking
- `target_ac`: Target's AC (for hit/miss determination)
- `weapon`: Weapon name (optional, for flavor)
- `advantage`: True if advantage
- `disadvantage`: True if disadvantage

**Why this tool:**
- Automatically determines hit/miss
- Handles advantage/disadvantage
- Logs to audit trail
- Returns formatted result

---

### **Tool 3: `mcp_dice-roller_roll_saving_throw`**
**When I use it:**
- **Every saving throw in the game**
- Spell saves: "Dexterity save DC 15 vs Fireball"
- Condition saves: "Constitution save vs poison"
- Environmental hazards: "Strength save vs falling rocks"
- Trap saves: "Dexterity save vs pit trap"
- Monster abilities: "Wisdom save vs Frightful Presence"

**Example usage:**
```
Me: "The wizard casts Fireball! Everyone make a Dexterity save DC 15"
Me (internally):
  1. roll_saving_throw(modifier=2, dc=15, ability="Dexterity", character="Goblin 1")
  2. roll_saving_throw(modifier=3, dc=15, ability="Dexterity", character="Goblin 2")
  3. roll_saving_throw(modifier=5, dc=15, ability="Dexterity", character="Eglath")
  4. Apply half damage to those who saved, full to those who failed
```

**Parameters:**
- `modifier`: Save modifier (ability + proficiency if proficient)
- `dc`: Difficulty Class
- `ability`: "Dexterity", "Constitution", "Wisdom", etc.
- `character`: Who is making the save
- `advantage`: True if advantage
- `disadvantage`: True if disadvantage

---

### **Tool 4: `mcp_dice-roller_roll_initiative`**
**When I use it:**
- **At the start of every combat encounter**
- Before combat begins
- When surprise round ends and normal initiative begins
- When new creatures join combat mid-encounter

**Example usage:**
```
Me: "Roll for initiative!"
Me (internally):
  1. Get all combatant stats
  2. roll_initiative(combatants=[
      {"name": "Eglath", "modifier": 3},
      {"name": "Torgga", "modifier": -1},
      {"name": "Goblin 1", "modifier": 2},
      {"name": "Goblin 2", "modifier": 2}
    ])
  3. Returns sorted initiative order
  4. Narrate: "Eglath goes first (21), then Goblin 1 (18), then Torgga (12)..."
```

**Parameters:**
- `combatants`: Array of {name, modifier, advantage?}
- Automatically rolls d20 + modifier for each
- Returns sorted list (highest to lowest)

**Note:** Combat-engine also has `roll_initiative_tool` which does this automatically when starting combat.

---

### **Tool 5: `mcp_dice-roller_get_roll_history`**
**When I use it:**
- **When player questions a roll** ("Did I really roll that low?")
- **When reviewing recent actions** ("What did the goblin roll last turn?")
- **For audit purposes** (verify fairness)
- **When debugging** ("Let me check what rolls happened")

**Example usage:**
```
Player: "Wait, did I really roll a 3 on that attack?"
Me:
  1. get_roll_history(character="Eglath", limit=5)
  2. Check: "Yes, your last attack was a 3 (1d20+5 = 8 total)"
  3. Confirm or correct as needed
```

**Parameters:**
- `character`: Filter by character name (optional)
- `limit`: How many recent rolls to retrieve (default 10)

**Why this tool:**
- Full audit trail of all rolls
- Cryptographically secure (can't be faked)
- Builds player trust
- Useful for debugging

---

## 📖 2. RULES-DATABASE MCP (9 Tools)

### **Tool 6: `mcp_rules-database_lookup_spell`**
**When I use it:**
- **Every time a spell is cast** (PC or NPC)
- **When player asks "What does X spell do?"**
- **When checking spell range, components, or effects**
- **Before narrating spell effects**

**Example usage:**
```
Player: "I cast Fireball at the goblins"
Me:
  1. lookup_spell("Fireball")
  2. Get: Level 3, 150ft range, 20ft radius, 8d6 fire damage, Dex save DC 15
  3. Narrate: "You hurl a bead of fire that explodes in a 20-foot radius!"
  4. Roll saves for all targets in radius
  5. Apply damage
```

**What I get:**
- Spell level, school, casting time
- Range, components, duration
- Full description and effects
- Damage dice and save DC
- Upcasting information

**Why this tool:**
- Never guess spell details
- Accurate range/area calculations
- Correct damage dice
- Proper save types

---

### **Tool 7: `mcp_rules-database_search_spells`**
**When I use it:**
- **When player asks "What healing spells do I have?"**
- **When searching for spells by class/level**
- **When looking for spells with specific effects**
- **When building NPC spell lists**

**Example usage:**
```
Player: "What cleric spells can I cast at 3rd level?"
Me:
  1. search_spells(query="cleric", spell_class="Cleric", spell_level=3)
  2. Returns: ["Revivify", "Spirit Guardians", "Mass Healing Word", ...]
  3. List options for player
```

**Parameters:**
- `query`: Search term (spell name, keyword)
- `spell_class`: Filter by class (optional)
- `spell_level`: Filter by level (optional)
- `school`: Filter by school (optional)
- `max_results`: Limit results (default 10)

---

### **Tool 8: `mcp_rules-database_get_spells_by_class`**
**When I use it:**
- **When player levels up** (show new spells available)
- **When creating NPC spellcasters**
- **When checking class spell lists**
- **When player asks "What spells can I learn?"**

**Example usage:**
```
Player: "I just hit level 5, what new wizard spells can I learn?"
Me:
  1. get_spells_by_class(spell_class="Wizard", spell_level=3)
  2. Returns all 3rd-level wizard spells
  3. Present list: "You can learn: Fireball, Counterspell, Fly, Haste..."
```

**Parameters:**
- `spell_class`: "Wizard", "Cleric", "Bard", etc.
- `spell_level`: Optional filter (0-9, where 0 = cantrip)

---

### **Tool 9: `mcp_rules-database_lookup_monster`**
**When I use it:**
- **Every time I need monster stats** (AC, HP, attacks, abilities)
- **Before starting combat** (get stat blocks)
- **When player asks "What's that creature?"**
- **When checking monster abilities** (Multiattack, Pack Tactics, etc.)

**Example usage:**
```
Me: "Three goblins emerge from the bushes!"
Me (internally):
  1. lookup_monster("Goblin")
  2. Get: AC 15, HP 7, Scimitar +4 (1d6+2), Shortbow +4 (1d6+2)
  3. Use stats for combat
  4. Narrate: "Small green creatures with yellow eyes, brandishing scimitars"
```

**What I get:**
- Complete stat block (AC, HP, Speed)
- Ability scores and modifiers
- Attacks and damage
- Special abilities
- Saves and skills
- Challenge Rating

**Why this tool:**
- Never invent monster stats
- Accurate CR for XP calculation
- Correct attack bonuses
- Proper ability descriptions

---

### **Tool 10: `mcp_rules-database_search_monsters`**
**When I use it:**
- **When planning encounters** ("What CR 2 monsters are there?")
- **When player asks "What kind of undead are there?"**
- **When searching by type** ("Show me all dragons")
- **When building encounter variety**

**Example usage:**
```
Me (planning): "I need a CR 3 undead for this encounter"
Me:
  1. search_monsters(query="undead", max_results=20)
  2. Filter by CR 3
  3. Select: Wight (CR 3, undead)
  4. Use in encounter
```

**Parameters:**
- `query`: Search term (name, type, keyword)
- `max_results`: Limit results (default 10)

---

### **Tool 11: `mcp_rules-database_lookup_condition`**
**When I use it:**
- **When condition is applied** (Grappled, Prone, Stunned, etc.)
- **When checking condition effects** ("What does Prone do?")
- **At start of each turn** (check if condition affects actions)
- **When condition ends** (verify duration/removal method)

**Example usage:**
```
Player: "I grapple the goblin"
Me:
  1. Roll contested Strength check
  2. If player wins: lookup_condition("Grappled")
  3. Get: "Speed becomes 0, can't benefit from bonuses to speed"
  4. Apply condition to goblin
  5. Narrate: "You grab the goblin, holding it fast. Its speed drops to 0."
```

**What I get:**
- Full condition description
- Mechanical effects
- How to end the condition
- Interactions with other rules

---

### **Tool 12: `mcp_rules-database_lookup_rule`**
**When I use it:**
- **When rule question arises** ("How does grappling work?")
- **When checking action economy** ("Can I dash and attack?")
- **When verifying mechanics** ("What's the cover rules?")
- **Before making rulings**

**Example usage:**
```
Player: "Can I shove the goblin prone and then attack?"
Me:
  1. lookup_rule("Shove")
  2. Get: "Special melee attack, replaces one attack from Attack action"
  3. lookup_rule("Prone")
  4. Get: "Melee attacks have advantage, ranged attacks have disadvantage"
  5. Answer: "Yes! Shove is a special attack, so you can shove then attack with advantage"
```

**Common rules I look up:**
- Grapple, Shove, Dash, Dodge, Help
- Cover, Advantage/Disadvantage
- Opportunity Attacks, Reactions
- Two-Weapon Fighting
- Spellcasting rules

---

### **Tool 13: `mcp_rules-database_search_rules`**
**When I use it:**
- **When I know a keyword but not exact rule name**
- **When searching for related rules**
- **When exploring rule interactions**

**Example usage:**
```
Player: "How does two-weapon fighting work?"
Me:
  1. search_rules(query="two weapon", max_results=5)
  2. Find: "Two-Weapon Fighting" rule
  3. lookup_rule("Two-Weapon Fighting") for details
```

**Parameters:**
- `query`: Search keyword
- `max_results`: Limit results (default 5)

---

### **Tool 14: `mcp_rules-database_lookup_action`**
**When I use it:**
- **When player takes standard action** (Attack, Dash, Dodge, Help, Hide, Search, Use Object)
- **When checking action effects**
- **When explaining action options**

**Example usage:**
```
Player: "I use the Help action"
Me:
  1. lookup_action("Help")
  2. Get: "You help an ally, giving them advantage on next ability check or attack"
  3. Apply effect: Next attack on target has advantage
  4. Narrate: "You distract the goblin, giving Eglath an opening!"
```

**Standard actions:**
- Attack, Dash, Dodge, Help, Hide, Ready, Search, Use Object

---

## 📚 3. SOURCEBOOKS MCP (4 Tools)

### **Tool 15: `mcp_sourcebooks_search_sourcebooks`**
**When I use it:**
- **When I need detailed lore or flavor text**
- **When rules-database doesn't have enough context**
- **When searching for edge cases or examples**
- **When player asks deep questions about mechanics**

**Example usage:**
```
Player: "What's the full description of how inspiration works?"
Me:
  1. First try: rules-database (might have basic rule)
  2. If need more: search_sourcebooks("inspiration", sourcebook="phb", max_results=3)
  3. Get full PHB text with examples and edge cases
  4. Provide complete answer
```

**Parameters:**
- `query`: Search term
- `sourcebook`: "phb", "dmg", "mm", or "all"
- `max_results`: Limit results (default 5)

**Priority:**
- Use rules-database first (faster)
- Use sourcebooks if need more detail/lore

---

### **Tool 16: `mcp_sourcebooks_lookup_rule`**
**When I use it:**
- **When I need full rule text from sourcebooks**
- **When rules-database lookup isn't sufficient**
- **When checking official wording**

**Example usage:**
```
Me: "Let me check the exact wording of the Grapple rule"
Me:
  1. lookup_rule("Grapple", sourcebook="phb")
  2. Get full PHB text with all examples
  3. Use for accurate ruling
```

**Parameters:**
- `rule_name`: Rule name
- `sourcebook`: "phb", "dmg", "mm", or "all"

---

### **Tool 17: `mcp_sourcebooks_get_section`**
**When I use it:**
- **When I need entire chapter/section**
- **When reading full combat rules**
- **When studying spellcasting chapter**
- **When preparing complex encounters**

**Example usage:**
```
Me (preparing): "I need to review the full Combat chapter"
Me:
  1. get_section("Combat", sourcebook="phb")
  2. Get entire Combat chapter
  3. Review for encounter prep
```

**Parameters:**
- `section_title`: Chapter/section name
- `sourcebook`: "phb", "dmg", or "mm"

---

### **Tool 18: `mcp_sourcebooks_list_sections`**
**When I use it:**
- **When exploring what's available**
- **When finding chapter names**
- **When checking table of contents**

**Example usage:**
```
Me: "What sections are in the DMG?"
Me:
  1. list_sections(sourcebook="dmg")
  2. Get: ["Combat", "Magic Items", "Creating Encounters", ...]
  3. Use to find relevant section
```

**Parameters:**
- `sourcebook`: "phb", "dmg", "mm", or "all"

---

## 🎵 4. MUSIC-AMBIENCE MCP (6 Tools)

### **Tool 19: `mcp_music-ambience_play_ambient`**
**When I use it:**
- **At scene transitions** (tavern → dungeon → combat)
- **To set atmosphere** (creepy dungeon, peaceful town)
- **When entering new location**
- **Silently, without announcing to players**

**Example usage:**
```
Me (narrating): "You enter the dimly lit tavern..."
Me (silently):
  1. play_ambient(scene="tavern", auto_open=true)
  2. Continue narration without mentioning music
```

**Scene types:**
- `tavern`, `forest`, `dungeon`, `combat`, `town`, `castle`, `temple`
- `wilderness`, `creepy`, `peaceful`, `tense`, `ocean`, `storm`, `swamp`, `winter`, `wagon`

**Parameters:**
- `scene`: Scene type
- `auto_open`: Start playing automatically (default true)

---

### **Tool 20: `mcp_music-ambience_play_sfx`**
**When I use it:**
- **For dramatic moments** (sword clash, spell cast, door creak)
- **To emphasize actions** (critical hit, spell explosion)
- **For environmental sounds** (thunder, fire crackling)

**Example usage:**
```
Me: "Torgga's mace strikes with divine radiance!"
Me (silently):
  1. play_sfx("spell_radiant")
  2. Continue narration
```

**Common SFX:**
- `spell_fireball`, `sword_slash`, `door_open`, `thunder`, `arrow_shot`

**Parameters:**
- `sfx_name`: Sound effect name

---

### **Tool 21: `mcp_music-ambience_list_scenes`**
**When I use it:**
- **When checking available ambient tracks**
- **When planning scene music**
- **Rarely during gameplay** (usually know what I need)

**Example usage:**
```
Me (checking): "What ambient tracks are available?"
Me:
  1. list_scenes()
  2. Get: ["tavern", "forest", "dungeon", "combat", ...]
  3. Select appropriate one
```

---

### **Tool 22: `mcp_music-ambience_list_sfx`**
**When I use it:**
- **When checking available sound effects**
- **When planning dramatic moments**
- **Rarely during gameplay**

**Example usage:**
```
Me: "What sound effects can I use for this spell?"
Me:
  1. list_sfx()
  2. Get: ["spell_fireball", "spell_lightning", ...]
  3. Select appropriate SFX
```

---

### **Tool 23: `mcp_music-ambience_get_current_track`**
**When I use it:**
- **When checking what's currently playing**
- **When transitioning scenes** (stop current, start new)
- **When debugging audio issues**

**Example usage:**
```
Me (transitioning): "Combat ends, entering peaceful town"
Me:
  1. get_current_track()
  2. If combat music playing: stop_music()
  3. play_ambient(scene="town")
```

---

### **Tool 24: `mcp_music-ambience_stop_music`**
**When I use it:**
- **When transitioning between scenes**
- **When scene ends** (combat → exploration)
- **When player requests silence**

**Example usage:**
```
Me: "The battle ends. Silence returns to the forest."
Me (silently):
  1. stop_music()
  2. Continue narration
```

---

## 📝 5. SESSION-RECORDER MCP (7 Tools)

### **Tool 25: `mcp_session-recorder_start_session_log`**
**When I use it:**
- **At the very start of every session**
- **Before any gameplay begins**
- **After reading CURRENT_STATE.json and CAMPAIGN_EVENTS.json**

**Example usage:**
```
User: "Start session"
Me:
  1. Read CURRENT_STATE.json
  2. Read CAMPAIGN_EVENTS.json
  3. start_session_log(campaign_name="Phandelver", session_title="Session 5")
  4. Begin narration
```

**Parameters:**
- `campaign_name`: Campaign identifier
- `session_title`: Optional title (defaults to "Session YYYY-MM-DD")

**Why this tool:**
- Creates session log file
- Tracks all events for continuity
- Enables event extraction later

---

### **Tool 26: `mcp_session-recorder_log_event`**
**When I use it:**
- **After every significant event**
- **Player choices and decisions**
- **Important rolls and outcomes**
- **NPC interactions**
- **Combat milestones**
- **Discoveries and revelations**

**Example usage:**
```
Player: "I spare the goblin's life"
Me:
  1. Narrate the choice
  2. log_event(event_type="choice", content="Party spared goblin prisoner", metadata={"npc": "Goblin", "consequence": "goblin_grateful"})
  3. Continue story
```

**Event types:**
- `narration`: Story events, descriptions
- `choice`: Player decisions
- `roll`: Important dice rolls
- `combat`: Combat events
- `npc_interaction`: NPC meetings/conversations
- `discovery`: Found items, locations, secrets
- `gate`: Information gates passed
- `consequence`: Long-term effects

**Parameters:**
- `event_type`: One of the types above
- `content`: Description of event
- `metadata`: Additional data (NPC names, roll results, etc.)

---

### **Tool 27: `mcp_session-recorder_stop_session_log`**
**When I use it:**
- **At the end of every session**
- **When user says "end session"**
- **Before closing out**

**Example usage:**
```
User: "That's it for tonight"
Me:
  1. Narrate session wrap-up
  2. stop_session_log()
  3. Confirm: "Session logged. See you next time!"
```

**Why this tool:**
- Closes log file properly
- Ensures all events are saved
- Prepares for next session

---

### **Tool 28: `mcp_session-recorder_get_session_status`**
**When I use it:**
- **When checking if logging is active**
- **When debugging** ("Is the session log running?")
- **Before starting new log** (check if one already active)

**Example usage:**
```
Me (checking): "Is session logging active?"
Me:
  1. get_session_status()
  2. Get: {"active": true, "campaign": "Phandelver", "session_id": "..."}
  3. Continue or start new log
```

---

### **Tool 29: `mcp_session-recorder_list_session_logs`**
**When I use it:**
- **When reviewing past sessions**
- **When checking what happened last time**
- **When extracting events for campaign continuity**

**Example usage:**
```
User: "What happened last session?"
Me:
  1. list_session_logs(campaign_name="Phandelver")
  2. Get: ["session_20260113_190304", "session_20260112_180000", ...]
  3. Read latest log file
  4. Summarize events
```

**Parameters:**
- `campaign_name`: Filter by campaign (optional)

---

### **Tool 30: `mcp_session-recorder_extract_events`**
**When I use it:**
- **After session ends** (extract structured events)
- **When updating CAMPAIGN_EVENTS.json**
- **When analyzing session outcomes**

**Example usage:**
```
Me (post-session):
  1. extract_events(session_id="session_20260113_190304", campaign_name="Phandelver")
  2. Get structured events array
  3. Use to update CAMPAIGN_EVENTS.json
```

**Parameters:**
- `session_id`: Session identifier
- `campaign_name`: Campaign name

---

### **Tool 31: `mcp_session-recorder_update_campaign_events`**
**When I use it:**
- **After extracting events from session log**
- **When updating CAMPAIGN_EVENTS.json**
- **When adding events to campaign history**

**Example usage:**
```
Me (post-session):
  1. Extract events from log
  2. update_campaign_events(campaign_name="Phandelver", events=[...])
  3. Events added to CAMPAIGN_EVENTS.json
```

**Parameters:**
- `campaign_name`: Campaign name
- `events`: Array of event objects

---

## ⚔️ 6. COMBAT-ENGINE MCP (9 Tools)

### **Tool 32: `mcp_combat-engine_start_combat`**
**When I use it:**
- **At the start of every combat encounter**
- **Before initiative is rolled**
- **When combat begins**

**Example usage:**
```
Me: "Roll for initiative! Three goblins leap from the bushes!"
Me (internally):
  1. Get PC stats: get_character_combat_stats() for each PC
  2. Get monster stats: lookup_monster("Goblin")
  3. start_combat({
      encounter_name: "Goblin Ambush",
      character_ids: ["Torgga_Brawnanvil", "Eglath_Bearkiller", ...],
      monster_data: [
        {creature_id: "goblin_1", name: "Goblin 1", creature_type: "monster",
         max_hp: 7, current_hp: 7, ac: 15, speed: 30, ...},
        ...
      ],
      battlefield_width: 20,
      battlefield_height: 20
    })
  4. Get combat_id for future calls
```

**What this does:**
- Creates combat state
- Tracks all combatants
- Sets up battlefield
- Returns combat_id for all future calls

**Parameters:**
- `encounter_name`: Display name
- `character_ids`: PC IDs (optional, can load from sheets)
- `monster_data`: Array of monster stat blocks
- `battlefield_width`: Grid width in 5ft squares
- `battlefield_height`: Grid height in 5ft squares
- `encounter_id`: Optional ID (auto-generated if not provided)

---

### **Tool 33: `mcp_combat-engine_roll_initiative_tool`**
**When I use it:**
- **Immediately after start_combat**
- **Before first turn**
- **Auto-rolls initiative for all combatants**

**Example usage:**
```
Me:
  1. start_combat(...) → Get combat_id
  2. roll_initiative_tool(combat_id="...")
  3. Returns sorted initiative order
  4. Narrate: "Eglath goes first (21), then Goblin 1 (18)..."
```

**What this does:**
- Automatically rolls d20 + initiative bonus for all
- Sorts by initiative (highest first)
- Sets turn order
- Returns initiative list

**Parameters:**
- `combat_id`: Combat identifier

**Note:** Uses initiative_bonus from character/monster data automatically.

---

### **Tool 34: `mcp_combat-engine_load_battlefield`**
**When I use it:**
- **After start_combat, before or after initiative**
- **To set initial positions**
- **To add terrain features**
- **To place obstacles**

**Example usage:**
```
Me:
  1. start_combat(...)
  2. load_battlefield({
      combat_id: "...",
      combatant_positions: {
        "Torgga_Brawnanvil": {x: 5, y: 10},
        "Eglath_Bearkiller": {x: 7, y: 10},
        "goblin_1": {x: 15, y: 8},
        "goblin_2": {x: 17, y: 8}
      },
      terrain_data: [
        {type: "difficult_terrain", x: 10, y: 10, width: 2, height: 2},
        {type: "cover", x: 12, y: 5, width: 1, height: 1}
      ]
    })
  3. Combat ready with positions set
```

**Parameters:**
- `combat_id`: Combat identifier
- `combatant_positions`: Dict of {creature_id: {x, y}}
- `terrain_data`: Array of terrain features (optional)

---

### **Tool 35: `mcp_combat-engine_next_turn_tool`**
**When I use it:**
- **After every turn completes**
- **To advance to next combatant**
- **At end of round** (moves to round 2, turn 1)

**Example usage:**
```
Me: "Eglath's turn ends. Next up: Goblin 1"
Me (internally):
  1. Complete Eglath's turn (attack, move, etc.)
  2. next_turn_tool(combat_id="...")
  3. Get: Next combatant is "Goblin 1", Round 1, Turn 2
  4. Narrate Goblin 1's turn
```

**What this does:**
- Advances turn counter
- Moves to next combatant in initiative
- Handles round transitions
- Returns current turn info

**Parameters:**
- `combat_id`: Combat identifier

---

### **Tool 36: `mcp_combat-engine_get_combat_status`**
**When I use it:**
- **At start of each turn** (check current state)
- **When player asks "What's the situation?"**
- **When checking HP/conditions**
- **When verifying positions**

**Example usage:**
```
Player: "What's everyone's HP?"
Me:
  1. get_combat_status(combat_id="...")
  2. Get: Full combat state with HP, conditions, positions
  3. Narrate: "Eglath: 45/65 HP, Torgga: 28/45 HP, Goblin 1: 2/7 HP..."
```

**What I get:**
- All combatants with current HP
- Current turn and round
- Positions on battlefield
- Active conditions
- Initiative order

**Parameters:**
- `combat_id`: Combat identifier

---

### **Tool 37: `mcp_combat-engine_attack_tool`**
**When I use it:**
- **Every attack in combat** (PCs and NPCs)
- **Melee and ranged attacks**
- **Spell attacks**

**Example usage:**
```
Player: "I attack Goblin 1 with my greataxe"
Me:
  1. get_combat_status() → Check positions (verify in range)
  2. attack_tool({
      combat_id: "...",
      attacker_id: "Eglath_Bearkiller",
      target_id: "goblin_1",
      attack_bonus: 7,  // STR + proficiency + magic
      damage_dice: "1d12+4",  // Greataxe damage
      damage_type: "slashing",
      advantage: false,
      disadvantage: false
    })
  3. Tool auto-rolls: d20+7 = 18 vs AC 15 → Hit!
  4. Tool auto-rolls damage: 1d12+4 = 9
  5. Apply 9 damage to goblin_1
  6. Narrate: "Your greataxe cleaves into the goblin, dealing 9 slashing damage!"
```

**What this does:**
- Auto-rolls attack (d20 + attack_bonus)
- Checks hit vs target AC
- Auto-rolls damage if hit
- Applies damage to target
- Returns hit/miss and damage

**Parameters:**
- `combat_id`: Combat identifier
- `attacker_id`: Attacking creature ID
- `target_id`: Target creature ID
- `attack_bonus`: Attack modifier
- `damage_dice`: Damage expression ("1d8+3", "2d6")
- `damage_type`: "slashing", "piercing", "fire", etc.
- `advantage`: True if advantage
- `disadvantage`: True if disadvantage

**Why this tool:**
- Handles all attack mechanics
- Auto-rolls (no manual dice)
- Tracks damage automatically
- Checks range and line of sight

---

### **Tool 38: `mcp_combat-engine_move_creature`**
**When I use it:**
- **When creature moves on battlefield**
- **Before attacking** (if need to close distance)
- **When taking Dash action**
- **When repositioning**

**Example usage:**
```
Player: "I move up to the goblin and attack"
Me:
  1. move_creature({
      combat_id: "...",
      creature_id: "Eglath_Bearkiller",
      new_position: {x: 14, y: 8},  // Adjacent to goblin at (15, 8)
      is_dash: false
    })
  2. Verify movement (check speed, difficult terrain)
  3. Then attack_tool() to attack
```

**Parameters:**
- `combat_id`: Combat identifier
- `creature_id`: Moving creature ID
- `new_position`: {x, y} coordinates
- `is_dash`: True if using Dash action (double speed)

**What this does:**
- Validates movement distance
- Checks difficult terrain
- Updates creature position
- Returns success/failure

---

### **Tool 39: `mcp_combat-engine_get_ai_action`**
**When I use it:**
- **On every enemy/NPC turn**
- **To decide what monster does**
- **For tactical decisions**

**Example usage:**
```
Me: "Goblin 1's turn"
Me (internally):
  1. get_ai_action(combat_id="...", creature_id="goblin_1")
  2. Get: {
      action: "attack",
      target: "Eglath_Bearkiller",
      reasoning: "Lowest AC target in range"
    }
  3. Execute: attack_tool(...)
  4. Narrate: "The goblin snarls and lunges at Eglath!"
```

**What this does:**
- Analyzes battlefield
- Considers monster intelligence
- Selects best target
- Chooses action (attack, move, ability)
- Returns recommended action

**Parameters:**
- `combat_id`: Combat identifier
- `creature_id`: Enemy creature ID

**Note:** This is a suggestion. I can override if it doesn't fit the monster's personality/intelligence.

---

### **Tool 40: `mcp_combat-engine_end_combat_tool`**
**When I use it:**
- **When all enemies defeated**
- **When combat ends** (flee, surrender, etc.)
- **After final turn**

**Example usage:**
```
Me: "The last goblin falls! Combat ends."
Me (internally):
  1. end_combat_tool(combat_id="...")
  2. Get: Combat summary (damage dealt, rounds, etc.)
  3. Auto-syncs all PC HP to Obsidian
  4. Proceed to post-combat (XP, loot, etc.)
```

**What this does:**
- Ends combat state
- Provides combat summary
- Syncs final HP to Obsidian
- Cleans up combat data
- Returns summary

**Parameters:**
- `combat_id`: Combat identifier

**After this:**
- Distribute XP (post-combat procedure)
- Distribute loot (post-combat procedure)
- Update Obsidian with rewards

---

## 📓 7. OBSIDIAN-SYNC MCP (17 Tools)

### **Tool 41: `mcp_obsidian-sync_update_character_hp`**
**When I use it:**
- **After EVERY damage or healing event**
- **During combat** (real-time HP updates)
- **After combat ends**
- **When resting** (restore HP)

**Example usage:**
```
Me: "The goblin's scimitar cuts into Eglath for 6 damage"
Me (immediately):
  1. attack_tool() → Eglath takes 6 damage (now 39/65 HP)
  2. update_character_hp("Eglath_Bearkiller", 39, 65)
  3. Obsidian file updated instantly
  4. Player can see HP change in real-time
```

**Parameters:**
- `character_name`: "Torgga_Brawnanvil", "Eglath_Bearkiller", etc.
- `new_hp`: Current HP
- `max_hp`: Maximum HP

**CRITICAL:** Update Obsidian HP after EVERY damage/healing event, not just at end of combat!

---

### **Tool 42: `mcp_obsidian-sync_update_character_xp`**
**When I use it:**
- **After combat ends** (distribute XP)
- **After quest completion** (quest XP reward)
- **After milestone events** (milestone XP)

**Example usage:**
```
Me (post-combat):
  1. Calculate XP: 2 Goblins (CR 1/4) = 100 XP total
  2. Divide by party: 100 / 5 = 20 XP each
  3. update_character_xp("Torgga_Brawnanvil", 20)
  4. update_character_xp("Eglath_Bearkiller", 20)
  5. ... (all party members)
  6. Narrate: "You each gain 20 XP (8,340 / 14,000 to Level 6)"
```

**Parameters:**
- `character_name`: Character name
- `xp_to_add`: XP to add (accumulates, doesn't replace)

**Note:** XP accumulates. Tool reads current XP and adds to it.

---

### **Tool 43: `mcp_obsidian-sync_update_character_currency`**
**When I use it:**
- **After looting enemies** (distribute coins)
- **After quest rewards** (gold payment)
- **After selling items**
- **After finding treasure**

**Example usage:**
```
Me (post-combat loot):
  1. Roll loot: 2d6 cp, 2d4 sp per goblin
  2. Total: 7 cp, 5 sp
  3. Divide: 1 cp, 1 sp each (2 cp, 1 sp remainder to first player)
  4. update_character_currency("Torgga_Brawnanvil", cp=2, sp=1)
  5. update_character_currency("Eglath_Bearkiller", cp=1, sp=1)
  6. ... (all party members)
```

**Parameters:**
- `character_name`: Character name
- `cp`: Copper pieces to add (default 0)
- `sp`: Silver pieces to add (default 0)
- `gp`: Gold pieces to add (default 0)
- `pp`: Platinum pieces to add (default 0)

**Note:** Currency accumulates. Tool reads current currency and adds to it.

---

### **Tool 44: `mcp_obsidian-sync_get_character_combat_stats`**
**When I use it:**
- **Before combat starts** (get PC stats)
- **When checking abilities** (for skill checks, saves)
- **When verifying modifiers** (attack bonus, save DC)
- **When reading character data**

**Example usage:**
```
Me (starting combat):
  1. get_character_combat_stats("Torgga_Brawnanvil")
  2. Get: {
      hp: {current: 45, maximum: 45},
      ac: 20,
      speed: 25,
      strength: 14, dexterity: 8, constitution: 16,
      initiative_bonus: -1,
      ...
    }
  3. Use stats for combat setup
```

**What I get:**
- Current/max HP
- AC, Speed
- Ability scores and modifiers
- Initiative bonus
- Proficiency bonus
- Saving throw proficiencies

**Parameters:**
- `character_name`: Character name (format: "FirstName_LastName")

---

### **Tool 45: `mcp_obsidian-sync_add_inventory_item`**
**When I use it:**
- **After looting** (general items: potions, rations, tools)
- **After finding treasure** (gems, art objects)
- **After purchasing items**
- **After quest rewards** (non-weapon/armor items)

**Example usage:**
```
Me (post-combat): "You find 3 potions of healing on the goblin"
Player: "I'll take them"
Me:
  1. add_inventory_item("Torgga_Brawnanvil", "Potion of Healing", quantity=3, weight=0.5)
  2. Item added to General Inventory table
  3. Narrate: "Added to your inventory"
```

**Parameters:**
- `character_name`: Character name
- `item_name`: Item name
- `quantity`: How many (default 1)
- `weight`: Weight in pounds (default 0)

**Note:** Goes to "General Inventory" table, not Weapons/Armor/Magic Items.

---

### **Tool 46: `mcp_obsidian-sync_remove_inventory_item`**
**When I use it:**
- **When item is used** (potion consumed, ration eaten)
- **When item is dropped**
- **When item is given away**
- **When reducing quantity**

**Example usage:**
```
Player: "I drink a healing potion"
Me:
  1. Roll healing: roll_dice("2d4+2", "Potion of Healing")
  2. Apply healing: update_character_hp(...)
  3. remove_inventory_item("Torgga_Brawnanvil", "Potion of Healing", quantity=1)
  4. Narrate: "You drink the potion and feel better. 2 potions remaining."
```

**Parameters:**
- `character_name`: Character name
- `item_name`: Item name
- `quantity`: How many to remove (default 1)

---

### **Tool 47: `mcp_obsidian-sync_add_weapon`**
**When I use it:**
- **After looting weapons**
- **After purchasing weapons**
- **After quest rewards** (weapon items)
- **When finding magic weapons**

**Example usage:**
```
Me: "You find a +1 Longsword on the goblin leader"
Player: "I'll take it"
Me:
  1. add_weapon("Torgga_Brawnanvil", "Longsword +1", 
                attack_bonus=6,  // STR + proficiency + magic
                damage="1d8+3 slashing",  // 1d8 + STR + magic
                properties="Versatile (1d10)",
                special_effects="+1 magic weapon",
                equipped=false)
  2. Weapon added to Weapons table
```

**Parameters:**
- `character_name`: Character name
- `weapon_name`: Weapon name
- `attack_bonus`: Attack modifier
- `damage`: Damage dice + type ("1d8+3 slashing")
- `properties`: Weapon properties ("Light", "Finesse", "Versatile (1d10)")
- `special_effects`: Magic effects, special abilities
- `equipped`: Is weapon currently equipped? (default false)

---

### **Tool 48: `mcp_obsidian-sync_remove_weapon`**
**When I use it:**
- **When weapon is dropped**
- **When weapon is given away**
- **When weapon breaks**
- **When removing from inventory**

**Example usage:**
```
Player: "I drop my old longsword"
Me:
  1. remove_weapon("Torgga_Brawnanvil", "Longsword")
  2. Weapon removed from Weapons table
```

**Parameters:**
- `character_name`: Character name
- `weapon_name`: Weapon name

---

### **Tool 49: `mcp_obsidian-sync_equip_weapon`**
**When I use it:**
- **When player equips weapon**
- **When switching weapons**
- **When drawing/sheathing weapon**

**Example usage:**
```
Player: "I draw my +1 Longsword"
Me:
  1. equip_weapon("Torgga_Brawnanvil", "Longsword +1", equipped=true)
  2. Equipped status updated in Weapons table
  3. Narrate: "You draw the gleaming blade"
```

**Parameters:**
- `character_name`: Character name
- `weapon_name`: Weapon name
- `equipped`: True to equip, False to unequip

---

### **Tool 50: `mcp_obsidian-sync_add_armor`**
**When I use it:**
- **After looting armor**
- **After purchasing armor**
- **After quest rewards** (armor items)
- **When finding magic armor**

**Example usage:**
```
Me: "You find a +1 Breastplate in the treasure hoard"
Player: "I'll take it"
Me:
  1. add_armor("Torgga_Brawnanvil", "Breastplate +1",
               ac_bonus=6,  // Base 14 + magic
               armor_type="Medium",
               properties="Stealth disadvantage",
               special_effects="+1 magic armor",
               equipped=false)
  2. Armor added to Armor & Shields table
```

**Parameters:**
- `character_name`: Character name
- `armor_name`: Armor name
- `ac_bonus`: AC bonus this armor provides
- `armor_type`: "Light", "Medium", "Heavy", "Shield"
- `properties`: Armor properties ("Stealth disadvantage", etc.)
- `special_effects`: Magic effects, special abilities
- `equipped`: Is armor currently equipped? (default false)

---

### **Tool 51: `mcp_obsidian-sync_remove_armor`**
**When I use it:**
- **When armor is dropped**
- **When armor is given away**
- **When armor is removed from inventory**

**Example usage:**
```
Player: "I take off my old chain mail"
Me:
  1. remove_armor("Torgga_Brawnanvil", "Chain Mail")
  2. Armor removed from table
```

**Parameters:**
- `character_name`: Character name
- `armor_name`: Armor name

---

### **Tool 52: `mcp_obsidian-sync_equip_armor`**
**When I use it:**
- **When player puts on armor**
- **When switching armor**
- **When donning/doffing armor**

**Example usage:**
```
Player: "I put on the +1 Breastplate"
Me:
  1. equip_armor("Torgga_Brawnanvil", "Breastplate +1", equipped=true)
  2. Equipped status updated
  3. Narrate: "You don the magical breastplate. Your AC is now 20."
```

**Parameters:**
- `character_name`: Character name
- `armor_name`: Armor name
- `equipped`: True to equip, False to unequip

---

### **Tool 53: `mcp_obsidian-sync_add_magic_item`**
**When I use it:**
- **After finding magic items**
- **After quest rewards** (magic items)
- **When identifying magic items**

**Example usage:**
```
Me: "You identify the ring as a Ring of Protection"
Player: "I'll take it"
Me:
  1. add_magic_item("Torgga_Brawnanvil", "Ring of Protection",
                    properties="+1 AC and +1 to all saving throws",
                    charges="N/A",
                    notes="Requires attunement",
                    attuned=false)
  2. Magic item added to Magic Items table
```

**Parameters:**
- `character_name`: Character name
- `item_name`: Magic item name
- `properties`: What the item does
- `charges`: Charge system ("3/3", "N/A")
- `notes`: Additional notes (attunement requirements, etc.)
- `attuned`: Is item currently attuned? (default false)

---

### **Tool 54: `mcp_obsidian-sync_remove_magic_item`**
**When I use it:**
- **When magic item is lost**
- **When magic item is given away**
- **When magic item is destroyed**

**Example usage:**
```
Me: "The artifact shatters into dust"
Me:
  1. remove_magic_item("Torgga_Brawnanvil", "Ancient Artifact")
  2. Item removed from Magic Items table
```

**Parameters:**
- `character_name`: Character name
- `item_name`: Magic item name

---

### **Tool 55: `mcp_obsidian-sync_attune_item`**
**When I use it:**
- **When player attunes to magic item**
- **When player breaks attunement**
- **When switching attuned items** (if at limit)

**Example usage:**
```
Player: "I attune to the Ring of Protection"
Me:
  1. Check attunement limit (3 items max)
  2. attune_item("Torgga_Brawnanvil", "Ring of Protection", attuned=true)
  3. Attuned status updated
  4. Narrate: "You feel the ring's magic bond with you. You're now attuned."
```

**Parameters:**
- `character_name`: Character name
- `item_name`: Magic item name
- `attuned`: True to attune, False to break attunement

---

### **Tool 56: `mcp_obsidian-sync_create_npc`**
**When I use it:**
- **When party meets new NPC**
- **When important NPC is introduced**
- **When creating NPCs for encounters**

**Example usage:**
```
Me: "A grizzled dwarf approaches you"
Me (internally):
  1. create_npc(npc_name="Gundren Rockseeker", 
                race="Dwarf",
                role="quest_giver",
                location="Phandalin",
                description="Dwarf prospector who hired the party",
                disposition="friendly")
  2. NPC created in Obsidian
  3. Continue narration
```

**Parameters:**
- `npc_name`: NPC name
- `race`: Race
- `role`: "ally", "enemy", "neutral", "quest_giver"
- `location`: Where NPC is
- `description`: NPC description
- `disposition`: "friendly", "hostile", "neutral"

**Note:** This creates NPC in Obsidian. For campaign wiki tracking, use campaign-wiki `create_npc` instead (which auto-syncs to Obsidian).

---

## 🏰 8. CAMPAIGN-WIKI MCP (11 Tools)

### **Tool 57: `mcp_campaign-wiki_create_or_load_wiki`**
**When I use it:**
- **At session start** (load campaign wiki)
- **Before using any other campaign-wiki tools**
- **Once per session** (wiki stays loaded)

**Example usage:**
```
Me (session start):
  1. Read CURRENT_STATE.json
  2. Read CAMPAIGN_EVENTS.json
  3. create_or_load_wiki(campaign_name="Phandelver")
  4. Wiki loaded with all NPCs, quests, factions
  5. Ready to use other wiki tools
```

**Parameters:**
- `campaign_name`: Campaign identifier
- `obsidian_vault`: Optional vault path (defaults to standard path)
- `maps_folder`: Optional maps folder

**What this does:**
- Loads or creates campaign wiki JSON
- Loads all NPCs, quests, locations, factions
- Sets up relationship graphs
- Prepares for wiki operations

---

### **Tool 58: `mcp_campaign-wiki_create_npc`**
**When I use it:**
- **When party meets new NPC**
- **When important NPC is introduced**
- **When NPC becomes relevant to story**

**Example usage:**
```
Me: "A mysterious figure in a hood approaches"
Me (internally):
  1. create_npc(campaign_name="Phandelver",
                name="Halia Thornton",
                role="quest_giver",
                description="Guild Master of Miner's Exchange",
                faction="Miner's Exchange")
  2. NPC created in wiki
  3. Auto-synced to Obsidian (if vault configured)
  4. Continue narration
```

**Parameters:**
- `campaign_name`: Campaign name
- `name`: NPC name
- `role`: "ally", "enemy", "neutral", "quest_giver"
- `description`: NPC description
- `npc_id`: Optional ID (auto-generated)

**Auto-sync:** NPC automatically synced to Obsidian when created!

---

### **Tool 59: `mcp_campaign-wiki_add_relationship`**
**When I use it:**
- **When NPCs interact** ("Gundren is friends with Sildar")
- **When relationships change**
- **When tracking NPC connections**

**Example usage:**
```
Me: "Gundren introduces you to his friend Sildar"
Me (internally):
  1. add_relationship(campaign_name="Phandelver",
                    from_entity="Gundren Rockseeker",
                    to_entity="Sildar Hallwinter",
                    relationship_type="friend",
                    description="Travel companions, trusted allies")
  2. Relationship added to wiki
  3. Both NPCs auto-synced to Obsidian with relationship links
```

**Parameters:**
- `campaign_name`: Campaign name
- `from_entity`: Source NPC ID or name
- `to_entity`: Target NPC ID or name
- `relationship_type`: "ally", "enemy", "family", "friend", "rival", "romantic", "business", "mentor_student", "neutral"
- `description`: Relationship description
- `strength`: 1-10 (default 5)

**Auto-sync:** Both NPCs automatically re-synced to Obsidian with updated relationships!

---

### **Tool 60: `mcp_campaign-wiki_create_quest`**
**When I use it:**
- **When NPC gives quest**
- **When quest becomes available**
- **When tracking quest objectives**

**Example usage:**
```
NPC: "I need you to investigate the crime scenes in Phandalin"
Me (internally):
  1. create_quest(campaign_name="Phandelver",
                 name="Investigate Crime Scenes",
                 description="Harbin wants you to investigate four crime scenes",
                 quest_type="investigation",
                 status="accepted",
                 quest_giver="Harbin Wester",
                 reward_gold=200,
                 reward_xp=500,
                 reward_items=["Potion of Healing"],
                 reward_reputation={"Phandalin Townsfolk": 10},
                 objectives=["Investigate Barthen's Well", 
                            "Investigate Miner's Exchange",
                            "Investigate Shrine of Luck",
                            "Investigate Sleeping Giant"])
  2. Quest created and tracked
```

**Parameters:**
- `campaign_name`: Campaign name
- `name`: Quest name
- `description`: Quest description
- `quest_type`: "main", "side", "personal", "faction", "bounty", "fetch", "escort", "investigation", "rescue", "combat"
- `status`: "not_started", "available", "accepted", "in_progress", "completed", "failed", "abandoned"
- `quest_giver`: NPC ID or name
- `reward_gold`: Gold reward
- `reward_xp`: XP reward
- `reward_items`: Array of item rewards
- `reward_reputation`: Dict of {faction_name: reputation_amount}
- `objectives`: Array of quest objectives
- `quest_id`: Optional ID (auto-generated)

---

### **Tool 61: `mcp_campaign-wiki_update_quest_status`**
**When I use it:**
- **When quest status changes** (accepted → in_progress → completed)
- **When quest is abandoned**
- **When quest fails**

**Example usage:**
```
Player: "We've finished investigating all four crime scenes"
Me:
  1. update_quest_status(campaign_name="Phandelver",
                        quest_id="investigate_crimes",
                        status="completed")
  2. Quest status updated
  3. date_completed automatically set
  4. Then use complete_quest() to distribute rewards
```

**Parameters:**
- `campaign_name`: Campaign name
- `quest_id`: Quest ID
- `status`: New status

**Auto-dates:** Automatically sets `date_accepted` when status becomes "accepted", `date_completed` when "completed".

---

### **Tool 62: `mcp_campaign-wiki_complete_quest`**
**When I use it:**
- **When quest is finished**
- **After update_quest_status(..., "completed")**
- **To automatically distribute rewards and reputation**

**Example usage:**
```
Me: "You've completed the investigation quest!"
Me (internally):
  1. update_quest_status(..., status="completed")
  2. complete_quest(campaign_name="Phandelver",
                   quest_id="investigate_crimes",
                   party_members=["Brevin", "Eglath", "Torgga", "Vandross", "Zephyr"])
  3. Returns: {
      rewards_distributed: {
        gold: {"Brevin": 40, "Eglath": 40, ...},  // 200 / 5 = 40 each
        xp: {"Brevin": 100, "Eglath": 100, ...},  // 500 / 5 = 100 each
        items: ["Potion of Healing"],  // Manual distribution
        reputation: {"Phandalin Townsfolk": 10}  // Auto-applied
      }
    }
  4. Apply gold via obsidian-sync: update_character_currency(...)
  5. Apply XP via obsidian-sync: update_character_xp(...)
  6. Ask player who gets Potion of Healing
  7. Reputation automatically updated!
```

**What this does:**
- Updates quest status to "completed"
- Splits gold evenly among party
- Splits XP evenly among party
- Lists items for manual distribution
- **Automatically updates faction reputation:**
  - If quest giver has faction → +5 reputation with that faction
  - Applies quest-specific reputation from `reward_reputation`
- Auto-syncs affected factions to Obsidian

**Parameters:**
- `campaign_name`: Campaign name
- `quest_id`: Quest ID
- `party_members`: Array of party member names (defaults to ["Party"])

**Returns:** Distribution amounts for applying via obsidian-sync tools.

---

### **Tool 63: `mcp_campaign-wiki_create_faction`**
**When I use it:**
- **When faction is introduced**
- **When organization becomes relevant**
- **When setting up faction system**

**Example usage:**
```
Me: "You learn about the Lords' Alliance"
Me (internally):
  1. create_faction(campaign_name="Phandelver",
                   name="Lords' Alliance",
                   faction_type="government",
                   description="Coalition of cities across Sword Coast",
                   goals=["Promote trade", "Mutual defense"],
                   rank_structure=["Clasp", "Member", "Agent", "Master"],
                   benefits={
                     "Clasp": ["10% discount", "Safe house access"],
                     "Member": ["20% discount", "Information network"]
                   })
  2. Faction created
  3. Auto-synced to Obsidian
```

**Parameters:**
- `campaign_name`: Campaign name
- `name`: Faction name
- `faction_type`: "guild", "religious", "military", "criminal", "merchant", "noble", "academic", "adventurer", "cult", "government", "other"
- `description`: Faction description
- `goals`: Array of faction goals
- `values`: Array of faction values
- `territory`: Array of territories
- `leader`: Leader NPC ID or name
- `headquarters`: Headquarters location
- `rank_structure`: Array of ranks (lowest to highest)
- `benefits`: Dict of {rank: [benefits]}
- `requirements`: Dict of {rank: requirements}
- `faction_id`: Optional ID (auto-generated)

**Auto-sync:** Faction automatically synced to Obsidian when created!

---

### **Tool 64: `mcp_campaign-wiki_update_faction_reputation`**
**When I use it:**
- **After quest completion** (if quest affects faction)
- **After significant actions** (helping/harming faction)
- **When reputation changes**

**Example usage:**
```
Me: "By completing the quest for Sildar, the Lords' Alliance takes notice"
Me (internally):
  1. update_faction_reputation(campaign_name="Phandelver",
                              faction_id="lords_alliance_id",
                              character_name="Party",
                              amount=5)
  2. Reputation updated: +5 (now 15, Friendly level)
  3. Auto-synced to Obsidian
```

**Parameters:**
- `campaign_name`: Campaign name
- `faction_id`: Faction ID
- `character_name`: "Party" or individual character name
- `amount`: Reputation change (+ or -)

**Auto-sync:** Faction automatically synced to Obsidian with updated reputation!

---

### **Tool 65: `mcp_campaign-wiki_update_faction_rank`**
**When I use it:**
- **When character earns promotion**
- **When rank requirements are met**
- **When manually setting rank**

**Example usage:**
```
Me: "You've completed 3 quests for the Lords' Alliance. You're promoted to Member rank!"
Me (internally):
  1. update_faction_rank(campaign_name="Phandelver",
                        faction_id="lords_alliance_id",
                        character_name="Party",
                        promote=true)  // Auto-promote to next rank
  2. Rank updated: "Member"
  3. Auto-synced to Obsidian
```

**Parameters:**
- `campaign_name`: Campaign name
- `faction_id`: Faction ID
- `character_name`: "Party" or individual character name
- `new_rank`: Specific rank title (optional if promote=true)
- `promote`: True to auto-promote to next rank

**Auto-sync:** Faction automatically synced to Obsidian with updated rank!

---

### **Tool 66: `mcp_campaign-wiki_get_faction_info`**
**When I use it:**
- **When checking party reputation with faction**
- **When checking rank and benefits**
- **When player asks about faction status**

**Example usage:**
```
Player: "What's our standing with the Lords' Alliance?"
Me:
  1. get_faction_info(campaign_name="Phandelver",
                     faction_id="lords_alliance_id",
                     character_name="Party")
  2. Get: {
      reputation: 15,
      reputation_level: "friendly",
      rank: "Clasp",
      can_promote: true,
      benefits: ["10% discount", "Safe house access"]
    }
  3. Narrate: "You're at Friendly reputation (15) with the Lords' Alliance, rank Clasp. You have access to safe houses and 10% discounts."
```

**Parameters:**
- `campaign_name`: Campaign name
- `faction_id`: Faction ID
- `character_name`: Optional, to get character-specific info

---

### **Tool 67: `mcp_campaign-wiki_sync_to_obsidian`**
**When I use it:**
- **At end of session** (sync all wiki data)
- **When manually exporting**
- **After major wiki updates**

**Example usage:**
```
Me (end of session):
  1. sync_to_obsidian(campaign_name="Phandelver")
  2. All NPCs, quests, locations, factions exported to Obsidian
  3. Wiki data synced
```

**Parameters:**
- `campaign_name`: Campaign name

**Note:** Most wiki operations auto-sync. This is for manual full sync.

---

## 🌤️ 9. WEATHER-CALENDAR MCP (2 Tools)

### **Tool 68: `mcp_weather-calendar_get_weather`**
**When I use it:**
- **At start of day** (describe weather)
- **When weather affects gameplay** (rain, fog, storms)
- **When players ask about weather**
- **For travel scenes** (weather during journey)

**Example usage:**
```
Me (morning): "You wake to a new day"
Me (internally):
  1. get_weather(season="winter", terrain="forest")
  2. Get: "Light snow, cold, visibility good"
  3. Narrate: "A light snow falls as you break camp. The forest is quiet and cold."
```

**Parameters:**
- `season`: "spring", "summer", "autumn", "winter"
- `terrain`: "forest", "mountain", "plains", "coast"

---

### **Tool 69: `mcp_weather-calendar_advance_time`**
**When I use it:**
- **After travel** (advance time by hours/days)
- **After long rest** (advance 8 hours)
- **When time passes** (waiting, downtime)
- **When tracking in-game time**

**Example usage:**
```
Me: "You travel for 6 hours to Phandalin"
Me (internally):
  1. advance_time(campaign_name="Phandelver", hours=6)
  2. Time advanced: Now 2:00 PM (was 8:00 AM)
  3. Continue narration
```

**Parameters:**
- `campaign_name`: Campaign name
- `hours`: Hours to advance

---

## 🕸️ 10. KNOWLEDGE-GRAPH MCP (3 Tools)

### **Tool 70: `mcp_knowledge-graph_add_entity`**
**When I use it:**
- **When tracking important entities** (NPCs, locations, items, factions)
- **When building relationship network**
- **When analyzing connections**

**Example usage:**
```
Me: "You discover the artifact"
Me (internally):
  1. add_entity(name="Ancient Artifact",
               entity_type="item",
               description="Powerful artifact sought by the Black Spider")
  2. Entity added to knowledge graph
  3. Can now link relationships
```

**Parameters:**
- `name`: Entity name
- `entity_type`: "npc", "location", "item", "faction"
- `description`: Entity description

---

### **Tool 71: `mcp_knowledge-graph_add_relationship`**
**When I use it:**
- **When tracking connections between entities**
- **When analyzing how things relate**
- **When building relationship network**

**Example usage:**
```
Me: "The artifact is connected to the Black Spider's plans"
Me (internally):
  1. add_relationship(from_entity="Ancient Artifact",
                    to_entity="Black Spider Network",
                    relationship="sought_by")
  2. Relationship added to graph
```

**Parameters:**
- `from_entity`: Source entity name
- `to_entity`: Target entity name
- `relationship`: Relationship type

---

### **Tool 72: `mcp_knowledge-graph_query_entity`**
**When I use it:**
- **When checking entity connections**
- **When analyzing relationships**
- **When exploring knowledge graph**

**Example usage:**
```
Me: "Let me check what we know about the Black Spider"
Me (internally):
  1. query_entity(name="Black Spider Network")
  2. Get: Entity info + all relationships
  3. Use for story connections
```

**Parameters:**
- `name`: Entity name

---

## 📊 SUMMARY: Tool Usage by Scenario

### **Session Start:**
1. `create_or_load_wiki` - Load campaign wiki
2. `start_session_log` - Begin logging
3. `get_weather` - Describe weather
4. `play_ambient` - Set scene music

### **Combat Start:**
1. `lookup_monster` - Get monster stats
2. `start_combat` - Initialize combat
3. `roll_initiative_tool` - Roll initiative
4. `load_battlefield` - Set positions
5. `play_ambient("combat")` - Combat music
6. `log_event("combat")` - Log combat start

### **During Combat Turn:**
1. `get_combat_status` - Check current state
2. `get_character_combat_stats` - Get PC stats (if needed)
3. `attack_tool` - Execute attack (auto-rolls)
4. `update_character_hp` - Update HP in Obsidian (real-time)
5. `move_creature` - Move on battlefield
6. `next_turn_tool` - Advance turn
7. `get_ai_action` - Enemy decision (on enemy turns)

### **Spell Casting:**
1. `lookup_spell` - Get spell details
2. `roll_saving_throw` - Targets make saves
3. `roll_dice` - Roll damage
4. `update_character_hp` - Apply damage/healing
5. `play_sfx` - Spell sound effect
6. `log_event("narration")` - Log spell cast

### **Quest Completion:**
1. `update_quest_status(..., "completed")` - Mark quest complete
2. `complete_quest` - Distribute rewards
3. `update_character_currency` - Add gold (via obsidian-sync)
4. `update_character_xp` - Add XP (via obsidian-sync)
5. `add_inventory_item` - Add items (via obsidian-sync)
6. `update_faction_reputation` - Auto-updated by complete_quest

### **Post-Combat:**
1. `end_combat_tool` - End combat
2. `update_character_xp` - Distribute XP
3. `update_character_currency` - Distribute coins
4. `add_inventory_item` - Add loot items
5. `add_weapon` / `add_armor` / `add_magic_item` - Add equipment
6. `log_event("combat")` - Log combat end

### **NPC Interaction:**
1. `create_npc` - If new NPC (auto-syncs to Obsidian)
2. `add_relationship` - Track relationships (auto-syncs)
3. `create_quest` - If quest given
4. `log_event("npc_interaction")` - Log interaction

---

## ✅ CRITICAL USAGE RULES

1. **NEVER roll dice manually** - Always use dice-roller tools
2. **NEVER invent stats** - Always use rules-database or sourcebooks
3. **ALWAYS update Obsidian HP** - After every damage/healing event
4. **ALWAYS use combat-engine** - For all combat encounters
5. **ALWAYS log major events** - Use session-recorder
6. **ALWAYS create NPCs in wiki** - When party meets new people (auto-syncs)
7. **ALWAYS complete quests properly** - Use complete_quest for auto-rewards
8. **ALWAYS check faction reputation** - When actions affect factions

---

**Total: 72 MCP Tools Across 10 Servers**

Every tool has a specific purpose. Use them consistently for accurate, tracked, and immersive gameplay! 🎲⚔️📖
