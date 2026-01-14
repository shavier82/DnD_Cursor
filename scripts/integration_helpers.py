#!/usr/bin/env python3
"""
Integration Helper Functions
Provides unified interface for MCP calls across all systems
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# MCP CALL WRAPPERS (for easy integration)
# ============================================================================

class MCPIntegration:
    """Unified interface for all MCP servers"""
    
    def __init__(self):
        self.cache = {}
        self.logger = logging.getLogger(__name__)
    
    # ========================================================================
    # CHARACTER DATA (Obsidian Sync MCP)
    # ========================================================================
    
    def get_character_stats(self, character_id: str) -> Dict[str, Any]:
        """Get character stats from Obsidian"""
        # In practice, this would call the Obsidian Sync MCP
        # For now, return cached or load from party_characters.json
        cache_key = f"char_stats_{character_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            party_file = Path("C:/DnD/DnD_Cursor/campaign_data/party_characters.json")
            if party_file.exists():
                with open(party_file, 'r', encoding='utf-8') as f:
                    party = json.load(f)
                    for char in party:
                        if char.get("character_id") == character_id:
                            self.cache[cache_key] = char
                            return char
        except Exception as e:
            logger.error(f"Error loading character stats: {e}")
        
        return {}
    
    def update_character_hp(self, character_id: str, new_hp: int) -> bool:
        """Update character HP in Obsidian"""
        # MCP: obsidian_sync.update_character_hp(character_id, new_hp)
        logger.info(f"UPDATE HP: {character_id} → {new_hp}")
        # Clear cache
        self.cache.pop(f"char_stats_{character_id}", None)
        return True
    
    def check_raging(self, character_id: str) -> bool:
        """Check if character is currently raging"""
        # MCP: obsidian_sync.check_raging(character_id)
        char = self.get_character_stats(character_id)
        resources = char.get("resources", [])
        for resource in resources:
            if resource.get("name") == "Rage":
                return resource.get("active", False)
        return False
    
    def use_spell_slot(self, character_id: str, spell_level: int) -> bool:
        """Use a spell slot"""
        # MCP: obsidian_sync.use_spell_slot(character_id, spell_level)
        logger.info(f"USE SPELL SLOT: {character_id} level {spell_level}")
        return True
    
    # ========================================================================
    # RULES & MECHANICS (Rules Database MCP)
    # ========================================================================
    
    def lookup_monster(self, monster_name: str) -> Dict[str, Any]:
        """Lookup monster stats"""
        cache_key = f"monster_{monster_name.lower()}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # MCP: rules_database.lookup_monster(monster_name)
        # Fallback: return basic stats
        fallback = {
            "name": monster_name,
            "ac": 15,
            "hp": 10,
            "speed": 30,
            "abilities": {"str": 10, "dex": 10, "con": 10, "int": 10, "wis": 10, "cha": 10}
        }
        self.cache[cache_key] = fallback
        return fallback
    
    def lookup_spell(self, spell_name: str) -> Dict[str, Any]:
        """Lookup spell details"""
        # MCP: rules_database.lookup_spell(spell_name)
        return {"name": spell_name, "level": 1, "school": "Evocation"}
    
    def lookup_condition(self, condition_name: str) -> Dict[str, Any]:
        """Lookup condition effects"""
        # MCP: rules_database.lookup_condition(condition_name)
        return {"name": condition_name, "effects": []}
    
    # ========================================================================
    # DICE ROLLING (Dice Roller MCP)
    # ========================================================================
    
    def roll_dice(self, expression: str, reason: str = "") -> Dict[str, Any]:
        """Roll dice"""
        # MCP: dice_roller.roll_dice(expression, reason)
        import random
        # Simple parser (fallback)
        if 'd' in expression:
            parts = expression.split('d')
            num = int(parts[0])
            die = int(parts[1].split('+')[0].split('-')[0])
            rolls = [random.randint(1, die) for _ in range(num)]
            total = sum(rolls)
            
            # Handle modifiers
            if '+' in expression:
                mod = int(expression.split('+')[1])
                total += mod
            elif '-' in expression:
                mod = int(expression.split('-')[1])
                total -= mod
            
            return {
                "expression": expression,
                "rolls": rolls,
                "total": total,
                "reason": reason
            }
        return {"expression": expression, "total": 0}
    
    def roll_attack(self, modifier: int, advantage: bool = False, disadvantage: bool = False) -> Dict[str, Any]:
        """Roll attack"""
        # MCP: dice_roller.roll_attack(modifier, advantage, disadvantage)
        import random
        if advantage:
            rolls = [random.randint(1, 20), random.randint(1, 20)]
            roll = max(rolls)
        elif disadvantage:
            rolls = [random.randint(1, 20), random.randint(1, 20)]
            roll = min(rolls)
        else:
            roll = random.randint(1, 20)
            rolls = [roll]
        
        return {
            "rolls": rolls,
            "roll": roll,
            "modifier": modifier,
            "total": roll + modifier,
            "advantage": advantage,
            "disadvantage": disadvantage
        }
    
    # ========================================================================
    # SESSION LOGGING (Session Recorder MCP)
    # ========================================================================
    
    def log_event(self, event_type: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Log session event"""
        # MCP: session_recorder.log_event(event_type, content, metadata)
        logger.info(f"LOG EVENT [{event_type}]: {content}")
        return True
    
    def start_session_log(self, campaign_name: str, session_title: str = None) -> bool:
        """Start session logging"""
        # MCP: session_recorder.start_session_log(campaign_name, session_title)
        logger.info(f"START SESSION: {campaign_name}")
        return True
    
    def stop_session_log(self) -> bool:
        """Stop session logging"""
        # MCP: session_recorder.stop_session_log()
        logger.info("STOP SESSION")
        return True
    
    # ========================================================================
    # CALENDAR & WEATHER (Weather/Calendar MCP)
    # ========================================================================
    
    def get_current_date_time(self) -> Dict[str, Any]:
        """Get current in-game date/time"""
        # MCP: weather_calendar.get_current_date_time()
        return {
            "date": "15 Mirtul, 1492 DR",
            "time": "3:00 PM",
            "season": "Spring"
        }
    
    def get_current_weather(self, location: str = "Phandalin") -> Dict[str, Any]:
        """Get current weather"""
        # MCP: weather_calendar.get_current_weather(location)
        return {
            "location": location,
            "condition": "Clear",
            "temperature": "Mild",
            "visibility": "Good",
            "travel_modifier": "100%",
            "effects": []
        }
    
    def advance_time(self, hours: int = 0, days: int = 0) -> bool:
        """Advance in-game time"""
        # MCP: weather_calendar.advance_time(hours, days)
        logger.info(f"ADVANCE TIME: +{hours}h, +{days}d")
        return True
    
    def long_rest(self) -> Dict[str, Any]:
        """Process long rest"""
        # MCP: weather_calendar.long_rest()
        logger.info("LONG REST: 8 hours")
        return {"hours_advanced": 8, "message": "Party rested"}
    
    # ========================================================================
    # KNOWLEDGE GRAPH (Knowledge Graph MCP)
    # ========================================================================
    
    def add_entity(self, entity_id: str, entity_type: str, name: str, data: Dict = None) -> bool:
        """Add entity to knowledge graph"""
        # MCP: knowledge_graph.add_entity(entity_id, entity_type, name, data)
        logger.info(f"ADD ENTITY: {entity_type} '{name}'")
        return True
    
    def add_relationship(self, from_id: str, to_id: str, relationship_type: str) -> bool:
        """Add relationship to knowledge graph"""
        # MCP: knowledge_graph.add_relationship(from_id, to_id, relationship_type)
        logger.info(f"ADD RELATIONSHIP: {from_id} --[{relationship_type}]--> {to_id}")
        return True
    
    def analyze_consequence_chain(self, choice_id: str) -> List[Dict[str, Any]]:
        """Analyze consequence chain"""
        # MCP: knowledge_graph.analyze_consequence_chain(choice_id)
        return []
    
    # ========================================================================
    # MUSIC & AMBIENCE (Music & Ambience MCP)
    # ========================================================================
    
    def play_ambient(self, scene: str, auto_open: bool = True) -> bool:
        """Play ambient music"""
        # MCP: music_ambience.play_ambient(scene, auto_open)
        logger.info(f"PLAY AMBIENT: {scene}")
        return True
    
    def play_sfx(self, sfx_name: str) -> bool:
        """Play sound effect"""
        # MCP: music_ambience.play_sfx(sfx_name)
        logger.info(f"PLAY SFX: {sfx_name}")
        return True
    
    def stop_music(self) -> bool:
        """Stop music"""
        # MCP: music_ambience.stop_music()
        logger.info("STOP MUSIC")
        return True
    
    # ========================================================================
    # CAMPAIGN WIKI (Campaign Wiki MCP)
    # ========================================================================
    
    def get_npc(self, npc_id: str) -> Dict[str, Any]:
        """Get NPC data"""
        # MCP: campaign_wiki.get_npc(npc_id)
        return {"id": npc_id, "name": "Unknown NPC"}
    
    def get_quest(self, quest_id: str) -> Dict[str, Any]:
        """Get quest data"""
        # MCP: campaign_wiki.get_quest(quest_id)
        return {"id": quest_id, "name": "Unknown Quest", "status": "active"}
    
    # ========================================================================
    # BATCH OPERATIONS
    # ========================================================================
    
    def batch_lookup_monsters(self, monster_names: List[str]) -> List[Dict[str, Any]]:
        """Lookup multiple monsters in parallel"""
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self.lookup_monster, name): name for name in monster_names}
            results = []
            for future in as_completed(futures):
                results.append(future.result())
            return results
    
    def batch_get_character_stats(self, character_ids: List[str]) -> List[Dict[str, Any]]:
        """Get stats for multiple characters in parallel"""
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self.get_character_stats, cid): cid for cid in character_ids}
            results = []
            for future in as_completed(futures):
                results.append(future.result())
            return results


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

