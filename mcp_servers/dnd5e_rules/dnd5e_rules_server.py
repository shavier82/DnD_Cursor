#!/usr/bin/env python3
"""
D&D 5e Rules Database MCP Server
Provides instant lookup for spells, monsters, items, conditions, and features
Uses the D&D 5e API (https://www.dnd5eapi.co/)
"""

import json
import logging
from typing import Dict, List, Any, Optional
import sys
from pathlib import Path
import asyncio
import aiohttp

# Add parent directory to path for MCP imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    import mcp.server.stdio
except ImportError:
    print("Error: MCP package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)


class DnD5eRulesServer:
    """MCP Server for D&D 5e rules lookup"""
    
    API_BASE_URL = "https://www.dnd5eapi.co/api"
    
    def __init__(self):
        self.server = Server("dnd5e-rules")
        
        # Setup logging (minimal output)
        logging.basicConfig(
            level=logging.WARNING,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        # Suppress verbose MCP library logs
        logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.ERROR)
        logging.getLogger("mcp").setLevel(logging.ERROR)
        
        self.logger = logging.getLogger("DnD5eRules")
        self.logger.setLevel(logging.WARNING)
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register all rules lookup tools"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="lookup_spell",
                    description="Look up a D&D 5e spell by name. Returns full spell details including level, school, casting time, range, components, duration, and description.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "spell_name": {
                                "type": "string",
                                "description": "Name of the spell to look up (e.g., 'Fireball', 'Cure Wounds')"
                            }
                        },
                        "required": ["spell_name"]
                    }
                ),
                Tool(
                    name="lookup_monster",
                    description="Look up a D&D 5e monster by name. Returns full stat block including AC, HP, abilities, actions, and traits.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "monster_name": {
                                "type": "string",
                                "description": "Name of the monster to look up (e.g., 'Goblin', 'Ancient Red Dragon')"
                            }
                        },
                        "required": ["monster_name"]
                    }
                ),
                Tool(
                    name="lookup_condition",
                    description="Look up a D&D 5e condition by name. Returns full condition description and mechanical effects.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "condition_name": {
                                "type": "string",
                                "description": "Name of the condition to look up (e.g., 'Frightened', 'Poisoned', 'Paralyzed')"
                            }
                        },
                        "required": ["condition_name"]
                    }
                ),
                Tool(
                    name="lookup_magic_item",
                    description="Look up a D&D 5e magic item by name. Returns item description, rarity, and properties.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "item_name": {
                                "type": "string",
                                "description": "Name of the magic item to look up (e.g., 'Bag of Holding', 'Ring of Protection')"
                            }
                        },
                        "required": ["item_name"]
                    }
                ),
                Tool(
                    name="lookup_feature",
                    description="Look up a D&D 5e class feature by name. Returns feature description and mechanics.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "feature_name": {
                                "type": "string",
                                "description": "Name of the feature to look up (e.g., 'Rage', 'Sneak Attack', 'Wild Shape')"
                            }
                        },
                        "required": ["feature_name"]
                    }
                ),
                Tool(
                    name="search_spells",
                    description="Search for spells by level and/or school. Returns list of matching spells.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "level": {
                                "type": "integer",
                                "description": "Spell level (0-9, where 0 is cantrip)"
                            },
                            "school": {
                                "type": "string",
                                "description": "School of magic (e.g., 'Evocation', 'Conjuration', 'Abjuration')"
                            }
                        }
                    }
                ),
                Tool(
                    name="search_monsters",
                    description="Search for monsters by challenge rating. Returns list of matching monsters.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "challenge_rating": {
                                "type": "string",
                                "description": "Challenge rating (e.g., '0', '1', '5', '0.5', '0.25')"
                            }
                        },
                        "required": ["challenge_rating"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls"""
            
            if name == "lookup_spell":
                return await self._handle_lookup_spell(arguments)
            elif name == "lookup_monster":
                return await self._handle_lookup_monster(arguments)
            elif name == "lookup_condition":
                return await self._handle_lookup_condition(arguments)
            elif name == "lookup_magic_item":
                return await self._handle_lookup_magic_item(arguments)
            elif name == "lookup_feature":
                return await self._handle_lookup_feature(arguments)
            elif name == "search_spells":
                return await self._handle_search_spells(arguments)
            elif name == "search_monsters":
                return await self._handle_search_monsters(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def _api_get(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Make GET request to D&D 5e API"""
        url = f"{self.API_BASE_URL}/{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        return None
                    else:
                        self.logger.error(f"API error: {response.status} for {url}")
                        return None
        except Exception as e:
            self.logger.error(f"API request failed: {e}")
            return None
    
    def _format_spell(self, spell: Dict[str, Any]) -> str:
        """Format spell data for display"""
        output = f"📜 **{spell['name']}**\n"
        output += f"*Level {spell['level']} {spell['school']['name']}*\n\n"
        
        output += f"**Casting Time:** {spell['casting_time']}\n"
        output += f"**Range:** {spell['range']}\n"
        output += f"**Components:** {', '.join(spell['components'])}"
        if spell.get('material'):
            output += f" ({spell['material']})"
        output += "\n"
        output += f"**Duration:** {spell['duration']}\n\n"
        
        # Description
        for desc in spell.get('desc', []):
            output += f"{desc}\n\n"
        
        # Higher levels
        if spell.get('higher_level'):
            output += "**At Higher Levels:** "
            for hl in spell['higher_level']:
                output += f"{hl}\n"
        
        # Classes
        if spell.get('classes'):
            classes = [c['name'] for c in spell['classes']]
            output += f"\n**Classes:** {', '.join(classes)}\n"
        
        return output
    
    def _format_monster(self, monster: Dict[str, Any]) -> str:
        """Format monster stat block for display"""
        output = f"👹 **{monster['name']}**\n"
        output += f"*{monster['size']} {monster['type']}, {monster['alignment']}*\n\n"
        
        # Defensive stats
        output += f"**AC:** {monster['armor_class'][0]['value']}\n"
        output += f"**HP:** {monster['hit_points']} ({monster['hit_points_roll']})\n"
        output += f"**Speed:** {', '.join([f'{k} {v}' for k, v in monster['speed'].items()])}\n\n"
        
        # Ability scores
        output += "**STR** | **DEX** | **CON** | **INT** | **WIS** | **CHA**\n"
        output += f"{monster['strength']} ({self._ability_mod(monster['strength']):+d}) | "
        output += f"{monster['dexterity']} ({self._ability_mod(monster['dexterity']):+d}) | "
        output += f"{monster['constitution']} ({self._ability_mod(monster['constitution']):+d}) | "
        output += f"{monster['intelligence']} ({self._ability_mod(monster['intelligence']):+d}) | "
        output += f"{monster['wisdom']} ({self._ability_mod(monster['wisdom']):+d}) | "
        output += f"{monster['charisma']} ({self._ability_mod(monster['charisma']):+d})\n\n"
        
        # Proficiencies
        if monster.get('proficiencies'):
            saves = [p for p in monster['proficiencies'] if 'Saving Throw' in p['proficiency']['name']]
            skills = [p for p in monster['proficiencies'] if 'Skill' in p['proficiency']['name']]
            if saves:
                output += f"**Saving Throws:** {', '.join([f\"{p['proficiency']['name'].replace('Saving Throw: ', '')} {p['value']:+d}\" for p in saves])}\n"
            if skills:
                output += f"**Skills:** {', '.join([f\"{p['proficiency']['name'].replace('Skill: ', '')} {p['value']:+d}\" for p in skills])}\n"
        
        # Resistances/Immunities
        if monster.get('damage_resistances'):
            output += f"**Damage Resistances:** {', '.join(monster['damage_resistances'])}\n"
        if monster.get('damage_immunities'):
            output += f"**Damage Immunities:** {', '.join(monster['damage_immunities'])}\n"
        if monster.get('condition_immunities'):
            conditions = [c['name'] for c in monster['condition_immunities']]
            output += f"**Condition Immunities:** {', '.join(conditions)}\n"
        
        # Senses
        if monster.get('senses'):
            output += f"**Senses:** {', '.join([f'{k} {v}' for k, v in monster['senses'].items()])}\n"
        
        # Languages
        output += f"**Languages:** {monster.get('languages', '—')}\n"
        output += f"**Challenge:** {monster['challenge_rating']} ({monster['xp']:,} XP)\n\n"
        
        # Special abilities
        if monster.get('special_abilities'):
            output += "**Special Abilities:**\n"
            for ability in monster['special_abilities']:
                output += f"***{ability['name']}.*** {ability['desc']}\n\n"
        
        # Actions
        if monster.get('actions'):
            output += "**Actions:**\n"
            for action in monster['actions']:
                output += f"***{action['name']}.*** {action['desc']}\n\n"
        
        # Legendary actions
        if monster.get('legendary_actions'):
            output += f"**Legendary Actions ({monster.get('legendary_actions', [{}])[0].get('usage', 3)} per turn):**\n"
            for action in monster['legendary_actions']:
                output += f"***{action['name']}.*** {action['desc']}\n\n"
        
        return output
    
    def _ability_mod(self, score: int) -> int:
        """Calculate ability modifier from score"""
        return (score - 10) // 2
    
    def _format_condition(self, condition: Dict[str, Any]) -> str:
        """Format condition for display"""
        output = f"⚠️ **{condition['name']}**\n\n"
        
        for desc in condition.get('desc', []):
            output += f"{desc}\n\n"
        
        return output
    
    def _format_magic_item(self, item: Dict[str, Any]) -> str:
        """Format magic item for display"""
        output = f"✨ **{item['name']}**\n"
        
        if item.get('equipment_category'):
            output += f"*{item['equipment_category']['name']}*\n"
        
        if item.get('rarity'):
            output += f"**Rarity:** {item['rarity']['name']}\n"
        
        if item.get('desc'):
            output += "\n"
            for desc in item['desc']:
                output += f"{desc}\n\n"
        
        return output
    
    async def _handle_lookup_spell(self, arguments: dict) -> list[TextContent]:
        """Look up a spell"""
        spell_name = arguments["spell_name"].lower().replace(" ", "-")
        
        data = await self._api_get(f"spells/{spell_name}")
        
        if data is None:
            return [TextContent(
                type="text",
                text=f"❌ Spell '{arguments['spell_name']}' not found. Check spelling or try a search."
            )]
        
        return [TextContent(type="text", text=self._format_spell(data))]
    
    async def _handle_lookup_monster(self, arguments: dict) -> list[TextContent]:
        """Look up a monster"""
        monster_name = arguments["monster_name"].lower().replace(" ", "-")
        
        data = await self._api_get(f"monsters/{monster_name}")
        
        if data is None:
            return [TextContent(
                type="text",
                text=f"❌ Monster '{arguments['monster_name']}' not found. Check spelling or try a search."
            )]
        
        return [TextContent(type="text", text=self._format_monster(data))]
    
    async def _handle_lookup_condition(self, arguments: dict) -> list[TextContent]:
        """Look up a condition"""
        condition_name = arguments["condition_name"].lower().replace(" ", "-")
        
        data = await self._api_get(f"conditions/{condition_name}")
        
        if data is None:
            return [TextContent(
                type="text",
                text=f"❌ Condition '{arguments['condition_name']}' not found."
            )]
        
        return [TextContent(type="text", text=self._format_condition(data))]
    
    async def _handle_lookup_magic_item(self, arguments: dict) -> list[TextContent]:
        """Look up a magic item"""
        item_name = arguments["item_name"].lower().replace(" ", "-")
        
        data = await self._api_get(f"magic-items/{item_name}")
        
        if data is None:
            return [TextContent(
                type="text",
                text=f"❌ Magic item '{arguments['item_name']}' not found."
            )]
        
        return [TextContent(type="text", text=self._format_magic_item(data))]
    
    async def _handle_lookup_feature(self, arguments: dict) -> list[TextContent]:
        """Look up a class feature"""
        feature_name = arguments["feature_name"].lower().replace(" ", "-")
        
        data = await self._api_get(f"features/{feature_name}")
        
        if data is None:
            return [TextContent(
                type="text",
                text=f"❌ Feature '{arguments['feature_name']}' not found."
            )]
        
        output = f"⚡ **{data['name']}**\n"
        if data.get('class'):
            output += f"*{data['class']['name']} - Level {data['level']}*\n\n"
        
        for desc in data.get('desc', []):
            output += f"{desc}\n\n"
        
        return [TextContent(type="text", text=output)]
    
    async def _handle_search_spells(self, arguments: dict) -> list[TextContent]:
        """Search for spells"""
        # Get all spells first
        data = await self._api_get("spells")
        
        if data is None:
            return [TextContent(type="text", text="❌ Failed to retrieve spell list.")]
        
        results = data.get('results', [])
        
        # Filter by level if provided
        if 'level' in arguments:
            level = arguments['level']
            # Fetch each spell's details to filter by level
            filtered = []
            for spell in results[:50]:  # Limit to avoid too many requests
                spell_data = await self._api_get(f"spells/{spell['index']}")
                if spell_data and spell_data['level'] == level:
                    filtered.append(spell_data['name'])
            
            output = f"📜 **Level {level} Spells:**\n"
            output += "\n".join([f"- {name}" for name in filtered[:20]])  # Limit results
            if len(filtered) > 20:
                output += f"\n\n*...and {len(filtered) - 20} more*"
        else:
            output = f"📜 **All Spells ({len(results)}):**\n"
            output += "\n".join([f"- {s['name']}" for s in results[:30]])
            if len(results) > 30:
                output += f"\n\n*...and {len(results) - 30} more*"
        
        return [TextContent(type="text", text=output)]
    
    async def _handle_search_monsters(self, arguments: dict) -> list[TextContent]:
        """Search for monsters by CR"""
        cr = arguments["challenge_rating"]
        
        # Get all monsters
        data = await self._api_get("monsters")
        
        if data is None:
            return [TextContent(type="text", text="❌ Failed to retrieve monster list.")]
        
        results = data.get('results', [])
        
        # Filter by CR
        filtered = []
        for monster in results:
            monster_data = await self._api_get(f"monsters/{monster['index']}")
            if monster_data and str(monster_data['challenge_rating']) == cr:
                filtered.append(monster_data['name'])
        
        output = f"👹 **CR {cr} Monsters:**\n"
        if filtered:
            output += "\n".join([f"- {name}" for name in filtered])
        else:
            output += "No monsters found with this CR."
        
        return [TextContent(type="text", text=output)]
    
    async def run(self):
        """Run the MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


if __name__ == "__main__":
    server = DnD5eRulesServer()
    import asyncio
    asyncio.run(server.run())














