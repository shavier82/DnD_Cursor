#!/usr/bin/env python3
"""Read current XP values from Google Sheets"""

import json
import sys
from pathlib import Path

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("ERROR: Google API libraries not installed")
    sys.exit(1)

def load_credentials(credentials_path):
    """Load service account credentials"""
    with open(credentials_path, 'r') as f:
        creds_data = json.load(f)
    
    credentials = service_account.Credentials.from_service_account_info(
        creds_data,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    return credentials

def get_character_id_from_name(name, service, spreadsheet_id):
    """Get character_id from character name"""
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Characters!A:Z'
    ).execute()
    
    values = result.get('values', [])
    if len(values) < 2:
        return None
    
    headers = [h.strip().lower() for h in values[0]]
    name_col = headers.index('character_name') if 'character_name' in headers else None
    id_col = headers.index('character_id') if 'character_id' in headers else None
    
    if name_col is None or id_col is None:
        return None
    
    for row in values[1:]:
        if len(row) > name_col and row[name_col].strip().lower() == name.lower():
            if len(row) > id_col:
                return row[id_col].strip()
    
    return None

def get_current_xp(service, spreadsheet_id, character_id):
    """Get current XP for a character"""
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='CSV_Characters!A:Z'
    ).execute()
    
    values = result.get('values', [])
    if len(values) < 2:
        return None
    
    headers = [h.strip().lower() for h in values[0]]
    id_col = headers.index('character_id') if 'character_id' in headers else None
    xp_col = headers.index('xp') if 'xp' in headers else None
    
    if id_col is None or xp_col is None:
        return None
    
    for row in values[1:]:
        if len(row) > id_col and row[id_col].strip().lower() == character_id.lower():
            if len(row) > xp_col and row[xp_col].strip():
                try:
                    return int(row[xp_col].strip().replace(',', ''))
                except ValueError:
                    return 0
    
    return None

def main():
    credentials_path = r'C:\DnD\keys\google_sheets_key.json'
    spreadsheet_id = '1kCcauRdoetVuSv7O1uH6gb95psX0S7quy1uilVpc2dw'
    
    credentials = load_credentials(credentials_path)
    service = build('sheets', 'v4', credentials=credentials)
    
    characters = {
        'Brevin': 'halfling_rogue',
        'Eglath Bearkiller': 'eglath_bearkiller',
        'Torgga Brawnanvil': 'torgga_brawnanvil',
        'Vandross Ephrates': 'vandross_ephrates'
    }
    
    for name, char_id in characters.items():
        xp = get_current_xp(service, spreadsheet_id, char_id)
        if xp is not None:
            print(f"{name}: {xp} XP")
        else:
            print(f"{name}: Could not read XP")

if __name__ == '__main__':
    main()

