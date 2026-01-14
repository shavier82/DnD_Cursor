# Knowledge Graph MCP Server - Complete Documentation

## Overview

The **Knowledge Graph MCP** is a relationship and consequence tracking system that maps how NPCs, factions, quests, and choices interconnect in your D&D campaign. It visualizes the web of relationships and analyzes the ripple effects of player decisions.

## Features

✅ **Entity Tracking** - NPCs, factions, quests, events, choices, locations, items, PCs  
✅ **Relationship Mapping** - 20+ relationship types (ally, enemy, leads, requires, causes, etc.)  
✅ **Consequence Chain Analysis** - Track how one choice leads to cascading effects  
✅ **Quest Dependency Trees** - Visualize which quests unlock others  
✅ **Faction Relationships** - Track alliances, wars, and neutrality  
✅ **Path Finding** - Find connections between any two entities  
✅ **Graph Export** - Export for visualization (D3.js, GraphViz)  
✅ **Campaign Import** - Auto-import from CAMPAIGN_EVENTS.json  

---

## Entity Types (8 Total)

| Type | Description | Examples |
|------|-------------|----------|
| **npc** | Non-player characters | Gundren Rockseeker, Sildar Hallwinter |
| **faction** | Organizations, groups | Redbrands, Lords' Alliance, Zhentarim |
| **quest** | Quests and objectives | Find Gundren, Clear Cragmaw Hideout |
| **event** | Campaign events | Battle of Phandalin, Gundren's Rescue |
| **choice** | Player decisions | Spare Glasstaff, Ally with Redbrands |
| **location** | Places | Phandalin, Cragmaw Castle, Wave Echo Cave |
| **item** | Important items | Spider Staff, Lightbringer, Lost Mine Map |
| **pc** | Player characters | Eglath, Torgga, Zephyr, Kraval, Pip |

---

## Relationship Types (20+ Total)

### NPC Relationships
- **ally**, **enemy**, **friend**, **rival**, **family**
- **mentor**, **student**, **employer**, **employee**

### Faction Relationships
- **member_of**, **leads**, **controls**
- **allied_with**, **at_war_with**, **neutral_to**

### Quest Relationships
- **requires**, **unlocks**, **blocks**, **related_to**, **rewards**

### Consequence Relationships
- **caused_by**, **leads_to**, **prevents**, **enables**, **affects**

### Location Relationships
- **located_in**, **controls_location**, **owns**

### Other
- **knows_about**, **seeks**, **protects**, **threatens**

---

## MCP Tools (11 Total)

### 1. `add_entity`
**Add an entity to the knowledge graph**

**Parameters:**
- `entity_id` (string, required): Unique ID (e.g., "gundren_rockseeker")
- `entity_type` (string, required): Entity type (npc/faction/quest/event/choice/location/item/pc)
- `name` (string, required): Display name
- `data` (object, optional): Additional data

**Example:**
```json
{
  "entity_id": "gundren_rockseeker",
  "entity_type": "npc",
  "name": "Gundren Rockseeker",
  "data": {
    "race": "Dwarf",
    "status": "alive",
    "location": "Phandalin"
  }
}
```

**Output:**
```json
{
  "success": true,
  "message": "Added npc 'Gundren Rockseeker' (ID: gundren_rockseeker)",
  "entity": {
    "id": "gundren_rockseeker",
    "type": "npc",
    "name": "Gundren Rockseeker"
  }
}
```

---

### 2. `add_relationship`
**Add a relationship between two entities**

**Parameters:**
- `from_id` (string, required): Source entity ID
- `to_id` (string, required): Target entity ID
- `relationship_type` (string, required): Relationship type
- `weight` (number, optional): Relationship strength (default: 1.0)
- `data` (object, optional): Additional data

**Example:**
```json
{
  "from_id": "gundren_rockseeker",
  "to_id": "sildar_hallwinter",
  "relationship_type": "ally",
  "weight": 0.9
}
```

**Output:**
```json
{
  "success": true,
  "message": "Added relationship: Gundren Rockseeker --[ally]--> Sildar Hallwinter",
  "relationship": {
    "from": "Gundren Rockseeker",
    "to": "Sildar Hallwinter",
    "type": "ally",
    "weight": 0.9
  }
}
```

---

### 3. `get_entity_connections`
**Get all connections for an entity**

**Parameters:**
- `entity_id` (string, required): Entity ID
- `relationship_type` (string, optional): Filter by relationship type

