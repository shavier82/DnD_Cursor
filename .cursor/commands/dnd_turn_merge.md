# /dnd_turn_merge - Merge Agent Outputs

## Purpose
Validates agent outputs, then merges them into the final 3-block user-facing response.

## Usage
```
/dnd_turn_merge <session-id>
```

## Action Steps

### Step 1: Validate Agent Outputs
**Run this command first:**
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:\DnD\DnD_Cursor\scripts\validate_agent_outputs.ps1 -SessionId <session-id>
```

**Expected result:**
- Exit code 0 if validation passes
- If validation fails, output will show which agent outputs are invalid
- **DO NOT proceed to merge if validation fails**

### Step 2: Run Merge Script
**If validation passes, run:**
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:\DnD\DnD_Cursor\scripts\merge_outputs.ps1 -SessionId <session-id>
```

**Output to chat:**
- Capture ONLY the final 3-block output (NARRATION, ASK, PATCH)
- Do NOT include script progress messages or merge JSON file paths
- If output starts with "BLOCKED:", show that single line only

## Expected Output Format

### Success Case
```
NARRATION:
<narration text>

ASK:
<ask text>

PATCH:
<JSON array or []>
```

### Blocked Case
```
BLOCKED: Pack missing required data: <reason>
```

## Process Details

### Validation Step
The validation script checks:
- All 4 agent output files exist
- Files are in coordination directory (not campaign/repo folders)
- JSON syntax is valid
- Required schema fields are present
- `agent_role` matches expected role name

### Merge Step
The merge script:
1. Reads all 4 agent JSON files from `C:\DnD\.coord-<session-id>\`
2. Checks for `blocked: true` in any agent → outputs BLOCKED
3. Checks QA status → outputs BLOCKED if not "ok"
4. Extracts NARRATION from NARRATOR
5. Builds ASK from REFEREE roll_request (if required) or default
6. Extracts PATCH from STATE_PATCHER (empty if roll pending)
7. Outputs exactly 3 blocks to stdout

## Safety Rules
- Never write to campaign folders
- All outputs remain in coordination directory
- Never modify agent output files
- Only read and merge, never delete

## Example Workflow

1. User runs: `/dnd_turn_merge demo-001`
2. System runs validation: `validate_agent_outputs.ps1 -SessionId demo-001`
3. If validation passes, system runs: `merge_outputs.ps1 -SessionId demo-001`
4. System outputs only the 3-block result to chat
