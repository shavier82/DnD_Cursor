# /dnd_turn_parallel — Parallel Agents Dispatch (HARDENED)

## Goal
Fan-out a single player turn to 4 worker agents (REFEREE, NARRATOR, STATE_PATCHER, QA_COMPLIANCE).
Each agent writes exactly one JSON output file to `C:\DnD\.coord-<session-id>\`.
No agent may write anywhere else.

## Usage
`/dnd_turn_parallel [session-id]`

If `session-id` is omitted, generate: `dnd-YYYYMMDD-HHmmss`

---

## INPUT FENCE (agents may only use these inputs)
**TURN_TEXT (required):** user's latest action/intent (the current turn)

**Read-only packs (repo):**
- `C:\DnD\DnD_Cursor\packs\session_preload.json`
- `C:\DnD\DnD_Cursor\packs\chapter_pack_<n>.json` (current chapter)
- `C:\DnD\DnD_Cursor\packs\encounter_pack.json`

**Read-only state (optional):**
- `C:\DnD\Campaigns\Phandelver\saves\CURRENT_STATE.json` (if it exists)

**DO NOT READ BEYOND THIS LIST**
- No browsing chapters/PDFs during PLAY.
- No reading other repo files.
- No reading any campaign files except CURRENT_STATE.json (optional).

---

## Step 1 — Session ID + Coordination Directory (outside repo)
1) Determine session id:
- If user passed `<session-id>`, use it
- Else generate: `dnd-$(Get-Date -Format 'yyyyMMdd-HHmmss')`

2) Coordination directory MUST be:
- `C:\DnD\.coord-<session-id>\`

3) Create it if missing.

4) Safety checks (ABORT if violated):
- Coord dir MUST NOT be inside:
  - `C:\DnD\DnD_Cursor\`
  - `C:\DnD\Campaigns\`

---

## Step 2 — Dispatch 4 workers (parallel)

### Global rules (ALL workers)
- Write ONLY one file: your role's JSON output file (exact name below).
- Output MUST be valid JSON matching the strict schema (no extra keys).
- If you cannot proceed due to missing required data: set `"blocked": true` and include `"reason"`.
- Never write to repo or campaign folders.
- Do not include commentary/markdown/logging in the JSON.

---

### Worker A — REFEREE (mechanics only)
**Allowed inputs:** TURN_TEXT + packs + optional CURRENT_STATE.json  
**Forbidden:** narration/worldbuilding, state patches  
**Output file:** `C:\DnD\.coord-<session-id>\dnd_out_REFEREE.json`

**Strict schema (exact keys):**
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
- Decide if a roll is required.
- If required=true, fill in skill_or_check, dc, formula, reason.
- mechanics_notes: array of short mechanics-only strings (no narration).

---

### Worker B — NARRATOR (narration only)
**Allowed inputs:** TURN_TEXT + encounter_pack + optional CURRENT_STATE.json  
**Forbidden:** DCs, rolls, rules text, patches/state changes  
**Output file:** `C:\DnD\.coord-<session-id>\dnd_out_NARRATOR.json`

**Strict schema (exact keys):**
```json
{
  "agent_role": "NARRATOR",
  "blocked": false,
  "reason": "",
  "narration": "(none)"
}
```

**Rules:**
- Output only narration for the immediate moment.
- Never mention dice/DC/modifiers/rules.

---

### Worker C — STATE_PATCHER (state deltas only)
**Allowed inputs:** TURN_TEXT + optional CURRENT_STATE.json + packs  
**Forbidden:** narration, inventing stats, DCs/rolls  
**Output file:** `C:\DnD\.coord-<session-id>\dnd_out_STATE_PATCHER.json`

**Strict schema (exact keys):**
```json
{
  "agent_role": "STATE_PATCHER",
  "blocked": false,
  "reason": "",
  "patches": []
}
```

**Rules:**
- patches MUST be an array.
- If REFEREE roll_request.required=true this turn, patches MUST be [].
- Otherwise output JSON Patch-like ops:
  - op: "add" | "replace" | "remove"
  - path: JSON pointer (starts with "/")
  - value: required for add/replace, omitted for remove
- Example:
  ```json
  [
    { "op": "replace", "path": "/scene/torch_lit", "value": true }
  ]
  ```

---

### Worker D — QA_COMPLIANCE (validator only)
**Allowed inputs:** the 3 worker JSON output files + rules in this doc  
**Forbidden:** generating game content  
**Output file:** `C:\DnD\.coord-<session-id>\dnd_out_QA_COMPLIANCE.json`

**Strict schema (exact keys):**
```json
{
  "agent_role": "QA_COMPLIANCE",
  "blocked": false,
  "reason": "",
  "status": "ok",
  "issues": []
}
```

**Checks:**
- All 3 worker files exist and are valid JSON.
- agent_role matches filename role.
- blocked is boolean.
- REFEREE has roll_request.required boolean.
- NARRATOR has narration string.
- STATE_PATCHER has patches array.
- All files located ONLY in `C:\DnD\.coord-<session-id>\`.
- If failures: status="fail" and issues populated.
- If critical (missing files / wrong location): blocked=true.

---

## Step 3 — Deterministic wait (DO NOT MERGE EARLY)

**Required files (exact names):**
- `dnd_out_REFEREE.json`
- `dnd_out_NARRATOR.json`
- `dnd_out_STATE_PATCHER.json`
- `dnd_out_QA_COMPLIANCE.json`

**Optional wait loop (PowerShell):**
```powershell
$dir="C:\DnD\.coord-<session-id>"
$need=@("dnd_out_REFEREE.json","dnd_out_NARRATOR.json","dnd_out_STATE_PATCHER.json","dnd_out_QA_COMPLIANCE.json")
for ($i=0; $i -lt 30; $i++) {
  $missing = $need | Where-Object { -not (Test-Path (Join-Path $dir $_)) }
  if ($missing.Count -eq 0) { break }
  Start-Sleep -Seconds 1
}
if ($missing.Count -gt 0) { throw "Timeout missing: $($missing -join ', ')" }
```

---

## Step 4 — Next instruction

When all 4 files exist:
- Tell user: `Run /dnd_turn_merge <session-id>`
- Do NOT merge inside this command.

---

## FILE INTEGRITY SENTINEL (do not remove)
SENTINEL_SHA1: 6d1e7b2a9a1c9a2b5d2f0b52c9db2a5d5a9b2a55