**Output:**
```json
{
  "entity": "Gundren Rockseeker",
  "type": "npc",
  "total_connections": 5,
  "connections": [
    {
      "direction": "outgoing",
      "relationship": "ally",
      "connected_to": "sildar_hallwinter",
      "connected_name": "Sildar Hallwinter",
      "connected_type": "npc",
      "weight": 0.9
    },
    {
      "direction": "incoming",
      "relationship": "seeks",
      "connected_to": "redbrands",
      "connected_name": "Redbrands",
      "connected_type": "faction",
      "weight": 1.0
    }
  ]
}
```

---

### 4. `find_connection_path`
**Find shortest path between two entities**

**Parameters:**
- `from_id` (string, required): Starting entity ID
- `to_id` (string, required): Target entity ID

**Output:**
```json
{
  "path_found": true,
  "length": 3,
  "path": [
    "Gundren Rockseeker --[ally]--> Sildar Hallwinter",
    "Sildar Hallwinter --[member_of]--> Lords' Alliance",
    "Lords' Alliance --[at_war_with]--> Redbrands"
  ]
}
```

**Use Case:** "How is Gundren connected to the Redbrands?"

---

### 5. `analyze_consequence_chain`
**Analyze consequence chain from a choice**

**Parameters:**
- `choice_id` (string, required): Choice ID
- `max_depth` (integer, optional): Maximum chain depth (default: 10)

**Output:**
```json
{
  "choice_id": "spare_glasstaff",
  "chain_length": 4,
  "consequence_chain": [
    {
      "id": "spare_glasstaff",
      "name": "Party spares Glasstaff",
      "type": "choice",
      "depth": 0
    },
    {
      "id": "glasstaff_escapes",
      "name": "Glasstaff escapes Phandalin",
      "type": "event",
      "depth": 1
    },
    {
      "id": "black_spider_warned",
      "name": "Black Spider learns of party",
      "type": "event",
      "depth": 2
    },
    {
      "id": "wave_echo_ambush",
      "name": "Ambush at Wave Echo Cave",
      "type": "event",
      "depth": 3
    }
  ]
}
```

**Use Case:** "What happens if we spare Glasstaff?"

---

### 6. `get_faction_relationships`
**Get all faction-to-faction relationships**

**Output:**
```json
{
  "total_faction_relationships": 6,
  "relationships": [
    {
      "from": "Lords' Alliance",
      "to": "Redbrands",
      "relationship": "at_war_with",
      "weight": 1.0
    },
    {
      "from": "Zhentarim",
      "to": "Lords' Alliance",
      "relationship": "rival",
      "weight": 0.8
    },
    {
      "from": "Redbrands",
      "to": "Black Spider",
      "relationship": "allied_with",
      "weight": 0.7
    }
  ]
}
```

---

### 7. `get_quest_dependencies`
**Get quest dependency tree**

**Parameters:**
- `quest_id` (string, optional): Specific quest ID (shows all if omitted)

**Output:**
```json
{
  "quest_id": "all",
  "total_dependencies": 8,
  "dependencies": [
    {
      "from": "Find Gundren",
      "to": "Clear Cragmaw Hideout",
      "dependency": "unlocks"
    },
    {
      "from": "Clear Cragmaw Hideout",
      "to": "Find Cragmaw Castle",
      "dependency": "unlocks"
    },
    {
      "from": "Find Cragmaw Castle",
      "to": "Rescue Gundren",
      "dependency": "requires"
    }
  ]
}
```

---

### 8. `import_from_campaign`
**Import entities and relationships from CAMPAIGN_EVENTS.json**

**Output:**
```json
{
  "success": true,
  "imported_count": 47,
  "message": "Imported 47 entities from CAMPAIGN_EVENTS.json"
}
```

**Use Case:** Auto-populate graph from existing campaign data

---

### 9. `export_graph`
**Export graph for visualization**

**Parameters:**
- `format` (string, optional): "json" (D3.js), "dot" (GraphViz), or "raw" (default: "json")
- `output_file` (string, optional): Output file path

**Output (JSON format):**
```json
{
  "nodes": [
    {"id": "gundren_rockseeker", "name": "Gundren Rockseeker", "type": "npc", "group": 0},
    {"id": "redbrands", "name": "Redbrands", "type": "faction", "group": 1}
  ],
  "links": [
    {"source": "gundren_rockseeker", "target": "sildar_hallwinter", "type": "ally", "weight": 0.9}
  ]
}
```

**Use Case:** Export for D3.js visualization or Obsidian Canvas

---

### 10. `get_graph_stats`
**Get knowledge graph statistics**

