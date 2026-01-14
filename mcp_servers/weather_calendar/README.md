# Weather & Calendar MCP Server

Track in-game time, weather, moon phases, and festivals for D&D 5e campaigns.

## Features

- **Harptos Calendar** (Forgotten Realms standard)
- **Season-based weather** with travel/combat effects
- **Moon phases** (lycanthropy tracking)
- **Festival calendar**
- **Travel time calculator**
- **Long rest integration**

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "weather-calendar": {
      "command": "python",
      "args": ["weather_calendar_server.py"],
      "cwd": "C:/DnD/DnD_Cursor/mcp_servers/weather_calendar"
    }
  }
}
```

## Quick Start

```python
# Check date and weather
get_current_date_time()
get_current_weather()

# Advance time
advance_time(hours=4)
advance_time(days=2)

# Long rest
long_rest()

# Check moon phase
get_moon_phase()

# Calculate travel
calculate_travel_time(distance_miles=30, terrain="road", pace="normal")
```

## Documentation

See `docs/MCP_WEATHER_CALENDAR_COMPLETE.md` for full documentation.

## State File

Calendar state is saved to: `C:/DnD/Campaigns/campaign_calendar.json`

## Calendar System

**12 Months (30 days each):**
Hammer, Alturiak, Ches, Tarsakh, Mirtul, Kythorn, Flamerule, Eleasis, Eleint, Marpenoth, Uktar, Nightal

**4 Seasons:**
Winter (Hammer, Alturiak, Nightal)
Spring (Ches, Tarsakh, Mirtul)
Summer (Kythorn, Flamerule, Eleasis)
Autumn (Eleint, Marpenoth, Uktar)

## Weather Effects

- **Clear/Partly Cloudy:** No effects
- **Rain:** Disadvantage on Perception, reduced travel speed
- **Thunderstorm:** Lightning hazard, difficult terrain
- **Snow/Blizzard:** Cold exposure, exhaustion risk
- **Fog:** Lightly obscured, reduced visibility

## Moon Phases

8 phases over ~30 days:
- New Moon → Waxing Crescent → First Quarter → Waxing Gibbous
- Full Moon → Waning Gibbous → Last Quarter → Waning Crescent

**Full Moon:** 100% lycanthropy risk, bright night
**New Moon:** 0% lycanthropy risk, very dark night

## License

Part of DnD_Cursor project.



