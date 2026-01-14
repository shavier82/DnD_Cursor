"""Location data models"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from enum import Enum


class LocationType(str, Enum):
    """Location type categories"""
    CITY = "city"
    TOWN = "town"
    VILLAGE = "village"
    DUNGEON = "dungeon"
    RUINS = "ruins"
    WILDERNESS = "wilderness"
    BUILDING = "building"
    TAVERN = "tavern"
    SHOP = "shop"
    TEMPLE = "temple"
    CASTLE = "castle"
    CAVE = "cave"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    PLANE = "plane"
    OTHER = "other"


class Location(BaseModel):
    """Location model"""
    
    # Identity
    location_id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Location name")
    location_type: LocationType = Field(..., description="Type of location")
    
    # Geography
    parent_location: Optional[str] = Field(default=None, description="Parent location ID (e.g., city for a tavern)")
    region: Optional[str] = Field(default=None, description="Region/province")
    coordinates: Optional[tuple[int, int]] = Field(default=None, description="Map coordinates")
    
    # Description
    description: str = Field(default="", description="General description")
    notable_features: List[str] = Field(default_factory=list, description="Notable features")
    atmosphere: str = Field(default="", description="Atmosphere/feeling of place")
    
    # Inhabitants
    population: Optional[int] = Field(default=None, description="Population size")
    dominant_race: Optional[str] = Field(default=None, description="Dominant race")
    npcs: List[str] = Field(default_factory=list, description="NPC IDs present here")
    factions: List[str] = Field(default_factory=list, description="Factions present")
    
    # Story
    history: str = Field(default="", description="Historical background")
    current_events: List[str] = Field(default_factory=list, description="Current happenings")
    rumors: List[str] = Field(default_factory=list, description="Rumors heard here")
    
    # Practical
    services: List[str] = Field(default_factory=list, description="Available services")
    shops: List[str] = Field(default_factory=list, description="Shops/merchants")
    inns_taverns: List[str] = Field(default_factory=list, description="Inns and taverns")
    dangers: List[str] = Field(default_factory=list, description="Known dangers")
    
    # Status
    visited: bool = Field(default=False, description="Whether party has visited")
    discovered_secrets: List[str] = Field(default_factory=list, description="Secrets party has discovered")
    
    # Related Content
    quests: List[str] = Field(default_factory=list, description="Quest IDs related to location")
    encounters: List[str] = Field(default_factory=list, description="Encounter IDs that occurred here")
    
    # Maps
    map_path: Optional[str] = Field(default=None, description="Path to location map image")
    battle_map_path: Optional[str] = Field(default=None, description="Path to battle map (if applicable)")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for searching")
    notes: List[str] = Field(default_factory=list, description="Session notes about location")
    
    # World Anvil
    world_anvil_id: Optional[str] = Field(default=None, description="World Anvil article ID")




