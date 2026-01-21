# NPC Automation System - Complete Guide

**Comprehensive NPC tracking with knowledge, interactions, disposition, and consequences**

---

## Overview

The NPC Automation System provides **dynamic, session-to-session tracking** of:
- ✅ What NPCs know (information revealed during sessions)
- ✅ Interaction history (conversations, trades, conflicts)
- ✅ Disposition changes (how NPCs feel about the party)
- ✅ Faction reputation (party standing with organizations)
- ✅ Consequence propagation (how party actions affect related NPCs)

---

## Architecture

```
┌─────────────────────────────────────────┐
│         SESSION RECORDER MCP            │
│  (Logs events during gameplay)          │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      OBSIDIAN SYNC MCP (Enhanced)       │
│  - update_npc_knowledge()               │
│  - log_npc_interaction()                │
│  - update_npc_disposition()             │
│  - update_faction_reputation()          │
│  - propagate_consequence()              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         OBSIDIAN VAULT (NPCs/)          │
│  - Knowledge sections (what they know)  │
│  - Interaction logs (conversation hist) │
│  - Disposition tracking (attitude)      │
│  - Consequence tracking (ripple effects)│
└─────────────────────────────────────────┘
```

---

## Tool 1: `create_npc`

**Purpose:** Create a new NPC file when the party meets them

### Usage:
```python
create_npc(
    npc_name="Gwyn Oresong",
    role="ally",
    description="Elderly human sage with white hair and piercing blue eyes. Expert in arcane crystals and ancient magic.",
    location="Phandalin",
    faction="Scholars of Candlekeep",
    disposition=5
)
```

### Parameters:
- **npc_name** (required): The NPC's full name
- **role** (optional): ally, enemy, neutral, quest_giver, merchant, etc. (default: "neutral")
- **description** (optional): Physical description and personality
- **location** (optional): Where they are found
- **faction** (optional): Faction affiliation
- **disposition** (optional): Initial disposition -10 to +10 (default: 0)

### What It Does:
1. Creates a new markdown file in `NPCs/` folder
2. Sets up proper frontmatter with metadata
3. Initializes sections for Description, Relationships
4. Sets initial disposition and mood

### Output in Obsidian:
```markdown
---
type: npc
role: ally
disposition: 5
alive: true
faction: Scholars of Candlekeep
location: Phandalin
---

# Gwyn Oresong

**Faction:** [[Scholars of Candlekeep]]
**Location:** [[Phandalin]]
**Role:** ally
**Disposition:** 5/10 (Friendly)

## Description
Elderly human sage with white hair and piercing blue eyes. Expert in arcane crystals and ancient magic.

## Relationships
*Add relationships here*
```

### Error Handling:
- If NPC already exists, returns error and suggests using update tools instead

---

## Tool 2: `update_npc_knowledge`

**Purpose:** Track what information NPCs learn during sessions

### Usage:
```python
update_npc_knowledge(
    npc_name="Harbin Wester",
    information="Party discovered psionic goblins led by Ruxithid, an aberrant mind-flayer kin",
    session_number=5,
    revealed_by="Party (full briefing)",
    npc_reaction="Shocked and deeply concerned. Immediately committed town resources to party's cause."
)
```

### What It Does:
1. Adds entry to NPC's "## Knowledge" section
2. Updates metadata with structured knowledge data
3. Timestamps the revelation
4. Records who revealed it and NPC's reaction

### Output in Obsidian:
```markdown
## Knowledge
- **Session 5** (2026-01-13): Party discovered psionic goblins led by Ruxithid, an aberrant mind-flayer kin *(Learned from: Party (full briefing))*
  - **Reaction:** Shocked and deeply concerned. Immediately committed town resources to party's cause.
```

---

## Tool 3: `log_npc_interaction`

**Purpose:** Log interactions and automatically update disposition

