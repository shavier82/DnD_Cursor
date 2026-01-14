"""AI tactical positioning and movement decisions"""

from typing import Optional, List, Tuple
from ..models.combat_state import CombatState
from ..models.battlefield import Position
from .target_selection import get_all_enemies, get_allies


def decide_position(
    combat_state: CombatState,
    creature_id: str,
    target_id: Optional[str] = None,
    objective: str = "engage"
) -> Optional[Position]:
    """Decide where creature should move
    
    Args:
        combat_state: Current combat state
        creature_id: The creature deciding movement
        target_id: Optional target to move toward/away from
        objective: Movement objective
            - "engage": Move toward target for melee
            - "maintain_range": Keep at ranged distance
            - "retreat": Move away from danger
            - "flank": Move to flanking position
            - "cover": Move to cover
    
    Returns:
        Target position to move to, or None if shouldn't move
    """
    combatant = combat_state.get_combatant(creature_id)
    if not combatant:
        return None
    
    current_pos = combat_state.battlefield.get_position(creature_id)
    if not current_pos:
        return None
    
    movement_remaining = combatant.movement_remaining
    if movement_remaining <= 0:
        return None
    
    # Execute based on objective
    if objective == "engage":
        return _move_to_engage(combat_state, creature_id, target_id, current_pos, movement_remaining)
    elif objective == "maintain_range":
        return _maintain_range(combat_state, creature_id, target_id, current_pos, movement_remaining)
    elif objective == "retreat":
        return _retreat(combat_state, creature_id, current_pos, movement_remaining)
    elif objective == "flank":
        return _move_to_flank(combat_state, creature_id, target_id, current_pos, movement_remaining)
    elif objective == "cover":
        return _move_to_cover(combat_state, creature_id, current_pos, movement_remaining)
    
    return None


def _move_to_engage(
    combat_state: CombatState,
    creature_id: str,
    target_id: Optional[str],
    current_pos: Position,
    movement: int
) -> Optional[Position]:
    """Move toward target for melee engagement"""
    if not target_id:
        # No specific target, find nearest enemy
        enemies = get_all_enemies(combat_state, creature_id)
        if not enemies:
            return None
        
        nearest = None
        nearest_dist = float('inf')
        for enemy_id in enemies:
            enemy_pos = combat_state.battlefield.get_position(enemy_id)
            if enemy_pos:
                dist = current_pos.distance_to(enemy_pos)
                if dist < nearest_dist:
                    nearest = enemy_id
                    nearest_dist = dist
        
        target_id = nearest
    
    if not target_id:
        return None
    
    target_pos = combat_state.battlefield.get_position(target_id)
    if not target_pos:
        return None
    
    # Move as close as possible to target
    return _move_toward(combat_state, current_pos, target_pos, movement)


def _maintain_range(
    combat_state: CombatState,
    creature_id: str,
    target_id: Optional[str],
    current_pos: Position,
    movement: int
) -> Optional[Position]:
    """Maintain ranged distance from target"""
    if not target_id:
        return None
    
    target_pos = combat_state.battlefield.get_position(target_id)
    if not target_pos:
        return None
    
    distance = current_pos.distance_to(target_pos)
    ideal_range = 30  # Typical ranged weapon range
    
    if distance < 15:
        # Too close, back away
        return _move_away(combat_state, current_pos, target_pos, movement)
    elif distance > 60:
        # Too far, move closer
        return _move_toward(combat_state, current_pos, target_pos, movement)
    else:
        # Good range, don't move
        return None


def _retreat(
    combat_state: CombatState,
    creature_id: str,
    current_pos: Position,
    movement: int
) -> Optional[Position]:
    """Retreat from all enemies"""
    enemies = get_all_enemies(combat_state, creature_id)
    if not enemies:
        return None
    
    # Find average position of enemies
    enemy_positions = []
    for enemy_id in enemies:
        enemy_pos = combat_state.battlefield.get_position(enemy_id)
        if enemy_pos:
            enemy_positions.append(enemy_pos)
    
    if not enemy_positions:
        return None
    
    # Calculate centroid of enemies
    avg_x = sum(p.x for p in enemy_positions) / len(enemy_positions)
    avg_y = sum(p.y for p in enemy_positions) / len(enemy_positions)
    enemy_center = Position(x=int(avg_x), y=int(avg_y))
    
    # Move away from enemy center
    return _move_away(combat_state, current_pos, enemy_center, movement)


def _move_to_flank(
    combat_state: CombatState,
    creature_id: str,
    target_id: Optional[str],
    current_pos: Position,
    movement: int
) -> Optional[Position]:
    """Move to flanking position"""
    if not target_id:
        return None
    
    target_pos = combat_state.battlefield.get_position(target_id)
    if not target_pos:
        return None
    
    # Find allies adjacent to target
    allies = get_allies(combat_state, creature_id)
    adjacent_allies = []
    for ally_id in allies:
        ally_pos = combat_state.battlefield.get_position(ally_id)
        if ally_pos and target_pos.is_adjacent(ally_pos):
            adjacent_allies.append(ally_pos)
    
    if not adjacent_allies:
        # No ally to flank with, just move to engage
        return _move_to_engage(combat_state, creature_id, target_id, current_pos, movement)
    
    # Try to position opposite the ally
    ally_pos = adjacent_allies[0]
    
    # Calculate opposite side
    dx = target_pos.x - ally_pos.x
    dy = target_pos.y - ally_pos.y
    
    # Opposite position is target + (dx, dy)
    flank_pos = Position(
        x=target_pos.x + dx,
        y=target_pos.y + dy,
        z=target_pos.z
    )
    
    # Check if flanking position is valid
    if combat_state.battlefield.is_valid_position(flank_pos) and \
       combat_state.battlefield.is_passable(flank_pos) and \
       not combat_state.battlefield.is_occupied(flank_pos, exclude=creature_id):
        # Check if we can reach it
        distance = current_pos.distance_to(flank_pos)
        if distance <= movement:
            return flank_pos
    
    # Flanking position not reachable, move toward it
    return _move_toward(combat_state, current_pos, flank_pos, movement)


