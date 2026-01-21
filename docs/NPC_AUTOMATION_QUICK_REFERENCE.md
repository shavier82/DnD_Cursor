# NPC Automation - Quick Reference

**7 Tools for Dynamic NPC Tracking**

---

## 1. Create New NPC (When Party Meets Them)

```python
create_npc(
    npc_name="Gwyn Oresong",
    role="ally",
    description="Elderly human sage with white hair, expert in arcane crystals",
    location="Phandalin",
    faction="Scholars of Candlekeep",
    disposition=5
)
```

**Creates:**
```markdown
# Gwyn Oresong

**Faction:** [[Scholars of Candlekeep]]
**Location:** [[Phandalin]]
**Role:** ally
**Disposition:** 5/10 (Friendly)

## Description
Elderly human sage with white hair, expert in arcane crystals
```

---

## 2. Track What NPCs Know

```python
update_npc_knowledge(
    npc_name="Harbin Wester",
    information="Ruxithid controls psionic goblins",
    session_number=5,
    revealed_by="Party",
    npc_reaction="Horrified, pledged support"
)
```

**Creates:**
```markdown
## Knowledge
- **Session 5** (2026-01-13): Ruxithid controls psionic goblins *(Learned from: Party)*
  - **Reaction:** Horrified, pledged support
```

---

## 3. Log Interactions (Auto-Updates Disposition)

```python
log_npc_interaction(
    npc_name="Harbin Wester",
    interaction_type="briefing",
    information_exchanged=["Ruxithid threat", "Obelisk location"],
    disposition_change=+3,
    session_number=5,
    notes="Offered militia support"
)
```

**Creates:**
```markdown
### Briefing - 2026-01-13 21:45
**Information Exchanged:**
- Ruxithid threat
- Obelisk location

**Disposition Change:** +3 → **Current: 8/10**
**Notes:** Offered militia support
```

---

## 4. Quick Disposition Update

```python
update_npc_disposition(
    npc_name="Sildar Hallwinter",
    disposition_change=+2,
    reason="Party rescued Gundren"
)
```

**Updates:**
```markdown
**Disposition:** 7/10 (Friendly) - *Party rescued Gundren*
```

---

## 5. Faction Reputation

```python
update_faction_reputation(
    faction_name="Lords' Alliance",
    reputation_change=+25,
    reason="Saved Phandalin from siege"
)
```

**Creates/Updates `Factions.md`:**
```markdown
## Lords' Alliance
**Current Reputation:** 45/100

### Reputation History
- **2026-01-13**: Saved Phandalin from siege (+25)
```

---

## 6. Propagate Consequences

```python
propagate_consequence(
    event_description="Party killed Vrek Snapjaw",
    affected_npcs=["Harbin Wester", "Sildar Hallwinter"],
    consequence_type="positive",
    session_number=5
)
```

**Adds to each NPC:**
```markdown
## Consequences
- **Session 5** (2026-01-13): Party killed Vrek Snapjaw *(positive)*
```

---

## 7. Get NPC Data

```python
get_npc_data(npc_name="Harbin Wester")
```

**Returns:**
```json
{
  "metadata": {
    "disposition": 8,
    "knowledge_entries": [...],
    "last_seen": "2026-01-13 21:45"
  },
  "content": "..."
}
```

---

## Disposition Scale

| Value | Mood | Behavior |
|-------|------|----------|
| +10 | Devoted | Will die for party |
| +5 to +9 | Friendly | Helpful, trusts party |
| 0 to +4 | Neutral+ | Polite, professional |
| -4 to 0 | Neutral- | Indifferent, cautious |
| -5 to -9 | Hostile | Unhelpful, antagonistic |
| -10 | Enemy | Attacks on sight |

---

## Faction Reputation Scale

| Value | Standing |
|-------|----------|
| +75 to +100 | Exalted |
| +50 to +74 | Revered |
| +25 to +49 | Honored |
| +1 to +24 | Friendly |
| 0 | Neutral |
| -25 to -49 | Hostile |
| -50 to -100 | Hated/Nemesis |

---

## Common Workflows

### After Major Conversation:
```python
log_npc_interaction(...)  # Full interaction log
update_npc_knowledge(...)  # What they learned
```

### After Party Helps NPC:
```python
update_npc_disposition(..., disposition_change=+2, reason="Party helped")
```

### After Faction Quest:
```python
update_faction_reputation(..., reputation_change=+20, reason="Completed quest")
```

### After World Event:
```python
propagate_consequence(..., affected_npcs=[...], consequence_type="positive")
```

---

## Files Updated

- **NPCs/[NPC_Name].md** - Individual NPC files
- **Factions.md** - Faction reputation tracker

---

**NPCs now remember everything!** 🧠📜

