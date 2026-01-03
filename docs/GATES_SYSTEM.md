# Gates System

## Overview

Gates are DC checks or saving throws that control access to information, areas, or outcomes. Cards in chapter packs include a `gates` array that defines what checks are required.

## Gate Structure

Gates are defined in card `gates` arrays:

```json
{
  "gates": [
    {
      "type": "check",
      "dc": 10,
      "ability": "Wisdom",
      "skill": "Survival",
      "note": ""
    },
    {
      "type": "save",
      "dc": 15,
      "ability": "Dexterity",
      "skill": "",
      "note": ""
    }
  ]
}
```

**Fields:**
- `type` - `"check"` (ability check) or `"save"` (saving throw)
- `dc` - Difficulty class
- `ability` - Ability score name (Wisdom, Dexterity, etc.)
- `skill` - Skill name (Survival, Perception, etc.) - only for checks
- `note` - Optional note

## Gate Tracking in State

Gates are tracked in `CURRENT_STATE.json`:

```json
{
  "gates": {
    "goblin_trail_found": false,
    "goblin_trail_details": false
  },
  "discoveries": {
    "goblin_trail_basic": false,
    "goblin_trail_tracks": false,
    "goblin_trail_bodies": false
  }
}
```

## How Gates Work

### 1. Card Defines Gates

Cards include `gates` array with required checks:

```json
{
  "id": "ch01_goblin_trail_001",
  "title": "Goblin Trail",
  "boxed_text": "On the north side of the road, characters can easily find a trail behind the thickets that leads northwest. A character who succeeds on a DC 10 Wisdom (Survival) check recognizes that about a dozen goblins have come and gone along the trail; the character also sees signs of two human-sized bodies being hauled from the ambush site.",
  "gates": [
    {
      "type": "check",
      "dc": 10,
      "ability": "Wisdom",
      "skill": "Survival",
      "note": "Reveals goblin count and body tracks"
    }
  ]
}
```

### 2. REFEREE Checks Gates

Before revealing information, REFEREE must:
1. Check if gate has been passed (in state)
2. If not passed, request the roll
3. If passed, reveal the information

### 3. STATE_PATCHER Updates Gates

After a successful gate check, STATE_PATCHER emits:

```json
{
  "patches": [
    {
      "op": "add",
      "path": "/gates/goblin_trail_details",
      "value": true
    },
    {
      "op": "add",
      "path": "/discoveries/goblin_trail_tracks",
      "value": true
    }
  ]
}
```

### 4. Information Revealed

Only after gate is passed:
- Reveal the detailed information
- Update state with discovery
- Allow progression based on discovery

## Example: Goblin Trail

### Card Text (ch01_steve_prescott_005)

**Basic information (no gate):**
> "On the north side of the road, characters can easily find a trail behind the thickets that leads northwest."

**Gated information (requires DC 10 Survival):**
> "A character who succeeds on a DC 10 Wisdom (Survival) check recognizes that about a dozen goblins have come and gone along the trail; the character also sees signs of two human-sized bodies being hauled from the ambush site."

### Workflow

1. **Party searches area:**
   - REFEREE: "You find a trail behind the thickets leading northwest."
   - No gate check needed for basic trail

2. **Party wants details:**
   - REFEREE: Requests DC 10 Wisdom (Survival) check
   - Player rolls: 12 (success)
   - STATE_PATCHER: Updates `/gates/goblin_trail_details` = true
   - REFEREE: Reveals "About a dozen goblins have used this trail, and you see signs of two human-sized bodies being dragged."

3. **State updated:**
   ```json
   {
     "gates": {
       "goblin_trail_details": true
     },
     "discoveries": {
       "goblin_trail_tracks": true,
       "goblin_trail_bodies": true
     }
   }
   ```

## REFEREE Rules

### Before Revealing Information

1. **Check card gates:**
   - Does the card have a `gates` array?
   - What information requires a gate check?

2. **Check state:**
   - Has this gate been passed?
   - What discoveries have been made?

3. **If gate not passed:**
   - Request the roll (DC, ability, skill)
   - Do NOT reveal gated information
   - Only reveal basic/non-gated information

4. **If gate passed:**
   - Reveal the gated information
   - Reference the discovery in state

## STATE_PATCHER Rules

### After Gate Check Success

1. **Emit patches:**
   ```json
   {
     "op": "add",
     "path": "/gates/<gate_name>",
     "value": true
   }
   ```

2. **Emit discoveries:**
   ```json
   {
     "op": "add",
     "path": "/discoveries/<discovery_name>",
     "value": true
   }
   ```

3. **Gate names should be:**
   - Descriptive: `goblin_trail_details`
   - Unique per gate: `snare_trap_noticed`
   - Based on card ID or scene: `ch01_goblin_trail_survival`

## Best Practices

1. **Never assume gates are passed** - Always check state first
2. **Gate names should be unique** - Use card ID or scene context
3. **Track discoveries separately** - Gates = checks passed, Discoveries = information found
4. **Respect gate order** - Some gates may depend on others
5. **Basic info vs gated info** - Always provide basic info, gate only detailed/special info

## Integration with Cards

Cards should structure information as:

**Basic (no gate):**
- Always available
- General description
- Obvious features

**Gated (requires check):**
- Detailed information
- Hidden features
- Special knowledge
- Progression requirements

Example:
```
Basic: "You see a trail leading northwest."
Gated: "A DC 10 Survival check reveals about a dozen goblins used this trail and two human-sized bodies were dragged."
```



