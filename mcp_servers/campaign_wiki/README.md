# Campaign Wiki MCP - Obsidian Integration

**Version:** 1.0.0  
**Status:** Core Implementation Complete

---

## Overview

Campaign Wiki MCP provides comprehensive campaign management with:
- 📝 **NPC Database** - Track NPCs with relationships, backgrounds, motivations
- 🗺️ **Location Database** - Locations with maps, descriptions, history
- 📜 **Quest Tracking** - Track quests from accepted → in-progress → completed
- ⏱️ **Timeline** - Chronicle campaign events with sessions, dates, consequences
- 🔗 **Relationship Graphs** - Visual NPC/PC relationship networks (networkx)
- 📓 **Obsidian Sync** - Export to Obsidian vault as markdown notes

---

## Features

### NPC Management
- Full character profiles (description, personality, background, motivations, secrets)
- Role tracking (ally, enemy, neutral, quest_giver, etc.)
- Disposition toward party (-10 to +10)
- Relationship tracking with other NPCs/PCs
- Quest associations
- Status tracking (alive/dead, last seen, first met)

### Location Management
- Location types (city, dungeon, tavern, etc.)
- Geographic hierarchy (parent locations, regions)
- Population, inhabitants, factions
- History, current events, rumors
- Services, shops, dangers
- **Map integration** (location maps, battle maps)
- Discovery tracking (visited, secrets discovered)

### Quest Tracking
- Quest types (main, side, personal, faction, etc.)
- Status workflow (available → accepted → in-progress → completed/failed)
- Objectives with completion tracking
- Quest givers, rewards (gold, XP, items, reputation)
- Related NPCs, locations, quests
- Consequences tracking

### Timeline
- Event types (combat, discovery, quest milestones, NPC interactions, etc.)
- Session tracking
- In-game and real-world dates
- Participants, locations, consequences
- Significance rating (1-10)
- Faction reputation changes

### Relationship Graphs
- Directed graph of all relationships
- Relationship types (family, friend, enemy, rival, romantic, ally, etc.)
- Relationship strength (1-10)
- Path finding (how are two entities connected?)
- Visual graph export (matplotlib)
- Graphviz DOT export

### Obsidian Integration
- Auto-generate markdown notes with frontmatter
- Organized folders (NPCs/, Locations/, Quests/)
- Internal links between notes
- Embed maps and images
- Tag support for filtering
- Graph view for relationship visualization
- Free and local (no subscriptions!)

---

## MCP Tools

### Core (5 tools):
1. **create_or_load_wiki** - Initialize or load campaign wiki
2. **create_npc** - Add new NPC with full profile
3. **create_quest** - Add new quest
4. **add_relationship** - Add NPC/PC relationship
5. **sync_to_obsidian** - Export everything to Obsidian vault

### Additional tools follow same pattern:
- create_location, update_npc, update_quest_status
- add_timeline_event, get_npc, get_quest, get_timeline
- get_relationship_graph, visualize_relationships
- search_wiki, import_from_campaign_events

---

## Installation

```powershell
cd "C:\DnD\DnD_Cursor\mcp_servers\campaign_wiki"
pip install -r requirements.txt
```

**Dependencies:**
- mcp, pydantic, networkx
- python-frontmatter
- matplotlib, watchdog
- python-dateutil

---

## Configuration

**Add to `.cursor/mcp.json`:**
```json
"campaign-wiki": {
  "command": "C:\\Users\\ksist\\AppData\\Local\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\\python.exe",
  "args": ["wiki_server.py"],
  "cwd": "C:\\DnD\\DnD_Cursor\\mcp_servers\\campaign_wiki"
}
```

---

## Usage Example

```python
# 1. Load wiki
create_or_load_wiki(
    campaign_name="Phandelver",
    obsidian_vault="C:\\Users\\ksist\\Documents\\Obsidian\\DnD",
    maps_folder="C:\\DnD\\Maps"
)

# 2. Create NPC
create_npc(
    campaign_name="Phandelver",
    name="Gundren Rockseeker",
    role="quest_giver",
    description="Dwarf prospector, friendly and eager",
    location="Phandalin",
    faction="Lords' Alliance"
)

# 3. Add relationship
add_relationship(
    campaign_name="Phandelver",
    from_entity="gundren",
    to_entity="sildar",
    relationship_type="friend",
    description="Long-time allies",
    strength=8
)

# 4. Create quest
create_quest(
    campaign_name="Phandelver",
    name="Find Cragmaw Castle",
    description="Locate Gundren's captors",
    quest_type="main",
    status="accepted",
    quest_giver="sildar",
    reward_gold=200,
    reward_xp=500
)

# 5. Sync to Obsidian
sync_to_obsidian(campaign_name="Phandelver")
```

---

## Integration

### With CAMPAIGN_EVENTS.json:
- Import events from CAMPAIGN_EVENTS.json to timeline
- Auto-create NPCs from events
- Track faction reputation changes
- Link quests to events

### With Combat Engine MCP:
- Link combat encounters to locations
- Track NPC deaths in combat
- Update NPC disposition based on combat outcomes

### With Session Recorder MCP:
- Auto-log timeline events from session logs
- Extract NPC interactions
- Track quest progress from session

---

## Map Integration

**Provide maps via:**
1. Set `maps_folder` when loading wiki
2. Reference maps in location data:
   ```python
   location.map_path = "C:\\DnD\\Maps\\phandalin_map.jpg"
   location.battle_map_path = "C:\\DnD\\Maps\\Battles\\phandalin_tavern_combat.jpg"
   ```
3. Maps auto-embed in Obsidian notes: `![[phandalin_map.jpg]]`

---

## Obsidian Vault Structure

```
Obsidian_Vault/
├── NPCs/
│   ├── Gundren_Rockseeker.md
│   ├── Sildar_Hallwinter.md
│   └── ...
├── Locations/
│   ├── Phandalin.md
│   ├── Wave_Echo_Cave.md
│   └── ...
├── Quests/
│   ├── Find_Cragmaw_Castle.md
│   ├── Rescue_Gundren.md
│   └── ...
└── Timeline/
    └── Campaign_Timeline.md
```

---

## Relationship Graph

**Generate visual graph:**
```python
visualize_relationships(
    campaign_name="Phandelver",
    output_path="C:\\DnD\\Phandelver\\relationships.png"
)
```

**Features:**
- Color-coded by relationship type (green=friend, red=enemy, etc.)
- Node sizes based on importance
- Directed edges showing relationship direction
- Find connections between any two entities

---

## Status

**V1.0:** 5 core tools implemented
**Pattern:** Established for 18 total tools
**Ready:** Install, configure, test

---

**Perfect for:**
- Campaign continuity tracking
- NPC relationship complexity
- Quest management
- Session note organization
- Visual campaign wikis (Obsidian)
- Free, local campaign database

