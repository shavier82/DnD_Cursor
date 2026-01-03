# Gates Enforcement System

## Overview

Gates are **MANDATORY** and must be enforced on **EVERY** skill check, save, and information reveal. This document defines the enforcement rules.

## Enforcement Rules

### REFEREE (MANDATORY)

**BEFORE revealing ANY information:**

1. **Load CURRENT_STATE.json** (required)
   - Check `/gates/` object for passed gates
   - Check `/discoveries/` object for discovered information

2. **Check card's `gates` array**
   - Does the information require a gate check?
   - What is the DC, ability, and skill?

3. **Decision tree:**
   ```
   IF card has gate:
     IF gate passed in state:
       → Reveal gated information
     ELSE:
       → DO NOT reveal gated information
       → Request roll (roll_request.required=true)
       → Only reveal basic/non-gated information
   ELSE:
     → Information is always available (reveal it)
   ```

4. **Never assume gates are passed**
   - Always check state first
   - If state doesn't exist, gates are NOT passed
   - If gate name not in state, gate is NOT passed

### STATE_PATCHER (MANDATORY)

**After successful gate check:**

1. **Wait for roll result**
   - Do NOT update gates when roll is requested
   - Only update gates when roll SUCCEEDS

2. **Emit patches:**
   ```json
   {
     "op": "add",
     "path": "/gates/<gate_name>",
     "value": true
   }
   ```

3. **Emit discoveries:**
   ```json
   {
     "op": "add",
     "path": "/discoveries/<discovery_name>",
     "value": true
   }
   ```

4. **Gate naming:**
   - Must be unique and descriptive
   - Based on card ID or scene context
   - Examples: `goblin_trail_details`, `snare_trap_noticed`, `pit_trap_spotted`

### QA_COMPLIANCE (MANDATORY)

**Validate gates are enforced:**

1. **Check REFEREE output:**
   - If gated information is revealed, verify gate is passed in state
   - If gate not passed but information revealed: FAIL validation

2. **Check STATE_PATCHER output:**
   - If gate patches are emitted, verify roll was successful
   - If gate patches without successful roll: FAIL validation

3. **Check roll requests:**
   - If REFEREE requests gate check, verify DC/ability/skill match card gates
   - If mismatch: FAIL validation

## Enforcement Examples

### Example 1: Goblin Trail Details

**Card (ch01_steve_prescott_005):**
- Has gate: DC 10 Wisdom (Survival)
- Basic info: "You find a trail leading northwest"
- Gated info: "About a dozen goblins used this trail and two human-sized bodies were dragged"

**REFEREE workflow:**
1. Load state: `/gates/goblin_trail_details` = false
2. Check card: Has gate for trail details
3. Action: Request DC 10 Wisdom (Survival) check
4. Reveal: "You find a trail leading northwest" (basic info only)
5. Do NOT reveal: Goblin count and body tracks (gated)

**After successful roll:**
1. STATE_PATCHER: Updates `/gates/goblin_trail_details` = true
2. Next turn: REFEREE checks state, gate is passed
3. Reveal: Full information including goblin count and body tracks

### Example 2: Snare Trap

**Card:**
- Has gate: DC 15 Wisdom (Perception) to notice snare
- Basic info: "You're walking along the trail"
- Gated info: "You notice a hidden snare ahead"

**REFEREE workflow:**
1. Load state: `/gates/snare_trap_noticed` = false
2. Check card: Has gate for snare detection
3. Action: Request DC 15 Wisdom (Perception) check
4. Reveal: "You're walking along the trail" (basic info)
5. Do NOT reveal: Snare location (gated)

**After successful roll:**
1. STATE_PATCHER: Updates `/gates/snare_trap_noticed` = true
2. Reveal: "You notice a hidden snare ahead"

**After failed roll:**
1. STATE_PATCHER: Does NOT update gate
2. Snare triggers (character must make Dex save)

## Validation Checklist

### REFEREE Output Validation

- [ ] State was loaded before information reveal
- [ ] Card gates were checked
- [ ] Gated information only revealed if gate passed
- [ ] Roll requested if gate not passed
- [ ] Basic information always available (no gate)

### STATE_PATCHER Output Validation

- [ ] Gates only updated after successful checks
- [ ] Gate names are unique and descriptive
- [ ] Discoveries match gates
- [ ] Patches use correct JSON Patch format

### QA_COMPLIANCE Validation

- [ ] No gated information revealed without gate being passed
- [ ] Gates only updated after successful checks
- [ ] Roll requests match card gates (DC, ability, skill)

## Failure Cases

### Case 1: Gate Not Checked

**Error:** REFEREE reveals gated information without checking state
**Detection:** QA_COMPLIANCE checks state, gate not passed
**Action:** Set status="fail", blocked=true

### Case 2: Gate Updated Without Success

**Error:** STATE_PATCHER updates gate after failed roll
**Detection:** QA_COMPLIANCE checks roll result
**Action:** Set status="fail", blocked=true

### Case 3: Wrong Gate Name

**Error:** Gate name doesn't match card context
**Detection:** Manual review or QA validation
**Action:** Set status="fail", add issue

## Best Practices

1. **Always load state first** - Never assume gates are passed
2. **Check card gates** - Every card should be checked for gates array
3. **Gate names must be unique** - Use card ID or scene context
4. **Basic vs gated info** - Always provide basic info, gate only detailed info
5. **State updates only on success** - Failed checks do NOT update gates
6. **QA validates everything** - No gate violations should pass validation

## Integration Points

### REFEREE
- Loads state at start of processing
- Checks gates before every information reveal
- Requests rolls for ungated gates
- Never reveals gated information without gate being passed

### STATE_PATCHER
- Updates gates only after successful checks
- Emits discovery patches
- Tracks gate names consistently

### QA_COMPLIANCE
- Validates gate enforcement
- Checks state consistency
- Blocks violations

### Merge Script
- Saves state after patches applied
- Ensures gates are persisted



