# Integration Quick Reference
## All 12 MCPs + Parallel Agents + DM Workflow

---

## 🎯 Quick Integration Cheatsheet

### Session Start (5 MCP calls)
```
1. session_recorder.start_session_log(campaign_name)
2. weather_calendar.get_current_date_time()
3. weather_calendar.get_current_weather()
4. music_ambience.play_ambient(scene="town")
5. obsidian_sync.get_party_status()
```

### Combat Start (7 MCP calls)
```
1. rules_database.lookup_monster(name)
2. music_ambience.play_ambient(scene="combat")
3. weather_calendar.get_current_weather()
4. dice_roller.roll_initiative(combatants)
5. combat_engine.start_combat()
6. session_recorder.log_event(type="combat")
7. knowledge_graph.add_entity(entity_id="combat_X", entity_type="event")
```

### Skill Check (4 MCP calls)
```
1. obsidian_sync.get_character_stats(character_id)
2. dice_roller.roll_dice(expression="1d20+modifier")
3. session_recorder.log_event(type="roll")
4. knowledge_graph.add_entity() [if important]
```

### Spell Cast (5 MCP calls)
```
1. rules_database.lookup_spell(spell_name)
2. obsidian_sync.use_spell_slot(character_id, level)
3. dice_roller.roll_dice(expression="damage_dice")
4. session_recorder.log_event(type="narration")
5. music_ambience.play_sfx("spell_X")
```

### Long Rest (4 MCP calls)
```
1. weather_calendar.long_rest()
2. obsidian_sync.restore_on_long_rest()
3. session_recorder.log_event(type="narration")
4. music_ambience.play_ambient(scene="peaceful")
```

### Travel (3 MCP calls)
```
1. weather_calendar.calculate_travel_time(distance, terrain, pace)
2. weather_calendar.advance_time(days=X, hours=Y)
3. music_ambience.play_ambient(scene="wilderness")
```

### NPC Interaction (4 MCP calls)
```
1. campaign_wiki.get_npc(npc_id)
2. knowledge_graph.get_entity_connections(entity_id=npc_id)
3. session_recorder.log_event(type="npc_interaction")
4. knowledge_graph.add_relationship(from_id="party", to_id=npc_id, type="spoke_with")
```

### Player Choice (4 MCP calls)
```
1. knowledge_graph.add_entity(entity_id="choice_X", entity_type="choice")
2. knowledge_graph.analyze_consequence_chain(choice_id)
3. session_recorder.log_event(type="choice")
4. knowledge_graph.add_relationship(from_id="choice_X", to_id="event_Y", type="leads_to")
```

---

## 🤖 Parallel Agent Integration

### Combat Turn (All 4 Agents + MCPs)

**AGENT 1: REFEREE**
```
MCPs Used:
- obsidian_sync.get_character_stats()
- obsidian_sync.check_raging()
- rules_database.lookup_monster()
- dice_roller.roll_attack()
- dice_roller.roll_dice()
- weather_calendar.get_current_weather()

Output: attack.json
```

**AGENT 2: NARRATOR**
```
MCPs Used:
- music_ambience.play_sfx()
- session_recorder.log_event()

Output: narration.txt
```

**AGENT 3: STATE_PATCHER**
```
MCPs Used:
- obsidian_sync.update_character_hp()
- obsidian_sync.deduct_rage_use()
- combat_engine.update_creature()
- knowledge_graph.add_entity()

Output: state_patch.json
```

**AGENT 4: QA_COMPLIANCE**
```
MCPs Used:
- (validation only, no MCP calls)

Output: validation.json
```

---

## 📊 Data Flow Map

```
USER COMMAND
    ↓
AI DM (Claude)
    ↓
┌───────────────────────────────────────────┐
│  Route to appropriate MCP(s)              │
├───────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────────┐  │
│  │  MCP Call   │ →  │  Data Retrieved │  │
│  └─────────────┘    └─────────────────┘  │
├───────────────────────────────────────────┤
│  Process with Parallel Agents (if combat) │
├───────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────────┐  │
│  │  MCP Update │ →  │  Data Written   │  │
│  └─────────────┘    └─────────────────┘  │
├───────────────────────────────────────────┤
│  Generate Response                        │
└───────────────────────────────────────────┘
    ↓
NARRATION + ASK + ACTIONS
```

---

## 🔗 Cross-MCP Connections

### Character Data Chain
```
Obsidian Sync MCP (source of truth)
    ↓
Combat Engine (reads stats)
    ↓
Dice Roller (uses modifiers)
    ↓
Obsidian Sync (writes updates)
```

### Event Logging Chain
```
Any Event Occurs
    ↓
Session Recorder (logs event)
    ↓
Knowledge Graph (creates entity/relationship)
    ↓
Campaign Wiki (updates quest/NPC status)
```

