"""Timeline data models"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class EventType(str, Enum):
    """Timeline event types"""
    COMBAT = "combat"
    DISCOVERY = "discovery"
    QUEST_START = "quest_start"
    QUEST_COMPLETE = "quest_complete"
    NPC_MET = "npc_met"
    NPC_DEATH = "npc_death"
    LOCATION_DISCOVERED = "location_discovered"
    CHOICE = "choice"
    CONSEQUENCE = "consequence"
    FACTION_REP = "faction_reputation"
    LEVEL_UP = "level_up"
    ITEM_ACQUIRED = "item_acquired"
    STORY_MILESTONE = "story_milestone"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    OTHER = "other"


class TimelineEvent(BaseModel):
    """Timeline event model"""
    
    # Identity
    event_id: str = Field(..., description="Unique identifier")
    event_type: EventType = Field(..., description="Type of event")
    title: str = Field(..., description="Event title")
    
    # When
    session_number: Optional[int] = Field(default=None, description="Session number")
    in_game_date: Optional[str] = Field(default=None, description="In-game date/time")
    real_date: datetime = Field(default_factory=datetime.now, description="Real-world date")
    
    # What
    description: str = Field(..., description="Event description")
    participants: List[str] = Field(default_factory=list, description="PC/NPC IDs involved")
    location: Optional[str] = Field(default=None, description="Location ID where event occurred")
    
    # Related Content
    related_quests: List[str] = Field(default_factory=list, description="Quest IDs affected")
    related_npcs: List[str] = Field(default_factory=list, description="NPC IDs affected")
    related_locations: List[str] = Field(default_factory=list, description="Location IDs affected")
    
    # Consequences
    consequences: List[str] = Field(default_factory=list, description="Consequences of event")
    reputation_changes: Dict[str, int] = Field(default_factory=dict, description="Faction reputation changes")
    
    # Metadata
    significance: int = Field(default=5, ge=1, le=10, description="How significant was this event (1-10)")
    tags: List[str] = Field(default_factory=list, description="Tags for searching")
    notes: str = Field(default="", description="Additional notes")
    
    # World Anvil
    world_anvil_id: Optional[str] = Field(default=None, description="World Anvil article ID")

