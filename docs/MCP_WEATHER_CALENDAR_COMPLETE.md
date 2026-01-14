# Weather & Calendar MCP Server - Complete Documentation

## Overview

The **Weather/Calendar MCP** tracks in-game time, generates realistic weather, calculates moon phases, and manages festivals for your D&D campaign. It uses the **Harptos Calendar** (Forgotten Realms standard).

## Features

✅ **Calendar System** - Track day/month/year/time in-game  
✅ **Weather Generation** - Season-based, realistic weather with travel effects  
✅ **Moon Phases** - 8-phase lunar cycle (for lycanthropy, werewolves, etc.)  
✅ **Festivals & Events** - Forgotten Realms festival calendar  
✅ **Travel Time Calculator** - Distance + terrain + weather = accurate travel time  
✅ **Long Rest Integration** - Automatically advance time and update weather  
✅ **Persistent State** - Calendar state saved to `campaign_calendar.json`

---

## Calendar System (Harptos)

### Months (30 days each)
1. **Hammer** (Winter)
2. **Alturiak** (Winter)
3. **Ches** (Spring)
4. **Tarsakh** (Spring)
5. **Mirtul** (Spring)
6. **Kythorn** (Summer)
7. **Flamerule** (Summer)
8. **Eleasis** (Summer)
9. **Eleint** (Autumn)
10. **Marpenoth** (Autumn)
11. **Uktar** (Autumn)
12. **Nightal** (Winter)

### Special Festivals
- **Midwinter** - Between Hammer and Alturiak
- **Greengrass** - Between Tarsakh and Mirtul
- **Midsummer** - Between Flamerule and Eleasis
- **Highharvestide** - Between Eleint and Marpenoth
- **The Feast of the Moon** - Between Uktar and Nightal

---

## Weather System

### Weather by Season

**Winter:** Freezing, Cold, Chilly | Clear, Snow, Blizzard, Freezing Rain  
**Spring:** Chilly, Cool, Mild, Warm | Clear, Rain, Thunderstorm  
**Summer:** Warm, Hot, Very Hot | Clear, Partly Cloudy, Thunderstorm  
**Autumn:** Cool, Mild, Warm | Clear, Overcast, Rain, Fog

### Weather Effects

| Condition | Travel Speed | Visibility | Effects |
|-----------|--------------|------------|---------|
| **Clear** | 100% | Excellent | None |
| **Partly Cloudy** | 100% | Good | None |
| **Light Rain** | 90% | Fair | Disadvantage on Perception (sight), Extinguishes torches |
| **Heavy Rain** | 75% | Poor | Disadvantage on Perception, Difficult terrain |
| **Thunderstorm** | 50% | Poor | Disadvantage on Perception, Lightning hazard |
| **Light Snow** | 90% | Fair | Disadvantage on Perception (sight) |
| **Heavy Snow** | 50% | Poor | Difficult terrain, Cold exposure |
| **Blizzard** | 25% | Very Poor | Heavy obscurement, DC 10 CON save or exhaustion |
| **Freezing Rain** | 50% | Poor | Difficult terrain (ice), DEX saves to avoid falling |
| **Fog** | 75% | Poor | Lightly obscured |

---

## Moon Phases

### 8-Phase Lunar Cycle (~30 days)

1. **New Moon** - Lycanthropy Risk: 0% | Night Visibility: Very Dark | Perception: -2
2. Waxing Crescent
3. First Quarter
4. Waxing Gibbous
5. **Full Moon** - Lycanthropy Risk: 100% | Night Visibility: Bright | Perception: +2
6. Waning Gibbous
7. Last Quarter
8. Waning Crescent

---

## MCP Tools

### 1. `get_current_date_time`
**Get the current in-game date and time**

**Output:**
```json
{
  "date": "15 Mirtul, 1492 DR",
  "time": "3:00 PM",
  "day": 15,
  "month": "Mirtul",
  "month_number": 5,
  "year": 1492,
  "season": "Spring",
  "location": "Phandalin"
}
```

---

### 2. `get_current_weather`
**Get current weather for a location**

**Parameters:**
- `location` (string, optional): Location name (default: "Phandalin")

**Output:**
```json
{
  "location": "Phandalin",
  "date": "15 Mirtul, 1492 DR",
  "season": "Spring",
  "condition": "Light Rain",
  "temperature": "Cool",
  "visibility": "Fair",
  "travel_modifier": "90%",
  "effects": [
    "Disadvantage on Perception (sight)",
    "Extinguishes torches"
  ]
}
```

---

### 3. `advance_time`
**Advance in-game time**

**Parameters:**
- `hours` (integer): Hours to advance (default: 0)
- `days` (integer): Days to advance (default: 0)
- `regenerate_weather` (boolean): Regenerate weather? (default: true)

**Output:**
```json
{
  "success": true,
  "new_date": "16 Mirtul, 1492 DR",
  "new_time": "11:00 AM",
  "hours_advanced": 24,
  "weather": "Partly Cloudy",
  "temperature": "Mild"
}
```

---

### 4. `get_moon_phase`
**Get current moon phase**

**Output:**
```json
{
  "date": "15 Mirtul, 1492 DR",
  "moon_phase": "Waxing Gibbous",
  "lycanthropy_risk": 50,
  "night_visibility": "Moderate",
  "perception_modifier": 0
}
```

**Use Case:** Werewolf encounters, night combat, stealth missions

---

### 5. `calculate_travel_time`
**Calculate travel time between locations**

**Parameters:**
- `distance_miles` (number, required): Distance in miles
- `terrain` (string): "road", "trail", "wilderness", "difficult" (default: "road")
- `pace` (string): "slow", "normal", "fast" (default: "normal")

