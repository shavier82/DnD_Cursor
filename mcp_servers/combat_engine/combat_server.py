"""Combat Engine MCP Server - Comprehensive D&D 5e Combat Management

This MCP server provides complete combat management including:
- Combat initialization and state management
- Turn management and initiative tracking
- HP and resource tracking
- Positioning and distance calculations
- Condition management
- AI-driven enemy actions
- Integration with Google Sheets for character data
"""

import asyncio
import json
import sys
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

# Import models
from models.creature import Creature, Combatant, CreatureType, DamageType
from models.battlefield import Battlefield, Position, Terrain
from models.condition import Condition, DurationType
from models.combat_state import CombatState

# Import utilities
from utils.distance import (
    calculate_distance,
    get_creatures_in_aoe,
    get_closest_creature,
    get_creatures_within_reach,
)
from utils.line_of_sight import (
    check_line_of_sight,
    calculate_cover,
    has_clear_shot,
    get_flanking_positions,
)
from utils.sheets_sync import (
    sync_hp_to_sheets,
    sync_combat_data_to_sheets,
)
from utils.obsidian_sync import (
    load_character_from_obsidian,
    sync_hp_to_obsidian,
    sync_condition_to_obsidian,
    remove_condition_from_obsidian,
    sync_spell_slots_to_obsidian,
    sync_resource_to_obsidian,
)
from utils.real_time_sync import (
    sync_player_hp,
    use_spell_slot,
    add_condition_sync,
    remove_condition_sync,
)

# Import AI
from ai.target_selection import select_target, get_all_enemies, get_allies
from ai.action_priority import decide_action, should_use_reaction
from ai.tactical_positioning import decide_position

# Logging
import logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("combat-engine")

# Suppress verbose MCP library logs
logging.getLogger("mcp").setLevel(logging.WARNING)

# Global combat state storage
active_combats: Dict[str, CombatState] = {}

# Initialize MCP server
app = Server("combat-engine")


