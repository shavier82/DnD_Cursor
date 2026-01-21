"""Faction model for campaign wiki"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum


class FactionType(str, Enum):
    """Types of factions"""
    GUILD = "guild"
    RELIGIOUS = "religious"
    MILITARY = "military"
    CRIMINAL = "criminal"
    MERCHANT = "merchant"
    NOBLE = "noble"
    ACADEMIC = "academic"
    ADVENTURER = "adventurer"
    CULT = "cult"
    GOVERNMENT = "government"
    OTHER = "other"


class ReputationLevel(str, Enum):
    """Reputation levels with factions"""
    HATED = "hated"           # -100 to -50
    HOSTILE = "hostile"       # -49 to -25
    UNFRIENDLY = "unfriendly" # -24 to -10
    NEUTRAL = "neutral"       # -9 to 9
    FRIENDLY = "friendly"     # 10 to 24
    HONORED = "honored"       # 25 to 49
    EXALTED = "exalted"       # 50 to 100


class Faction(BaseModel):
    """Faction model with reputation and rank tracking"""
    
    faction_id: str = Field(..., description="Unique faction identifier")
    name: str = Field(..., description="Faction name")
    faction_type: FactionType = Field(default=FactionType.OTHER, description="Type of faction")
    
    # Description
    description: str = Field(default="", description="Faction description")
    goals: List[str] = Field(default_factory=list, description="Faction goals and objectives")
    values: List[str] = Field(default_factory=list, description="Faction values and principles")
    territory: List[str] = Field(default_factory=list, description="Territories controlled")
    
    # Leadership
    leader: Optional[str] = Field(default=None, description="Leader NPC ID or name")
    headquarters: Optional[str] = Field(default=None, description="Headquarters location ID or name")
    
    # Membership
    member_npcs: List[str] = Field(default_factory=list, description="NPC IDs who are members")
    size: Optional[str] = Field(default=None, description="Faction size (small/medium/large/huge)")
    
    # Reputation System
    reputation: Dict[str, int] = Field(
        default_factory=dict,
        description="Reputation scores by character/party name (range: -100 to 100)"
    )
    rank: Dict[str, str] = Field(
        default_factory=dict,
        description="Rank titles by character/party name"
    )
    
    # Rank Structure (hierarchical ranks from lowest to highest)
    rank_structure: List[str] = Field(
        default_factory=list,
        description="List of rank titles from lowest to highest (e.g., ['Initiate', 'Member', 'Veteran', 'Officer', 'Leader'])"
    )
    
    # Benefits and Requirements
    benefits: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Benefits by rank (e.g., {'Member': ['10% discount', 'Access to guild hall']})"
    )
    requirements: Dict[str, str] = Field(
        default_factory=dict,
        description="Requirements for each rank (e.g., {'Officer': 'Reputation 50+ and complete 3 quests'})"
    )
    
    # Relations
    allied_factions: List[str] = Field(default_factory=list, description="Allied faction IDs")
    enemy_factions: List[str] = Field(default_factory=list, description="Enemy faction IDs")
    
    # Status
    active: bool = Field(default=True, description="Whether faction is currently active")
    notes: str = Field(default="", description="Additional notes")
    
    def get_reputation_level(self, character_name: str) -> ReputationLevel:
        """Get reputation level for a character"""
        rep = self.reputation.get(character_name, 0)
        if rep <= -50:
            return ReputationLevel.HATED
        elif rep <= -25:
            return ReputationLevel.HOSTILE
        elif rep <= -10:
            return ReputationLevel.UNFRIENDLY
        elif rep < 10:
            return ReputationLevel.NEUTRAL
        elif rep < 25:
            return ReputationLevel.FRIENDLY
        elif rep < 50:
            return ReputationLevel.HONORED
        else:
            return ReputationLevel.EXALTED
    
    def get_rank_index(self, character_name: str) -> int:
        """Get rank index (0 = lowest, higher = higher rank)"""
        rank_title = self.rank.get(character_name, "")
        if not rank_title or not self.rank_structure:
            return -1
        try:
            return self.rank_structure.index(rank_title)
        except ValueError:
            return -1
    
    def can_promote(self, character_name: str) -> bool:
        """Check if character can be promoted to next rank"""
        current_rank_idx = self.get_rank_index(character_name)
        if current_rank_idx == -1 or current_rank_idx >= len(self.rank_structure) - 1:
            return False
        return True
    
    def promote(self, character_name: str) -> Optional[str]:
        """Promote character to next rank. Returns new rank or None if can't promote."""
        if not self.can_promote(character_name):
            return None
        current_rank_idx = self.get_rank_index(character_name)
        new_rank = self.rank_structure[current_rank_idx + 1]
        self.rank[character_name] = new_rank
        return new_rank
    
    def adjust_reputation(self, character_name: str, amount: int, min_value: int = -100, max_value: int = 100) -> int:
        """Adjust reputation for a character. Returns new reputation value."""
        current = self.reputation.get(character_name, 0)
        new_rep = max(min_value, min(max_value, current + amount))
        self.reputation[character_name] = new_rep
        return new_rep
