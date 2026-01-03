#!/usr/bin/env python3
"""
Calculate Passive Perception for characters
Passive Perception = 10 + Wisdom modifier + proficiency bonus (if proficient)
"""

import json
import sys
from pathlib import Path

def calculate_passive_perception(character_data):
    """Calculate passive Perception for a character"""
    wis = character_data.get('stats', {}).get('wisdom', 10)
    wis_mod = (wis - 10) // 2
    
    # Check if proficient in Perception
    skills = character_data.get('proficiencies', {}).get('skills', [])
    # Handle both list and string formats
    if isinstance(skills, list):
        proficient = 'Perception' in skills
    else:
        proficient = False
    
    # Calculate proficiency bonus (level 1-4 = +2, 5-8 = +3, etc.)
    level = character_data.get('level', 1)
    if level <= 4:
        prof_bonus = 2
    elif level <= 8:
        prof_bonus = 3
    elif level <= 12:
        prof_bonus = 4
    elif level <= 16:
        prof_bonus = 5
    else:
        prof_bonus = 6
    
    passive = 10 + wis_mod
    if proficient:
        passive += prof_bonus
    
    return passive

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Calculate passive Perception')
    parser.add_argument('character_file', help='Path to character JSON file')
    args = parser.parse_args()
    
    with open(args.character_file, 'r', encoding='utf-8-sig') as f:
        char = json.load(f)
    
    passive = calculate_passive_perception(char)
    name = char.get('name', 'Unknown')
    
    print(f"{name}: Passive Perception {passive}")
    return passive

if __name__ == "__main__":
    main()

