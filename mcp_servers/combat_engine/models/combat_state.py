"""Combat state management"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

from .creature import Combatant, Creature
from .battlefield import Battlefield, Position
from .condition import Condition, DurationType


class CombatState(BaseModel):
    """Complete combat state"""
    
    # Identity
    combat_id: str = Field(..., description="Unique combat identifier")
    encounter_name: str = Field(default="Unknown Encounter", description="Name of encounter")
    
    # Combatants
    combatants: Dict[str, Combatant] = Field(default_factory=dict, description="All combatants by ID")
    
    # Battlefield
    battlefield: Battlefield = Field(..., description="The battlefield")
    
    # Initiative Order
    initiative_order: List[str] = Field(default_factory=list, description="Creature IDs in initiative order")
    current_turn_index: int = Field(default=0, ge=0, description="Index in initiative order")
    round_number: int = Field(default=1, ge=1, description="Current round number")
    
    # Conditions
    conditions: Dict[str, List[Condition]] = Field(
        default_factory=dict,
        description="Active conditions by creature_id"
    )
    
    # Combat Status
    is_active: bool = Field(default=True, description="Whether combat is ongoing")
    started_at: datetime = Field(default_factory=datetime.now, description="When combat started")
    ended_at: Optional[datetime] = Field(default=None, description="When combat ended")
    
    # Metadata
    encounter_data: Dict[str, Any] = Field(default_factory=dict, description="Original encounter data")
    
    def add_combatant(self, combatant: Combatant) -> bool:
        """Add a combatant to combat"""
        if combatant.creature.creature_id in self.combatants:
            return False
        
        self.combatants[combatant.creature.creature_id] = combatant
        return True
    
    def remove_combatant(self, creature_id: str) -> bool:
        """Remove a combatant from combat"""
        if creature_id not in self.combatants:
            return False
        
        del self.combatants[creature_id]
        
        # Remove from initiative order
        if creature_id in self.initiative_order:
            self.initiative_order.remove(creature_id)
        
        # Clean up conditions
        if creature_id in self.conditions:
            del self.conditions[creature_id]
        
        return True
    
    def get_combatant(self, creature_id: str) -> Optional[Combatant]:
        """Get a combatant by ID"""
        return self.combatants.get(creature_id)
    
    def sort_initiative(self):
        """Sort combatants by initiative (high to low)"""
        self.initiative_order = sorted(
            self.combatants.keys(),
            key=lambda cid: self.combatants[cid].initiative,
            reverse=True
        )
    
    def get_current_combatant(self) -> Optional[Combatant]:
        """Get the combatant whose turn it is"""
        if not self.initiative_order or self.current_turn_index >= len(self.initiative_order):
            return None
        
        creature_id = self.initiative_order[self.current_turn_index]
        return self.get_combatant(creature_id)
    
    def next_turn(self) -> Optional[Combatant]:
        """Advance to next turn"""
        if not self.initiative_order:
            return None
        
        # End current combatant's turn
        current = self.get_current_combatant()
        if current:
            current.end_turn()
            self.tick_conditions(current.creature.creature_id)
        
        # Advance turn index
        self.current_turn_index += 1
        
        # Check for new round
        if self.current_turn_index >= len(self.initiative_order):
            self.current_turn_index = 0
            self.round_number += 1
        
        # Start new combatant's turn
        next_combatant = self.get_current_combatant()
        if next_combatant:
            next_combatant.reset_turn()
        
        return next_combatant
    
    def apply_condition(
        self,
        creature_id: str,
        condition_name: str,
        duration_type: DurationType = DurationType.ROUNDS,
        duration: int = 1,
        save_dc: Optional[int] = None,
        save_ability: Optional[str] = None,
        source_creature_id: Optional[str] = None,
    ) -> bool:
        """Apply a condition to a combatant"""
        if creature_id not in self.combatants:
            return False
        
        condition = Condition.create(
            name=condition_name,
            duration_type=duration_type,
            duration=duration,
            save_dc=save_dc,
            save_ability=save_ability,
            source_creature_id=source_creature_id,
        )
        
        if creature_id not in self.conditions:
            self.conditions[creature_id] = []
        
        # Check if condition already exists (don't stack, refresh duration instead)
        existing = next((c for c in self.conditions[creature_id] if c.name == condition_name), None)
        if existing:
            existing.duration_remaining = max(existing.duration_remaining, condition.duration_remaining)
        else:
            self.conditions[creature_id].append(condition)
            
            # Update combatant's active conditions list
            combatant = self.get_combatant(creature_id)
            if combatant and condition_name not in combatant.active_conditions:
                combatant.active_conditions.append(condition_name)
        
        return True
    
    def remove_condition(self, creature_id: str, condition_name: str) -> bool:
        """Remove a condition from a combatant"""
        if creature_id not in self.conditions:
            return False
        
        self.conditions[creature_id] = [
            c for c in self.conditions[creature_id]
            if c.name != condition_name
        ]
        
        # Update combatant's active conditions list
        combatant = self.get_combatant(creature_id)
        if combatant and condition_name in combatant.active_conditions:
            combatant.active_conditions.remove(condition_name)
        
        return True
    
    def tick_conditions(self, creature_id: str):
        """Tick down condition durations for a creature"""
        if creature_id not in self.conditions:
            return
        
        expired = []
        for condition in self.conditions[creature_id]:
            if condition.tick():
                expired.append(condition.name)
        
        # Remove expired conditions
        for condition_name in expired:
            self.remove_condition(creature_id, condition_name)
    
    def get_conditions(self, creature_id: str) -> List[Condition]:
        """Get all active conditions for a creature"""
        return self.conditions.get(creature_id, [])
    
    def check_combat_end(self) -> Optional[str]:
        """Check if combat should end. Returns winning side or None."""
        alive_players = [
            c for c in self.combatants.values()
            if c.is_player and c.is_alive
        ]
        alive_enemies = [
            c for c in self.combatants.values()
            if not c.is_player and c.is_alive
        ]
        
        if not alive_enemies:
            return "players"
        elif not alive_players:
            return "enemies"
        
        return None
    
    def end_combat(self, winner: Optional[str] = None):
        """End combat"""
        self.is_active = False
        self.ended_at = datetime.now()
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get a summary of combat status"""
        current = self.get_current_combatant()
        
        return {
            "combat_id": self.combat_id,
            "encounter_name": self.encounter_name,
            "round": self.round_number,
            "current_turn": {
                "creature_id": current.creature.creature_id if current else None,
                "name": current.creature.name if current else None,
                "initiative": current.initiative if current else None,
            },
            "combatants": {
                cid: {
                    "name": c.creature.name,
                    "hp": f"{c.creature.current_hp}/{c.creature.max_hp}",
                    "hp_percent": c.creature.hp_percent,
                    "ac": c.creature.ac,
                    "conditions": c.active_conditions,
                    "is_alive": c.is_alive,
                }
                for cid, c in self.combatants.items()
            },
            "is_active": self.is_active,
        }
    
    def get_creature_summary(self, creature_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed summary of a specific creature"""
        combatant = self.get_combatant(creature_id)
        if not combatant:
            return None
        
        creature = combatant.creature
        position = self.battlefield.get_position(creature_id)
        
        return {
            "creature_id": creature_id,
            "name": creature.name,
            "type": creature.creature_type,
            "hp": f"{creature.current_hp}/{creature.max_hp}",
            "temp_hp": creature.temp_hp,
            "ac": creature.ac,
            "initiative": combatant.initiative,
            "position": position.to_tuple() if position else None,
            "position_feet": position.to_feet() if position else None,
            "conditions": combatant.active_conditions,
            "concentrating_on": combatant.concentrating_on,
            "movement_remaining": combatant.movement_remaining,
            "can_act": combatant.can_act,
            "has_action": not combatant.has_taken_action,
            "has_bonus_action": not combatant.has_taken_bonus_action,
            "has_reaction": not combatant.has_taken_reaction,
            "is_alive": combatant.is_alive,
        }




