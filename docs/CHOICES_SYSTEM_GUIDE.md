# Choices and Consequences System - Complete Guide

## What You Asked For

You wanted **"a static JSON file that keeps track of things that happen, choices that are made etc. So you can call back on it to remember things that has happened in the past. I want the choices that we make to have long lasting affects on the campaign and beyond."**

**✅ This system already exists and is being used!**

## The File

**Location:** `C:\DnD\Campaigns\Phandelver\saves\CAMPAIGN_EVENTS.json`

This is your static JSON file that:
- ✅ Tracks everything that happens
- ✅ Records all choices made
- ✅ Tracks long-lasting effects
- ✅ Can be referenced to remember past events
- ✅ Ensures choices affect the campaign and beyond

## Current Status

**Currently Tracking:**
- 4 choices logged
- 2 consequences recorded
- 5 NPCs with relationship history
- 9 quests tracked
- Multiple events recorded

## How It Works

### 1. Choices Are Logged

Every significant choice you make is recorded with:
- What you chose
- What alternatives existed
- Immediate impact
- Long-term consequences
- Who/what was affected

### 2. Consequences Are Tracked

Consequences are tracked separately and can:
- Be active, resolved, or ongoing
- Have different severity levels
- Manifest immediately or later
- Affect NPCs, locations, factions
- Carry over to other campaigns

### 3. The AI References It

Before any interaction, the AI:
1. Loads CAMPAIGN_EVENTS.json
2. Checks past choices affecting the situation
3. References active consequences
4. Checks NPC relationship history
5. Uses this to inform current events

### 4. Long-Term Effects Manifest

Consequences can:
- Appear immediately
- Manifest days/weeks later
- Affect future chapters
- Carry to other campaigns

## Example: How Your Choices Create Long-Term Effects

**Example Choice:**
- "Destroyed the Forge of Spells"

**Immediate Impact:**
- Forge destroyed, magical power lost

**Long-Term Consequence:**
- Phandalin loses economic potential
- Gundren's opinion affected
- Future campaigns won't have access to forge
- Marked as cross-campaign effect

**How It's Used:**
- When you interact with Gundren later, he remembers
- When you return to Phandalin, the forge is gone
- In future campaigns, the forge won't exist
- NPCs may reference the destroyed forge

## Querying Your Choices

Use the query script to explore your campaign history:

```powershell
# Show summary
python C:\DnD\DnD_Cursor\scripts\query_campaign_choices.py --summary

# Find choices affecting an NPC
python C:\DnD\DnD_Cursor\scripts\query_campaign_choices.py --npc "Mirna Dendrar"

# Show active consequences
python C:\DnD\DnD_Cursor\scripts\query_campaign_choices.py --active-consequences

# Show choices with long-term impact
python C:\DnD\DnD_Cursor\scripts\query_campaign_choices.py --long-term

# Show all choices
python C:\DnD\DnD_Cursor\scripts\query_campaign_choices.py --all-choices
```

## Adding Choices Manually

You can add choices manually using the script:

```powershell
python C:\DnD\DnD_Cursor\scripts\add_campaign_choice.py `
  --choice "Destroyed the Forge of Spells" `
  --location "wave_echo_cave_w15" `
  --chapter 4 `
  --type "tactical" `
  --alternatives "Leave forge intact" "Capture forge" `
  --immediate "Forge destroyed, magical power lost" `
  --consequence "Phandalin loses economic potential, no magical item production" `
  --severity "major" `
  --affected-npcs "Gundren Rockseeker" `
  --affected-locations "Phandalin" "Wave Echo Cave" `
  --future-impact "Future campaigns won't have access to forge" `
  --cross-campaign
```

## File Structure

The file contains these sections:

```json
{
  "campaign": "Phandelver",
  "last_updated": "timestamp",
  
  "events": [
    // All story events, encounters, quests
  ],
  
  "choices_log": [
    // All player choices with consequences
  ],
  
  "consequences": {
    // Active and resolved consequences
  },
  
  "npcs": {
    // NPC relationships and history
  },
  
  "quests": {
    // Quest status and progress
  },
  
  "factions": {
    // Faction relationships
  },
  
  "cross_campaign_effects": [
    // Effects that carry to other campaigns
  ]
}
```

## Ensuring Long-Lasting Effects

The system is designed to ensure choices have long-lasting effects:

1. **Choices are logged** - Every significant choice is recorded
2. **Consequences are created** - Long-term effects are tracked separately
3. **NPCs remember** - Relationship history tracks how choices affected NPCs
4. **World state changes** - Locations and factions are affected
5. **Cross-campaign effects** - Some effects carry to other campaigns
6. **AI references it** - The AI checks past choices before interactions

## What Gets Tracked Automatically

✅ Encounter completions
✅ Quest progress
✅ Location discoveries
✅ Major milestones

## What Needs Manual Tracking

⚠️ Significant player choices (use add_campaign_choice.py)
⚠️ Moral decisions
⚠️ Resource allocation
⚠️ Consequence creation
⚠️ Cross-campaign effects

## Integration

The system is fully integrated:
- ✅ AI loads it at session start
- ✅ AI checks it before NPC interactions
- ✅ AI references it when determining outcomes
- ✅ AI updates it when choices are made
- ✅ Automatic tracking for encounters/quests

## Next Steps

1. **Review current choices** - See what's been tracked
2. **Add missing choices** - Use the script to add important past choices
3. **Create consequences** - Add long-term effects for existing choices
4. **Reference in gameplay** - The AI will automatically use it

## Documentation

- **Full System Docs:** `C:\DnD\DnD_Cursor\docs\CAMPAIGN_EVENTS_SYSTEM.md`
- **Choices Guide:** `C:\DnD\DnD_Cursor\docs\CHOICES_AND_CONSEQUENCES_SYSTEM.md`
- **Enhanced Tracking:** `C:\DnD\DnD_Cursor\docs\ENHANCED_CHOICES_TRACKING.md`

















