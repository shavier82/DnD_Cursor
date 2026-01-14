#!/usr/bin/env python3
"""
Weather & Calendar MCP Server
Track in-game time, weather, moon phases, and festivals for D&D campaigns.

Features:
- Calendar tracking (day/month/year)
- Weather generation (season-based)
- Moon phases (for lycanthropy, etc.)
- Festival/event calendar
- Time advancement
- Travel time calculations
"""

import json
import logging
import random
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import math

# MCP SDK imports
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
from mcp import types

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Suppress verbose MCP library logs
logging.getLogger("mcp.server.session").setLevel(logging.ERROR)
logging.getLogger("mcp.server.stdio").setLevel(logging.ERROR)

# Calendar state file
CALENDAR_STATE_FILE = Path("C:/DnD/Campaigns/campaign_calendar.json")

app = Server("weather-calendar")

# ============================================================================
# CALENDAR SYSTEM (Harptos Calendar - Forgotten Realms)
# ============================================================================

MONTHS = [
    {"name": "Hammer", "season": "Winter", "days": 30},
    {"name": "Alturiak", "season": "Winter", "days": 30},
    {"name": "Ches", "season": "Spring", "days": 30},
    {"name": "Tarsakh", "season": "Spring", "days": 30},
    {"name": "Mirtul", "season": "Spring", "days": 30},
    {"name": "Kythorn", "season": "Summer", "days": 30},
    {"name": "Flamerule", "season": "Summer", "days": 30},
    {"name": "Eleasis", "season": "Summer", "days": 30},
    {"name": "Eleint", "season": "Autumn", "days": 30},
    {"name": "Marpenoth", "season": "Autumn", "days": 30},
    {"name": "Uktar", "season": "Autumn", "days": 30},
    {"name": "Nightal", "season": "Winter", "days": 30}
]

FESTIVALS = {
    "Midwinter": {"month": 1, "day": 0, "description": "Between Hammer and Alturiak"},
    "Greengrass": {"month": 5, "day": 0, "description": "Between Tarsakh and Mirtul"},
    "Midsummer": {"month": 7, "day": 0, "description": "Between Flamerule and Eleasis"},
    "Highharvestide": {"month": 10, "day": 0, "description": "Between Eleint and Marpenoth"},
    "The Feast of the Moon": {"month": 12, "day": 0, "description": "Between Uktar and Nightal"}
}

# ============================================================================
# WEATHER SYSTEM
# ============================================================================

WEATHER_BY_SEASON = {
    "Winter": {
        "temperatures": ["Freezing", "Cold", "Cold", "Chilly"],
        "conditions": [
            {"name": "Clear", "weight": 20},
            {"name": "Partly Cloudy", "weight": 25},
            {"name": "Overcast", "weight": 20},
            {"name": "Light Snow", "weight": 15},
            {"name": "Heavy Snow", "weight": 10},
            {"name": "Blizzard", "weight": 5},
            {"name": "Freezing Rain", "weight": 5}
        ]
    },
    "Spring": {
        "temperatures": ["Chilly", "Cool", "Mild", "Warm"],
        "conditions": [
            {"name": "Clear", "weight": 25},
            {"name": "Partly Cloudy", "weight": 30},
            {"name": "Overcast", "weight": 15},
            {"name": "Light Rain", "weight": 15},
            {"name": "Heavy Rain", "weight": 10},
            {"name": "Thunderstorm", "weight": 5}
        ]
    },
    "Summer": {
        "temperatures": ["Warm", "Hot", "Hot", "Very Hot"],
        "conditions": [
            {"name": "Clear", "weight": 35},
            {"name": "Partly Cloudy", "weight": 30},
            {"name": "Overcast", "weight": 10},
            {"name": "Light Rain", "weight": 10},
            {"name": "Heavy Rain", "weight": 5},
            {"name": "Thunderstorm", "weight": 10}
        ]
    },
    "Autumn": {
        "temperatures": ["Cool", "Mild", "Warm", "Chilly"],
        "conditions": [
            {"name": "Clear", "weight": 25},
            {"name": "Partly Cloudy", "weight": 25},
            {"name": "Overcast", "weight": 20},
            {"name": "Light Rain", "weight": 15},
            {"name": "Heavy Rain", "weight": 10},
            {"name": "Fog", "weight": 5}
        ]
    }
}

