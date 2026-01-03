#!/usr/bin/env python3
"""
Import Character from Text Dump
Parses character sheet data from text dumps and converts to JSON format
"""

import json
import sys
import argparse
import re
from pathlib import Path
from datetime import datetime

def parse_character_text(text):
    """Parse character data from text dump"""
    char_data = {
        "name": "",
        "class": "",
        "level": 1,
        "race": "",
        "background": "",
        "alignment": "",
        "stats": {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10
        },
        "ac": 10,
        "hp": {
            "current": 0,
            "max": 0,
            "temp": 0
        },
        "proficiencies": {
            "armor": [],
            "weapons": [],
            "tools": [],
            "saving_throws": [],
            "skills": []
        },
        "xp": 0,
        "xp_to_next": 300,
        "spell_slots": {},
        "prepared_spells": [],
        "known_spells": [],
        "cantrips": [],
        "equipment": [],
        "features": [],
        "notes": ""
    }
    
    lines = text.split('\n')
    
    # Extract name (usually first line or after "Name:")
    for i, line in enumerate(lines):
        if re.match(r'^Name\s*[:]\s*(.+)$', line, re.IGNORECASE):
            char_data["name"] = re.match(r'^Name\s*[:]\s*(.+)$', line, re.IGNORECASE).group(1).strip()
            break
        elif i == 0 and line.strip() and not re.match(r'^(Class|Level|Race|AC|HP)', line, re.IGNORECASE):
            char_data["name"] = line.strip()
            break
    
    # Extract class and level
    for line in lines:
        # "Class: Fighter 4" or "Fighter Level 4" or "Level 4 Fighter"
        match = re.search(r'(?:Class|Level)\s*[:]?\s*(\w+)\s*(?:Level|Lvl)?\s*(\d+)', line, re.IGNORECASE)
        if match:
            char_data["class"] = match.group(1).strip()
            char_data["level"] = int(match.group(2))
            break
        match = re.search(r'(\w+)\s+(?:Level|Lvl)\s*(\d+)', line, re.IGNORECASE)
        if match:
            char_data["class"] = match.group(1).strip()
            char_data["level"] = int(match.group(2))
            break
    
    # Extract race
    for line in lines:
        match = re.search(r'Race\s*[:]\s*(.+?)(?:\s+Background|$)', line, re.IGNORECASE)
        if match:
            char_data["race"] = match.group(1).strip()
            break
    
    # Extract AC
    for line in lines:
        match = re.search(r'AC\s*[:]?\s*(\d+)', line, re.IGNORECASE)
        if match:
            char_data["ac"] = int(match.group(1))
            break
    
    # Extract HP
    for line in lines:
        # "HP: 45/45" or "Hit Points: 45" or "45/45 HP"
        match = re.search(r'(?:HP|Hit\s+Points?)\s*[:]?\s*(\d+)(?:/(\d+))?', line, re.IGNORECASE)
        if match:
            current = int(match.group(1))
            max_hp = int(match.group(2)) if match.group(2) else current
            char_data["hp"]["current"] = current
            char_data["hp"]["max"] = max_hp
            break
    
    # Extract ability scores
    ability_patterns = {
        "strength": r'STR(?:ength)?\s*[:]?\s*(\d+)',
        "dexterity": r'DEX(?:terity)?\s*[:]?\s*(\d+)',
        "constitution": r'CON(?:stitution)?\s*[:]?\s*(\d+)',
        "intelligence": r'INT(?:elligence)?\s*[:]?\s*(\d+)',
        "wisdom": r'WIS(?:dom)?\s*[:]?\s*(\d+)',
        "charisma": r'CHA(?:risma)?\s*[:]?\s*(\d+)'
    }
    
    for ability, pattern in ability_patterns.items():
        for line in lines:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                char_data["stats"][ability] = int(match.group(1))
                break
    
    # Extract XP
    for line in lines:
        match = re.search(r'XP\s*[:]?\s*(\d+)', line, re.IGNORECASE)
        if match:
            char_data["xp"] = int(match.group(1))
            break
    
    # Extract proficiencies (look for common patterns)
    for line in lines:
        if re.search(r'Proficiencies?', line, re.IGNORECASE):
            # Try to extract skill proficiencies
            skills = re.findall(r'(\w+\s+\w+)', line)
            for skill in skills:
                if any(s in skill.lower() for s in ['athletics', 'acrobatics', 'stealth', 'perception', 'investigation', 'insight', 'persuasion', 'deception', 'intimidation', 'performance']):
                    char_data["proficiencies"]["skills"].append(skill.strip())
    
    return char_data

def calculate_xp_to_next(level, current_xp):
    """Calculate XP needed for next level"""
    xp_table = {
        1: 300, 2: 900, 3: 2700, 4: 6500, 5: 14000,
        6: 23000, 7: 34000, 8: 48000, 9: 64000, 10: 85000,
        11: 100000, 12: 120000, 13: 140000, 14: 165000, 15: 195000,
        16: 225000, 17: 265000, 18: 305000, 19: 355000, 20: 0
    }
    
    if level >= 20:
        return 0
    
    next_level_xp = xp_table.get(level + 1, 0)
    if next_level_xp == 0:
        return 0
    
    return next_level_xp - current_xp

def main():
    parser = argparse.ArgumentParser(description='Import character from text dump')
    parser.add_argument('input_file', help='Path to text file with character data')
    parser.add_argument('--output-dir', default=None, help='Output directory (default: campaign characters folder)')
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)
    
    # Load paths config
    script_dir = Path(__file__).parent
    config_path = script_dir.parent / "config" / "paths.json"
    
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}")
        sys.exit(1)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        campaign_dir = Path(config['default_campaign_dir'])
        output_dir = campaign_dir / "characters"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read input text
    print(f"[import] Reading character data from: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Parse character data
    print("[import] Parsing character data...")
    char_data = parse_character_text(text)
    
    # Calculate XP to next level
    if char_data["xp"] > 0:
        char_data["xp_to_next"] = calculate_xp_to_next(char_data["level"], char_data["xp"])
    
    # Generate filename
    if char_data["name"]:
        filename = re.sub(r'[^a-zA-Z0-9_-]', '_', char_data["name"]).lower() + ".json"
    else:
        filename = f"character_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    output_path = output_dir / filename
    
    # Write JSON
    print(f"[import] Writing character data to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(char_data, f, indent=2, ensure_ascii=False)
    
    print(f"[import] SUCCESS: Character imported as {filename}")
    print(f"[import] Name: {char_data['name'] or 'Unknown'}")
    print(f"[import] Class: {char_data['class'] or 'Unknown'} Level {char_data['level']}")
    print(f"[import] AC: {char_data['ac']}, HP: {char_data['hp']['current']}/{char_data['hp']['max']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())