**Output:**
```json
{
  "distance_miles": 30,
  "terrain": "trail",
  "pace": "normal",
  "base_speed_mph": 2.25,
  "weather_modifier": "90%",
  "adjusted_speed_mph": 2.03,
  "total_travel_hours": 14.8,
  "travel_time": "1 days, 6 hours",
  "note": "Assumes 8 hours travel per day"
}
```

**Travel Speeds:**
- Slow: 2 mph, Normal: 3 mph, Fast: 4 mph
- Terrain modifiers: Road (100%), Trail (75%), Wilderness (50%), Difficult (25%)
- Weather modifiers: Applied automatically from current weather

---

### 6. `set_date_time`
**Set the in-game date and time**

**Parameters:**
- `day` (integer, required): Day of month (1-30)
- `month` (integer, required): Month (1-12)
- `year` (integer, required): Year (e.g., 1492)
- `hour` (integer): Hour (0-23, default: 12)
- `minute` (integer): Minute (0-59, default: 0)

**Output:**
```json
{
  "success": true,
  "date": "1 Hammer, 1493 DR",
  "time": "12:00 PM",
  "season": "Winter"
}
```

---

### 7. `get_upcoming_festivals`
**Get upcoming festivals and special days**

**Parameters:**
- `days_ahead` (integer): Days to look ahead (default: 30)

**Output:**
```json
{
  "current_date": "15 Mirtul, 1492 DR",
  "upcoming_festivals": [
    {
      "name": "Greengrass",
      "description": "Between Tarsakh and Mirtul",
      "note": "Check calendar for exact date"
    }
  ]
}
```

---

### 8. `long_rest`
**Advance time by 8 hours (long rest) and update weather**

**Output:**
```json
{
  "success": true,
  "message": "Party took a long rest (8 hours)",
  "new_date": "16 Mirtul, 1492 DR",
  "new_time": "8:00 AM",
  "weather": "Clear",
  "reminder": "All spell slots and HP recovered (update character sheets)"
}
```

---

## Usage Examples

### Example 1: Session Start
```
DM: "What's the date and weather today?"
→ get_current_date_time()
→ get_current_weather()

Output:
"It's 15 Mirtul, 1492 DR (Spring), 3:00 PM.
Weather in Phandalin: Light Rain, Cool
Visibility: Fair
Effects: Disadvantage on Perception (sight), Extinguishes torches"
```

### Example 2: Overland Travel
```
DM: "The party travels 30 miles to Neverwinter along a trail."
→ calculate_travel_time(distance_miles=30, terrain="trail", pace="normal")

Output:
"Travel time: 1 day, 6 hours (accounting for light rain)."

→ advance_time(days=1, hours=6)
"You arrive in Neverwinter on 16 Mirtul at 9:00 PM."
```

### Example 3: Werewolf Encounter
```
DM: "Is it a full moon tonight?"
→ get_moon_phase()

Output:
"Moon phase: Full Moon
Lycanthropy risk: 100%
Night visibility: Bright (+2 Perception)"
```

### Example 4: Long Rest
```
DM: "The party takes a long rest."
→ long_rest()

Output:
"Party rested for 8 hours.
New time: 16 Mirtul, 8:00 AM
Weather: Clear, Mild
Reminder: All spell slots and HP recovered."
```

---

## Integration with Other Systems

### With Session Recorder
```
→ start_session_log(campaign_name="Lost Mine of Phandelver")
→ get_current_date_time()  # Log session date
→ log_event(event_type="narration", content="Weather: Light Rain")
```

### With Combat Engine
```
# Before combat
→ get_current_weather()  # Check for weather effects on combat

# Heavy rain = difficult terrain, disadvantage on Perception
```

### With Obsidian Sync
```
# After advancing time
→ advance_time(days=3)
→ sync_to_obsidian()  # Update timeline in Obsidian vault
```

---

## Configuration

**Calendar State File:**
`C:/DnD/Campaigns/campaign_calendar.json`

**Default Starting Date:**
- Day: 1, Month: 1 (Hammer), Year: 1492 DR
- Time: 12:00 PM
- Location: Phandalin
- Weather: Clear, Mild

**Customization:**
Use `set_date_time()` to change the starting date for your campaign.

---

## Technical Details

**MCP Server:** `weather-calendar`  
**Port:** stdio (no port needed)  
**Dependencies:** `mcp`  
**Language:** Python 3.10+

**File Locations:**
- Server: `C:\DnD\DnD_Cursor\mcp_servers\weather_calendar\weather_calendar_server.py`
- State: `C:\DnD\Campaigns\campaign_calendar.json`

---

## Quick Reference Card

| Task | Tool | Parameters |
|------|------|------------|
| Check date/time | `get_current_date_time()` | None |
| Check weather | `get_current_weather()` | location (optional) |
| Advance time | `advance_time()` | hours, days |
| Long rest | `long_rest()` | None |
| Moon phase | `get_moon_phase()` | None |
| Travel time | `calculate_travel_time()` | distance_miles, terrain, pace |
| Set date | `set_date_time()` | day, month, year, hour, minute |
| Festivals | `get_upcoming_festivals()` | days_ahead |

---

## Tips for DMs

1. **Start each session:** Check date/time and weather
2. **Track travel:** Use `calculate_travel_time()` for realistic distances
3. **Weather effects:** Apply mechanical effects (disadvantage, difficult terrain)
4. **Moon phases:** Plan werewolf encounters around full moons
5. **Long rests:** Use `long_rest()` to auto-advance time
6. **Seasonal flavor:** Use season/weather for narrative immersion

---

✅ **Weather/Calendar MCP is ready!**

Test with: `get_current_date_time()`, `get_current_weather()`, `get_moon_phase()`



