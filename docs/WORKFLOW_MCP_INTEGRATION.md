# Workflow-MCP Integration Guide

**How the workflow system integrates with MCP tools for automatic Obsidian sync.**

---

## Current State

The workflow system provides:
- ✅ Structured reminders for what to do
- ✅ Workflow state tracking
- ✅ Validation of what was done
- ⚠️ **But does NOT automatically call MCP tools**

**Why?** The workflow script runs as a Python subprocess and cannot directly call MCP tools. MCP tools are only available to the AI agent through the MCP protocol.

---

## Solution: AI Agent Must Call MCP Tools

When the workflow is triggered, the AI agent (me) must:

1. **Run the workflow script** (provides structure and validation)
2. **IMMEDIATELY call the required MCP tools** (actually does the work)
3. **Verify completion** (check workflow state)

---

## Integration Patterns

### Pattern 1: Spell Cast Workflow

**Workflow Trigger:**
```bash
python scripts/dm_workflow.py spell_cast --character Zephyr --level 3
```

**AI Agent Must Then:**
```python
# IMMEDIATELY after workflow runs:
mcp_obsidian-sync_use_spell_slot(
    character_name="Zephyr_Sparkwhistle",
    spell_level=3
)
```

**Result:**
- ✅ Workflow state tracked
- ✅ Spell slot deducted in Obsidian
- ✅ Real-time sync complete

---

### Pattern 2: Post-Combat Workflow

**Workflow Trigger:**
```bash
python scripts/dm_workflow.py post_combat --combat-id combat_123
```

**AI Agent Must Then:**
```python
# Step 1: End combat
mcp_combat-engine_end_combat_tool(combat_id="combat_123")

# Step 2: Calculate XP (from defeated enemies)
# Example: 2 Goblins (CR 1/4 each) = 100 XP total, 2 PCs = 50 XP each
total_xp = 100
xp_per_pc = total_xp / 2  # 50 XP each

# Step 3: Update XP for EACH PC
mcp_obsidian-sync_update_character_xp(
    character_name="Torgga_Brawnanvil",
    xp_to_add=50
)
mcp_obsidian-sync_update_character_xp(
    character_name="Eglath_Bearkiller",
    xp_to_add=50
)

# Step 4: Roll currency loot
# Example: 2d6 cp, 2d4 sp per goblin
# (Use dice-roller MCP for this)

# Step 5: Update currency for EACH PC
mcp_obsidian-sync_update_character_currency(
    character_name="Torgga_Brawnanvil",
    cp=3,  # Example: 7 cp / 2 PCs = 3 each + 1 remainder
    sp=2   # Example: 5 sp / 2 PCs = 2 each + 1 remainder
)
mcp_obsidian-sync_update_character_currency(
    character_name="Eglath_Bearkiller",
    cp=3,
    sp=2
)

# Step 6: List items (ask players what they want)

# Step 7: Add chosen items
mcp_obsidian-sync_add_inventory_item(
    character_name="Torgga_Brawnanvil",
    item_name="Arrow",
    quantity=8,
    weight=0.4
)
```

**Result:**
- ✅ Workflow state tracked
- ✅ XP distributed to Obsidian
- ✅ Currency distributed to Obsidian
- ✅ Items added to Obsidian
- ✅ Real-time sync complete

---

### Pattern 3: Resource Use (Rage, Ki, etc.)

**When resource is used:**
```python
# IMMEDIATELY call:
mcp_obsidian-sync_use_resource(
    character_name="Eglath_Bearkiller",
    resource_name="rage",
    current=2,  # Current value after use
    maximum=3   # Maximum value
)
```

**Or via combat-engine:**
```python
mcp_combat-engine_use_resource(
    combat_id="combat_123",
    creature_id="eglath_bearkiller",
    resource_name="rage",
    current=2,
    maximum=3,
    amount=1
)
```

**Result:**
- ✅ Resource deducted in Obsidian
- ✅ Real-time sync complete

---

### Pattern 4: HP Changes

**When HP changes:**
```python
# IMMEDIATELY call:
mcp_obsidian-sync_update_character_hp(
    character_name="Torgga_Brawnanvil",
    new_hp=35,  # Current HP after damage
    max_hp=52   # Maximum HP
)
```