**Output:**
```json
{
  "total_nodes": 52,
  "total_edges": 87,
  "node_types": {
    "npc": 23,
    "faction": 8,
    "quest": 12,
    "event": 6,
    "choice": 3
  },
  "edge_types": {
    "ally": 15,
    "enemy": 8,
    "member_of": 23,
    "requires": 10,
    "leads_to": 12
  },
  "last_updated": "2026-01-13T15:30:00"
}
```

---

### 11. `search_entities`
**Search for entities by name or type**

**Parameters:**
- `query` (string, required): Search query
- `entity_type` (string, optional): Filter by type

**Output:**
```json
{
  "query": "gundren",
  "entity_type": "all",
  "total_results": 2,
  "results": [
    {"id": "gundren_rockseeker", "name": "Gundren Rockseeker", "type": "npc"},
    {"id": "rescue_gundren", "name": "Rescue Gundren", "type": "quest"}
  ]
}
```

---

## Usage Examples

### Example 1: Building the NPC Web
```
# Add NPCs
→ add_entity(entity_id="gundren_rockseeker", entity_type="npc", name="Gundren Rockseeker")
→ add_entity(entity_id="sildar_hallwinter", entity_type="npc", name="Sildar Hallwinter")
→ add_entity(entity_id="glasstaff", entity_type="npc", name="Glasstaff")

# Add relationships
→ add_relationship(from_id="gundren_rockseeker", to_id="sildar_hallwinter", relationship_type="ally")
→ add_relationship(from_id="glasstaff", to_id="redbrands", relationship_type="leads")
→ add_relationship(from_id="gundren_rockseeker", to_id="glasstaff", relationship_type="enemy")

# Query connections
→ get_entity_connections(entity_id="gundren_rockseeker")
```

### Example 2: Tracking Consequence Chains
```
# Add a player choice
→ add_entity(entity_id="choice_spare_glasstaff", entity_type="choice", name="Party spares Glasstaff")

# Add consequence events
→ add_entity(entity_id="event_glasstaff_escapes", entity_type="event", name="Glasstaff escapes")
→ add_entity(entity_id="event_black_spider_warned", entity_type="event", name="Black Spider warned")

# Link consequences
→ add_relationship(from_id="choice_spare_glasstaff", to_id="event_glasstaff_escapes", relationship_type="leads_to")
→ add_relationship(from_id="event_glasstaff_escapes", to_id="event_black_spider_warned", relationship_type="leads_to")

# Analyze impact
→ analyze_consequence_chain(choice_id="choice_spare_glasstaff")
```

### Example 3: Faction Web
```
# Add factions
→ add_entity(entity_id="lords_alliance", entity_type="faction", name="Lords' Alliance")
→ add_entity(entity_id="redbrands", entity_type="faction", name="Redbrands")
→ add_entity(entity_id="zhentarim", entity_type="faction", name="Zhentarim")

# Add faction relationships
→ add_relationship(from_id="lords_alliance", to_id="redbrands", relationship_type="at_war_with")
→ add_relationship(from_id="zhentarim", to_id="lords_alliance", relationship_type="rival")

# Query faction dynamics
→ get_faction_relationships()
```

### Example 4: Quest Dependencies
```
# Add quests
→ add_entity(entity_id="quest_find_gundren", entity_type="quest", name="Find Gundren")
→ add_entity(entity_id="quest_clear_hideout", entity_type="quest", name="Clear Cragmaw Hideout")
→ add_entity(entity_id="quest_find_castle", entity_type="quest", name="Find Cragmaw Castle")

# Add dependencies
→ add_relationship(from_id="quest_find_gundren", to_id="quest_clear_hideout", relationship_type="unlocks")
→ add_relationship(from_id="quest_clear_hideout", to_id="quest_find_castle", relationship_type="unlocks")

# View dependency tree
→ get_quest_dependencies()
```

---

## Integration with Other Systems

### With CAMPAIGN_EVENTS.json
```
# Auto-import all events and participants
→ import_from_campaign()

# This creates:
- Event nodes for each campaign event
- NPC nodes for all participants
- "participated_in" relationships
- Choice nodes for decision points
- "leads_to" relationships for consequences
```

### With CHOICES_AND_CONSEQUENCES System
```
# After a player choice
1. Add choice node: add_entity(entity_id="choice_X", entity_type="choice", name="...")
2. Add consequence event: add_entity(entity_id="event_Y", entity_type="event", name="...")
3. Link them: add_relationship(from_id="choice_X", to_id="event_Y", relationship_type="leads_to")
4. Analyze impact: analyze_consequence_chain(choice_id="choice_X")
```

### With Obsidian Sync
```
# Export graph for Obsidian Canvas
→ export_graph(format="json", output_file="C:/Users/ksist/Documents/Obsidian/DnD/Graphs/knowledge_graph.json")

# Then import into Obsidian Canvas for visual editing
```

