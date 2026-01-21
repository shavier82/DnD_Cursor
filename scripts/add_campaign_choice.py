#!/usr/bin/env python3
"""
Add a choice and its consequences to CAMPAIGN_EVENTS.json
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
        # Create new file if it doesn't exist
        return {
            "campaign": campaign_dir.name,
            "last_updated": datetime.now().isoformat(),
            "events": [],
            "choices_log": [],
            "consequences": {},
            "npcs": {},
            "quests": {},
            "factions": {}
        }
    
    with open(events_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_campaign_events(campaign_dir: Path, events_data: Dict[str, Any]):
    """Save CAMPAIGN_EVENTS.json"""
    events_file = campaign_dir / "saves" / "CAMPAIGN_EVENTS.json"
    events_file.parent.mkdir(parents=True, exist_ok=True)
    
    events_data['last_updated'] = datetime.now().isoformat()
    
    with open(events_file, 'w', encoding='utf-8') as f:
        json.dump(events_data, f, indent=2, ensure_ascii=False)

def add_choice(
    campaign_dir: Path,
    choice: str,
    location: str,
    chapter: int,
    choice_type: str = "tactical",
    alternatives: List[str] = None,
    immediate_impact: str = None,
    long_term_consequences: List[Dict] = None,
    affected_entities: List[str] = None,
    cross_campaign: bool = False
):
    """Add a choice to the choices_log"""
    events_data = load_campaign_events(campaign_dir)
    
    if 'choices_log' not in events_data:
        events_data['choices_log'] = []
    
    choice_id = f"choice_{len(events_data['choices_log']) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    choice_entry = {
        "id": choice_id,
        "timestamp": datetime.now().isoformat(),
        "chapter": chapter,
        "location": location,
        "choice_type": choice_type,
        "choice": choice,
        "alternatives": alternatives or [],
        "immediate_impact": immediate_impact or "",
        "long_term_consequences": long_term_consequences or [],
        "affected_entities": affected_entities or [],
        "cross_campaign_impact": cross_campaign
    }
    
    events_data['choices_log'].append(choice_entry)
    
    # Create consequences if provided
    if long_term_consequences:
        if 'consequences' not in events_data:
            events_data['consequences'] = {}
        
        for cons in long_term_consequences:
            cons_id = cons.get('id', f"cons_{len(events_data['consequences']) + 1}")
            events_data['consequences'][cons_id] = {
                "id": cons_id,
                "status": "active",
                "severity": cons.get('severity', 'moderate'),
                "origin_choice": choice_id,
                "manifestation": cons.get('description', ''),
                "factors": [choice],
                "affected_entities": {
                    "npcs": cons.get('affected_npcs', []),
                    "locations": cons.get('affected_locations', []),
                    "factions": cons.get('affected_factions', [])
                },
                "future_impact": cons.get('future_impact', ''),
                "cross_campaign": cross_campaign,
                "timeline": [
                    {
                        "timestamp": datetime.now().isoformat(),
                        "event": "Consequence created",
                        "severity_change": "unchanged"
                    }
                ]
            }
    
    save_campaign_events(campaign_dir, events_data)
    print(f"OK: Choice added: {choice}")
    if long_term_consequences:
        print(f"OK: {len(long_term_consequences)} consequence(s) created")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Add a choice to CAMPAIGN_EVENTS.json')
    parser.add_argument('--campaign', default='Phandelver', help='Campaign name')
    parser.add_argument('--choice', required=True, help='What was chosen')
    parser.add_argument('--location', required=True, help='Where the choice was made')
    parser.add_argument('--chapter', type=int, required=True, help='Chapter number')
    parser.add_argument('--type', default='tactical', choices=['moral', 'tactical', 'social', 'resource', 'quest'], help='Type of choice')
    parser.add_argument('--alternatives', nargs='+', help='Alternative options that could have been chosen')
    parser.add_argument('--immediate', help='Immediate impact of the choice')
    parser.add_argument('--consequence', help='Long-term consequence description')
    parser.add_argument('--severity', default='moderate', choices=['minor', 'moderate', 'major', 'critical'], help='Consequence severity')
    parser.add_argument('--affected-npcs', nargs='+', help='NPCs affected by this choice')
    parser.add_argument('--affected-locations', nargs='+', help='Locations affected by this choice')
    parser.add_argument('--affected-factions', nargs='+', help='Factions affected by this choice')
    parser.add_argument('--future-impact', help='How this affects future events')
    parser.add_argument('--cross-campaign', action='store_true', help='This choice affects other campaigns')
    
    args = parser.parse_args()
    
    # Load config
    config_path = Path(__file__).parent.parent / "config" / "paths.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    campaign_dir = Path(config['campaigns_root']) / args.campaign
    
    # Build long-term consequences if provided
    long_term_consequences = []
    if args.consequence:
        long_term_consequences.append({
            "id": f"cons_{args.choice.lower().replace(' ', '_')[:30]}",
            "description": args.consequence,
            "severity": args.severity,
            "affected_npcs": args.affected_npcs or [],
            "affected_locations": args.affected_locations or [],
            "affected_factions": args.affected_factions or [],
            "future_impact": args.future_impact or ""
        })
    
    add_choice(
        campaign_dir=campaign_dir,
        choice=args.choice,
        location=args.location,
        chapter=args.chapter,
        choice_type=args.type,
        alternatives=args.alternatives,
        immediate_impact=args.immediate,
        long_term_consequences=long_term_consequences,
        affected_entities=(args.affected_npcs or []) + (args.affected_locations or []),
        cross_campaign=args.cross_campaign
    )

if __name__ == '__main__':
    main()































