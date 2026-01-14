# Campaign Wiki MCP - Build Complete ✅

**Date:** 2026-01-13  
**Status:** COMPLETE - Ready for installation

---

## 🎉 What Was Built

### **7th MCP Server: Campaign Wiki**

A comprehensive campaign management system with:

✅ **NPC Database** - Full profiles with relationships
✅ **Location Database** - With map integration
✅ **Quest Tracking** - Status workflow management
✅ **Timeline** - Chronicle all campaign events
✅ **Relationship Graphs** - Visual networks with networkx
✅ **Obsidian Sync** - Export as markdown notes
✅ **World Anvil Sync** - Public campaign wiki

---

## 📦 What's Included

### File Structure:
```
mcp_servers/campaign_wiki/
├── wiki_server.py (5 core MCP tools)
├── requirements.txt
├── README.md
├── models/
│   ├── npc.py (NPC, NPCRelationship)
│   ├── location.py (Location, LocationType)
│   ├── quest.py (Quest, QuestStatus)
│   ├── timeline.py (TimelineEvent)
│   └── campaign_wiki.py (Main wiki model)
└── utils/
    ├── relationship_graph.py (networkx graphs)
    ├── obsidian_sync.py (Markdown export)
    ├── world_anvil_sync.py (API integration)
    └── markdown_export.py (Export utilities)
```

---

## 🚀 Key Features

### NPC Management:
- **Full Profiles:** Description, personality, background, motivations, secrets
- **Roles:** ally, enemy, neutral, quest_giver, merchant, faction_leader
- **Status:** Alive/dead, disposition toward party (-10 to +10)
- **Relationships:** Track connections with other NPCs/PCs
- **Quest Links:** Associate NPCs with quests
- **Session Notes:** Track interactions over time

### Location Management:
- **Types:** city, dungeon, tavern, ruins, wilderness, etc.
- **Geography:** Parent locations, regions, coordinates
- **Details:** Population, inhabitants, factions, services
- **History:** Background, current events, rumors
- **🗺️ MAP INTEGRATION:** Attach location maps and battle maps
- **Discovery:** Track visited locations, discovered secrets

### Quest Tracking:
- **Status Workflow:** not_started → available → accepted → in-progress → completed/failed
- **Types:** main, side, personal, faction, bounty, escort, investigation
- **Objectives:** Track completion of individual objectives
- **Rewards:** Gold, XP, items, reputation
- **Relations:** Link to NPCs, locations, other quests
- **Consequences:** Track quest outcomes

### Timeline:
- **Event Types:** combat, discovery, quest milestones, NPC met/death, choices, consequences
- **Tracking:** Session number, in-game date, real date
- **Participants:** Track who was involved
- **Impact:** Consequences, faction reputation changes
- **Significance:** Rate events 1-10

### Relationship Graphs:
- **Types:** family, friend, enemy, rival, romantic, ally, business, mentor/student
- **Strength:** 1-10 rating
- **Visual:** Generate graph images (matplotlib)
- **Analysis:** Find connections between entities
- **Export:** Graphviz DOT format

### Obsidian Integration:
- **Markdown Notes:** Auto-generate with frontmatter
- **Organization:** NPCs/, Locations/, Quests/ folders
- **Internal Links:** Cross-reference between notes
- **Tags:** For filtering and searching
- **Maps:** Embed images in notes

### World Anvil Integration:
- **API Sync:** Export to World Anvil (requires API key)
- **Article Types:** Characters, locations, quests
- **Public Wiki:** Share campaign with players/community
- **ID Tracking:** Track World Anvil IDs for updates

---

## 🔧 Installation

### 1. Install Dependencies:
```powershell
cd "C:\DnD\DnD_Cursor\mcp_servers\campaign_wiki"
pip install -r requirements.txt
```

**Packages:** mcp, pydantic, networkx, python-frontmatter, requests, matplotlib, watchdog, python-dateutil

### 2. Configure MCP:
Add to `.cursor/mcp.json`:
```json
"campaign-wiki": {
  "command": "C:\\Users\\ksist\\AppData\\Local\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\\python.exe",
  "args": ["wiki_server.py"],
  "cwd": "C:\\DnD\\DnD_Cursor\\mcp_servers\\campaign_wiki"
}
```

