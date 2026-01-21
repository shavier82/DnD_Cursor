#!/usr/bin/env python3
"""
D&D Rules Database MCP Server
Provides instant lookups from the structured rules database.

This server offers:
- Instant rule lookups (grapple, shove, etc.)
- Monster stat block retrieval
- Condition definitions
- Action descriptions
- Spell information (when implemented)
"""

import json
import logging
from pathlib import Path
from typing import Any, Sequence
import sys

# MCP SDK imports
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Suppress verbose MCP library logs
logging.getLogger("mcp.server.session").setLevel(logging.ERROR)
logging.getLogger("mcp.server.stdio").setLevel(logging.ERROR)

# Rules database directory
RULES_DB_DIR = Path(r"C:\DnD\DnD_Cursor\rules_database")

# Load database files into memory for instant access
DATABASE = {}

def load_database():
    """Load all database files into memory."""
    global DATABASE
    
    db_files = {
        "rules": "rules.json",
        "conditions": "conditions.json",
        "monsters": "monsters.json",
        "actions": "actions.json",
        "spells": "spells.json",
        "magic_items": "magic_items.json"
    }
    
    for db_name, filename in db_files.items():
        file_path = RULES_DB_DIR / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                DATABASE[db_name] = json.load(f)
            logger.info(f"Loaded {db_name}: {len(DATABASE[db_name])} entries")
        else:
            DATABASE[db_name] = {}
            logger.warning(f"{db_name} not found at {file_path}")
    
    logger.info("Rules database loaded successfully")

# Initialize database
load_database()

# Create MCP server
app = Server("rules-database")