### With Campaign Wiki
```
# For each NPC in the wiki
1. Add NPC to knowledge graph
2. Add relationships to other NPCs, factions, quests
3. Link to wiki page in data field
```

---

## Visualization

### D3.js Force Graph
```javascript
// Export graph
→ export_graph(format="json", output_file="graph.json")

// Use with D3.js force-directed graph
const graph = JSON.parse(graphData);
const simulation = d3.forceSimulation(graph.nodes)
  .force("link", d3.forceLink(graph.links).id(d => d.id))
  .force("charge", d3.forceManyBody().strength(-100))
  .force("center", d3.forceCenter(width / 2, height / 2));
```

### GraphViz
```bash
# Export to DOT format
→ export_graph(format="dot", output_file="graph.dot")

# Render with GraphViz
dot -Tpng graph.dot -o graph.png
```

### Obsidian Canvas
```
# Export JSON and import into Obsidian Canvas
→ export_graph(format="json", output_file="C:/Users/ksist/Documents/Obsidian/DnD/Graphs/campaign_graph.json")

# Manually create Canvas file or use a converter script
```

---

## Advanced Analysis

### Find Key NPCs (Most Connected)
```python
# Get all NPCs with their connection counts
npcs = []
for npc_id, npc_data in graph.nodes.items():
    if npc_data["type"] == "npc":
        connections = graph.get_connections(npc_id)
        npcs.append({"name": npc_data["name"], "connections": len(connections)})

# Sort by connections
npcs.sort(key=lambda x: x["connections"], reverse=True)
```

### Find Faction Influence
```python
# Count all NPCs in each faction
for faction_id, faction_data in graph.nodes.items():
    if faction_data["type"] == "faction":
        members = graph.get_connections(faction_id, "member_of")
        print(f"{faction_data['name']}: {len(members)} members")
```

### Predict Quest Availability
```python
# Check which quests are unlocked
completed_quests = ["quest_find_gundren", "quest_clear_hideout"]
available_quests = []

for quest_id, quest_data in graph.nodes.items():
    if quest_data["type"] == "quest" and quest_id not in completed_quests:
        # Check if all requirements are met
        requirements = graph.get_connections(quest_id, "requires")
        if all(req["connected_to"] in completed_quests for req in requirements):
            available_quests.append(quest_data["name"])
```

---

## Configuration

**Graph State File:**
`C:/DnD/Campaigns/knowledge_graph.json`

**Campaign Events Source:**
`C:/DnD/Campaigns/CAMPAIGN_EVENTS.json`

**Auto-Import:** Use `import_from_campaign()` to populate graph from existing campaign data.

---

## Technical Details

**MCP Server:** `knowledge-graph`  
**Port:** stdio (no port needed)  
**Dependencies:** `mcp`, `networkx`  
**Language:** Python 3.10+  
**Graph Library:** NetworkX (for path finding and analysis)

**File Locations:**
- Server: `C:\DnD\DnD_Cursor\mcp_servers\knowledge_graph\knowledge_graph_server.py`
- State: `C:\DnD\Campaigns\knowledge_graph.json`

---

## Quick Reference Card

| Task | Tool | Parameters |
|------|------|------------|
| Add entity | `add_entity()` | entity_id, entity_type, name, data |
| Add relationship | `add_relationship()` | from_id, to_id, relationship_type, weight |
| Get connections | `get_entity_connections()` | entity_id, relationship_type |
| Find path | `find_connection_path()` | from_id, to_id |
| Analyze consequences | `analyze_consequence_chain()` | choice_id, max_depth |
| Faction relationships | `get_faction_relationships()` | None |
| Quest dependencies | `get_quest_dependencies()` | quest_id (optional) |
| Import campaign data | `import_from_campaign()` | None |
| Export graph | `export_graph()` | format, output_file |
| Graph stats | `get_graph_stats()` | None |
| Search entities | `search_entities()` | query, entity_type |

---

## Tips for DMs

1. **Start small:** Add NPCs and factions first, then build relationships
2. **Track consequences:** After every major choice, add it to the graph and link consequences
3. **Visualize quarterly:** Export and visualize the graph every few sessions
4. **Use for planning:** Check `find_connection_path()` to discover unexpected NPC connections
5. **Quest gating:** Use quest dependencies to ensure logical progression
6. **Faction dynamics:** Update faction relationships as alliances shift

---

✅ **Knowledge Graph MCP is ready!**

Test with: `add_entity()`, `add_relationship()`, `import_from_campaign()`



