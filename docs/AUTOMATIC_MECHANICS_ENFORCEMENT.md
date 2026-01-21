# Automatic Mechanics Enforcement - Preventing AI Forgetfulness

## Problem
The AI DM was forgetting to:
1. Deduct spell slots when used
2. Add skill modifiers to dice rolls
3. Update character resources automatically
4. Follow mandatory procedures

## Solution: Multi-Layer Enforcement System

### Layer 1: MCP Tools (Automatic)
**ALWAYS use MCP tools instead of manual file edits:**

| Action | MCP Tool | When to Use |
|--------|----------|-------------|
| Spell slot used | `mcp_combat-engine_use_spell_slot(combat_id, creature_id, spell_level)` | ANY spell slot use (combat or out of combat) |
| HP changed | `mcp_obsidian-sync_update_character_hp(character_name, new_hp, max_hp)` | After ANY HP change |
| XP gained | `mcp_obsidian-sync_update_character_xp(character_name, xp_to_add)` | After combat, quest completion |
| Resource used | `mcp_combat-engine_use_resource(combat_id, creature_id, resource_name, current, maximum)` | Rage, Ki, Channel Divinity, etc. |
| Skill check | `mcp_dice-roller_roll_dice(1d20, reason, character)` + add skill bonus from character sheet | ALL skill checks |

### Layer 2: Checklist Enforcement
**The `MECHANICS_AUTOMATION_CHECKLIST.md` is MANDATORY:**
- Pre-session validation blocks session if not read
- Context reminders trigger before critical operations
- All procedures documented with exact tool calls

### Layer 3: Skill Modifiers
**ALWAYS add full skill bonus (not just ability modifier):**
1. Check character sheet for skill bonus
2. Roll 1d20
3. Add skill bonus (ability + proficiency/expertise)
4. Compare to DC

**Example:**
- Brevin's Stealth: Roll 15 + 9 (skill bonus) = 24
- NOT: Roll 15 + 3 (DEX only) = 18

### Layer 4: Automatic Reminders
**Run `python scripts/mechanics_reminder.py <context>` before:**
- `spell_cast` - Reminds to use `use_spell_slot`
- `post_combat` - Reminds all post-combat procedures
- `skill_check` - Reminds to add skill modifiers

## Critical Rules

### ❌ NEVER:
- Manually edit Obsidian files for spell slots, HP, XP, resources
- Roll dice without adding skill modifiers
- Skip MCP tool calls
- Guess mechanics (always use MCP lookup tools)

### ✅ ALWAYS:
- Use MCP tools for all character data updates
- Add full skill bonuses to skill checks
- Check character sheets for exact bonuses
- Use MCP lookup tools for rules/spells/monsters

## Workflow Examples

### Spell Slot Used (Out of Combat)
```
1. Zephyr uses spell slot to recharge crystal
2. IMMEDIATELY call: mcp_combat-engine_use_spell_slot(
       combat_id="none" or create temporary,
       creature_id="Zephyr_Sparkwhistle",
       spell_level=1
   )
3. Continue with action
```

### Skill Check
```
1. Player wants to pick lock
2. Check Brevin's character sheet: Thieves' Tools +6
3. Roll: mcp_dice-roller_roll_dice("1d20", "lock picking", "Brevin")
4. Result: 19 + 6 (skill bonus) = 25 vs DC 15 → Success
```

## Enforcement Status

✅ **Implemented:**
- Pre-session validation (blocks session)
- Context reminders (triggers before operations)
- Checklist documentation (mandatory reference)
- MCP tools available (use them!)

🚧 **Needs Improvement:**
- AI must remember to use MCP tools (not manual edits)
- AI must add skill bonuses automatically
- AI must check character sheets for exact values

## Next Steps

1. **Always use MCP tools** - Never manually edit files
2. **Always add skill bonuses** - Check character sheets first
3. **Run reminders** - Use `mechanics_reminder.py` before critical operations
4. **Reference checklist** - Check `MECHANICS_AUTOMATION_CHECKLIST.md` when unsure
