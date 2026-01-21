# Choices and Consequences System

## Overview

The **Choices and Consequences System** is a comprehensive tracking system that records all significant player choices, their immediate outcomes, and their long-term effects on the campaign and beyond. This ensures that decisions made early in the campaign continue to influence events, NPC relationships, and story outcomes throughout the entire campaign and even into future campaigns.

## File Location

**Primary File:**
- `C:\DnD\Campaigns\<campaign>\saves\CAMPAIGN_EVENTS.json`

**Example:**
- `C:\DnD\Campaigns\Phandelver\saves\CAMPAIGN_EVENTS.json`

## Enhanced File Structure

```json
{
  "campaign": "Phandelver",
  "last_updated": "2026-01-13T00:00:00.0000000-05:00",
  "campaign_start_date": "2026-01-02T00:00:00.0000000-05:00",
  
  "events": [
    {
      "id": "unique_event_id",
      "timestamp": "ISO timestamp",
      "chapter": 2,
      "location": "location_name",
      "type": "story_event|quest|encounter|choice|milestone",
      "title": "Event Title",
      "description": "Detailed description of what happened",
      "participants": ["Character1", "Character2"],
      "choices": [
        {
          "action": "What the party chose to do",
          "consequence": "Immediate result",
          "long_term_impact": "How this affects future events",
          "severity": "minor|moderate|major|critical",
          "affected_areas": ["npc_relationships", "quest_progression", "world_state"]
        }
      ],
      "outcomes": {
        "immediate": {},
        "short_term": {},
        "long_term": {}
      },
      "tags": ["rescue", "moral_choice", "resource_allocation"]
    }
  ],
  
  "choices_log": [
    {
      "id": "choice_unique_id",
      "timestamp": "ISO timestamp",
      "chapter": 2,
      "location": "location_name",
      "choice_type": "moral|tactical|social|resource|quest",
      "choice": "What was chosen",
      "alternatives": ["What could have been chosen instead"],
      "immediate_impact": "What happened right away",
      "long_term_consequences": [
        {
          "consequence_id": "consequence_ref",
          "description": "How this choice affects future events",
          "severity": "minor|moderate|major|critical",
          "manifestation_timing": "immediate|short_term|long_term|future_campaign",
          "affected_entities": ["NPC names", "locations", "factions"]
        }
      ],
      "reversibility": "reversible|partially_reversible|irreversible",
      "cross_campaign_impact": false
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
  },
  
  "npcs": {
    "npc_name": {
      "name": "NPC Name",
      "location": "Current location",
      "relationship": "grateful|hostile|neutral|positive|negative|trusted|feared",
      "relationship_level": 0,
      "status": "alive|dead|missing|imprisoned",
      "interactions": [
        {
          "event_id": "reference to event",
          "timestamp": "ISO timestamp",
          "type": "rescue|quest|trade|combat|social|gift",
          "outcome": "what happened",
          "relationship_change": "+2|-1|etc",
          "choice_impact": "How player choices affected this interaction"
        }
      ],
      "memory": [
        "Things the NPC remembers about the party",
        "Specific actions that affected their opinion"
      ],
      "notes": "Additional context",
      "long_term_effects": [
        {
          "effect": "How this NPC relationship affects future events",
          "trigger": "What would activate this effect"
        }
      ]
    }
  },
  
  "quests": {
    "quest_id": {
      "id": "quest_id",
      "giver": "NPC name",
      "status": "active|completed|failed|abandoned",
      "objective": "What needs to be done",
      "reward": "What the reward is",
      "completion_notes": "How it was completed",
      "choices_made": [
        {
          "choice_id": "reference to choice",
          "impact": "How this choice affected quest completion"
        }
      ],
      "consequences": [
        "How completing/failing this quest affects the world"
      ]
    }
  },
  
  "factions": {
    "faction_name": {
      "name": "Faction Name",
      "relationship": "allied|friendly|neutral|unfriendly|hostile",
      "reputation": 0,
      "membership": {
        "characters": ["Character names"],
        "rank": "rank_name",
        "benefits": ["list of benefits"]
      },
      "interactions": [
        {
          "event_id": "reference to event",
          "impact": "How this affected faction relationship"
        }
      ],
      "long_term_effects": [
        "How faction relationship affects future events"
      ]
    }
  },
  
  "world_state": {
    "locations": {
      "location_name": {
        "status": "cleared|occupied|destroyed|changed",
        "changes": ["What changed about this location"],
        "affected_by_choices": ["choice_ids that affected this location"]
      }
    },
    "ongoing_effects": [
      {
        "effect": "Description of ongoing world effect",
        "origin": "choice_id or event_id",
        "duration": "permanent|temporary|until_condition"
      }
    ]
  },
  
  "cross_campaign_effects": [
    {
      "id": "cross_campaign_effect_id",
      "origin_campaign": "Phandelver",
      "origin_choice": "choice_id",
      "effect": "What carries over to other campaigns",
      "applicable_campaigns": ["all", "specific_campaign_names"],
      "type": "reputation|relationship|resource|knowledge|item"
    }
  ]
}
```

## Key Features

### 1. Choice Tracking
- **Every significant choice** is logged with:
  - What was chosen
  - What alternatives existed
  - Immediate impact
  - Long-term consequences
  - Severity level
  - Reversibility

### 2. Consequence Tracking
- **Consequences are tracked separately** from events:
  - Status (active, resolved, ongoing, escalated)
  - Severity (minor, moderate, major, critical)
  - What choice/event caused it
  - How it manifests in the world
  - What entities are affected
  - Timeline of how it develops

