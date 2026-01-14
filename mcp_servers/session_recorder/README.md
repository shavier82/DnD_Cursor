# 📝 Session Logger & Event Tracker MCP Server

**Logs text-based D&D gameplay, extracts events, and updates campaign state.**

---

## Features

- 📝 **Session Logging** - Record gameplay as it happens (text-based)
- 🏷️ **Event Tagging** - Categorize events (narration, choices, rolls, combat)
- 🤖 **Event Extraction** - AI-powered structured data extraction
- 💾 **Auto-Update** - Writes directly to `CAMPAIGN_EVENTS.json`
- 📊 **Session Summaries** - Generate readable session reports

---

## Installation

```bash
pip install mcp
```

**No additional dependencies required!** Pure Python, lightweight, fast.

---

## Usage

### 1. Start Session Logging
```python
start_session_log(
    campaign_name="WaterdeepDragonHeist",
    session_title="Chapter 5 - Investigation"  # Optional
)
# Returns: { "success": true, "session_id": "session_20260113_140000" }
```

### 2. Log Events During Gameplay
```python
# Log narration
log_event(
    event_type="narration",
    content="You enter the Sleeping Giant tavern. The room is dimly lit..."
)

# Log player choice
log_event(
    event_type="choice",
    content="Brevin decides to approach the bartender",
    metadata={"character": "Brevin", "choice": "approach_bartender"}
)

# Log dice roll
log_event(
    event_type="roll",
    content="Torgga rolls Persuasion",
    metadata={"character": "Torgga", "skill": "Persuasion", "result": 20, "outcome": "critical_success"}
)

# Log combat
log_event(
    event_type="combat",
    content="Bandits attack! Initiative rolled."
)

# Log NPC interaction
log_event(
    event_type="npc_interaction",
    content="The bartender reveals the Redbrands meet in Tresendar Manor cellar",
    metadata={"npc": "Bartender", "relationship": "friendly"}
)

# Log discovery
log_event(
    event_type="discovery",
    content="Party finds a silver amulet with an eye symbol",
    metadata={"item": "Silver Amulet of Scrying", "location": "Sleeping Giant"}
)

# Log gate passed
log_event(
    event_type="gate",
    content="Brevin passes Perception DC 15 - notices cloaked figure",
    metadata={"gate": "perception_dc15_cloaked_figure", "passed": True}
)

# Log consequence
log_event(
    event_type="consequence",
    content="Party's actions alert the Redbrands - they increase patrols",
    metadata={"consequence_of": "loud_tavern_fight", "severity": "medium"}
)
```

### 3. Stop Logging
```python
stop_session_log()
# Returns: { "success": true, "total_events": 47, "duration_minutes": 180 }
```

### 4. Extract Events (AI Analysis)
```python
extract_events(
    session_id="session_20260113_140000",
    campaign_name="WaterdeepDragonHeist"
)
# Returns: Analysis prompt for AI to extract structured events
```

### 5. Update Campaign Events
```python
update_campaign_events(
    campaign_name="WaterdeepDragonHeist",
    events=[
        {
            "timestamp": "2026-01-13T15:30:00",
            "event_type": "encounter",
            "description": "Party confronted bandits in tavern",
            "location": "Sleeping Giant",
            "participants": ["Bartender", "Cloaked Figure", "4 Bandits"],
            "outcome": "Victory - learned about Tresendar Manor",
            "significance": "high"
        }
    ]
)
# Returns: { "success": true, "events_added": 1, "total_events": 48 }
```

---

## Event Types

| Type | Description | Example |
|------|-------------|---------|
| `narration` | DM narration/scene setting | "You enter a dark cavern..." |
| `choice` | Player decision/action | "Brevin decides to sneak past" |
| `roll` | Dice roll and outcome | "Torgga rolls Athletics: 18" |
| `combat` | Combat-related events | "Goblin attacks Vandross" |
| `npc_interaction` | Conversations with NPCs | "Sildar reveals quest information" |
| `discovery` | Finding items/information | "Party discovers secret door" |
| `gate` | Information gate pass/fail | "Perception DC 15: PASS" |
| `consequence` | Result of player actions | "Town guards become hostile" |

---

## Workflow

### Standard Session Flow

1. **Session Start:**
   ```python
   start_session_log(campaign_name="Phandelver")
   ```

2. **During Gameplay:** AI automatically logs events as they happen
   - Narration blocks → `log_event("narration", ...)`
   - Player actions → `log_event("choice", ...)`
   - Dice rolls → `log_event("roll", ...)`
   - Combat → `log_event("combat", ...)`
   - NPC talks → `log_event("npc_interaction", ...)`

3. **Session End:**
   ```python
   stop_session_log()
   ```

4. **Post-Session:** AI extracts structured events
   ```python
   extract_events(session_id="...", campaign_name="...")
   ```

5. **Auto-Update:** AI updates `CAMPAIGN_EVENTS.json`
   ```python
   update_campaign_events(campaign_name="...", events=[...])
   ```

---

## File Locations

**Session Logs:** `C:\DnD\DnD_Cursor\session_logs\`
- `session_YYYYMMDD_HHMMSS.jsonl` - Session event logs (JSON Lines format)

**Campaign Updates:** `C:\DnD\Campaigns\<campaign>\saves\CAMPAIGN_EVENTS.json`

**Backups:** `CAMPAIGN_EVENTS_backup_YYYYMMDD_HHMMSS.json` (auto-created)

---

## Event Schema

**Session Log Entry:**
```json
{
  "type": "narration|choice|roll|combat|npc_interaction|discovery|gate|consequence",
  "timestamp": "2026-01-13T15:30:00",
  "content": "Text description of the event",
  "metadata": {
    "character": "Brevin",
    "custom_field": "value"
  }
}
```

**Campaign Event (extracted):**
```json
{
  "timestamp": "2026-01-13T15:30:00",
  "event_type": "encounter|choice|discovery|consequence|gate",
  "description": "What happened",
  "location": "Where it happened",
  "participants": ["NPC1", "NPC2"],
  "outcome": "Result of the event",
  "gates_passed": ["gate_name"],
  "significance": "high|medium|low"
}
```

---

## Integration with DM Workflow

**The AI DM will automatically:**
1. Start session logging when gameplay begins
2. Log all narration, choices, and events silently
3. Stop logging when session ends
4. Extract structured events from the log
5. Update `CAMPAIGN_EVENTS.json` automatically

**You don't need to call these tools manually** - the AI handles it transparently!

---

## Tips

**For Best Results:**
- Let the AI log events automatically during gameplay
- Review extracted events before finalizing (AI will show you)
- Use meaningful metadata for complex events
- Tag significant choices and consequences explicitly

**Session Log Format:**
- JSON Lines (`.jsonl`) - one event per line
- Easy to parse, stream, and search
- Human-readable with any text editor

---

## Advanced: Manual Session Review

**List all sessions:**
```python
list_session_logs()
# Returns: List of all sessions with metadata

list_session_logs(campaign_name="Phandelver")
# Returns: Only Phandelver sessions
```

**Check session status:**
```python
get_session_status()
# Returns: { "active": true, "session_id": "...", "events_logged": 47 }
```

---

**Status:** ✅ Ready for text-based session logging!
