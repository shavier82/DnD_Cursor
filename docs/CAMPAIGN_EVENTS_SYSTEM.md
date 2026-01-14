# Campaign Events System

## Overview

The Campaign Events System tracks story events, choices, NPC relationships, and consequences across the campaign. This ensures continuity and that past decisions impact future events.

**This is the static JSON file that keeps track of things that happen, choices that are made, and their long-lasting effects on the campaign and beyond.** Every significant choice is logged, and consequences are tracked separately to ensure that decisions made early in the campaign continue to influence events throughout the entire campaign and even into future campaigns.

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
      "id": "consequence_unique_id",
      "status": "active|resolved|ongoing|escalated",
      "severity": "minor|moderate|major|critical",
      "origin_choice": "choice_id_that_caused_this",
      "origin_event": "event_id_that_caused_this",
      "manifestation": "How this consequence appears in the world",
      "factors": ["list of contributing factors"],
      "affected_entities": {
        "npcs": ["NPC names"],
        "locations": ["location names"],
        "factions": ["faction names"],
        "quests": ["quest_ids"]
      },
      "future_impact": "How this affects future events",
      "resolution_conditions": "What would resolve or change this consequence",
      "cross_campaign": false,
      "timeline": [
        {
          "timestamp": "ISO timestamp",
          "event": "What happened related to this consequence",
          "severity_change": "increased|decreased|unchanged"
        }
      ]
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

### Choices (CRITICAL - Long-Lasting Effects)
- **Every significant player choice MUST be logged** in `choices_log` with:
  - What was chosen
  - What alternatives existed
  - Immediate impact
  - Long-term consequences (if any)
  - Affected entities (NPCs, locations, factions)
  - Severity level (minor, moderate, major, critical)
  - Cross-campaign impact flag (if applicable)
- **When to log a choice:**
  - Affects NPC relationships
  - Changes world state
  - Has moral implications
  - Allocates resources (time, money, items)
  - Affects quest progression
  - Creates or resolves consequences
  - Has potential long-term impact
- **Player decisions that affect NPCs**
- **Moral choices**
- **Quest acceptance/completion**
- **Resource allocation decisions**
- **Relationship-building actions**
- **Tactical decisions with long-term implications**

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
1. **Load CAMPAIGN_EVENTS.json** at session start (MANDATORY)
2. **Check NPC relationships** before interactions
3. **Reference past choices** when making decisions (MANDATORY - check choices_log)
4. **Check active consequences** before determining outcomes (MANDATORY - check consequences)
5. **Update events** when significant story moments occur
6. **Track consequences** of player actions (MANDATORY - create consequences for significant choices)
7. **Log significant choices** in choices_log (MANDATORY - every significant choice must be logged)
8. **Ensure choices have long-lasting effects** (MANDATORY - consequences must manifest appropriately)

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

## Automatic Event Tracking

The system automatically tracks many events from state changes without manual intervention:

- **Encounter completions** - Automatically creates events when encounters are completed
- **Quest item discoveries** - Automatically updates quest status when quest items are discovered
- **Quest location arrivals** - Automatically tracks progress when party arrives at quest locations
- **Major milestones** - Detects and records significant state changes

**Script:** `C:\DnD\DnD_Cursor\scripts\auto_event_tracker.ps1`

**Integration:** Runs automatically after each turn merge (`merge_outputs.ps1`)

**Reference:** See `C:\DnD\DnD_Cursor\docs\AUTO_EVENT_TRACKING.md` for detailed documentation on what gets tracked automatically and how it works.

## Choices and Consequences Tracking (CRITICAL)

### Purpose
**This system ensures that choices made by players have long-lasting effects on the campaign and beyond.** Every significant choice is logged, and consequences are tracked separately to ensure continuity and that past decisions impact future events.

### Key Principles
1. **Every significant choice MUST be logged** - Don't skip logging important decisions
2. **Consequences MUST be created** - When a choice has delayed effects, create a consequence entry
3. **NPCs remember** - Relationship history tracks how choices affected NPCs
4. **World state changes** - Locations and factions are affected by choices
5. **Consequences manifest** - Effects appear at appropriate times (immediate, short-term, long-term, future campaign)
6. **Cross-campaign effects** - Some choices affect future campaigns

### Choice Logging Format
When logging a choice, include:
- **What was chosen** - Clear description of the decision
- **Alternatives** - What other options existed
- **Immediate impact** - What happened right away
- **Long-term consequences** - How this affects future events
- **Affected entities** - NPCs, locations, factions affected
- **Severity** - minor, moderate, major, or critical
- **Cross-campaign flag** - Whether this affects other campaigns

### Consequence Creation Format
When creating a consequence, include:
- **Status** - active, resolved, ongoing, or escalated
- **Severity** - minor, moderate, major, or critical
- **Origin** - Which choice/event caused it
- **Manifestation** - How it appears in the world
- **Affected entities** - NPCs, locations, factions, quests
- **Future impact** - How this affects future events
- **Timeline** - Track how the consequence develops over time

### Ensuring Long-Lasting Effects
To ensure choices have long-lasting effects:
1. **Always log significant choices** - Don't skip logging important decisions
2. **Create consequences** - When a choice has delayed effects, create a consequence entry
3. **Update NPC relationships** - Track how choices affect how NPCs view the party
4. **Reference past choices** - Check past choices before presenting options
5. **Manifest consequences** - Have consequences appear later in the campaign
6. **Cross-reference** - Link related choices and consequences together

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

