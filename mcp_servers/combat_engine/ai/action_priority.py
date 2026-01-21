"""AI action priority and decision making"""

from typing import Dict, Any, Optional, List
from models.combat_state import CombatState
from models.creature import Combatant
from .target_selection import get_all_enemies


def decide_action(
    combat_state: CombatState,
    creature_id: str,
    target_id: Optional[str] = None
) -> Dict[str, Any]:
    """Decide what action an AI creature should take
    
    Args:
        combat_state: Current combat state
        creature_id: The creature deciding action
        target_id: Optional pre-selected target
    
    Returns:
        Dict with action details:
        {
            "action_type": str ("attack", "spell", "ability", "disengage", "dodge", "dash", "hide"),
            "target_id": str (target creature ID),
            "details": dict (action-specific details)
        }
    """
    combatant = combat_state.get_combatant(creature_id)
    if not combatant or not combatant.can_act:
        return {"action_type": "none", "reason": "Cannot act"}
    
    creature = combatant.creature
    enemies = get_all_enemies(combat_state, creature_id)
    
    if not enemies:
        return {"action_type": "none", "reason": "No enemies"}
    
    # Get current position
    position = combat_state.battlefield.get_position(creature_id)
    if not position:
        return {"action_type": "none", "reason": "No position"}
    
    # Calculate tactical situation
    situation = _assess_situation(combat_state, creature_id, enemies)
    
    # Decision tree based on situation
    
    # 1. Self-preservation: Flee if very low HP and outnumbered
    if situation["hp_critical"] and situation["outnumbered"]:
        return {
            "action_type": "disengage",
            "reason": "Low HP and outnumbered, retreating",
            "details": {}
        }
    
    # 2. No adjacent enemies and ranged attack available: Use ranged attack
    if not situation["adjacent_enemies"] and creature.special_abilities:
        ranged_ability = _find_ranged_ability(creature)
        if ranged_ability and target_id:
            distance = combat_state.battlefield.get_distance(creature_id, target_id)
            if distance and distance <= ranged_ability.get("range", 80):
                return {
                    "action_type": "ability",
                    "target_id": target_id,
                    "details": {"ability": ranged_ability}
                }
    
    # 3. Multiple enemies in AoE range: Use AoE spell/ability
    if situation["enemies_clustered"]:
        aoe_ability = _find_aoe_ability(creature)
        if aoe_ability:
            return {
                "action_type": "spell" if "spell" in aoe_ability else "ability",
                "target_id": situation["cluster_center"],
                "details": {"ability": aoe_ability, "aoe": True}
            }
    
    # 4. Adjacent enemy: Standard melee attack
    if situation["adjacent_enemies"]:
        return {
            "action_type": "attack",
            "target_id": situation["adjacent_enemies"][0],
            "details": {"weapon": "melee"}
        }
    
    # 5. Enemy within move+attack range: Move and attack
    nearest_enemy = situation["nearest_enemy"]
    if nearest_enemy:
        distance = combat_state.battlefield.get_distance(creature_id, nearest_enemy["id"])
        movement = combatant.movement_remaining
        
        if distance and distance <= movement + 5:  # Can move and attack
            return {
                "action_type": "attack",
                "target_id": nearest_enemy["id"],
                "details": {"weapon": "melee", "move_first": True, "move_distance": distance - 5}
            }
    
    # 6. Enemy out of range: Dash closer
    if nearest_enemy:
        return {
            "action_type": "dash",
            "target_id": nearest_enemy["id"],
            "reason": "Moving closer to enemy",
            "details": {}
        }
    
    # 7. Surrounded and low HP: Dodge
    if situation["surrounded"] and situation["hp_low"]:
        return {
            "action_type": "dodge",
            "reason": "Defensive posture",
            "details": {}
        }
    
    # 8. Default: Standard attack on nearest
    if nearest_enemy:
        return {
            "action_type": "attack",
            "target_id": nearest_enemy["id"],
            "details": {"weapon": "melee"}
        }
    
    # 9. Nothing to do
    return {"action_type": "dodge", "details": {}}


