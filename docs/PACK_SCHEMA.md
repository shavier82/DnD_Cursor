# PACK Schema Documentation

## Overview

PACK files are JSON structures used to organize and manage D&D campaign content, including session preload data, chapter-specific content, and encounter information.

## Pack Types

### session_preload
Pre-loads essential game data before a session starts. Contains foundational cards that apply across chapters.

### chapter_pack
Contains content specific to a numbered chapter. Each chapter pack corresponds to one chapter in the campaign.

### encounter_pack
Contains encounter-specific content, combat encounters, and related mechanics. Not tied to a specific chapter.

## Top-Level Structure

All pack files must include these required fields:

```json
{
  "pack_type": "<session_preload|chapter_pack|encounter_pack>",
  "pack_version": "1.0",
  "source": "Mines of Phandelver and Below",
  "chapter": <number or null>,
  "cards": []
}
```

### Field Definitions

- **pack_type** (string, required): One of `session_preload`, `chapter_pack`, or `encounter_pack`
- **pack_version** (string, required): Version identifier for the pack format (currently "1.0")
- **source** (string, required): Source material identifier
- **chapter** (number | null, required): 
  - For `chapter_pack`: The chapter number (1-8)
  - For `session_preload` and `encounter_pack`: `null`
- **cards** (array, required): Array of card objects (initially empty `[]`)

## Card Object Shape

Each card in the `cards` array has the following structure:

```json
{
  "id": "<unique-card-identifier>",
  "type": "<card-type>",
  "title": "<card-title>",
  "text": "<card-content>",
  "gates": []
}
```

### Card Fields

- **id** (string, required): Unique identifier for the card
- **type** (string, required): Type of card (e.g., "encounter", "location", "npc", "item", "note")
- **title** (string, required): Display title for the card
- **text** (string, required): Card content/text
- **gates** (array, required): Array of gate objects (initially empty `[]`)

## Gate Object Shape

Gates control conditional logic and dice roll mechanics for cards:

```json
{
  "trigger": "<trigger-condition>",
  "roll": "<dice-expression>",
  "dc": <difficulty-class>,
  "on_success": "<success-action>",
  "on_fail": "<failure-action>"
}
```

### Gate Fields

- **trigger** (string, required): Condition that activates the gate (e.g., "player-enters", "skill-check", "combat-start")
- **roll** (string, optional): Dice expression (e.g., "d20", "2d6+3", "d100")
- **dc** (number, optional): Difficulty class/target number for the roll
- **on_success** (string, required): Action or outcome when condition/roll succeeds
- **on_fail** (string, required): Action or outcome when condition/roll fails

## Patch Object Shape (State Updates)

Patches are used by the STATE_PATCHER agent to update game state. They follow a JSON Patch-like structure:

```json
{
  "op": "replace|add|remove",
  "path": "/path/to/field",
  "value": <new value>
}
```

### Patch Fields

- **op** (string, required): Operation type - one of:
  - `"replace"`: Replace existing value
  - `"add"`: Add new field/value
  - `"remove"`: Remove field/value
- **path** (string, required): JSON Pointer path to the field (e.g., "/characters/rogue/hp", "/party/gold")
- **value** (any, required for "replace" and "add"): New value to set

### Patch Examples

```json
[
  {
    "op": "replace",
    "path": "/characters/rogue/hp",
    "value": 18
  },
  {
    "op": "add",
    "path": "/characters/rogue/conditions",
    "value": ["poisoned"]
  },
  {
    "op": "remove",
    "path": "/party/gold"
  }
]
```

### Patch Rules

1. **Empty on Roll Pending**: If REFEREE determines a roll is required (`roll_request.required: true`), STATE_PATCHER MUST output `patches: []` (empty array)
2. **Path Format**: Use JSON Pointer notation (RFC 6901) - paths start with `/`
3. **Order Matters**: Patches are applied in array order
4. **Validation**: All patches must be valid JSON Patch operations

## Validation Rules

1. All pack files must be valid JSON
2. Required top-level keys must exist: `pack_type`, `pack_version`, `source`, `chapter`, `cards`
3. `pack_type` must be one of the three valid types
4. `chapter` must be `null` for `session_preload` and `encounter_pack`
5. `chapter` must be a number (1-8) for `chapter_pack`
6. `cards` must be an array (can be empty)
7. Each card must have `id`, `type`, `title`, `text`, and `gates` fields
8. Each gate must have `trigger`, `on_success`, and `on_fail` fields

## File Naming Convention

- `session_preload.json` - Session preload pack
- `chapter_pack_<n>.json` - Chapter pack for chapter `<n>`
- `encounter_pack.json` - Encounter pack

