# Travel Manager MCP Server

Automatically tracks and deducts rations and water during D&D travel.

## Features

- **Automatic Ration Deduction**: Deducts 1 ration per day per party member
- **Party Management**: Processes all party members at once
- **Obsidian Integration**: Updates character sheets in real-time
- **Travel Types**: Supports overland and underground travel

## Tools

### `process_travel`
Process travel for the entire party and automatically deduct rations.

**Parameters:**
- `party_members`: List of character names (format: "FirstName_LastName")
- `days`: Number of days traveled
- `travel_type`: "overland" or "underground" (optional, default: "overland")

**Example:**
```python
process_travel(
    party_members=["Torgga_Brawnanvil", "Eglath_Bearkiller", "Brevin", "Vandross_Ephrates", "Zephyr_Sparkwhistle"],
    days=2,
    travel_type="underground"
)
```

### `update_rations`
Manually deduct rations for a single character (for adjustments).

**Parameters:**
- `character_name`: Character name (format: "FirstName_LastName")
- `days`: Number of days of rations to deduct

### `check_random_encounter`
Roll for random encounters during travel. Checks if an encounter occurs (1d20, 17-20 triggers) and determines which enemies based on biome, terrain, and time of day.

**Parameters:**
- `biome`: Biome type - "forest", "plains", "mountain", "hills", "grassland", etc. (optional, default: "plains")
- `terrain`: Terrain type - "overland", "underground", "tunnel", "cave", "dungeon", etc. (optional, default: "overland")
- `time_of_day`: "day" or "night" (optional, default: "day")

**Returns:**
- If encounter occurs: Details including enemy type, quantity, and description
- If no encounter: Confirmation that travel continues uneventfully

**Example:**
```python
# Check for encounter during day travel in forest
check_random_encounter(
    biome="forest",
    terrain="overland",
    time_of_day="day"
)

# Check for encounter during night in tunnel network
check_random_encounter(
    biome="plains",  # Not used for underground
    terrain="underground",
    time_of_day="night"
)
```

**Encounter Tables:**
- **Underground/Tunnel**: Goblins, giant rats, spiders, carrion crawlers, gelatinous cube, stirges, ochre jellies
- **Forest**: Stirges, wolves, goblins, hobgoblins, bugbears, owlbear, bandits
- **Plains**: Wolves, goblins, hobgoblins, bandits, orcs, ogre, gnolls
- **Mountain**: Goblins, hobgoblins, bugbears, orcs, bandits, ogre, harpies
- **Default (Triboar Trail)**: Stirges, ogre, goblin band, hobgoblin squad, bugbear scouts, wolves, owlbear

**Encounter Check Rules:**
- Roll 1d20: 17-20 triggers an encounter
- If triggered: Roll 1d12 on the appropriate encounter table
- Some encounters only occur during day (e.g., ogre) or only at night (e.g., ghouls)

## Usage

When the party travels:
1. Call `process_travel()` with party members and days
2. The tool automatically deducts rations from each character's inventory
3. Returns summary of what was deducted

## Notes

- Rations: 1 per day per person
- Water: Not auto-deducted (waterskins can be refilled)
- Weight: Automatically adjusted (2 lb per day of rations)
