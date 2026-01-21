# Resource Guard System

**Deterministic resource tracking with fail-closed validation.**

## Overview

The Resource Guard system enforces a protocol for tracking resource spends (spell slots, rage, ki, etc.) that prevents "forgetting to deduct" errors through machine-checkable validation.

## How It Works

### 1. SPEND Tags (Inline Markers)

Whenever any PC spends a resource, the DM output must include an inline marker:

```
[SPEND <actor_id> <resource> <level?> <amount>]
```

**Examples:**
- `[SPEND brevin spell_slot 2 1]` → Brevin spends 1 level-2 slot
- `[SPEND torgga_brawnanvil rage 1]` → Torgga spends 1 rage
- `[SPEND vandross_ephrates superiority_die 1]` → Vandross spends 1 superiority die
- `[SPEND zephyr_sparkwhistle ki 2]` → Zephyr spends 2 ki points

**Note:** Spell slots require the level: `spell_slot <level> <amount>`. Other resources just need `<resource> <amount>`.

### 2. STATE-DELTA Block (Reconciliation)

At the end of the DM response, include a fenced block that declares what changed:

```
STATE-DELTA
- brevin: spell_slot.2 -= 1
- torgga_brawnanvil: rage -= 1
END STATE-DELTA
```

**Format:**
- Each resource change on its own line
- Format: `- <actor>: <resource>.<level?> -= <amount>`
- Spell slots: `spell_slot.2` (level required)
- Other resources: `rage`, `ki`, etc. (no level)

### 3. Validation Rules

The Resource Guard validates:

- ✅ Every SPEND tag has a matching STATE-DELTA entry
- ✅ STATE-DELTA amounts match SPEND tag amounts exactly
- ✅ No underflow (resource count can't go negative)
- ✅ All resources are from the allowed list

**If validation fails → BLOCKED** (response must be regenerated)

## Allowed Resources

- `spell_slot` (requires level: `spell_slot.2` for level 2)
- `rage`
- `superiority_die`
- `ki`
- `maneuver`
- `wild_shape`
- `channel_divinity`
- `bardic_inspiration`
- `sorcery_point`

## Example Response Format

```
NARRATION:
Torgga raises her holy symbol, channeling divine energy into Eglath's wounds. 
The gash on his shoulder begins to close as warmth spreads through his body.

[SPEND torgga_brawnanvil spell_slot 1 1]

The healing magic restores 1d8+3 hit points.

ASK:
What do you do next?

ACTIONS:
1. Press forward
2. Search the area
3. Take a short rest

STATE-DELTA
- torgga_brawnanvil: spell_slot.1 -= 1
END STATE-DELTA
```

## Multiple Resource Spends

```
NARRATION:
Eglath enters a rage, then attacks! [SPEND eglath_bearkiller rage 1]
Torgga casts Shield of Faith on Eglath. [SPEND torgga_brawnanvil spell_slot 1 1]

ASK:
What do you do next?

ACTIONS:
...

STATE-DELTA
- eglath_bearkiller: rage -= 1
- torgga_brawnanvil: spell_slot.1 -= 1
END STATE-DELTA
```

## Resource State File

Canonical resource counts are stored in: `scripts/resources_state.json`

This file is the single source of truth for resource availability. The guard checks against this file to prevent underflow.

**Format:**
```json
{
  "brevin": {
    "spell_slots": {},
    "rage": 0,
    "ki": 0,
    ...
  },
  "torgga_brawnanvil": {
    "spell_slots": {
      "1": 4,
      "2": 3,
      "3": 2
    },
    "channel_divinity": 1,
    ...
  }
}
```

## Integration

### dm_workflow.py

The Resource Guard is automatically called after `response_guard.py` when validating DM responses:

```bash
echo "response text" | python scripts/dm_workflow.py respond
```

Order of validation:
1. Preflight gate (packs/state/mcp)
2. Response guard (combat authority)
3. **Resource guard** (resource spend enforcement)

### dmregen.py

When a response is blocked due to resource guard failure, `dmregen.py` provides specific regeneration instructions:

```bash
echo "response text" | python scripts/dmregen.py
```

**Output for resource guard failures:**
```
BLOCKED: resource spend detected but STATE-DELTA block is missing
REGEN_INSTRUCTION: Regenerate with SPEND tags + STATE-DELTA block. ...
```

## Why This Works

**Protocol over memory:** The system doesn't rely on "the model remembering it spent something." Instead, it requires:
- Explicit tags (what happened)
- State delta (what was deducted)
- Machine validation (they must match)

**Fail-closed:** If validation fails, the response is blocked until regenerated correctly. No silent failures.

**Deterministic:** The guard can be run independently and will produce the same result every time.

## Manual Testing

Test the guard directly:

```bash
# Valid response
echo "Cast spell. [SPEND torgga_brawnanvil spell_slot 1 1] STATE-DELTA - torgga_brawnanvil: spell_slot.1 -= 1 END STATE-DELTA" | python scripts/resource_guard.py

# Missing STATE-DELTA (should block)
echo "Cast spell. [SPEND torgga_brawnanvil spell_slot 1 1]" | python scripts/resource_guard.py

# Underflow (should block)
echo "Rage. [SPEND eglath_bearkiller rage 5] STATE-DELTA - eglath_bearkiller: rage -= 5 END STATE-DELTA" | python scripts/resource_guard.py --verbose
```

## Troubleshooting

**"BLOCKED: resource spend detected but STATE-DELTA block is missing"**
- Add a STATE-DELTA block at the end of your response
- Ensure every SPEND tag has a matching entry in STATE-DELTA

**"BLOCKED: resource spend not reconciled"**
- Check that STATE-DELTA amounts match SPEND tag amounts exactly
- Check for typos in actor names or resource names
- Verify no underflow (spending more than available)

**"BLOCKED: invalid STATE-DELTA line format"**
- Ensure each line starts with `- `
- Format: `- actor: resource.level -= amount`
- Spell slots require `.level` (e.g., `spell_slot.2`)
- Other resources don't use `.level` (e.g., `rage`)
