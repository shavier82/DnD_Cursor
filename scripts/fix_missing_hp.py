#!/usr/bin/env python3
"""Fix missing HP Max for Torgga and Vandross"""

import json
from pathlib import Path

config_path = Path(__file__).parent.parent / "config" / "paths.json"
with open(config_path, 'r') as f:
    config = json.load(f)

players_dir = Path(config['default_campaign_dir']) / "players"

# Update Torgga
torgga_file = players_dir / "torgga_brawnanvil.json"
with open(torgga_file, 'r', encoding='utf-8') as f:
    char_data = json.load(f)

if 'hit_points' not in char_data:
    char_data['hit_points'] = {}
char_data['hit_points']['maximum'] = 48

with open(torgga_file, 'w', encoding='utf-8') as f:
    json.dump(char_data, f, indent=2)

print("Torgga: Updated HP Max to 48")

# Update Vandross
vandross_file = players_dir / "vandross_ephrates.json"
with open(vandross_file, 'r', encoding='utf-8') as f:
    char_data = json.load(f)

if 'hit_points' not in char_data:
    char_data['hit_points'] = {}
char_data['hit_points']['maximum'] = 44

with open(vandross_file, 'w', encoding='utf-8') as f:
    json.dump(char_data, f, indent=2)

print("Vandross: Updated HP Max to 44")

print("Done!")

