**Or via combat-engine:**
```python
# Combat-engine automatically syncs HP, but you can also:
mcp_combat-engine_apply_healing(
    combat_id="combat_123",
    creature_id="torgga_brawnanvil",
    healing_amount=10
)
# This automatically syncs to Obsidian
```

**Result:**
- ✅ HP updated in Obsidian
- ✅ Real-time sync complete

---

## Available MCP Tools for Obsidian Sync

### Character Data
- `mcp_obsidian-sync_update_character_hp(character_name, new_hp, max_hp)` - Update HP
- `mcp_obsidian-sync_update_character_xp(character_name, xp_to_add)` - Add XP
- `mcp_obsidian-sync_update_character_currency(character_name, cp, sp, gp, pp)` - Update currency
- `mcp_obsidian-sync_use_spell_slot(character_name, spell_level)` - Deduct spell slot
- `mcp_obsidian-sync_use_resource(character_name, resource_name, current, maximum)` - Use resource

### Inventory
- `mcp_obsidian-sync_add_inventory_item(character_name, item_name, quantity, weight)` - Add item
- `mcp_obsidian-sync_remove_inventory_item(character_name, item_name, quantity)` - Remove item
- `mcp_obsidian-sync_add_weapon(character_name, weapon_name, attack_bonus, damage, properties)` - Add weapon
- `mcp_obsidian-sync_add_armor(character_name, armor_name, ac_bonus, armor_type, properties)` - Add armor
- `mcp_obsidian-sync_add_magic_item(character_name, item_name, properties, charges, attuned)` - Add magic item

### Combat Integration
- `mcp_combat-engine_use_spell_slot(combat_id, creature_id, spell_level)` - Use spell slot (auto-syncs)
- `mcp_combat-engine_use_resource(combat_id, creature_id, resource_name, current, maximum)` - Use resource (auto-syncs)
- `mcp_combat-engine_apply_healing(combat_id, creature_id, healing_amount)` - Apply healing (auto-syncs)

---

## Workflow Enhancement Needed

The workflow system should be enhanced to:

1. **Provide structured MCP tool call templates** - Show exactly which tools to call with what parameters
2. **Track MCP tool calls** - Verify that tools were actually called
3. **Validate Obsidian sync** - Check that Obsidian files were actually updated

**Current limitation:** Workflow script can't call MCP tools directly, so AI agent must do it.

**Solution:** Make it crystal clear in `.cursorrules` that when workflows trigger, MCP tools MUST be called immediately.

---

## Updated Workflow Execution Pattern

### For Spell Casting

```
1. Workflow triggered: python scripts/dm_workflow.py spell_cast --character Zephyr --level 3
2. AI agent IMMEDIATELY calls: mcp_obsidian-sync_use_spell_slot("Zephyr_Sparkwhistle", 3)
3. Workflow state updated: Spell slot tracked
4. Validation: Check Obsidian file was updated
```

### For Post-Combat

```
1. Workflow triggered: python scripts/dm_workflow.py post_combat --combat-id combat_123
2. AI agent IMMEDIATELY calls:
   - end_combat_tool(combat_id)
   - update_character_xp() for EACH PC
   - update_character_currency() for EACH PC
   - add_inventory_item() for chosen items
3. Workflow state updated: Post-combat procedures tracked
4. Validation: Check all Obsidian files were updated
```

---

## Enforcement

**In `.cursorrules`:**
- When workflow is triggered, AI MUST immediately call the required MCP tools
- Cannot proceed until MCP tools are called
- Workflow state must show completion

**Validation:**
- Check workflow state file to verify procedures were completed
- Check Obsidian files to verify data was actually updated
- Run validation script to verify everything

---

## Summary

**Current State:**
- ✅ Workflow provides structure and reminders
- ⚠️ Workflow does NOT automatically call MCP tools
- ✅ AI agent must call MCP tools when workflow triggers

**What's Needed:**
- ✅ Clear instructions in `.cursorrules` to call MCP tools immediately
- ✅ Workflow provides structured templates for MCP tool calls
- ✅ Validation to verify MCP tools were actually called

**The workflow system provides the structure, but the AI agent must actually execute the MCP tool calls.**

---

**Last Updated:** 2026-01-16  
**Status:** ⚠️ Workflow provides structure, but MCP tool calls must be made by AI agent
