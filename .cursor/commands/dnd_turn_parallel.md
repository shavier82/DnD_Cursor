# /dnd_turn_parallel - Parallel Agents Dispatch

## Purpose
Dispatches 4 worker agents (REFEREE, NARRATOR, STATE_PATCHER, QA_COMPLIANCE) in parallel to process a D&D turn. Each agent MUST write its output to the coordination directory with the exact schema specified below.

## Usage
```
/dnd_turn_parallel [session-id]
```

If `session-id` is not provided, generate: `dnd-$(Get-Date -Format 'yyyyMMdd-HHmmss')`

## Process

### Step 1: Session ID & Coordination Directory
1. If session-id provided, use it. Otherwise generate: `dnd-YYYYMMDD-HHmmss`
2. Create coordination directory: `C:\DnD\.coord-<session-id>\`
3. **CRITICAL SAFETY CHECK**: Verify the path does NOT contain:
   - `C:\DnD\Campaigns\` (campaign folder)
   - `C:\DnD\DnD_Cursor\` (repo folder)
4. If path violates safety, abort with error

### Step 2: Dispatch 4 Worker Agents (Parallel)

**CRITICAL**: Each agent MUST:
- Write ONLY to its designated file in the coordination directory
- Use the EXACT schema specified below (no deviations)
- Set `blocked: true` if it cannot process (with optional `reason` or `block_reason` field)
- Never write to campaign folders or repo folders

#### Agent 1: REFEREE
**Output File**: `C:\DnD\.coord-<session-id>\dnd_out_REFEREE.json`

**Strict Schema** (copy this exactly):
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
  "mechanics_notes": []
}
```

**Instructions**:
- Your ONLY responsibility: mechanics, rolls, DCs
- Determine if a dice roll is required (`roll_request.required: true/false`)
- If `required: true`, populate: `skill_or_check`, `dc`, `formula`, `reason`
- If `required: false`, `roll_request` object must still exist but fields can be empty/default
- `mechanics_notes` is an array of strings (can be empty `[]`)
- If you cannot process due to missing data, set `blocked: true` and optionally add `reason: "..."` or `block_reason: "..."`
- **DO NOT** write anywhere except the output file above

#### Agent 2: NARRATOR
**Output File**: `C:\DnD\.coord-<session-id>\dnd_out_NARRATOR.json`

**Strict Schema** (copy this exactly):
```json
{
  "agent_role": "NARRATOR",
  "blocked": false,
  "narration": "You step cautiously into the dimly lit corridor..."
}
```

**Instructions**:
- Your ONLY responsibility: narration and storytelling
- Generate immersive narrative text for the `narration` field
- `narration` must be a non-empty string (if truly no narration, use "(none)")
- If you cannot process due to missing data, set `blocked: true` and optionally add `reason: "..."` or `block_reason: "..."`
- **DO NOT** write anywhere except the output file above

#### Agent 3: STATE_PATCHER
**Output File**: `C:\DnD\.coord-<session-id>\dnd_out_STATE_PATCHER.json`

**Strict Schema** (copy this exactly):
```json
{
  "agent_role": "STATE_PATCHER",
  "blocked": false,
  "patches": []
}
```

**Instructions**:
- Your ONLY responsibility: state updates (PATCH deltas)
- `patches` MUST be an array (can be empty `[]`)
- **CRITICAL RULE**: If REFEREE determines `roll_request.required: true`, you MUST output `patches: []` (empty array) because state cannot be updated until the roll completes
- If no roll pending, generate JSON Patch-like operations:
  ```json
  [
    {
      "op": "replace",
      "path": "/characters/rogue/hp",
      "value": 18
    }
  ]
  ```
- Valid `op` values: `"replace"`, `"add"`, `"remove"`
- `path` uses JSON Pointer notation (starts with `/`)
- If you cannot process due to missing data, set `blocked: true` and optionally add `reason: "..."` or `block_reason: "..."`
- **DO NOT** write anywhere except the output file above

#### Agent 4: QA_COMPLIANCE
**Output File**: `C:\DnD\.coord-<session-id>\dnd_out_QA_COMPLIANCE.json`

