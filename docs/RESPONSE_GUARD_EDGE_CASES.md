# Response Guard Edge Cases - Analysis

## Current `respond()` Implementation Edge Cases

### ✅ Edge Case 1: Combat Not Active
**Current behavior:** Defaults to `--is-pc-turn true` (fail-open)
**Status:** ✅ HANDLED CORRECTLY

When combat is not active, all turns are treated as PC turns. This is safe because:
- Non-combat interactions are always player-driven
- Enemy turns only exist during combat
- Fail-open prevents false positives

**Line:** `dm_workflow.py:807-808`

---

### ⚠️ Edge Case 2: Combat Initiated but No `current_turn`
**Current behavior:** Prints warning, defaults to PC turn
**Status:** ⚠️ NEEDS REVIEW

**Scenario:**
```json
{
  "combat": {
    "initiated": true,
    "combat_id": "abc123",
    "current_turn": null  // Missing or null
  }
}
```

**Current code (lines 771-772):**
```python
else:
    print("⚠️  Combat initiated but no current_turn found")
```

**Issue:** Falls through to default PC turn, but we're actually in combat. Could be:
1. Combat just started (turn not set yet)
2. Combat ended but state not updated
3. Data corruption

**Recommendation:** 
- Check `combat.ended` or `combat.is_active` flag
- If combat is active but no current_turn, fail-closed (assume enemy turn) OR
- Check if we can derive from `initiative_order[0]`

**Suggested fix:**
```python
if current_turn_id:
    # ... existing code
else:
    # Combat active but no current turn - check if ended
    if combat_data.get("ended", False):
        print("ℹ️  Combat ended - treating as non-combat")
        # Default to PC turn (safe)
    else:
        # Combat active but no turn set - could be initialization
        # Default to enemy turn (fail-closed, more restrictive)
        print("⚠️  Combat active but no current_turn - defaulting to enemy turn (fail-closed)")
        # Could also try to derive from initiative_order
        initiative_order = combat_data.get("initiative_order", [])
        if initiative_order:
            current_turn_id = initiative_order[0]
            # ... continue with derived turn
```

---

### ✅ Edge Case 3: Missing Combat Status File
**Current behavior:** Handled by `response_guard.py` (exits with error)
**Status:** ✅ HANDLED CORRECTLY

If `--combat-status` file doesn't exist, `response_guard.py` exits with code 1 and error message.

**Line:** `response_guard.py:115-117`

---

### ✅ Edge Case 4: Invalid JSON in Combat Status
**Current behavior:** Caught by `response_guard.py` with clear error
**Status:** ✅ HANDLED CORRECTLY

`json.JSONDecodeError` is caught and reported.

**Line:** `response_guard.py:119-121`

---

### ✅ Edge Case 5: Temp File Cleanup
**Current behavior:** Cleaned up in `finally` block
**Status:** ✅ HANDLED CORRECTLY

Temp file is always deleted, even if validation fails.

**Line:** `dm_workflow.py:839-843`

---

## Recommendations

### Priority 1: Fix Edge Case 2
When combat is initiated but `current_turn` is missing:
1. Check if combat has ended (`combat.ended` or `combat.is_active: false`)
2. If ended → treat as non-combat (PC turn, fail-open)
3. If active but no turn → derive from `initiative_order[0]` OR fail-closed (enemy turn)

### Priority 2: Add Combat Status Validation
Before creating temp file, validate combat_status structure:
```python
if combat_status:
    # Validate structure
    if "current_turn" not in combat_status or "creature_id" not in combat_status.get("current_turn", {}):
        print("⚠️  Invalid combat status structure - defaulting to PC turn")
        combat_status = None  # Fall back to PC turn
```

---

## Testing Checklist

- [x] Combat active with valid current_turn → ✅ Works
- [x] Combat not active → ✅ Defaults to PC turn
- [ ] Combat active but current_turn missing → ⚠️ Needs fix
- [x] Invalid combat status file → ✅ Handled
- [x] "Any reactions?" on enemy turn → ✅ Allowed
- [x] "Do you want to do anything?" on enemy turn → ✅ Blocked
- [x] Temp file cleanup → ✅ Works

---

## Summary

**Current state:** 4/6 edge cases handled correctly

**Action needed:**
1. Fix combat active + missing current_turn case (Edge Case 2)
2. Consider adding combat status structure validation
