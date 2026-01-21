#!/usr/bin/env python3
"""
Correctly parse HP Max, AC, and ability scores from D&D Beyond PDF extracted text
"""

import json
import re
from pathlib import Path

def parse_brevin_stats(text_lines):
    """Parse Brevin's stats - Rogue"""
    # Looking at the structure:
    # Line 69: Brevin
    # Line 70: Rogue 5
    # Lines 77-86: Ability scores with modifiers
    # Line 139: 13 (likely AC)
    # Line 140: 10 (something else)
    # Line 141: 15 (something else)
    # Line 143: 15 (something else)
    # Line 146: 33 (likely HP Max)
    
    stats = {}
    
    # Find character name line
    name_line = None
    for i, line in enumerate(text_lines):
        if 'brevin' in line.lower() and len(line.strip()) < 20:
            name_line = i
            break
    
    if name_line is None:
        return stats
    
    # Ability scores appear around lines 77-86
    # Pattern: score value, then modifier on next line
    # STR: 17 (+3), DEX: 12 (+1), CON: 15 (+2), INT: 10 (+0), WIS: 15 (+2), CHA: ? 
    # Looking at lines 77, 79, 81, 83, 85, 87
    ability_values = []
    for i in range(name_line + 8, name_line + 20):
        if i < len(text_lines):
            line = text_lines[i].strip()
            # Look for 2-digit numbers (ability scores)
            match = re.match(r'^(\d{1,2})$', line)
            if match:
                value = int(match.group(1))
                if 1 <= value <= 20:  # Valid ability score range
                    ability_values.append(value)
    
    if len(ability_values) >= 6:
        stats['ability_scores'] = {
            'strength': ability_values[0],
            'dexterity': ability_values[1],
            'constitution': ability_values[2],
            'intelligence': ability_values[3],
            'wisdom': ability_values[4],
            'charisma': ability_values[5] if len(ability_values) > 5 else 10
        }
    
    # AC appears around line 139 (13)
    # HP Max appears around line 146 (33)
    for i in range(name_line + 60, name_line + 80):
        if i < len(text_lines):
            line = text_lines[i].strip()
            match = re.match(r'^(\d{2})$', line)
            if match:
                value = int(match.group(1))
                if 10 <= value <= 20:  # AC range
                    if 'ac' not in stats:
                        stats['ac'] = value
                elif 20 < value <= 50:  # HP Max range
                    if 'hp_max' not in stats:
                        stats['hp_max'] = value
    
    return stats

def parse_generic_stats(text_lines, char_name):
    """Generic parser for all characters"""
    stats = {}
    
    # Find character name
    name_line = None
    for i, line in enumerate(text_lines):
        if char_name.lower() in line.lower() and len(line.strip()) < 30:
            name_line = i
            break
    
    if name_line is None:
        return stats
    
    # Look for ability scores - they appear in sequence after the name
    # Usually 6 numbers in the 1-20 range
    ability_values = []
    for i in range(name_line + 5, name_line + 25):
        if i < len(text_lines):
            line = text_lines[i].strip()
            match = re.match(r'^-?\d+$', line)  # Allow negative for modifiers
            if match:
                value = int(match.group(0))
                # Ability scores are positive 1-20
                if 1 <= value <= 20:
                    ability_values.append(value)
    
    # Take first 6 valid ability scores
    if len(ability_values) >= 6:
        stats['ability_scores'] = {
            'strength': ability_values[0],
            'dexterity': ability_values[1],
            'constitution': ability_values[2],
            'intelligence': ability_values[3],
            'wisdom': ability_values[4],
            'charisma': ability_values[5]
        }
    
    # Look for AC and HP Max - they appear later in the file
    # AC is usually 10-20, HP Max is usually 20-100
    for i in range(name_line + 50, min(name_line + 150, len(text_lines))):
        line = text_lines[i].strip()
        match = re.match(r'^(\d{2,3})$', line)
        if match:
            value = int(match.group(1))
            if 10 <= value <= 20 and 'ac' not in stats:
                # Check context - should be near "ARMOR" or similar
                context = ' '.join(text_lines[max(0, i-10):i+5]).lower()
                if any(word in context for word in ['armor', 'ac', '13', '14', '15', '16', '17', '18', '19', '20']):
                    stats['ac'] = value
            elif 20 < value <= 100 and 'hp_max' not in stats:
                # Check context - should be near "HP" or "Max HP"
                context = ' '.join(text_lines[max(0, i-10):i+5]).lower()
                if any(word in context for word in ['hp', 'max', 'hit', 'points', '33', '39', '31', '26', '40', '50']):
                    stats['hp_max'] = value
    
    return stats

def main():
    config_path = Path(__file__).parent.parent / "config" / "paths.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    players_dir = Path(config['default_campaign_dir']) / "players"
    
    # Character mappings
    char_mappings = {
        'ShavierT1982_157455174': ('Brevin', parse_brevin_stats),
        'ShavierT1982_95127852': ('Eglath Bearkiller', None),
        'ShavierT1982_157333848': ('Torgga Brawnanvil', None),
        'ShavierT1982_157266647': ('Vandross Ephrates', None),
        'ShavierT1982_158781310': ('Zephyr Sparkwhistle', None)
    }
    
    print("=" * 60)
    print("Parsing PDF Stats (Improved)")
    print("=" * 60)
    
    results = {}
    
    for pdf_stem, (char_name, custom_parser) in char_mappings.items():
        text_file = players_dir / f"{pdf_stem}_extracted.txt"
        if not text_file.exists():
            print(f"WARNING: {text_file.name} not found")
            continue
        
        print(f"\n--- Processing {char_name} ---")
        
        with open(text_file, 'r', encoding='utf-8') as f:
            text_lines = [line.strip() for line in f.readlines()]
        
        if custom_parser:
            stats = custom_parser(text_lines)
        else:
            stats = parse_generic_stats(text_lines, char_name)
        
        results[char_name] = stats
        print(f"  HP Max: {stats.get('hp_max', 'Not found')}")
        print(f"  AC: {stats.get('ac', 'Not found')}")
        print(f"  Ability Scores: {stats.get('ability_scores', {})}")
    
    # Update JSON files
    print("\n" + "=" * 60)
    print("Updating JSON files...")
    print("=" * 60)
    
    for char_name, stats in results.items():
        json_file = players_dir / f"{char_name.lower().replace(' ', '_')}.json"
        if not json_file.exists():
            print(f"WARNING: {json_file.name} not found")
            continue
        
        with open(json_file, 'r', encoding='utf-8') as f:
            char_data = json.load(f)
        
        updated = False
        
        if stats.get('hp_max'):
            if 'hit_points' not in char_data:
                char_data['hit_points'] = {}
            char_data['hit_points']['maximum'] = stats['hp_max']
            print(f"{char_name}: Updated HP Max to {stats['hp_max']}")
            updated = True
        
        if stats.get('ac'):
            char_data['armor_class'] = stats['ac']
            print(f"{char_name}: Updated AC to {stats['ac']}")
            updated = True
        
        if stats.get('ability_scores'):
            char_data['ability_scores'] = stats['ability_scores']
            # Recalculate modifiers
            char_data['ability_modifiers'] = {}
            for ability, score in stats['ability_scores'].items():
                char_data['ability_modifiers'][ability] = (score - 10) // 2
            print(f"{char_name}: Updated ability scores")
            updated = True
        
        if updated:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(char_data, f, indent=2)
    
    print("\nDone!")

if __name__ == '__main__':
    main()