### 3. Reload Cursor:
`Ctrl+Shift+P` → "Developer: Reload Window"

---

## 📝 Usage Example

```python
# 1. Initialize wiki
create_or_load_wiki(
    campaign_name="Phandelver",
    obsidian_vault="C:\\Users\\ksist\\Documents\\Obsidian\\DnD",
    maps_folder="C:\\DnD\\Maps"
)

# 2. Create NPCs
create_npc(
    campaign_name="Phandelver",
    name="Gundren Rockseeker",
    role="quest_giver",
    description="Friendly dwarf prospector",
    faction="Lords' Alliance",
    location="Phandalin"
)

# 3. Add relationships
add_relationship(
    campaign_name="Phandelver",
    from_entity="gundren",
    to_entity="sildar",
    relationship_type="friend",
    strength=8
)

# 4. Create quest
create_quest(
    campaign_name="Phandelver",
    name="Rescue Gundren",
    description="Find and rescue Gundren from Cragmaw Castle",
    quest_type="main",
    status="accepted",
    quest_giver="sildar",
    reward_gold=200
)

# 5. Sync to Obsidian
sync_to_obsidian(campaign_name="Phandelver")
```

---

## 🗺️ Map Integration

**You mentioned you can provide dungeon maps and battlemaps!**

**How to integrate:**

1. **Set maps folder:**
   ```python
   create_or_load_wiki(
       campaign_name="Phandelver",
       maps_folder="C:\\DnD\\Maps"
   )
   ```

2. **Add maps to locations:**
   ```python
   create_location(
       campaign_name="Phandelver",
       name="Wave Echo Cave",
       location_type="dungeon",
       map_path="C:\\DnD\\Maps\\wave_echo_cave.jpg",
       battle_map_path="C:\\DnD\\Maps\\Battles\\wave_echo_cave_encounter_1.jpg"
   )
   ```

3. **Maps auto-embed in Obsidian:**
   - Location notes will include: `![[wave_echo_cave.jpg]]`
   - Visible in Obsidian vault
   - Easy reference during gameplay

---

## 🔗 Integration

### With CAMPAIGN_EVENTS.json:
- Import events to timeline
- Auto-create NPCs from events
- Track faction reputation
- Link quests to consequences

### With Session Recorder:
- Auto-log timeline events
- Extract NPC interactions
- Track quest progress

### With Combat Engine:
- Link encounters to locations
- Track NPC deaths
- Update dispositions

### With Obsidian:
- Rich campaign notes
- Internal linking
- Tag-based organization
- Visual graphs and maps

### With World Anvil:
- Public campaign wiki
- Share with players
- Community engagement

---

## 📊 Complete MCP Suite

| # | Server | Tools | Status |
|---|--------|-------|--------|
| 1 | dice-roller | 5 | ✅ TESTED |
| 2 | rules-database | 9 | ✅ TESTED |
| 3 | sourcebooks | 4 | ✅ TESTED |
| 4 | music-ambience | 6 | ✅ TESTED |
| 5 | session-recorder | 7 | ✅ TESTED |
| 6 | combat-engine | 9 | ⚙️ READY |
| **7** | **campaign-wiki** | **5** | **⚙️ READY** |

**Total: 45 D&D-specific MCP tools**

---

## ✅ COMPLETE

**You now have THE MOST COMPREHENSIVE D&D AI SYSTEM:**
- 🎲 True random dice rolling with audit trails
- 📖 Instant rules/spells/monsters lookup (391 spells, 499 monsters)
- 📚 Full sourcebook text search (DMG/PHB/MM 2024)
- 🎵 Immersive ambient music and sound effects
- 📝 Automatic session logging and event tracking
- ⚔️ Full combat engine with AI-driven enemies
- 🏰 **Campaign wiki with NPC relationships, quest tracking, and map integration**

**Perfect for:**
- Tracking complex NPC relationships
- Managing multi-threaded quests
- Chronicling campaign history
- Organizing session notes
- Creating visual campaign wikis (Obsidian)
- Sharing campaigns publicly (World Anvil)
- **Integrating dungeon maps and battlemaps**

---

**Install dependencies, configure mcp.json, reload Cursor, and start building your campaign wiki! 🏰📝🗺️**




