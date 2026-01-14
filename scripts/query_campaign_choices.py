#!/usr/bin/env python3
"""
Query and display campaign choices and consequences
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def load_campaign_events(campaign_dir: Path) -> Dict[str, Any]:
    """Load CAMPAIGN_EVENTS.json"""
    events_file = campaign_dir / "saves" / "CAMPAIGN_EVENTS.json"
    if not events_file.exists():
        print(f"ERROR: CAMPAIGN_EVENTS.json not found at {events_file}")
        sys.exit(1)
    
    with open(events_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_choices_affecting_npc(events_data: Dict, npc_name: str) -> List[Dict]:
    """Find all choices that affected a specific NPC"""
    choices = []
    if 'choices_log' not in events_data:
        return choices
    
    for choice in events_data['choices_log']:
        if 'affected_entities' in choice.get('long_term_consequences', []):
            for consequence in choice['long_term_consequences']:
                if npc_name in consequence.get('affected_entities', []):
                    choices.append(choice)
                    break
    
    # Also check NPC interactions
    if 'npcs' in events_data and npc_name.lower() in events_data['npcs']:
        npc = events_data['npcs'][npc_name.lower()]
        for interaction in npc.get('interactions', []):
            if 'choice_impact' in interaction:
                # Find the choice that caused this interaction
                for choice in events_data.get('choices_log', []):
                    if choice.get('id') == interaction.get('choice_id'):
                        choices.append(choice)
    
    return choices

def find_active_consequences(events_data: Dict) -> List[Dict]:
    """Find all active consequences"""
    if 'consequences' not in events_data:
        return []
    
    return [
        cons for cons in events_data['consequences'].values()
        if cons.get('status') == 'active' or cons.get('status') == 'ongoing'
    ]

def find_choices_with_long_term_impact(events_data: Dict) -> List[Dict]:
    """Find all choices with long-term consequences"""
    if 'choices_log' not in events_data:
        return []
    
    return [
        choice for choice in events_data['choices_log']
        if choice.get('long_term_consequences') and len(choice['long_term_consequences']) > 0
    ]

def find_cross_campaign_effects(events_data: Dict) -> List[Dict]:
    """Find all cross-campaign effects"""
    if 'cross_campaign_effects' not in events_data:
        return []
    
    return events_data['cross_campaign_effects']

def display_choice(choice: Dict, index: int = None):
    """Display a choice in a readable format"""
    prefix = f"{index}. " if index is not None else ""
    print(f"\n{prefix}CHOICE: {choice.get('choice', 'Unknown')}")
    print(f"  Location: {choice.get('location', 'Unknown')}")
    print(f"  Chapter: {choice.get('chapter', 'Unknown')}")
    print(f"  Type: {choice.get('choice_type', 'Unknown')}")
    print(f"  Timestamp: {choice.get('timestamp', 'Unknown')}")
    
    if choice.get('alternatives'):
        print(f"  Alternatives: {', '.join(choice['alternatives'])}")
    
    if choice.get('immediate_impact'):
        print(f"  Immediate Impact: {choice['immediate_impact']}")
    
    if choice.get('long_term_consequences'):
        print(f"  Long-Term Consequences:")
        for cons in choice['long_term_consequences']:
            print(f"    - {cons.get('description', 'Unknown')} (Severity: {cons.get('severity', 'Unknown')})")
    
    if choice.get('cross_campaign_impact'):
        print(f"  ⚠️  CROSS-CAMPAIGN IMPACT")

def display_consequence(cons: Dict, index: int = None):
    """Display a consequence in a readable format"""
    prefix = f"{index}. " if index is not None else ""
    print(f"\n{prefix}CONSEQUENCE: {cons.get('manifestation', 'Unknown')}")
    print(f"  Status: {cons.get('status', 'Unknown')}")
    print(f"  Severity: {cons.get('severity', 'Unknown')}")
    print(f"  Origin: {cons.get('origin_choice', cons.get('origin_event', 'Unknown'))}")
    
    if cons.get('affected_entities'):
        entities = cons['affected_entities']
        if entities.get('npcs'):
            print(f"  Affected NPCs: {', '.join(entities['npcs'])}")
        if entities.get('locations'):
            print(f"  Affected Locations: {', '.join(entities['locations'])}")
        if entities.get('factions'):
            print(f"  Affected Factions: {', '.join(entities['factions'])}")
    
    if cons.get('future_impact'):
        print(f"  Future Impact: {cons['future_impact']}")
    
    if cons.get('cross_campaign'):
        print(f"  ⚠️  CROSS-CAMPAIGN EFFECT")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Query campaign choices and consequences')
    parser.add_argument('--campaign', default='Phandelver', help='Campaign name')
    parser.add_argument('--npc', help='Find choices affecting this NPC')
    parser.add_argument('--active-consequences', action='store_true', help='Show all active consequences')
    parser.add_argument('--long-term', action='store_true', help='Show choices with long-term impact')
    parser.add_argument('--cross-campaign', action='store_true', help='Show cross-campaign effects')
    parser.add_argument('--all-choices', action='store_true', help='Show all choices')
    parser.add_argument('--summary', action='store_true', help='Show summary statistics')
    
    args = parser.parse_args()
    
    # Load config
    config_path = Path(__file__).parent.parent / "config" / "paths.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    campaign_dir = Path(config['campaigns_root']) / args.campaign
    
    # Load events
    events_data = load_campaign_events(campaign_dir)
    
    print("=" * 60)
    print(f"Campaign Choices and Consequences Query")
    print(f"Campaign: {args.campaign}")
    print("=" * 60)
    
    if args.summary:
        print("\n--- SUMMARY ---")
        total_choices = len(events_data.get('choices_log', []))
        total_consequences = len(events_data.get('consequences', {}))
        active_consequences = len([c for c in events_data.get('consequences', {}).values() if c.get('status') in ['active', 'ongoing']])
        cross_campaign = len(events_data.get('cross_campaign_effects', []))
        
        print(f"Total Choices Logged: {total_choices}")
        print(f"Total Consequences: {total_consequences}")
        print(f"Active Consequences: {active_consequences}")
        print(f"Cross-Campaign Effects: {cross_campaign}")
        print(f"NPCs Tracked: {len(events_data.get('npcs', {}))}")
        print(f"Quests Tracked: {len(events_data.get('quests', {}))}")
    
    if args.npc:
        print(f"\n--- Choices Affecting {args.npc} ---")
        choices = find_choices_affecting_npc(events_data, args.npc)
        if choices:
            for i, choice in enumerate(choices, 1):
                display_choice(choice, i)
        else:
            print(f"No choices found affecting {args.npc}")
    
    if args.active_consequences:
        print("\n--- Active Consequences ---")
        consequences = find_active_consequences(events_data)
        if consequences:
            for i, cons in enumerate(consequences, 1):
                display_consequence(cons, i)
        else:
            print("No active consequences found")
    
    if args.long_term:
        print("\n--- Choices with Long-Term Impact ---")
        choices = find_choices_with_long_term_impact(events_data)
        if choices:
            for i, choice in enumerate(choices, 1):
                display_choice(choice, i)
        else:
            print("No choices with long-term impact found")
    
    if args.cross_campaign:
        print("\n--- Cross-Campaign Effects ---")
        effects = find_cross_campaign_effects(events_data)
        if effects:
            for i, effect in enumerate(effects, 1):
                print(f"\n{i}. {effect.get('effect', 'Unknown')}")
                print(f"   Origin Campaign: {effect.get('origin_campaign', 'Unknown')}")
                print(f"   Type: {effect.get('type', 'Unknown')}")
        else:
            print("No cross-campaign effects found")
    
    if args.all_choices:
        print("\n--- All Choices ---")
        choices = events_data.get('choices_log', [])
        if choices:
            for i, choice in enumerate(choices, 1):
                display_choice(choice, i)
        else:
            print("No choices logged yet")
    
    if not any([args.npc, args.active_consequences, args.long_term, args.cross_campaign, args.all_choices, args.summary]):
        print("\nUse --help to see available query options")
        print("\nExamples:")
        print("  python query_campaign_choices.py --summary")
        print("  python query_campaign_choices.py --npc 'Mirna Dendrar'")
        print("  python query_campaign_choices.py --active-consequences")
        print("  python query_campaign_choices.py --long-term")
        print("  python query_campaign_choices.py --cross-campaign")

if __name__ == '__main__':
    main()

















