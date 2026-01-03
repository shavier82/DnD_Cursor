#!/usr/bin/env python3
"""
Execute Sheet Operations from STATE_PATCHER Output
Processes sheet_ops array from dnd_out_STATE_PATCHER.json
"""

import json
import sys
import argparse
from pathlib import Path

# Import condition and update functions
from manage_conditions import (
    load_credentials, get_character_id_from_name,
    add_condition, remove_condition, tick_conditions
)
from update_sheets_data import (
    update_character_xp, update_character_currency, update_character_resources
)

try:
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("ERROR: Google API libraries not installed")

def execute_sheet_ops(service, spreadsheet_id, sheet_ops):
    """Execute a list of sheet operations"""
    results = []
    
    for op in sheet_ops:
        op_type = op.get('op', '')
        
        if op_type == 'condition_add':
            character_id = op.get('character_id')
            condition = op.get('condition')
            source = op.get('source', 'unknown')
            duration_type = op.get('duration_type')
            duration_value = op.get('duration_value', 0)
            ticks_remaining = op.get('ticks_remaining', duration_value)
            mechanical_effects = op.get('mechanical_effects', '')
            
            if add_condition(service, spreadsheet_id, character_id, condition, source,
                           duration_type, duration_value, mechanical_effects):
                results.append(f"OK: Added {condition} to {character_id}")
            else:
                results.append(f"ERROR: Failed to add {condition} to {character_id}")
        
        elif op_type == 'condition_remove':
            character_id = op.get('character_id')
            condition = op.get('condition')
            source = op.get('source')
            
            if remove_condition(service, spreadsheet_id, character_id, condition, source):
                results.append(f"OK: Removed {condition} from {character_id}")
            else:
                results.append(f"ERROR: Failed to remove {condition} from {character_id}")
        
        elif op_type == 'condition_tick':
            mode = op.get('mode', 'round')
            amount = op.get('amount', 1)
            
            count = tick_conditions(service, spreadsheet_id, mode, amount)
            results.append(f"OK: Ticked {count} condition(s)")
        
        elif op_type == 'currency_add':
            character_id = op.get('character_id')
            currency_data = {
                'cp': op.get('cp', 0),
                'sp': op.get('sp', 0),
                'ep': op.get('ep', 0),
                'gp': op.get('gp', 0),
                'pp': op.get('pp', 0)
            }
            
            if update_character_currency(service, spreadsheet_id, character_id, currency_data):
                results.append(f"OK: Updated currency for {character_id}")
            else:
                results.append(f"ERROR: Failed to update currency for {character_id}")
        
        elif op_type == 'resource_set':
            character_id = op.get('character_id')
            resource_name = op.get('resource')
            resource_data = {}
            if 'max' in op:
                resource_data['max'] = op['max']
            if 'remaining' in op:
                resource_data['remaining'] = op['remaining']
            if 'active' in op:
                resource_data['active'] = op['active']
            
            resources = {resource_name: resource_data}
            
            if update_character_resources(service, spreadsheet_id, character_id, resources):
                results.append(f"OK: Updated {resource_name} for {character_id}")
            else:
                results.append(f"ERROR: Failed to update {resource_name} for {character_id}")
        
        elif op_type == 'xp_add' or op_type == 'xp_set':
            character_id = op.get('character_id')
            xp = op.get('xp', op.get('value', 0))
            
            if update_character_xp(service, spreadsheet_id, character_id, xp):
                results.append(f"OK: Updated XP for {character_id} to {xp}")
            else:
                results.append(f"ERROR: Failed to update XP for {character_id}")
        
        else:
            results.append(f"WARNING: Unknown operation type: {op_type}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Execute sheet operations from STATE_PATCHER output')
    parser.add_argument('--input', required=True, help='Path to dnd_out_STATE_PATCHER.json')
    parser.add_argument('--credentials', default='C:\\DnD\\keys\\google_sheets_key.json', help='Credentials file')
    parser.add_argument('--spreadsheet-id', default='1kCcauRdoetVuSv7O1uH6gb95psX0S7quy1uilVpc2dw', help='Spreadsheet ID')
    args = parser.parse_args()
    
    if not GOOGLE_AVAILABLE:
        print("ERROR: Google API libraries not installed")
        sys.exit(1)
    
    # Load STATE_PATCHER output
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)
    
    with open(input_path, 'r', encoding='utf-8-sig') as f:
        state_patcher = json.load(f)
    
    # Extract sheet_ops
    sheet_ops = state_patcher.get('sheet_ops', [])
    
    if not sheet_ops:
        print("No sheet operations to execute")
        return 0
    
    print(f"[execute] Processing {len(sheet_ops)} sheet operation(s)...")
    
    # Load credentials and build service
    credentials = load_credentials(args.credentials)
    service = build('sheets', 'v4', credentials=credentials)
    
    # Execute operations
    results = execute_sheet_ops(service, args.spreadsheet_id, sheet_ops)
    
    # Print results
    for result in results:
        print(f"[execute] {result}")
    
    # Check for errors
    errors = [r for r in results if r.startswith("ERROR")]
    if errors:
        print(f"\n[execute] FAILED: {len(errors)} error(s)")
        return 1
    else:
        print(f"\n[execute] SUCCESS: All operations completed")
        return 0

if __name__ == "__main__":
    sys.exit(main())



