# Knowledge Graph MCP Server

Track NPC relationships, faction connections, quest dependencies, and consequence chains for D&D 5e campaigns.

## Features

- **Entity Tracking**: NPCs, factions, quests, events, choices, locations, items, PCs
- **Relationship Mapping**: 20+ relationship types (ally, enemy, leads, requires, causes, etc.)
- **Consequence Chain Analysis**: Track how choices lead to cascading effects
- **Quest Dependency Trees**: Visualize which quests unlock others
- **Faction Relationships**: Track alliances, wars, and neutrality
- **Path Finding**: Find connections between any two entities
- **Graph Export**: Export for visualization (D3.js, GraphViz, Obsidian Canvas)
- **Campaign Import**: Auto-import from CAMPAIGN_EVENTS.json

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "knowledge-graph": {
      "command": "python",
      "args": ["knowledge_graph_server.py"],
      "cwd": "C:/DnD/DnD_Cursor/mcp_servers/knowledge_graph"
    }
  }
}
```

## Quick Start

```python
# Add entities
add_entity(entity_id="gundren_rockseeker", entity_type="npc", name="Gundren Rockseeker")
add_entity(entity_id="redbrands", entity_type="faction", name="Redbrands")

# Add relationships
add_relationship(from_id="gundren_rockseeker", to_id="sildar_hallwinter", relationship_type="ally")

# Query
get_entity_connections(entity_id="gundren_rockseeker")
find_connection_path(from_id="gundren_rockseeker", to_id="black_spider")

# Analyze consequences
analyze_consequence_chain(choice_id="spare_glasstaff")

# Export
export_graph(format="json", output_file="graph.json")
```

## Documentation

See `docs/MCP_KNOWLEDGE_GRAPH_COMPLETE.md` for full documentation.

## Entity Types

- **npc**: Non-player characters
- **faction**: Organizations, groups
- **quest**: Quests and objectives
- **event**: Campaign events
- **choice**: Player decisions
- **location**: Places
- **item**: Important items
- **pc**: Player characters

## Relationship Types

### NPC Relationships
ally, enemy, friend, rival, family, mentor, student, employer, employee

### Faction Relationships
member_of, leads, controls, allied_with, at_war_with, neutral_to

### Quest Relationships
requires, unlocks, blocks, related_to, rewards

### Consequence Relationships
caused_by, leads_to, prevents, enables, affects

### Other
knows_about, seeks, protects, threatens, located_in, owns

## State File

Graph state is saved to: `C:/DnD/Campaigns/knowledge_graph.json`

## Use Cases

- **"How is Gundren connected to the Black Spider?"** → `find_connection_path()`
- **"What happens if we spare Glasstaff?"** → `analyze_consequence_chain()`
- **"Which factions are at war?"** → `get_faction_relationships()`
- **"Which quests can we do now?"** → `get_quest_dependencies()`
- **"Who are the key NPCs?"** → `get_graph_stats()` + `get_entity_connections()`

## License

Part of DnD_Cursor project.



