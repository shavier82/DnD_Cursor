"""Condition tracking and effects"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class DurationType(str, Enum):
    """Duration types for conditions"""
    ROUNDS = "rounds"
    MINUTES = "minutes"
    HOURS = "hours"
    UNTIL_SAVE = "until_save"
    UNTIL_LONG_REST = "until_long_rest"
    PERMANENT = "permanent"


class ConditionEffect(BaseModel):
    """Effects of a D&D 5e condition"""
    
    # Standard D&D 5e conditions with their effects
    CONDITION_EFFECTS: Dict[str, Dict[str, Any]] = {
        "blinded": {
            "description": "Can't see, auto-fail sight checks",
            "attack_disadvantage": True,
            "attacks_have_advantage": True,
        },
        "charmed": {
            "description": "Can't attack charmer, charmer has advantage on social checks",
            "cannot_attack_source": True,
        },
        "deafened": {
            "description": "Can't hear, auto-fail hearing checks",
        },
        "frightened": {
            "description": "Disadvantage on checks/attacks while source visible, can't move closer",
            "attack_disadvantage": True,
            "ability_check_disadvantage": True,
        },
        "grappled": {
            "description": "Speed becomes 0, can't benefit from speed bonuses",
            "speed_override": 0,
        },
        "incapacitated": {
            "description": "Can't take actions or reactions",
            "cannot_act": True,
            "cannot_react": True,
        },
        "invisible": {
            "description": "Impossible to see, attack rolls have advantage, attacks against have disadvantage",
            "attack_advantage": True,
            "attacks_have_disadvantage": True,
        },
        "paralyzed": {
            "description": "Incapacitated, can't move or speak, auto-fail STR/DEX saves, attacks have advantage, hits within 5ft are crits",
            "cannot_act": True,
            "cannot_react": True,
            "cannot_move": True,
            "auto_fail_str_saves": True,
            "auto_fail_dex_saves": True,
            "attacks_have_advantage": True,
            "melee_hits_are_crits": True,
        },
        "petrified": {
            "description": "Transformed to stone, incapacitated, can't move or speak, unaware, resistant to all damage, immune to poison/disease",
            "cannot_act": True,
            "cannot_react": True,
            "cannot_move": True,
            "resistance_all": True,
        },
        "poisoned": {
            "description": "Disadvantage on attack rolls and ability checks",
            "attack_disadvantage": True,
            "ability_check_disadvantage": True,
        },
        "prone": {
            "description": "Disadvantage on attacks, melee attacks against have advantage, ranged attacks against have disadvantage",
            "attack_disadvantage": True,
            "melee_attacks_have_advantage": True,
            "ranged_attacks_have_disadvantage": True,
            "movement_cost_double": True,
        },
        "restrained": {
            "description": "Speed is 0, attack disadvantage, attacks against have advantage, disadvantage on DEX saves",
            "speed_override": 0,
            "attack_disadvantage": True,
            "attacks_have_advantage": True,
            "dex_save_disadvantage": True,
        },
        "stunned": {
            "description": "Incapacitated, can't move, can speak falteringly, auto-fail STR/DEX saves, attacks against have advantage",
            "cannot_act": True,
            "cannot_react": True,
            "cannot_move": True,
            "auto_fail_str_saves": True,
            "auto_fail_dex_saves": True,
            "attacks_have_advantage": True,
        },
        "unconscious": {
            "description": "Incapacitated, can't move or speak, unaware, drop held items, fall prone, auto-fail STR/DEX saves, attacks have advantage, hits within 5ft are crits",
            "cannot_act": True,
            "cannot_react": True,
            "cannot_move": True,
            "auto_fail_str_saves": True,
            "auto_fail_dex_saves": True,
            "attacks_have_advantage": True,
            "melee_hits_are_crits": True,
            "auto_prone": True,
        },
        "exhaustion": {
            "description": "Cumulative penalties (see exhaustion levels)",
            "has_levels": True,
        },
    }
    
    name: str = Field(..., description="Condition name")
    effects: Dict[str, Any] = Field(default_factory=dict, description="Condition effects")
    
    @classmethod
    def from_name(cls, name: str) -> "ConditionEffect":
        """Create condition effect from standard D&D 5e condition name"""
        name_lower = name.lower()
        effects = cls.CONDITION_EFFECTS.get(name_lower, {})
        return cls(name=name, effects=effects)
    
    def has_effect(self, effect: str) -> bool:
        """Check if condition has a specific effect"""
        return self.effects.get(effect, False)


class Condition(BaseModel):
    """An active condition on a combatant"""
    
    name: str = Field(..., description="Condition name")
    duration_type: DurationType = Field(..., description="How duration is measured")
    duration_remaining: int = Field(default=0, ge=0, description="Duration remaining")
    
    # Save DC (for conditions that allow saves)
    save_dc: Optional[int] = Field(default=None, description="DC to save against condition")
    save_ability: Optional[str] = Field(default=None, description="Ability to save with (STR, DEX, etc.)")
    save_on_turn_end: bool = Field(default=False, description="Can save at end of turn")
    
    # Source tracking
    source_creature_id: Optional[str] = Field(default=None, description="Who applied this condition")
    source_spell: Optional[str] = Field(default=None, description="Spell that caused condition")
    
    # Exhaustion level (special case)
    exhaustion_level: int = Field(default=1, ge=1, le=6, description="Exhaustion level (1-6)")
    
    # Metadata
    effect: ConditionEffect = Field(default_factory=lambda: ConditionEffect(name="unknown", effects={}))
    
    @classmethod
    def create(
        cls,
        name: str,
        duration_type: DurationType = DurationType.ROUNDS,
        duration: int = 1,
        save_dc: Optional[int] = None,
        save_ability: Optional[str] = None,
        source_creature_id: Optional[str] = None,
    ) -> "Condition":
        """Create a condition with standard effects"""
        effect = ConditionEffect.from_name(name)
        return cls(
            name=name,
            duration_type=duration_type,
            duration_remaining=duration,
            save_dc=save_dc,
            save_ability=save_ability,
            source_creature_id=source_creature_id,
            effect=effect,
        )
    
    def tick(self) -> bool:
        """Decrement duration. Returns True if condition expired."""
        if self.duration_type in [DurationType.PERMANENT, DurationType.UNTIL_SAVE, DurationType.UNTIL_LONG_REST]:
            return False
        
        self.duration_remaining = max(0, self.duration_remaining - 1)
        return self.duration_remaining == 0
    
    def is_expired(self) -> bool:
        """Check if condition has expired"""
        if self.duration_type in [DurationType.PERMANENT, DurationType.UNTIL_SAVE, DurationType.UNTIL_LONG_REST]:
            return False
        return self.duration_remaining <= 0


class ExhaustionLevel:
    """Exhaustion level effects"""
    
    EFFECTS = {
        1: "Disadvantage on ability checks",
        2: "Speed halved",
        3: "Disadvantage on attack rolls and saving throws",
        4: "HP maximum halved",
        5: "Speed reduced to 0",
        6: "Death",
    }
    
    @classmethod
    def get_effect(cls, level: int) -> str:
        """Get description of exhaustion level"""
        effects = [cls.EFFECTS[i] for i in range(1, min(level + 1, 7))]
        return "; ".join(effects)
    
    @classmethod
    def affects_speed(cls, level: int) -> bool:
        """Check if exhaustion affects speed"""
        return level >= 2
    
    @classmethod
    def affects_attacks(cls, level: int) -> bool:
        """Check if exhaustion affects attacks"""
        return level >= 3
    
    @classmethod
    def affects_hp(cls, level: int) -> bool:
        """Check if exhaustion affects max HP"""
        return level >= 4
    
    @classmethod
    def is_fatal(cls, level: int) -> bool:
        """Check if exhaustion level is fatal"""
        return level >= 6




