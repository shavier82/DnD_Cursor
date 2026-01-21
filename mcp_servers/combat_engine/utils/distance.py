"""Distance and AoE calculations using shapely"""

from typing import List, Tuple, Optional
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import unary_union
import math

from models.battlefield import Position, Battlefield


class AoEShape:
    """Area of Effect shapes for D&D 5e spells"""
    
    @staticmethod
    def sphere(center: Position, radius: int) -> Point:
        """Create a sphere AoE (e.g., Fireball - 20ft radius)"""
        # Convert to feet, create circle
        center_feet = Point(center.x * 5, center.y * 5)
        return center_feet.buffer(radius)
    
    @staticmethod
    def cube(corner: Position, size: int) -> Polygon:
        """Create a cube AoE (e.g., Thunderwave - 15ft cube)"""
        # Cube originates from caster, size is in feet
        x, y = corner.x * 5, corner.y * 5
        return Polygon([
            (x, y),
            (x + size, y),
            (x + size, y + size),
            (x, y + size)
        ])
    
    @staticmethod
    def cone(origin: Position, direction: float, length: int, width_angle: float = 53.13) -> Polygon:
        """Create a cone AoE (e.g., Burning Hands - 15ft cone)
        
        Args:
            origin: Starting position
            direction: Direction in degrees (0=East, 90=North, 180=West, 270=South)
            length: Length of cone in feet
            width_angle: Width of cone in degrees (default ~53° for D&D 5e cones)
        """
        # Convert origin to feet
        ox, oy = origin.x * 5, origin.y * 5
        
        # Calculate cone points
        direction_rad = math.radians(direction)
        half_angle = math.radians(width_angle / 2)
        
        # Left edge of cone
        left_angle = direction_rad + half_angle
        left_x = ox + length * math.cos(left_angle)
        left_y = oy + length * math.sin(left_angle)
        
        # Right edge of cone
        right_angle = direction_rad - half_angle
        right_x = ox + length * math.cos(right_angle)
        right_y = oy + length * math.sin(right_angle)
        
        # Create triangle for cone
        return Polygon([(ox, oy), (left_x, left_y), (right_x, right_y)])
    
    @staticmethod
    def line(start: Position, end: Position, width: int = 5) -> Polygon:
        """Create a line AoE (e.g., Lightning Bolt - 100ft line, 5ft wide)"""
        # Convert to feet
        sx, sy = start.x * 5, start.y * 5
        ex, ey = end.x * 5, end.y * 5
        
        # Create line and buffer it
        line = LineString([(sx, sy), (ex, ey)])
        return line.buffer(width / 2)
    
    @staticmethod
    def cylinder(center: Position, radius: int, height: int = 10) -> Point:
        """Create a cylinder AoE (e.g., Flame Strike - 10ft radius, 40ft high)
        Note: Height is ignored in 2D combat, but tracked for 3D scenarios
        """
        # For 2D combat, cylinder is same as sphere
        return AoEShape.sphere(center, radius)


def calculate_distance(pos1: Position, pos2: Position) -> int:
    """Calculate distance between two positions in feet (D&D 5e rules)"""
    return pos1.distance_to(pos2)


def get_creatures_in_aoe(
    battlefield: Battlefield,
    aoe_shape: str,
    **kwargs
) -> List[str]:
    """Get all creatures within an AoE
    
    Args:
        battlefield: The battlefield
        aoe_shape: Type of AoE ("sphere", "cube", "cone", "line", "cylinder")
        **kwargs: Shape-specific parameters
            sphere: center (Position), radius (int)
            cube: corner (Position), size (int)
            cone: origin (Position), direction (float), length (int)
            line: start (Position), end (Position), width (int)
            cylinder: center (Position), radius (int)
    
    Returns:
        List of creature IDs in the AoE
    """
    # Create the AoE geometry
    if aoe_shape == "sphere":
        geometry = AoEShape.sphere(kwargs["center"], kwargs["radius"])
    elif aoe_shape == "cube":
        geometry = AoEShape.cube(kwargs["corner"], kwargs["size"])
    elif aoe_shape == "cone":
        geometry = AoEShape.cone(
            kwargs["origin"],
            kwargs["direction"],
            kwargs["length"],
            kwargs.get("width_angle", 53.13)
        )
    elif aoe_shape == "line":
        geometry = AoEShape.line(
            kwargs["start"],
            kwargs["end"],
            kwargs.get("width", 5)
        )
    elif aoe_shape == "cylinder":
        geometry = AoEShape.cylinder(kwargs["center"], kwargs["radius"])
    else:
        raise ValueError(f"Unknown AoE shape: {aoe_shape}")
    
    # Check which creatures are in the AoE
    creatures_in_aoe = []
    for creature_id, pos in battlefield.creature_positions.items():
        creature_point = Point(pos.x * 5, pos.y * 5)
        if geometry.contains(creature_point) or geometry.intersects(creature_point.buffer(2.5)):
            creatures_in_aoe.append(creature_id)
    
    return creatures_in_aoe


def calculate_path_distance(
    battlefield: Battlefield,
    start: Position,
    end: Position,
    avoid_creatures: bool = True
) -> Optional[int]:
    """Calculate actual movement distance accounting for obstacles
    
    Args:
        battlefield: The battlefield
        start: Starting position
        end: Ending position
        avoid_creatures: Whether to path around other creatures
    
    Returns:
        Distance in feet, or None if no path exists
    """
    # Simple implementation: just use straight-line distance
    # For more complex pathfinding, could use networkx with A*
    
    # Check if direct path is possible
    if battlefield.is_passable(end):
        if not avoid_creatures or not battlefield.is_occupied(end):
            return start.distance_to(end)
    
    # If direct path blocked, would need pathfinding algorithm
    # For now, return None to indicate no simple path
    return None


def get_closest_creature(
    battlefield: Battlefield,
    from_creature_id: str,
    candidates: List[str],
    exclude_self: bool = True
) -> Optional[Tuple[str, int]]:
    """Find the closest creature from a list of candidates
    
    Args:
        battlefield: The battlefield
        from_creature_id: Creature to measure from
        candidates: List of candidate creature IDs
        exclude_self: Whether to exclude from_creature_id from candidates
    
    Returns:
        Tuple of (creature_id, distance) or None if no candidates
    """
    from_pos = battlefield.get_position(from_creature_id)
    if from_pos is None:
        return None
    
    closest = None
    closest_distance = float('inf')
    
    for candidate_id in candidates:
        if exclude_self and candidate_id == from_creature_id:
            continue
        
        candidate_pos = battlefield.get_position(candidate_id)
        if candidate_pos is None:
            continue
        
        distance = from_pos.distance_to(candidate_pos)
        if distance < closest_distance:
            closest = candidate_id
            closest_distance = distance
    
    return (closest, int(closest_distance)) if closest else None


def get_creatures_within_reach(
    battlefield: Battlefield,
    creature_id: str,
    reach: int = 5
) -> List[str]:
    """Get all creatures within melee reach
    
    Args:
        battlefield: The battlefield
        creature_id: The creature
        reach: Reach in feet (default 5, some weapons have 10)
    
    Returns:
        List of creature IDs within reach
    """
    pos = battlefield.get_position(creature_id)
    if pos is None:
        return []
    
    within_reach = []
    for other_id, other_pos in battlefield.creature_positions.items():
        if other_id != creature_id:
            distance = pos.distance_to(other_pos)
            if distance <= reach:
                within_reach.append(other_id)
    
    return within_reach




