#!/usr/bin/env python3
"""
List all characters in the campaign
"""

import json
from pathlib import Path

def main():
    # Load paths config
    script_dir = Path(__file__).parent
    config_path = script_dir.parent / "config" / "paths.json"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    campaign_dir = Path(config['default_campaign_dir'])
    players_dir = campaign_dir / "players"
    
    if not players_dir.exists():
        print("No players directory found")
        return
    
    # Find all character JSON files
    char_files = list(players_dir.glob("*.json"))
    
    if not char_files:
        print("No character files found")
        return
    
    print(f"Characters in {players_dir}:")
    print()
    
    for char_file in sorted(char_files):
        with open(char_file, 'r', encoding='utf-8') as f:
            char = json.load(f)
        
        print(f"  {char.get('character_name', char_file.stem)}")
        print(f"    Level: {char.get('level', '?')}")
        print(f"    XP: {char.get('xp', 0)}/{char.get('xp_to_next', 0)} to next")
        print(f"    Class: {char.get('class', 'Unknown')}")
        print(f"    File: {char_file.name}")
        print()

if __name__ == "__main__":
    main()

