#!/usr/bin/env python3
"""
Weather & Calendar MCP Server for D&D Campaigns
Handles weather generation, calendar tracking, and time management.
"""

import sys
import json
import random
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    from mcp.server.stdio import stdio_server
except ImportError:
    print("ERROR: mcp package not found. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

class WeatherCalendarServer:
    def __init__(self):
        self.campaign_path = Path("C:/DnD/Campaigns")
        
    def get_weather(self, season: str, terrain: str) -> dict:
        """Generate weather based on season and terrain."""
        weather_types = {
            "spring": ["Clear", "Partly Cloudy", "Rainy", "Windy"],
            "summer": ["Clear", "Hot", "Partly Cloudy", "Thunderstorm"],
            "autumn": ["Cloudy", "Rainy", "Windy", "Foggy"],
            "winter": ["Clear", "Snowy", "Blizzard", "Overcast"]
        }
        
        season_weather = weather_types.get(season.lower(), weather_types["spring"])
        weather = random.choice(season_weather)
        
        temp_ranges = {
            "spring": (50, 70),
            "summer": (70, 95),
            "autumn": (45, 65),
            "winter": (20, 45)
        }
        
        temp_range = temp_ranges.get(season.lower(), (50, 70))
        temperature = random.randint(*temp_range)
        
        return {
            "weather": weather,
            "temperature": temperature,
            "season": season,
            "terrain": terrain
        }
    
    def advance_time(self, campaign_name: str, hours: int) -> dict:
        """Advance campaign time by specified hours."""
        return {
            "campaign": campaign_name,
            "hours_passed": hours,
            "message": f"Advanced time by {hours} hours"
        }


# Initialize MCP server
app = Server("weather-calendar")
server = WeatherCalendarServer()


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_weather",
            description="Generate weather for the current location",
            inputSchema={
                "type": "object",
                "properties": {
                    "season": {
                        "type": "string",
                        "description": "Current season (spring/summer/autumn/winter)"
                    },
                    "terrain": {
                        "type": "string",
                        "description": "Terrain type (forest/mountain/plains/coast)"
                    }
                },
                "required": ["season", "terrain"]
            }
        ),
        Tool(
            name="advance_time",
            description="Advance campaign time by hours",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_name": {"type": "string"},
                    "hours": {"type": "integer"}
                },
                "required": ["campaign_name", "hours"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "get_weather":
            result = server.get_weather(
                arguments.get("season", "spring"),
                arguments.get("terrain", "plains")
            )
        elif name == "advance_time":
            result = server.advance_time(
                arguments.get("campaign_name"),
                arguments.get("hours", 1)
            )
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


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


