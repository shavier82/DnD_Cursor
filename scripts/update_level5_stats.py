#!/usr/bin/env python3
"""
Import characters from D&D Beyond PDFs and update Google Sheets with level 5 stats
"""

import json
import sys
import subprocess
from pathlib import Path

# Character name mapping (PDF name -> Sheet character_id)
CHARACTER_MAPPING = {
    'Brevin': 'halfling_rogue',
    'Eglath Bearkiller': 'eglath_bearkiller',
    'Torgga Brawnanvil': 'torgga_brawnanvil',
    'Vandross Ephrates': 'vandross_ephrates',
    'Zephyr Sparkwhistle': 'zephyr_sparkwhistle'
}

# PDF URLs
PDF_URLS = [
    'https://www.dndbeyond.com/sheet-pdfs/ShavierT1982_158781310.pdf',
    'https://www.dndbeyond.com/sheet-pdfs/ShavierT1982_95127852.pdf',
    'https://www.dndbeyond.com/sheet-pdfs/ShavierT1982_157333848.pdf',
    'https://www.dndbeyond.com/sheet-pdfs/ShavierT1982_157455174.pdf',
    'https://www.dndbeyond.com/sheet-pdfs/ShavierT1982_157266647.pdf'
]

def load_config():
    """Load paths config"""
    config_path = Path(__file__).parent.parent / "config" / "paths.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def import_character_from_pdf(url, character_name=None):
    """Import character from PDF URL"""
    script_path = Path(__file__).parent / "import_character.py"
    
    cmd = ['python', str(script_path), '--url', url]
    if character_name:
        cmd.extend(['--name', character_name])
    
    print(f"\n[import] Importing character from {url}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: Import failed: {result.stderr}")
        return None
    
    print(result.stdout)
    
    # Find the character JSON file
    config = load_config()
    players_dir = Path(config['default_campaign_dir']) / "players"
    
    # The import script creates a JSON file based on character name
    # We need to find it
    if character_name:
        char_file = players_dir / f"{character_name.lower().replace(' ', '_')}.json"
        if char_file.exists():
            return char_file
    
    # If no name provided, try to find the most recent JSON file
    json_files = list(players_dir.glob("*.json"))
    if json_files:
        # Get the most recently modified
        char_file = max(json_files, key=lambda p: p.stat().st_mtime)
        return char_file
    
    return None

def update_sheets_from_json(char_json_path, character_id):
    """Update Google Sheets with character stats from JSON"""
    script_path = Path(__file__).parent / "update_sheets_data.py"
    
    # Load character JSON
    with open(char_json_path, 'r', encoding='utf-8') as f:
        char_data = json.load(f)
    
    print(f"\n[update] Updating {character_id} in Google Sheets...")
    print(f"  Level: {char_data.get('level', 'N/A')}")
    print(f"  AC: {char_data.get('ac', 'N/A')}")
    print(f"  HP Max: {char_data.get('hp', {}).get('max', 'N/A')}")
    
    # Update using sync_from_json command if available
    # Otherwise, we'll need to manually update each field
    # For now, let's use the sync command
    cmd = ['python', str(script_path), 'sync', str(char_json_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: Sync failed: {result.stderr}")
        # Fall back to manual updates
        return update_sheets_manual(char_data, character_id)
    
    print(result.stdout)
    return True

def update_sheets_manual(char_data, character_id):
    """Manually update sheets with character stats"""
    # This would require reading the CSV_Characters sheet structure
    # and updating specific columns
    # For now, we'll use the import script's merge functionality
    # and then sync
    print(f"[update] Manual update for {character_id} not yet implemented")
    print(f"  Please use the sync command or update sheets manually")
    return False

def main():
    print("=" * 60)
    print("Level 5 Character Stats Update")
    print("=" * 60)
    
    config = load_config()
    players_dir = Path(config['default_campaign_dir']) / "players"
    players_dir.mkdir(parents=True, exist_ok=True)
    
    imported_chars = {}
    
    # Step 1: Import all characters from PDFs
    print("\n[STEP 1] Importing characters from PDFs...")
    for i, url in enumerate(PDF_URLS, 1):
        print(f"\n--- Character {i}/{len(PDF_URLS)} ---")
        
        # Try to determine character name from mapping
        # We'll need to import first to get the name, then map it
        char_json = import_character_from_pdf(url)
        
        if char_json and char_json.exists():
            with open(char_json, 'r', encoding='utf-8') as f:
                char_data = json.load(f)
            
            # Try multiple possible name fields
            char_name = (char_data.get('name') or 
                        char_data.get('character_name') or 
                        char_data.get('characterName') or 
                        '')
            
            print(f"[import] Character name from JSON: {char_name}")
            print(f"[import] JSON keys: {list(char_data.keys())[:10]}...")
            
            # Find matching character_id
            character_id = None
            for mapped_name, mapped_id in CHARACTER_MAPPING.items():
                if char_name.lower() == mapped_name.lower():
                    character_id = mapped_id
                    break
            
            if character_id:
                imported_chars[character_id] = {
                    'json_path': char_json,
                    'name': char_name,
                    'data': char_data
                }
                print(f"[import] Mapped to character_id: {character_id}")
            else:
                print(f"[import] WARNING: Could not map '{char_name}' to a character_id")
                print(f"[import] Available mappings: {list(CHARACTER_MAPPING.keys())}")
                # Try to match by filename
                json_name = char_json.stem.lower().replace('_', ' ')
                for mapped_name, mapped_id in CHARACTER_MAPPING.items():
                    if json_name == mapped_name.lower() or mapped_name.lower() in json_name:
                        character_id = mapped_id
                        char_name = mapped_name
                        imported_chars[character_id] = {
                            'json_path': char_json,
                            'name': char_name,
                            'data': char_data
                        }
                        print(f"[import] Matched by filename to character_id: {character_id}")
                        break
        else:
            print(f"[import] ERROR: Failed to import character from {url}")
    
    # Step 2: Update Google Sheets
    print("\n" + "=" * 60)
    print("[STEP 2] Updating Google Sheets...")
    print("=" * 60)
    
    for character_id, char_info in imported_chars.items():
        print(f"\n--- Updating {character_id} ({char_info['name']}) ---")
        update_sheets_from_json(char_info['json_path'], character_id)
    
    print("\n" + "=" * 60)
    print("Update Complete!")
    print("=" * 60)
    print("\nImported characters:")
    for char_id, char_info in imported_chars.items():
        print(f"  - {char_info['name']} ({char_id})")
        print(f"    Level: {char_info['data'].get('level', 'N/A')}")
        print(f"    AC: {char_info['data'].get('ac', 'N/A')}")
        print(f"    HP Max: {char_info['data'].get('hp', {}).get('max', 'N/A')}")

if __name__ == '__main__':
    main()

