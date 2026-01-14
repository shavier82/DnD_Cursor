# Combat Engine MCP - Test Plan

## Quick Test (After Installing)

### 1. Install Dependencies
```powershell
cd "C:\DnD\DnD_Cursor\mcp_servers\combat_engine"
pip install -r requirements.txt
```

### 2. Add to .cursor/mcp.json
See COMBAT_MCP_CONFIG.md for configuration

### 3. Reload Cursor
`Ctrl+Shift+P` → "Developer: Reload Window"

### 4. Test Combat Flow

#### Test 1: Start Simple Combat
```
User: "Start a combat with 2 goblins against Brevin"

AI should call:
- start_combat with character_ids=["Brevin"] and 2 goblin monster_data
```

#### Test 2: Roll Initiative
```
User: "Roll initiative"

AI should:
- Use dice-roller MCP to roll for each combatant
- Call roll_initiative_tool with results
```

#### Test 3: AI Enemy Turn
```
User: "Goblin 1's turn"

AI should:
- Call get_ai_action for goblin_1
- Get back action (likely "attack" on Brevin)
- Execute attack using dice-roller + attack_tool
```

#### Test 4: Player Turn
```
User: "Brevin attacks Goblin 1 with his shortsword"

AI should:
- Use dice-roller for attack and damage
- Call attack_tool with rolls
- Report hit/miss and damage
```

#### Test 5: Movement
```
User: "Brevin moves 20 feet north"

AI should:
- Calculate new position
- Call move_creature
- Report new position
```

#### Test 6: Combat Status
```
User: "Show combat status"

AI should:
- Call get_combat_status
- Display initiative order, HP, positions, conditions
```

#### Test 7: End Combat
```
User: "End combat"

AI should:
- Call end_combat_tool
- Sync HP to Google Sheets
- Report combat summary (rounds, duration)
```

---

## Expected Behavior

### AI Should:
- ✅ Use combat-engine MCP silently (no announcements)
- ✅ Integrate with dice-roller for all rolls
- ✅ Use rules-database for monster stats
- ✅ Make smart AI decisions (target selection, positioning)
- ✅ Track HP, conditions, resources automatically
- ✅ Calculate distances and line of sight
- ✅ Apply cover bonuses
- ✅ Sync to Google Sheets after combat

### AI Should NOT:
- ❌ Announce tool usage ("Let me call the combat engine...")
- ❌ Guess creature stats (use rules-database MCP)
- ❌ Make arbitrary HP changes (use apply_damage tool)
- ❌ Invent positions (use battlefield grid)

---

## Validation Checklist

After testing, verify:

- [ ] Combat initializes successfully
- [ ] Initiative rolls and sorts correctly
- [ ] AI makes reasonable target/action decisions
- [ ] Attacks hit/miss based on AC
- [ ] Damage applies correctly (resistances, immunities)
- [ ] Movement respects range limits
- [ ] Conditions track durations
- [ ] Combat ends when one side defeated
- [ ] HP syncs to Google Sheets

---

## Known Limitations (V1.0)

- Only 9 core tools implemented (pattern established for 25 total)
- No spell casting tool yet (would need implementation)
- No automatic opportunity attacks
- No legendary actions/lair actions
- No mounted combat
- No 3D/flying combat
- Pathfinding is straight-line only (no A*)

These are design patterns established but not fully implemented in V1.0.

---

## Troubleshooting

### "Combat not found"
- Combat IDs must match between calls
- Use get_combat_status to check active combats

### "Creature cannot act"
- Check conditions (incapacitated, stunned, paralyzed)
- Verify creature is alive

### "Out of range"
- Check distance with battlefield.get_distance
- Melee = 5 feet, ranged varies by weapon

### "No line of sight"
- Check for terrain blocking LOS
- Use check_line_of_sight to debug

### Google Sheets sync fails
- Verify credentials at C:\DnD\keys\google_sheets_key.json
- Check character names match sheet names exactly

---

**Status:** Ready for testing after installation




