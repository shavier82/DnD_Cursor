#!/usr/bin/env python3
"""
True Random Dice Roller MCP Server
Provides cryptographically secure dice rolling with audit trails for D&D campaigns.
"""

import sys
import json
import secrets
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
except ImportError:
    print("ERROR: mcp package not found. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Audit log path
AUDIT_LOG_PATH = Path(__file__).parent / "dice_rolls_audit.jsonl"

# Initialize MCP server
app = Server("dice-roller")


def secure_roll(sides: int) -> int:
    """
    Roll a single die with cryptographically secure randomness.
    
    Args:
        sides: Number of sides on the die
        
    Returns:
        Random number between 1 and sides (inclusive)
    """
    return secrets.randbelow(sides) + 1


def parse_dice_expression(expression: str) -> tuple[int, int, int]:
    """
    Parse a dice expression like "2d6+3" into components.
    
    Args:
        expression: Dice expression (e.g., "2d6+3", "1d20", "4d8-2")
        
    Returns:
        Tuple of (num_dice, die_sides, modifier)
        
    Raises:
        ValueError: If expression is invalid
    """
    # Remove spaces
    expression = expression.replace(" ", "").lower()
    
    # Match patterns like "2d6+3", "1d20", "d20+5", "3d8-2"
    match = re.match(r'^(\d*)d(\d+)([+-]\d+)?$', expression)
    if not match:
        raise ValueError(f"Invalid dice expression: {expression}")
    
    num_dice = int(match.group(1)) if match.group(1) else 1
    die_sides = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0
    
    if num_dice < 1 or num_dice > 100:
        raise ValueError("Number of dice must be between 1 and 100")
    if die_sides < 2 or die_sides > 100:
        raise ValueError("Die sides must be between 2 and 100")
    
    return num_dice, die_sides, modifier


def log_roll(roll_data: Dict[str, Any]) -> None:
    """
    Log a roll to the audit trail.
    
    Args:
        roll_data: Dictionary containing roll details
    """
    roll_data["timestamp"] = datetime.utcnow().isoformat() + "Z"
    
    try:
        with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(roll_data) + "\n")
    except Exception as e:
        print(f"Warning: Failed to log roll: {e}", file=sys.stderr)


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available dice rolling tools."""
    return [
        Tool(
            name="roll_dice",
            description="Roll dice with cryptographically secure randomness. Supports standard notation like '2d6+3', '1d20', '4d8-2'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dice_expression": {
                        "type": "string",
                        "description": "Dice expression in format NdX+modifier (e.g., '2d6+3', '1d20', '4d8-2')"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the roll (for audit trail)"
                    },
                    "character": {
                        "type": "string",
                        "description": "Character making the roll (optional)"
                    }
                },
                "required": ["dice_expression", "reason"]
            }
        ),
        Tool(
            name="roll_attack",
            description="Roll an attack (1d20 + modifier) with advantage, disadvantage, or normal.",
            inputSchema={
                "type": "object",
                "properties": {
                    "modifier": {
                        "type": "integer",
                        "description": "Attack modifier to add to the roll"
                    },
                    "character": {
                        "type": "string",
                        "description": "Character making the attack"
                    },
                    "weapon": {
                        "type": "string",
                        "description": "Weapon being used (optional)"
                    },
                    "advantage": {
                        "type": "boolean",
                        "description": "Roll with advantage (roll twice, take higher)"
                    },
                    "disadvantage": {
                        "type": "boolean",
                        "description": "Roll with disadvantage (roll twice, take lower)"
                    },
                    "target_ac": {
                        "type": "integer",
                        "description": "Target AC for hit/miss determination (optional)"
                    }
                },
                "required": ["modifier", "character"]
            }
        ),
        Tool(
            name="roll_initiative",
            description="Roll initiative for one or more combatants.",
            inputSchema={
                "type": "object",
                "properties": {
                    "combatants": {
                        "type": "array",
                        "description": "Array of combatants to roll initiative for",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Combatant name"
                                },
                                "modifier": {
                                    "type": "integer",
                                    "description": "Initiative modifier"
                                },
                                "advantage": {
                                    "type": "boolean",
                                    "description": "Roll with advantage (optional)"
                                }
                            },
                            "required": ["name", "modifier"]
                        }
                    }
                },
                "required": ["combatants"]
            }
        ),
        Tool(
            name="roll_saving_throw",
            description="Roll a saving throw (1d20 + modifier) against a DC.",
            inputSchema={
                "type": "object",
                "properties": {
                    "modifier": {
                        "type": "integer",
                        "description": "Saving throw modifier"
                    },
                    "dc": {
                        "type": "integer",
                        "description": "Difficulty Class"
                    },
                    "ability": {
                        "type": "string",
                        "description": "Ability being saved (e.g., 'Dexterity', 'Constitution')"
                    },
                    "character": {
                        "type": "string",
                        "description": "Character making the save"
                    },
                    "advantage": {
                        "type": "boolean",
                        "description": "Roll with advantage"
                    },
                    "disadvantage": {
                        "type": "boolean",
                        "description": "Roll with disadvantage"
                    }
                },
                "required": ["modifier", "dc", "ability", "character"]
            }
        ),
        Tool(
            name="get_roll_history",
            description="Retrieve recent roll history from audit log.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of recent rolls to retrieve (default: 10)"
                    },
                    "character": {
                        "type": "string",
                        "description": "Filter by character name (optional)"
                    }
                }
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    
    if name == "roll_dice":
        dice_expr = arguments["dice_expression"]
        reason = arguments["reason"]
        character = arguments.get("character", "Unknown")
        
        try:
            num_dice, die_sides, modifier = parse_dice_expression(dice_expr)
            
            # Roll the dice
            rolls = [secure_roll(die_sides) for _ in range(num_dice)]
            roll_sum = sum(rolls)
            total = roll_sum + modifier
            
            # Log the roll
            log_roll({
                "type": "dice_roll",
                "character": character,
                "expression": dice_expr,
                "num_dice": num_dice,
                "die_sides": die_sides,
                "rolls": rolls,
                "roll_sum": roll_sum,
                "modifier": modifier,
                "total": total,
                "reason": reason
            })
            
            # Format output
            rolls_str = ", ".join(str(r) for r in rolls)
            result = f"🎲 Dice Roll: {dice_expr}\n"
            result += f"Reason: {reason}\n"
            if character != "Unknown":
                result += f"Character: {character}\n"
            result += f"Rolls: [{rolls_str}]\n"
            if modifier != 0:
                result += f"Modifier: {modifier:+d}\n"
            result += f"**Total: {total}**"
            
            return [TextContent(type="text", text=result)]
            
        except ValueError as e:
            return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
    
    elif name == "roll_attack":
        modifier = arguments["modifier"]
        character = arguments["character"]
        weapon = arguments.get("weapon", "weapon")
        advantage = arguments.get("advantage", False)
        disadvantage = arguments.get("disadvantage", False)
        target_ac = arguments.get("target_ac")
        
        # Roll attack
        if advantage and disadvantage:
            # Cancel out to normal roll
            roll = secure_roll(20)
            rolls = [roll]
        elif advantage:
            rolls = [secure_roll(20), secure_roll(20)]
            roll = max(rolls)
        elif disadvantage:
            rolls = [secure_roll(20), secure_roll(20)]
            roll = min(rolls)
        else:
            roll = secure_roll(20)
            rolls = [roll]
        
        total = roll + modifier
        is_crit = (roll == 20)
        is_fumble = (roll == 1)
        
        # Determine hit/miss
        result_text = ""
        if target_ac is not None:
            if is_crit:
                result_text = "CRITICAL HIT!"
            elif is_fumble:
                result_text = "CRITICAL MISS!"
            elif total >= target_ac:
                result_text = "HIT!"
            else:
                result_text = "MISS!"
        
        # Log the roll
        log_roll({
            "type": "attack_roll",
            "character": character,
            "weapon": weapon,
            "roll": roll,
            "rolls": rolls,
            "modifier": modifier,
            "total": total,
            "advantage": advantage,
            "disadvantage": disadvantage,
            "target_ac": target_ac,
            "result": result_text,
            "is_crit": is_crit,
            "is_fumble": is_fumble
        })
        
        # Format output
        output = f"⚔️ Attack Roll: {character}"
        if weapon != "weapon":
            output += f" with {weapon}"
        output += "\n"
        
        if len(rolls) > 1:
            rolls_str = ", ".join(str(r) for r in rolls)
            adv_text = "Advantage" if advantage else "Disadvantage"
            output += f"{adv_text}: [{rolls_str}] → {roll}\n"
        else:
            output += f"d20: {roll}\n"
        
        output += f"Modifier: {modifier:+d}\n"
        output += f"**Total: {total}**"
        
        if result_text:
            output += f"\n**{result_text}**"
        
        return [TextContent(type="text", text=output)]
    
    elif name == "roll_initiative":
        combatants = arguments["combatants"]
        results = []
        
        for combatant in combatants:
            name = combatant["name"]
            modifier = combatant["modifier"]
            advantage = combatant.get("advantage", False)
            
            if advantage:
                rolls = [secure_roll(20), secure_roll(20)]
                roll = max(rolls)
            else:
                roll = secure_roll(20)
                rolls = [roll]
            
            total = roll + modifier
            
            results.append({
                "name": name,
                "roll": roll,
                "rolls": rolls,
                "modifier": modifier,
                "total": total,
                "advantage": advantage
            })
            
            # Log individual initiative roll
            log_roll({
                "type": "initiative",
                "character": name,
                "roll": roll,
                "rolls": rolls,
                "modifier": modifier,
                "total": total,
                "advantage": advantage
            })
        
        # Sort by total (descending)
        results.sort(key=lambda x: x["total"], reverse=True)
        
        # Format output
        output = "🎯 Initiative Order:\n\n"
        for i, result in enumerate(results, 1):
            output += f"{i}. **{result['name']}**: {result['total']}"
            if result['advantage']:
                rolls_str = ", ".join(str(r) for r in result['rolls'])
                output += f" (Advantage: [{rolls_str}] → {result['roll']} + {result['modifier']})"
            else:
                output += f" ({result['roll']} + {result['modifier']})"
            output += "\n"
        
        return [TextContent(type="text", text=output)]
    
    elif name == "roll_saving_throw":
        modifier = arguments["modifier"]
        dc = arguments["dc"]
        ability = arguments["ability"]
        character = arguments["character"]
        advantage = arguments.get("advantage", False)
        disadvantage = arguments.get("disadvantage", False)
        
        # Roll save
        if advantage and disadvantage:
            roll = secure_roll(20)
            rolls = [roll]
        elif advantage:
            rolls = [secure_roll(20), secure_roll(20)]
            roll = max(rolls)
        elif disadvantage:
            rolls = [secure_roll(20), secure_roll(20)]
            roll = min(rolls)
        else:
            roll = secure_roll(20)
            rolls = [roll]
        
        total = roll + modifier
        success = (total >= dc)
        is_crit_success = (roll == 20)
        is_crit_fail = (roll == 1)
        
        result_text = "SUCCESS!" if success else "FAILURE!"
        if is_crit_success:
            result_text = "CRITICAL SUCCESS!"
        elif is_crit_fail:
            result_text = "CRITICAL FAILURE!"
        
        # Log the roll
        log_roll({
            "type": "saving_throw",
            "character": character,
            "ability": ability,
            "roll": roll,
            "rolls": rolls,
            "modifier": modifier,
            "total": total,
            "dc": dc,
            "success": success,
            "advantage": advantage,
            "disadvantage": disadvantage,
            "is_crit_success": is_crit_success,
            "is_crit_fail": is_crit_fail
        })
        
        # Format output
        output = f"🛡️ Saving Throw: {character} ({ability})\n"
        
        if len(rolls) > 1:
            rolls_str = ", ".join(str(r) for r in rolls)
            adv_text = "Advantage" if advantage else "Disadvantage"
            output += f"{adv_text}: [{rolls_str}] → {roll}\n"
        else:
            output += f"d20: {roll}\n"
        
        output += f"Modifier: {modifier:+d}\n"
        output += f"**Total: {total}** vs DC {dc}\n"
        output += f"**{result_text}**"
        
        return [TextContent(type="text", text=output)]
    
    elif name == "get_roll_history":
        limit = arguments.get("limit", 10)
        character_filter = arguments.get("character")
        
        try:
            if not AUDIT_LOG_PATH.exists():
                return [TextContent(type="text", text="No roll history found.")]
            
            with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Parse and filter rolls
            rolls = []
            for line in reversed(lines):  # Most recent first
                try:
                    roll = json.loads(line)
                    if character_filter and roll.get("character") != character_filter:
                        continue
                    rolls.append(roll)
                    if len(rolls) >= limit:
                        break
                except json.JSONDecodeError:
                    continue
            
            if not rolls:
                return [TextContent(type="text", text="No matching rolls found.")]
            
            # Format output
            output = f"📜 Roll History (Last {len(rolls)} rolls):\n\n"
            for i, roll in enumerate(rolls, 1):
                roll_type = roll.get("type", "unknown")
                character = roll.get("character", "Unknown")
                timestamp = roll.get("timestamp", "Unknown time")
                
                output += f"{i}. **{character}** - {roll_type}\n"
                output += f"   Time: {timestamp}\n"
                
                if roll_type == "dice_roll":
                    output += f"   Expression: {roll.get('expression')}\n"
                    output += f"   Total: {roll.get('total')}\n"
                    output += f"   Reason: {roll.get('reason')}\n"
                elif roll_type == "attack_roll":
                    output += f"   Weapon: {roll.get('weapon')}\n"
                    output += f"   Total: {roll.get('total')}\n"
                    output += f"   Result: {roll.get('result')}\n"
                elif roll_type == "saving_throw":
                    output += f"   Ability: {roll.get('ability')}\n"
                    output += f"   Total: {roll.get('total')} vs DC {roll.get('dc')}\n"
                    output += f"   Success: {roll.get('success')}\n"
                elif roll_type == "initiative":
                    output += f"   Total: {roll.get('total')}\n"
                
                output += "\n"
            
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error reading roll history: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Main entry point for the MCP server."""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