def _assess_situation(
    combat_state: CombatState,
    creature_id: str,
    enemies: List[str]
) -> Dict[str, Any]:
    """Assess tactical situation for decision making"""
    combatant = combat_state.get_combatant(creature_id)
    if not combatant:
        return {}
    
    creature = combatant.creature
    position = combat_state.battlefield.get_position(creature_id)
    
    # HP status
    hp_percent = creature.hp_percent
    hp_critical = hp_percent < 0.2
    hp_low = hp_percent < 0.5
    
    # Adjacent enemies
    adjacent = combat_state.battlefield.get_adjacent_creatures(creature_id)
    adjacent_enemies = [eid for eid in adjacent if eid in enemies]
    
    # Surrounded check
    surrounded = len(adjacent_enemies) >= 3
    
    # Outnumbered check
    allies = [
        c for c in combat_state.combatants.values()
        if c.is_player == combatant.is_player and c.is_alive and c.creature.creature_id != creature_id
    ]
    outnumbered = len(enemies) > len(allies) + 1
    
    # Find nearest enemy
    nearest_enemy = None
    nearest_distance = float('inf')
    if position:
        for enemy_id in enemies:
            enemy_pos = combat_state.battlefield.get_position(enemy_id)
            if enemy_pos:
                dist = position.distance_to(enemy_pos)
                if dist < nearest_distance:
                    nearest_distance = dist
                    nearest_enemy = {"id": enemy_id, "distance": dist}
    
    # Check for clustered enemies (3+ within 20 feet of each other)
    enemies_clustered = False
    cluster_center = None
    if len(enemies) >= 3:
        for enemy_id in enemies:
            enemy_pos = combat_state.battlefield.get_position(enemy_id)
            if enemy_pos:
                nearby = combat_state.battlefield.get_creatures_in_radius(enemy_pos, 20)
                nearby_enemies = [eid for eid in nearby if eid in enemies]
                if len(nearby_enemies) >= 3:
                    enemies_clustered = True
                    cluster_center = enemy_id
                    break
    
    return {
        "hp_critical": hp_critical,
        "hp_low": hp_low,
        "adjacent_enemies": adjacent_enemies,
        "surrounded": surrounded,
        "outnumbered": outnumbered,
        "nearest_enemy": nearest_enemy,
        "enemies_clustered": enemies_clustered,
        "cluster_center": cluster_center,
    }


def _find_ranged_ability(creature) -> Optional[Dict[str, Any]]:
    """Find a ranged attack ability"""
    # Look through special abilities for ranged attacks
    for ability in creature.special_abilities:
        if ability.get("range", 0) > 5:  # More than melee range
            return ability
    return None


def _find_aoe_ability(creature) -> Optional[Dict[str, Any]]:
    """Find an AoE ability"""
    # Look through special abilities for AoE
    for ability in creature.special_abilities:
        if ability.get("aoe", False) or "radius" in ability or "cone" in ability.get("name", "").lower():
            return ability
    return None


def should_use_legendary_action(
    combat_state: CombatState,
    creature_id: str,
    trigger: str
) -> Optional[Dict[str, Any]]:
    """Decide if creature should use a legendary action
    
    Args:
        combat_state: Current combat state
        creature_id: The creature with legendary actions
        trigger: What triggered the check ("turn_end", "movement", "attack")
    
    Returns:
        Legendary action to use, or None
    """
    combatant = combat_state.get_combatant(creature_id)
    if not combatant or combatant.creature.legendary_actions <= 0:
        return None
    
    # Simple heuristic: use legendary actions to attack when available
    if trigger == "turn_end":
        enemies = get_all_enemies(combat_state, creature_id)
        adjacent = combat_state.battlefield.get_adjacent_creatures(creature_id)
        adjacent_enemies = [eid for eid in adjacent if eid in enemies]
        
        if adjacent_enemies:
            return {
                "action": "legendary_attack",
                "target_id": adjacent_enemies[0],
                "cost": 1
            }
    
    return None


def should_use_reaction(
    combat_state: CombatState,
    creature_id: str,
    trigger: str,
    trigger_creature_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Decide if creature should use a reaction
    
    Args:
        combat_state: Current combat state
        creature_id: The creature that could react
        trigger: What triggered the reaction check
            - "opportunity_attack": Enemy leaving reach
            - "counterspell": Enemy casting spell
            - "shield": Being attacked
        trigger_creature_id: The creature that triggered the reaction
    
    Returns:
        Reaction to use, or None
    """
    combatant = combat_state.get_combatant(creature_id)
    if not combatant or combatant.has_taken_reaction or not combatant.can_act:
        return None
    
    if trigger == "opportunity_attack" and trigger_creature_id:
        # Always take opportunity attacks
        return {
            "reaction": "opportunity_attack",
            "target_id": trigger_creature_id
        }
    
    elif trigger == "counterspell" and trigger_creature_id:
        # Counterspell if creature has it available
        # Would need to check spell slots
        if combatant.creature.spell_slots.get(3, 0) > 0:
            return {
                "reaction": "counterspell",
                "target_id": trigger_creature_id
            }
    
    elif trigger == "shield" and trigger_creature_id:
        # Use Shield spell if would be hit and spell slot available
        if combatant.creature.spell_slots.get(1, 0) > 0:
            # Would need more context (attack roll vs AC) to decide
            # For now, simple heuristic: use if low HP
            if combatant.creature.hp_percent < 0.5:
                return {
                    "reaction": "shield"
                }
    
    return None




