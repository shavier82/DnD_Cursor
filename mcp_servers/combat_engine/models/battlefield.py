"""Battlefield and positioning models"""

from typing import List, Optional, Dict, Set
from pydantic import BaseModel, Field
import numpy as np


class Position(BaseModel):
    """A position on the battlefield grid"""
    x: int = Field(..., description="X coordinate (in 5-foot squares)")
    y: int = Field(..., description="Y coordinate (in 5-foot squares)")
    z: int = Field(default=0, description="Z coordinate for elevation (in 5-foot increments)")
    
    def to_tuple(self) -> tuple[int, int, int]:
        """Convert to tuple"""
        return (self.x, self.y, self.z)
    
    def to_feet(self) -> tuple[int, int, int]:
        """Convert to feet"""
        return (self.x * 5, self.y * 5, self.z * 5)
    
    def distance_to(self, other: "Position") -> int:
        """Calculate distance in feet to another position (using D&D 5e rules)"""
        dx = abs(self.x - other.x) * 5
        dy = abs(self.y - other.y) * 5
        dz = abs(self.z - other.z) * 5
        
        # D&D 5e diagonal movement: every other diagonal is 10 feet
        # We use the simpler "max" rule for distance
        return max(dx, dy, dz)
    
    def is_adjacent(self, other: "Position") -> bool:
        """Check if positions are adjacent (within 5 feet)"""
        return self.distance_to(other) <= 5


class TerrainType(str):
    """Types of terrain"""
    NORMAL = "normal"
    DIFFICULT = "difficult"
    IMPASSABLE = "impassable"
    COVER_HALF = "half_cover"
    COVER_THREE_QUARTERS = "three_quarters_cover"
    COVER_TOTAL = "total_cover"


class Terrain(BaseModel):
    """Terrain feature on the battlefield"""
    position: Position = Field(..., description="Position of terrain")
    terrain_type: str = Field(..., description="Type of terrain")
    description: str = Field(default="", description="Description of terrain")
    blocks_line_of_sight: bool = Field(default=False, description="Whether terrain blocks LOS")
    provides_cover: bool = Field(default=False, description="Whether terrain provides cover")
    cover_bonus: int = Field(default=0, description="AC bonus from cover (+2 half, +5 three-quarters)")


class Battlefield(BaseModel):
    """The battlefield grid and terrain"""
    
    # Grid dimensions (in 5-foot squares)
    width: int = Field(..., ge=1, description="Width in 5-foot squares")
    height: int = Field(..., ge=1, description="Height in 5-foot squares")
    
    # Terrain features
    terrain: List[Terrain] = Field(default_factory=list, description="Terrain features")
    
    # Creature positions (tracked separately)
    # creature_id -> Position
    creature_positions: Dict[str, Position] = Field(default_factory=dict)
    
    def is_valid_position(self, pos: Position) -> bool:
        """Check if position is within battlefield bounds"""
        return (
            0 <= pos.x < self.width and
            0 <= pos.y < self.height
        )
    
    def is_passable(self, pos: Position) -> bool:
        """Check if position is passable"""
        if not self.is_valid_position(pos):
            return False
        
        # Check terrain
        for t in self.terrain:
            if t.position.to_tuple() == pos.to_tuple():
                if t.terrain_type == TerrainType.IMPASSABLE:
                    return False
        
        return True
    
    def is_occupied(self, pos: Position, exclude: Optional[str] = None) -> bool:
        """Check if position is occupied by a creature"""
        for creature_id, creature_pos in self.creature_positions.items():
            if creature_id == exclude:
                continue
            if creature_pos.to_tuple() == pos.to_tuple():
                return True
        return False
    
    def get_creature_at(self, pos: Position) -> Optional[str]:
        """Get creature ID at position"""
        for creature_id, creature_pos in self.creature_positions.items():
            if creature_pos.to_tuple() == pos.to_tuple():
                return creature_id
        return None
    
    def move_creature(self, creature_id: str, new_pos: Position) -> bool:
        """Move a creature to a new position"""
        if not self.is_valid_position(new_pos):
            return False
        
        if not self.is_passable(new_pos):
            return False
        
        if self.is_occupied(new_pos, exclude=creature_id):
            return False
        
        self.creature_positions[creature_id] = new_pos
        return True
    
    def get_position(self, creature_id: str) -> Optional[Position]:
        """Get creature's position"""
        return self.creature_positions.get(creature_id)
    
    def get_distance(self, creature_id_a: str, creature_id_b: str) -> Optional[int]:
        """Get distance between two creatures in feet"""
        pos_a = self.get_position(creature_id_a)
        pos_b = self.get_position(creature_id_b)
        
        if pos_a is None or pos_b is None:
            return None
        
        return pos_a.distance_to(pos_b)
    
    def get_creatures_in_radius(self, center: Position, radius: int) -> List[str]:
        """Get all creatures within radius (in feet)"""
        creatures = []
        for creature_id, pos in self.creature_positions.items():
            if center.distance_to(pos) <= radius:
                creatures.append(creature_id)
        return creatures
    
    def get_adjacent_creatures(self, creature_id: str) -> List[str]:
        """Get all creatures adjacent to this creature"""
        pos = self.get_position(creature_id)
        if pos is None:
            return []
        
        adjacent = []
        for other_id, other_pos in self.creature_positions.items():
            if other_id != creature_id and pos.is_adjacent(other_pos):
                adjacent.append(other_id)
        return adjacent
    
    def get_terrain_at(self, pos: Position) -> List[Terrain]:
        """Get all terrain features at position"""
        return [t for t in self.terrain if t.position.to_tuple() == pos.to_tuple()]
    
    def calculate_movement_cost(self, from_pos: Position, to_pos: Position) -> int:
        """Calculate movement cost in feet"""
        base_distance = from_pos.distance_to(to_pos)
        
        # Check for difficult terrain at destination
        terrain = self.get_terrain_at(to_pos)
        for t in terrain:
            if t.terrain_type == TerrainType.DIFFICULT:
                return base_distance * 2
        
        return base_distance
    
    def visualize(self, width: int = 80) -> str:
        """Create ASCII visualization of battlefield"""
        # Create empty grid
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]
        
        # Add terrain
        for t in self.terrain:
            x, y = t.position.x, t.position.y
            if 0 <= x < self.width and 0 <= y < self.height:
                if t.terrain_type == TerrainType.IMPASSABLE:
                    grid[y][x] = "#"
                elif t.provides_cover:
                    grid[y][x] = "◆"
                elif t.terrain_type == TerrainType.DIFFICULT:
                    grid[y][x] = "~"
        
        # Add creatures (numbered)
        for idx, (creature_id, pos) in enumerate(self.creature_positions.items(), 1):
            x, y = pos.x, pos.y
            if 0 <= x < self.width and 0 <= y < self.height:
                grid[y][x] = str(idx) if idx < 10 else "+"
        
        # Build string
        lines = ["+" + "-" * self.width + "+"]
        for row in grid:
            lines.append("|" + "".join(row) + "|")
        lines.append("+" + "-" * self.width + "+")
        
        return "\n".join(lines)




