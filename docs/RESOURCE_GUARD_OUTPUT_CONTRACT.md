# Resource Guard - Output Contract Fix

**Deterministic output contract - quiet mode is exactly ONE line.**

## Problem Fixed

Previously, quiet mode was printing multiple lines:
```
OK: response_guard passed
RESOURCE GUARD: OK: resource_guard passed
END REPORT
```

This broke the "single line status" philosophy and defeated `dmregen.py`.

## Solution

**Quiet mode (default):** Print exactly ONE line, always:
- `OK: dm_workflow passed` (all guards pass)
- `BLOCKED: <reason>` (any guard fails)
- `ERROR: <reason>` (fatal error)

**Verbose mode (`--verbose`):** Print one fenced REPORT with subsections:
```
REPORT WRID=<id>
RESPONSE_GUARD OUTPUT
<output>
RESOURCE_GUARD OUTPUT
<output>
APPLY_STATE_DELTA OUTPUT
<output>
END REPORT
```

## Implementation

### dm_workflow.py respond()

**Changed behavior:**
1. Capture all guard outputs (don't print immediately)
2. Run guards in sequence: response_guard → resource_guard → apply_state_delta
3. Collect all outputs
4. Decide final output:
   - **Quiet:** Print exactly one line
   - **Verbose:** Print one fenced REPORT with all subsections

**Key changes:**
- Don't print intermediate guard outputs directly
- Capture all stdout before deciding what to show
- Quiet mode always prints "OK: dm_workflow passed" if all pass
- Verbose mode shows full fenced REPORT with subsections

### apply_state_delta.py

**Changed behavior:**
- Silent by default (no output unless `--verbose` or `--dry-run`)
- Only prints to stdout when explicitly requested
- Output is captured by `dm_workflow.py` and shown in verbose mode

## Backup Folder Structure

**Deterministic backup location:**
```
scripts/backups/resources_state/resources_state.<timestamp>.json
```

**Key changes:**
- Backups go into `scripts/backups/resources_state/` folder
- Folder is created automatically if missing
- Predictable naming: `resources_state.<timestamp>.json`
- Timestamp format: `YYYYMMDD_HHMMSS`

**Example:**
```
scripts/backups/resources_state/resources_state.20260120_175354.json
scripts/backups/resources_state/resources_state.20260120_175400.json
```

## Testing

### Quiet Mode (Default)
```bash
echo "response text" | python scripts/dm_workflow.py respond
```
**Output:** Exactly one line
- `OK: dm_workflow passed` ✅
- `BLOCKED: <reason>` ✅
- `ERROR: <reason>` ✅

### Verbose Mode
```bash
echo "response text" | python scripts/dm_workflow.py respond --verbose
```
**Output:** One fenced REPORT block with subsections
```
REPORT WRID=<id>
RESPONSE_GUARD OUTPUT
...
RESOURCE_GUARD OUTPUT
...
APPLY_STATE_DELTA OUTPUT
...
END REPORT
```

## Benefits

1. **Deterministic output** - Always know what to expect
2. **dmregen.py works** - Single line status for clipboard parsing
3. **Clean verbose output** - One fenced report with all information
4. **Predictable backups** - Always in same folder with same naming
5. **No path confusion** - Backup folder is relative to script location

## Files Modified

- `scripts/dm_workflow.py` - Output contract enforcement
- `scripts/apply_state_delta.py` - Silent by default, deterministic backups

## Status

✅ **Complete** - Output contract is now deterministic and fail-closed.
