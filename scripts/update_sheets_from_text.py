#!/usr/bin/env python3
"""
Update Google Sheets from Text File Imports
Reads character data from text files and updates Google Sheets with stats, feats, abilities
Does NOT update HP, XP, inventory, currency (those stay in sheets)
"""

import json
import sys
import argparse
import re
from pathlib import Path
from datetime import datetime

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("ERROR: Google API libraries not installed")

def load_credentials(credentials_path):
    """Load service account credentials"""
    with open(credentials_path, 'r') as f:
        creds_data = json.load(f)
    
    credentials = service_account.Credentials.from_service_account_info(
        creds_data,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    return credentials

def parse_character_text(text):
    """Parse character data from D&D Beyond text dump"""
    char_data = {}
    lines = [line.strip() for line in text.split('\n')]
    
    # Line 58: Name (index 57)
    if len(lines) > 57:
        name_line = lines[57].strip()
        if name_line and len(name_line) > 1:
            # Fix common typos/name variations
            name_mapping = {
                'Brovin': 'Brevin',
                'Halfling Rogue': 'Brevin'
            }
            char_data['name'] = name_mapping.get(name_line, name_line)
    
    # Line 59: Class Level (index 58)
    if len(lines) > 58:
        class_line = lines[58]
        match = re.search(r'(\w+)\s+(\d+)', class_line)
        if match:
            char_data['class'] = match.group(1)
            char_data['level'] = int(match.group(2))
    
    # Line 60: Race Background XP (index 59)
    if len(lines) > 59:
        race_line = lines[59]
        # Extract race (first word, usually capitalized)
        parts = race_line.split()
        if parts:
            # Common races
            common_races = ['Halfling', 'Goliath', 'Dwarf', 'Hill Dwarf', 'Human', 'Elf', 'Tiefling', 'Dragonborn']
            for race in common_races:
                if race in race_line:
                    char_data['race'] = race
                    break
    
    # Lines 61-72: Ability scores (indices 60-71)
    # Format: score on one line, modifier on next
    ability_order = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
    abilities = {}
    for i in range(6):
        score_idx = 60 + (i * 2)
        if score_idx < len(lines):
            score_line = lines[score_idx]
            match = re.search(r'^(\d{1,2})$', score_line)
            if match:
                score = int(match.group(1))
                if 8 <= score <= 20:
                    abilities[ability_order[i]] = score
    
    char_data['stats'] = abilities
    
    # AC: Look for pattern like "+5 15" or "+3 15" around line 103 (index 102)
    for i in range(100, min(110, len(lines))):
        line = lines[i]
        # Pattern: +X Y where Y is AC
        match = re.search(r'\+?\d+\s+(\d{2})', line)
        if match:
            ac = int(match.group(1))
            if 10 <= ac <= 30:
                char_data['ac'] = ac
                break
    
    # Speed: Look for "30 ft. (Walking)" around line 105
    for i in range(103, min(108, len(lines))):
        line = lines[i]
        match = re.search(r'(\d+)\s*ft\.', line)
        if match:
            char_data['speed'] = int(match.group(1))
            break
    
    # Features/Abilities: Look for feature descriptions
    features = []
    for i, line in enumerate(lines):
        # Look for common feature keywords
        if any(keyword in line.lower() for keyword in ['sneak attack', 'rage', 'second wind', 'action surge', 'divine domain', 'wails from the grave', 'reckless attack', 'danger sense']):
            if len(line) > 5 and len(line) < 100:
                features.append(line.strip())
    
    if features:
        char_data['features'] = features
    
    return char_data

def get_character_id_from_name(name, service, spreadsheet_id):
    """Find character_id from CSV_Characters by name"""
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Characters!A:B'
    ).execute()
    
    values = result.get('values', [])
    if len(values) < 2:
        return None
    
    # Name mapping for variations (text file name -> sheet name)
    name_mapping = {
        'brevin': 'halfling rogue',
        'brovin': 'halfling rogue',
        'eglath bearkiller': 'eglath bearkiller',
        'ergath': 'eglath bearkiller'
    }
    
    name_lower = name.lower()
    
    # Check direct match first
    for row in values[1:]:
        if len(row) >= 2:
            sheet_name = row[1].strip().lower()
            if sheet_name == name_lower:
                return row[0].strip()
    
    # Check name mappings
    if name_lower in name_mapping:
        mapped_name = name_mapping[name_lower]
        for row in values[1:]:
            if len(row) >= 2:
                sheet_name = row[1].strip().lower()
                if sheet_name == mapped_name:
                    return row[0].strip()
    
    return None