mcp = MCPIntegration()


# ============================================================================
# WORKFLOW HELPERS
# ============================================================================

def session_start_workflow(campaign_name: str) -> Dict[str, Any]:
    """Complete session start workflow"""
    results = {}
    
    # 1. Start session log
    mcp.start_session_log(campaign_name)
    results["session_log"] = "started"
    
    # 2. Get date/time
    date_time = mcp.get_current_date_time()
    results["date_time"] = date_time
    
    # 3. Get weather
    weather = mcp.get_current_weather()
    results["weather"] = weather
    
    # 4. Play ambient music
    mcp.play_ambient("town")
    results["music"] = "playing"
    
    # 5. Log event
    mcp.log_event("narration", f"Session started: {date_time['date']}, {weather['condition']}")
    
    return results


def combat_start_workflow(enemy_type: str, enemy_count: int) -> Dict[str, Any]:
    """Complete combat start workflow"""
    results = {}
    
    # 1. Lookup monsters
    monsters = mcp.batch_lookup_monsters([enemy_type] * enemy_count)
    results["monsters"] = monsters
    
    # 2. Switch to combat music
    mcp.play_ambient("combat")
    results["music"] = "combat"
    
    # 3. Check weather effects
    weather = mcp.get_current_weather()
    results["weather"] = weather
    
    # 4. Log event
    mcp.log_event("combat", f"Combat started: {enemy_count} {enemy_type}")
    
    # 5. Add to knowledge graph
    combat_id = f"combat_{enemy_type}_{enemy_count}"
    mcp.add_entity(combat_id, "event", f"Combat: {enemy_count} {enemy_type}")
    results["event_id"] = combat_id
    
    return results


