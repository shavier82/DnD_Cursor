# Knowledge Graph MCP - Quick Reference

## Entity Types
**npc** | **faction** | **quest** | **event** | **choice** | **location** | **item** | **pc**

## Relationship Types
**NPC:** ally, enemy, friend, rival, family, mentor, student  
**Faction:** member_of, leads, allied_with, at_war_with, neutral_to  
**Quest:** requires, unlocks, blocks, related_to, rewards  
**Consequence:** caused_by, leads_to, prevents, enables, affects  
**Other:** knows_about, seeks, protects, threatens, located_in, owns

---

## Essential Tools

### Building the Graph
```
# Add entities
add_entity(
  entity_id="gundren_rockseeker",
  entity_type="npc",
  name="Gundren Rockseeker",
  data={...}
)

# Add relationships
add_relationship(
  from_id="gundren_rockseeker",
  to_id="sildar_hallwinter",
  relationship_type="ally",
  weight=0.9
)
```

### Querying
```
# Get all connections for an entity
get_entity_connections(entity_id="gundren_rockseeker")

# Find path between two entities
find_connection_path(from_id="gundren", to_id="black_spider")

# Search for entities
search_entities(query="gundren", entity_type="npc")
```

### Analysis
```
# Analyze consequence chain from a choice
analyze_consequence_chain(choice_id="spare_glasstaff", max_depth=10)

# Get all faction relationships
get_faction_relationships()

# Get quest dependencies
get_quest_dependencies()  # All quests
get_quest_dependencies(quest_id="rescue_gundren")  # Specific quest
```

### Data Management
```
# Import from CAMPAIGN_EVENTS.json
import_from_campaign()

# Export for visualization
export_graph(format="json", output_file="graph.json")  # D3.js
export_graph(format="dot", output_file="graph.dot")    # GraphViz

# Get graph statistics
get_graph_stats()
```

---

## Common Workflows

### Track NPC Relationships
```
1. add_entity() for each NPC
2. add_relationship() for connections (ally, enemy, family, etc.)
3. get_entity_connections() to view web
4. find_connection_path() to find links
```

### Track Consequences
```
1. add_entity() for choice (type="choice")
2. add_entity() for each consequence event (type="event")
3. add_relationship() with "leads_to" type
4. analyze_consequence_chain() to see ripple effects
```

### Faction Dynamics
```
1. add_entity() for each faction (type="faction")
2. add_relationship() for NPCs (type="member_of")
3. add_relationship() for faction alliances (type="allied_with", "at_war_with")
4. get_faction_relationships() to view dynamics
```

### Quest Dependencies
```
1. add_entity() for each quest (type="quest")
2. add_relationship() for dependencies (type="requires", "unlocks")
3. get_quest_dependencies() to view tree
4. Check before allowing quest start
```

---

## Integration Commands

**Import from campaign:**
```
import_from_campaign()  # Auto-populate from CAMPAIGN_EVENTS.json
```

**Export for visualization:**
```
export_graph(format="json", output_file="C:/Users/ksist/Documents/Obsidian/DnD/Graphs/campaign.json")
```

**After major choice:**
```
1. add_entity(entity_id="choice_X", entity_type="choice", name="...")
2. add_relationship(from_id="choice_X", to_id="event_Y", relationship_type="leads_to")
3. analyze_consequence_chain(choice_id="choice_X")
```

---

## Quick Examples

### Example 1: NPC Web
```
add_entity(entity_id="gundren", entity_type="npc", name="Gundren Rockseeker")
add_entity(entity_id="sildar", entity_type="npc", name="Sildar Hallwinter")
add_relationship(from_id="gundren", to_id="sildar", relationship_type="ally")
get_entity_connections(entity_id="gundren")
```

### Example 2: Consequence Chain
```
add_entity(entity_id="spare_glasstaff", entity_type="choice", name="Spare Glasstaff")
add_entity(entity_id="glasstaff_escapes", entity_type="event", name="Glasstaff Escapes")
add_relationship(from_id="spare_glasstaff", to_id="glasstaff_escapes", relationship_type="leads_to")
analyze_consequence_chain(choice_id="spare_glasstaff")
```

### Example 3: Faction War
```
add_entity(entity_id="lords_alliance", entity_type="faction", name="Lords' Alliance")
add_entity(entity_id="redbrands", entity_type="faction", name="Redbrands")
add_relationship(from_id="lords_alliance", to_id="redbrands", relationship_type="at_war_with")
get_faction_relationships()
```

---

## Visualization

**D3.js Force Graph:**
```
export_graph(format="json", output_file="graph.json")
# Import into D3.js force-directed graph
```

**GraphViz:**
```
export_graph(format="dot", output_file="graph.dot")
# Render: dot -Tpng graph.dot -o graph.png
```

**Obsidian Canvas:**
```
export_graph(format="json", output_file="C:/Users/ksist/Documents/Obsidian/DnD/Graphs/campaign.json")
# Import into Obsidian Canvas
```

---

## DM Tips

✅ **Track as you go** - Add entities and relationships during sessions  
✅ **Import first** - Use `import_from_campaign()` to bootstrap  
✅ **Visualize regularly** - Export and view graph every few sessions  
✅ **Use for planning** - Find unexpected connections for plot hooks  
✅ **Weight relationships** - Use 0.0-1.0 to show strength (0.1=weak, 0.9=strong)  
✅ **Analyze impact** - Before revealing a secret, check `analyze_consequence_chain()`



