"""Line of sight and cover calculations"""

from typing import Optional, Tuple
from shapely.geometry import LineString, Point
from ..models.battlefield import Battlefield, Position, TerrainType


def check_line_of_sight(
    battlefield: Battlefield,
    from_pos: Position,
    to_pos: Position,
    ignore_creatures: bool = True
) -> bool:
    """Check if there's a clear line of sight between two positions
    
    Args:
        battlefield: The battlefield
        from_pos: Starting position
        to_pos: Target position
        ignore_creatures: Whether to ignore other creatures (default True)
    
    Returns:
        True if line of sight exists, False if blocked
    """
    # Create line between positions (in feet)
    line = LineString([
        (from_pos.x * 5, from_pos.y * 5),
        (to_pos.x * 5, to_pos.y * 5)
    ])
    
    # Check terrain that blocks LOS
    for terrain in battlefield.terrain:
        if terrain.blocks_line_of_sight:
            terrain_point = Point(terrain.position.x * 5, terrain.position.y * 5)
            # Terrain blocks if line passes through it (with small buffer for terrain size)
            if line.intersects(terrain_point.buffer(2.5)):
                return False
    
    # Optionally check creatures (total cover)
    if not ignore_creatures:
        for creature_id, creature_pos in battlefield.creature_positions.items():
            creature_point = Point(creature_pos.x * 5, creature_pos.y * 5)
            # Check if line passes through creature space
            if line.intersects(creature_point.buffer(2.5)):
                # Don't count start/end positions as blocking
                if creature_pos.to_tuple() not in [from_pos.to_tuple(), to_pos.to_tuple()]:
                    return False
    
    return True


def calculate_cover(
    battlefield: Battlefield,
    attacker_pos: Position,
    target_pos: Position
) -> Tuple[str, int]:
    """Calculate cover bonus for a target
    
    Args:
        battlefield: The battlefield
        attacker_pos: Attacker position
        target_pos: Target position
    
    Returns:
        Tuple of (cover_type, ac_bonus)
        cover_type: "none", "half", "three_quarters", "total"
        ac_bonus: 0, +2, +5, or full block
    """
    # Create line between attacker and target
    line = LineString([
        (attacker_pos.x * 5, attacker_pos.y * 5),
        (target_pos.x * 5, target_pos.y * 5)
    ])
    
    # Check terrain for cover
    best_cover = ("none", 0)
    
    for terrain in battlefield.terrain:
        if not terrain.provides_cover:
            continue
        
        terrain_point = Point(terrain.position.x * 5, terrain.position.y * 5)
        
        # Check if terrain is between attacker and target
        # Terrain provides cover if it's close to the line but not at attacker position
        if line.distance(terrain_point) < 5:  # Within 5 feet of line
            # Don't count cover if terrain is at attacker's position
            if attacker_pos.distance_to(terrain.position) > 5:
                cover_bonus = terrain.cover_bonus
                
                if cover_bonus >= 5:
                    cover_type = "three_quarters"
                elif cover_bonus >= 2:
                    cover_type = "half"
                else:
                    cover_type = "none"
                
                # Use best available cover
                if cover_bonus > best_cover[1]:
                    best_cover = (cover_type, cover_bonus)
    
    # Check for total cover (no line of sight)
    if not check_line_of_sight(battlefield, attacker_pos, target_pos):
        best_cover = ("total", 999)  # Effectively immune to targeted attacks
    
    return best_cover


def has_clear_shot(
    battlefield: Battlefield,
    attacker_id: str,
    target_id: str
) -> Tuple[bool, Optional[str]]:
    """Check if attacker has a clear shot at target
    
    Args:
        battlefield: The battlefield
        attacker_id: Attacker creature ID
        target_id: Target creature ID
    
    Returns:
        Tuple of (has_clear_shot, reason)
        has_clear_shot: True if can attack, False if blocked
        reason: Explanation if blocked (e.g., "No line of sight", "Target has total cover")
    """
    attacker_pos = battlefield.get_position(attacker_id)
    target_pos = battlefield.get_position(target_id)
    
    if attacker_pos is None or target_pos is None:
        return (False, "Invalid positions")
    
    # Check line of sight
    if not check_line_of_sight(battlefield, attacker_pos, target_pos):
        return (False, "No line of sight")
    
    # Check for total cover
    cover_type, _ = calculate_cover(battlefield, attacker_pos, target_pos)
    if cover_type == "total":
        return (False, "Target has total cover")
    
    return (True, None)


def get_flanking_positions(
    battlefield: Battlefield,
    target_id: str,
    attacker_id: Optional[str] = None
) -> list[str]:
    """Get creatures that are flanking the target
    
    Flanking (optional rule): Creatures on opposite sides of target get advantage.
    Two creatures flank if they're on opposite sides and both within 5 feet.
    
    Args:
        battlefield: The battlefield
        target_id: Target being flanked
        attacker_id: Optional specific attacker to check flanking for
    
    Returns:
        List of creature IDs that provide flanking for the attacker
    """
    target_pos = battlefield.get_position(target_id)
    if target_pos is None:
        return []
    
    # Get all adjacent creatures (within 5 feet)
    adjacent = battlefield.get_adjacent_creatures(target_id)
    
    if attacker_id:
        # Check if any adjacent creature is opposite the attacker
        attacker_pos = battlefield.get_position(attacker_id)
        if attacker_pos is None or attacker_id not in adjacent:
            return []
        
        flanking_allies = []
        for ally_id in adjacent:
            if ally_id == attacker_id:
                continue
            
            ally_pos = battlefield.get_position(ally_id)
            if ally_pos is None:
                continue
            
            # Check if ally is roughly opposite attacker (simple check: distance > 5 between them)
            # More accurate: check if target is between them
            attacker_to_target = (target_pos.x - attacker_pos.x, target_pos.y - attacker_pos.y)
            ally_to_target = (target_pos.x - ally_pos.x, target_pos.y - ally_pos.y)
            
            # Opposite sides if vectors point in opposite directions (dot product < 0)
            dot_product = attacker_to_target[0] * ally_to_target[0] + attacker_to_target[1] * ally_to_target[1]
            if dot_product < 0:
                flanking_allies.append(ally_id)
        
        return flanking_allies
    else:
        # Return all adjacent creatures (for general flanking check)
        return adjacent


def calculate_difficult_terrain_cost(
    battlefield: Battlefield,
    from_pos: Position,
    to_pos: Position
) -> int:
    """Calculate movement cost accounting for difficult terrain
    
    Args:
        battlefield: The battlefield
        from_pos: Starting position
        to_pos: Ending position
    
    Returns:
        Movement cost in feet
    """
    base_distance = from_pos.distance_to(to_pos)
    
    # Check if destination has difficult terrain
    terrain_at_dest = battlefield.get_terrain_at(to_pos)
    for terrain in terrain_at_dest:
        if terrain.terrain_type == TerrainType.DIFFICULT:
            return base_distance * 2  # Difficult terrain costs double
    
    return base_distance




