# Obsidian Resource Sync - Complete Implementation

**MCP-only resource sync with SHA verification - fail-closed and deterministic.**

## Overview

Resources are now synced to Obsidian vault with cryptographic verification. The system ensures:
- Local `scripts/resources_state.json` is a staging mirror
- Obsidian `DnD/state/resources_state.json` is the authoritative source
- Every sync is verified with SHA256 hash comparison
- If sync fails → BLOCKED (even if guards passed)

## Architecture

### Two-Phase Commit Pattern

```
1. Resource Spend → SPEND tags + STATE-DELTA
2. resource_guard.py validates
3. apply_state_delta.py updates local staging copy
4. sync_resources_obsidian.py:
   - Writes to Obsidian vault
   - Reads back from Obsidian vault
   - Verifies SHA256 matches
5. If SHA mismatch → BLOCKED
```

### Files

1. **`scripts/resources_state.json`** (staging mirror)
   - Updated by `apply_state_delta.py`
   - Never manually edited
   - Always synced to Obsidian after changes

2. **`C:/Users/ksist/Documents/Obsidian/DnD/state/resources_state.json`** (authoritative)
   - Source of truth
   - Updated via `sync_resources_obsidian.py`
   - SHA verified after every write

3. **`scripts/mcp_obsidian_config.json`** (config)
   ```json
   {
     "vault_path": "C:/Users/ksist/Documents/Obsidian",
     "resources_file_path": "DnD/state/resources_state.json"
   }
   ```

4. **`scripts/sync_resources_obsidian.py`** (sync + verify)
   - Writes local staging copy to Obsidian
   - Reads back and calculates SHA256
   - Compares with expected SHA
   - Returns 0 if match, 1 if mismatch

## Workflow Integration

### Automatic Sync in dm_workflow.py

After `apply_state_delta.py` succeeds:
1. Run `sync_resources_obsidian.py`
2. If sync fails → BLOCKED (quiet mode: one line error)
3. If sync succeeds → Continue (silent in quiet mode)

**Order:**
1. Preflight gate
2. Response guard
3. Resource guard
4. Apply STATE-DELTA (local staging)
5. **Sync to Obsidian + SHA verify** ← NEW
6. Print final status

### Output Contract

**Quiet mode:**
- Success: `OK: dm_workflow passed` (one line)
- Sync failure: `BLOCKED: obsidian sync failed (sha mismatch) ...` (one line)

**Verbose mode:**
```
REPORT WRID=<id>
RESPONSE_GUARD OUTPUT
...
RESOURCE_GUARD OUTPUT
...
APPLY_STATE_DELTA OUTPUT
...
OBSIDIAN_SYNC OUTPUT
OK: obsidian sync passed (SHA verified)
END REPORT
```

## SHA Verification

Every sync performs:
1. Calculate SHA256 of local staging copy
2. Write to Obsidian vault
3. Read back from Obsidian vault
4. Calculate SHA256 of read-back content
5. Compare: `wanted_sha == got_sha`
6. If mismatch → BLOCKED with error message

**Why this works:**
- Cryptographic verification (SHA256)
- Readback confirms write succeeded
- Mismatch = corruption or write failure
- Fail-closed: blocks until sync verified

## Configuration

### Vault Path

Edit `scripts/mcp_obsidian_config.json`:
```json
{
  "vault_path": "C:/Users/ksist/Documents/Obsidian",
  "resources_file_path": "DnD/state/resources_state.json"
}
```

**Note:** `vault_path` is absolute, `resources_file_path` is relative to vault root.

## Testing

### Manual Sync Test
```bash
python scripts/sync_resources_obsidian.py
```
- Exit code 0 = success (SHA verified)
- Exit code 1 = failure (prints error to stderr)

### Full Workflow Test
```bash
echo "Cast spell. [SPEND torgga_brawnanvil spell_slot 1 1] STATE-DELTA - torgga_brawnanvil: spell_slot.1 -= 1 END STATE-DELTA" | python scripts/dm_workflow.py respond
```

**Expected:**
- `OK: dm_workflow passed` (if all steps succeed)
- `BLOCKED: ...` (if any step fails, including sync)

### Verify SHA Match
```python
import hashlib
f1 = open('scripts/resources_state.json','rb').read()
f2 = open('C:/Users/ksist/Documents/Obsidian/DnD/state/resources_state.json','rb').read()
print('SHA match:', hashlib.sha256(f1).hexdigest() == hashlib.sha256(f2).hexdigest())
```

## Error Handling

### Sync Failures

**Write error:**
```
BLOCKED: obsidian sync failed (write error): <details>
```

**Readback error:**
```
BLOCKED: obsidian sync failed (readback error): <details>
```

**SHA mismatch:**
```
BLOCKED: obsidian sync failed (sha mismatch) wanted=<sha>... got=<sha>...
```

**All sync failures block the entire workflow** - even if guards passed.

## Why This Is "Locked Down"

1. **Deterministic:** SHA verification is machine-checkable
2. **Fail-closed:** Sync failure = BLOCKED (no silent failures)
3. **Two-phase commit:** Write + readback + verify
4. **Cryptographic:** SHA256 ensures integrity
5. **Single source of truth:** Obsidian is authoritative

## Status

✅ **Complete** - Obsidian resource sync with SHA verification is fully integrated and production-ready.

The system now ensures:
- Resources are always synced to Obsidian
- Sync is verified with SHA256
- Failures are detected and block the workflow
- No silent sync failures possible