### Time & Weather Chain
```
Weather/Calendar (tracks time)
    ↓
Session Recorder (logs time changes)
    ↓
Obsidian Sync (updates timeline)
    ↓
Campaign Wiki (updates location/time context)
```

---

## 🎲 Common Workflow Scripts

### Use Python Integration Helpers
```python
from scripts.integration_helpers import mcp, session_start_workflow, combat_start_workflow

# Session start
session_start_workflow("Lost Mine of Phandelver")

# Combat
combat_start_workflow("Goblin", 5)

# Skill check
skill_check_workflow("eglath_bearkiller", "intimidation", 15)

# Long rest
long_rest_workflow(["eglath_bearkiller", "torgga_brawnanvil", "zephyr_sparkwhistle", "kraval_ironskull", "pip_cobblestone"])
```

---

## 🚨 Error Handling

### MCP Unavailable
```python
try:
    result = mcp.lookup_monster("Goblin")
except Exception as e:
    # Fallback: use default stats
    result = {"ac": 10, "hp": 10}
```

### Data Conflict
```python
# Obsidian is source of truth for:
# - Stats, features, weapons, resources
# Google Sheets (being phased out) for:
# - Inventory, currency (temporary)

# Always read from Obsidian first
stats = mcp.get_character_stats(char_id)
```

---

## 📈 Performance Tips

1. **Batch MCP calls** when possible
   ```python
   monsters = mcp.batch_lookup_monsters(["Goblin", "Orc", "Troll"])
   ```

2. **Cache frequent lookups**
   ```python
   # Monster stats don't change mid-session
   mcp.lookup_monster("Goblin")  # Cached after first call
   ```

3. **Parallel agent processing** (already implemented)
   - All 4 agents run simultaneously
   - <5 seconds per combat turn

---

## 🔍 Debugging Integration

### Check MCP Status
```bash
# List all running MCP servers
# (Cursor handles this automatically)
```

### View Integration Logs
```bash
tail -f logs/integration.log
```

### Test Single MCP
```python
from scripts.integration_helpers import mcp

# Test dice roller
print(mcp.roll_dice("1d20+5", "test roll"))

# Test character data
print(mcp.get_character_stats("eglath_bearkiller"))
```

---

## 📚 When to Use Each MCP

| If you need... | Use this MCP |
|----------------|--------------|
| Monster stats | `rules_database.lookup_monster()` |
| Spell details | `rules_database.lookup_spell()` |
| Condition effects | `rules_database.lookup_condition()` |
| Character stats | `obsidian_sync.get_character_stats()` |
| Update HP | `obsidian_sync.update_character_hp()` |
| Use spell slot | `obsidian_sync.use_spell_slot()` |
| Roll dice | `dice_roller.roll_dice()` |
| Roll attack | `dice_roller.roll_attack()` |
| Roll initiative | `dice_roller.roll_initiative()` |
| Log event | `session_recorder.log_event()` |
| Get date/time | `weather_calendar.get_current_date_time()` |
| Get weather | `weather_calendar.get_current_weather()` |
| Advance time | `weather_calendar.advance_time()` |
| Long rest | `weather_calendar.long_rest()` |
| Travel time | `weather_calendar.calculate_travel_time()` |
| NPC data | `campaign_wiki.get_npc()` |
| Quest data | `campaign_wiki.get_quest()` |
| Add entity | `knowledge_graph.add_entity()` |
| Add relationship | `knowledge_graph.add_relationship()` |
| Analyze consequences | `knowledge_graph.analyze_consequence_chain()` |
| Play music | `music_ambience.play_ambient()` |
| Play SFX | `music_ambience.play_sfx()` |
| Balanced encounter | `encounter_builder.build_encounter()` |
| Start combat | `combat_engine.start_combat()` |

---

## ✅ Integration Checklist

Before starting a session, verify:

- [ ] All 12 MCP servers configured in `.cursor/mcp.json`
- [ ] `CURRENT_STATE.json` exists and is valid
- [ ] `CAMPAIGN_EVENTS.json` exists
- [ ] `party_characters.json` is up-to-date
- [ ] Obsidian vault at correct path
- [ ] `integration_helpers.py` is accessible
- [ ] Parallel agent scripts are in `agents/` folder

---

## 🎉 You're Ready!

All 12 MCP servers are fully integrated with the parallel agent system and DM workflow.

**Start your session with:**
```python
from scripts.integration_helpers import session_start_workflow
session_start_workflow("Lost Mine of Phandelver")
```

**Or just tell the AI DM:**
```
"Start session for Lost Mine of Phandelver"
```

The AI will automatically route to the appropriate MCPs! 🎲✨



