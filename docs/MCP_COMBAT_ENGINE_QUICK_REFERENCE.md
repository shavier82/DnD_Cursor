# MCP Combat Engine Quick Reference

**Purpose:** Comprehensive D&D 5e combat management with AI-driven enemies, positioning, and automatic HP/resource tracking

---

## Core Functions

### 1. Start Combat
```python
start_combat(
    encounter_id="goblin_ambush_1",
    encounter_name="Goblin Ambush",
    battlefield_width=20,
    battlefield_height=20,
    character_ids=["Brevin", "Eglath Bearkiller", "Torgga Brawnanvil", "Vandross Ephrates"],
    monster_data=[{
        "creature_id": "goblin_1",
        "name": "Goblin Archer",
        "creature_type": "monster",
        "max_hp": 7,
        "current_hp": 7,
        "ac": 15,
        "strength": 8,
        "dexterity": 14,
        # ... other stats
    }]
)
```
- Initializes combat state
- Loads player characters from Google Sheets
- Creates battlefield grid
- Returns combat_id for all subsequent calls

### 2. Roll Initiative
```python
roll_initiative_tool(
    combat_id="goblin_ambush_1",
    initiative_rolls={
        "brevin": 22,
        "eglath_bearkiller": 14,
        "goblin_1": 18,
    }
)
```
- Set initiative for all combatants
- Automatically sorts initiative order
- Returns turn order

### 3. Next Turn
```python
next_turn_tool(combat_id="goblin_ambush_1")
```
- Advances to next creature in initiative
- Resets turn state (action, bonus action, movement)
- Ticks condition durations
- Checks for combat end

### 4. Get Combat Status
```python
get_combat_status(combat_id="goblin_ambush_1")
```
- Returns full combat state:
  - Current turn (creature, initiative)
  - All combatants (HP, AC, conditions)
  - Round number
  - Combat active status

### 5. Attack
```python
attack_tool(
    combat_id="goblin_ambush_1",
    attacker_id="brevin",
    target_id="goblin_1",
    weapon_type="melee",
    attack_roll=18,
    damage_roll=12,
    damage_type="piercing"
)
```
- Processes attack with cover, distance, LOS checks
- Applies damage (accounting for resistances)
- Tracks damage dealt/taken
- Checks for death

### 6. Move Creature
```python
move_creature(
    combat_id="goblin_ambush_1",
    creature_id="brevin",
    new_x=5,
    new_y=10,
    new_z=0
)
```
- Moves creature on battlefield grid
- Checks movement range
- Validates position (passable, not occupied)
- Updates movement used

### 7. Get AI Action
```python
get_ai_action(
    combat_id="goblin_ambush_1",
    creature_id="goblin_1"
)
```
- AI selects target (balanced strategy)
- AI decides action (attack, spell, ability, disengage, dodge, dash)
- Returns action details to execute

### 8. End Combat
```python
end_combat_tool(combat_id="goblin_ambush_1")
```
- Syncs player HP/resources to Google Sheets
- Records combat duration and rounds
- Cleans up combat state

---

## Combat Flow

### Standard Turn Sequence:
```
1. next_turn() → Get current combatant
2. IF player:
     - Wait for player action input
     - Execute player action (attack, spell, move)
   ELSE:
     - get_ai_action() → Get AI decision
     - Execute AI action automatically
3. Repeat until combat ends
4. end_combat() → Sync to sheets
```

---

## AI Strategies

The AI uses intelligent decision-making:

### Target Selection:
- **Balanced** (default): Smart scoring (HP%, concentration, distance, threat)
- **Priority**: Concentrating/low HP enemies first
- **Nearest**: Closest enemy
- **Weakest**: Lowest HP enemy

### Action Priority:
1. **Flee** if very low HP and outnumbered
2. **AoE spell** if 3+ enemies clustered
3. **Ranged attack** if no adjacent enemies and range available
4. **Melee attack** if adjacent enemy
5. **Move and attack** if enemy within move+attack range
6. **Dash** if enemy far away
7. **Dodge** if surrounded and low HP

### Tactical Positioning:
- **Engage**: Move toward melee range
- **Maintain Range**: Keep 15-60 feet for ranged attacks
- **Retreat**: Move away from all enemies
- **Flank**: Position opposite ally
- **Cover**: Move to terrain with cover

---

## Features

### HP & Resources:
- Current HP, max HP, temp HP
- Damage resistances/immunities/vulnerabilities
- Spell slot tracking
- Death saves (players only)

### Positioning:
- Grid-based battlefield (5-foot squares)
- Terrain (impassable, difficult, cover)
- Distance calculations (D&D 5e diagonal rules)
- Line of sight checks
- Cover bonuses (+2 half, +5 three-quarters, total)

### Conditions:
- All 15 standard D&D 5e conditions
- Duration tracking (rounds, minutes, until save)
- Automatic expiration
- Effects on stats (speed, attacks, saves)

### AoE Calculations:
- Sphere (Fireball)
- Cube (Thunderwave)
- Cone (Burning Hands)
- Line (Lightning Bolt)
- Accurate creature detection

---

## Integration

### With Other MCPs:

**dice-roller:**
- Use for all attack rolls, damage rolls, initiative
- Combat engine validates and applies results

**rules-database:**
- Load monster stats before combat
- Check condition effects
- Lookup spell details for spell attacks

**music-ambience:**
- Auto-play combat music on start_combat
- Play sound effects on attacks/spells

**session-recorder:**
- Auto-log combat start/end
- Log significant events (crits, deaths)

**Google Sheets:**
- Load character data at combat start
- Sync HP/spell slots after combat end

---

## Example Usage

```python
# 1. Start
start_combat(
    encounter_id="cave_fight",
    character_ids=["Brevin", "Eglath Bearkiller"],
    monster_data=[lookup_monster("Goblin"), lookup_monster("Bugbear")]
)

# 2. Initiative
roll_initiative_tool(combat_id="cave_fight", initiative_rolls={...})

# 3. Enemy turn (automatic)
ai_action = get_ai_action(combat_id="cave_fight", creature_id="goblin_1")
# AI says: attack nearest (Brevin)
attack_roll = roll_attack(...)
attack_tool(combat_id="cave_fight", attacker_id="goblin_1", target_id="brevin", ...)

# 4. Player turn
attack_roll = roll_attack(...)
attack_tool(combat_id="cave_fight", attacker_id="brevin", target_id="goblin_1", ...)

# 5. Continue...
next_turn_tool(combat_id="cave_fight")

# 6. End
end_combat_tool(combat_id="cave_fight")
```

---

## Best Practices

1. **Always use dice-roller MCP** for randomness, not Python random
2. **Always check AI action before executing** - validate it makes sense
3. **Track movement** - check remaining movement before moving
4. **Apply cover bonuses** - automatic in attack_tool
5. **Sync to sheets** - always call end_combat when done
6. **Use balanced AI** - most realistic enemy behavior

---

## Performance

- Initiative sort: <0.1s
- AI decision: ~0.5-1s
- Attack processing: <0.1s
- Turn advancement: <0.1s
- Target: <5s per enemy turn

---

## Status

**V1.0:** 9 core tools implemented
**Pattern:** Established for 25 total tools
**Ready:** Install dependencies, configure mcp.json, test

---

**Remember: Combat engine is OPTIONAL. Use for complex combats. Simple fights can use manual tracking with dice-roller + rules-database MCPs.**




