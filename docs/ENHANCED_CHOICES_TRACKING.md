# Enhanced Choices and Consequences Tracking

## Overview

The **CAMPAIGN_EVENTS.json** file is your static JSON file that tracks everything that happens, choices made, and their long-lasting effects. This system ensures that decisions made early in the campaign continue to influence events throughout the entire campaign and even into future campaigns.

## Current System Status

✅ **File Location:** `C:\DnD\Campaigns\Phandelver\saves\CAMPAIGN_EVENTS.json`

✅ **Currently Tracks:**
- Events (story events, encounters, quests)
- Choices log (player decisions)
- Consequences (long-term effects)
- NPC relationships and interactions
- Quest status and progress
- Faction relationships

## How It Works

### 1. Choices Are Logged
Every significant player choice is recorded in the `choices_log` array with:
- What was chosen
- What alternatives existed
- Immediate impact
- Long-term consequences
- Severity level

### 2. Consequences Are Tracked
Consequences are tracked separately in the `consequences` object:
- Status (active, resolved, ongoing)
- What choice/event caused it
- How it manifests in the world
- Timeline of how it develops
- Cross-campaign effects

### 3. NPCs Remember
NPC relationships track:
- Relationship level and history
- Past interactions
- How choices affected them
- Long-term effects of relationship

### 4. The System Is Referenced
Before any significant interaction, the AI:
1. Loads CAMPAIGN_EVENTS.json
2. Checks past choices affecting the situation
3. References active consequences
4. Checks NPC relationship history
5. Uses this context to inform current events

## Querying Your Choices

Use the query script to explore your campaign history:

```powershell
# Show summary
python C:\DnD\DnD_Cursor\scripts\query_campaign_choices.py --summary

# Find all choices affecting a specific NPC
python C:\DnD\DnD_Cursor\scripts\query_campaign_choices.py --npc "Mirna Dendrar"

# Show all active consequences
python C:\DnD\DnD_Cursor\scripts\query_campaign_choices.py --active-consequences

# Show choices with long-term impact
python C:\DnD\DnD_Cursor\scripts\query_campaign_choices.py --long-term

# Show cross-campaign effects
python C:\DnD\DnD_Cursor\scripts\query_campaign_choices.py --cross-campaign

# Show all choices
python C:\DnD\DnD_Cursor\scripts\query_campaign_choices.py --all-choices
```

## What Gets Tracked Automatically

The system automatically tracks:
- ✅ Encounter completions
- ✅ Quest progress
- ✅ Location discoveries
- ✅ Major milestones

## What Needs Manual Tracking

You (or the AI) should manually track:
- ⚠️ Significant player choices
- ⚠️ Moral decisions
- ⚠️ Resource allocation decisions
- ⚠️ NPC relationship changes
- ⚠️ Consequence creation
- ⚠️ Cross-campaign effects

## Example: How a Choice Creates Long-Term Effects

**Choice Made:**
- Destroyed the Forge of Spells

**Immediate Impact:**
- Forge destroyed, magical power lost

**Long-Term Consequence:**
- Phandalin loses potential economic growth
- No magical item production possible
- Gundren may express disappointment in future interactions
- Future campaigns in Phandalin won't have access to the forge

**How It's Tracked:**
1. Choice logged in `choices_log`
2. Consequence created in `consequences`
3. NPC relationship updated (Gundren's opinion affected)
4. World state updated (location status changed)
5. Cross-campaign effect marked (affects future campaigns)

## Ensuring Long-Lasting Effects

To ensure choices have long-lasting effects:

1. **Always log significant choices** - Don't skip logging important decisions
2. **Create consequences** - When a choice has delayed effects, create a consequence entry
3. **Update NPC relationships** - Track how choices affect how NPCs view the party
4. **Reference past choices** - The AI should check past choices before presenting options
5. **Manifest consequences** - Have consequences appear later in the campaign
6. **Cross-reference** - Link related choices and consequences together

## File Structure

The file is located at:
- `C:\DnD\Campaigns\Phandelver\saves\CAMPAIGN_EVENTS.json`

It contains:
- `events[]` - All story events
- `choices_log[]` - All player choices
- `consequences{}` - All active and resolved consequences
- `npcs{}` - NPC relationships and history
- `quests{}` - Quest status and progress
- `factions{}` - Faction relationships
- `cross_campaign_effects[]` - Effects that carry to other campaigns

## Best Practices

1. **Be Specific** - Include enough detail to understand context months later
2. **Track Severity** - Mark how significant each choice/consequence is
3. **Link Events** - Reference related choices and consequences
4. **Timeline Everything** - Use ISO timestamps
5. **Document Alternatives** - Note what could have been chosen instead
6. **Track Manifestation** - Note when consequences will appear
7. **Update Status** - Keep consequence status current

## Integration

The system is integrated into the gameplay:
- ✅ AI agents load it at session start
- ✅ AI checks it before NPC interactions
- ✅ AI references it when determining outcomes
- ✅ AI updates it when significant choices are made
- ✅ Automatic tracking for encounters and quests

## Next Steps

1. **Review current choices** - Use the query script to see what's been tracked
2. **Enhance existing entries** - Add more detail to existing choices/consequences
3. **Create missing consequences** - If choices were made but consequences weren't created, add them
4. **Reference in gameplay** - The AI will automatically reference this file, but you can remind it if needed

















