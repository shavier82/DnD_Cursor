# Response Guard Acceptance Tests

## Test Suite: Enemy Turn Validation

**Setup:** All tests use `--is-pc-turn false` (enemy turn)

### ✅ Should PASS (Allowed Reactions Questions)

```bash
# Test 1: Simple reactions question
echo "Any reactions?" | python scripts/response_guard.py --is-pc-turn false
# Expected: OK: response_guard passed (exit 0)

# Test 2: Reactions with parenthetical list (commas)
echo "Any reactions? (Shield, Counterspell)" | python scripts/response_guard.py --is-pc-turn false
# Expected: OK: response_guard passed (exit 0)

# Test 3: Reactions with parenthetical list (slashes)
echo "Reactions? (Shield / Absorb Elements)" | python scripts/response_guard.py --is-pc-turn false
# Expected: OK: response_guard passed (exit 0)

# Test 4: Just "Reactions?"
echo "Reactions?" | python scripts/response_guard.py --is-pc-turn false
# Expected: OK: response_guard passed (exit 0)

# Test 5: With ASK: prefix
echo "ASK:`nAny reactions? (Shield, Counterspell)" | python scripts/response_guard.py --is-pc-turn false
# Expected: OK: response_guard passed (exit 0)
```

### ❌ Should BLOCK (Forbidden Questions)

```bash
# Test 1: Delegation question
echo "Ontharyx attacks. What does he do?" | python scripts/response_guard.py --is-pc-turn false
# Expected: BLOCKED: monster turn delegation detected (exit 1)

# Test 2: Generic delegation
echo "Do you want to do anything?" | python scripts/response_guard.py --is-pc-turn false
# Expected: BLOCKED: monster turn delegation detected (exit 1)

# Test 3: PC-only phrase on enemy turn
echo "What do you do?" | python scripts/response_guard.py --is-pc-turn false
# Expected: BLOCKED: monster turn delegation detected (exit 1)

# Test 4: Mixed question (delegation + shield keyword)
echo "What does Ontharyx do? Shield?" | python scripts/response_guard.py --is-pc-turn false
# Expected: BLOCKED: monster turn delegation detected (exit 1)
```

## Test Suite: PC Turn Validation

**Setup:** All tests use `--is-pc-turn true` (PC turn)

### ✅ Should PASS

```bash
# Test 1: PC turn prompt
echo "What do you do?" | python scripts/response_guard.py --is-pc-turn true
# Expected: OK: response_guard passed (exit 0)

# Test 2: Any question allowed on PC turns
echo "What does Brevin do?" | python scripts/response_guard.py --is-pc-turn true
# Expected: OK: response_guard passed (exit 0)
```

## Test Suite: Auto-Detection from Combat Status

```bash
# Create test combat status file
echo '{"current_turn": {"creature_id": "ontharyx"}, "is_active": true}' > test_status.json

# Test 1: Enemy turn auto-detected
echo "Any reactions?" | python scripts/response_guard.py --combat-status test_status.json
# Expected: OK: response_guard passed (exit 0)

# Test 2: Enemy turn with delegation
echo "What does Ontharyx do?" | python scripts/response_guard.py --combat-status test_status.json
# Expected: BLOCKED: monster turn delegation detected (exit 1)

# Test 3: PC turn auto-detected
echo '{"current_turn": {"creature_id": "brevin"}, "is_active": true}' > test_status_pc.json
echo "What do you do?" | python scripts/response_guard.py --combat-status test_status_pc.json
# Expected: OK: response_guard passed (exit 0)

# Cleanup
rm test_status.json test_status_pc.json
```

## Test Suite: Edge Cases

```bash
# Test 1: Combat active but current_turn missing (fail-closed)
echo '{"is_active": true}' > test_status_missing.json
echo "Any reactions?" | python scripts/response_guard.py --combat-status test_status_missing.json
# Expected: BLOCKED: combat active but current_turn.creature_id missing (exit 1)

# Test 2: Combat not active (fail-open, default to PC turn)
echo '{"is_active": false}' > test_status_inactive.json
echo "What do you do?" | python scripts/response_guard.py --combat-status test_status_inactive.json
# Expected: OK: response_guard passed (exit 0)

# Test 3: Missing PC roster file (fail-closed)
mv scripts/pc_roster.json scripts/pc_roster.json.bak
echo "Any reactions?" | python scripts/response_guard.py --is-pc-turn false
# Expected: ERROR: PC roster file not found (exit 1)
mv scripts/pc_roster.json.bak scripts/pc_roster.json

# Cleanup
rm test_status_missing.json test_status_inactive.json
```

## Quick Test Command

Run all acceptance tests:

```powershell
# Enemy turn - should pass
"Any reactions?" | python scripts/response_guard.py --is-pc-turn false
"Any reactions? (Shield, Counterspell)" | python scripts/response_guard.py --is-pc-turn false
"Reactions?" | python scripts/response_guard.py --is-pc-turn false

# Enemy turn - should block
"What does Ontharyx do?" | python scripts/response_guard.py --is-pc-turn false
"Do you want to do anything?" | python scripts/response_guard.py --is-pc-turn false
"What do you do?" | python scripts/response_guard.py --is-pc-turn false
```

## Expected Output Format

**On PASS:**
```
OK: response_guard passed
```
(Exit code: 0, stdout only, no stderr)

**On BLOCK:**
```
BLOCKED: monster turn delegation detected
```
(Exit code: 1, stdout only, violations to stderr only if --verbose)
