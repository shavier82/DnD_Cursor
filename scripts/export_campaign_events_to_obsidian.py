"""Export CAMPAIGN_EVENTS.json to Obsidian vault

This script exports:
1. Campaign Events - Individual event files with dates
2. Consequences Tracker - Active consequences tracking
3. Choices Log - Player choices and their impacts

All organized in Obsidian with proper linking and metadata.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import frontmatter

# Add campaign_wiki to path
sys.path.insert(0, str(Path(__file__).parent.parent / "mcp_servers" / "campaign_wiki"))

from utils.obsidian_sync import ObsidianSync

# Paths
CAMPAIGN_PATH = Path("C:/DnD/Campaigns/Phandelver")
CAMPAIGN_EVENTS_PATH = CAMPAIGN_PATH / "saves" / "CAMPAIGN_EVENTS.json"
OBSIDIAN_VAULT = Path("C:/Users/ksist/Documents/Obsidian/DnD")

def format_date(timestamp_str: str) -> str:
    """Format ISO timestamp to readable date"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d")
    except:
        return timestamp_str.split('T')[0] if 'T' in timestamp_str else timestamp_str

def export_campaign_events():
    """Export campaign events to Obsidian"""
    print("=" * 80)
    print("EXPORTING CAMPAIGN EVENTS TO OBSIDIAN")
    print("=" * 80)
    print()
    
    # Read CAMPAIGN_EVENTS.json
    with open(CAMPAIGN_EVENTS_PATH, 'r', encoding='utf-8') as f:
        campaign_data = json.load(f)
    
    # Create folders
    events_folder = OBSIDIAN_VAULT / "Campaign_Events"
    consequences_folder = OBSIDIAN_VAULT / "Consequences"
    choices_folder = OBSIDIAN_VAULT / "Choices"
    boons_folder = OBSIDIAN_VAULT / "Boons_And_Rewards"
    
    events_folder.mkdir(exist_ok=True)
    consequences_folder.mkdir(exist_ok=True)
    choices_folder.mkdir(exist_ok=True)
    boons_folder.mkdir(exist_ok=True)
    
    # Export Events
    print("Exporting Campaign Events...")
    events = campaign_data.get("events", [])
    event_files = []
    
    for event in events:
        event_id = event.get("id", "unknown")
        event_type = event.get("type", "story_event")
        title = event.get("title", event.get("type", "Unknown Event"))
        timestamp = event.get("timestamp", "")
        
        # Create filename
        date_part = format_date(timestamp)
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)
        filename = f"{date_part}_{safe_title.replace(' ', '_')}.md"
        filepath = events_folder / filename
        
        # Create frontmatter
        metadata = {
            'type': 'campaign_event',
            'event_id': event_id,
            'event_type': event_type,
            'timestamp': timestamp,
            'date': format_date(timestamp),
            'chapter': event.get("chapter"),
            'location': event.get("location"),
            'tags': [event_type, f"chapter-{event.get('chapter', 'unknown')}"],
        }
        
        # Build content
        content = f"# {title}\n\n"
        content += f"**Date:** {format_date(timestamp)}\n"
        content += f"**Chapter:** {event.get('chapter', 'Unknown')}\n"
        content += f"**Location:** {event.get('location', 'Unknown')}\n\n"
        
        if event.get("description"):
            content += f"## Description\n{event['description']}\n\n"
        
        # Participants
        participants = event.get("participants", [])
        if participants:
            content += "## Participants\n"
            for p in participants:
                # Link to NPC or Player Character if exists
                if " " in p:
                    # Might be a player character
                    safe_name = p.replace(" ", "_")
                    content += f"- [[{p}|{safe_name}]]\n"
                else:
                    content += f"- [[{p}]]\n"
            content += "\n"
        
        # Outcomes
        outcomes = event.get("outcomes", {})
        if outcomes:
            content += "## Outcomes\n"
            for key, value in outcomes.items():
                if isinstance(value, bool):
                    content += f"- **{key.replace('_', ' ').title()}:** {'Yes' if value else 'No'}\n"
                else:
                    content += f"- **{key.replace('_', ' ').title()}:** {value}\n"
            content += "\n"
        
        # Choices (if any)
        choices = event.get("choices", [])
        if choices:
            content += "## Choices Made\n"
            for choice in choices:
                action = choice.get("action", "")
                consequence = choice.get("consequence", "")
                content += f"- **{action}** → {consequence}\n"
            content += "\n"
        
        # Rewards (if any)
        rewards = event.get("rewards", {})
        quest_reward = event.get("quest_reward", "")
        if rewards or quest_reward:
            content += "## Rewards\n"
            if isinstance(rewards, dict):
                for key, value in rewards.items():
                    content += f"- **{key.replace('_', ' ').title()}:** {value}\n"
            if quest_reward:
                content += f"- **Quest Reward:** {quest_reward}\n"
            content += "\n"
        
        # Related quests/NPCs
        if event.get("quest_giver"):
            content += f"**Quest Giver:** [[{event['quest_giver']}]]\n\n"
        
        # Write file
        post = frontmatter.Post(content, **metadata)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        event_files.append((filename, title, format_date(timestamp)))
        print(f"  [+] {filename}")
    
    print(f"\n[+] Exported {len(events)} campaign events\n")
    
    # Export Consequences
    print("Exporting Consequences...")
    consequences = campaign_data.get("consequences", {})
    consequence_files = []
    
    for cons_key, cons in consequences.items():
        cons_id = cons.get("id", cons_key)
        status = cons.get("status", "unknown")
        severity = cons.get("severity", "unknown")
        
        # Create filename
        safe_title = cons.get("manifestation", cons_id).replace(" ", "_")
        filename = f"{cons_id}_{safe_title[:50]}.md"
        filepath = consequences_folder / filename
        
        # Create frontmatter
        metadata = {
            'type': 'consequence',
            'consequence_id': cons_id,
            'status': status,
            'severity': severity,
            'cross_campaign': cons.get("cross_campaign", False),
            'tags': [status, severity, 'consequence'],
        }
        
        # Build content
        content = f"# {cons.get('manifestation', cons_id)}\n\n"
        content += f"**Status:** {status.title()}\n"
        content += f"**Severity:** {severity.title()}\n\n"
        
        if cons.get("manifestation"):
            content += f"## Manifestation\n{cons['manifestation']}\n\n"
        
        # Origin
        origin_choice = cons.get("origin_choice")
        origin_event = cons.get("origin_event")
        if origin_choice or origin_event:
            content += "## Origin\n"
            if origin_choice:
                content += f"- **Choice:** {origin_choice}\n"
            if origin_event:
                content += f"- **Event:** [[{origin_event}]]\n"
            content += "\n"
        
        # Affected Entities
        affected = cons.get("affected_entities", {})
        if affected:
            content += "## Affected Entities\n"
            for entity_type, entities in affected.items():
                if entities:
                    content += f"### {entity_type.replace('_', ' ').title()}\n"
                    for entity in entities:
                        content += f"- [[{entity}]]\n"
                    content += "\n"
        
        # Future Impact
        if cons.get("future_impact"):
            content += f"## Future Impact\n{cons['future_impact']}\n\n"
        
        # Timeline
        timeline = cons.get("timeline", [])
        if timeline:
            content += "## Timeline\n"
            for entry in timeline:
                date = format_date(entry.get("timestamp", ""))
                event_desc = entry.get("event", "")
                content += f"- **{date}:** {event_desc}\n"
            content += "\n"
        
        # Write file
        post = frontmatter.Post(content, **metadata)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        consequence_files.append((filename, cons.get("manifestation", cons_id), status))
        print(f"  [+] {filename}")
    
    print(f"\n[+] Exported {len(consequences)} consequences\n")
    
    # Export Choices
    print("Exporting Choices Log...")
    choices = campaign_data.get("choices_log", [])
    choice_files = []
    
    for choice in choices:
        choice_id = choice.get("id", "unknown")
        choice_desc = choice.get("choice", "Unknown Choice")
        timestamp = choice.get("timestamp", "")
        
        # Create filename
        date_part = format_date(timestamp)
        safe_desc = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in choice_desc[:50])
        filename = f"{date_part}_{safe_desc.replace(' ', '_')}.md"
        filepath = choices_folder / filename
        
        # Create frontmatter
        metadata = {
            'type': 'player_choice',
            'choice_id': choice_id,
            'choice_type': choice.get("choice_type", "unknown"),
            'timestamp': timestamp,
            'date': format_date(timestamp),
            'chapter': choice.get("chapter"),
            'location': choice.get("location"),
            'tags': [choice.get("choice_type", "unknown"), f"chapter-{choice.get('chapter', 'unknown')}"],
        }
        
        # Build content
        content = f"# {choice_desc}\n\n"
        content += f"**Date:** {format_date(timestamp)}\n"
        content += f"**Chapter:** {choice.get('chapter', 'Unknown')}\n"
        content += f"**Location:** {choice.get('location', 'Unknown')}\n"
        content += f"**Type:** {choice.get('choice_type', 'Unknown')}\n\n"
        
        # Choice and alternatives
        content += f"## Choice Made\n{choice_desc}\n\n"
        
        alternatives = choice.get("alternatives", [])
        if alternatives:
            content += "## Alternatives\n"
            for alt in alternatives:
                content += f"- {alt}\n"
            content += "\n"
        
        # Immediate Impact
        if choice.get("immediate_impact"):
            content += f"## Immediate Impact\n{choice['immediate_impact']}\n\n"
        
        # Long-term Consequences
        long_term = choice.get("long_term_consequences", [])
        if long_term:
            content += "## Long-Term Consequences\n"
            for cons in long_term:
                cons_id = cons.get("id", "")
                desc = cons.get("description", "")
                severity = cons.get("severity", "")
                content += f"- **[{cons_id}]([[{cons_id}_{cons.get('description', '')[:30].replace(' ', '_')}]])** ({severity}): {desc}\n"
            content += "\n"
        
        # Affected Entities
        affected = choice.get("affected_entities", [])
        if affected:
            content += "## Affected Entities\n"
            for entity in affected:
                content += f"- [[{entity}]]\n"
            content += "\n"
        
        # Write file
        post = frontmatter.Post(content, **metadata)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        choice_files.append((filename, choice_desc, format_date(timestamp)))
        print(f"  [+] {filename}")
    
    print(f"\n[+] Exported {len(choices)} choices\n")
    
    # Create index files
    print("Creating index files...")
    
    # Events Index
    events_index = events_folder / "00_Campaign_Events_Index.md"
    with open(events_index, 'w', encoding='utf-8') as f:
        f.write("# Campaign Events Index\n\n")
        f.write("## All Events\n\n")
        for filename, title, date in sorted(event_files, key=lambda x: x[2], reverse=True):
            f.write(f"- [[{filename.replace('.md', '')}|{date} - {title}]]\n")
    
    print(f"  [+] Created events index\n")
    
    # Consequences Index
    cons_index = consequences_folder / "00_Consequences_Tracker.md"
    with open(cons_index, 'w', encoding='utf-8') as f:
        f.write("# Consequences Tracker\n\n")
        
        # Group by status
        by_status = {}
        for filename, title, status in consequence_files:
            if status not in by_status:
                by_status[status] = []
            by_status[status].append((filename, title))
        
        for status in ['active', 'ongoing', 'resolved', 'escalated']:
            if status in by_status:
                f.write(f"## {status.title()}\n\n")
                for filename, title in by_status[status]:
                    f.write(f"- [[{filename.replace('.md', '')}|{title}]]\n")
                f.write("\n")
    
    print(f"  [+] Created consequences index\n")
    
    # Choices Index
    choices_index = choices_folder / "00_Choices_Log_Index.md"
    with open(choices_index, 'w', encoding='utf-8') as f:
        f.write("# Choices Log Index\n\n")
        f.write("## All Choices\n\n")
        for filename, title, date in sorted(choice_files, key=lambda x: x[2], reverse=True):
            f.write(f"- [[{filename.replace('.md', '')}|{date} - {title[:60]}]]\n")
    
    print(f"  [+] Created choices index\n")
    
    # Export Boons & Campaign Rewards
    print("Exporting Boons & Campaign Rewards...")
    boons = []
    boon_ids_seen = set()
    
    # Extract boons/rewards from events AND choices_log (some events get misplaced)
    events_for_boons = campaign_data.get("events", [])
    choices_for_boons = campaign_data.get("choices_log", [])
    
    # Combine both sources - some "events" are incorrectly in choices_log
    all_potential_events = list(events_for_boons) + [c for c in choices_for_boons if c.get("type") in ["quest", "encounter", "story_event"] or c.get("quest_giver") or c.get("rewards")]
    
    for event in all_potential_events:
        rewards = event.get("rewards", {})
        quest_reward = event.get("quest_reward", "")
        quest_giver = event.get("quest_giver", "Unknown")
        event_title = event.get("title", event.get("type", "Unknown Event"))
        timestamp = event.get("timestamp", "")
        
        # Check for service-based rewards (permanent benefits) in rewards.service
        if isinstance(rewards, dict) and rewards.get("service"):
            service_desc = rewards.get("service", "")
            boon_id = f"boon_{event.get('id', 'unknown')}"
            
            if boon_id not in boon_ids_seen:
                boon = {
                    "id": boon_id,
                    "name": service_desc.split("(")[0].strip() if "(" in service_desc else service_desc,
                    "type": "service",
                    "description": service_desc,
                    "source_quest": event_title,
                    "quest_giver": quest_giver,
                    "date_earned": format_date(timestamp),
                    "status": "active",
                    "duration": service_desc.split("(")[1].strip(")") if "(" in service_desc and "duration:" not in service_desc.split("(")[1].lower() else "permanent",
                    "location": event.get("location", ""),
                    "notes": event.get("notes", "")
                }
                boons.append(boon)
                boon_ids_seen.add(boon_id)
        
        # Also check for service-based rewards in quest_reward (free services, lodging, etc.)
        # Only check if we didn't already add this boon from rewards.service
        if isinstance(quest_reward, str) and f"boon_{event.get('id', 'unknown')}" not in boon_ids_seen:
            # Check for free services, lodging, recurring income
            quest_lower = quest_reward.lower()
            if any(keyword in quest_lower for keyword in ["free", "share", "profit", "income", "monthly", "weekly", "recurring", "lodging", "room and board"]):
                boon_id = f"boon_{event.get('id', 'unknown')}"
                
                if boon_id not in boon_ids_seen:
                    # Determine type
                    if any(keyword in quest_lower for keyword in ["share", "profit", "income", "monthly", "weekly", "recurring"]):
                        boon_type = "recurring_income"
                    elif any(keyword in quest_lower for keyword in ["free", "lodging", "room", "board", "service"]):
                        boon_type = "service"
                    else:
                        boon_type = "boon"
                    
                    boon = {
                        "id": boon_id,
                        "name": quest_reward.split("(")[0].strip() if "(" in quest_reward else quest_reward,
                        "type": boon_type,
                        "description": quest_reward,
                        "source_quest": event_title,
                        "quest_giver": quest_giver,
                        "date_earned": format_date(timestamp),
                        "status": "active",
                        "duration": quest_reward.split("(")[1].strip(")") if "(" in quest_reward else "permanent",
                        "location": event.get("location", ""),
                        "notes": event.get("notes", "")
                    }
                    boons.append(boon)
                    boon_ids_seen.add(boon_id)
    
    # Create boon files
    boon_files = []
    for boon in boons:
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in boon["name"])
        filename = f"{safe_name.replace(' ', '_')}.md"
        filepath = boons_folder / filename
        
        # Create frontmatter
        metadata = {
            'type': 'boon',
            'boon_id': boon["id"],
            'boon_type': boon["type"],
            'status': boon["status"],
            'date_earned': boon["date_earned"],
            'tags': [boon["type"], 'boon', 'reward'],
        }
        
        # Build content
        content = f"# {boon['name']}\n\n"
        content += f"**Type:** {boon['type'].replace('_', ' ').title()}\n"
        content += f"**Status:** {boon['status'].title()}\n"
        content += f"**Date Earned:** {boon['date_earned']}\n"
        content += f"**Duration:** {boon['duration']}\n\n"
        
        if boon.get("source_quest"):
            content += f"**Source:** [[{boon['source_quest'].replace(' ', '_')}]]\n"
        if boon.get("quest_giver"):
            content += f"**From:** [[{boon['quest_giver']}]]\n"
        if boon.get("location"):
            content += f"**Location:** [[{boon['location']}]]\n"
        content += "\n"
        
        content += f"## Description\n{boon['description']}\n\n"
        
        if boon.get("notes"):
            content += f"## Notes\n{boon['notes']}\n\n"
        
        # Write file
        post = frontmatter.Post(content, **metadata)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        boon_files.append((filename, boon["name"], boon["status"]))
        print(f"  [+] {filename}")
    
    print(f"\n[+] Exported {len(boons)} boons/rewards\n")
    
    # Create Boons Index
    boons_index = boons_folder / "00_Boons_And_Rewards_Index.md"
    with open(boons_index, 'w', encoding='utf-8') as f:
        f.write("# Boons & Campaign Rewards\n\n")
        f.write("## Active Boons\n\n")
        for filename, name, status in boon_files:
            if status == "active":
                f.write(f"- [[{filename.replace('.md', '')}|{name}]]\n")
        f.write("\n## All Boons\n\n")
        for filename, name, status in sorted(boon_files, key=lambda x: x[1]):
            f.write(f"- [[{filename.replace('.md', '')}|{name}]] ({status})\n")
    
    print(f"  [+] Created boons index\n")
    
    print("=" * 80)
    print("EXPORT COMPLETE")
    print("=" * 80)
    print(f"[+] Campaign Events: {len(events)} files")
    print(f"[+] Consequences: {len(consequences)} files")
    print(f"[+] Choices: {len(choices)} files")
    print(f"[+] Boons & Rewards: {len(boons)} files")
    print(f"\nLocation: {OBSIDIAN_VAULT}")
    print(f"- Campaign_Events/")
    print(f"- Consequences/")
    print(f"- Choices/")
    print(f"- Boons_And_Rewards/")

if __name__ == "__main__":
    export_campaign_events()
