# Map Guard System - Battlemap Validation

## Overview

The Map Guard System ensures battlemap state never drifts by enforcing a single source of truth, atomic updates, and deterministic coordinates. It acts as a hard gate during combat, similar to the preflight gate.

## Components

### 1. `map_guard.py` - Core Validation Script

Validates battlemap state before every PLAY response during combat:
- Validates CURRENT_STATE.json exists and parses
- Determines battlemap JSON path from combat_id/location
- Validates battlemap structure (grid, coordinates, tokens, bounds)
- Checks for coordinate drift, duplicates, invalid positions
- Outputs MAP_RECEIPT that must be pasted verbatim

**Usage:**
```bash
python scripts/map_guard.py
python scripts/map_guard.py --verbose
```

### 2. `dm_workflow.py mapcheck` - Workflow Integration

Wraps `map_guard.py` in the unified workflow system:
- Quiet mode: one line output
- Verbose mode: fenced REPORT block with WRID

**Usage:**
```bash
python scripts/dm_workflow.py mapcheck
python scripts/dm_workflow.py mapcheck --verbose
```

### 3. `dmmap.py` - Helper Script

Simplified interface for map validation:
- Runs `dm_workflow.py mapcheck`
- On failure, prints ready-to-paste instruction

**Usage:**
```bash
python scripts/dmmap.py
python scripts/dmmap.py --verbose
```

### 4. `map_clip.ps1` - PowerShell Helper

Runs map guard and copies receipt to clipboard:
- Executes `map_guard.py`
- Copies output to clipboard
- Preserves formatting

**Usage:**
```powershell
.\scripts\map_clip.ps1
```

## Map Guard Contract

### Single Source of Truth

- `scripts/combat_positions_<location>.json` is the ONLY authoritative map state during PLAY
- Renderer must render from this file (never from memory, never from encounter_pack after init)

### Immutable Base, Mutable Overlay

- `encounter_pack.json` provides static map definition (grid size, walls, terrain, initial positions)
- `scripts/combat_positions_<location>.json` holds live overlay (token positions, conditions, HP, statuses, dynamic terrain changes)

### Atomic Update Rule

Every token move / terrain change must be applied as one "transaction":
1. Compute changes
2. Write `scripts/combat_positions_<location>.json` once
3. Refresh renderer once

### Deterministic Coordinates

- **Coordinate system:** origin=top_left, x=col, y=row
- **Grid unit:** squares only (no half-squares)
- **Token ID:** stable IDs (never name-based)
- **Renderer:** always uses `combatants[]` from JSON

**Enforcement:**
- No floats (integers only)
- No out-of-bounds
- No missing token IDs
- No renderer stale

## MAP_RECEIPT Format

Valid MAP_RECEIPT (must include all fields):
```
MAP_RECEIPT
- ENCOUNTER_ID: <encounter_id>
- CURRENT_STATE: loaded
- BATTLEMAP: loaded (<filename>)
- COORD_SYS: ok (origin=top_left, x=col, y=row)
- TOKENS: ok (N=<count>)
- BOUNDS: ok (<width>x<height>)
- MAP_HASH: <hash>
- MAP_REFRESH_DUE: false
```

If no combat is active:
```
MAP_RECEIPT
- ENCOUNTER_ID: none (no active combat)
- CURRENT_STATE: loaded
- BATTLEMAP: not_required
- COORD_SYS: ok (origin=top_left, xy=col_row)
- MAP_REFRESH_DUE: false
```

## Hard Gate Enforcement

**During combat (CURRENT_STATE.json combat.initiated=true and combat.ended=false):**

The user's CURRENT message must include a fenced code block that starts with:
```text
MAP_RECEIPT
```

If combat is active and no valid MAP_RECEIPT is present, respond ONLY with:
```
BLOCKED: run map_clip.ps1 and paste the MAP_RECEIPT (```text block) in your message
```

**Validation Rules:**
- First line must be exactly: "MAP_RECEIPT"
- Each subsequent field must be on its own line starting with "- "
- If combat is active, ALL fields must be present and valid
- If no combat is active, MAP_RECEIPT is not required

## Battlemap JSON Structure

Required fields:
- `grid_size`: integer (pixels per square, typically 5)
- `map_width_squares`: integer (grid width)
- `map_height_squares`: integer (grid height)
- `combatants`: dictionary of token_id -> token_data
- `defeated`: list of defeated token IDs (optional)
- `terrain`: dictionary of terrain_id -> terrain_data (optional)
- `combat_status`: combat state overlay (optional)

Token data structure:
```json
{
  "x": <integer>,
  "y": <integer>,
  "color": "<color_name>",
  "label": "<single_char>",
  "elevated": <boolean> (optional),
  "unconscious": <boolean> (optional)
}
```

Terrain data structure:
```json
{
  "x": <integer>,
  "y": <integer>,
  "width": <integer>,
  "height": <integer>,
  "color": "<color_name>",
  "type": "<terrain_type>"
}
```

## Common Issues and Fixes

### Issue: "Defeated token X not found in combatants"
**Fix:** This is now allowed - defeated tokens may be removed from combatants. The validation no longer checks for their presence.

### Issue: "Coordinates must be integers"
**Fix:** Ensure all x, y coordinates are integers, not floats. Use `int(x)` when computing positions.

### Issue: "x=Y out of bounds"
**Fix:** Check that coordinates are within 0 to (width-1) for x and 0 to (height-1) for y.

### Issue: "Missing required field"
**Fix:** Ensure battlemap JSON has `grid_size`, `map_width_squares`, and `map_height_squares` at the top level.

## Integration with Workflow

The map guard is integrated into the unified workflow system:
- Runs automatically during combat (via hard gate)
- Can be run manually: `python scripts/dm_workflow.py mapcheck`
- Helper script: `python scripts/dmmap.py`

## PowerShell Aliases (Optional)

Add to your PowerShell profile for convenience:
```powershell
function dmmap {
    python C:\DnD\DnD_Cursor\scripts\dmmap.py @args
}

function dmmapreport {
    python C:\DnD\DnD_Cursor\scripts\dm_workflow.py mapcheck --verbose
}
```

## See Also

- `.cursorrules` - MAP HARD GATE section
- `scripts/map_guard.py` - Core validation script
- `scripts/view_battlemap.py` - Battlemap renderer
- `docs/BATTLEMAP_SYSTEM.md` - Battlemap system documentation