def _move_to_cover(
    combat_state: CombatState,
    creature_id: str,
    current_pos: Position,
    movement: int
) -> Optional[Position]:
    """Move to nearest cover"""
    # Find terrain that provides cover
    cover_positions = []
    for terrain in combat_state.battlefield.terrain:
        if terrain.provides_cover:
            cover_positions.append(terrain.position)
    
    if not cover_positions:
        return None
    
    # Find nearest cover within movement range
    nearest_cover = None
    nearest_dist = float('inf')
    
    for cover_pos in cover_positions:
        dist = current_pos.distance_to(cover_pos)
        if dist <= movement and dist < nearest_dist:
            # Check if position is passable and not occupied
            if combat_state.battlefield.is_passable(cover_pos) and \
               not combat_state.battlefield.is_occupied(cover_pos, exclude=creature_id):
                nearest_cover = cover_pos
                nearest_dist = dist
    
    return nearest_cover


def _move_toward(
    combat_state: CombatState,
    from_pos: Position,
    to_pos: Position,
    movement: int
) -> Optional[Position]:
    """Move toward a position (straight line)"""
    distance = from_pos.distance_to(to_pos)
    
    if distance <= movement:
        # Can reach target
        return to_pos
    
    # Move as far as possible toward target
    # Calculate direction vector
    dx = to_pos.x - from_pos.x
    dy = to_pos.y - from_pos.y
    
    # Normalize and scale by movement
    length = max(abs(dx), abs(dy))
    if length == 0:
        return None
    
    # Move in 5-foot increments
    move_squares = movement // 5
    step_x = int((dx / length) * move_squares)
    step_y = int((dy / length) * move_squares)
    
    new_pos = Position(
        x=from_pos.x + step_x,
        y=from_pos.y + step_y,
        z=from_pos.z
    )
    
    # Validate position
    if combat_state.battlefield.is_valid_position(new_pos) and \
       combat_state.battlefield.is_passable(new_pos) and \
       not combat_state.battlefield.is_occupied(new_pos):
        return new_pos
    
    return None


def _move_away(
    combat_state: CombatState,
    from_pos: Position,
    away_from: Position,
    movement: int
) -> Optional[Position]:
    """Move away from a position"""
    # Calculate opposite direction
    dx = from_pos.x - away_from.x
    dy = from_pos.y - away_from.y
    
    # Normalize and scale by movement
    length = max(abs(dx), abs(dy))
    if length == 0:
        # Already at same position, move in any direction
        dx, dy = 1, 0
        length = 1
    
    # Move in 5-foot increments
    move_squares = movement // 5
    step_x = int((dx / length) * move_squares)
    step_y = int((dy / length) * move_squares)
    
    new_pos = Position(
        x=from_pos.x + step_x,
        y=from_pos.y + step_y,
        z=from_pos.z
    )
    
    # Validate position
    if combat_state.battlefield.is_valid_position(new_pos) and \
       combat_state.battlefield.is_passable(new_pos) and \
       not combat_state.battlefield.is_occupied(new_pos):
        return new_pos
    
    # If direct retreat blocked, try adjacent squares
    for dx_offset in [-1, 0, 1]:
        for dy_offset in [-1, 0, 1]:
            if dx_offset == 0 and dy_offset == 0:
                continue
            
            alt_pos = Position(
                x=from_pos.x + dx_offset,
                y=from_pos.y + dy_offset,
                z=from_pos.z
            )
            
            if combat_state.battlefield.is_valid_position(alt_pos) and \
               combat_state.battlefield.is_passable(alt_pos) and \
               not combat_state.battlefield.is_occupied(alt_pos):
                # Check if this moves away from threat
                if alt_pos.distance_to(away_from) > from_pos.distance_to(away_from):
                    return alt_pos
    
    return None


def find_optimal_position_for_aoe(
    combat_state: CombatState,
    caster_id: str,
    aoe_type: str,
    aoe_size: int,
    enemies: List[str],
    allies: List[str]
) -> Optional[Tuple[Position, List[str]]]:
    """Find optimal position to cast an AoE spell
    
    Args:
        combat_state: Current combat state
        caster_id: The caster's creature ID
        aoe_type: Type of AoE ("sphere", "cone", "line")
        aoe_size: Size of AoE in feet
        enemies: List of enemy IDs
        allies: List of ally IDs
    
    Returns:
        Tuple of (optimal_position, affected_enemies) or None
    """
    battlefield = combat_state.battlefield
    
    # Try each grid position as potential AoE center
    best_position = None
    best_score = 0
    best_targets = []
    
    for x in range(battlefield.width):
        for y in range(battlefield.height):
            test_pos = Position(x=x, y=y)
            
            # Count enemies and allies in AoE
            creatures_in_aoe = battlefield.get_creatures_in_radius(test_pos, aoe_size)
            
            enemies_hit = [cid for cid in creatures_in_aoe if cid in enemies]
            allies_hit = [cid for cid in creatures_in_aoe if cid in allies or cid == caster_id]
            
            # Score: +1 per enemy, -2 per ally
            score = len(enemies_hit) - (2 * len(allies_hit))
            
            if score > best_score:
                best_score = score
                best_position = test_pos
                best_targets = enemies_hit
    
    if best_score > 0:
        return (best_position, best_targets)
    
    return None




