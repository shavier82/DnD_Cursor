# Combat Dice Pool System

**Status:** ⚠️ DEPRECATED (Replaced by MCP True Random Dice Roller)  
**Replacement:** See `TRUE_RANDOM_DICE_INTEGRATION.md` and `MCP_DICE_ROLLER_QUICK_REFERENCE.md`  
**Purpose:** [HISTORICAL] Speed Optimization - Pre-roll dice pools to eliminate rolling during combat  

## ⚠️ DEPRECATION NOTICE

This system is **NO LONGER USED** as of 2026-01-13. It has been replaced by the **MCP True Random Dice Roller** system, which provides:
- Cryptographically secure random number generation
- Full audit trail for all rolls
- Real-time rolling with acceptable performance (~0.5 seconds per roll)
- Transparent and verifiable results

**DO NOT USE THIS SYSTEM.** Always use the MCP dice roller instead.

See:
- `docs/TRUE_RANDOM_DICE_INTEGRATION.md` - Complete integration guide
- `docs/MCP_DICE_ROLLER_QUICK_REFERENCE.md` - Quick function reference
- `.cursorrules` - MCP TRUE RANDOM DICE ROLLER section

---

## [HISTORICAL] Original Documentation - Combat Dice Pool System

### Overview

To accelerate combat processing, at the start of each encounter, **pre-roll dice pools** for all enemies. This eliminates the need to roll dice during enemy turns, dramatically speeding up combat resolution.

### System Rules

#### 1. Pool Creation (Encounter Start)

When combat is initiated:

1. **For each enemy, create two pools:**
   - **Hit Pool**: Array of attack roll results (1d20 + modifiers)
   - **Damage Pool**: Array of damage roll results (based on weapon/spell)

2. **Pool size:** Generate 20-30 rolls per pool (enough for a typical encounter)

3. **Store pools in CURRENT_STATE.json:**
   ```json
   {
     "combat": {
       "dice_pools": {
         "Goblin_1": {
           "hit_pool": [18, 14, 7, 22, 15, ...],
           "damage_pool": [5, 8, 3, 7, 6, ...],
           "hit_index": 0,
           "damage_index": 0
         }
       }
     }
   }
   ```

#### 2. Pool Consumption (Enemy Turns)

When an enemy acts:

1. **Attack Roll:**
   - Get `hit_pool[hit_index]`
   - Increment `hit_index` by 1
   - Compare result vs target AC

2. **Damage Roll (if hit):**
   - Get `damage_pool[damage_index]`
   - Increment `damage_index` by 1
   - Apply damage to target

3. **Update state** with new indices

#### 3. Benefits

- **Speed:** No dice rolling during combat (50-70% faster)
- **Consistency:** Rolls are pre-calculated and stored
- **No delays:** Eliminates tool calls during enemy turns

### Example Workflow

```
Combat Initiated → Generate pools for all enemies → Store in state
↓
Enemy Turn 1 → Use hit_pool[0] → If hit, use damage_pool[0] → Increment indices
↓
Enemy Turn 2 → Use hit_pool[1] → If hit, use damage_pool[1] → Increment indices
↓
Continue until combat ends
```

### Performance Impact

- **Without pools:** ~30-60 seconds per enemy turn (rolling + processing)
- **With pools:** ~5-10 seconds per enemy turn (lookup only)
- **Savings:** ~20-50 seconds per enemy turn

---

**Note:** This system is deprecated. Use MCP True Random Dice Roller instead for truly random, auditable results.