**Strict Schema** (copy this exactly):
```json
{
  "agent_role": "QA_COMPLIANCE",
  "blocked": false,
  "status": "ok",
  "issues": []
}
```

**Instructions**:
- Your ONLY responsibility: validate output format and guardrails
- After all other agents complete, validate:
  1. All 3 agent outputs exist and are valid JSON
  2. Each output has `agent_role` matching its role name
  3. Each output has `blocked` field (boolean)
  4. REFEREE has `roll_request` object
  5. NARRATOR has `narration` string
  6. STATE_PATCHER has `patches` array
  7. All files are in coordination directory (not campaign/repo)
- Set `status: "ok"` if all validations pass, `status: "fail"` otherwise
- If validation fails, populate `issues` array with descriptive strings
- If critical issues found (e.g., files in wrong location), set `blocked: true`
- **DO NOT** write anywhere except the output file above

### Step 3: Wait for All Outputs
- Monitor coordination directory for all 4 files:
  - `dnd_out_REFEREE.json`
  - `dnd_out_NARRATOR.json`
  - `dnd_out_STATE_PATCHER.json`
  - `dnd_out_QA_COMPLIANCE.json`
- Wait until all 4 files exist
- If timeout (e.g., 5 minutes), report which files are missing

### Step 4: Notify User
- Report completion status
- If all completed, instruct: `Run /dnd_turn_merge <session-id> to generate final output`
- If any failed, list which agents failed

## Safety Rules (NON-NEGOTIABLE)

1. **Coordination directory MUST be**: `C:\DnD\.coord-<session-id>\`
2. **Coordination directory MUST NOT be inside**:
   - `C:\DnD\Campaigns\` (campaign folder)
   - `C:\DnD\DnD_Cursor\` (repo folder)
3. **Agent outputs MUST be written ONLY to**:
   - `C:\DnD\.coord-<session-id>\dnd_out_<ROLE>.json`
4. **Agent outputs MUST NEVER be written to**:
   - Any file under `C:\DnD\Campaigns\Phandelver\`
   - Any file under `C:\DnD\DnD_Cursor\` (except coordination dir is outside repo)
5. **Schema compliance**: Each agent MUST produce the exact schema specified above

## Schema Validation Checklist

Before considering agents complete, verify:
- [ ] `dnd_out_REFEREE.json` exists and has: `agent_role: "REFEREE"`, `blocked`, `roll_request`, `mechanics_notes`
- [ ] `dnd_out_NARRATOR.json` exists and has: `agent_role: "NARRATOR"`, `blocked`, `narration`
- [ ] `dnd_out_STATE_PATCHER.json` exists and has: `agent_role: "STATE_PATCHER"`, `blocked`, `patches` (array)
- [ ] `dnd_out_QA_COMPLIANCE.json` exists and has: `agent_role: "QA_COMPLIANCE"`, `blocked`, `status`, `issues`
- [ ] All files are valid JSON
- [ ] All files are in coordination directory only

## Example Output

```
Parallel agents dispatched for session: dnd-20241215-143022
Coordination directory: C:\DnD\.coord-dnd-20241215-143022\

Waiting for agent outputs...
✓ REFEREE completed → C:\DnD\.coord-dnd-20241215-143022\dnd_out_REFEREE.json
✓ NARRATOR completed → C:\DnD\.coord-dnd-20241215-143022\dnd_out_NARRATOR.json
✓ STATE_PATCHER completed → C:\DnD\.coord-dnd-20241215-143022\dnd_out_STATE_PATCHER.json
✓ QA_COMPLIANCE completed → C:\DnD\.coord-dnd-20241215-143022\dnd_out_QA_COMPLIANCE.json

All agents completed. Run /dnd_turn_merge dnd-20241215-143022 to generate final output.
```

## Error Handling

If any agent fails:
- Report which agent failed
- Check if output file exists (may be partial/invalid)
- If file exists but is invalid JSON, report parsing error
- If file missing, report timeout
- Do NOT proceed to merge if any agent failed
