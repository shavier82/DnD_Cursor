# Knowledge Graph MCP - Campaign Relationship Tracking

## What Is This For?

The **Knowledge Graph MCP** tracks entities and their relationships in your D&D campaign. Think of it as a **network map** of how everything connects.

---

## Core Purpose

### What It Does
- **Tracks entities**: NPCs, locations, items, factions
- **Maps relationships**: Who knows whom, who's allied with whom, where things are located
- **Queries connections**: "Show me everyone connected to Gundren Rockseeker"
- **Visualizes the web**: Creates a graph of campaign connections

### What It's NOT
- ❌ Not a character sheet system (that's Obsidian Sync)
- ❌ Not detailed NPC storage (that's Campaign Wiki)
- ❌ Not session logging (that's Session Recorder)
- ❌ Not rules/mechanics (that's Rules Database)

---

## When to Use It

### Use Cases

#### 1. Track NPC Relationships
```python
# Gundren knows Sildar
add_relationship(
    from_entity="Gundren Rockseeker",
    to_entity="Sildar Hallwinter",
    relationship="ally"
)

# Nezznar is enemy of Gundren
add_relationship(
    from_entity="Nezznar the Black Spider",
    to_entity="Gundren Rockseeker",
    relationship="enemy"
)
```

**Result:** Query "Gundren Rockseeker" → Shows allies and enemies

#### 2. Track Faction Membership
```python
# Sildar is member of Lords' Alliance
add_relationship(
    from_entity="Sildar Hallwinter",
    to_entity="Lords' Alliance",
    relationship="member_of"
)

# Party members are also members
add_relationship(
    from_entity="Brevin",
    to_entity="Lords' Alliance",
    relationship="member_of"
)
```

**Result:** Query "Lords' Alliance" → Shows all members

#### 3. Track Item Locations
```python
# Forge of Spells is located in Wave Echo Cave
add_relationship(
    from_entity="Forge of Spells",
    to_entity="Wave Echo Cave",
    relationship="located_in"
)

# Psionic Disruptor is owned by Brevin
add_relationship(
    from_entity="Psionic Disruptor",
    to_entity="Brevin",
    relationship="owned_by"
)
```

**Result:** Query "Wave Echo Cave" → Shows what's located there

#### 4. Track Quest Connections
```python
# Quest involves NPC
add_relationship(
    from_entity="Defeat the Black Spider",
    to_entity="Nezznar the Black Spider",
    relationship="target"
)

# Quest given by NPC
add_relationship(
    from_entity="Defeat the Black Spider",
    to_entity="Gundren Rockseeker",
    relationship="quest_giver"
)
```

**Result:** Query quest → Shows all connected entities

#### 5. Track Consequence Chains
```python
# Choice leads to consequence
add_relationship(
    from_entity="Destroyed Forge of Spells",
    to_entity="Economic Impact on Phandalin",
    relationship="causes"
)

# Consequence affects entity
add_relationship(
    from_entity="Economic Impact on Phandalin",
    to_entity="Gundren Rockseeker",
    relationship="affects"
)
```

**Result:** Query choice → Shows ripple effects

---

## How It Differs From Campaign Wiki

### Campaign Wiki MCP
- Stores **detailed information** about NPCs, quests, locations
- Like a **database table** with full stat blocks and descriptions
- CRUD operations (Create, Read, Update, Delete)
- Example: "Gundren Rockseeker is a dwarf, level 3 fighter, AC 16, HP 28..."

### Knowledge Graph MCP
- Stores **relationships** between entities
- Like a **network graph** showing connections
- Graph traversal and queries
- Example: "Gundren → allied_with → Sildar, enemy_of → Nezznar, member_of → Lords' Alliance"

### They Work Together

```
Campaign Wiki (Details):          Knowledge Graph (Connections):
┌─────────────────────┐          ┌─────────────────────────────┐
│ Gundren Rockseeker  │          │ Gundren ──ally──> Sildar    │
│ - Race: Dwarf       │    +     │ Gundren ──enemy──> Nezznar  │
│ - Class: Fighter 3  │          │ Gundren ──member──> Alliance│
│ - AC: 16, HP: 28    │          │ Gundren ──located──> Prison │
│ - Personality: ...  │          └─────────────────────────────┘
└─────────────────────┘

         ↓
Combined View: Full NPC with relationship context
```

---

## MCP Functions

### 1. `add_entity`
Register a new entity in the graph.

```python
mcp_knowledge-graph_add_entity(
    name="Lord Ruxithid",
    entity_type="npc",
    description="Mind flayer controlling psionic goblin network"
)
```

**Entity Types:**
- `npc` - Non-player characters
- `location` - Places (cities, dungeons, regions)
- `item` - Objects (artifacts, weapons, quest items)
- `faction` - Organizations (Lords' Alliance, Zhentarim)
- `quest` - Objectives and missions
- `event` - Significant occurrences
- `choice` - Player decisions
- `consequence` - Results of choices

### 2. `add_relationship`
Connect two entities with a relationship.

```python
mcp_knowledge-graph_add_relationship(
    from_entity="Lord Ruxithid",
    to_entity="Vrek Snapjaw",
    relationship="commands"
)
```

**Common Relationship Types:**
- `ally` / `enemy` - Friendly/hostile relationships
- `member_of` - Faction membership
- `located_in` - Physical location
- `owned_by` - Possession
- `quest_giver` / `target` - Quest connections
- `parent_of` / `child_of` - Family
- `commands` / `serves` - Hierarchy
- `knows` - Awareness/acquaintance
- `loves` / `hates` - Strong emotions
- `causes` / `affected_by` - Consequence chains

### 3. `query_entity`
Get all information and connections for an entity.

```python
mcp_knowledge-graph_query_entity(
    name="Gundren Rockseeker"
)
```

**Returns:**
```json
{
  "entity": "Gundren Rockseeker",
  "info": {
    "type": "npc",
    "description": "Dwarf merchant seeking Wave Echo Cave"
  },
  "relationships": [
    {
      "from": "Gundren Rockseeker",
      "to": "Sildar Hallwinter",
      "type": "ally"
    },
    {
      "from": "Nezznar the Black Spider",
      "to": "Gundren Rockseeker",
      "type": "enemy"
    },
    {
      "from": "Gundren Rockseeker",
      "to": "Wave Echo Cave",
      "type": "seeks"
    }
  ]
}
```

---

## Usage Examples

### Example 1: Party Joins Lords' Alliance

```python
# When party joins faction
for character in ["Brevin", "Eglath Bearkiller", "Torgga Brawnanvil", 
                  "Vandross Ephrates", "Zephyr Sparkwhistle"]:
    add_relationship(
        from_entity=character,
        to_entity="Lords' Alliance",
        relationship="member_of"
    )
```

**Query:** "Who's in Lords' Alliance?"
```python
query_entity("Lords' Alliance")
# Returns: All party members + Sildar + other members
```

### Example 2: Track Enemy Network

```python
# Build enemy hierarchy
add_entity("Lord Ruxithid", "npc", "Mind flayer leader")
add_entity("Vrek Snapjaw", "npc", "Goblin psi commander")
add_entity("Shaman", "npc", "Controls psionic crystals")

add_relationship("Lord Ruxithid", "Vrek Snapjaw", "commands")
add_relationship("Lord Ruxithid", "Shaman", "commands")
add_relationship("Shaman", "Psionic Crystal Network", "controls")
```

**Query:** "Who does Ruxithid command?"
```python
query_entity("Lord Ruxithid")
# Returns: Vrek Snapjaw, Shaman
```

### Example 3: Consequence Tracking

```python
# Party destroyed Forge of Spells
add_entity(
    "Forge Destruction",
    "event",
    "Party destroyed Forge of Spells to prevent Black Spider"
)

add_relationship("Forge Destruction", "Gundren Rockseeker", "disappoints")
add_relationship("Forge Destruction", "Phandalin Economy", "harms")
add_relationship("Forge Destruction", "Black Spider", "thwarts")
```

**Query:** "What did destroying the forge affect?"
```python
query_entity("Forge Destruction")
# Returns: Gundren (disappointed), Economy (harmed), Black Spider (thwarted)
```

---

## Integration with Other MCPs

### With Campaign Wiki
```python
# Campaign Wiki: Store detailed NPC info
campaign_wiki.create_npc(
    name="Lord Ruxithid",
    race="Mind Flayer",
    stats={...}
)

# Knowledge Graph: Store relationships
knowledge_graph.add_relationship(
    "Lord Ruxithid",
    "Vrek Snapjaw",
    "commands"
)
```

### With Session Recorder
```python
# Session Recorder: Log event
session_recorder.log_event(
    "choice",
    "Party allied with Gundren"
)

# Knowledge Graph: Track relationship
knowledge_graph.add_relationship(
    "Party",
    "Gundren Rockseeker",
    "ally"
)
```

### With Choices & Consequences System
```python
# Choice made
add_entity("Destroyed Forge", "choice", "...")

# Consequence created
add_entity("Economic Impact", "consequence", "...")

# Link them
add_relationship("Destroyed Forge", "Economic Impact", "causes")

# Track who's affected
add_relationship("Economic Impact", "Gundren", "affects")
add_relationship("Economic Impact", "Phandalin", "affects")
```

---

## Visualization Potential

While the MCP doesn't currently visualize, the data structure supports:

### Graph View (Future)
```
         Lords' Alliance
              ↑
    ┌─────────┼─────────┐
  Brevin   Sildar   Vandross
    ↓                  ↓
  Zephyr          Eglath
```

### Faction Network (Future)
```
    Lords' Alliance ──enemy──> Zhentarim
           ↓                        ↓
      [5 members]              [? members]
           ↓                        ↓
    [Active quests]           [Enemy quests]
```

### Consequence Chain (Future)
```
Destroyed Forge
    ├──> disappoints ──> Gundren
    ├──> harms ──> Phandalin Economy
    │       └──> affects ──> Merchants
    └──> thwarts ──> Black Spider
```

---

## When NOT to Use Knowledge Graph

### Don't Use For:

1. **Character Stats**
   - Use Obsidian Sync instead
   - Knowledge Graph: Relationships only

2. **Combat Tracking**
   - Use Combat Engine
   - Knowledge Graph: No real-time state

3. **Detailed NPC Info**
   - Use Campaign Wiki
   - Knowledge Graph: Connections only

4. **Session Events**
   - Use Session Recorder
   - Knowledge Graph: Long-term relationships

5. **Rules Lookups**
   - Use Rules Database
   - Knowledge Graph: World data only

---

## Best Practices

### 1. Add Entities First
```python
# ❌ BAD: Add relationship before entities exist
add_relationship("Unknown NPC", "Party", "ally")

# ✅ GOOD: Add entities first
add_entity("New NPC", "npc", "Helpful merchant")
add_relationship("New NPC", "Party", "ally")
```

### 2. Use Consistent Naming
```python
# ❌ BAD: Inconsistent names
add_entity("Gundren", "npc", "...")
add_relationship("Gundren Rockseeker", "Sildar", "ally")

# ✅ GOOD: Exact same names
add_entity("Gundren Rockseeker", "npc", "...")
add_relationship("Gundren Rockseeker", "Sildar Hallwinter", "ally")
```

### 3. Use Standard Relationship Types
```python
# ❌ BAD: Random types
add_relationship("NPC1", "NPC2", "is friends with")
add_relationship("NPC3", "NPC4", "friend")
add_relationship("NPC5", "NPC6", "friendly")

# ✅ GOOD: Standard type
add_relationship("NPC1", "NPC2", "ally")
add_relationship("NPC3", "NPC4", "ally")
add_relationship("NPC5", "NPC6", "ally")
```

### 4. Track Both Directions
```python
# ✅ GOOD: Track command hierarchy both ways
add_relationship("Lord Ruxithid", "Vrek Snapjaw", "commands")
add_relationship("Vrek Snapjaw", "Lord Ruxithid", "serves")
```

---

## Data Persistence

### Current: In-Memory Only
⚠️ **WARNING:** Current implementation stores data in memory only. It's lost when MCP restarts.

### Needed: File-Based Storage
```python
# TODO: Save to JSON file
self.graph_file = campaign_path / "knowledge_graph.json"
self.save_graph()
self.load_graph()
```

### Future: Graph Database
Consider Neo4j or similar for large campaigns with thousands of relationships.

---

## Summary

**Knowledge Graph MCP** = **Relationship Mapper**

Use it to:
✅ Track who knows whom
✅ Map faction memberships
✅ Connect quests to NPCs
✅ Chain choices to consequences
✅ Visualize the campaign network

Don't use it for:
❌ Character stats (use Obsidian Sync)
❌ Detailed NPC info (use Campaign Wiki)
❌ Session logs (use Session Recorder)
❌ Rules/mechanics (use Rules Database)

**Think of it as:** The web connecting everything in your campaign world.
