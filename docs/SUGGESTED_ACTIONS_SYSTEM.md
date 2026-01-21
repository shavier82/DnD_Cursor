# Suggested Actions System

## Overview

The Suggested Actions System automatically generates actionable suggestions for players when entering locations or scenes. This provides immediate guidance on available options without requiring players to ask "what can I do?"

## When Suggested Actions Are Generated

Suggested actions are automatically generated when:
- **Entering a new location** (e.g., moving to W5: Assayers' Office)
- **Entering a new scene** (transitioning between areas)
- **Completing an action that opens new options** (e.g., defeating enemies unlocks exploration)

## How It Works

### NARRATOR Agent Responsibility

When the NARRATOR agent processes a location entry, it MUST:
1. **Load the location card** from the appropriate chapter pack
2. **Parse the card** for actionable elements:
   - Locked containers (chests, doors, strongboxes)
   - Gates requiring checks (from `mechanics` field)
   - Treasure/loot to search for
   - Items to examine (records, texts, objects)
   - Nearby areas to explore
3. **Generate suggested_actions array** with formatted action strings
4. **Include requirements** (tools, DCs, skills) when applicable

### Location Card Parsing

The NARRATOR agent extracts actionable elements from location cards:

**From `boxed_text`:**
- Locked containers: "locked iron strongbox", "locked chest", "locked door"
- Tool requirements: "requiring thieves' tools", "requiring [tool]"
- DC checks: "DC 20 Dexterity check", "DC 15 Perception check"
- Treasure mentions: "Treasure.", "contains [coins/items]"
- Examination items: "examine", "read [language]", "inspect"
- Area references: "lead to W6", "entrance to H1", "passage to A3"

**From `mechanics` field:**
- Gates requiring checks: Parsed from JSON gates array
- DC and ability/skill combinations
- Special requirements or notes

### Action Format

Each suggested action is a plain text string that:
- Describes the action clearly
- Includes requirements in parentheses when applicable
- Uses consistent formatting

**Examples:**
- `"Attempt to pick the lock (Requires thieves' tools and a DC 20 Dexterity check)"`
- `"Search the room thoroughly"`
- `"Examine the old records (if anyone can read Dwarvish)"`
- `"Continue exploring (move to W6)"`
- `"Make a DC 15 Wisdom (Perception) check to spot hidden trap"`

## Output Integration

### NARRATOR Output Schema

```json
{
  "agent_role": "NARRATOR",
  "blocked": false,
  "narration": "You push open the door and step into what was once an office...",
  "suggested_actions": [
    "Attempt to pick the lock (Requires thieves' tools and a DC 20 Dexterity check)",
    "Examine the old records (if anyone can read Dwarvish)",
    "Search the room thoroughly"
  ]
}
```

### Final Output Format

The merge script includes suggested actions in the final output:

```
NARRATION:
<narration text>

ASK:
<roll request or "(none)">

ACTIONS:
- Attempt to pick the lock (Requires thieves' tools and a DC 20 Dexterity check)
- Examine the old records (if anyone can read Dwarvish)
- Search the room thoroughly
```

If no actions are suggested, the ACTIONS block shows:
```
ACTIONS:
(none)
```

## State Management

Suggested actions do NOT affect game state directly. They are purely informational to guide player choices. However:

- Actions that have been completed (e.g., chest opened) should NOT appear in subsequent suggested actions for that location
- STATE_PATCHER should track completed actions to prevent duplicate suggestions

## Examples

### Example 1: W5 - Assayers' Office

**Location Card** contains:
- Locked iron strongbox (DC 20 Dexterity, thieves' tools required)
- Old paper scraps (examine if Dwarvish can be read)
- Treasure mentioned in strongbox

**Suggested Actions Generated:**
```json
{
  "suggested_actions": [
    "Attempt to pick the lock on the strongbox (Requires thieves' tools and a DC 20 Dexterity check)",
    "Examine the old records (if anyone can read Dwarvish)",
    "Search the room thoroughly"
  ]
}
```

### Example 2: Location with Gates

**Location Card** contains:
- `mechanics`: `[{"type": "check", "dc": 14, "ability": "Wisdom", "skill": "Perception"}]`
- Description mentions listening at a door

**Suggested Actions Generated:**
```json
{
  "suggested_actions": [
    "Make a DC 14 Wisdom (Perception) check to listen at the door",
    "Search the room thoroughly"
  ]
}
```

## Best Practices

1. **Be Specific**: Include DCs, tools, and skill requirements in action descriptions
2. **Be Actionable**: Actions should be things players can actually attempt
3. **Include Context**: Mention relevant conditions (e.g., "if anyone can read Dwarvish")
4. **Avoid Duplication**: Don't suggest the same action multiple times
5. **Update After Actions**: Remove completed actions from future suggestions (via state tracking)

## Technical Implementation

### Helper Script

A helper script `extract_suggested_actions.ps1` provides utility functions for parsing location cards, but NARRATOR agent can generate actions directly from card data without requiring the helper script.

### Validation

The `validate_agent_outputs.ps1` script validates that:
- `suggested_actions` is an optional field for NARRATOR
- If present, `suggested_actions` must be an array of strings
- No strict validation of action content (formatting is flexible)

## Integration with Gates System

Suggested actions work seamlessly with the Gates System:
- If a gate check is required, suggest it as an action with the DC and skill
- After the gate is passed (tracked in state), the action can be updated or removed from future suggestions
- Gated information should NOT be revealed in the action description itself

## Future Enhancements

Potential improvements:
- Action priorities/ordering (most important first)
- Action categories (examine, interact, explore, combat)
- Character-specific actions (only suggest if relevant character is present)
- Context-aware suggestions based on party composition
- Dynamic action updates based on completed actions
