### Usage:
```python
log_npc_interaction(
    npc_name="Harbin Wester",
    interaction_type="briefing",
    information_exchanged=[
        "Ruxithid threat details",
        "Obelisk Core location (Zorzula's Rest)",
        "Party's plan to assault the Deep Temple",
        "Request for town militia support"
    ],
    disposition_change=+3,  # Party saved the town
    session_number=5,
    notes="Harbin pledged full support. Offered supplies and militia for the assault."
)
```

### What It Does:
1. Creates timestamped interaction log
2. **Auto-updates disposition** (current + change, clamped to -10/+10)
3. Updates "Last Seen" timestamp
4. Records information exchanged
5. Adds notes about the interaction

### Output in Obsidian:
```markdown
## Interactions

### Briefing - 2026-01-13 21:45
**Session 5**

**Information Exchanged:**
- Ruxithid threat details
- Obelisk Core location (Zorzula's Rest)
- Party's plan to assault the Deep Temple
- Request for town militia support

**Disposition Change:** +3 (improved) → **Current: 8/10**

**Notes:** Harbin pledged full support. Offered supplies and militia for the assault.
```

---

## Tool 4: `update_npc_disposition`

**Purpose:** Quick disposition updates without full interaction log

### Usage:
```python
update_npc_disposition(
    npc_name="Sildar Hallwinter",
    disposition_change=+2,
    reason="Party rescued Gundren Rockseeker"
)
```

### What It Does:
1. Updates disposition value
2. Updates disposition line in NPC stats
3. Records reason for change

### Output in Obsidian:
```markdown
**Disposition:** 7/10 (Friendly) - *Party rescued Gundren Rockseeker*
```

---

## Tool 5: `update_faction_reputation`

**Purpose:** Track party reputation with factions/organizations

### Usage:
```python
update_faction_reputation(
    faction_name="Lords' Alliance",
    reputation_change=+25,
    reason="Saved Phandalin from psionic goblin siege, eliminated Vrek Snapjaw"
)
```

### What It Does:
1. Creates or updates faction entry in `Factions.md`
2. Tracks reputation on -100 to +100 scale
3. Maintains reputation history with timestamps

### Output in Obsidian (`Factions.md`):
```markdown
# Factions & Reputation

## Lords' Alliance
**Current Reputation:** 45/100

### Reputation History
- **2026-01-13**: Saved Phandalin from psionic goblin siege, eliminated Vrek Snapjaw (+25 reputation)
- **2026-01-10**: Cleared Redbrand Hideout, arrested Glasstaff (+20 reputation)
```

---

## Tool 6: `propagate_consequence`

**Purpose:** Automatically update related NPCs when major events occur

### Usage:
```python
propagate_consequence(
    event_description="Party killed Vrek Snapjaw and decimated the goblin forces at Phandalin",
    affected_npcs=[
        "Harbin Wester",
        "Sildar Hallwinter",
        "Daran Edermath",
        "Sister Garaele"
    ],
    consequence_type="positive",
    session_number=5
)
```

### What It Does:
1. Adds consequence entry to each affected NPC
2. Creates "## Consequences" section if needed
3. Tracks how party actions ripple through the world

### Output in Obsidian (for each NPC):
```markdown
## Consequences
*How party actions have affected this NPC:*

- **Session 5** (2026-01-13): Party killed Vrek Snapjaw and decimated the goblin forces at Phandalin *(positive)*
```

---

## Tool 7: `get_npc_data`

**Purpose:** Retrieve NPC data for AI decision-making

### Usage:
```python
get_npc_data(npc_name="Harbin Wester")
```

### Returns:
```json
{
  "metadata": {
    "type": "npc",
    "role": "quest_giver",
    "disposition": 8,
    "alive": true,
    "last_seen": "2026-01-13 21:45",
    "knowledge_entries": [
      {
        "session": 5,
        "date": "2026-01-13",
        "information": "Party discovered psionic goblins...",
        "source": "Party (full briefing)"
      }
    ]
  },
  "content": "... (full markdown content) ..."
}
```

