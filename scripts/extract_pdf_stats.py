#!/usr/bin/env python3
"""
Extract HP Max and AC from PDF extracted text files
"""

import json
import re
from pathlib import Path

def extract_stats_from_text(text_file):
    """Extract HP Max, AC, and ability scores from extracted text"""
    with open(text_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]
    
    stats = {
        'hp_max': None,
        'ac': None,
        'ability_scores': {}
    }
    
    # Look for HP Max - usually appears after "Max HP" label
    for i, line in enumerate(lines):
        if 'max hp' in line.lower() and i + 1 < len(lines):
            # Next line or nearby should have the value
            for offset in [1, 2, 3]:
                if i + offset < len(lines):
                    value = lines[i + offset].strip()
                    # Try to extract number
                    match = re.search(r'(\d+)', value)
                    if match:
                        stats['hp_max'] = int(match.group(1))
                        break
    
    # Look for AC - can appear in various places
    # Pattern 1: After "ARMOR" label
    for i, line in enumerate(lines):
        if line.strip().upper() == 'ARMOR' and i + 1 < len(lines):
            # Look for number in next few lines
            for offset in range(1, 10):
                if i + offset < len(lines):
                    value = lines[i + offset].strip()
                    match = re.search(r'(\d+)', value)
                    if match and 10 <= int(match.group(1)) <= 30:  # Reasonable AC range
                        stats['ac'] = int(match.group(1))
                        break
            if stats['ac']:
                break
    
    # Pattern 2: Look for standalone numbers that could be AC (10-30 range)
    if not stats['ac']:
        for i, line in enumerate(lines):
            # Look for lines with just a number in reasonable AC range
            match = re.match(r'^(\d{2})$', line.strip())
            if match:
                value = int(match.group(1))
                if 10 <= value <= 30:
                    # Check context - should be near armor/defense related text
                    context = ' '.join(lines[max(0, i-5):i+5]).lower()
                    if any(word in context for word in ['armor', 'ac', 'defense', 'hit points', 'hp']):
                        stats['ac'] = value
                        break
    
    # Extract ability scores - look for patterns like "STR 17" or "17 +3"
    abilities = {
        'STR': 'strength',
        'DEX': 'dexterity', 
        'CON': 'constitution',
        'INT': 'intelligence',
        'WIS': 'wisdom',
        'CHA': 'charisma'
    }
    
    for i, line in enumerate(lines):
        for abbr, full_name in abilities.items():
            # Pattern: "STR 17" or "17 +3" after STR label
            if abbr in line.upper():
                # Look for number in this line or next
                match = re.search(r'(\d{1,2})', line)
                if match:
                    score = int(match.group(1))
                    if 1 <= score <= 30:  # Valid ability score range
                        stats['ability_scores'][full_name] = score
                # Also check next line
                elif i + 1 < len(lines):
                    match = re.search(r'(\d{1,2})', lines[i + 1])
                    if match:
                        score = int(match.group(1))
                        if 1 <= score <= 30:
                            stats['ability_scores'][full_name] = score
    
    return stats

def main():
    config_path = Path(__file__).parent.parent / "config" / "paths.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    players_dir = Path(config['default_campaign_dir']) / "players"
    
    # Find all extracted text files
    text_files = list(players_dir.glob("*_extracted.txt"))
    
    print("=" * 60)
    print("Extracting Stats from PDFs")
    print("=" * 60)
    
    results = {}
    
    for text_file in text_files:
        print(f"\n--- Processing {text_file.name} ---")
        stats = extract_stats_from_text(text_file)
        
        # Try to match to character
        pdf_name = text_file.name.replace('_extracted.txt', '')
        
        # Find corresponding JSON file
        json_files = list(players_dir.glob("*.json"))
        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                char_data = json.load(f)
            if char_data.get('source_pdf') == pdf_name + '.pdf':
                char_name = char_data.get('character_name', 'Unknown')
                results[char_name] = stats
                print(f"Character: {char_name}")
                print(f"  HP Max: {stats['hp_max']}")
                print(f"  AC: {stats['ac']}")
                print(f"  Ability Scores: {stats['ability_scores']}")
                break
    
    # Update JSON files
    print("\n" + "=" * 60)
    print("Updating JSON files...")
    print("=" * 60)
    
    for char_name, stats in results.items():
        json_file = players_dir / f"{char_name.lower().replace(' ', '_')}.json"
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                char_data = json.load(f)
            
            # Update stats
            if stats['hp_max']:
                if 'hit_points' not in char_data:
                    char_data['hit_points'] = {}
                char_data['hit_points']['maximum'] = stats['hp_max']
                print(f"{char_name}: Updated HP Max to {stats['hp_max']}")
            
            if stats['ac']:
                char_data['armor_class'] = stats['ac']
                print(f"{char_name}: Updated AC to {stats['ac']}")
            
            if stats['ability_scores']:
                if 'ability_scores' not in char_data:
                    char_data['ability_scores'] = {}
                char_data['ability_scores'].update(stats['ability_scores'])
                # Recalculate modifiers
                if 'ability_modifiers' not in char_data:
                    char_data['ability_modifiers'] = {}
                for ability, score in stats['ability_scores'].items():
                    char_data['ability_modifiers'][ability] = (score - 10) // 2
                print(f"{char_name}: Updated ability scores")
            
            # Save updated JSON
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(char_data, f, indent=2)
    
    print("\nDone!")

if __name__ == '__main__':
    main()































