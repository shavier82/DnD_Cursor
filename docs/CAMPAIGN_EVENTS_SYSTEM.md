# Campaign Events System

## Overview

The Campaign Events System tracks story events, choices, NPC relationships, and consequences across the campaign. This ensures continuity and that past decisions impact future events.

## File Location

**Campaign Events File:**
- `C:\DnD\Campaigns\<campaign>\saves\CAMPAIGN_EVENTS.json`

**Example:**
- `C:\DnD\Campaigns\Phandelver\saves\CAMPAIGN_EVENTS.json`

## File Structure

```json
{
  "campaign": "Phandelver",
  "last_updated": "2026-01-03T11:09:23.5401796-05:00",
  "events": [
    {
      "id": "unique_event_id",
      "timestamp": "ISO timestamp",
      "chapter": 2,
      "location": "location_name",
      "type": "story_event|quest|encounter|choice",
      "title": "Event Title",
      "description": "Detailed description of what happened",
      "participants": ["Character1", "Character2"],
      "choices": [
        {
          "action": "What the party did",
          "consequence": "What resulted from this action"
        }
      ],
      "outcomes": {
        "key": "value"
      }
    }
  ],
  "npcs": {
    "npc_name": {
      "name": "NPC Name",
      "location": "Current location",
      "relationship": "positive|neutral|negative|grateful|hostile",
      "status": "alive|dead|missing",
      "interactions": [
        {
          "event_id": "reference to event",
          "type": "rescue|quest|trade|combat",
          "outcome": "what happened"
        }
      ],
      "notes": "Additional context"
    }
  },
  "quests": {
    "quest_id": {
      "id": "quest_id",
      "giver": "NPC name",
      "status": "active|completed|failed",
      "objective": "What needs to be done",
      "reward": "What the reward is",
      "completion_notes": "How it was completed"
    }
  },
  "choices_log": [
    {
      "timestamp": "ISO timestamp",
      "chapter": 2,
      "location": "location_name",
      "choice": "What was chosen",
      "impact": "What this choice affected"
    }
  ],
  "consequences": {
    "consequence_key": {
      "status": "current status",
      "level": "severity or level",
      "factors": ["list of contributing factors"],
      "future_impact": "How this affects future events"
    }
  }
}
```

## When to Update

### Story Events
- Major NPC interactions
- Rescues or saves
- Discoveries of important information
- Character deaths or significant changes
- Location discoveries

### Choices
- Player decisions that affect NPCs
- Moral choices
- Quest acceptance/completion
- Resource allocation decisions
- Relationship-building actions

### NPC Relationships
- First meeting
- Significant interactions
- Relationship changes (positive/negative)
- Quest giving/completion
- Gifts or favors

### Quests
- Quest given
- Quest progress
- Quest completion
- Quest failure

## Usage in Play Mode

### REFEREE / NARRATOR / STATE_PATCHER

All agents should:
1. **Load CAMPAIGN_EVENTS.json** at session start
2. **Check NPC relationships** before interactions
3. **Reference past choices** when making decisions
4. **Update events** when significant story moments occur
5. **Track consequences** of player actions

### Example: NPC Interaction

**Before interacting with Mirna Dendrar:**
1. Load `CAMPAIGN_EVENTS.json`
2. Check `npcs.mirna_dendrar.relationship` → "grateful"
3. Check `npcs.mirna_dendrar.interactions` → See past events
4. Reference `quests.mirna_necklace.status` → "completed"
5. Use this context to inform dialogue and reactions

### Example: Quest Completion

**When returning necklace to Mirna:**
1. Check `quests.mirna_necklace.status` → "completed"
2. Check `npcs.mirna_dendrar.relationship` → "grateful"
3. Reference `events.mirna_necklace_quest.outcomes.mirna_expects_return` → true
4. Update event with completion details
5. Update NPC relationship if changed

## Best Practices

1. **Be Specific**: Include enough detail to understand context later
2. **Track Consequences**: Always note how choices affect future events
3. **Update Relationships**: Track NPC relationship changes
4. **Reference Events**: Link related events together
5. **Timestamp Everything**: Use ISO timestamps for chronological tracking
6. **Document Choices**: Log all significant player decisions

## Example Event Entry

```json
{
  "id": "redbrand_hideout_mirna_husband",
  "timestamp": "2026-01-02T18:00:00.0000000-05:00",
  "chapter": 2,
  "location": "redbrand_hideout",
  "type": "story_event",
  "title": "Recovery of Mirna Dendrar's Husband",
  "description": "Party discovered and recovered the remains of Mirna Dendrar's husband in the Redbrand hideout. The husband was killed by the Redbrands.",
  "participants": ["Brevin", "Ergath", "Torgga", "Vandross"],
  "choices": [
    {
      "action": "Recovered husband's remains",
      "consequence": "Able to return remains to Mirna Dendrar"
    },
    {
      "action": "Found husband's necklace",
      "consequence": "Returned necklace to Mirna, establishing trust"
    }
  ],
  "outcomes": {
    "mirna_relationship": "grateful",
    "mirna_quest_given": true,
    "husband_remains_recovered": true
  }
}
```

## Integration with CURRENT_STATE.json

- **CURRENT_STATE.json**: Tracks current scene, combat, encounters, gates
- **CAMPAIGN_EVENTS.json**: Tracks story context, relationships, choices, consequences
- Both files work together to provide complete campaign context

## Manual Updates

Events can be manually updated by editing the JSON file directly, or through STATE_PATCHER patches:

```json
{
  "op": "add",
  "path": "/events/-",
  "value": {
    "id": "new_event_id",
    "timestamp": "2026-01-03T12:00:00.0000000-05:00",
    "chapter": 3,
    "location": "thundertree",
    "type": "story_event",
    "title": "Event Title",
    "description": "Event description",
    "participants": ["Brevin", "Ergath", "Torgga", "Vandross"],
    "choices": [],
    "outcomes": {}
  }
}
```

