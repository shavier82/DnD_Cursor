# MCP Session Recorder Quick Reference

**Purpose:** Log gameplay sessions, track events, and automatically update `CAMPAIGN_EVENTS.json`

---

## Core Functions

### 1. Start Session Logging
```python
start_session_log(campaign_name, session_title=None)
```
- **campaign_name**: Campaign folder name (e.g., "Phandelver", "Dragonheist")
- **session_title**: Optional custom title (defaults to "Session YYYY-MM-DD")
- **Returns:** Session ID, log file path
- **Usage:** Call at session start (optional - only if you want detailed session tracking)

### 2. Log Event
```python
log_event(event_type, content, metadata={})
```
- **event_type:** One of:
  - `narration` - Scene descriptions, DM narration
  - `choice` - Player decisions and choices
  - `roll` - Dice roll results
  - `combat` - Combat actions and outcomes
  - `npc_interaction` - NPC conversations and interactions
  - `discovery` - New information, clues, or secrets revealed
  - `gate` - Gate passed (perception check, investigation, etc.)
  - `consequence` - Consequence of past choice manifesting
- **content:** Text description of the event
- **metadata:** Optional dict with additional data
  - Examples: `{"character": "Brevin", "dc": 15, "success": true}`
  - Examples: `{"npc": "Gundren", "location": "Wave Echo Cave"}`

### 3. Stop Session Logging
```python
stop_session_log()
```
- Stops current logging session
- Returns summary (events logged, duration)

### 4. Get Session Status
```python
get_session_status()
```
- Check if logging is active
- Returns: session_id, campaign, duration, events_logged

### 5. List Session Logs
```python
list_session_logs(campaign_name=None)
```
- List all session logs, optionally filtered by campaign
- Returns: Array of session log files with metadata

### 6. Extract Events (Advanced)
```python
extract_events(session_id, campaign_name)
```
- Extract structured events from a session log
- Useful for post-session analysis

### 7. Update Campaign Events (Advanced)
```python
update_campaign_events(campaign_name, events)
```
- Add events to `CAMPAIGN_EVENTS.json`
- Usually called automatically after session ends

---

## Typical Session Workflow

### Option 1: Manual Logging (Full Control)
```python
# Start of session
start_session_log("Phandelver", "Chapter 3 - Wave Echo Cave")

# During session
log_event("narration", "The party enters the echoing cavern...")
log_event("choice", "Players chose to investigate the left tunnel", 
          {"choice_id": "cave_fork", "location": "Wave Echo Cave"})
log_event("roll", "Brevin rolls Stealth: 22 (1d20+8=14+8)", 
          {"character": "Brevin", "check": "Stealth", "result": 22})
log_event("gate", "Brevin passes DC 15 Perception check", 
          {"gate_name": "spot_ambush", "dc": 15})
log_event("discovery", "Brevin spots hidden goblins in the shadows")
log_event("combat", "Initiative rolled - Brevin: 18, Goblins: 12")

# End of session
stop_session_log()
```

### Option 2: No Logging (Default)
- Just play naturally
- Session recorder is completely optional
- Use only when you want detailed session tracking

---

## When to Use Session Logging

**Use session logging when:**
- Running a long, story-heavy campaign
- Tracking complex political intrigue
- Recording session for later transcription
- Want automatic event extraction for CAMPAIGN_EVENTS.json

**Skip session logging when:**
- One-shot adventures
- Combat-heavy sessions
- Quick dungeon crawls
- User prefers minimal overhead

---

## Integration with CAMPAIGN_EVENTS.json

Session logs can be automatically parsed to update `CAMPAIGN_EVENTS.json`:

1. Session ends: `stop_session_log()`
2. Extract events: `extract_events(session_id, campaign_name)`
3. Update campaign: `update_campaign_events(campaign_name, events)`

This creates a persistent record of choices, consequences, and story developments.

---

## File Locations

- **Session logs:** `C:\DnD\DnD_Cursor\session_logs\session_YYYYMMDD_HHMMSS.jsonl`
- **Format:** JSON Lines (one JSON object per line)
- **Campaign events:** `C:\DnD\Campaigns\<campaign>\saves\CAMPAIGN_EVENTS.json`

---

## Best Practices

1. **Log significant events only** - Don't log every dice roll, focus on story beats
2. **Use metadata effectively** - Include character names, DCs, locations
3. **Log choices immediately** - Capture player decisions as they happen
4. **Log consequences when they manifest** - Track long-term choice effects
5. **Stop logging at session end** - Ensures proper file closure

---

## Error Handling

- **No active session:** Returns error if you try to log without starting session
- **Invalid event type:** Must be one of 7 valid types
- **Duplicate start:** Can't start new session while one is active (must stop first)

---

## Example Session Log Entry

```json
{
  "timestamp": "2026-01-13T14:23:45.123456",
  "event_type": "choice",
  "content": "Players chose to trust Gundren and follow him to Wave Echo Cave",
  "metadata": {
    "choice_id": "trust_gundren",
    "npc": "Gundren Rockseeker",
    "location": "Phandalin",
    "consequence_hook": "gundren_betrayal_possible"
  }
}
```

---

## Quick Command Reference

```python
# Start
start_session_log("Phandelver")

# Log
log_event("narration", "Description...")
log_event("choice", "Decision...", {"choice_id": "..."})
log_event("roll", "Result...", {"character": "...", "dc": 15})
log_event("gate", "Gate passed", {"gate_name": "..."})
log_event("discovery", "New information...")
log_event("npc_interaction", "NPC conversation...")
log_event("combat", "Combat action...")
log_event("consequence", "Past choice manifests...")

# Stop
stop_session_log()

# Status
get_session_status()

# List logs
list_session_logs("Phandelver")
```

---

**Remember: Session logging is OPTIONAL. Use it when it adds value to your campaign tracking!**