---

## Workflow Examples

### Example 1: Post-Combat Briefing

```python
# 1. Log the interaction
log_npc_interaction(
    npc_name="Harbin Wester",
    interaction_type="post-combat briefing",
    information_exchanged=[
        "Goblin siege repelled",
        "Vrek Snapjaw captured and interrogated",
        "Ruxithid threat revealed",
        "Zorzula's Rest location identified"
    ],
    disposition_change=+3,
    session_number=5,
    notes="Harbin extremely grateful. Town owes party a great debt."
)

# 2. Update knowledge
update_npc_knowledge(
    npc_name="Harbin Wester",
    information="Ruxithid is a mind-flayer kin controlling psionic goblins via Obelisk fragments",
    session_number=5,
    revealed_by="Party interrogation of Vrek Snapjaw",
    npc_reaction="Horrified. Realizes threat is existential, not just local banditry."
)

# 3. Update faction rep
update_faction_reputation(
    faction_name="Phandalin Militia",
    reputation_change=+30,
    reason="Defended town during dawn siege, saved dozens of lives"
)

# 4. Propagate to related NPCs
propagate_consequence(
    event_description="Party saved Phandalin from annihilation during goblin dawn siege",
    affected_npcs=["Sildar Hallwinter", "Daran Edermath", "Sister Garaele", "Toblen Stonehill"],
    consequence_type="positive",
    session_number=5
)
```

---

### Example 2: Betrayal Scenario

```python
# Party betrays an NPC
log_npc_interaction(
    npc_name="Reidoth the Druid",
    interaction_type="betrayal",
    information_exchanged=[
        "Party promised to spare Venomfang",
        "Party killed Venomfang for loot"
    ],
    disposition_change=-8,  # Massive drop
    session_number=3,
    notes="Reidoth witnessed the betrayal. Furious. Will not aid party again."
)

# Propagate to Reidoth's allies
propagate_consequence(
    event_description="Party betrayed Reidoth by killing Venomfang despite their promise",
    affected_npcs=["Qelline Alderleaf", "Sister Garaele"],  # Reidoth's friends
    consequence_type="negative",
    session_number=3
)

# Update faction rep
update_faction_reputation(
    faction_name="Emerald Enclave",
    reputation_change=-40,
    reason="Betrayed Reidoth, killed dragon despite druid's protection"
)
```

---

### Example 3: Secret Revealed

```python
# Party discovers and shares a secret
update_npc_knowledge(
    npc_name="Sildar Hallwinter",
    information="Iarno Albrek (Glasstaff) was the Redbrand leader and Black Spider agent",
    session_number=2,
    revealed_by="Party (showed evidence from hideout)",
    npc_reaction="Devastated. Iarno was his friend and fellow Lord's Alliance member. Feels personally responsible."
)

# This affects Sildar's disposition toward the party (they delivered bad news)
update_npc_disposition(
    npc_name="Sildar Hallwinter",
    disposition_change=-1,  # Slight drop (not party's fault, but painful)
    reason="Bearer of bad news about Iarno's betrayal"
)
```

---

## Integration with Session Recorder

### Automatic Logging During Sessions

When using Session Recorder MCP, you can automatically trigger NPC updates:

```python
# During session, when party talks to NPC:
log_event(
    event_type="npc_interaction",
    content="Party briefed Harbin Wester on Ruxithid threat",
    metadata={
        "npc": "Harbin Wester",
        "information": ["Ruxithid", "Obelisk", "Zorzula's Rest"],
        "disposition_change": +3
    }
)

# Then immediately update NPC:
log_npc_interaction(
    npc_name="Harbin Wester",
    interaction_type="briefing",
    information_exchanged=["Ruxithid threat", "Obelisk location", "Party plans"],
    disposition_change=+3,
    session_number=5
)
```

---

## Disposition Scale

