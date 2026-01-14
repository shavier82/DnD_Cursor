"""Markdown export utilities"""

from typing import Dict, Any
from pathlib import Path


class MarkdownExporter:
    """Export wiki content to markdown files"""
    
    @staticmethod
    def export_npc(npc_data: Dict[str, Any]) -> str:
        """Export NPC to markdown"""
        md = f"# {npc_data['name']}\n\n"
        
        if npc_data.get('title'):
            md += f"*{npc_data['title']}*\n\n"
        
        md += "## Basic Info\n"
        md += f"- **Role:** {npc_data.get('role', 'Unknown')}\n"
        md += f"- **Faction:** {npc_data.get('faction', 'None')}\n"
        md += f"- **Location:** {npc_data.get('location', 'Unknown')}\n"
        md += f"- **Alive:** {'Yes' if npc_data.get('alive', True) else 'No'}\n\n"
        
        if npc_data.get('description'):
            md += f"## Description\n{npc_data['description']}\n\n"
        
        if npc_data.get('personality'):
            md += f"## Personality\n{npc_data['personality']}\n\n"
        
        if npc_data.get('background'):
            md += f"## Background\n{npc_data['background']}\n\n"
        
        if npc_data.get('quests'):
            md += "## Related Quests\n"
            for quest in npc_data['quests']:
                md += f"- {quest}\n"
            md += "\n"
        
        return md
    
    @staticmethod
    def export_quest_summary(quests: Dict[str, Any]) -> str:
        """Export quest summary to markdown"""
        md = "# Quest Log\n\n"
        
        for status in ["accepted", "in_progress", "completed", "failed"]:
            status_quests = [q for q in quests.values() if q.get('status') == status]
            if status_quests:
                md += f"## {status.replace('_', ' ').title()}\n"
                for quest in status_quests:
                    md += f"- **{quest['name']}** ({quest.get('quest_type', 'side')})\n"
                    md += f"  - {quest.get('description', 'No description')}\n"
                md += "\n"
        
        return md
    
    @staticmethod
    def export_timeline(events: list) -> str:
        """Export timeline to markdown"""
        md = "# Campaign Timeline\n\n"
        
        # Sort by session number
        sorted_events = sorted(events, key=lambda e: e.get('session_number', 0))
        
        current_session = None
        for event in sorted_events:
            session = event.get('session_number')
            if session != current_session:
                current_session = session
                md += f"## Session {session}\n\n"
            
            md += f"### {event['title']}\n"
            md += f"*{event.get('event_type', 'other')}*\n\n"
            md += f"{event['description']}\n\n"
        
        return md




