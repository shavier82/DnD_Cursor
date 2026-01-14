# True Random Dice Roller MCP Integration

**Status:** ACTIVE  
**Priority:** MANDATORY for all NPC and system dice rolls  
**Location:** `C:\DnD\DnD_Cursor\mcp_servers\dice_roller\`

## Overview

The True Random Dice Roller MCP provides cryptographically secure random number generation for all dice rolls. This replaces pre-rolled dice pools and ensures truly random, auditable results.

## When to Use MCP Dice Roller (MANDATORY)

### ✅ ALWAYS Use MCP Dice Roller For:

1. **NPC Combat Rolls**
   - Attack rolls (use `roll_attack` with character name, weapon, modifier)
   - Damage rolls (use `roll_dice` with damage formula)
   - Saving throws (use `roll_saving_throw` with ability, DC, modifier)

2. **NPC Skill Checks**
   - Perception checks (use `roll_dice` with "1d20+modifier")
   - Stealth checks
   - Investigation, Insight, etc.

3. **Random Encounters**
   - Encounter check rolls (1d20)
   - Encounter type rolls (1d12 for Triboar Trail table)
   - Creature quantity rolls (1d4+2, 2d4, etc.)

4. **Initiative**
   - NPC initiative (use `roll_initiative` with all combatants)
   - Party initiative (can roll all at once)

5. **Random Events**
   - Loot rolls
   - Trap detection DCs
   - Any other random determination

6. **Monster Behavior**
   - Random target selection
   - Morale checks
   - Reaction rolls

### 🎲 Available MCP Dice Roller Functions:

#### 1. `mcp_dice-roller_roll_dice`
**General purpose dice rolling**
```
Parameters:
  - dice_expression: "1d20", "2d6+3", "8d6", etc.
  - reason: Why this roll is happening
  - character (optional): Who is rolling

Example: Roll Perception check for goblin
  dice_expression: "1d20+2"
  reason: "Goblin Perception check to spot party"
  character: "Goblin Scout"
```

#### 2. `mcp_dice-roller_roll_attack`
**Attack rolls with automatic modifier calculation**
```
Parameters:
  - character: Name of attacker
  - weapon: Weapon being used
  - modifier: Attack bonus
  - target_ac (optional): Target AC for hit/miss
  - advantage (optional): true/false
  - disadvantage (optional): true/false

Example: Goblin attacks Brevin
  character: "Goblin"
  weapon: "Scimitar"
  modifier: 4
  target_ac: 15
```

#### 3. `mcp_dice-roller_roll_saving_throw`
**Saving throws with automatic success/fail**
```
Parameters:
  - character: Who is making the save
  - ability: "Dexterity", "Constitution", etc.
  - modifier: Save bonus
  - dc: Difficulty Class
  - advantage (optional): true/false
  - disadvantage (optional): true/false

Example: Goblin Dexterity save vs fireball
  character: "Goblin"
  ability: "Dexterity"
  modifier: 2
  dc: 15
```

#### 4. `mcp_dice-roller_roll_initiative`
**Initiative for all combatants at once**
```
Parameters:
  - combatants: JSON array of {name, modifier, advantage (optional)}

Example: Combat starts
  combatants: [
    {"name": "Brevin", "modifier": 4},
    {"name": "Goblin 1", "modifier": 2},
    {"name": "Goblin 2", "modifier": 2},
    {"name": "Bugbear", "modifier": 1}
  ]
```

#### 5. `mcp_dice-roller_get_roll_history`
**Retrieve audit trail of recent rolls**
```
Parameters:
  - limit (optional): Number of rolls to retrieve (default: 10)
  - character (optional): Filter by character name

Example: Check last 5 rolls
  limit: 5
