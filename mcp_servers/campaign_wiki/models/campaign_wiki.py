"""Main Campaign Wiki model"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from pathlib import Path
import json

from .npc import NPC, NPCRelationship
from .location import Location
from .quest import Quest
from .timeline import TimelineEvent
from .player_character import PlayerCharacter
from .faction import Faction


class CampaignWiki(BaseModel):
    """Complete campaign wiki state"""
    
    campaign_name: str = Field(..., description="Campaign name")
    
    # Data
    player_characters: Dict[str, PlayerCharacter] = Field(default_factory=dict, description="Player characters")
    npcs: Dict[str, NPC] = Field(default_factory=dict)
    locations: Dict[str, Location] = Field(default_factory=dict)
    quests: Dict[str, Quest] = Field(default_factory=dict)
    timeline: List[TimelineEvent] = Field(default_factory=list)
    relationships: List[NPCRelationship] = Field(default_factory=list)
    
    # Metadata
    session_notes: Dict[int, str] = Field(default_factory=dict, description="Session notes by session number")
    factions: Dict[str, Faction] = Field(default_factory=dict, description="Faction data")
    
    # Paths
    data_path: Optional[str] = Field(default=None, description="Path to wiki data file")
    obsidian_vault: Optional[str] = Field(default=None, description="Obsidian vault path")
    maps_folder: Optional[str] = Field(default=None, description="Maps folder path")
    
    def save(self, path: Optional[str] = None):
        """Save wiki to JSON"""
        save_path = path or self.data_path
        if not save_path:
            raise ValueError("No save path specified")
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(self.model_dump(), f, indent=2, default=str)
    
    @classmethod
    def load(cls, path: str) -> "CampaignWiki":
        """Load wiki from JSON"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Migrate old faction format (Dict[str, Dict] -> Dict[str, Faction])
        if 'factions' in data and data['factions']:
            migrated_factions = {}
            for faction_id, faction_data in data['factions'].items():
                # If it's already a Faction dict (has faction_id), use it directly
                # Otherwise, it's the old format and needs migration
                if isinstance(faction_data, dict):
                    if 'faction_id' not in faction_data:
                        # Old format - create Faction with faction_id from key
                        faction_data['faction_id'] = faction_id
                    try:
                        migrated_factions[faction_id] = Faction(**faction_data)
                    except Exception:
                        # If migration fails, keep as dict (will be converted on next save)
                        migrated_factions[faction_id] = faction_data
                else:
                    migrated_factions[faction_id] = faction_data
            data['factions'] = migrated_factions
        
        return cls(**data)