WEATHER_EFFECTS = {
    "Clear": {"travel_mod": 1.0, "visibility": "Excellent", "effects": []},
    "Partly Cloudy": {"travel_mod": 1.0, "visibility": "Good", "effects": []},
    "Overcast": {"travel_mod": 1.0, "visibility": "Good", "effects": []},
    "Light Rain": {"travel_mod": 0.9, "visibility": "Fair", "effects": ["Disadvantage on Perception (sight)", "Extinguishes torches"]},
    "Heavy Rain": {"travel_mod": 0.75, "visibility": "Poor", "effects": ["Disadvantage on Perception (sight/sound)", "Extinguishes torches", "Difficult terrain"]},
    "Thunderstorm": {"travel_mod": 0.5, "visibility": "Poor", "effects": ["Disadvantage on Perception", "Lightning hazard", "Difficult terrain"]},
    "Light Snow": {"travel_mod": 0.9, "visibility": "Fair", "effects": ["Disadvantage on Perception (sight)"]},
    "Heavy Snow": {"travel_mod": 0.5, "visibility": "Poor", "effects": ["Disadvantage on Perception", "Difficult terrain", "Cold exposure"]},
    "Blizzard": {"travel_mod": 0.25, "visibility": "Very Poor", "effects": ["Heavy obscurement", "Difficult terrain", "Cold exposure", "DC 10 CON save or 1 exhaustion"]},
    "Freezing Rain": {"travel_mod": 0.5, "visibility": "Poor", "effects": ["Difficult terrain (ice)", "DEX saves or fall prone", "Cold exposure"]},
    "Fog": {"travel_mod": 0.75, "visibility": "Poor", "effects": ["Disadvantage on Perception (sight)", "Lightly obscured"]}
}

# ============================================================================
# MOON PHASES
# ============================================================================

MOON_PHASES = [
    "New Moon",
    "Waxing Crescent",
    "First Quarter",
    "Waxing Gibbous",
    "Full Moon",
    "Waning Gibbous",
    "Last Quarter",
    "Waning Crescent"
]

MOON_EFFECTS = {
    "New Moon": {"lycanthropy_risk": 0, "visibility": "Very Dark", "perception_mod": -2},
    "Full Moon": {"lycanthropy_risk": 100, "visibility": "Bright", "perception_mod": +2}
}