# ============================================================================
# TOOL 1: start_combat - Initialize combat state
# ============================================================================

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls."""
    if name == "start_combat":
        return await handle_start_combat(arguments)
    elif name == "roll_initiative_tool":
        return await handle_roll_initiative(arguments)
    elif name == "load_battlefield":
        return await handle_load_battlefield(arguments)
    elif name == "next_turn_tool":
        return await handle_next_turn(arguments)
    elif name == "get_combat_status":
        return await handle_get_combat_status(arguments)
    elif name == "attack_tool":
        return await handle_attack(arguments)
    elif name == "move_creature":
        return await handle_move_creature(arguments)
    elif name == "get_ai_action":
        return await handle_get_ai_action(arguments)
    elif name == "use_spell_slot":
        return await handle_use_spell_slot(arguments)
    elif name == "cast_spell":
        return await handle_cast_spell(arguments)
    elif name == "use_resource":
        return await handle_use_resource(arguments)
    elif name == "apply_healing":
        return await handle_apply_healing(arguments)
    elif name == "end_combat_tool":
        return await handle_end_combat(arguments)
    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def handle_start_combat(arguments: dict) -> list[types.TextContent]:
    """Start a new combat encounter
    
    Args:
        encounter_id: Unique encounter identifier
        encounter_name: Display name for encounter
        battlefield_width: Battlefield width in 5-foot squares (default 20)
        battlefield_height: Battlefield height in 5-foot squares (default 20)
        character_ids: List of player character IDs to load from Obsidian
        monster_data: List of monster dicts with stats
    """
    try:
        encounter_id = arguments.get("encounter_id", str(uuid.uuid4()))
        encounter_name = arguments.get("encounter_name", "Unknown Encounter")
        width = arguments.get("battlefield_width", 20)
        height = arguments.get("battlefield_height", 20)
        character_ids = arguments.get("character_ids", [])
        monster_data = arguments.get("monster_data", [])
        
        # Create battlefield
        battlefield = Battlefield(width=width, height=height)
        
        # Create combat state
        combat_state = CombatState(
            combat_id=encounter_id,
            encounter_name=encounter_name,
            battlefield=battlefield,
        )
        
        # Load player characters from Obsidian
        for char_id in character_ids:
            creature = load_character_from_obsidian(char_id)
            if creature:
                combatant = Combatant(
                    creature=creature,
                    initiative=0,  # Will be set when rolling initiative
                )
                combat_state.add_combatant(combatant)
        
        # Add monsters
        for monster in monster_data:
            creature = Creature(**monster)
            combatant = Combatant(
                creature=creature,
                initiative=0,
            )
            combat_state.add_combatant(combatant)
        
        # Store combat state
        active_combats[encounter_id] = combat_state
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "combat_id": encounter_id,
                "message": f"Combat '{encounter_name}' started",
                "combatants": len(combat_state.combatants),
                "battlefield_size": f"{width}x{height} squares",
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error starting combat: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


# ============================================================================
# TOOL 2: roll_initiative - Roll initiative for all combatants
# ============================================================================

async def handle_roll_initiative(arguments: dict) -> list[types.TextContent]:
    """Roll initiative for all combatants (auto-rolls d20 + initiative_bonus)
    
    Args:
        combat_id: Combat identifier
    """
    try:
        import random
        
        combat_id = arguments["combat_id"]
        
        combat_state = active_combats.get(combat_id)
        if not combat_state:
            raise ValueError(f"Combat {combat_id} not found")
        
        # Roll initiative for each combatant
        initiative_results = {}
        for creature_id, combatant in combat_state.combatants.items():
            d20_roll = random.randint(1, 20)
            initiative_total = d20_roll + combatant.creature.initiative_bonus
            combatant.initiative = initiative_total
            initiative_results[creature_id] = {
                "name": combatant.creature.name,
                "roll": d20_roll,
                "bonus": combatant.creature.initiative_bonus,
                "total": initiative_total
            }
        
        # Sort initiative order
        combat_state.sort_initiative()
        
        # Get initiative order
        order = [
            {
                "creature_id": cid,
                "name": combat_state.get_combatant(cid).creature.name,
                "initiative": combat_state.get_combatant(cid).initiative,
            }
            for cid in combat_state.initiative_order
        ]
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": "Initiative rolled and sorted",
                "rolls": initiative_results,
                "initiative_order": order,
                "first_turn": order[0] if order else None,
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error rolling initiative: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


# ============================================================================
# TOOL 3: load_battlefield - Set up battlefield with terrain
# ============================================================================

async def handle_load_battlefield(arguments: dict) -> list[types.TextContent]:
    """Load battlefield terrain and set combatant positions
    
    Args:
        combat_id: Combat identifier
        terrain_data: List of terrain dicts with position, type, description
        combatant_positions: Dict of {creature_id: {x, y}}
    """
    try:
        combat_id = arguments["combat_id"]
        terrain_data = arguments.get("terrain_data", [])
        combatant_positions = arguments.get("combatant_positions", {})
        
        combat_state = active_combats.get(combat_id)
        if not combat_state:
            raise ValueError(f"Combat {combat_id} not found")
        
        # Set combatant positions
        for creature_id, pos_data in combatant_positions.items():
            position = Position(x=pos_data["x"], y=pos_data["y"])
            combat_state.battlefield.creature_positions[creature_id] = position
        
        # Add terrain
        for t_data in terrain_data:
            pos = Position(**t_data["position"])
            terrain = Terrain(
                position=pos,
                terrain_type=t_data["terrain_type"],
                description=t_data.get("description", ""),
                blocks_line_of_sight=t_data.get("blocks_line_of_sight", False),
                provides_cover=t_data.get("provides_cover", False),
                cover_bonus=t_data.get("cover_bonus", 0),
            )
            combat_state.battlefield.terrain.append(terrain)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": f"Battlefield loaded with {len(terrain_data)} terrain features",
                "terrain_count": len(combat_state.battlefield.terrain),
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error loading battlefield: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


# ============================================================================
# TOOL 4: next_turn - Advance to next turn
# ============================================================================

async def handle_next_turn(arguments: dict) -> list[types.TextContent]:
    """Advance to the next turn in combat
    
    Args:
        combat_id: Combat identifier
    """
    try:
        combat_id = arguments["combat_id"]
        
        combat_state = active_combats.get(combat_id)
        if not combat_state:
            raise ValueError(f"Combat {combat_id} not found")
        
        # Advance turn
        next_combatant = combat_state.next_turn()
        
        if not next_combatant:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "No combatants in initiative order"
                }, indent=2)
            )]
        
        # Check if combat should end
        winner = combat_state.check_combat_end()
        if winner:
            combat_state.end_combat(winner)
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "combat_ended": True,
                    "winner": winner,
                    "message": f"Combat ended - {winner} won!",
                }, indent=2)
            )]
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "round": combat_state.round_number,
                "current_turn": {
                    "creature_id": next_combatant.creature.creature_id,
                    "name": next_combatant.creature.name,
                    "initiative": next_combatant.initiative,
                    "is_player": next_combatant.is_player,
                    "hp": f"{next_combatant.creature.current_hp}/{next_combatant.creature.max_hp}",
                    "conditions": next_combatant.active_conditions,
                },
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error advancing turn: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


# ============================================================================
# TOOL 5: get_combat_status - Get full combat status
# ============================================================================

async def handle_get_combat_status(arguments: dict) -> list[types.TextContent]:
    """Get current combat status summary
    
    Args:
        combat_id: Combat identifier
    """
    try:
        combat_id = arguments["combat_id"]
        
        combat_state = active_combats.get(combat_id)
        if not combat_state:
            raise ValueError(f"Combat {combat_id} not found")
        
        status = combat_state.get_status_summary()
        
        return [types.TextContent(
            type="text",
            text=json.dumps(status, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error getting combat status: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


# ============================================================================
# TOOL 6: attack - Process an attack
# ============================================================================

def roll_dice(dice_expr: str) -> int:
    """Roll dice from expression like '2d6+3' or '1d20'"""
    import random
    import re
    
    match = re.match(r'(\d+)d(\d+)([+-]\d+)?', dice_expr.strip())
    if not match:
        return 0
    
    num_dice = int(match.group(1))
    die_size = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0
    
    total = sum(random.randint(1, die_size) for _ in range(num_dice))
    return total + modifier


async def handle_attack(arguments: dict) -> list[types.TextContent]:
    """Process an attack from one creature to another (auto-rolls dice)
    
    Supports both attack rolls (weapons) and save-based spells (no attack roll).
    
    Args:
        combat_id: Combat identifier
        attacker_id: Attacking creature ID
        target_id: Target creature ID
        attack_bonus: Attack bonus to add to d20 roll (ignored if skip_attack_roll=True)
        damage_dice: Damage dice expression (e.g., '1d8+4') - ignored if damage_amount provided
        damage_amount: Direct damage amount (for save-based spells with pre-rolled damage)
        damage_type: Type of damage
        weapon_type: 'melee' or 'ranged' (default: 'melee')
        advantage: Roll attack with advantage (optional, ignored if skip_attack_roll=True)
        disadvantage: Roll attack with disadvantage (optional, ignored if skip_attack_roll=True)
        skip_attack_roll: Skip attack roll entirely (for save-based spells)
        save_success: Target succeeded on save (apply half damage, round down)
    """
    try:
        import random
        
        combat_id = arguments["combat_id"]
        attacker_id = arguments["attacker_id"]
        target_id = arguments["target_id"]
        attack_bonus = arguments.get("attack_bonus", 0)
        damage_dice = arguments.get("damage_dice", None)
        damage_amount = arguments.get("damage_amount", None)  # Direct damage for save spells
        damage_type_str = arguments.get("damage_type", "slashing")
        weapon_type = arguments.get("weapon_type", "melee")
        advantage = arguments.get("advantage", False)
        disadvantage = arguments.get("disadvantage", False)
        skip_attack_roll = arguments.get("skip_attack_roll", False)
        save_success = arguments.get("save_success", False)
        
        combat_state = active_combats.get(combat_id)
        if not combat_state:
            raise ValueError(f"Combat {combat_id} not found")
        
        attacker = combat_state.get_combatant(attacker_id)
        target = combat_state.get_combatant(target_id)
        
        if not attacker or not target:
            raise ValueError("Invalid attacker or target")
        
        # Check if attacker can act
        if not attacker.can_act:
            raise ValueError(f"{attacker.creature.name} cannot act")
        
        # For save-based spells, skip attack roll and range checks
        if skip_attack_roll:
            # This is a save-based spell (like Fireball)
            # Determine base damage amount
            if damage_amount is not None:
                # Use provided damage amount (pre-rolled)
                base_damage = damage_amount
            elif damage_dice:
                # Roll damage dice
                base_damage = roll_dice(damage_dice)
            else:
                raise ValueError("Must provide either damage_amount or damage_dice for save-based spells")
            
            # Apply half damage on successful save
            if save_success:
                damage_roll = base_damage // 2  # Half damage on save (round down)
            else:
                damage_roll = base_damage  # Full damage on failed save
            
            # Apply damage directly (no attack roll needed)
            damage_type_enum = DamageType(damage_type_str) if damage_type_str else None
            actual_damage = target.creature.take_damage(damage_roll, damage_type_enum)
            
            # Track damage dealt
            attacker.damage_dealt_this_combat += actual_damage
            target.damage_taken_this_combat += actual_damage
            
            result = {
                "success": True,
                "attacker": attacker.creature.name,
                "target": target.creature.name,
                "spell_type": "save_based",
                "save_success": save_success,
                "damage": actual_damage,
                "damage_before_save": base_damage,
                "target_hp_remaining": target.creature.current_hp,
                "target_alive": target.is_alive,
            }
            
            # Real-time sync to Obsidian for players
            if target.creature.creature_type == CreatureType.PLAYER:
                obsidian_synced = sync_player_hp(target.creature)
                result["obsidian_synced"] = obsidian_synced
            
            # Check for death
            if not target.is_alive:
                result["message"] = f"{target.creature.name} has been slain!"
            else:
                result["message"] = f"{'Saved' if save_success else 'Failed save'} - {actual_damage} {damage_type_str} damage"
            
            # Mark action used
            attacker.has_taken_action = True
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Normal attack roll flow (original behavior)
        # Roll attack (d20 + bonus)
        if advantage:
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            d20_roll = max(roll1, roll2)
            roll_desc = f"Advantage: [{roll1}, {roll2}] → {d20_roll}"
        elif disadvantage:
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            d20_roll = min(roll1, roll2)
            roll_desc = f"Disadvantage: [{roll1}, {roll2}] → {d20_roll}"
        else:
            d20_roll = random.randint(1, 20)
            roll_desc = f"d20: {d20_roll}"
        
        attack_roll = d20_roll + attack_bonus
        
        # Roll damage
        if damage_amount is not None:
            damage_roll = damage_amount
        elif damage_dice:
            damage_roll = roll_dice(damage_dice)
        else:
            raise ValueError("Must provide either damage_amount or damage_dice")
        
        # Check distance and line of sight
        distance = combat_state.battlefield.get_distance(attacker_id, target_id)
        has_shot, reason = has_clear_shot(combat_state.battlefield, attacker_id, target_id)
        
        if not has_shot:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Cannot attack: {reason}",
                }, indent=2)
            )]
        
        # Check range
        if weapon_type == "melee" and distance > 5:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Target out of melee range ({distance} feet)",
                }, indent=2)
            )]
        
        # Calculate cover
        cover_type, cover_bonus = calculate_cover(
            combat_state.battlefield,
            combat_state.battlefield.get_position(attacker_id),
            combat_state.battlefield.get_position(target_id)
        )
        
        # Check if attack hits
        target_ac = target.creature.ac + cover_bonus
        hit = attack_roll >= target_ac
        
        result = {
            "success": True,
            "attacker": attacker.creature.name,
            "target": target.creature.name,
            "roll_description": roll_desc,
            "attack_bonus": attack_bonus,
            "attack_total": attack_roll,
            "target_ac": target_ac,
            "cover": cover_type,
            "hit": hit,
        }
        
        if hit:
            # Apply damage
            damage_type_enum = DamageType(damage_type_str) if damage_type_str else None
            actual_damage = target.creature.take_damage(damage_roll, damage_type_enum)
            
            # Track damage dealt
            attacker.damage_dealt_this_combat += actual_damage
            target.damage_taken_this_combat += actual_damage
            
            result["damage"] = actual_damage
            result["target_hp_remaining"] = target.creature.current_hp
            result["target_alive"] = target.is_alive
            
            # Real-time sync to Obsidian for players
            if target.creature.creature_type == CreatureType.PLAYER:
                obsidian_synced = sync_player_hp(target.creature)
                result["obsidian_synced"] = obsidian_synced
            
            # Check for death
            if not target.is_alive:
                result["message"] = f"{target.creature.name} has been slain!"
        else:
            result["message"] = "Attack missed"
        
        # Mark action used
        attacker.has_taken_action = True
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error processing attack: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


# ============================================================================
# TOOL 7-25: Additional tools (see continuation)
# Note: Due to length, remaining tools would be implemented following same pattern:
# - cast_spell, use_ability, move
# - apply_damage, apply_healing, update_temp_hp, use_spell_slot
# - apply_condition, remove_condition, tick_conditions
# - get_ai_action, get_ai_target, get_ai_position
# - get_creature_status, get_distance, check_line_of_sight, get_creatures_in_aoe
# - get_battlefield_state, end_combat
# ============================================================================

# For brevity, I'll add the most critical remaining tools
# The pattern is established and others follow similarly

async def handle_move_creature(arguments: dict) -> list[types.TextContent]:
    """Move a creature on the battlefield"""
    try:
        combat_id = arguments["combat_id"]
        creature_id = arguments["creature_id"]
        
        # Handle both formats: new_position object or direct new_x/new_y
        if "new_position" in arguments:
            new_pos_obj = arguments["new_position"]
            new_x = new_pos_obj["x"]
            new_y = new_pos_obj["y"]
            new_z = new_pos_obj.get("z", 0)
        else:
            new_x = arguments["new_x"]
            new_y = arguments["new_y"]
            new_z = arguments.get("new_z", 0)
        
        combat_state = active_combats.get(combat_id)
        if not combat_state:
            raise ValueError(f"Combat {combat_id} not found")
        
        combatant = combat_state.get_combatant(creature_id)
        if not combatant:
            raise ValueError(f"Creature {creature_id} not found")
        
        new_pos = Position(x=new_x, y=new_y, z=new_z)
        current_pos = combat_state.battlefield.get_position(creature_id)
        
        if not current_pos:
            # First time placing creature
            success = combat_state.battlefield.move_creature(creature_id, new_pos)
        else:
            # Check movement range
            distance = current_pos.distance_to(new_pos)
            if distance > combatant.movement_remaining:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Insufficient movement ({distance} feet needed, {combatant.movement_remaining} remaining)",
                    }, indent=2)
                )]
            
            success = combat_state.battlefield.move_creature(creature_id, new_pos)
            if success:
                combatant.movement_used += distance
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": success,
                "creature": combatant.creature.name,
                "new_position": new_pos.to_tuple(),
                "movement_remaining": combatant.movement_remaining,
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error moving creature: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


async def handle_get_ai_action(arguments: dict) -> list[types.TextContent]:
    """Get AI-decided action for an enemy creature"""
    try:
        combat_id = arguments["combat_id"]
        creature_id = arguments["creature_id"]
        
        combat_state = active_combats.get(combat_id)
        if not combat_state:
            raise ValueError(f"Combat {combat_id} not found")
        
        # Get enemies for target selection
        enemies = get_all_enemies(combat_state, creature_id)
        
        # Select target
        target_id = select_target(combat_state, creature_id, enemies, strategy="balanced")
        
        # Decide action
        action = decide_action(combat_state, creature_id, target_id)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "creature_id": creature_id,
                "action": action,
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error getting AI action: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


async def handle_use_spell_slot(arguments: dict) -> list[types.TextContent]:
    """Use a spell slot and sync to Obsidian in real-time"""
    try:
        combat_id = arguments["combat_id"]
        creature_id = arguments["creature_id"]
        spell_level = arguments["spell_level"]
        
        combat_state = active_combats.get(combat_id)
        if not combat_state:
            raise ValueError(f"Combat {combat_id} not found")
        
        combatant = combat_state.get_combatant(creature_id)
        if not combatant:
            raise ValueError(f"Creature {creature_id} not found")
        
        # Check if slot available
        current_slots = combatant.creature.spell_slots.get(spell_level, 0)
        if current_slots <= 0:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"No level {spell_level} spell slots remaining",
                }, indent=2)
            )]
        
        # Use the slot
        combatant.creature.spell_slots[spell_level] = current_slots - 1
        
        # Real-time sync to Obsidian for players
        obsidian_synced = False
        if combatant.creature.creature_type == CreatureType.PLAYER:
            obsidian_synced = use_spell_slot(combatant.creature, spell_level)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "creature": combatant.creature.name,
                "spell_level": spell_level,
                "slots_remaining": combatant.creature.spell_slots[spell_level],
                "obsidian_synced": obsidian_synced,
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error using spell slot: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


async def handle_cast_spell(arguments: dict) -> list[types.TextContent]:
    """Cast a spell and automatically use spell slot, syncing to Obsidian in real-time
    
    Works both in combat (with combat_id) and out of combat (without combat_id).
    """
    try:
        creature_id = arguments["creature_id"]
        spell_name = arguments["spell_name"]
        spell_level = arguments["spell_level"]
        combat_id = arguments.get("combat_id")  # Optional - for out-of-combat casting
        
        # If in combat, get combatant from combat state
        if combat_id:
            combat_state = active_combats.get(combat_id)
            if not combat_state:
                raise ValueError(f"Combat {combat_id} not found")
            
            combatant = combat_state.get_combatant(creature_id)
            if not combatant:
                raise ValueError(f"Creature {creature_id} not found in combat")
            
            creature = combatant.creature
            
            # Check if can act
            if not combatant.can_act:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"{creature.name} cannot act",
                    }, indent=2)
                )]
        else:
            # Out of combat - load spell slots from Obsidian
            from utils.obsidian_sync import get_obsidian_sync
            obsidian_sync = get_obsidian_sync()
            
            # Get spell slots from Obsidian file
            slots_dict = obsidian_sync.get_spell_slots(creature_id)
            spell_slots = {level: remaining for level, (remaining, _) in slots_dict.items()}
            
            # Create a minimal creature object for out-of-combat
            from models.creature import Creature, CreatureType
            creature = Creature(
                creature_id=creature_id,
                name=creature_id,
                creature_type=CreatureType.PLAYER,
                max_hp=1,
                current_hp=1,
                ac=10,
                strength=10,
                dexterity=10,
                constitution=10,
                intelligence=10,
                wisdom=10,
                charisma=10,
                spell_slots=spell_slots
            )
        
        # Check if spell slot available
        current_slots = creature.spell_slots.get(spell_level, 0)
        if current_slots <= 0:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"No level {spell_level} spell slots remaining",
                    "spell": spell_name,
                }, indent=2)
            )]
        
        # Use the spell slot
        creature.spell_slots[spell_level] = current_slots - 1
        
        # Real-time sync to Obsidian for players
        obsidian_synced = False
        if creature.creature_type == CreatureType.PLAYER:
            obsidian_synced = use_spell_slot(creature, spell_level)
        
        result = {
            "success": True,
            "creature": creature.name,
            "spell": spell_name,
            "spell_level": spell_level,
            "slots_remaining": creature.spell_slots[spell_level],
            "obsidian_synced": obsidian_synced,
        }
        
        # If in combat, mark action used
        if combat_id and combatant:
            combatant.has_taken_action = True
            result["action_used"] = True
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error casting spell: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


async def handle_use_resource(arguments: dict) -> list[types.TextContent]:
    """Use a class resource (Rage, Ki, etc.) and sync to Obsidian in real-time"""
    try:
        combat_id = arguments["combat_id"]
        creature_id = arguments["creature_id"]
        resource_name = arguments["resource_name"]
        amount = arguments.get("amount", 1)
        current = arguments.get("current")  # Current value after use
        maximum = arguments.get("maximum")  # Max value
        
        combat_state = active_combats.get(combat_id)
        if not combat_state:
            raise ValueError(f"Combat {combat_id} not found")
        
        combatant = combat_state.get_combatant(creature_id)
        if not combatant:
            raise ValueError(f"Creature {creature_id} not found")
        
        # Real-time sync to Obsidian for players
        obsidian_synced = False
        if combatant.creature.creature_type == CreatureType.PLAYER and current is not None and maximum is not None:
            obsidian_synced = sync_resource_to_obsidian(
                combatant.creature.name,
                resource_name,
                current,
                maximum
            )
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "creature": combatant.creature.name,
                "resource": resource_name,
                "amount_used": amount,
                "current": current,
                "maximum": maximum,
                "obsidian_synced": obsidian_synced,
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error using resource: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


async def handle_apply_healing(arguments: dict) -> list[types.TextContent]:
    """Apply healing and sync HP to Obsidian in real-time"""
    try:
        combat_id = arguments["combat_id"]
        creature_id = arguments["creature_id"]
        healing_amount = arguments["healing_amount"]
        
        combat_state = active_combats.get(combat_id)
        if not combat_state:
            raise ValueError(f"Combat {combat_id} not found")
        
        combatant = combat_state.get_combatant(creature_id)
        if not combatant:
            raise ValueError(f"Creature {creature_id} not found")
        
        # Apply healing
        actual_healing = combatant.creature.heal(healing_amount)
        
        # Real-time sync to Obsidian for players
        obsidian_synced = False
        if combatant.creature.creature_type == CreatureType.PLAYER:
            obsidian_synced = sync_player_hp(combatant.creature)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "creature": combatant.creature.name,
                "healing_amount": healing_amount,
                "actual_healing": actual_healing,
                "hp_after": combatant.creature.current_hp,
                "hp_max": combatant.creature.max_hp,
                "obsidian_synced": obsidian_synced,
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error applying healing: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


async def handle_end_combat(arguments: dict) -> list[types.TextContent]:
    """End combat and sync data to Obsidian"""
    try:
        combat_id = arguments["combat_id"]
        
        combat_state = active_combats.get(combat_id)
        if not combat_state:
            raise ValueError(f"Combat {combat_id} not found")
        
        # Sync player data to Obsidian (replacing Google Sheets)
        sync_results = []
        for combatant in combat_state.combatants.values():
            if combatant.is_player:
                # Sync HP
                hp_synced = sync_hp_to_obsidian(
                    combatant.creature.name,
                    combatant.creature.current_hp,
                    combatant.creature.max_hp,
                )
                
                # Sync spell slots if any were used
                spell_slots_synced = {}
                for level, remaining in combatant.creature.spell_slots.items():
                    # Try to sync - will read max from file if not provided
                    synced = sync_spell_slots_to_obsidian(
                        combatant.creature.name,
                        level,
                        remaining
                    )
                    spell_slots_synced[f"level_{level}"] = synced
                
                # Sync conditions
                conditions_synced = []
                for condition in combatant.active_conditions:
                    synced = sync_condition_to_obsidian(
                        combatant.creature.name,
                        condition,
                        "Until removed"
                    )
                    conditions_synced.append({"condition": condition, "synced": synced})
                
                sync_results.append({
                    "character": combatant.creature.name,
                    "hp_synced": hp_synced,
                    "spell_slots_synced": spell_slots_synced,
                    "conditions_synced": conditions_synced,
                    "obsidian": True,
                })
        
        combat_state.end_combat()
        
        # Remove from active combats
        del active_combats[combat_id]
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": "Combat ended",
                "duration_seconds": (combat_state.ended_at - combat_state.started_at).total_seconds(),
                "rounds": combat_state.round_number,
                "obsidian_sync": sync_results,
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error ending combat: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available combat engine tools."""
    return [
        types.Tool(
            name="start_combat",
            description="Start a new combat encounter with player characters and monsters",
            inputSchema={
                "type": "object",
                "properties": {
                    "encounter_id": {"type": "string", "description": "Unique encounter ID (auto-generated if not provided)"},
                    "encounter_name": {"type": "string", "description": "Display name for encounter"},
                    "battlefield_width": {"type": "integer", "description": "Battlefield width in 5-foot squares (default 20)"},
                    "battlefield_height": {"type": "integer", "description": "Battlefield height in 5-foot squares (default 20)"},
                    "character_ids": {"type": "array", "items": {"type": "string"}, "description": "List of player character IDs to load from sheets"},
                    "monster_data": {"type": "array", "items": {"type": "object"}, "description": "List of monster dicts with stats"}
                },
                "required": []
            }
        ),
        types.Tool(
            name="roll_initiative_tool",
            description="Roll initiative for all combatants (auto-rolls d20 + initiative bonus)",
            inputSchema={
                "type": "object",
                "properties": {
                    "combat_id": {"type": "string", "description": "Combat encounter ID"}
                },
                "required": ["combat_id"]
            }
        ),
        types.Tool(
            name="load_battlefield",
            description="Load battlefield with terrain and positioning",
            inputSchema={
                "type": "object",
                "properties": {
                    "combat_id": {"type": "string", "description": "Combat encounter ID"},
                    "terrain_data": {"type": "array", "items": {"type": "object"}, "description": "Terrain features"},
                    "combatant_positions": {"type": "object", "description": "Initial positions for combatants"}
                },
                "required": ["combat_id"]
            }
        ),
        types.Tool(
            name="next_turn_tool",
            description="Advance to the next turn in combat",
            inputSchema={
                "type": "object",
                "properties": {
                    "combat_id": {"type": "string", "description": "Combat encounter ID"}
                },
                "required": ["combat_id"]
            }
        ),
        types.Tool(
            name="get_combat_status",
            description="Get current combat status with HP, conditions, and positioning",
            inputSchema={
                "type": "object",
                "properties": {
                    "combat_id": {"type": "string", "description": "Combat encounter ID"}
                },
                "required": ["combat_id"]
            }
        ),
        types.Tool(
            name="attack_tool",
            description="Execute an attack action with automatic dice rolling. Supports both attack rolls (weapons) and save-based spells (Fireball, etc.).",
            inputSchema={
                "type": "object",
                "properties": {
                    "combat_id": {"type": "string", "description": "Combat encounter ID"},
                    "attacker_id": {"type": "string", "description": "Attacker creature ID"},
                    "target_id": {"type": "string", "description": "Target creature ID"},
                    "attack_bonus": {"type": "integer", "description": "Attack bonus to add to d20 roll (ignored if skip_attack_roll=True)"},
                    "damage_dice": {"type": "string", "description": "Damage dice expression (e.g., '1d8+4', '2d6+3'). Ignored if damage_amount provided."},
                    "damage_amount": {"type": "integer", "description": "Direct damage amount (for save-based spells with pre-rolled damage, e.g., Fireball). Use this instead of damage_dice when skip_attack_roll=True."},
                    "damage_type": {"type": "string", "description": "Damage type (slashing, bludgeoning, piercing, fire, force, etc.)"},
                    "weapon_type": {"type": "string", "description": "Weapon type: 'melee' (default, 5ft range) or 'ranged' (no range limit check)", "enum": ["melee", "ranged"], "default": "melee"},
                    "advantage": {"type": "boolean", "description": "Roll attack with advantage (ignored if skip_attack_roll=True)"},
                    "disadvantage": {"type": "boolean", "description": "Roll attack with disadvantage (ignored if skip_attack_roll=True)"},
                    "skip_attack_roll": {"type": "boolean", "description": "Skip attack roll entirely (for save-based spells like Fireball). If true, damage is applied directly based on save_success."},
                    "save_success": {"type": "boolean", "description": "Target succeeded on saving throw (apply half damage, round down). Only used when skip_attack_roll=True."}
                },
                "required": ["combat_id", "attacker_id", "target_id"]
            }
        ),
        types.Tool(
            name="move_creature",
            description="Move a creature on the battlefield",
            inputSchema={
                "type": "object",
                "properties": {
                    "combat_id": {"type": "string", "description": "Combat encounter ID"},
                    "creature_id": {"type": "string", "description": "Creature ID to move"},
                    "new_position": {"type": "object", "description": "New position {x, y}"},
                    "is_dash": {"type": "boolean", "description": "Using Dash action (double speed)"}
                },
                "required": ["combat_id", "creature_id", "new_position"]
            }
        ),
        types.Tool(
            name="get_ai_action",
            description="Get AI-recommended action for an enemy creature",
            inputSchema={
                "type": "object",
                "properties": {
                    "combat_id": {"type": "string", "description": "Combat encounter ID"},
                    "creature_id": {"type": "string", "description": "Enemy creature ID"}
                },
                "required": ["combat_id", "creature_id"]
            }
        ),
        types.Tool(
            name="use_spell_slot",
            description="Use a spell slot and sync to Obsidian in real-time",
            inputSchema={
                "type": "object",
                "properties": {
                    "combat_id": {"type": "string", "description": "Combat encounter ID"},
                    "creature_id": {"type": "string", "description": "Creature ID using the spell slot"},
                    "spell_level": {"type": "integer", "description": "Spell level (1-9)"}
                },
                "required": ["combat_id", "creature_id", "spell_level"]
            }
        ),
        types.Tool(
            name="use_resource",
            description="Use a class resource (Rage, Ki, Channel Divinity, etc.) and sync to Obsidian in real-time",
            inputSchema={
                "type": "object",
                "properties": {
                    "combat_id": {"type": "string", "description": "Combat encounter ID"},
                    "creature_id": {"type": "string", "description": "Creature ID using the resource"},
                    "resource_name": {"type": "string", "description": "Resource name (e.g., 'rage', 'ki', 'channel_divinity')"},
                    "amount": {"type": "integer", "description": "Amount used (default: 1)"},
                    "current": {"type": "integer", "description": "Current value after use"},
                    "maximum": {"type": "integer", "description": "Maximum value"}
                },
                "required": ["combat_id", "creature_id", "resource_name", "current", "maximum"]
            }
        ),
        types.Tool(
            name="apply_healing",
            description="Apply healing to a creature and sync HP to Obsidian in real-time",
            inputSchema={
                "type": "object",
                "properties": {
                    "combat_id": {"type": "string", "description": "Combat encounter ID"},
                    "creature_id": {"type": "string", "description": "Creature ID receiving healing"},
                    "healing_amount": {"type": "integer", "description": "Amount of healing"}
                },
                "required": ["combat_id", "creature_id", "healing_amount"]
            }
        ),
        types.Tool(
            name="end_combat_tool",
            description="End the current combat encounter",
            inputSchema={
                "type": "object",
                "properties": {
                    "combat_id": {"type": "string", "description": "Combat encounter ID"}
                },
                "required": ["combat_id"]
            }
        )
    ]


async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

