# MCP Dice Roller Quick Reference

**MANDATORY:** Use MCP dice roller for ALL NPC and system rolls.

## Quick Function Reference

### 🎲 General Roll
```
Function: mcp_dice-roller_roll_dice
Use: Any dice roll (attacks, damage, checks, etc.)
Parameters:
  - dice_expression: "1d20", "2d6+3", "8d6-2"
  - reason: "Why rolling"
  - character (optional): "Who is rolling"
```

### ⚔️ Attack Roll
```
Function: mcp_dice-roller_roll_attack
Use: NPC/creature attack rolls
Parameters:
  - character: "Goblin"
  - weapon: "Scimitar"
  - modifier: 4
  - target_ac (optional): 15
  - advantage (optional): true/false
  - disadvantage (optional): true/false
```

### 🛡️ Saving Throw
```
Function: mcp_dice-roller_roll_saving_throw
Use: NPC/creature saving throws
Parameters:
  - character: "Goblin"
  - ability: "Dexterity" (or Str, Con, Int, Wis, Cha)
  - modifier: 2
  - dc: 15
  - advantage (optional): true/false
  - disadvantage (optional): true/false
```

### 🎯 Initiative
```
Function: mcp_dice-roller_roll_initiative
Use: Initiative for all combatants at once
Parameters:
  - combatants: [
      {"name": "Brevin", "modifier": 4},
      {"name": "Goblin", "modifier": 2}
    ]
```

### 📜 Roll History
```
Function: mcp_dice-roller_get_roll_history
Use: View recent rolls for audit/verification
Parameters:
  - limit (optional): 10
  - character (optional): "Brevin"
```

## Common Use Cases

### ✅ Combat Turn (Goblin)
```
1. Initiative: roll_initiative with all combatants
2. Attack: roll_attack (character="Goblin", weapon="Scimitar", modifier=4, target_ac=15)
3. If hit: roll_dice (dice_expression="1d6+2", reason="Goblin scimitar damage")
4. Apply damage to target
```

### ✅ Random Encounter
```
1. Encounter check: roll_dice (dice_expression="1d20", reason="Triboar Trail encounter check")
2. If 17-20: roll_dice (dice_expression="1d12", reason="Encounter type")
3. Quantity: roll_dice (dice_expression="1d4+2", reason="Number of stirges")
```

### ✅ Skill Check (NPC)
```
Perception: roll_dice (dice_expression="1d20+2", reason="Goblin Perception to spot party", character="Goblin Scout")
Stealth: roll_dice (dice_expression="1d20+6", reason="Goblin Stealth to hide", character="Goblin Scout")
```

### ✅ Trap/Hazard
```
Save: roll_saving_throw (character="Brevin", ability="Dexterity", modifier=7, dc=15)
Damage: roll_dice (dice_expression="2d10", reason="Falling debris damage")
```

## Integration Notes

- **ALWAYS use MCP for NPC rolls** (attacks, saves, checks, damage)
- **ALWAYS use MCP for random events** (encounters, loot, reactions)
- **Player rolls:** Still ask player to roll, then use their result
- **Audit trail:** All rolls logged automatically to `dice_roll_audit.log`
- **Performance:** ~0.5 seconds per roll (acceptable for real-time play)

## Dice Pool System: DEPRECATED

- ❌ Do NOT use pre-rolled dice pools
- ❌ Do NOT generate hit_pool/damage_pool at encounter start
- ❌ Do NOT consume from pools during combat
- ✅ ALWAYS call MCP dice roller in real-time instead

---

**Status:** ACTIVE  
**Priority:** MANDATORY  
**Created:** 2026-01-13















