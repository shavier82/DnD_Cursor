# /dnd_turn_parallel — Parallel Agents Dispatch (HARDENED v2)

## Cursor Tool Output Limits (prevents connection bugs)
**CRITICAL**: If a terminal/tool command would produce more than ~30 lines:
- Redirect full output to a file under `C:\DnD\.coord-<session-id>\logs\`
- Print ONLY a 10–20 line summary to chat
- Never paste large command outputs into chat

**If a debug session is active:**
- Do not run tool-based commands; stop debug first.

---

## IMPORTANT: Where to run this
- Run `/dnd_turn_parallel` **in Cursor Chat** (the command palette chat), not in PowerShell.
- PowerShell will NOT recognize `/dnd_turn_parallel` (it will throw CommandNotFound).

---

## Goal
Fan-out a single player turn to 4 workers:
- **REFEREE** (mechanics only)
- **NARRATOR** (narration only)
- **STATE_PATCHER** (state deltas only)
- **QA_COMPLIANCE** (schema + guardrails)

Each worker writes exactly one JSON file to:
`C:\DnD\.coord-<session-id>\dnd_out_<ROLE>.json`

No worker may write anywhere else.

---

## Usage
`/dnd_turn_parallel [session-id]`

If omitted, generate: `dnd-$(Get-Date -Format 'yyyyMMdd-HHmmss')`

---

## INPUT FENCE (global)
Workers may only use these read inputs:

### TURN_TEXT (required)
- The user's latest action/intent (the current turn)

### Read-only packs (campaign)
- `C:\DnD\Campaigns\Phandelver\packs\session_preload.json`
- `C:\DnD\Campaigns\Phandelver\packs\chapter_pack_<n>.json` (current chapter)
- `C:\DnD\Campaigns\Phandelver\packs\encounter_pack.json`

### Read-only character stats (required)
- `C:\DnD\Campaigns\Phandelver\characters\*.json` (character stat files)
- REFEREE must load character JSON files before processing combat actions
- If character file is missing, REFEREE must BLOCK the action

### Read-only state (optional)
- `C:\DnD\Campaigns\Phandelver\saves\CURRENT_STATE.json` (if it exists)

### Explicitly FORBIDDEN (BUILD-only inputs)
- `C:\DnD\Sourcebooks\**` (raw sourcebook text - BUILD only)
- `C:\DnD\Campaigns\Phandelver\chapters\**` (raw chapter text dumps - BUILD only)
- Any `.txt` files in sourcebooks or chapters directories
- PDF files anywhere

### DO NOT READ BEYOND THIS LIST
- No browsing chapters/PDFs during PLAY.
- No reading other repo files.
- No reading any campaign files except packs and CURRENT_STATE.json.

---

## Step 1 — Session ID + Coordination Directory (outside repo)
1) Determine session id:
- If user passed `<session-id>`, use it
- Else generate: `dnd-$(Get-Date -Format 'yyyyMMdd-HHmmss')`

2) Coordination directory MUST be:
- `C:\DnD\.coord-<session-id>\`

3) Create subfolders if missing:
- `C:\DnD\.coord-<session-id>\logs\`

4) Safety checks (ABORT if violated):
- Coord dir MUST NOT be inside:
  - `C:\DnD\DnD_Cursor\`
  - `C:\DnD\Campaigns\`

---

## Step 2 — Dispatch workers (lane-locked)

### Global rules (ALL workers)
- Write ONLY one file: your role's JSON output file (exact name below).
- Output MUST be valid JSON matching the strict schema (no extra keys).
- If you cannot proceed due to missing required data: set `"blocked": true` and include `"reason"`.
- Never write to repo or campaign folders.
- Do not include commentary/markdown/logging in the JSON.

---

### Worker A — REFEREE (mechanics only)
**Allowed inputs:**
- TURN_TEXT
- campaign pack files (3): `C:\DnD\Campaigns\Phandelver\packs\*.json`
- **character JSON files**: `C:\DnD\Campaigns\Phandelver\characters\*.json`
- **REQUIRED: CURRENT_STATE.json** (MUST be loaded to check gates before ANY information reveal)

**Explicitly forbidden:**
- Narration/worldbuilding
- State patches / "what changes" assertions
- Reading other agents' outputs

**CRITICAL: Character stats loading:**
- Before processing any combat action involving a player character, REFEREE MUST:
  1. Load the character's JSON file from the characters directory
  2. Extract AC, HP, ability scores, and features
  3. **Check active conditions** using: `python C:\DnD\DnD_Cursor\scripts\manage_conditions.py effects <character_name>`
  4. **Apply condition effects** to AC, attack rolls, saves, skills:
     - AC modifiers (ac_mod)
     - Attack advantage/disadvantage
     - Save advantage/disadvantage
     - Skill advantage/disadvantage
     - Speed modifiers
     - Damage resistance/immunity
  5. Use these combined values for all calculations
- If character file is missing or invalid: set "blocked": true with reason

**CRITICAL: Gates enforcement (MANDATORY):**
- **BEFORE revealing ANY information from cards, REFEREE MUST:**
  1. **Load CURRENT_STATE.json** to check gate status
  2. **Check card's `gates` array** - does the information require a gate check?
  3. **If gate exists and NOT passed in state:**
     - DO NOT reveal the gated information
     - Request the required roll (DC, ability, skill)
     - Only reveal basic/non-gated information
  4. **If gate exists and IS passed in state:**
     - Reveal the gated information
     - Reference the discovery from state
  5. **If no gate exists:**
     - Information is always available (basic information)
- **Gate checking is MANDATORY for ALL skill checks, saves, and information reveals**
- **Never assume a gate has been passed** - always check state first
- **Example workflow:**
  - Card has gate: DC 10 Wisdom (Survival) for trail details
  - Check state: `/gates/goblin_trail_details` = false
  - Action: Request roll, do NOT reveal details
  - After successful roll: STATE_PATCHER updates gate, then reveal details

**Output file:**
- `C:\DnD\.coord-<session-id>\dnd_out_REFEREE.json`

**Strict schema (no extra keys):**
```json
{
  "agent_role": "REFEREE",
  "blocked": false,
  "reason": "",
  "roll_request": {
    "required": false,
    "skill_or_check": "",
    "dc": 0,
    "formula": "1d20",
    "reason": ""
  },
  "mechanics_notes": []
}
```

**Rules:**
- If a roll is required, set roll_request.required=true and fill skill_or_check, dc, formula, reason.
- If no roll is required, roll_request must still exist (use defaults).
- mechanics_notes is an array of strings; it may be empty.

---

### Worker B — NARRATOR (narration only)
**Allowed inputs:**
- TURN_TEXT
- campaign pack files (3): `C:\DnD\Campaigns\Phandelver\packs\*.json`
- optional CURRENT_STATE.json

**Explicitly forbidden:**
- DCs, dice, mechanics rulings
- State patches
- Reading other agents' outputs

**Output file:**
- `C:\DnD\.coord-<session-id>\dnd_out_NARRATOR.json`

**Strict schema (no extra keys):**
```json
{
  "agent_role": "NARRATOR",
  "blocked": false,
  "reason": "",
  "narration": "(none)"
}
```

**Rules:**
- Narration must be a string.
- If truly no narration: use "(none)".
- No mechanics language like "DC 15", "roll", "advantage", etc.

---

### Worker C — STATE_PATCHER (state deltas only)
**Allowed inputs:**
- TURN_TEXT
- campaign pack files (3): `C:\DnD\Campaigns\Phandelver\packs\*.json`
- optional CURRENT_STATE.json
- **AND the REFEREE output file ONLY:**
  - `C:\DnD\.coord-<session-id>\dnd_out_REFEREE.json` (read-only)

**Explicitly forbidden:**
- Writing narration
- Determining DCs or inventing roll outcomes
- Reading NARRATOR or QA outputs

**Output file:**
- `C:\DnD\.coord-<session-id>\dnd_out_STATE_PATCHER.json`

**Strict schema (no extra keys):**
```json
{
  "agent_role": "STATE_PATCHER",
  "blocked": false,
  "reason": "",
  "patches": [],
  "sheet_ops": []
}
```

**Rules:**
- Read REFEREE output. If roll_request.required=true => you MUST output patches: [].
- Only emit patches that are deterministic without a roll (e.g., "party moves to door" if movement is allowed and distance is known in state/packs).
- If state is unknown (no CURRENT_STATE.json), be conservative: output patches: [].
- Patch format (JSON Patch-like):
  - op: "add" | "replace" | "remove"
  - path: JSON Pointer starting with /
  - value: required for add/replace
- Example patch:
  ```json
  [
    { "op": "replace", "path": "/scene/door/status", "value": "opened" }
  ]
  ```
- **CRITICAL: Gate tracking (MANDATORY):**
  - **After REFEREE requests a gate check (roll_request.required=true with gate context):**
    - Wait for roll result (do NOT update gates yet)
  - **After successful gate check (when roll succeeds):**
    - Emit patches to update gates and discoveries:
      ```json
      [
        {
          "op": "add",
          "path": "/gates/<gate_name>",
          "value": true
        },
        {
          "op": "add",
          "path": "/discoveries/<discovery_name>",
          "value": true
        }
      ]
      ```
  - **Gate names must match card context:**
    - Use card ID or scene-based names: `goblin_trail_details`, `snare_trap_noticed`
    - Be specific and unique per gate
  - **Only update gates after successful checks** - failed checks do NOT update gates
- **Sheet Operations (sheet_ops):**
  - Emit sheet_ops array for Google Sheets updates (conditions, currency, resources, XP)
  - Operations: `condition_add`, `condition_remove`, `condition_tick`, `currency_add`, `resource_set`
  - Example sheet_ops:
    ```json
    [
      {
        "op": "condition_add",
        "character_id": "eglath_bearkiller",
        "condition": "poisoned",
        "source": "goblin_arrow",
        "duration_type": "rounds",
        "duration_value": 3,
        "ticks_remaining": 3,
        "mechanical_effects": ""
      }
    ]
    ```
- **State Saving:**
  - After encounters end or scene transitions, emit patches with paths like:
    - `/encounter/goblin_ambush` - marks encounter as completed
    - `/scene/area` - updates current area
    - `/scene/location` - updates current location
    - `/combat/ended` - marks combat as ended
  - The merge script automatically saves state to `CURRENT_STATE.json` when these patches are detected

---

### Worker D — QA_COMPLIANCE (validation only)
**Allowed inputs:**
- The four agent output files in the coordination directory (read-only)
- Nothing else

**Explicitly forbidden:**
- Changing content ("fixing" other agents)
- Adding narration/mechanics/patches of its own

**Output file:**
- `C:\DnD\.coord-<session-id>\dnd_out_QA_COMPLIANCE.json`

**Strict schema (no extra keys):**
```json
{
  "agent_role": "QA_COMPLIANCE",
  "blocked": false,
  "reason": "",
  "status": "ok",
  "issues": []
}
```

**Rules:**
- Validate:
  - All required files exist and are valid JSON
  - agent_role matches each filename role
  - Required keys exist per schema
  - If REFEREE requires roll => STATE_PATCHER patches must be []
  - Files are in `C:\DnD\.coord-<session-id>\` (not repo/campaign)
  - **Gates enforcement (CRITICAL - MANDATORY):**
    - Load CURRENT_STATE.json to check gate status
    - If REFEREE reveals gated information: verify gate exists in card AND gate is passed in state
    - If gate not passed but gated information revealed: set status="fail", add issue "Gate violation: <gate_name> not passed"
    - If REFEREE requests gate check: verify roll_request has correct DC/ability/skill matching card gates
    - If STATE_PATCHER updates gates: verify roll was successful (check REFEREE output for roll result)
    - If gate updated without successful roll: set status="fail", add issue "Gate updated without successful check"
- On failure: set status="fail" and populate issues[].
- If failure is critical (wrong location / missing files / gate violation): set blocked=true.

---

## Step 3 — Deterministic wait

**CRITICAL**: Do not proceed until all four output files exist.

**Required filenames:**
- dnd_out_REFEREE.json
- dnd_out_NARRATOR.json
- dnd_out_STATE_PATCHER.json
- dnd_out_QA_COMPLIANCE.json

**Optional PowerShell wait loop (write full output to logs if needed):**
```powershell
$dir="C:\DnD\.coord-<session-id>"
$need=@("dnd_out_REFEREE.json","dnd_out_NARRATOR.json","dnd_out_STATE_PATCHER.json","dnd_out_QA_COMPLIANCE.json")
for ($i=0; $i -lt 30; $i++) {
  $missing = $need | Where-Object { -not (Test-Path (Join-Path $dir $_)) }
  if ($missing.Count -eq 0) { break }
  Start-Sleep -Seconds 1
}
if ($missing.Count -gt 0) { throw "Timeout. Missing: $($missing -join ', ')" }
```

---

## Step 4 — Next instruction to user

If all files exist:
- Tell user: `Run /dnd_turn_merge <session-id>`

If any missing or QA failed:
- Output only: `BLOCKED: Pack missing required data: <reason>`

---

## FILE INTEGRITY SENTINEL (do not remove)
SENTINEL_SHA1: 9f2a7e3c1d4b7aa0c3c9f1d2a6b8c0d1e4f5a678
