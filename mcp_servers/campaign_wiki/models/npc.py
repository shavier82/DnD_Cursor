"""NPC data models"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class NPCRole(str, Enum):
    """NPC role types"""
    ALLY = "ally"
    ENEMY = "enemy"
    NEUTRAL = "neutral"
    QUEST_GIVER = "quest_giver"
    MERCHANT = "merchant"
    FACTION_LEADER = "faction_leader"
    COMPANION = "companion"


class RelationshipType(str, Enum):
    """Types of relationships"""
    FAMILY = "family"
    FRIEND = "friend"
    ENEMY = "enemy"
    RIVAL = "rival"
    ROMANTIC = "romantic"
    BUSINESS = "business"
    MENTOR_STUDENT = "mentor_student"
    ALLY = "ally"
    NEUTRAL = "neutral"


class NPC(BaseModel):
    """NPC character model"""
    
    # Identity
    npc_id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="NPC name")
    title: Optional[str] = Field(default=None, description="Title (e.g., 'Sir', 'Lord')")
    aliases: List[str] = Field(default_factory=list, description="Known aliases")
    
    # Basic Info
    race: Optional[str] = Field(default=None, description="Race")
    age: Optional[int] = Field(default=None, description="Age")
    gender: Optional[str] = Field(default=None, description="Gender")
    occupation: Optional[str] = Field(default=None, description="Occupation")
    
    # Role
    role: NPCRole = Field(default=NPCRole.NEUTRAL, description="NPC's role")
    faction: Optional[str] = Field(default=None, description="Faction affiliation")
    location: Optional[str] = Field(default=None, description="Current/home location")
    
    # Description
    description: str = Field(default="", description="Physical description")
    personality: str = Field(default="", description="Personality traits")
    motivations: List[str] = Field(default_factory=list, description="Goals/motivations")
    secrets: List[str] = Field(default_factory=list, description="Hidden information")
    
    # Story
    background: str = Field(default="", description="Backstory")
    first_met: Optional[str] = Field(default=None, description="When/where party met them")
    last_seen: Optional[str] = Field(default=None, description="Last interaction")
    
    # Status
    alive: bool = Field(default=True, description="Whether NPC is alive")
    disposition: int = Field(default=0, ge=-10, le=10, description="Disposition toward party (-10 hostile, 0 neutral, +10 friendly)")
    
    # Related Content
    quests: List[str] = Field(default_factory=list, description="Quest IDs related to this NPC")
    items: List[str] = Field(default_factory=list, description="Notable items they possess")
    notes: List[str] = Field(default_factory=list, description="Session notes about this NPC")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for searching")
    image_path: Optional[str] = Field(default=None, description="Path to NPC portrait")
    
    # World Anvil
    world_anvil_id: Optional[str] = Field(default=None, description="World Anvil article ID")


class NPCRelationship(BaseModel):
    """Relationship between two NPCs or NPC and PC"""
    
    from_entity: str = Field(..., description="Entity ID (NPC or PC)")
    to_entity: str = Field(..., description="Target entity ID")
    relationship_type: RelationshipType = Field(..., description="Type of relationship")
    description: str = Field(default="", description="Description of relationship")
    strength: int = Field(default=5, ge=1, le=10, description="Relationship strength (1-10)")
    is_public: bool = Field(default=True, description="Whether relationship is known to party")
    notes: List[str] = Field(default_factory=list, description="Notes about relationship")




