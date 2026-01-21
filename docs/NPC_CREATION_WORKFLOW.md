# NPC Creation Workflow - Campaign Guide

**When party meets new NPCs → Automatically create them in Obsidian**

---

## The Problem

Previously, NPCs met during sessions had to be manually created in Obsidian later. This meant:
- ❌ No record of first impressions
- ❌ Risk of forgetting minor NPCs
- ❌ Inconsistent NPC tracking
- ❌ Lost context between sessions

---

## The Solution

**Use `create_npc()` during sessions when party meets new NPCs!**

```python
create_npc(
    npc_name="NPC Name",
    role="ally|enemy|neutral|quest_giver|merchant",
    description="Physical description and personality",
    location="Where they are",
    faction="Faction name (if any)",
    disposition=0  # -10 (hostile) to +10 (friendly)
)
```

---

## Workflow During Campaign

### Step 1: Party Meets New NPC

**DM Narration:**
> "You enter the apothecary and meet an elderly woman with silver hair and kind eyes. She introduces herself as Gwyn Oresong, a sage visiting from Candlekeep who's studying the recent goblin activity."

### Step 2: Create NPC Immediately

```python
create_npc(
    npc_name="Gwyn Oresong",
    role="ally",
    description="Elderly human woman with silver hair and kind eyes. Sage from Candlekeep studying goblin activity. Warm demeanor, speaks softly but with authority.",
    location="Phandalin",
    faction="Scholars of Candlekeep",
    disposition=3  # Initially friendly
)
```

**What This Creates in Obsidian:**

```markdown
---
type: npc
role: ally
disposition: 3
alive: true
faction: Scholars of Candlekeep
location: Phandalin
---

# Gwyn Oresong

**Faction:** [[Scholars of Candlekeep]]
**Location:** [[Phandalin]]
**Role:** ally
**Disposition:** 3/10 (Warm)

## Description
Elderly human woman with silver hair and kind eyes. Sage from Candlekeep studying goblin activity. Warm demeanor, speaks softly but with authority.

## Relationships
*Add relationships here*
```

### Step 3: Track First Interaction

```python
log_npc_interaction(
    npc_name="Gwyn Oresong",
    interaction_type="first_meeting",
    information_exchanged=[
        "Party introduced themselves",
        "Gwyn is researching goblin psionic abilities",
        "She offers to help analyze the crystal shards"
    ],
    disposition_change=+2,  # Party made good impression
    session_number=5,
    notes="Gwyn impressed by party's professionalism and interest in research"
)
```

---

## Role Types Reference

| Role | When to Use | Initial Disposition |
|------|-------------|---------------------|
| **ally** | Friendly NPCs who help the party | +3 to +5 |
| **quest_giver** | NPCs offering quests | 0 to +3 |
| **merchant** | Shopkeepers, traders | 0 |
| **neutral** | Random townsfolk, bystanders | 0 |
| **informant** | NPCs with useful information | -2 to +2 |
| **rival** | Competing adventurers, not hostile | -2 to +1 |
| **suspicious** | NPCs who don't trust party | -3 to -1 |
| **enemy** | Hostile NPCs, antagonists | -5 to -10 |

---

## Quick Creation Templates

### Template: Friendly Townsfolk
```python
create_npc(
    npc_name="[Name]",
    role="ally",
    description="[Physical description]. [Personality]. [Occupation].",
    location="[Town/City]",
    disposition=2
)
```

### Template: Merchant
```python
create_npc(
    npc_name="[Name]",
    role="merchant",
    description="[Physical description]. Runs [shop name]. [Personality traits].",
    location="[Town/City]",
    disposition=0
)
```

### Template: Quest Giver
```python
create_npc(
    npc_name="[Name]",
    role="quest_giver",
    description="[Physical description]. [Motivation]. [Problem they need solved].",
    location="[Location]",
    faction="[Faction if any]",
    disposition=1
)
```

### Template: Antagonist
```python
create_npc(
    npc_name="[Name]",
    role="enemy",
    description="[Physical description]. [Personality]. [Motivations/goals].",
    location="[Base of operations]",
    faction="[Villain faction]",
    disposition=-7
)
```

### Template: Random Encounter
```python
create_npc(
    npc_name="[Name or descriptor like 'Traveling Merchant']",
    role="neutral",
    description="[Brief physical description].",
    location="[Road/wilderness]",
    disposition=0
)
```

---

## Disposition Guidelines

### Initial Disposition by Context

| Context | Suggested Disposition |
|---------|----------------------|
| Party saved their life | +8 to +10 |
| Party helped their faction | +5 to +7 |
| Friendly introduction | +2 to +4 |
| Neutral meeting | 0 |
| Cautious/suspicious | -2 to -1 |
| Hostile territory | -4 to -3 |
| Known enemy | -7 to -5 |
| Mortal enemy | -10 to -8 |

---

## Full Example: Campaign Session

### Scenario: Party Enters Phandalin Inn

**DM:**
> "As you enter the Stonehill Inn, you notice several NPCs..."

#### NPC 1: Innkeeper (Already Exists)
```python
# Toblen Stonehill already in vault, just use him
log_npc_interaction(
    npc_name="Toblen Stonehill",
    interaction_type="greeting",
    information_exchanged=["Party rents rooms for the night"],
    disposition_change=+1,
    session_number=5
)
```