def update_character_in_sheet(service, spreadsheet_id, character_id, updates):
    """Update character row in CSV_Characters sheet"""
    # First, get the current data to find the row
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Characters!A:Z'
    ).execute()
    
    values = result.get('values', [])
    if len(values) < 2:
        print(f"ERROR: CSV_Characters sheet is empty or missing headers")
        return False
    
    headers = [h.strip().lower() for h in values[0]]
    
    # Find the row with this character_id
    row_index = None
    for i, row in enumerate(values[1:], start=2):  # Start at row 2 (1-indexed, +1 for header)
        if len(row) > 0 and row[0].strip().lower() == character_id.lower():
            row_index = i
            break
    
    if not row_index:
        print(f"ERROR: Character ID '{character_id}' not found in CSV_Characters")
        return False
    
    # Build update values
    updates_list = []
    for header, value in updates.items():
        if header in headers:
            col_index = headers.index(header)
            # Convert to A1 notation (A=0, B=1, etc.)
            col_letter = chr(65 + col_index)  # A=65
            range_name = f'CSV_Characters!{col_letter}{row_index}'
            updates_list.append({
                'range': range_name,
                'values': [[str(value)]]
            })
    
    if not updates_list:
        print(f"WARNING: No valid columns to update for {character_id}")
        return False
    
    # Batch update
    body = {
        'valueInputOption': 'RAW',
        'data': updates_list
    }
    
    try:
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()
        return True
    except HttpError as error:
        print(f"ERROR: Failed to update sheet: {error}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Update Google Sheets from text file imports')
    parser.add_argument('--credentials', default='C:\\DnD\\keys\\google_sheets_key.json', help='Credentials file path')
    parser.add_argument('--spreadsheet-id', default='1kCcauRdoetVuSv7O1uH6gb95psX0S7quy1uilVpc2dw', help='Spreadsheet ID')
    parser.add_argument('--text-dir', default='C:\\DnD\\Campaigns\\Phandelver\\players', help='Directory with text files')
    args = parser.parse_args()
    
    if not GOOGLE_AVAILABLE:
        print("ERROR: Google API libraries not installed")
        sys.exit(1)
    
    # Load credentials
    print(f"[update] Loading credentials...")
    credentials = load_credentials(args.credentials)
    service = build('sheets', 'v4', credentials=credentials)
    
    # Find text files
    text_dir = Path(args.text_dir)
    text_files = list(text_dir.glob("*.txt"))
    
    if not text_files:
        print(f"ERROR: No .txt files found in {text_dir}")
        sys.exit(1)
    
    print(f"[update] Found {len(text_files)} text file(s)")
    
    # Process each text file
    updated = 0
    for text_file in text_files:
        print(f"\n[update] Processing {text_file.name}...")
        
        # Read and parse text file
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        char_data = parse_character_text(text)
        
        if not char_data.get('name'):
            print(f"  WARNING: Could not parse character name from {text_file.name}")
            continue
        
        char_name = char_data['name']
        print(f"  Character: {char_name}")
        
        # Find character_id in sheet
        character_id = get_character_id_from_name(char_name, service, args.spreadsheet_id)
        if not character_id:
            print(f"  WARNING: Character '{char_name}' not found in CSV_Characters sheet")
            continue
        
        print(f"  Character ID: {character_id}")
        
        # Build updates (only stats/abilities, NOT HP/XP/inventory)
        updates = {}
        
        if 'class' in char_data and 'level' in char_data:
            updates['class_level'] = f"{char_data['class']} {char_data['level']}"
            updates['level'] = char_data['level']
        
        if 'ac' in char_data:
            updates['ac'] = char_data['ac']
        
        if 'speed' in char_data:
            updates['speed_override'] = char_data['speed']
        
        # Add features to condition_notes if present
        if 'features' in char_data and char_data['features']:
            features_text = "; ".join(char_data['features'][:5])  # Limit to first 5 features
            updates['condition_notes'] = features_text
        
        # Note: We're NOT updating HP, XP, inventory, currency - those stay in sheets
        
        if updates:
            print(f"  Updating: {', '.join(updates.keys())}")
            if update_character_in_sheet(service, args.spreadsheet_id, character_id, updates):
                print(f"  OK: Updated {char_name}")
                updated += 1
            else:
                print(f"  ERROR: Failed to update {char_name}")
        else:
            print(f"  WARNING: No updates to apply for {char_name}")
    
    print(f"\n[update] SUCCESS: Updated {updated} character(s)")
    return 0

if __name__ == "__main__":
    sys.exit(main())