| Value | Mood | Behavior |
|-------|------|----------|
| +10 | Devoted | Will risk life for party |
| +7 to +9 | Loyal | Trusts party completely |
| +5 to +6 | Friendly | Helpful, offers aid |
| +2 to +4 | Warm | Positive, willing to assist |
| 0 to +1 | Neutral (Positive) | Polite, professional |
| -1 to 0 | Neutral (Negative) | Indifferent, cautious |
| -2 to -4 | Cold | Unhelpful, suspicious |
| -5 to -6 | Unfriendly | Actively unhelpful |
| -7 to -9 | Hostile | Antagonistic, may attack |
| -10 | Enemy | Will attack on sight |

---

## Faction Reputation Scale

| Value | Standing | Benefits/Consequences |
|-------|----------|----------------------|
| +75 to +100 | Exalted | Free services, quest rewards doubled, faction quests available |
| +50 to +74 | Revered | Discounts, priority assistance, special quests |
| +25 to +49 | Honored | Friendly treatment, minor discounts |
| +1 to +24 | Friendly | Positive interactions, standard services |
| 0 | Neutral | No special treatment |
| -1 to -24 | Unfriendly | Cold treatment, higher prices |
| -25 to -49 | Hostile | Refused service, active opposition |
| -50 to -74 | Hated | Bounty on party, attacks on sight |
| -75 to -100 | Nemesis | Faction actively hunting party |

---

## Best Practices

### 1. Log Major Interactions
```python
# After significant conversations:
log_npc_interaction(...)
```

### 2. Track Information Flow
```python
# When party reveals important info:
update_npc_knowledge(...)
```

### 3. Update Disposition Regularly
```python
# After party helps/harms NPC:
update_npc_disposition(...)
```

### 4. Maintain Faction Relations
```python
# After major faction-related events:
update_faction_reputation(...)
```

### 5. Propagate Consequences
```python
# After world-changing events:
propagate_consequence(...)
```

---

## NPC File Structure (Example)

```markdown
---
type: npc
role: quest_giver
disposition: 8
alive: true
last_seen: "2026-01-13 21:45"
faction: Phandalin Militia
knowledge_entries:
  - session: 5
    date: "2026-01-13"
    information: "Ruxithid threat details"
    source: "Party briefing"
---

# Harbin Wester

**Faction:** [[Phandalin Militia]]
**Location:** [[Phandalin]]
**Role:** quest_giver
**Disposition:** 8/10 (Friendly)

## Description
Townmaster of Phandalin...

## Interactions

### Briefing - 2026-01-13 21:45
**Session 5**

**Information Exchanged:**
- Ruxithid threat details
- Obelisk location
- Party's assault plans

**Disposition Change:** +3 (improved) → **Current: 8/10**

**Notes:** Pledged full support. Offered supplies and militia.

## Knowledge
- **Session 5** (2026-01-13): Ruxithid is mind-flayer kin controlling goblins *(Learned from: Party)*
  - **Reaction:** Horrified. Committed all town resources to stopping the threat.

## Consequences
*How party actions have affected this NPC:*

- **Session 5** (2026-01-13): Party saved Phandalin from goblin siege *(positive)*

## Relationships
- **[[Sildar Hallwinter]]** - ally: Lords' Alliance colleague
```

---

## Quick Command Reference

```python
# Knowledge
update_npc_knowledge(npc_name, information, session_number, revealed_by, npc_reaction=None)

# Interactions
log_npc_interaction(npc_name, interaction_type, information_exchanged, disposition_change=0, session_number=None, notes=None)

# Disposition
update_npc_disposition(npc_name, disposition_change, reason=None)

# Factions
update_faction_reputation(faction_name, reputation_change, reason)

# Consequences
propagate_consequence(event_description, affected_npcs, consequence_type, session_number)

# Query
get_npc_data(npc_name)
```

---

**Your NPCs now have memory, personality, and dynamic relationships!** 🧠🤝📜

