"""Creature and Combatant data models"""

from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
from enum import Enum


class CreatureType(str, Enum):
    """D&D creature types"""
    PLAYER = "player"
    MONSTER = "monster"
    NPC = "npc"


class DamageType(str, Enum):
    """D&D damage types"""
    ACID = "acid"
    BLUDGEONING = "bludgeoning"
    COLD = "cold"
    FIRE = "fire"
    FORCE = "force"
    LIGHTNING = "lightning"
    NECROTIC = "necrotic"
    PIERCING = "piercing"
    POISON = "poison"
    PSYCHIC = "psychic"
    RADIANT = "radiant"
    SLASHING = "slashing"
    THUNDER = "thunder"


class Creature(BaseModel):
    """Base creature model with D&D 5e stats"""
    
    # Identity
    creature_id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Creature name")
    creature_type: CreatureType = Field(..., description="Player/Monster/NPC")
    
    # Core Stats
    max_hp: int = Field(..., ge=1, description="Maximum HP")
    current_hp: int = Field(..., description="Current HP")
    temp_hp: int = Field(default=0, ge=0, description="Temporary HP")
    ac: int = Field(..., ge=1, description="Armor Class")
    
    # Ability Scores
    strength: int = Field(..., ge=1, le=30)
    dexterity: int = Field(..., ge=1, le=30)
    constitution: int = Field(..., ge=1, le=30)
    intelligence: int = Field(..., ge=1, le=30)
    wisdom: int = Field(..., ge=1, le=30)
    charisma: int = Field(..., ge=1, le=30)
    
    # Combat Stats
    initiative_bonus: int = Field(default=0, description="Initiative modifier")
    speed: int = Field(default=30, ge=0, description="Movement speed in feet")
    
    # Resistances/Immunities
    damage_resistances: List[DamageType] = Field(default_factory=list)
    damage_immunities: List[DamageType] = Field(default_factory=list)
    damage_vulnerabilities: List[DamageType] = Field(default_factory=list)
    condition_immunities: List[str] = Field(default_factory=list)
    
    # Special Abilities
    special_abilities: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Resources (for monsters with spell slots, legendary actions, etc.)
    spell_slots: Dict[int, int] = Field(default_factory=dict, description="Spell slots by level")
    legendary_actions: int = Field(default=0, description="Legendary actions remaining")
    
    # Metadata
    source: str = Field(default="manual", description="Where this creature was loaded from")
    
    @property
    def is_alive(self) -> bool:
        """Check if creature is alive"""
        return self.current_hp > 0
    
    @property
    def hp_percent(self) -> float:
        """HP as a percentage"""
        return self.current_hp / self.max_hp if self.max_hp > 0 else 0
    
    @property
    def modifier(self, ability: str) -> int:
        """Get ability modifier"""
        ability_score = getattr(self, ability.lower())
        return (ability_score - 10) // 2
    
    def take_damage(self, damage: int, damage_type: Optional[DamageType] = None) -> int:
        """Apply damage, accounting for temp HP and resistances"""
        # Check immunities
        if damage_type and damage_type in self.damage_immunities:
            return 0
        
        # Check resistances/vulnerabilities
        if damage_type:
            if damage_type in self.damage_resistances:
                damage = damage // 2
            elif damage_type in self.damage_vulnerabilities:
                damage = damage * 2
        
        # Apply to temp HP first
        if self.temp_hp > 0:
            if damage <= self.temp_hp:
                self.temp_hp -= damage
                return 0
            else:
                damage -= self.temp_hp
                self.temp_hp = 0
        
        # Apply to current HP
        actual_damage = min(damage, self.current_hp)
        self.current_hp = max(0, self.current_hp - damage)
        
        return actual_damage
    
    def heal(self, healing: int) -> int:
        """Heal the creature"""
        actual_healing = min(healing, self.max_hp - self.current_hp)
        self.current_hp = min(self.max_hp, self.current_hp + healing)
        return actual_healing


class Combatant(BaseModel):
    """Combatant in combat (extends Creature with combat-specific data)"""
    
    creature: Creature = Field(..., description="The creature data")
    
    # Combat State
    initiative: int = Field(..., description="Initiative roll result")
    position: tuple[int, int] = Field(default=(0, 0), description="Grid position (x, y)")
    
    # Turn State
    has_taken_action: bool = Field(default=False)
    has_taken_bonus_action: bool = Field(default=False)
    has_taken_reaction: bool = Field(default=False)
    movement_used: int = Field(default=0, ge=0, description="Movement used this turn")
    
    # Conditions
    active_conditions: List[str] = Field(default_factory=list)
    
    # Concentration
    concentrating_on: Optional[str] = Field(default=None, description="Spell being concentrated on")
    
    # Combat Tracking
    damage_dealt_this_combat: int = Field(default=0, ge=0)
    damage_taken_this_combat: int = Field(default=0, ge=0)
    
    # Death Saves (for players)
    death_save_successes: int = Field(default=0, ge=0, le=3)
    death_save_failures: int = Field(default=0, ge=0, le=3)
    
    @property
    def is_player(self) -> bool:
        """Check if this is a player character"""
        return self.creature.creature_type == CreatureType.PLAYER
    
    @property
    def is_alive(self) -> bool:
        """Check if combatant is alive"""
        return self.creature.is_alive
    
    @property
    def can_act(self) -> bool:
        """Check if combatant can take actions (not incapacitated/stunned/etc.)"""
        incapacitating = ["incapacitated", "stunned", "paralyzed", "unconscious", "petrified"]
        return not any(cond in self.active_conditions for cond in incapacitating)
    
    @property
    def movement_remaining(self) -> int:
        """Remaining movement this turn"""
        speed = self.creature.speed
        
        # Check for speed-reducing conditions
        if "grappled" in self.active_conditions or "restrained" in self.active_conditions:
            speed = 0
        elif "prone" in self.active_conditions:
            speed = speed // 2
        
        return max(0, speed - self.movement_used)
    
    def reset_turn(self):
        """Reset turn state at start of turn"""
        self.has_taken_action = False
        self.has_taken_bonus_action = False
        self.has_taken_reaction = False
        self.movement_used = 0
        
        # Legendary actions reset at start of creature's turn
        if self.creature.legendary_actions > 0:
            self.creature.legendary_actions = 3  # Reset to max
    
    def end_turn(self):
        """Process end-of-turn effects"""
        # This will be called by combat_state to tick condition durations
        pass