#### NPC 2: New Patron at Bar
```python
# Create new NPC on the fly
create_npc(
    npc_name="Daran Edermath",
    role="ally",
    description="Retired human adventurer, late 50s, scarred face, former fighter. Runs an apple orchard now. Gruff but honorable.",
    location="Phandalin",
    faction="Order of the Gauntlet",
    disposition=1
)

# Log first meeting
log_npc_interaction(
    npc_name="Daran Edermath",
    interaction_type="first_meeting",
    information_exchanged=[
        "Daran is concerned about orc raids",
        "He was a member of Order of the Gauntlet",
        "Offers information about old ruins nearby"
    ],
    disposition_change=+2,
    session_number=5,
    notes="Daran respects competent adventurers. Party impressed him with their professionalism."
)
```

#### NPC 3: Mysterious Hooded Figure
```python
create_npc(
    npc_name="Halia Thornton",
    role="neutral",
    description="Human woman, mid-30s, calculating amber eyes, well-dressed. Guildmaster of Miner's Exchange. Ambitious and cunning.",
    location="Phandalin",
    faction="Zhentarim (secret)",
    disposition=-1  # Wary, evaluating party
)

log_npc_interaction(
    npc_name="Halia Thornton",
    interaction_type="first_meeting",
    information_exchanged=[
        "Halia runs the Miner's Exchange",
        "She's interested in party's capabilities",
        "Hints at future job opportunities"
    ],
    disposition_change=0,
    session_number=5,
    notes="Halia is assessing whether party could be useful. Neutral for now."
)
```

---

## Best Practices

### 1. Create NPCs Immediately
✅ **Do:** Create NPC file as soon as they're introduced
❌ **Don't:** Wait until after session to add them

### 2. Capture First Impressions
✅ **Do:** Include personality and appearance in description
❌ **Don't:** Leave description blank with intent to "fill in later"

### 3. Set Appropriate Disposition
✅ **Do:** Consider context and party actions so far
❌ **Don't:** Default everything to 0

### 4. Log First Interaction
✅ **Do:** Use `log_npc_interaction()` after creating NPC
❌ **Don't:** Create NPC without tracking first meeting

### 5. Minor NPCs Still Get Files
✅ **Do:** Create files even for minor NPCs (shopkeepers, guards)
❌ **Don't:** Skip "unimportant" NPCs (they might become important later!)

---

## Special Cases

### Anonymous NPCs
For unnamed NPCs (guards, bandits, etc.):
```python
create_npc(
    npc_name="Guard Captain (East Gate)",
    role="neutral",
    description="Weathered human male, 40s, stern expression. Guards east entrance to Phandalin.",
    location="Phandalin",
    disposition=0
)
```

### Enemy NPCs (Named Combatants)
```python
create_npc(
    npc_name="Vrek Snapjaw",
    role="enemy",
    description="Goblin Psi Commander. Glowing purple eyes, carries obsidian shard. Intelligent and ruthless.",
    location="Zorzula's Rest",
    faction="Ruxithid's Forces",
    disposition=-9
)
```

### NPCs from Player Backstories
```python
create_npc(
    npc_name="[Relative/Contact Name]",
    role="ally",
    description="[Player's description from backstory].",
    location="[Where they are]",
    disposition=+7  # Already have relationship with PC
)

# Add relationship immediately
# (Do this in Campaign Wiki MCP or Knowledge Graph MCP)
add_relationship(
    from_entity="[PC Name]",
    to_entity="[NPC Name]",
    relationship_type="family",  # or friend, mentor, etc.
    description="[Nature of relationship]"
)
```

---

## Integration with Other Systems

### Session Recorder
```python
# Log in session recorder when NPC is created
log_event(
    event_type="npc_interaction",
    content=f"Party met {npc_name} for the first time",
    metadata={
        "npc": npc_name,
        "location": location,
        "first_meeting": True
    }
)
```

### Campaign Wiki
```python
# After creating in Obsidian, optionally add to Campaign Wiki
create_npc(  # Campaign Wiki version
    npc_id=str(uuid.uuid4()),
    name=npc_name,
    role=role,
    description=description,
    # ... other fields
)
sync_to_obsidian()
```

---

## Quick Command Reference

```python
# 1. Create NPC
create_npc(npc_name, role, description, location, faction, disposition)

# 2. Log First Meeting
log_npc_interaction(npc_name, "first_meeting", information_exchanged, disposition_change, session_number)

# 3. Update as Campaign Progresses
update_npc_knowledge(npc_name, information, session_number, revealed_by, npc_reaction)
update_npc_disposition(npc_name, disposition_change, reason)
```

---

## Benefits

✅ **Complete NPC Roster** - Never forget who the party met
✅ **Consistent Tracking** - All NPCs have same structure
✅ **First Impression Context** - Remember how NPCs were introduced
✅ **Disposition History** - Track how relationships evolved
✅ **Session Continuity** - NPCs remember party between sessions
✅ **DM Reference** - Quick lookup during prep

---

**Create every NPC the party meets. Your world will feel alive!** 🌍👥










