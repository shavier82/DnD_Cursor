"""AI target selection logic"""

from typing import List, Optional, Callable
from models.combat_state import CombatState
from models.creature import Combatant


def select_target(
    combat_state: CombatState,
    attacker_id: str,
    enemies: List[str],
    strategy: str = "balanced"
) -> Optional[str]:
    """Select best target for an enemy to attack
    
    Args:
        combat_state: Current combat state
        attacker_id: The attacking creature's ID
        enemies: List of potential target IDs
        strategy: Target selection strategy
            - "balanced": Smart balanced approach (default)
            - "nearest": Attack nearest enemy
            - "weakest": Attack lowest HP enemy
            - "priority": Attack concentrating/low HP enemies
            - "random": Random target
    
    Returns:
        Target creature ID or None
    """
    if not enemies:
        return None
    
    attacker = combat_state.get_combatant(attacker_id)
    if not attacker:
        return None
    
    # Filter to only alive enemies
    alive_enemies = [
        eid for eid in enemies
        if combat_state.get_combatant(eid) and combat_state.get_combatant(eid).is_alive
    ]
    
    if not alive_enemies:
        return None
    
    # Apply strategy
    if strategy == "nearest":
        return _select_nearest(combat_state, attacker_id, alive_enemies)
    elif strategy == "weakest":
        return _select_weakest(combat_state, alive_enemies)
    elif strategy == "priority":
        return _select_priority(combat_state, alive_enemies)
    elif strategy == "random":
        import random
        return random.choice(alive_enemies)
    else:  # "balanced" - default smart behavior
        return _select_balanced(combat_state, attacker_id, alive_enemies)


def _select_nearest(combat_state: CombatState, attacker_id: str, enemies: List[str]) -> Optional[str]:
    """Select nearest enemy"""
    attacker_pos = combat_state.battlefield.get_position(attacker_id)
    if not attacker_pos:
        return enemies[0]
    
    nearest = None
    nearest_dist = float('inf')
    
    for enemy_id in enemies:
        enemy_pos = combat_state.battlefield.get_position(enemy_id)
        if not enemy_pos:
            continue
        
        dist = attacker_pos.distance_to(enemy_pos)
        if dist < nearest_dist:
            nearest = enemy_id
            nearest_dist = dist
    
    return nearest


def _select_weakest(combat_state: CombatState, enemies: List[str]) -> Optional[str]:
    """Select enemy with lowest HP"""
    weakest = None
    lowest_hp = float('inf')
    
    for enemy_id in enemies:
        enemy = combat_state.get_combatant(enemy_id)
        if not enemy:
            continue
        
        if enemy.creature.current_hp < lowest_hp:
            weakest = enemy_id
            lowest_hp = enemy.creature.current_hp
    
    return weakest


def _select_priority(combat_state: CombatState, enemies: List[str]) -> Optional[str]:
    """Select priority target (concentrating, low HP, high threat)"""
    # Priority order:
    # 1. Concentrating spellcaster below 50% HP
    # 2. Enemy below 30% HP (finish them off)
    # 3. Concentrating spellcaster
    # 4. Highest damage dealer
    # 5. Lowest HP
    
    concentrating_low_hp = []
    low_hp = []
    concentrating = []
    high_damage = []
    
    for enemy_id in enemies:
        enemy = combat_state.get_combatant(enemy_id)
        if not enemy:
            continue
        
        is_concentrating = enemy.concentrating_on is not None
        hp_percent = enemy.creature.hp_percent
        
        if is_concentrating and hp_percent < 0.5:
            concentrating_low_hp.append(enemy_id)
        elif hp_percent < 0.3:
            low_hp.append(enemy_id)
        elif is_concentrating:
            concentrating.append(enemy_id)
        elif enemy.damage_dealt_this_combat > 10:
            high_damage.append((enemy_id, enemy.damage_dealt_this_combat))
    
    # Return highest priority target
    if concentrating_low_hp:
        return concentrating_low_hp[0]
    elif low_hp:
        return low_hp[0]
    elif concentrating:
        return concentrating[0]
    elif high_damage:
        high_damage.sort(key=lambda x: x[1], reverse=True)
        return high_damage[0][0]
    else:
        return _select_weakest(combat_state, enemies)


def _select_balanced(combat_state: CombatState, attacker_id: str, enemies: List[str]) -> Optional[str]:
    """Balanced target selection (default smart AI)"""
    # Score each enemy based on multiple factors
    scores = {}
    
    attacker_pos = combat_state.battlefield.get_position(attacker_id)
    
    for enemy_id in enemies:
        enemy = combat_state.get_combatant(enemy_id)
        if not enemy:
            continue
        
        score = 0
        
        # Factor 1: HP (prefer lower HP)
        hp_percent = enemy.creature.hp_percent
        if hp_percent < 0.3:
            score += 30  # Very low HP = high priority
        elif hp_percent < 0.5:
            score += 20  # Low HP = medium priority
        elif hp_percent < 0.7:
            score += 10  # Medium HP = some priority
        
        # Factor 2: Concentrating (break concentration)
        if enemy.concentrating_on:
            score += 25
        
        # Factor 3: Distance (prefer closer targets)
        if attacker_pos:
            enemy_pos = combat_state.battlefield.get_position(enemy_id)
            if enemy_pos:
                dist = attacker_pos.distance_to(enemy_pos)
                if dist <= 5:
                    score += 15  # Adjacent = easy target
                elif dist <= 30:
                    score += 10  # Within normal range
                elif dist <= 60:
                    score += 5   # Medium range
                # Far away = no bonus
        
        # Factor 4: Damage dealt (threat assessment)
        damage_dealt = enemy.damage_dealt_this_combat
        if damage_dealt > 20:
            score += 15  # High threat
        elif damage_dealt > 10:
            score += 10  # Medium threat
        elif damage_dealt > 0:
            score += 5   # Some threat
        
        # Factor 5: Conditions (avoid attacking heavily debuffed enemies)
        if "paralyzed" in enemy.active_conditions or "unconscious" in enemy.active_conditions:
            score -= 10  # Already out of fight, focus elsewhere
        
        scores[enemy_id] = score
    
    # Return enemy with highest score
    if scores:
        best_target = max(scores.items(), key=lambda x: x[1])
        return best_target[0]
    
    return enemies[0] if enemies else None


def get_all_enemies(combat_state: CombatState, attacker_id: str) -> List[str]:
    """Get all enemies for an attacker
    
    Args:
        combat_state: Current combat state
        attacker_id: The attacker's creature ID
    
    Returns:
        List of enemy creature IDs
    """
    attacker = combat_state.get_combatant(attacker_id)
    if not attacker:
        return []
    
    is_player = attacker.is_player
    
    # Enemies are opposite type
    enemies = [
        cid for cid, combatant in combat_state.combatants.items()
        if combatant.is_player != is_player and combatant.is_alive
    ]
    
    return enemies


def get_allies(combat_state: CombatState, creature_id: str) -> List[str]:
    """Get all allies for a creature
    
    Args:
        combat_state: Current combat state
        creature_id: The creature's ID
    
    Returns:
        List of ally creature IDs
    """
    creature = combat_state.get_combatant(creature_id)
    if not creature:
        return []
    
    is_player = creature.is_player
    
    # Allies are same type
    allies = [
        cid for cid, combatant in combat_state.combatants.items()
        if cid != creature_id and combatant.is_player == is_player and combatant.is_alive
    ]
    
    return allies




