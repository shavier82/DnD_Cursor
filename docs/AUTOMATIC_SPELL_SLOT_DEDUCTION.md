# Automatic Spell Slot Deduction

## Problem
The AI DM was manually editing Obsidian files to deduct spell slots, which was error-prone and easy to forget.

## Solution
**ALWAYS use the MCP tool `mcp_obsidian-sync_use_spell_slot` instead of manual file edits.**

## When to Use

### ✅ Use MCP Tool For:
- **Spell casting** - When a player casts any spell
- **Spell slot use** - When a spell slot is used for ANY purpose (recharging items, powering mechanisms, etc.)
- **Out of combat** - Even when not in combat, use the MCP tool
- **Non-spell uses** - If a spell slot is expended for any reason

### ❌ Never:
- Manually edit the Obsidian markdown file
- Just roll dice without updating spell slots
- Assume spell slots are updated

## Tool Usage

```python
# CORRECT - Use MCP tool
mcp_obsidian-sync_use_spell_slot(
    character_name="Zephyr_Sparkwhistle",
    spell_level=1
)

# WRONG - Manual file edit
# search_replace(file_path, "●●●● (4/4)", "●●●○ (3/4)")
```

## Workflow

1. **Spell slot is used** (spell cast, item recharged, etc.)
2. **IMMEDIATELY** call `mcp_obsidian-sync_use_spell_slot(character_name, spell_level)`
3. **Continue** with the action (resolve spell effect, etc.)

## Enforcement

This is documented in `MECHANICS_AUTOMATION_CHECKLIST.md`:
- Section: "REAL-TIME OBSIDIAN SYNC (MANDATORY)"
- Section: "Spell Casting Workflow (MANDATORY)"

**The checklist is enforced by pre-session validation. This procedure cannot be skipped.**

## Related Tools

- `mcp_obsidian-sync_update_character_hp` - For HP changes
- `mcp_obsidian-sync_update_character_xp` - For XP gains
- `mcp_obsidian-sync_use_resource` - For class resources (Rage, Ki, etc.)
