#!/usr/bin/env python3
"""
Sync Character Data from Google Sheets
Reads character data from Google Sheets CSV-style sheets and updates local JSON files
Uses service account credentials for authentication
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("ERROR: Google API libraries not installed. Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")

def load_credentials(credentials_path):
    """Load service account credentials from JSON file"""
    if not Path(credentials_path).exists():
        raise FileNotFoundError(f"Credentials file not found: {credentials_path}")
    
    with open(credentials_path, 'r') as f:
        creds_data = json.load(f)
    
    credentials = service_account.Credentials.from_service_account_info(
        creds_data,
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )
    return credentials

def get_sheet_data(service, spreadsheet_id, range_name):
    """Read data from Google Sheet"""
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        return result.get('values', [])
    except HttpError as error:
        print(f"ERROR: An error occurred reading {range_name}: {error}")
        return None

def parse_csv_sheet(sheet_data):
    """Parse CSV-style sheet into dict with headers as keys"""
    if not sheet_data or len(sheet_data) < 2:
        return []
    
    headers = [h.strip().lower() for h in sheet_data[0]]
    rows = []
    
    for row_data in sheet_data[1:]:
        row_dict = {}
        for i, header in enumerate(headers):
            if i < len(row_data):
                row_dict[header] = row_data[i].strip() if row_data[i] else ""
            else:
                row_dict[header] = ""
        rows.append(row_dict)
    
    return rows

def sync_characters_from_sheets(service, spreadsheet_id, character_ids=None):
    """Sync all character data from multiple CSV sheets"""
    
    # Read CSV_Characters (main character data)
    print("[sync] Reading CSV_Characters...")
    chars_data = get_sheet_data(service, spreadsheet_id, "CSV_Characters!A:Z")
    if not chars_data:
        print("ERROR: Could not read CSV_Characters")
        return None
    
    characters = parse_csv_sheet(chars_data)
    print(f"[sync] Found {len(characters)} character(s)")
    
    # Filter by character_ids if provided
    if character_ids:
        characters = [c for c in characters if c.get('character_id', '').lower() in [cid.lower() for cid in character_ids]]
        print(f"[sync] Filtered to {len(characters)} character(s)")
    
    # Read supporting data
    print("[sync] Reading CSV_Resources...")
    resources_data = get_sheet_data(service, spreadsheet_id, "CSV_Resources!A:Z")
    resources = parse_csv_sheet(resources_data) if resources_data else []
    
    print("[sync] Reading CSV_SpellSlots...")
    slots_data = get_sheet_data(service, spreadsheet_id, "CSV_SpellSlots!A:Z")
    slots = parse_csv_sheet(slots_data) if slots_data else []
    
    print("[sync] Reading CSV_Inventory...")
    inventory_data = get_sheet_data(service, spreadsheet_id, "CSV_Inventory!A:Z")
    inventory = parse_csv_sheet(inventory_data) if inventory_data else []
    
    print("[sync] Reading CSV_Currency...")
    currency_data = get_sheet_data(service, spreadsheet_id, "CSV_Currency!A:Z")
    currency = parse_csv_sheet(currency_data) if currency_data else []
    
    # Group supporting data by character_id
    resources_by_char = defaultdict(list)
    for r in resources:
        char_id = r.get('character_id', '').lower()
        if char_id:
            resources_by_char[char_id].append(r)
    
    slots_by_char = defaultdict(dict)
    for s in slots:
        char_id = s.get('character_id', '').lower()
        if char_id:
            slot_level = s.get('slot_level', '').strip()
            slots_by_char[char_id][slot_level] = {
                'max': int(s.get('max', 0) or 0),
                'remaining': int(s.get('remaining', 0) or 0)
            }
    
    inventory_by_char = defaultdict(list)
    for inv in inventory:
        char_id = inv.get('character_id', '').lower()
        if char_id:
            # The 'now ' column (with trailing space) contains the item name
            item_name = inv.get('now ', '').strip()
            if not item_name:
                # Fallback to 'name' if 'now ' is empty
                item_name = inv.get('name', '').strip()
            if item_name and item_name != inv.get('name', '').strip():  # Don't use character name as item name
                inventory_by_char[char_id].append({
                    'name': item_name,
                    'quantity': int(inv.get('quantity', 1) or 1),
                    'weight_lbs': float(inv.get('weight_lbs', 0) or 0),
                    'type': inv.get('type', '').strip(),
                    'equipped': inv.get('equipped', '').strip().lower() == 'yes',
                    'notes': inv.get('notes', '').strip()
                })
    
    currency_by_char = {}
    for curr in currency:
        char_id = curr.get('character_id', '').lower()
        if char_id:
            currency_by_char[char_id] = {
                'cp': int(curr.get('cp', 0) or 0),
                'sp': int(curr.get('sp', 0) or 0),
                'ep': int(curr.get('ep', 0) or 0),
                'gp': int(curr.get('gp', 0) or 0),
                'pp': int(curr.get('pp', 0) or 0)
            }
    
    # Build character JSON objects
    synced_characters = []
    for char in characters:
        char_id = char.get('character_id', '').lower()
        char_name = char.get('name', '').strip()
        
        if not char_name:
            print(f"[sync] WARNING: Skipping character with no name (ID: {char_id})")
            continue
        
        # Parse class and level
        class_level = char.get('class_level', '').strip()
        level_str = char.get('level', '').strip()
        char_class = ""
        level = 1
        
        if class_level:
            parts = class_level.split()
            if len(parts) >= 2:
                char_class = parts[0]
                try:
                    level = int(parts[1])
                except ValueError:
                    level = int(level_str) if level_str else 1
            else:
                char_class = class_level
                level = int(level_str) if level_str else 1
        
        # Build character data
        char_data = {
            "name": char_name,
            "class": char_class,
            "level": level,
            "race": "",  # Not in CSV_Characters, would need separate source
            "background": "",
            "alignment": "",
            "stats": {
                "strength": 10,  # Not in CSV_Characters
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            },
            "ac": int(char.get('ac', 10) or 10),
            "hp": {
                "current": int(char.get('hp_current', 0) or 0),
                "max": int(char.get('hp_max', 0) or 0),
                "temp": 0
            },
            "proficiencies": {
                "armor": [],
                "weapons": [],
                "tools": [],
                "saving_throws": [],
                "skills": []
            },
            "xp": int(char.get('xp', 0).replace(',', '') if char.get('xp') else 0),
            "xp_to_next": 0,  # Will calculate
            "spell_slots": slots_by_char.get(char_id, {}),
            "prepared_spells": [],
            "known_spells": [],
            "cantrips": [],
            "equipment": inventory_by_char.get(char_id, []),
            "features": [],
            "inventory": inventory_by_char.get(char_id, []),
            "currency": currency_by_char.get(char_id, {"cp": 0, "sp": 0, "ep": 0, "gp": 0, "pp": 0}),
            "resources": {},
            "notes": char.get('condition_notes', '').strip(),
            "last_synced": datetime.now().isoformat()
        }
        
        # Add resources
        for res in resources_by_char.get(char_id, []):
            res_name = res.get('resource', '').strip()
            if res_name:
                char_data['resources'][res_name] = {
                    'max': int(res.get('max', 0) or 0),
                    'remaining': int(res.get('remaining', 0) or 0),
                    'active': res.get('active', '').strip().lower() == 'yes'
                }
        
        # Calculate XP to next level
        def calculate_xp_to_next(level, current_xp):
            xp_table = {
                1: 300, 2: 900, 3: 2700, 4: 6500, 5: 14000,
                6: 23000, 7: 34000, 8: 48000, 9: 64000, 10: 85000,
                11: 100000, 12: 120000, 13: 140000, 14: 165000, 15: 195000,
                16: 225000, 17: 265000, 18: 305000, 19: 355000, 20: 0
            }
            if level >= 20:
                return 0
            next_level_xp = xp_table.get(level + 1, 0)
            return max(0, next_level_xp - current_xp) if next_level_xp > 0 else 0
        
        char_data['xp_to_next'] = calculate_xp_to_next(char_data['level'], char_data['xp'])
        
        synced_characters.append((char_id, char_data))
    
    return synced_characters

def main():
    parser = argparse.ArgumentParser(description='Sync character data from Google Sheets')
    parser.add_argument('--credentials', default='C:\\DnD\\keys\\google_sheets_key.json', help='Path to Google service account credentials JSON file')
    parser.add_argument('--spreadsheet-id', default='1kCcauRdoetVuSv7O1uH6gb95psX0S7quy1uilVpc2dw', help='Google Sheets spreadsheet ID')
    parser.add_argument('--characters', nargs='+', help='Character IDs to sync (if not provided, syncs all)')
    parser.add_argument('--output-dir', default=None, help='Output directory (default: campaign characters folder)')
    args = parser.parse_args()
    
    if not GOOGLE_AVAILABLE:
        print("ERROR: Google API libraries not installed")
        print("Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
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
    
    # Load credentials and build service
    print(f"[sync] Loading credentials from: {args.credentials}")
    credentials = load_credentials(args.credentials)
    service = build('sheets', 'v4', credentials=credentials)
    
    # Sync characters
    print(f"[sync] Syncing from spreadsheet: {args.spreadsheet_id}")
    synced = sync_characters_from_sheets(service, args.spreadsheet_id, args.characters)
    
    if not synced:
        print("ERROR: No characters synced")
        sys.exit(1)
    
    # Write JSON files
    synced_count = 0
    for char_id, char_data in synced:
        # Generate filename from character name
        filename = char_data['name'].lower().replace(' ', '_') + ".json"
        output_path = output_dir / filename
        
        print(f"[sync] Writing {filename}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(char_data, f, indent=2, ensure_ascii=False)
        
        print(f"[sync] OK {char_data['name']}: Level {char_data['level']} {char_data['class']}, AC {char_data['ac']}, HP {char_data['hp']['current']}/{char_data['hp']['max']}")
        if char_data.get('resources'):
            res_str = ", ".join([f"{k}: {v['remaining']}/{v['max']}" for k, v in char_data['resources'].items()])
            print(f"      Resources: {res_str}")
        synced_count += 1
    
    print(f"[sync] SUCCESS: Synced {synced_count} character(s) to {output_dir}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
