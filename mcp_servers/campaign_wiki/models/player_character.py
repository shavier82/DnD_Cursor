"""Player Character data models"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from enum import Enum


class AbilityScores(BaseModel):
    """Character ability scores"""
    strength: int = Field(default=10, ge=1, le=30)
    dexterity: int = Field(default=10, ge=1, le=30)
    constitution: int = Field(default=10, ge=1, le=30)
    intelligence: int = Field(default=10, ge=1, le=30)
    wisdom: int = Field(default=10, ge=1, le=30)
    charisma: int = Field(default=10, ge=1, le=30)
    
    def modifier(self, ability: str) -> int:
        """Calculate ability modifier"""
        score = getattr(self, ability.lower())
        return (score - 10) // 2


class HitPoints(BaseModel):
    """HP tracking"""
    current: int = Field(..., description="Current HP")
    maximum: int = Field(..., description="Max HP")
    temporary: int = Field(default=0, description="Temp HP")


class Currency(BaseModel):
    """Character wealth"""
    cp: int = Field(default=0, description="Copper pieces")
    sp: int = Field(default=0, description="Silver pieces")
    ep: int = Field(default=0, description="Electrum pieces")
    gp: int = Field(default=0, description="Gold pieces")
    pp: int = Field(default=0, description="Platinum pieces")
    
    def total_gp(self) -> float:
        """Calculate total wealth in GP"""
        return (
            self.cp / 100 +
            self.sp / 10 +
            self.ep / 2 +
            self.gp +
            self.pp * 10
        )


class SpellSlots(BaseModel):
    """Spell slot tracking"""
    level: int = Field(..., ge=1, le=9, description="Spell level")
    maximum: int = Field(..., ge=0, description="Max slots")
    remaining: int = Field(..., ge=0, description="Remaining slots")


class ClassResource(BaseModel):
    """Class-specific resource (Ki, Rage, etc.)"""
    name: str = Field(..., description="Resource name")
    maximum: int = Field(..., ge=0, description="Max uses")
    remaining: int = Field(..., ge=0, description="Remaining uses")
    active: bool = Field(default=False, description="Currently active")
    recharge: str = Field(default="long_rest", description="Recharge type")


class InventoryItem(BaseModel):
    """Inventory item"""
    name: str = Field(..., description="Item name")
    quantity: int = Field(default=1, ge=0, description="Quantity")
    weight: float = Field(default=0.0, ge=0, description="Weight in lbs")
    item_type: str = Field(default="", description="Item type")
    equipped: bool = Field(default=False, description="Is equipped")
    notes: str = Field(default="", description="Item notes")


class Weapon(BaseModel):
    """Weapon or attack"""
    name: str = Field(..., description="Weapon name")
    attack_bonus: int = Field(default=0, description="Attack bonus")
    damage_dice: str = Field(..., description="Damage dice (e.g., '1d8+2')")
    damage_type: str = Field(..., description="Damage type")
    properties: List[str] = Field(default_factory=list, description="Weapon properties")


class PlayerCharacter(BaseModel):
    """Complete player character model"""
    
    # Identity
    character_id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Character name")
    player_name: Optional[str] = Field(default=None, description="Player name")
    
    # Core Info
    char_class: str = Field(..., description="Character class")
    level: int = Field(default=1, ge=1, le=20, description="Character level")
    race: str = Field(default="", description="Character race")
    background: str = Field(default="", description="Character background")
    alignment: str = Field(default="", description="Alignment")
    
    # Ability Scores
    ability_scores: AbilityScores = Field(default_factory=AbilityScores)
    
    # Combat Stats
    hp: HitPoints = Field(..., description="Hit points")
    ac: int = Field(default=10, ge=1, description="Armor Class")
    initiative_bonus: int = Field(default=0, description="Initiative bonus")
    speed: int = Field(default=30, ge=0, description="Speed in feet")
    proficiency_bonus: int = Field(default=2, ge=2, description="Proficiency bonus")
    
    # Proficiencies
    armor_proficiencies: List[str] = Field(default_factory=list)
    weapon_proficiencies: List[str] = Field(default_factory=list)
    tool_proficiencies: List[str] = Field(default_factory=list)
    saving_throw_proficiencies: List[str] = Field(default_factory=list)
    skill_proficiencies: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    
    # Progression
    xp: int = Field(default=0, ge=0, description="Experience points")
    xp_to_next_level: int = Field(default=300, ge=0, description="XP needed for next level")
    
    # Magic
    spell_slots: List[SpellSlots] = Field(default_factory=list, description="Spell slots by level")
    spells_known: List[str] = Field(default_factory=list, description="Known spells")
    spells_prepared: List[str] = Field(default_factory=list, description="Prepared spells")
    cantrips: List[str] = Field(default_factory=list, description="Known cantrips")
    spellcasting_ability: Optional[str] = Field(default=None, description="Spellcasting ability")
    spell_save_dc: Optional[int] = Field(default=None, description="Spell save DC")
    spell_attack_bonus: Optional[int] = Field(default=None, description="Spell attack bonus")
    
    # Resources
    class_resources: List[ClassResource] = Field(default_factory=list, description="Class resources")
    hit_dice: Dict[str, int] = Field(default_factory=dict, description="Hit dice remaining")
    
    # Equipment & Wealth
    inventory: List[InventoryItem] = Field(default_factory=list, description="Inventory items")
    weapons: List[Weapon] = Field(default_factory=list, description="Weapons and attacks")
    currency: Currency = Field(default_factory=Currency, description="Currency")
    
    # Character Details
    personality_traits: str = Field(default="", description="Personality traits")
    ideals: str = Field(default="", description="Ideals")
    bonds: str = Field(default="", description="Bonds")
    flaws: str = Field(default="", description="Flaws")
    backstory: str = Field(default="", description="Character backstory")
    appearance: str = Field(default="", description="Physical appearance")
    
    # Features & Traits
    features: List[str] = Field(default_factory=list, description="Class/racial features")
    
    # Campaign Integration
    quests: List[str] = Field(default_factory=list, description="Active quest IDs")
    relationships: List[str] = Field(default_factory=list, description="Relationship IDs")
    notes: str = Field(default="", description="DM notes")
    
    # Sync Metadata
    last_synced: Optional[str] = Field(default=None, description="Last sync timestamp")
    source: str = Field(default="google_sheets", description="Data source")
    
    def calculate_ability_modifier(self, ability: str) -> int:
        """Calculate ability score modifier"""
        return self.ability_scores.modifier(ability)
    
    def calculate_proficiency_bonus(self) -> int:
        """Calculate proficiency bonus from level"""
        return 2 + ((self.level - 1) // 4)
    
    def calculate_spell_save_dc(self) -> int:
        """Calculate spell save DC"""
        if not self.spellcasting_ability:
            return None
        mod = self.calculate_ability_modifier(self.spellcasting_ability)
        return 8 + self.proficiency_bonus + mod
    
    def calculate_spell_attack_bonus(self) -> int:
        """Calculate spell attack bonus"""
        if not self.spellcasting_ability:
            return None
        mod = self.calculate_ability_modifier(self.spellcasting_ability)
        return self.proficiency_bonus + mod
    
    def total_weight_carried(self) -> float:
        """Calculate total inventory weight"""
        return sum(item.weight * item.quantity for item in self.inventory)
    
    def carrying_capacity(self) -> int:
        """Calculate carrying capacity"""
        return self.ability_scores.strength * 15

