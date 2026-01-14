"""Google Sheets reader for character data"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
from collections import defaultdict

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class SheetsReader:
    """Read character data from Google Sheets"""
    
    def __init__(self, credentials_path: str, spreadsheet_id: str):
        """Initialize sheets reader
        
        Args:
            credentials_path: Path to Google service account JSON
            spreadsheet_id: Google Sheets spreadsheet ID
        """
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.service = None
        
        if not GOOGLE_AVAILABLE:
            raise ImportError("Google API libraries not installed. Run: pip install google-auth google-api-python-client")
    
    def connect(self):
        """Connect to Google Sheets API"""
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        self.service = build('sheets', 'v4', credentials=credentials)
    
    def get_sheet_data(self, range_name: str) -> List[List[str]]:
        """Read data from a sheet range"""
        if not self.service:
            self.connect()
        
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range_name
        ).execute()
        
        return result.get('values', [])
    
    def parse_csv_sheet(self, sheet_data: List[List[str]]) -> List[Dict[str, str]]:
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
    
    @staticmethod
    def calculate_modifier(ability_score: int) -> int:
        """Calculate ability modifier from score"""
        return (ability_score - 10) // 2
    
    def read_characters(self) -> List[Dict[str, Any]]:
        """Read all character data from Google Sheets
        
        Returns list of character dicts with all data
        """
        # Read all sheets
        chars_data = self.get_sheet_data("CSV_Characters!A:Z")
        characters = self.parse_csv_sheet(chars_data)
        
        resources_data = self.get_sheet_data("CSV_Resources!A:Z")
        resources = self.parse_csv_sheet(resources_data) if resources_data else []
        
        slots_data = self.get_sheet_data("CSV_SpellSlots!A:Z")
        slots = self.parse_csv_sheet(slots_data) if slots_data else []
        
        inventory_data = self.get_sheet_data("CSV_Inventory!A:Z")
        inventory = self.parse_csv_sheet(inventory_data) if inventory_data else []
        
        currency_data = self.get_sheet_data("CSV_Currency!A:Z")
        currency = self.parse_csv_sheet(currency_data) if currency_data else []
        
        # Group supporting data by character_id
        resources_by_char = defaultdict(list)
        for r in resources:
            char_id = r.get('character_id', '').lower()
            if char_id:
                resources_by_char[char_id].append(r)
        
        slots_by_char = defaultdict(list)
        for s in slots:
            char_id = s.get('character_id', '').lower()
            if char_id:
                slot_level = s.get('slot_level', '').strip()
                try:
                    slots_by_char[char_id].append({
                        'level': int(slot_level),
                        'maximum': int(s.get('max', 0) or 0),
                        'remaining': int(s.get('remaining', 0) or 0)
                    })
                except ValueError:
                    pass
        
        inventory_by_char = defaultdict(list)
        for inv in inventory:
            char_id = inv.get('character_id', '').lower()
            if char_id:
                # Try multiple column names for item name (headers are lowercased)
                item_name = (inv.get('now ', '').strip() or 
                           inv.get('now', '').strip() or 
                           inv.get('item_name', '').strip())
                
                # Only use 'name' as fallback if it's NOT the same as character_id
                if not item_name:
                    name_val = inv.get('name', '').strip()
                    # Don't use character name as item name
                    if name_val.lower().replace(' ', '_') != char_id:
                        item_name = name_val
                
                # Skip if item_name is empty or is the character name
                char_name = inv.get('name', '').strip()
                if item_name and item_name != char_name:
                    inventory_by_char[char_id].append({
                        'name': item_name,
                        'quantity': int(inv.get('quantity', 1) or 1),
                        'weight': float(inv.get('weight_lbs', 0) or 0),
                        'item_type': inv.get('type', '').strip(),
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
        
        # Build character data
        result = []
        for char in characters:
            char_id = char.get('character_id', '').lower()
            char_name = char.get('name', '').strip()
            
            if not char_name:
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
            
            # Parse ability scores
            def get_ability_score(ability_name: str) -> int:
                """Get ability score from various possible column names"""
                # Try short form first (str, dex, con, etc.)
                score = char.get(ability_name.lower(), '').strip()
                if score and score.isdigit():
                    return int(score)
                # Try long form (strength, dexterity, etc.)
                full_names = {
                    'str': 'strength',
                    'dex': 'dexterity',
                    'con': 'constitution',
                    'int': 'intelligence',
                    'wis': 'wisdom',
                    'cha': 'charisma'
                }
                if ability_name in full_names:
                    score = char.get(full_names[ability_name], '').strip()
                    if score and score.isdigit():
                        return int(score)
                return 10  # Default
            
            stats = {
                'str': get_ability_score('str'),
                'dex': get_ability_score('dex'),
                'con': get_ability_score('con'),
                'int': get_ability_score('int'),
                'wis': get_ability_score('wis'),
                'cha': get_ability_score('cha')
            }
            
            char_data = {
                "character_id": char_id,
                "name": char_name,
                "char_class": char_class,
                "level": level,
                "race": char.get('race', '').strip() or char.get('ancestry', '').strip(),
                "player": char.get('player', '').strip(),
                "ac": int(char.get('ac', 10) or 10),
                "initiative_bonus": int(char.get('initiative', 0) or 0),
                "proficiency_bonus": int(char.get('proficiency_bonus', 2) or 2),
                "speed": int(char.get('speed', 30) or 30),
                "hp": {
                    "current": int(char.get('hp_current', 0) or 0),
                    "maximum": int(char.get('hp_max', 0) or 0),
                    "temporary": 0
                },
                "stats": stats,
                "xp": int(char.get('xp', '0').replace(',', '') if char.get('xp') else 0),
                "spell_slots": slots_by_char.get(char_id, []),
                "inventory": inventory_by_char.get(char_id, []),
                "currency": currency_by_char.get(char_id, {"cp": 0, "sp": 0, "ep": 0, "gp": 0, "pp": 0}),
                "class_resources": [],
                "notes": char.get('condition_notes', '').strip(),
                "last_synced": datetime.now().isoformat()
            }
            
            # Add resources
            for res in resources_by_char.get(char_id, []):
                res_name = res.get('resource', '').strip()
                if res_name:
                    char_data['class_resources'].append({
                        'name': res_name,
                        'maximum': int(res.get('max', 0) or 0),
                        'remaining': int(res.get('remaining', 0) or 0),
                        'active': res.get('active', '').strip().lower() == 'yes',
                        'recharge': 'long_rest'
                    })
            
            result.append(char_data)
        
        return result