def skill_check_workflow(character_id: str, skill: str, dc: int) -> Dict[str, Any]:
    """Complete skill check workflow"""
    results = {}
    
    # 1. Get character stats
    char = mcp.get_character_stats(character_id)
    modifier = char.get("skills", {}).get(skill, 0)
    results["character"] = char.get("name")
    results["modifier"] = modifier
    
    # 2. Roll dice
    roll = mcp.roll_dice(f"1d20+{modifier}", f"{skill} check")
    results["roll"] = roll
    
    # 3. Determine success
    success = roll["total"] >= dc
    results["success"] = success
    results["dc"] = dc
    
    # 4. Log event
    outcome = "SUCCESS" if success else "FAILURE"
    mcp.log_event("roll", f"{char.get('name')} {skill} check: {roll['total']} vs DC {dc} - {outcome}")
    
    return results


def long_rest_workflow(character_ids: List[str]) -> Dict[str, Any]:
    """Complete long rest workflow"""
    results = {}
    
    # 1. Advance time
    rest_result = mcp.long_rest()
    results["time_advanced"] = rest_result
    
    # 2. Restore HP for all characters
    for char_id in character_ids:
        char = mcp.get_character_stats(char_id)
        max_hp = char.get("hp_max", 0)
        mcp.update_character_hp(char_id, max_hp)
    results["characters_restored"] = len(character_ids)
    
    # 3. Log event
    mcp.log_event("narration", "Party took a long rest. HP and resources restored.")
    
    # 4. Play peaceful music
    mcp.play_ambient("peaceful")
    results["music"] = "peaceful"
    
    return results


# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":
    print("Testing Integration Helpers...")
    
    print("\n1. Session Start")
    print(json.dumps(session_start_workflow("Test Campaign"), indent=2))
    
    print("\n2. Combat Start")
    print(json.dumps(combat_start_workflow("Goblin", 3), indent=2))
    
    print("\n3. Skill Check")
    print(json.dumps(skill_check_workflow("eglath_bearkiller", "intimidation", 15), indent=2))
    
    print("\nIntegration helpers working!")

