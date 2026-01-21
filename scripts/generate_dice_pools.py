#!/usr/bin/env python3
"""
Generate Dice Pools for Combat Encounters
Creates pre-rolled hit and damage pools for all enemies at encounter start.
This dramatically speeds up combat by eliminating dice rolling during enemy turns.
"""

import json
import random
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any

def generate_pool(size: int, dice_type: int, modifier: int) -> List[int]:
    """Generate a pool of dice rolls"""
    return [random.randint(1, dice_type) + modifier for _ in range(size)]

def generate_dice_pools_for_enemy(
    enemy_name: str,
    attack_modifier: int,
    damage_dice: str,  # e.g., "1d8", "2d6", "1d6+1d4"
    damage_modifier: int = 0,
    pool_size: int = 25
) -> Dict[str, Any]:
    """
    Generate hit and damage pools for an enemy.
    
    Args:
        enemy_name: Name of the enemy
        attack_modifier: Attack modifier (1d20 + this)
        damage_dice: Damage dice string (e.g., "1d8", "2d6", "1d6+1d4")
        damage_modifier: Damage modifier (added to each damage roll)
        pool_size: Number of rolls to generate (default 25)
    
    Returns:
        Dictionary with hit_pool, damage_pool, and metadata
    """
    # Generate hit pool (1d20 + attack_modifier)
    hit_pool = generate_pool(pool_size, 20, attack_modifier)
    
    # Parse damage dice string
    damage_rolls = []
    if '+' in damage_dice:
        # Multiple dice types (e.g., "1d6+1d4")
        parts = damage_dice.split('+')
        for part in parts:
            part = part.strip()
            if 'd' in part:
                count, size = part.split('d')
                count = int(count) if count else 1
                size = int(size)
                for _ in range(count):
                    damage_rolls.append((size,))
            else:
                # Static modifier in dice string (rare)
                damage_modifier += int(part)
    else:
        # Single die type (e.g., "1d8", "2d6")
        if 'd' in damage_dice:
            count, size = damage_dice.split('d')
            count = int(count) if count else 1
            size = int(size)
            for _ in range(count):
                damage_rolls.append((size,))
        else:
            # Static damage (rare)
            damage_rolls = [(0, int(damage_dice))]
    
    # Generate damage pool
    damage_pool = []
    for _ in range(pool_size):
        total_damage = damage_modifier
        for die_size in damage_rolls:
            total_damage += random.randint(1, die_size)
        damage_pool.append(total_damage)
    
    return {
        "hit_pool": hit_pool,
        "damage_pool": damage_pool,
        "hit_index": 0,
        "damage_index": 0,
        "attack_modifier": attack_modifier,
        "damage_formula": damage_dice,
        "damage_modifier": damage_modifier
    }

def generate_dice_pools_from_state(
    state_file: str,
    enemies: Dict[str, Dict[str, Any]],
    pool_size: int = 25
) -> bool:
    """
    Generate dice pools for all enemies and update state file.
    
    Args:
        state_file: Path to CURRENT_STATE.json
        enemies: Dictionary mapping enemy names to their stats
                  Format: {
                    "Enemy Name": {
                      "attack_modifier": 4,
                      "damage_dice": "1d8",
                      "damage_modifier": 2
                    }
                  }
        pool_size: Number of rolls to generate per pool (default 25)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read current state
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        # Initialize dice_pools if it doesn't exist
        if 'combat' not in state:
            state['combat'] = {}
        if 'dice_pools' not in state['combat']:
            state['combat']['dice_pools'] = {}
        
        # Generate pools for each enemy
        for enemy_name, enemy_stats in enemies.items():
            pool_data = generate_dice_pools_for_enemy(
                enemy_name=enemy_name,
                attack_modifier=enemy_stats.get('attack_modifier', 0),
                damage_dice=enemy_stats.get('damage_dice', '1d6'),
                damage_modifier=enemy_stats.get('damage_modifier', 0),
                pool_size=pool_size
            )
            state['combat']['dice_pools'][enemy_name] = pool_data
        
        # Write updated state
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        print(f"OK: Generated dice pools for {len(enemies)} enemies")
        return True
    
    except FileNotFoundError:
        print(f"ERROR: State file not found: {state_file}")
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in state file: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Failed to generate dice pools: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Generate dice pools for combat encounters'
    )
    parser.add_argument(
        'state_file',
        help='Path to CURRENT_STATE.json file'
    )
    parser.add_argument(
        '--enemy',
        action='append',
        nargs=4,
        metavar=('NAME', 'ATTACK_MOD', 'DAMAGE_DICE', 'DAMAGE_MOD'),
        help='Enemy definition: name, attack modifier, damage dice (e.g., 1d8), damage modifier. Can be specified multiple times.'
    )
    parser.add_argument(
        '--pool-size',
        type=int,
        default=25,
        help='Number of rolls per pool (default: 25)'
    )
    
    args = parser.parse_args()
    
    if not args.enemy:
        print("ERROR: At least one --enemy must be specified")
        print("Usage: python generate_dice_pools.py <state_file> --enemy NAME ATTACK_MOD DAMAGE_DICE DAMAGE_MOD [--enemy ...]")
        sys.exit(1)
    
    # Parse enemy definitions
    enemies = {}
    for enemy_def in args.enemy:
        name = enemy_def[0]
        try:
            attack_mod = int(enemy_def[1])
            damage_dice = enemy_def[2]
            damage_mod = int(enemy_def[3])
            
            enemies[name] = {
                'attack_modifier': attack_mod,
                'damage_dice': damage_dice,
                'damage_modifier': damage_mod
            }
        except (ValueError, IndexError) as e:
            print(f"ERROR: Invalid enemy definition: {enemy_def} - {e}")
            sys.exit(1)
    
    # Generate pools
    success = generate_dice_pools_from_state(
        args.state_file,
        enemies,
        pool_size=args.pool_size
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
































