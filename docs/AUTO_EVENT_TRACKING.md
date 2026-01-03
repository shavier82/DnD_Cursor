# Automatic Event Tracking System

## Overview

The Automatic Event Tracking System automatically detects milestones, quest progress, and story events from state changes and updates `CAMPAIGN_EVENTS.json` without manual intervention.

## How It Works

### Automatic Detection

The system runs automatically after each turn merge (`merge_outputs.ps1`) and detects:

1. **Encounter Completions**
   - When `/encounters/<name>` is added to state
   - Automatically creates an event entry
   - Links to party members and location

2. **Quest Item Discoveries**
   - When `/discoveries/` entries match quest objectives
   - Automatically updates quest status to "completed"
   - Records completion timestamp and notes

3. **Location-Based Quest Progress**
   - When party moves to a quest location (`/scene/location`)
   - Updates quest progress if party is at quest location
   - Tracks "at_location" progress

4. **State-Based Event Detection**
   - Scans completed encounters in state
   - Checks discoveries against active quests
   - Creates events for major milestones

### Integration

**Called from:** `merge_outputs.ps1` after state is saved

**Script:** `C:\DnD\DnD_Cursor\scripts\auto_event_tracker.ps1`

**Parameters:**
- `-Campaign`: Campaign name
- `-StateFile`: Path to CURRENT_STATE.json
- `-Patches`: Array of patches from STATE_PATCHER

## What Gets Tracked Automatically

### Events Created
- Encounter completions
- Major discoveries
- Location arrivals at quest locations

### Quest Updates
- Status changes (active → completed)
- Progress tracking (at_location)
- Completion timestamps
- Completion notes

### NPC Updates
- Relationship changes (when detected)
- Interaction logging (when detected)

## Manual Override

While the system is automatic, you can still manually update `CAMPAIGN_EVENTS.json` for:
- Complex story events
- NPC relationship changes
- Custom quest milestones
- Player choices that don't trigger state changes

## Quest Tracking Patterns

The system recognizes these patterns:

### Quest Item Discovery
```json
{
  "discoveries": {
    "u9_herbalist_shop_necklace": true
  }
}
```
If a quest has `quest_item: "necklace"`, this discovery will mark the quest as completed.

### Quest Location Arrival
```json
{
  "scene": {
    "location": "u9_herbalist_s_shop"
  }
}
```
If a quest has `quest_location: "Thundertree, U9: Herbalist's Shop"`, this will update quest progress.

### Encounter Completion
```json
{
  "encounters": [
    {
      "name": "venomfang_dragon",
      "completed": true
    }
  ]
}
```
This automatically creates an encounter event.

## Configuration

No configuration needed - the system works automatically for all campaigns.

## Limitations

The system is designed to catch common patterns but may not detect:
- Complex multi-step quests
- NPC dialogue choices
- Moral decisions
- Resource allocation choices

For these, manual updates to `CAMPAIGN_EVENTS.json` may still be needed.

## Best Practices

1. **Let it run automatically** - Don't disable it
2. **Review periodically** - Check `CAMPAIGN_EVENTS.json` to ensure events are being tracked
3. **Manual updates for complex events** - Add detailed context manually when needed
4. **Quest naming** - Use clear quest item names that match discovery names for auto-detection