# Level-up data
LEVEL_UP_DATA = {
    "proficiency_bonus": {
        1: 2, 2: 2, 3: 2, 4: 2, 5: 3, 6: 3, 7: 3, 8: 3, 9: 4, 10: 4,
        11: 4, 12: 4, 13: 5, 14: 5, 15: 5, 16: 5, 17: 6, 18: 6, 19: 6, 20: 6
    },
    "xp_by_level": {
        1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000, 8: 34000,
        9: 48000, 10: 64000, 11: 85000, 12: 100000, 13: 120000, 14: 140000,
        15: 165000, 16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
    },
    "hp_by_class": {
        "Barbarian": 12,
        "Fighter": 10,
        "Paladin": 10,
        "Ranger": 10,
        "Cleric": 8,
        "Druid": 8,
        "Monk": 8,
        "Rogue": 8,
        "Warlock": 8,
        "Bard": 8,
        "Sorcerer": 6,
        "Wizard": 6
    },
    "class_features": {
        "Barbarian": {
            1: ["Rage (2/day)", "Unarmored Defense"],
            2: ["Reckless Attack", "Danger Sense"],
            3: ["Primal Path", "Primal Knowledge"],
            4: ["Ability Score Improvement"],
            5: ["Extra Attack", "Fast Movement"],
            6: ["Path Feature"],
            7: ["Feral Instinct", "Instinctive Pounce"],
            8: ["Ability Score Improvement"],
            9: ["Brutal Critical (1 die)"],
            10: ["Path Feature", "Primal Knowledge"],
            11: ["Relentless Rage"],
            12: ["Ability Score Improvement"],
            13: ["Brutal Critical (2 dice)"],
            14: ["Path Feature"],
            15: ["Persistent Rage"],
            16: ["Ability Score Improvement"],
            17: ["Brutal Critical (3 dice)"],
            18: ["Indomitable Might"],
            19: ["Ability Score Improvement"],
            20: ["Primal Champion"]
        },
        "Fighter": {
            1: ["Fighting Style", "Second Wind"],
            2: ["Action Surge (1/rest)"],
            3: ["Martial Archetype"],
            4: ["Ability Score Improvement"],
            5: ["Extra Attack"],
            6: ["Ability Score Improvement"],
            7: ["Martial Archetype Feature"],
            8: ["Ability Score Improvement"],
            9: ["Indomitable (1/rest)"],
            10: ["Martial Archetype Feature"],
            11: ["Extra Attack (2)"],
            12: ["Ability Score Improvement"],
            13: ["Indomitable (2/rest)"],
            14: ["Ability Score Improvement"],
            15: ["Martial Archetype Feature"],
            16: ["Ability Score Improvement"],
            17: ["Action Surge (2/rest)", "Indomitable (3/rest)"],
            18: ["Martial Archetype Feature"],
            19: ["Ability Score Improvement"],
            20: ["Extra Attack (3)"]
        },
        "Cleric": {
            1: ["Spellcasting", "Divine Domain"],
            2: ["Channel Divinity (1/rest)", "Divine Domain Feature"],
            3: ["2nd-level Spells"],
            4: ["Ability Score Improvement"],
            5: ["3rd-level Spells", "Destroy Undead (CR 1/2)"],
            6: ["Channel Divinity (2/rest)", "Divine Domain Feature"],
            7: ["4th-level Spells"],
            8: ["Ability Score Improvement", "Destroy Undead (CR 1)", "Divine Domain Feature"],
            9: ["5th-level Spells"],
            10: ["Divine Intervention"],
            11: ["6th-level Spells", "Destroy Undead (CR 2)"],
            12: ["Ability Score Improvement"],
            13: ["7th-level Spells"],
            14: ["Destroy Undead (CR 3)"],
            15: ["8th-level Spells"],
            16: ["Ability Score Improvement"],
            17: ["9th-level Spells", "Destroy Undead (CR 4)", "Divine Domain Feature"],
            18: ["Channel Divinity (3/rest)"],
            19: ["Ability Score Improvement"],
            20: ["Divine Intervention Improvement"]
        },
        "Rogue": {
            1: ["Expertise", "Sneak Attack (1d6)", "Thieves' Cant"],
            2: ["Cunning Action"],
            3: ["Sneak Attack (2d6)", "Roguish Archetype"],
            4: ["Ability Score Improvement"],
            5: ["Sneak Attack (3d6)", "Uncanny Dodge"],
            6: ["Expertise"],
            7: ["Sneak Attack (4d6)", "Evasion"],
            8: ["Ability Score Improvement"],
            9: ["Sneak Attack (5d6)", "Roguish Archetype Feature"],
            10: ["Ability Score Improvement"],
            11: ["Sneak Attack (6d6)", "Reliable Talent"],
            12: ["Ability Score Improvement"],
            13: ["Sneak Attack (7d6)", "Roguish Archetype Feature"],
            14: ["Blindsense"],
            15: ["Sneak Attack (8d6)", "Slippery Mind"],
            16: ["Ability Score Improvement"],
            17: ["Sneak Attack (9d6)", "Roguish Archetype Feature"],
            18: ["Elusive"],
            19: ["Sneak Attack (10d6)", "Ability Score Improvement"],
            20: ["Stroke of Luck"]
        },
        "Wizard": {
            1: ["Spellcasting", "Arcane Recovery"],
            2: ["Arcane Tradition"],
            3: ["2nd-level Spells"],
            4: ["Ability Score Improvement"],
            5: ["3rd-level Spells"],
            6: ["Arcane Tradition Feature"],
            7: ["4th-level Spells"],
            8: ["Ability Score Improvement"],
            9: ["5th-level Spells"],
            10: ["Arcane Tradition Feature"],
            11: ["6th-level Spells"],
            12: ["Ability Score Improvement"],
            13: ["7th-level Spells"],
            14: ["Arcane Tradition Feature"],
            15: ["8th-level Spells"],
            16: ["Ability Score Improvement"],
            17: ["9th-level Spells"],
            18: ["Spell Mastery"],
            19: ["Ability Score Improvement"],
            20: ["Signature Spells"]
        }
    },
    "spell_slots": {
        "Cleric": {
            1: [2, 0, 0, 0, 0, 0, 0, 0, 0],
            2: [3, 0, 0, 0, 0, 0, 0, 0, 0],
            3: [4, 2, 0, 0, 0, 0, 0, 0, 0],
            4: [4, 3, 0, 0, 0, 0, 0, 0, 0],
            5: [4, 3, 2, 0, 0, 0, 0, 0, 0],
            6: [4, 3, 3, 0, 0, 0, 0, 0, 0],
            7: [4, 3, 3, 1, 0, 0, 0, 0, 0],
            8: [4, 3, 3, 2, 0, 0, 0, 0, 0],
            9: [4, 3, 3, 3, 1, 0, 0, 0, 0],
            10: [4, 3, 3, 3, 2, 0, 0, 0, 0],
            11: [4, 3, 3, 3, 2, 1, 0, 0, 0],
            12: [4, 3, 3, 3, 2, 1, 0, 0, 0],
            13: [4, 3, 3, 3, 2, 1, 1, 0, 0],
            14: [4, 3, 3, 3, 2, 1, 1, 0, 0],
            15: [4, 3, 3, 3, 2, 1, 1, 1, 0],
            16: [4, 3, 3, 3, 2, 1, 1, 1, 0],
            17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
            18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
            19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
            20: [4, 3, 3, 3, 3, 2, 2, 1, 1]
        },
        "Wizard": {
            1: [2, 0, 0, 0, 0, 0, 0, 0, 0],
            2: [3, 0, 0, 0, 0, 0, 0, 0, 0],
            3: [4, 2, 0, 0, 0, 0, 0, 0, 0],
            4: [4, 3, 0, 0, 0, 0, 0, 0, 0],
            5: [4, 3, 2, 0, 0, 0, 0, 0, 0],
            6: [4, 3, 3, 0, 0, 0, 0, 0, 0],
            7: [4, 3, 3, 1, 0, 0, 0, 0, 0],
            8: [4, 3, 3, 2, 0, 0, 0, 0, 0],
            9: [4, 3, 3, 3, 1, 0, 0, 0, 0],
            10: [4, 3, 3, 3, 2, 0, 0, 0, 0],
            11: [4, 3, 3, 3, 2, 1, 0, 0, 0],
            12: [4, 3, 3, 3, 2, 1, 0, 0, 0],
            13: [4, 3, 3, 3, 2, 1, 1, 0, 0],
            14: [4, 3, 3, 3, 2, 1, 1, 0, 0],
            15: [4, 3, 3, 3, 2, 1, 1, 1, 0],
            16: [4, 3, 3, 3, 2, 1, 1, 1, 0],
            17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
            18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
            19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
            20: [4, 3, 3, 3, 3, 2, 2, 1, 1]
        }
    }
}