def load_calendar_state() -> Dict[str, Any]:
    """Load calendar state from file"""
    if CALENDAR_STATE_FILE.exists():
        with open(CALENDAR_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Default starting date
        return {
            "day": 1,
            "month": 1,  # Hammer
            "year": 1492,  # Default Forgotten Realms year
            "hour": 12,
            "minute": 0,
            "location": "Phandalin",
            "weather": "Clear",
            "temperature": "Mild",
            "last_updated": datetime.now().isoformat()
        }


def save_calendar_state(state: Dict[str, Any]):
    """Save calendar state to file"""
    CALENDAR_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = datetime.now().isoformat()
    with open(CALENDAR_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, indent=2, fp=f)


def get_month_name(month: int) -> str:
    """Get month name from month number (1-12)"""
    return MONTHS[month - 1]["name"]


def get_season(month: int) -> str:
    """Get season from month number"""
    return MONTHS[month - 1]["season"]


def calculate_moon_phase(day: int, month: int, year: int) -> str:
    """Calculate moon phase based on date (simplified)"""
    # Total days since year start
    total_days = sum(MONTHS[i]["days"] for i in range(month - 1)) + day
    # Moon cycle is ~30 days
    phase_index = (total_days % 30) // 4  # 8 phases, ~4 days each
    return MOON_PHASES[phase_index % 8]


def generate_weather(season: str, current_weather: str = None) -> Dict[str, Any]:
    """Generate weather based on season (with continuity from current weather)"""
    season_data = WEATHER_BY_SEASON[season]
    
    # Generate condition
    conditions = season_data["conditions"]
    total_weight = sum(c["weight"] for c in conditions)
    rand = random.randint(1, total_weight)
    
    cumulative = 0
    condition = "Clear"
    for cond in conditions:
        cumulative += cond["weight"]
        if rand <= cumulative:
            condition = cond["name"]
            break
    
    # If there's current weather, slightly bias toward similar conditions
    if current_weather and random.random() < 0.3:
        condition = current_weather
    
    # Generate temperature
    temperature = random.choice(season_data["temperatures"])
    
    # Get weather effects
    effects = WEATHER_EFFECTS.get(condition, {})
    
    return {
        "condition": condition,
        "temperature": temperature,
        "travel_modifier": effects.get("travel_mod", 1.0),
        "visibility": effects.get("visibility", "Good"),
        "effects": effects.get("effects", [])
    }


def format_date(day: int, month: int, year: int) -> str:
    """Format date as string"""
    month_name = get_month_name(month)
    return f"{day} {month_name}, {year} DR"


def format_time(hour: int, minute: int) -> str:
    """Format time as string"""
    period = "AM" if hour < 12 else "PM"
    display_hour = hour if hour <= 12 else hour - 12
    if display_hour == 0:
        display_hour = 12
    return f"{display_hour}:{minute:02d} {period}"


# ============================================================================
# MCP TOOLS
# ============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available weather/calendar tools"""
    return [
        Tool(
            name="get_current_date_time",
            description="Get the current in-game date and time",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_current_weather",
            description="Get current weather for a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Location name (e.g., 'Phandalin')",
                        "default": "Phandalin"
                    }
                }
            }
        ),
        Tool(
            name="advance_time",
            description="Advance in-game time (hours, days, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "hours": {"type": "integer", "default": 0},
                    "days": {"type": "integer", "default": 0},
                    "regenerate_weather": {"type": "boolean", "default": True}
                }
            }
        ),
        Tool(
            name="get_moon_phase",
            description="Get current moon phase (for lycanthropy, etc.)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="calculate_travel_time",
            description="Calculate travel time between locations",
            inputSchema={
                "type": "object",
                "properties": {
                    "distance_miles": {"type": "number"},
                    "terrain": {
                        "type": "string",
                        "enum": ["road", "trail", "wilderness", "difficult"],
                        "default": "road"
                    },
                    "pace": {
                        "type": "string",
                        "enum": ["slow", "normal", "fast"],
                        "default": "normal"
                    }
                },
                "required": ["distance_miles"]
            }
        ),
        Tool(
            name="set_date_time",
            description="Set the in-game date and time",
            inputSchema={
                "type": "object",
                "properties": {
                    "day": {"type": "integer"},
                    "month": {"type": "integer"},
                    "year": {"type": "integer"},
                    "hour": {"type": "integer", "default": 12},
                    "minute": {"type": "integer", "default": 0}
                },
                "required": ["day", "month", "year"]
            }
        ),
        Tool(
            name="get_upcoming_festivals",
            description="Get upcoming festivals and special days",
            inputSchema={
                "type": "object",
                "properties": {
                    "days_ahead": {"type": "integer", "default": 30}
                }
            }
        ),
        Tool(
            name="long_rest",
            description="Advance time by 8 hours (long rest) and update weather",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "get_current_date_time":
            state = load_calendar_state()
            
            date_str = format_date(state["day"], state["month"], state["year"])
            time_str = format_time(state["hour"], state["minute"])
            season = get_season(state["month"])
            
            return [TextContent(type="text", text=json.dumps({
                "date": date_str,
                "time": time_str,
                "day": state["day"],
                "month": get_month_name(state["month"]),
                "month_number": state["month"],
                "year": state["year"],
                "season": season,
                "location": state.get("location", "Unknown")
            }, indent=2))]
        
        elif name == "get_current_weather":
            state = load_calendar_state()
            location = arguments.get("location", state.get("location", "Phandalin"))
            
            # Generate weather if not present or if new day
            if "weather" not in state or state.get("weather") == "":
                season = get_season(state["month"])
                weather = generate_weather(season)
                state["weather"] = weather["condition"]
                state["temperature"] = weather["temperature"]
                save_calendar_state(state)
            else:
                season = get_season(state["month"])
                weather_data = WEATHER_EFFECTS.get(state["weather"], {})
                weather = {
                    "condition": state["weather"],
                    "temperature": state.get("temperature", "Mild"),
                    "travel_modifier": weather_data.get("travel_mod", 1.0),
                    "visibility": weather_data.get("visibility", "Good"),
                    "effects": weather_data.get("effects", [])
                }
            
            return [TextContent(type="text", text=json.dumps({
                "location": location,
                "date": format_date(state["day"], state["month"], state["year"]),
                "season": season,
                "condition": weather["condition"],
                "temperature": weather["temperature"],
                "visibility": weather["visibility"],
                "travel_modifier": f"{weather['travel_modifier']*100:.0f}%",
                "effects": weather["effects"]
            }, indent=2))]
        
        elif name == "advance_time":
            state = load_calendar_state()
            hours = arguments.get("hours", 0)
            days = arguments.get("days", 0)
            regen_weather = arguments.get("regenerate_weather", True)
            
            # Advance time
            total_hours = hours + (days * 24)
            state["hour"] += total_hours
            
            # Handle day rollover
            while state["hour"] >= 24:
                state["hour"] -= 24
                state["day"] += 1
                
                # Handle month rollover
                month_days = MONTHS[state["month"] - 1]["days"]
                if state["day"] > month_days:
                    state["day"] = 1
                    state["month"] += 1
                    
                    # Handle year rollover
                    if state["month"] > 12:
                        state["month"] = 1
                        state["year"] += 1
            
            # Regenerate weather if advancing days and flag is set
            if (days > 0 or hours >= 12) and regen_weather:
                season = get_season(state["month"])
                weather = generate_weather(season, state.get("weather"))
                state["weather"] = weather["condition"]
                state["temperature"] = weather["temperature"]
            
            save_calendar_state(state)
            
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "new_date": format_date(state["day"], state["month"], state["year"]),
                "new_time": format_time(state["hour"], state["minute"]),
                "hours_advanced": total_hours,
                "weather": state["weather"],
                "temperature": state["temperature"]
            }, indent=2))]
        
        elif name == "get_moon_phase":
            state = load_calendar_state()
            phase = calculate_moon_phase(state["day"], state["month"], state["year"])
            
            effects = MOON_EFFECTS.get(phase, {"lycanthropy_risk": 50, "visibility": "Moderate", "perception_mod": 0})
            
            return [TextContent(type="text", text=json.dumps({
                "date": format_date(state["day"], state["month"], state["year"]),
                "moon_phase": phase,
                "lycanthropy_risk": effects.get("lycanthropy_risk", 50),
                "night_visibility": effects.get("visibility", "Moderate"),
                "perception_modifier": effects.get("perception_mod", 0)
            }, indent=2))]
        
        elif name == "calculate_travel_time":
            distance = arguments["distance_miles"]
            terrain = arguments.get("terrain", "road")
            pace = arguments.get("pace", "normal")
            
            # Base travel speeds (miles per hour)
            pace_speeds = {"slow": 2, "normal": 3, "fast": 4}
            terrain_mods = {"road": 1.0, "trail": 0.75, "wilderness": 0.5, "difficult": 0.25}
            
            speed = pace_speeds[pace] * terrain_mods[terrain]
            
            # Get weather modifier
            state = load_calendar_state()
            weather_effects = WEATHER_EFFECTS.get(state.get("weather", "Clear"), {})
            weather_mod = weather_effects.get("travel_mod", 1.0)
            
            adjusted_speed = speed * weather_mod
            travel_hours = distance / adjusted_speed
            
            # Calculate days and hours
            travel_days = int(travel_hours // 8)  # 8 hours of travel per day
            remaining_hours = travel_hours % 8
            
            return [TextContent(type="text", text=json.dumps({
                "distance_miles": distance,
                "terrain": terrain,
                "pace": pace,
                "base_speed_mph": speed,
                "weather_modifier": f"{weather_mod*100:.0f}%",
                "adjusted_speed_mph": adjusted_speed,
                "total_travel_hours": round(travel_hours, 1),
                "travel_time": f"{travel_days} days, {int(remaining_hours)} hours",
                "note": f"Assumes {8} hours travel per day"
            }, indent=2))]
        
        elif name == "set_date_time":
            state = load_calendar_state()
            state["day"] = arguments["day"]
            state["month"] = arguments["month"]
            state["year"] = arguments["year"]
            state["hour"] = arguments.get("hour", 12)
            state["minute"] = arguments.get("minute", 0)
            
            # Regenerate weather for new date
            season = get_season(state["month"])
            weather = generate_weather(season)
            state["weather"] = weather["condition"]
            state["temperature"] = weather["temperature"]
            
            save_calendar_state(state)
            
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "date": format_date(state["day"], state["month"], state["year"]),
                "time": format_time(state["hour"], state["minute"]),
                "season": season
            }, indent=2))]
        
        elif name == "get_upcoming_festivals":
            state = load_calendar_state()
            days_ahead = arguments.get("days_ahead", 30)
            
            # Calculate upcoming festivals (simplified)
            upcoming = []
            for festival, data in FESTIVALS.items():
                upcoming.append({
                    "name": festival,
                    "description": data["description"],
                    "note": "Check calendar for exact date"
                })
            
            return [TextContent(type="text", text=json.dumps({
                "current_date": format_date(state["day"], state["month"], state["year"]),
                "upcoming_festivals": upcoming[:3]  # Show first 3
            }, indent=2))]
        
        elif name == "long_rest":
            state = load_calendar_state()
            
            # Advance 8 hours
            state["hour"] += 8
            if state["hour"] >= 24:
                state["hour"] -= 24
                state["day"] += 1
                
                # Handle month rollover
                month_days = MONTHS[state["month"] - 1]["days"]
                if state["day"] > month_days:
                    state["day"] = 1
                    state["month"] += 1
                    if state["month"] > 12:
                        state["month"] = 1
                        state["year"] += 1
            
            # Regenerate weather
            season = get_season(state["month"])
            weather = generate_weather(season, state.get("weather"))
            state["weather"] = weather["condition"]
            state["temperature"] = weather["temperature"]
            
            save_calendar_state(state)
            
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "message": "Party took a long rest (8 hours)",
                "new_date": format_date(state["day"], state["month"], state["year"]),
                "new_time": format_time(state["hour"], state["minute"]),
                "weather": state["weather"],
                "reminder": "All spell slots and HP recovered (update character sheets)"
            }, indent=2))]
        
        else:
            return [TextContent(type="text", text=json.dumps({
                "error": f"Unknown tool: {name}"
            }, indent=2))]
    
    except Exception as e:
        logger.error(f"Error in {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=json.dumps({
            "error": str(e)
        }, indent=2))]


async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())




