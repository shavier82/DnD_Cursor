# Parallel Agents Architecture

## Overview

The D&D engine uses a parallel agents architecture where multiple specialized agents process different aspects of a turn simultaneously, then merge their outputs into a single, deterministic response.

## Agent Roles

### REFEREE
**Responsibility**: Mechanics, rolls, DCs only
- Validates rules compliance
- Determines if dice rolls are required
- Calculates DCs and roll formulas
- Outputs: `dnd_out_REFEREE.json`

**Output Schema**:
```json
{
  "agent_role": "REFEREE",
  "blocked": false,
  "roll_request": {
    "required": true,
    "skill_or_check": "Perception",
    "dc": 15,
    "formula": "1d20+3",
    "reason": "Spotting hidden trap"
  },
  "mechanics_notes": ["Trap requires Perception DC 15"]
}
```

### NARRATOR
**Responsibility**: Narration only
- Generates narrative descriptions
- Handles dialogue and scene-setting
- Creates immersive text
- Outputs: `dnd_out_NARRATOR.json`

**Output Schema**:
```json
{
  "agent_role": "NARRATOR",
  "blocked": false,
  "narration": "You step cautiously into the dimly lit corridor..."
}
```

### STATE_PATCHER
**Responsibility**: State updates only (PATCH deltas)
- Updates game state (HP, conditions, positions)
- Tracks resource consumption
- Generates JSON Patch-like operations
- Outputs: `dnd_out_STATE_PATCHER.json`
- **CRITICAL**: `patches` MUST be `[]` if a roll is pending

**Output Schema**:
```json
{
  "agent_role": "STATE_PATCHER",
  "blocked": false,
  "patches": [
    {
      "op": "replace",
      "path": "/characters/rogue/hp",
      "value": 18
    }
  ]
}
```

### QA_COMPLIANCE
**Responsibility**: Output format + guardrails validation
- Validates all agent outputs match schemas
- Checks guardrail compliance
- Flags format issues
- Outputs: `dnd_out_QA_COMPLIANCE.json`

**Output Schema**:
```json
{
  "agent_role": "QA_COMPLIANCE",
  "blocked": false,
  "status": "ok",
  "issues": []
}
```

### MERGE
**Responsibility**: Compose final 3-block response
- Reads all agent outputs
- Applies merge rules
- Generates final user-facing output
- Outputs: `dnd_out_MERGE.json` and formatted text

**Output Schema**:
```json
{
  "agent_role": "MERGE",
  "blocked": false,
  "final": {
    "NARRATION": "...",
    "ASK": "...",
    "PATCH": []
  }
}
```

## Workflow

### Phase 1: Parallel Execution (Fan-out)
1. User initiates turn with `/dnd_turn_parallel`
2. System prompts for or generates `session-id`
3. Creates coordination directory: `C:\DnD\.coord-<session-id>\`
4. Dispatches 4 worker agents in parallel:
   - REFEREE
   - NARRATOR
   - STATE_PATCHER
   - QA_COMPLIANCE
5. Each agent writes its JSON output to coordination directory
6. System waits for all 4 outputs to exist

### Phase 2: Merge (Fan-in)
1. User runs `/dnd_turn_merge` with same `session-id`
2. MERGE agent reads all 4 worker outputs
3. Applies merge rules:
   - If any agent has `blocked: true` → output `BLOCKED: Pack missing required data: <what>`
   - If REFEREE says `roll_request.required: true` → ASK must request roll
   - If roll pending → PATCH must be `[]`
   - Compose final 3-block output
4. Outputs formatted response:
   ```
   NARRATION:
   <narration text>
   
   ASK:
   <ask text>
   
   PATCH:
   <JSON array or []>
   ```

## Output Format Rules

### Success Case
Final output MUST be exactly these 3 blocks, in order:
```
NARRATION:
<text from NARRATOR>

ASK:
<text requesting player action or roll if REFEREE.roll_request.required=true>

PATCH:
<JSON array from STATE_PATCHER.patches>
```

### Blocked Case
If any agent has `blocked: true`, output ONLY:
```
BLOCKED: Pack missing required data: <description>
```

## Safety Rules

1. **No Campaign Writes**: All outputs go to `C:\DnD\.coord-<session-id>\`
2. **No Git in Campaign**: Never create `.git` in campaign folder
3. **Worktrees Only in Repo**: All agent worktrees must be in `C:\DnD\DnD_Cursor`
4. **Block Propagation**: If any agent blocks, final output is blocked
5. **Roll Pending**: If roll required, PATCH must be empty array

## Coordination Directory Structure

```
C:\DnD\.coord-<session-id>\
├── dnd_out_REFEREE.json
├── dnd_out_NARRATOR.json
├── dnd_out_STATE_PATCHER.json
├── dnd_out_QA_COMPLIANCE.json
└── dnd_out_MERGE.json
```

## Agent Contracts

Each agent MUST:
1. Write only to its designated output file in coordination directory
2. Include `agent_role` field matching its role name
3. Include `blocked` boolean field
4. Follow its specific output schema
5. Never write to campaign folders
6. Never create files outside coordination directory

## Merge Rules

MERGE agent MUST:
1. Read all 4 worker agent outputs
2. Check if any has `blocked: true` → output BLOCKED message
3. Check QA_COMPLIANCE status → fail if not "ok"
4. Extract NARRATION from NARRATOR.narration
5. Build ASK from REFEREE.roll_request if required=true
6. Extract PATCH from STATE_PATCHER.patches (empty if roll pending)
7. Output exactly 3 blocks in specified format