```

## Integration with Combat System

### OLD System (Dice Pools):
```
Pre-roll 25 attack rolls and 25 damage rolls at encounter start
Consume from pool during combat
Fast but predictable
```

### NEW System (True Random MCP):
```
Roll dice in real-time using MCP during combat
Each roll is cryptographically secure
Fully auditable
Only slightly slower (~0.5 seconds per roll)
```

### Workflow for NPC Combat Turn:

**BEFORE (with dice pools):**
1. Get next roll from pool
2. Apply to attack
3. If hit, get next damage roll from pool
4. Apply damage

**NOW (with MCP):**
1. Call `roll_attack` with NPC stats
2. MCP returns attack total and hit/miss
3. If hit, call `roll_dice` with damage formula
4. MCP returns damage total
5. Apply damage

## Integration with REFEREE Agent

**CRITICAL: REFEREE agent MUST use MCP dice roller for ALL NPC rolls.**

### REFEREE Output Format:

```json
{
  "roll_request": {
    "required": false,
    "type": "none",
    "ability": "none",
    "dc": 0,
    "skill": "none",
    "note": "none"
  },
  "mechanics_notes": "Goblin attacks Brevin. MCP Roll: 1d20+4 = 18 vs AC 15 (HIT). Damage: 1d6+2 = 7 slashing damage.",
  "npc_rolls": [
    {
      "npc": "Goblin",
      "action": "Attack with Scimitar",
      "attack_roll": {
        "mcp_call": "roll_attack",
        "character": "Goblin",
        "weapon": "Scimitar",
        "modifier": 4,
        "target_ac": 15,
        "result": 18,
        "hit": true
      },
      "damage_roll": {
        "mcp_call": "roll_dice",
        "dice_expression": "1d6+2",
        "reason": "Goblin scimitar damage vs Brevin",
        "result": 7
      }
    }
  ]
}
```

## Integration with Parallel Agent Pipeline

### When Processing NPC Turns:

1. **REFEREE agent generates agent output** (dnd_out_REFEREE.json)
   - Determines NPC action
   - **IMPORTANT: REFEREE does NOT call MCP directly**
   - Instead, REFEREE specifies what rolls are needed

2. **AI Assistant (me) processes REFEREE output**
   - Reads REFEREE's roll requirements
   - **Calls MCP dice roller for each required roll**
   - Updates mechanics_notes with roll results
   - Passes results to NARRATOR

3. **NARRATOR creates narrative** using roll results
   - Describes attack hitting or missing
   - Describes damage impact
   - Creates cinematic turn narrative

4. **STATE_PATCHER updates state** with results
   - Applies damage to character HP
   - Updates combat status
   - Logs turn narrative

## Performance Considerations

### Speed Comparison:
- **Dice Pool System:** ~0.1 seconds per roll (pre-rolled)
- **MCP True Random:** ~0.5 seconds per roll (real-time)
- **Trade-off:** +0.4 seconds per roll for true randomness and auditability

### Optimization Strategy:
- **NPC turns with 1 attack:** +0.5 seconds (acceptable)
- **NPC turns with multi-attack (2-3 attacks):** +1-1.5 seconds (acceptable)
- **Boss encounters with many rolls:** May accumulate, but still fast enough

**Conclusion:** MCP dice roller is fast enough for real-time use, with the benefit of true randomness and full audit trail.

## Audit Trail Benefits

### Every Roll is Logged:
- Timestamp
- Character/NPC name
- Roll type (attack, damage, save, check)
- Formula used
- Result
- Reason for roll

### Audit Log Location:
`C:\DnD\DnD_Cursor\mcp_servers\dice_roller\dice_roll_audit.log`

### Use Cases:
- Verify combat results
- Check for patterns or bias
- Review past encounters
- Dispute resolution

## Migration from Dice Pools

### Status:
- **Dice Pool System:** DEPRECATED (kept for reference, no longer used)
- **MCP True Random:** ACTIVE (mandatory for all NPC/system rolls)

### If Dice Pools Still Exist in State:
- Ignore them
- Do NOT consume from pools
- Always call MCP dice roller instead

### Update Required Files:
- ✅ `TRUE_RANDOM_DICE_INTEGRATION.md` (this file)
- ⏳ `.cursorrules` (update combat rules to mandate MCP usage)
- ⏳ `COMBAT_DICE_POOL_SYSTEM.md` (mark as deprecated)
- ⏳ `ENCOUNTER_EXECUTION_GUIDE.md` (update to reference MCP roller)

## Examples in Practice

### Example 1: Goblin Ambush
```
AI: Rolling initiative for combat...
[Calls MCP: roll_initiative with party + 3 goblins]
MCP Result: Brevin (20), Goblin 1 (18), Vandross (16), Goblin 2 (15), Torgga (10), Goblin 3 (8)

AI: Goblin 1 attacks Brevin with scimitar...
[Calls MCP: roll_attack, character="Goblin 1", weapon="Scimitar", modifier=4, target_ac=15]
MCP Result: Rolled 14, Total 18 vs AC 15 (HIT)

AI: Rolling damage...
[Calls MCP: roll_dice, dice_expression="1d6+2", reason="Goblin scimitar damage"]
MCP Result: Rolled [5], Total 7

AI: Goblin 1's scimitar slashes Brevin for 7 slashing damage!
```

### Example 2: Random Encounter Check
```
AI: Checking for random encounters on Triboar Trail...
[Calls MCP: roll_dice, dice_expression="1d20", reason="Triboar Trail encounter check - day"]
MCP Result: Rolled [18], Total 18 (17-20 = encounter!)

AI: An encounter occurs! Rolling encounter type...
[Calls MCP: roll_dice, dice_expression="1d12", reason="Triboar Trail encounter type"]
MCP Result: Rolled [7], Total 7 (Hobgoblin squad)

AI: Rolling number of hobgoblins...
[Calls MCP: roll_dice, dice_expression="1d4+3", reason="Hobgoblin squad size"]
MCP Result: Rolled [3], Total 6 hobgoblins

AI: A squad of 6 hobgoblins appears on the trail ahead!
```

### Example 3: Trap Saving Throw
```
AI: Brevin steps on the pressure plate. Darts shoot from the walls!
AI: Rolling Dexterity save for Brevin...
[Calls MCP: roll_saving_throw, character="Brevin", ability="Dexterity", modifier=7, dc=15]
MCP Result: Rolled 12, Total 19 vs DC 15 (SUCCESS)

AI: Brevin deftly dodges the poisoned darts!
```

## Summary

**MANDATORY RULE:** The AI assistant (me) MUST use the MCP True Random Dice Roller for ALL NPC and system dice rolls. This ensures:
- True randomness (cryptographically secure)
- Full auditability (every roll logged)
- Transparency (players can verify results)
- Fair gameplay (no predictable patterns)

**Performance Impact:** Minimal (~0.5 seconds per roll), acceptable for real-time gameplay.

**Dice Pool System:** DEPRECATED. Do not use pre-rolled dice pools.

**Audit Trail:** All rolls logged to `dice_roll_audit.log` with timestamps and context.

---

**Reference:** Created 2026-01-13 to document MCP dice roller integration.