app = Server("rules-database")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="lookup_rule",
            description="Look up a specific D&D rule (e.g., 'Grapple', 'Shove', 'Initiative'). Returns the full rule text, mechanics, and related information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_name": {
                        "type": "string",
                        "description": "Name of the rule to look up (e.g., 'Grapple', 'Shove')"
                    }
                },
                "required": ["rule_name"]
            }
        ),
        Tool(
            name="lookup_monster",
            description="Get a monster's stat block and information (e.g., 'Goblin', 'Ancient Red Dragon', 'Beholder'). Returns AC, HP, abilities, actions, and lore.",
            inputSchema={
                "type": "object",
                "properties": {
                    "monster_name": {
                        "type": "string",
                        "description": "Name of the monster (e.g., 'Goblin', 'Dragon')"
                    }
                },
                "required": ["monster_name"]
            }
        ),
        Tool(
            name="lookup_condition",
            description="Get the definition and effects of a status condition (e.g., 'Grappled', 'Prone', 'Stunned', 'Paralyzed').",
            inputSchema={
                "type": "object",
                "properties": {
                    "condition_name": {
                        "type": "string",
                        "description": "Name of the condition (e.g., 'Grappled', 'Prone')"
                    }
                },
                "required": ["condition_name"]
            }
        ),
        Tool(
            name="lookup_action",
            description="Get the description of a standard action (e.g., 'Attack', 'Dash', 'Dodge', 'Help').",
            inputSchema={
                "type": "object",
                "properties": {
                    "action_name": {
                        "type": "string",
                        "description": "Name of the action (e.g., 'Attack', 'Dash')"
                    }
                },
                "required": ["action_name"]
            }
        ),
        Tool(
            name="search_monsters",
            description="Search for monsters by name, type, or keyword (e.g., 'goblin', 'dragon', 'undead'). Returns a list of matching monsters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term (monster name, type, or keyword)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_rules",
            description="Search for rules by name or keyword (e.g., 'grapple', 'advantage', 'cover'). Returns matching rules.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term (rule name or keyword)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="lookup_spell",
            description="Look up a specific spell (e.g., 'Fireball', 'Cure Wounds', 'Shield'). Returns spell level, school, components, and classes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "spell_name": {
                        "type": "string",
                        "description": "Name of the spell (e.g., 'Fireball', 'Cure Wounds')"
                    }
                },
                "required": ["spell_name"]
            }
        ),
        Tool(
            name="search_spells",
            description="Search for spells by name, class, level, or school (e.g., 'fire', 'cleric', 'evocation'). Returns matching spells.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term (spell name, class, school, or keyword)"
                    },
                    "spell_class": {
                        "type": "string",
                        "description": "Filter by class (e.g., 'Wizard', 'Cleric')"
                    },
                    "spell_level": {
                        "type": "integer",
                        "description": "Filter by spell level (0-9, where 0 = cantrip)"
                    },
                    "school": {
                        "type": "string",
                        "description": "Filter by school (e.g., 'Evocation', 'Abjuration')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_spells_by_class",
            description="Get all spells for a specific class, organized by level (e.g., 'Wizard', 'Cleric'). Optionally filter by spell level.",
            inputSchema={
                "type": "object",
                "properties": {
                    "spell_class": {
                        "type": "string",
                        "description": "Class name (e.g., 'Wizard', 'Cleric', 'Bard')"
                    },
                    "spell_level": {
                        "type": "integer",
                        "description": "Optional: Filter by spell level (0-9, where 0 = cantrip)"
                    }
                },
                "required": ["spell_class"]
            }
        ),
        Tool(
            name="level_up_guide",
            description="Get comprehensive level-up information for a character: HP gain, new features, spell slots, proficiency bonus, and step-by-step checklist.",
            inputSchema={
                "type": "object",
                "properties": {
                    "char_class": {
                        "type": "string",
                        "description": "Character class (Barbarian, Fighter, Cleric, Rogue, Wizard)"
                    },
                    "current_level": {
                        "type": "integer",
                        "description": "Current level (1-19)"
                    },
                    "constitution_modifier": {
                        "type": "integer",
                        "description": "Constitution modifier for HP calculation"
                    }
                },
                "required": ["char_class", "current_level", "constitution_modifier"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls."""
    try:
        if name == "lookup_rule":
            return await handle_lookup_rule(arguments)
        elif name == "lookup_monster":
            return await handle_lookup_monster(arguments)
        elif name == "lookup_condition":
            return await handle_lookup_condition(arguments)
        elif name == "lookup_action":
            return await handle_lookup_action(arguments)
        elif name == "search_monsters":
            return await handle_search_monsters(arguments)
        elif name == "search_rules":
            return await handle_search_rules(arguments)
        elif name == "lookup_spell":
            return await handle_lookup_spell(arguments)
        elif name == "search_spells":
            return await handle_search_spells(arguments)
        elif name == "get_spells_by_class":
            return await handle_get_spells_by_class(arguments)
        elif name == "level_up_guide":
            # Handle level_up_guide inline since it doesn't have a separate handler
            char_class = arguments.get("char_class", "").title()
            current_level = arguments.get("current_level", 1)
            constitution_modifier = arguments.get("constitution_modifier", 0)
            
            if current_level < 1 or current_level > 19:
                return [TextContent(type="text", text="Error: Current level must be between 1 and 19")]
            
            next_level = current_level + 1
            
            # Get class-specific data
            class_data = LEVEL_UP_DATA["class_features"].get(char_class, {})
            if not class_data:
                return [TextContent(type="text", text=f"Error: Class '{char_class}' not found. Available classes: {', '.join(LEVEL_UP_DATA['class_features'].keys())}")]
            
            # Build response
            result = f"**Level Up: {char_class} {current_level} → {next_level}**\n\n"
            
            # HP Gain
            hp_die = LEVEL_UP_DATA["hp_by_class"].get(char_class, 8)
            hp_gain = hp_die // 2 + 1 + constitution_modifier
            result += f"**HP Gain:** {hp_gain} ({hp_die}//2 + 1 + {constitution_modifier} CON)\n\n"
            
            # Proficiency Bonus
            prof_bonus = LEVEL_UP_DATA["proficiency_bonus"].get(next_level, 2)
            result += f"**Proficiency Bonus:** +{prof_bonus}\n\n"
            
            # Class Features
            new_features = class_data.get(next_level, [])
            if new_features:
                result += f"**New Features:**\n"
                for feature in new_features:
                    result += f"  - {feature}\n"
                result += "\n"
            
            # Spell Slots (if applicable)
            spell_slots = LEVEL_UP_DATA["spell_slots"].get(char_class, {}).get(next_level)
            if spell_slots:
                result += f"**Spell Slots:** {spell_slots}\n\n"
            
            # XP Required
            xp_required = LEVEL_UP_DATA["xp_by_level"].get(next_level, 0)
            result += f"**XP Required for Level {next_level}:** {xp_required:,}\n"
            
            return [TextContent(type="text", text=result)]
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Error in {name}: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def handle_lookup_rule(arguments: dict) -> Sequence[TextContent]:
    """Look up a specific rule."""
    rule_name = arguments.get("rule_name", "").lower().replace(' ', '_')
    
    if rule_name in DATABASE["rules"]:
        rule = DATABASE["rules"][rule_name]
        
        result = f"**{rule['name']}**\n\n"
        result += f"**Type:** {rule['type']}\n"
        result += f"**Source:** {rule['source']}\n"
        result += f"**Category:** {rule['category']}\n\n"
        result += f"**Summary:** {rule['summary']}\n\n"
        
        if rule.get("mechanics"):
            result += "**Mechanics:**\n"
            for key, value in rule["mechanics"].items():
                result += f"- **{key.replace('_', ' ').title()}:** {value}\n"
            result += "\n"
        
        result += f"**Full Text:**\n{rule['full_text']}\n"
        
        if rule.get("related_rules"):
            result += f"\n**Related Rules:** {', '.join(rule['related_rules'])}"
        
        return [TextContent(type="text", text=result)]
    else:
        return [TextContent(type="text", text=f"Rule '{arguments.get('rule_name')}' not found in database.")]

async def handle_lookup_monster(arguments: dict) -> Sequence[TextContent]:
    """Look up a monster stat block."""
    monster_name = arguments.get("monster_name", "").lower().replace(' ', '_').replace("'", "")
    
    # Try exact match first
    if monster_name in DATABASE["monsters"]:
        monster = DATABASE["monsters"][monster_name]
    else:
        # Try partial match
        matches = [m for m_id, m in DATABASE["monsters"].items() if monster_name in m_id or monster_name in m["name"].lower()]
        if matches:
            monster = matches[0]
        else:
            # Show available monsters starting with that letter
            suggestions = [m["name"] for m in DATABASE["monsters"].values() if m["name"].lower().startswith(monster_name[0] if monster_name else 'a')][:10]
            return [TextContent(type="text", text=f"Monster '{arguments.get('monster_name')}' not found. Suggestions: {', '.join(suggestions)}")]
    
    result = f"**{monster['name']}**\n"
    result += f"{monster['size']} {monster['type']}, {monster['alignment']}\n\n"
    result += f"**AC:** {monster['ac']}\n"
    result += f"**HP:** {monster['hp_average']} ({monster['hp']})\n"
    result += f"**Speed:** {', '.join([f'{k} {v} ft.' for k, v in monster['speed'].items()])}\n"
    result += f"**CR:** {monster['cr']}\n"
    result += f"**Source:** {monster['source']}\n"
    
    return [TextContent(type="text", text=result)]

async def handle_lookup_condition(arguments: dict) -> Sequence[TextContent]:
    """Look up a condition definition."""
    condition_name = arguments.get("condition_name", "").lower().replace(' ', '_')
    
    if condition_name in DATABASE["conditions"]:
        condition = DATABASE["conditions"][condition_name]
        
        result = f"**{condition['name']}** (Condition)\n\n"
        result += f"**Summary:** {condition['summary']}\n\n"
        result += "**Effects:**\n"
        for effect in condition["effects"]:
            result += f"- {effect}\n"
        result += f"\n**Ends When:** {condition['ends_when']}\n"
        result += f"\n**Full Text:**\n{condition['full_text']}\n"
        result += f"\n**Source:** {condition['source']}"
        
        return [TextContent(type="text", text=result)]
    else:
        return [TextContent(type="text", text=f"Condition '{arguments.get('condition_name')}' not found in database.")]

async def handle_lookup_action(arguments: dict) -> Sequence[TextContent]:
    """Look up an action description."""
    action_name = arguments.get("action_name", "").lower().replace(' ', '_')
    
    if action_name in DATABASE["actions"]:
        action = DATABASE["actions"][action_name]
        
        result = f"**{action['name']}** ({action['action_type']})\n\n"
        result += f"**Summary:** {action['summary']}\n\n"
        result += f"**Full Text:**\n{action['full_text']}\n"
        result += f"\n**Source:** {action['source']}"
        
        return [TextContent(type="text", text=result)]
    else:
        return [TextContent(type="text", text=f"Action '{arguments.get('action_name')}' not found in database.")]

async def handle_search_monsters(arguments: dict) -> Sequence[TextContent]:
    """Search for monsters with improved multi-word matching."""
    query = arguments.get("query", "").lower()
    max_results = arguments.get("max_results", 10)
    
    # Split query into individual words for better partial matching
    query_words = query.split()
    
    matches = []
    for monster in DATABASE["monsters"].values():
        monster_name_lower = monster["name"].lower()
        monster_type_lower = monster["type"].lower()
        
        # Check if query matches as a phrase (best match)
        if query in monster_name_lower or query in monster_type_lower:
            matches.append((monster, 3))  # Priority 3: exact phrase match
        # Check if all query words appear in monster name (good match)
        elif all(word in monster_name_lower for word in query_words):
            matches.append((monster, 2))  # Priority 2: all words present
        # Check if any query word matches (weak match)
        elif any(word in monster_name_lower or word in monster_type_lower for word in query_words):
            matches.append((monster, 1))  # Priority 1: partial match
        # Check keywords as fallback
        elif any(any(word in kw for word in query_words) for kw in monster.get("keywords", [])):
            matches.append((monster, 1))  # Priority 1: keyword match
    
    # Sort by priority (highest first), then by name
    matches.sort(key=lambda x: (-x[1], x[0]["name"]))
    
    # Take only the monsters (remove priority scores) and limit results
    matches = [m[0] for m in matches[:max_results]]
    
    if matches:
        result = f"**Found {len(matches)} monster(s) matching '{arguments.get('query')}':**\n\n"
        for monster in matches:
            result += f"- **{monster['name']}** ({monster['size']} {monster['type']}, CR {monster['cr']})\n"
        return [TextContent(type="text", text=result)]
    else:
        return [TextContent(type="text", text=f"No monsters found matching '{arguments.get('query')}'.")]

async def handle_search_rules(arguments: dict) -> Sequence[TextContent]:
    """Search for rules."""
    query = arguments.get("query", "").lower()
    max_results = arguments.get("max_results", 5)
    
    matches = []
    for rule in DATABASE["rules"].values():
        if (query in rule["name"].lower() or
            any(query in kw for kw in rule.get("keywords", []))):
            matches.append(rule)
        
        if len(matches) >= max_results:
            break
    
    if matches:
        result = f"**Found {len(matches)} rule(s) matching '{arguments.get('query')}':**\n\n"
        for rule in matches:
            result += f"- **{rule['name']}**: {rule['summary']}\n"
        return [TextContent(type="text", text=result)]
    else:
        return [TextContent(type="text", text=f"No rules found matching '{arguments.get('query')}'.")]

async def handle_lookup_spell(arguments: dict) -> Sequence[TextContent]:
    """Look up a specific spell."""
    spell_name = arguments.get("spell_name", "").lower().replace(' ', '_').replace("'", "")
    
    if spell_name in DATABASE["spells"]:
        spell = DATABASE["spells"][spell_name]
        
        level_str = "Cantrip" if spell["level"] == 0 else f"Level {spell['level']}"
        
        result = f"**{spell['name']}**\n"
        result += f"{level_str} {spell['school']}\n\n"
        result += f"**Classes:** {', '.join(spell['classes'])}\n"
        
        components = []
        if spell.get("concentration"):
            components.append("Concentration")
        if spell.get("ritual"):
            components.append("Ritual")
        if spell.get("material"):
            components.append("Material")
        
        if components:
            result += f"**Special:** {', '.join(components)}\n"
        
        result += f"\n**Source:** {spell['source']}"
        
        return [TextContent(type="text", text=result)]
    else:
        # Try partial match
        matches = [s for s_id, s in DATABASE["spells"].items() if spell_name in s["name"].lower()]
        if matches:
            suggestions = [s["name"] for s in matches[:5]]
            return [TextContent(type="text", text=f"Spell '{arguments.get('spell_name')}' not found. Did you mean: {', '.join(suggestions)}?")]
        return [TextContent(type="text", text=f"Spell '{arguments.get('spell_name')}' not found in database.")]

async def handle_search_spells(arguments: dict) -> Sequence[TextContent]:
    """Search for spells with optional filters."""
    query = arguments.get("query", "").lower()
    spell_class = arguments.get("spell_class", "").lower()
    spell_level = arguments.get("spell_level")
    school = arguments.get("school", "").lower()
    max_results = arguments.get("max_results", 10)
    
    matches = []
    for spell in DATABASE["spells"].values():
        # Apply filters
        if spell_class and spell_class not in [c.lower() for c in spell["classes"]]:
            continue
        if spell_level is not None and spell["level"] != spell_level:
            continue
        if school and school not in spell["school"].lower():
            continue
        
        # Check query match
        if (query in spell["name"].lower() or
            query in spell["school"].lower() or
            any(query in c.lower() for c in spell["classes"]) or
            any(query in kw for kw in spell.get("keywords", []))):
            matches.append(spell)
        
        if len(matches) >= max_results:
            break
    
    if matches:
        result = f"**Found {len(matches)} spell(s) matching '{arguments.get('query')}':**\n\n"
        for spell in matches:
            level_str = "Cantrip" if spell["level"] == 0 else f"L{spell['level']}"
            result += f"- **{spell['name']}** ({level_str} {spell['school']}) - {', '.join(spell['classes'])}\n"
        return [TextContent(type="text", text=result)]
    else:
        return [TextContent(type="text", text=f"No spells found matching your criteria.")]

async def handle_get_spells_by_class(arguments: dict) -> Sequence[TextContent]:
    """Get all spells for a specific class."""
    spell_class = arguments.get("spell_class", "").title()
    spell_level = arguments.get("spell_level")
    
    # Filter spells by class
    class_spells = [s for s in DATABASE["spells"].values() if spell_class in s["classes"]]
    
    if spell_level is not None:
        class_spells = [s for s in class_spells if s["level"] == spell_level]
    
    if not class_spells:
        return [TextContent(type="text", text=f"No spells found for {spell_class}" + (f" at level {spell_level}" if spell_level is not None else "") + ".")]
    
    # Organize by level
    by_level = {}
    for spell in class_spells:
        level = spell["level"]
        if level not in by_level:
            by_level[level] = []
        by_level[level].append(spell)
    
    # Sort each level alphabetically
    for level in by_level:
        by_level[level].sort(key=lambda s: s["name"])
    
    result = f"**{spell_class} Spells**"
    if spell_level is not None:
        result += f" (Level {spell_level})"
    result += f"\n\nTotal: {len(class_spells)} spells\n\n"
    
    for level in sorted(by_level.keys()):
        level_str = "Cantrips (Level 0)" if level == 0 else f"Level {level} Spells"
        result += f"**{level_str}** ({len(by_level[level])} spells):\n"
        for spell in by_level[level]:
            result += f"- {spell['name']} ({spell['school']})"
            if spell.get("concentration"):
                result += " [C]"
            if spell.get("ritual"):
                result += " [R]"
            result += "\n"
        result += "\n"
    
    return [TextContent(type="text", text=result)]

async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


