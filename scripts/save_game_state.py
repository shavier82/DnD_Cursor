#!/usr/bin/env python3
"""
Save Game State
Saves current game state to campaign-specific save file
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def save_game_state(state_data, campaign="Phandelver"):
    """Save game state to campaign save file"""
    
    # Load paths config
    script_dir = Path(__file__).parent
    config_path = script_dir.parent / "config" / "paths.json"
    
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}")
        return False
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Determine save file path
    campaign_dir = Path(config['default_campaign_dir'])
    saves_dir = campaign_dir / "saves"
    saves_dir.mkdir(parents=True, exist_ok=True)
    
    save_file = saves_dir / "CURRENT_STATE.json"
    
    # Add metadata
    state_data['last_saved'] = datetime.now().isoformat()
    state_data['campaign'] = campaign
    
    # Save to file
    try:
        with open(save_file, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=2, ensure_ascii=False)
        
        print(f"OK: Game state saved to {save_file}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to save game state: {e}")
        return False

def load_game_state(campaign="Phandelver"):
    """Load game state from campaign save file"""
    
    # Load paths config
    script_dir = Path(__file__).parent
    config_path = script_dir.parent / "config" / "paths.json"
    
    if not config_path.exists():
        return None
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Determine save file path
    campaign_dir = Path(config['default_campaign_dir'])
    save_file = campaign_dir / "saves" / "CURRENT_STATE.json"
    
    if not save_file.exists():
        return None
    
    try:
        with open(save_file, 'r', encoding='utf-8-sig') as f:
            state = json.load(f)
        return state
    except Exception as e:
        print(f"ERROR: Failed to load game state: {e}")
        return None

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Save or load game state')
    parser.add_argument('action', choices=['save', 'load'], help='Action to perform')
    parser.add_argument('--input', help='Path to state JSON file (for save)')
    parser.add_argument('--campaign', default='Phandelver', help='Campaign name')
    args = parser.parse_args()
    
    if args.action == 'save':
        if args.input:
            # Load state from input file
            with open(args.input, 'r', encoding='utf-8-sig') as f:
                state = json.load(f)
        else:
            # Create minimal state
            state = {
                'timestamp': datetime.now().isoformat(),
                'scene': {},
                'party': {},
                'combat': {}
            }
        
        if save_game_state(state, args.campaign):
            return 0
        else:
            return 1
    
    elif args.action == 'load':
        state = load_game_state(args.campaign)
        if state:
            print(json.dumps(state, indent=2))
            return 0
        else:
            print("No save state found")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())



