#!/usr/bin/env python3
"""
Travel Manager MCP Server for D&D Campaigns
Automatically deducts rations and water during travel.
"""

import sys
import json
import re
import random
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    from mcp.server.stdio import stdio_server
except ImportError:
    print("ERROR: mcp package not found. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)


class TravelManagerServer:
    def __init__(self):
        self.vault_path = Path("C:/Users/ksist/Documents/Obsidian/DnD/Player Characters")
        
    def read_character_file(self, character_name: str) -> Optional[str]:
        """Read character file from Obsidian vault."""
        file_path = self.vault_path / f"{character_name}.md"
        if not file_path.exists():
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return None
    
    def write_character_file(self, character_name: str, content: str) -> bool:
        """Write character file to Obsidian vault."""
        file_path = self.vault_path / f"{character_name}.md"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            return False
    
    def update_rations(self, character_name: str, days: int) -> dict:
        """Deduct rations for travel days."""
        content = self.read_character_file(character_name)
        if not content:
            return {"error": f"Character file not found: {character_name}"}
        
        lines = content.split('\n')
        modified = False
        found_rations = False
        
        # Find and update rations in inventory table
        in_inventory = False
        header_passed = False
        for i, line in enumerate(lines):
            # Look for inventory section
            if "### General Inventory" in line or "## Equipment & Inventory" in line:
                in_inventory = True
                header_passed = False
                continue
            
            # Check if we've left the inventory section
            if in_inventory and line.startswith("##") and "Inventory" not in line and "Equipment" not in line:
                break
            
            # Skip header row and separator row
            if in_inventory and line.strip().startswith("|"):
                if "Item" in line and "Quantity" in line:
                    header_passed = True
                    continue
                if line.strip().startswith("|---"):
                    continue
                
                # Look for rations row in table (after header)
                if header_passed and "Rations" in line:
                    found_rations = True
                    # Parse the table row: | Item | Quantity | Weight (lb) | Notes |
                    # Split by | and strip each part
                    parts = [p.strip() for p in line.split('|')]
                    # Remove empty first and last elements from split (before first | and after last |)
                    if parts and not parts[0]:
                        parts = parts[1:]
                    if parts and not parts[-1]:
                        parts = parts[:-1]
                    
                    if len(parts) >= 2:
                        try:
                            # Column structure: Item | Quantity | Weight (lb) | Notes
                            item_col = 0
                            qty_col = 1
                            weight_col = 2 if len(parts) > 2 else -1
                            
                            # Check if first column contains "Rations"
                            if "Rations" in parts[item_col]:
                                # Parse quantity (should be a number)
                                qty_str = parts[qty_col].strip()
                                qty_match = re.search(r'(\d+)', qty_str)
                                if qty_match:
                                    current_qty = int(qty_match.group(1))
                                    new_qty = max(0, current_qty - days)
                                    
                                    # Update quantity column
                                    parts[qty_col] = str(new_qty)
                                    
                                    # Update weight if present (rations are 2 lb per day)
                                    if weight_col >= 0 and weight_col < len(parts):
                                        weight_str = parts[weight_col].strip()
                                        weight_match = re.search(r'(\d+\.?\d*)', weight_str)
                                        if weight_match:
                                            current_weight = float(weight_match.group(1))
                                            new_weight = max(0, current_weight - (days * 2))
                                            parts[weight_col] = f"{new_weight:.1f}"
                                    
                                    # Reconstruct the line with proper formatting
                                    new_line = "| " + " | ".join(parts) + " |"
                                    lines[i] = new_line
                                    modified = True
                                    break
                        except (ValueError, IndexError, AttributeError) as e:
                            # Try alternative parsing
                            pass
        
        if modified:
            new_content = '\n'.join(lines)
            self.write_character_file(character_name, new_content)
            return {
                "success": True,
                "character": character_name,
                "days": days,
                "rations_deducted": days
            }
        elif not found_rations:
            return {
                "success": False,
                "error": "Could not find rations in inventory table",
                "character": character_name
            }
        else:
            return {
                "success": False,
                "error": "Could not parse rations quantity",
                "character": character_name
            }
    
    def get_encounter_table(self, biome: str, terrain: str, time_of_day: str) -> dict:
        """
        Get the appropriate encounter table based on biome, terrain, and time of day.
        
        Returns a dict with:
        - table_name: Name of the encounter table
        - encounters: Dict mapping roll ranges to encounter descriptions
        - day_only: List of rolls that only occur during day
        - night_only: List of rolls that only occur at night
        """
        biome_lower = biome.lower()
        terrain_lower = terrain.lower()
        time_lower = time_of_day.lower()
        
        # Underground/Tunnel Network encounters
        if terrain_lower in ["underground", "tunnel", "cave", "dungeon"]:
            return {
                "table_name": "Tunnel Network Encounters",
                "encounters": {
                    (1, 2): {"description": "1d4 + 1 goblin scouts (patrol)", "roll": "1d4+1", "type": "goblin"},
                    (3, 4): {"description": "1d3 goblin psi brawlers (patrol)", "roll": "1d3", "type": "goblin_psi"},
                    (5, 6): {"description": "1d4 + 2 giant rats", "roll": "1d4+2", "type": "beast"},
                    (7, 8): {"description": "1d3 giant spiders", "roll": "1d3", "type": "beast"},
                    (9, 9): {"description": "1d2 carrion crawlers", "roll": "1d2", "type": "monster"},
                    (10, 10): {"description": "1 gelatinous cube", "roll": "1", "type": "ooze"},
                    (11, 11): {"description": "1d4 + 1 stirges", "roll": "1d4+1", "type": "beast"},
                    (12, 12): {"description": "1d2 ochre jellies", "roll": "1d2", "type": "ooze"}
                },
                "day_only": [],
                "night_only": []
            }
        
        # Forest encounters
        elif biome_lower in ["forest", "woodland", "woods"]:
            return {
                "table_name": "Forest Encounters",
                "encounters": {
                    (1, 2): {"description": "1d4 + 2 stirges", "roll": "1d4+2", "type": "beast"},
                    (3, 4): {"description": "1d4 + 2 wolves", "roll": "1d4+2", "type": "beast"},
                    (5, 6): {"description": "1d3 + 1 goblins", "roll": "1d3+1", "type": "goblin"},
                    (7, 8): {"description": "1d2 + 1 hobgoblins", "roll": "1d2+1", "type": "hobgoblin"},
                    (9, 10): {"description": "1d2 bugbears", "roll": "1d2", "type": "bugbear"},
                    (11, 11): {"description": "1 owlbear", "roll": "1", "type": "beast"},
                    (12, 12): {"description": "1d2 + 1 bandits", "roll": "1d2+1", "type": "humanoid"}
                },
                "day_only": [11],  # Owlbear only during day
                "night_only": []
            }
        
        # Plains/Grassland encounters
        elif biome_lower in ["plains", "grassland", "prairie"]:
            return {
                "table_name": "Plains Encounters",
                "encounters": {
                    (1, 2): {"description": "1d4 + 2 wolves", "roll": "1d4+2", "type": "beast"},
                    (3, 4): {"description": "1d3 + 1 goblins", "roll": "1d3+1", "type": "goblin"},
                    (5, 6): {"description": "1d2 + 1 hobgoblins", "roll": "1d2+1", "type": "hobgoblin"},
                    (7, 8): {"description": "1d4 + 1 bandits", "roll": "1d4+1", "type": "humanoid"},
                    (9, 10): {"description": "1d2 + 1 orcs", "roll": "1d2+1", "type": "orc"},
                    (11, 11): {"description": "1 ogre", "roll": "1", "type": "giant"},
                    (12, 12): {"description": "1d3 + 1 gnolls", "roll": "1d3+1", "type": "gnoll"}
                },
                "day_only": [11],  # Ogre only during day
                "night_only": []
            }
        
        # Mountain encounters
        elif biome_lower in ["mountain", "hills", "hill"]:
            return {
                "table_name": "Mountain Encounters",
                "encounters": {
                    (1, 2): {"description": "1d4 + 1 goblins", "roll": "1d4+1", "type": "goblin"},
                    (3, 4): {"description": "1d2 + 1 hobgoblins", "roll": "1d2+1", "type": "hobgoblin"},
                    (5, 6): {"description": "1d2 bugbears", "roll": "1d2", "type": "bugbear"},
                    (7, 8): {"description": "1d3 + 1 orcs", "roll": "1d3+1", "type": "orc"},
                    (9, 10): {"description": "1d2 + 1 bandits", "roll": "1d2+1", "type": "humanoid"},
                    (11, 11): {"description": "1 ogre", "roll": "1", "type": "giant"},
                    (12, 12): {"description": "1d2 + 1 harpies", "roll": "1d2+1", "type": "monster"}
                },
                "day_only": [11],  # Ogre only during day
                "night_only": []
            }
        
        # Default: Triboar Trail (from Lost Mine of Phandelver)
        else:
            return {
                "table_name": "Triboar Trail Encounters",
                "encounters": {
                    (1, 2): {"description": "1d4 + 2 stirges", "roll": "1d4+2", "type": "beast"},
                    (3, 4): {"description": "1 ogre", "roll": "1", "type": "giant"},
                    (5, 6): {"description": "Cragmaw goblin band (2d4 goblins + 1 goblin boss)", "roll": "2d4+1", "type": "goblin"},
                    (7, 8): {"description": "Hobgoblin squad (1d4 + 3 hobgoblins)", "roll": "1d4+3", "type": "hobgoblin"},
                    (9, 10): {"description": "Bugbear scouts (2 bugbears)", "roll": "2", "type": "bugbear"},
                    (11, 11): {"description": "1d4 + 2 wolves", "roll": "1d4+2", "type": "beast"},
                    (12, 12): {"description": "1 owlbear", "roll": "1", "type": "beast"}
                },
                "day_only": [3, 4],  # Ogre only during day
                "night_only": [4]  # Ghouls only at night (not in this table, but structure supports it)
            }
    
    def roll_dice_expression(self, expression: str) -> int:
        """Parse and roll a dice expression like '1d4+2' or '2d6'."""
        try:
            # Handle formats like "1d4+2", "2d6", "1d3+1"
            if "+" in expression:
                dice_part, modifier = expression.split("+")
                num_dice, die_size = map(int, dice_part.split("d"))
                return sum(random.randint(1, die_size) for _ in range(num_dice)) + int(modifier)
            elif "-" in expression:
                dice_part, modifier = expression.split("-")
                num_dice, die_size = map(int, dice_part.split("d"))
                return sum(random.randint(1, die_size) for _ in range(num_dice)) - int(modifier)
            else:
                # Just a number or dice expression
                if "d" in expression:
                    num_dice, die_size = map(int, expression.split("d"))
                    return sum(random.randint(1, die_size) for _ in range(num_dice))
                else:
                    return int(expression)
        except:
            return 1
    
    def check_random_encounter(self, biome: str, terrain: str, time_of_day: str) -> dict:
        """
        Check for a random encounter during travel.
        
        Args:
            biome: Biome type (forest, plains, mountain, etc.)
            terrain: Terrain type (overland, underground, tunnel, etc.)
            time_of_day: "day" or "night"
        
        Returns:
            Dict with encounter details or None if no encounter
        """
        # Roll 1d20 to check if encounter occurs (17-20 triggers)
        encounter_check = random.randint(1, 20)
        
        if encounter_check < 17:
            return {
                "encounter_occurred": False,
                "encounter_check_roll": encounter_check,
                "message": "No encounter - travel continues uneventfully"
            }
        
        # Encounter occurred - get the appropriate table
        encounter_table = self.get_encounter_table(biome, terrain, time_of_day)
        
        # Roll 1d12 to determine encounter type
        encounter_roll = random.randint(1, 12)
        
        # Check if this roll is valid for the time of day
        time_lower = time_of_day.lower()
        day_only = encounter_table.get("day_only", [])
        night_only = encounter_table.get("night_only", [])
        
        # If roll is day-only but it's night, or night-only but it's day, re-roll
        if (encounter_roll in day_only and time_lower != "day") or \
           (encounter_roll in night_only and time_lower != "night"):
            # Re-roll to get a valid encounter for this time of day
            max_attempts = 10
            for _ in range(max_attempts):
                encounter_roll = random.randint(1, 12)
                if not ((encounter_roll in day_only and time_lower != "day") or 
                        (encounter_roll in night_only and time_lower != "night")):
                    break
        
        # Find the encounter for this roll
        encounter_details = None
        for (min_roll, max_roll), details in encounter_table["encounters"].items():
            if min_roll <= encounter_roll <= max_roll:
                encounter_details = details.copy()
                encounter_details["roll_range"] = (min_roll, max_roll)
                break
        
        if not encounter_details:
            return {
                "encounter_occurred": False,
                "encounter_check_roll": encounter_check,
                "encounter_roll": encounter_roll,
                "error": "Could not find encounter for roll"
            }
        
        # Roll for actual quantities
        quantity_roll = self.roll_dice_expression(encounter_details["roll"])
        encounter_details["quantity"] = quantity_roll
        
        return {
            "encounter_occurred": True,
            "encounter_check_roll": encounter_check,
            "encounter_roll": encounter_roll,
            "biome": biome,
            "terrain": terrain,
            "time_of_day": time_of_day,
            "table_name": encounter_table["table_name"],
            "encounter": encounter_details
        }
    
    def process_travel(self, party_members: List[str], days: int, travel_type: str = "overland") -> dict:
        """
        Process travel and automatically deduct rations/water for all party members.
        
        Args:
            party_members: List of character names (format: "FirstName_LastName")
            days: Number of days traveled
            travel_type: "overland" or "underground" (affects water availability)
        """
        results = []
        errors = []
        
        for character_name in party_members:
            # Deduct rations (1 per day per person)
            ration_result = self.update_rations(character_name, days)
            results.append(ration_result)
            
            if not ration_result.get("success"):
                errors.append(f"{character_name}: {ration_result.get('error', 'Unknown error')}")
        
        # Water handling: Overland travel may have water sources, underground might not
        # For now, we'll note water consumption but not auto-deduct (waterskins can be refilled)
        water_note = ""
        if travel_type == "underground":
            water_note = "Note: Waterskins may need refilling from underground sources."
        elif travel_type == "overland":
            water_note = "Note: Waterskins can be refilled from streams/rivers."
        
        return {
            "success": len(errors) == 0,
            "days_traveled": days,
            "travel_type": travel_type,
            "party_members": party_members,
            "results": results,
            "errors": errors,
            "water_note": water_note,
            "rations_per_person": days,
            "total_rations_consumed": days * len(party_members)
        }


# Initialize MCP server
app = Server("travel-manager")
server = TravelManagerServer()


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="process_travel",
            description="Process travel and automatically deduct rations for all party members. Deducts 1 ration per day per person.",
            inputSchema={
                "type": "object",
                "properties": {
                    "party_members": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of character names (format: 'FirstName_LastName')"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days traveled"
                    },
                    "travel_type": {
                        "type": "string",
                        "enum": ["overland", "underground"],
                        "description": "Type of travel (affects water availability notes)",
                        "default": "overland"
                    }
                },
                "required": ["party_members", "days"]
            }
        ),
        Tool(
            name="update_rations",
            description="Deduct rations for a single character (for manual adjustments)",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {
                        "type": "string",
                        "description": "Character name (format: 'FirstName_LastName')"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days of rations to deduct"
                    }
                },
                "required": ["character_name", "days"]
            }
        ),
        Tool(
            name="check_random_encounter",
            description="Roll for random encounters during travel. Checks if encounter occurs (1d20, 17-20 triggers) and determines which enemies based on biome, terrain, and time of day.",
            inputSchema={
                "type": "object",
                "properties": {
                    "biome": {
                        "type": "string",
                        "description": "Biome type: forest, plains, mountain, hills, grassland, etc. (default: 'plains')",
                        "default": "plains"
                    },
                    "terrain": {
                        "type": "string",
                        "description": "Terrain type: overland, underground, tunnel, cave, dungeon, etc. (default: 'overland')",
                        "default": "overland"
                    },
                    "time_of_day": {
                        "type": "string",
                        "enum": ["day", "night"],
                        "description": "Time of day (affects which encounters can occur)",
                        "default": "day"
                    }
                },
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "process_travel":
            result = server.process_travel(
                arguments["party_members"],
                arguments["days"],
                arguments.get("travel_type", "overland")
            )
        elif name == "update_rations":
            result = server.update_rations(
                arguments["character_name"],
                arguments["days"]
            )
        elif name == "check_random_encounter":
            result = server.check_random_encounter(
                arguments.get("biome", "plains"),
                arguments.get("terrain", "overland"),
                arguments.get("time_of_day", "day")
            )
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]


async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
