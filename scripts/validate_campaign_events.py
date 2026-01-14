import json
import sys

try:
    with open(r'C:\DnD\Campaigns\Phandelver\saves\CAMPAIGN_EVENTS.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print('JSON is valid')
    print(f'Total events: {len(data.get("events", []))}')
    print(f'Total choices: {len(data.get("choices_log", []))}')
    print(f'Total consequences: {len(data.get("consequences", {}))}')
    print(f'Total NPCs: {len(data.get("npcs", {}))}')
    print(f'Total quests: {len(data.get("quests", {}))}')
    print(f'Total factions: {len(data.get("factions", {}))}')
except json.JSONDecodeError as e:
    print(f'JSON Error: {e}')
    print(f'Line {e.lineno}, Column {e.colno}')
    sys.exit(1)
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)

















