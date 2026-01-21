"""Real-time sync helpers for combat engine"""

import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from .obsidian_sync import (
    sync_hp_to_obsidian,
    sync_spell_slots_to_obsidian,
    sync_resource_to_obsidian,
    sync_condition_to_obsidian,
    remove_condition_from_obsidian,
)
from models.creature import Creature, CreatureType


def sync_player_hp(creature: Creature) -> bool:
    """Sync player HP to Obsidian in real-time"""
    if creature.creature_type == CreatureType.PLAYER:
        return sync_hp_to_obsidian(
            creature.name,
            creature.current_hp,
            creature.max_hp
        )
    return False


def use_spell_slot(creature: Creature, level: int) -> bool:
    """Use a spell slot and sync to Obsidian in real-time"""
    if creature.creature_type != CreatureType.PLAYER:
        return False
    
    # Check if slot available
    current_slots = creature.spell_slots.get(level, 0)
    if current_slots <= 0:
        return False
    
    # Use the slot
    creature.spell_slots[level] = current_slots - 1
    
    # Sync to Obsidian
    return sync_spell_slots_to_obsidian(
        creature.name,
        level,
        creature.spell_slots[level]
    )


def use_resource(creature: Creature, resource_name: str, current: int, maximum: int, amount: int = 1) -> bool:
    """Use a class resource (Rage, Ki, Superiority Dice, etc.) and sync to Obsidian in real-time
    
    Args:
        creature: The creature using the resource
        resource_name: Name of the resource (e.g., 'rage', 'ki', 'superiority_dice')
        current: Current value after use
        maximum: Maximum value
        amount: Amount used (default 1)
    
    Returns:
        True if synced successfully, False otherwise
    """
    if creature.creature_type != CreatureType.PLAYER:
        return False
    
    # Sync to Obsidian
    return sync_resource_to_obsidian(creature.name, resource_name, current, maximum)


def add_condition_sync(creature: Creature, condition: str, duration: str = "") -> bool:
    """Add a condition and sync to Obsidian in real-time"""
    if creature.creature_type == CreatureType.PLAYER:
        return sync_condition_to_obsidian(creature.name, condition, duration)
    return False


def remove_condition_sync(creature: Creature, condition: str) -> bool:
    """Remove a condition and sync to Obsidian in real-time"""
    if creature.creature_type == CreatureType.PLAYER:
        return remove_condition_from_obsidian(creature.name, condition)
    return False
