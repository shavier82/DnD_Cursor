"""Quest data models"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class QuestStatus(str, Enum):
    """Quest status"""
    NOT_STARTED = "not_started"
    AVAILABLE = "available"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


class QuestType(str, Enum):
    """Quest type categories"""
    MAIN = "main"
    SIDE = "side"
    PERSONAL = "personal"
    FACTION = "faction"
    BOUNTY = "bounty"
    FETCH = "fetch"
    ESCORT = "escort"
    INVESTIGATION = "investigation"
    RESCUE = "rescue"
    COMBAT = "combat"


class Quest(BaseModel):
    """Quest model"""
    
    # Identity
    quest_id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Quest name")
    quest_type: QuestType = Field(default=QuestType.SIDE, description="Type of quest")
    
    # Description
    description: str = Field(..., description="Quest description")
    objectives: List[str] = Field(default_factory=list, description="Quest objectives")
    objectives_completed: List[bool] = Field(default_factory=list, description="Which objectives are complete")
    
    # Quest Giver
    quest_giver: Optional[str] = Field(default=None, description="NPC ID who gave quest")
    quest_giver_location: Optional[str] = Field(default=None, description="Location where quest was given")
    
    # Status
    status: QuestStatus = Field(default=QuestStatus.NOT_STARTED, description="Current status")
    date_accepted: Optional[datetime] = Field(default=None, description="When quest was accepted")
    date_completed: Optional[datetime] = Field(default=None, description="When quest was completed")
    
    # Rewards
    reward_gold: int = Field(default=0, ge=0, description="Gold reward")
    reward_items: List[str] = Field(default_factory=list, description="Item rewards")
    reward_xp: int = Field(default=0, ge=0, description="XP reward")
    reward_reputation: Dict[str, int] = Field(default_factory=dict, description="Reputation changes by faction")
    
    # Related Content
    related_npcs: List[str] = Field(default_factory=list, description="NPC IDs involved")
    related_locations: List[str] = Field(default_factory=list, description="Location IDs involved")
    related_quests: List[str] = Field(default_factory=list, description="Related quest IDs")
    
    # Story
    background: str = Field(default="", description="Quest background/context")
    consequences: List[str] = Field(default_factory=list, description="Consequences of quest outcome")
    notes: List[str] = Field(default_factory=list, description="Session notes about quest")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for searching")
    priority: int = Field(default=5, ge=1, le=10, description="Priority level (1-10)")
    
    # World Anvil
    world_anvil_id: Optional[str] = Field(default=None, description="World Anvil article ID")




