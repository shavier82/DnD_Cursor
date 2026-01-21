#!/usr/bin/env python3
"""
Mechanics Validation Script
Validates that mandatory procedures were followed during a session.

Usage:
    python scripts/validate_mechanics.py --session-id <id>
    python scripts/validate_mechanics.py --check-combat <combat_id>
    python scripts/validate_mechanics.py --check-quest <quest_id>
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Paths
CAMPAIGN_ROOT = Path(r"C:\DnD\Campaigns\Phandelver")
CURRENT_STATE = CAMPAIGN_ROOT / "saves" / "CURRENT_STATE.json"
CAMPAIGN_EVENTS = CAMPAIGN_ROOT / "saves" / "CAMPAIGN_EVENTS.json"
SESSION_LOGS = Path(r"C:\DnD\DnD_Cursor\session_logs")


class MechanicsValidator:
    """Validates that mandatory mechanics were followed"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.state = None
        self.events = None
        
    def load_data(self):
        """Load current state and campaign events"""
        try:
            with open(CURRENT_STATE, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
        except Exception as e:
            self.errors.append(f"Failed to load CURRENT_STATE.json: {e}")
            
        try:
            with open(CAMPAIGN_EVENTS, 'r', encoding='utf-8') as f:
                self.events = json.load(f)
        except Exception as e:
            self.errors.append(f"Failed to load CAMPAIGN_EVENTS.json: {e}")
    
    def validate_combat_post_procedures(self, combat_id: Optional[str] = None):
        """Validate that post-combat procedures were followed"""
        if not self.state or "combat" not in self.state:
            return
            
        combat = self.state.get("combat", {})
        
        # Check if combat ended
        if combat.get("ended") and not combat.get("post_combat_completed"):
            self.warnings.append(
                "⚠️ Combat ended but post-combat procedures may not be complete. "
                "Verify: XP distributed, currency looted, items distributed, Obsidian synced."
            )
        
        # Check for combatants with HP changes
        combatants = combat.get("combatants", {})
        for name, data in combatants.items():
            if data.get("status") == "defeated" and "xp_awarded" not in data:
                self.warnings.append(
                    f"⚠️ {name} was defeated but 'xp_awarded' flag not set. "
                    "Verify XP was distributed."
                )
    
    def validate_obsidian_sync(self):
        """Validate that Obsidian sync flags are set"""
        if not self.state:
            return
            
        # Check for recent HP changes without sync flags
        combat = self.state.get("combat", {})
        combatants = combat.get("combatants", {})
        
        for name, data in combatants.items():
            if isinstance(name, str) and any(char.isupper() for char in name):
                # Likely a PC
                if "obsidian_synced" not in data and data.get("hp") != data.get("max_hp"):
                    self.warnings.append(
                        f"⚠️ {name} has HP changes but 'obsidian_synced' flag not set. "
                        "Verify Obsidian sync was called."
                    )
    
    def validate_npc_status(self):
        """Validate that NPC status changes were logged"""
        if not self.events:
            return
            
        # Check for NPC deaths in events
        events = self.events.get("events", [])
        npc_deaths = [e for e in events if "npc" in str(e).lower() and "death" in str(e).lower()]
        
        if npc_deaths:
            for event in npc_deaths:
                if "update_npc" not in str(event).lower():
                    self.warnings.append(
                        f"⚠️ NPC death event found but may not have used update_npc tool. "
                        "Verify NPC status was updated in campaign wiki."
                    )
    
    def validate_quest_completion(self):
        """Validate that quest completions distributed rewards"""
        if not self.events:
            return
            
        events = self.events.get("events", [])
        completed_quests = [e for e in events if e.get("type") == "quest" and e.get("status") == "completed"]
        
        for quest in completed_quests:
            if "reward_distributed" not in quest:
                self.warnings.append(
                    f"⚠️ Quest '{quest.get('title', 'Unknown')}' completed but "
                    "'reward_distributed' flag not set. Verify rewards were distributed."
                )
    
    def validate_session_log(self, session_id: Optional[str] = None):
        """Validate that session was logged"""
        if not session_id:
            # Find latest session log
            session_logs = sorted(SESSION_LOGS.glob("session_*.jsonl"), reverse=True)
            if session_logs:
                session_id = session_logs[0].stem
            else:
                self.warnings.append("⚠️ No session logs found.")
                return
        
        log_file = SESSION_LOGS / f"{session_id}.jsonl"
        if not log_file.exists():
            self.warnings.append(f"⚠️ Session log {session_id} not found.")
            return
        
        # Check if log has events
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) < 5:
                    self.warnings.append(
                        f"⚠️ Session log {session_id} has very few events. "
                        "Consider logging more session activity."
                    )
        except Exception as e:
            self.errors.append(f"Failed to read session log: {e}")
    
    def validate_all(self, session_id: Optional[str] = None, combat_id: Optional[str] = None):
        """Run all validations"""
        print("🔍 Validating mechanics...")
        print()
        
        self.load_data()
        
        if combat_id:
            self.validate_combat_post_procedures(combat_id)
        else:
            self.validate_combat_post_procedures()
        
        self.validate_obsidian_sync()
        self.validate_npc_status()
        self.validate_quest_completion()
        self.validate_session_log(session_id)
        
        # Print results
        if self.errors:
            print("❌ ERRORS:")
            for error in self.errors:
                print(f"  {error}")
            print()
        
        if self.warnings:
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        if not self.errors and not self.warnings:
            print("✅ All validations passed!")
        else:
            print(f"📊 Summary: {len(self.errors)} errors, {len(self.warnings)} warnings")
        
        return len(self.errors) == 0


def main():
    parser = argparse.ArgumentParser(description="Validate mechanics procedures")
    parser.add_argument("--session-id", help="Session ID to validate")
    parser.add_argument("--combat-id", help="Combat ID to validate")
    parser.add_argument("--quest-id", help="Quest ID to validate")
    parser.add_argument("--all", action="store_true", help="Run all validations")
    
    args = parser.parse_args()
    
    validator = MechanicsValidator()
    
    if args.all or not any([args.session_id, args.combat_id, args.quest_id]):
        validator.validate_all(session_id=args.session_id, combat_id=args.combat_id)
    elif args.combat_id:
        validator.validate_combat_post_procedures(args.combat_id)
    elif args.quest_id:
        validator.validate_quest_completion()
    else:
        validator.validate_all(session_id=args.session_id)
    
    exit(0 if len(validator.errors) == 0 else 1)


if __name__ == "__main__":
    main()
