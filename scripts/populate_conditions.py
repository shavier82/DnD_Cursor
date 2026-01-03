#!/usr/bin/env python3
"""
Populate CSV_Conditions with standard D&D 5e condition definitions
"""

import json
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def load_credentials(credentials_path):
    """Load service account credentials"""
    with open(credentials_path, 'r') as f:
        creds_data = json.load(f)
    
    credentials = service_account.Credentials.from_service_account_info(
        creds_data,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    return credentials

# Standard D&D 5e conditions with mechanical effects
CONDITIONS = {
    "Blinded": {
        "mechanical_effects": json.dumps({
            "attack_disadvantage": True,
            "skill_disadvantage": ["Perception", "Investigation", "Stealth"],
            "condition_immunity": ["blinded"]
        })
    },
    "Charmed": {
        "mechanical_effects": json.dumps({
            "condition_immunity": ["charmed"]
        })
    },
    "Deafened": {
        "mechanical_effects": json.dumps({
            "skill_disadvantage": ["Perception"]
        })
    },
    "Exhaustion": {
        "mechanical_effects": json.dumps({
            "note": "Level-based effects handled separately"
        })
    },
    "Frightened": {
        "mechanical_effects": json.dumps({
            "attack_disadvantage": True,
            "skill_disadvantage": ["Perception"],
            "save_disadvantage": ["Wisdom"]
        })
    },
    "Grappled": {
        "mechanical_effects": json.dumps({
            "speed_mod": 0,
            "condition_immunity": ["prone"]
        })
    },
    "Incapacitated": {
        "mechanical_effects": json.dumps({
            "attack_disadvantage": True,
            "condition_immunity": ["incapacitated"]
        })
    },
    "Invisible": {
        "mechanical_effects": json.dumps({
            "attack_advantage": True,
            "skill_advantage": ["Stealth"]
        })
    },
    "Paralyzed": {
        "mechanical_effects": json.dumps({
            "attack_disadvantage": True,
            "save_disadvantage": ["Dexterity"],
            "condition_immunity": ["paralyzed"]
        })
    },
    "Petrified": {
        "mechanical_effects": json.dumps({
            "attack_disadvantage": True,
            "damage_resistance": ["all"],
            "condition_immunity": ["petrified", "frightened"]
        })
    },
    "Poisoned": {
        "mechanical_effects": json.dumps({
            "attack_disadvantage": True,
            "skill_disadvantage": ["Perception", "Investigation"]
        })
    },
    "Prone": {
        "mechanical_effects": json.dumps({
            "attack_disadvantage": True,
            "skill_disadvantage": ["Stealth"]
        })
    },
    "Restrained": {
        "mechanical_effects": json.dumps({
            "attack_disadvantage": True,
            "save_disadvantage": ["Dexterity"],
            "speed_mod": 0
        })
    },
    "Stunned": {
        "mechanical_effects": json.dumps({
            "attack_disadvantage": True,
            "save_disadvantage": ["Dexterity"],
            "condition_immunity": ["stunned"]
        })
    },
    "Unconscious": {
        "mechanical_effects": json.dumps({
            "attack_disadvantage": True,
            "attack_advantage": True,  # Attacks against unconscious have advantage
            "condition_immunity": ["unconscious"]
        })
    },
    # Common buffs/debuffs
    "Blessed": {
        "mechanical_effects": json.dumps({
            "attack_advantage": True,
            "save_advantage": ["Dexterity", "Strength", "Constitution"]
        })
    },
    "Bane": {
        "mechanical_effects": json.dumps({
            "attack_disadvantage": True,
            "save_disadvantage": ["Dexterity", "Strength", "Constitution"]
        })
    },
    "Haste": {
        "mechanical_effects": json.dumps({
            "ac_mod": 2,
            "speed_mod": 30,
            "attack_advantage": True,
            "save_advantage": ["Dexterity"]
        })
    },
    "Slow": {
        "mechanical_effects": json.dumps({
            "speed_mod": -30,
            "attack_disadvantage": True,
            "save_disadvantage": ["Dexterity"]
        })
    },
    "Shield of Faith": {
        "mechanical_effects": json.dumps({
            "ac_mod": 2
        })
    },
    "Enlarge": {
        "mechanical_effects": json.dumps({
            "attack_advantage": True  # On Strength checks
        })
    },
    "Reduce": {
        "mechanical_effects": json.dumps({
            "attack_disadvantage": True,  # On Strength checks
            "damage_resistance": ["all"]  # Reduced damage
        })
    },
    "Inspired": {
        "mechanical_effects": json.dumps({
            "attack_advantage": True  # On one roll
        })
    },
    "Rage": {
        "mechanical_effects": json.dumps({
            "damage_resistance": ["bludgeoning", "piercing", "slashing"],
            "attack_advantage": True  # On Strength checks
        })
    }
}

def populate_conditions(service, spreadsheet_id):
    """Populate CSV_Conditions sheet with condition definitions"""
    
    # Check if sheet exists and has data
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='CSV_Conditions!A:B'
        ).execute()
        existing = result.get('values', [])
    except HttpError:
        existing = []
    
    # Prepare rows
    rows = []
    if not existing or len(existing) < 2:
        # Add header row
        rows.append(['condition_name', 'mechanical_effects'])
    
    # Add condition rows
    for condition_name, data in CONDITIONS.items():
        rows.append([condition_name, data['mechanical_effects']])
    
    # Write to sheet
    try:
        if not existing or len(existing) < 2:
            # Write header + all conditions
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='CSV_Conditions!A:B',
                valueInputOption='RAW',
                body={'values': rows}
            ).execute()
            print(f"OK: Created CSV_Conditions with {len(CONDITIONS)} conditions")
        else:
            # Append new conditions (skip existing)
            existing_names = {row[0].strip().lower() for row in existing[1:] if len(row) > 0}
            new_rows = []
            for condition_name, data in CONDITIONS.items():
                if condition_name.lower() not in existing_names:
                    new_rows.append([condition_name, data['mechanical_effects']])
            
            if new_rows:
                service.spreadsheets().values().append(
                    spreadsheetId=spreadsheet_id,
                    range='CSV_Conditions!A:B',
                    valueInputOption='RAW',
                    insertDataOption='INSERT_ROWS',
                    body={'values': new_rows}
                ).execute()
                print(f"OK: Added {len(new_rows)} new conditions")
            else:
                print(f"OK: All {len(CONDITIONS)} conditions already exist")
        
        return True
    except HttpError as error:
        print(f"ERROR: Failed to populate conditions: {error}")
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Populate CSV_Conditions with condition definitions')
    parser.add_argument('--credentials', default='C:\\DnD\\keys\\google_sheets_key.json', help='Credentials file')
    parser.add_argument('--spreadsheet-id', default='1kCcauRdoetVuSv7O1uH6gb95psX0S7quy1uilVpc2dw', help='Spreadsheet ID')
    args = parser.parse_args()
    
    # Load credentials
    credentials = load_credentials(args.credentials)
    service = build('sheets', 'v4', credentials=credentials)
    
    # Populate conditions
    if populate_conditions(service, args.spreadsheet_id):
        print(f"SUCCESS: CSV_Conditions populated with {len(CONDITIONS)} conditions")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())



