#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mechanics Reminder System
Automatically reminds AI to check mechanics checklist at key moments.

This script is called automatically before critical operations.
"""

import json
import sys
import io
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

VALIDATION_FILE = Path(__file__).parent.parent / ".mechanics_validated.json"
CHECKLIST_PATH = Path(__file__).parent.parent / "MECHANICS_AUTOMATION_CHECKLIST.md"

def get_reminder_for_context(context: str):
    """Get specific reminder based on context"""
    
    reminders = {
        "pre_combat": [
            "⚔️ PRE-COMBAT REMINDER:",
            "  - HP changes → update_character_hp() to Obsidian",
            "  - Spell slots → use_spell_slot() to Obsidian",
            "  - Resources → use_resource() to Obsidian",
            "  - Conditions → add_condition()/remove_condition() to Obsidian"
        ],
        "post_combat": [
            "💰 POST-COMBAT REMINDER (MANDATORY):",
            "  1. end_combat_tool(combat_id)",
            "  2. Calculate XP → update_character_xp() for EACH PC",
            "  3. Roll currency → update_character_currency() for EACH PC",
            "  4. List items → ask players → add_inventory_item() for chosen items",
            "  5. Show summary → ask 'What next?'"
        ],
        "npc_status_change": [
            "🎭 NPC STATUS REMINDER:",
            "  - NPC dies/executed → update_npc(alive=false, status='executed')",
            "  - Auto-syncs to Obsidian (no manual steps needed)"
        ],
        "quest_completion": [
            "📜 QUEST COMPLETION REMINDER:",
            "  - Use complete_quest() tool → Auto-distributes:",
            "    * Gold (evenly divided)",
            "    * XP (evenly divided)",
            "    * Items (lists for players)",
            "    * Faction reputation (+5 to quest giver's faction)"
        ],
        "spell_cast": [
            "✨ SPELL CAST REMINDER:",
            "  - After spell cast → use_spell_slot(creature_id, spell_level)",
            "  - Auto-deducts slot and syncs to Obsidian",
            "  - Then resolve spell effect"
        ],
        "inventory_change": [
            "📦 INVENTORY REMINDER:",
            "  - Always include quantity and weight",
            "  - Use add_inventory_item(name, item, qty, weight)",
            "  - Auto-updates Obsidian table"
        ],
        "session_start": [
            "🚀 SESSION START REMINDER:",
            "  - Read MECHANICS_AUTOMATION_CHECKLIST.md FIRST",
            "  - Read CURRENT_STATE.json",
            "  - Read CAMPAIGN_EVENTS.json",
            "  - Load campaign wiki: create_or_load_wiki()"
        ],
        "travel_start": [
            "🚶 TRAVEL START REMINDER (MANDATORY):",
            "  1. Check character rations (1 per person per day)",
            "  2. If insufficient, check Party Wagon and transfer rations",
            "  3. Call process_travel(party_members, days, travel_type) MCP tool",
            "  4. For each day of travel:",
            "     - Check for random encounters (1d20 per day/night, 17-20 triggers)",
            "     - Use check_random_encounter(biome, terrain, time_of_day) if encounter occurs",
            "  5. Update CURRENT_STATE.json with new location",
            "  6. Handle long rests (restore HP/spell slots/resources after each full day)",
            "  7. Update character sheets after long rest"
        ],
        "npc_faction_interaction": [
            "🏰 FACTION REPUTATION REMINDER (MANDATORY):",
            "  - When helping or angering NPCs with faction affiliations:",
            "  1. Check if NPC has a faction (via get_npc_data or campaign wiki)",
            "  2. Determine reputation change based on action:",
            "     * Helping NPC: +5 to +25 reputation (based on significance)",
            "     * Angering NPC: -5 to -25 reputation (based on severity)",
            "  3. Call update_faction_reputation(campaign_name, faction_id, 'Party', amount)",
            "  4. Auto-syncs to Obsidian (no manual steps needed)",
            "  - CRITICAL: This happens automatically when completing quests via complete_quest()"
        ]
    }
    
    return reminders.get(context, [
        "⚠️  MECHANICS REMINDER:",
        "  - Check MECHANICS_AUTOMATION_CHECKLIST.md for procedures"
    ])


def check_validation():
    """Check if checklist was validated"""
    if not VALIDATION_FILE.exists():
        return False, "Checklist not validated. Run: python scripts/pre_session_check.py"
    
    try:
        with open(VALIDATION_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("checklist_read", False), "Checklist validated"
    except:
        return False, "Validation file corrupted"


def print_reminder(context: str):
    """Print reminder for specific context"""
    reminder = get_reminder_for_context(context)
    
    print("\n" + "="*60)
    for line in reminder:
        print(line)
    print("="*60 + "\n")
    
    # Check validation
    validated, message = check_validation()
    if not validated:
        print(f"⚠️  {message}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/mechanics_reminder.py <context>")
        print("\nContexts: pre_combat, post_combat, npc_status_change, quest_completion, spell_cast, inventory_change, session_start, travel_start")
        sys.exit(1)
    
    context = sys.argv[1]
    print_reminder(context)