### 3. Long-Term Effects
- **NPC Relationships**: Track relationship levels and how they change over time
- **Faction Reputation**: Track standing with organizations
- **World State**: Track how locations and the world change
- **Cross-Campaign Effects**: Track effects that carry over to other campaigns

### 4. Consequence Manifestation
- **Immediate**: Happens right away
- **Short-term**: Happens within days/weeks
- **Long-term**: Happens within months/years
- **Future Campaign**: Effects that carry to other campaigns

## Usage Guidelines

### When to Log a Choice

Log a choice when it:
- Affects NPC relationships
- Changes the world state
- Has moral implications
- Allocates resources (time, money, items)
- Affects quest progression
- Creates or resolves consequences
- Has potential long-term impact

### When to Create a Consequence

Create a consequence when:
- A choice has delayed or ongoing effects
- Multiple choices contribute to an outcome
- An effect will manifest later in the campaign
- An effect might carry to future campaigns

### How to Reference Past Choices

**Before any significant interaction:**
1. Load `CAMPAIGN_EVENTS.json`
2. Check `choices_log` for relevant past choices
3. Check `consequences` for active consequences
4. Check `npcs` for relationship history
5. Check `factions` for reputation
6. Use this context to inform current events

## Example: Tracking a Choice with Long-Term Consequences

```json
{
  "choices_log": [
    {
      "id": "destroy_forge_of_spells",
      "timestamp": "2026-01-08T00:15:00.0000000-05:00",
      "chapter": 4,
      "location": "wave_echo_cave_w15",
      "choice_type": "tactical|moral",
      "choice": "Destroyed the Forge of Spells to prevent the Black Spider from using it",
      "alternatives": [
        "Leave the forge intact",
        "Attempt to capture and use the forge",
        "Destroy only the brazier"
      ],
      "immediate_impact": "Forge of Spells destroyed, green flame extinguished, magical power lost",
      "long_term_consequences": [
        {
          "consequence_id": "forge_destruction_impact",
          "description": "Phandalin loses potential source of magical items and economic growth",
          "severity": "major",
          "manifestation_timing": "long_term",
          "affected_entities": ["Phandalin", "Gundren Rockseeker", "Mining operations"]
        }
      ],
      "reversibility": "irreversible",
      "cross_campaign_impact": true
    }
  ],
  "consequences": {
    "forge_destruction_impact": {
      "id": "forge_destruction_impact",
      "status": "active",
      "severity": "major",
      "origin_choice": "destroy_forge_of_spells",
      "origin_event": "w15_forge_destruction",
      "manifestation": "Phandalin's economic potential reduced, no magical item production possible",
      "factors": ["forge_destroyed", "magical_power_lost"],
      "affected_entities": {
        "npcs": ["Gundren Rockseeker"],
        "locations": ["Phandalin", "Wave Echo Cave"],
        "factions": [],
        "quests": []
      },
      "future_impact": "Future campaigns in Phandalin will not have access to the Forge of Spells. Economic development may be slower. Gundren may express disappointment.",
      "resolution_conditions": "Cannot be resolved - forge is permanently destroyed",
      "cross_campaign": true,
      "timeline": [
        {
          "timestamp": "2026-01-08T00:15:00.0000000-05:00",
          "event": "Forge destroyed",
          "severity_change": "unchanged"
        }
      ]
    }
  }
}
```

## Integration with Gameplay

### REFEREE / NARRATOR / STATE_PATCHER

All agents should:
1. **Load CAMPAIGN_EVENTS.json** at session start
2. **Check choices_log** before presenting options
3. **Reference consequences** when determining outcomes
4. **Update choices_log** when players make significant decisions
5. **Create/update consequences** when choices have delayed effects
6. **Check NPC relationships** before interactions
7. **Reference faction reputation** when dealing with organizations

### Automatic Tracking

The system automatically tracks:
- Encounter completions
- Quest progress
- Location discoveries
- Major milestones

### Manual Updates

Manual updates should be made for:
- Significant player choices
- Moral decisions
- Resource allocation
- Relationship changes
- Consequence creation
- Cross-campaign effects

## Best Practices

1. **Be Specific**: Include enough detail to understand context months later
2. **Track Severity**: Mark how significant each choice/consequence is
3. **Link Events**: Reference related choices and consequences
4. **Timeline Everything**: Use ISO timestamps for chronological tracking
5. **Document Alternatives**: Note what could have been chosen instead
6. **Track Manifestation**: Note when consequences will appear
7. **Cross-Reference**: Link choices to consequences and events
8. **Update Status**: Keep consequence status current (active/resolved/ongoing)

## Querying the System

### Find All Choices Affecting an NPC
```json
Search choices_log where affected_entities contains "NPC_name"
```

### Find All Active Consequences
```json
Filter consequences where status == "active"
```

### Find Choices with Long-Term Impact
```json
Filter choices_log where long_term_consequences.length > 0
```

### Find Cross-Campaign Effects
```json
Filter cross_campaign_effects where applicable_campaigns contains "target_campaign"
```

## Scripts and Tools

- **auto_event_tracker.ps1**: Automatically tracks encounters and quests
- **Manual updates**: Edit CAMPAIGN_EVENTS.json directly or use STATE_PATCHER patches

## Future Enhancements

Potential additions:
- Consequence severity escalation over time
- Choice dependency chains (choice A enables choice B)
- Reputation decay over time
- Faction relationship modifiers
- World state change tracking
- Cross-campaign effect propagation































