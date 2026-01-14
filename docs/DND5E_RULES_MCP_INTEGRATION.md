# D&D 5e Rules Database MCP Integration

**Status:** ACTIVE  
**Priority:** Use for runtime rule lookups  
**API Source:** D&D 5e API (https://www.dnd5eapi.co/)

---

## Overview

The D&D 5e Rules Database MCP provides instant access to SRD (System Reference Document) content during gameplay. This complements chapter packs by providing on-demand lookups when pack data is missing or for quick reference.

## When to Use

### ✅ ALWAYS Use for Runtime Lookups:

1. **Missing Pack Data**
   - Spell not in chapter pack → Lookup spell
   - Monster not in encounter pack → Lookup monster
   - Feature not documented → Lookup feature

2. **Quick Reference During Play**
   - Player asks "What does Frightened do?" → Lookup condition
   - GM needs to verify spell mechanics → Lookup spell
   - Encounter needs monster stats → Lookup monster

3. **Adventure Prep**
   - Finding encounter options → Search monsters by CR
   - Finding spell options for NPCs → Search spells by level
   - Verifying item properties → Lookup magic item

4. **Rules Clarification**
   - Condition effects unclear → Lookup condition
   - Spell details needed → Lookup spell
   - Feature mechanics uncertain → Lookup feature

### ❌ DON'T Use When:

1. **Pack Has the Data** - Chapter packs are primary source
2. **Non-SRD Content** - API only has SRD content (core rules)
3. **Custom Content** - Homebrew/campaign-specific content not in API

---

## Available Tools

### 1. `mcp_dnd5e-rules_lookup_spell`
**Look up spell by name**

```
Parameters:
  - spell_name: "Fireball" (or any spell name)

Returns:
  - Level, school, casting time, range
  - Components (V, S, M) and materials
  - Duration and concentration
  - Full description
  - Higher level effects
  - Available classes
```

**Example Usage:**
- Player casts unknown spell → Lookup details
- NPC spellcaster needs spell → Get full mechanics
- Verify spell components → Check requirements

### 2. `mcp_dnd5e-rules_lookup_monster`
**Look up monster by name**

```
Parameters:
  - monster_name: "Goblin" (or any monster name)

Returns:
  - AC, HP, speed
  - Ability scores and modifiers
  - Saves and skills
  - Resistances/immunities
  - Senses and languages
  - Challenge rating and XP
  - Special abilities
  - Actions (attacks, abilities)
  - Legendary actions (if applicable)
```

**Example Usage:**
- Encounter not in pack → Get stat block
- Random encounter appears → Lookup stats
- Verify monster abilities → Check mechanics

### 3. `mcp_dnd5e-rules_lookup_condition`
**Look up condition by name**

```
Parameters:
  - condition_name: "Frightened" (or any condition)

Returns:
  - Full condition description
  - Mechanical effects
  - How condition works
```

**Example Usage:**
- Player affected by condition → Lookup effects
- GM applies condition → Verify mechanics
- Clarify condition rules → Get details

### 4. `mcp_dnd5e-rules_lookup_magic_item`
**Look up magic item by name**

```
Parameters:
  - item_name: "Bag of Holding" (or any item)

Returns:
  - Item description
  - Rarity
  - Magical properties
  - Usage rules
```

**Example Usage:**
- Loot contains magic item → Get description
- Player uses item → Verify effects
- Treasure generation → Get item details

### 5. `mcp_dnd5e-rules_lookup_feature`
**Look up class feature by name**

```
Parameters:
  - feature_name: "Rage" (or any feature)

Returns:
  - Feature description
  - Class and level
  - Mechanical effects
  - Usage rules
```

**Example Usage:**
- Verify NPC feature → Get mechanics
- Player asks about feature → Lookup details
- Feature clarification → Get rules

### 6. `mcp_dnd5e-rules_search_spells`
**Search spells by level/school**

```
Parameters:
  - level (optional): 0-9 (0 = cantrip)
  - school (optional): "Evocation", "Conjuration", etc.

Returns:
  - List of matching spells
```

**Example Usage:**
- Prep NPC spellcaster → Find spell options
- Generate spell scroll → Search by level
- Plan encounter → Find appropriate spells

### 7. `mcp_dnd5e-rules_search_monsters`
**Search monsters by CR**

```
Parameters:
  - challenge_rating: "0", "1", "5", "0.5", etc.

Returns:
  - List of monsters with that CR
```

**Example Usage:**
- Build encounter → Find CR-appropriate monsters
- Random encounter → Get options
- Balance combat → Find suitable creatures

---

## Integration with Gameplay

### Workflow: Missing Pack Data

**BEFORE (without MCP):**
1. Pack missing data
2. BLOCK or ask user
3. Wait for manual lookup
4. Continue gameplay

**NOW (with MCP):**
1. Pack missing data
2. Call MCP lookup tool (instant)
3. Get full details (<1 second)
4. Continue gameplay seamlessly

### Workflow: Rules Clarification

**BEFORE:**
1. Player asks about condition
2. GM looks up in book (30-60 seconds)
3. Read to player
4. Continue

**NOW:**
1. Player asks about condition
2. AI calls MCP lookup (instant)
3. Display formatted condition
4. Continue immediately

---

## Integration with Parallel Agent System

### REFEREE Agent Usage:

When REFEREE needs rule data not in packs:

```json
{
  "mechanics_notes": "Goblin attacks Brevin. [MCP: Lookup Goblin stats]. AC 15, +4 to hit, 1d6+2 damage.",
  "mcp_lookup_required": true,
  "lookup_type": "monster",
  "lookup_name": "Goblin"
}
```

**AI Assistant then:**
1. Calls `mcp_dnd5e-rules_lookup_monster` with "Goblin"
2. Gets stat block
3. Updates mechanics_notes with stats
4. Continues turn processing

### NARRATOR Agent Usage:

When NARRATOR needs spell/item description:

```json
{
  "narration": "Sildar casts a spell. [MCP: Lookup Cure Wounds]. Healing light washes over your wounds.",
  "mcp_lookup_required": true,
  "lookup_type": "spell",
  "lookup_name": "Cure Wounds"
}
```

---

## Performance

- **API Response Time:** <1 second (async requests)
- **Caching:** Browser-level caching (repeat lookups are instant)
- **Availability:** 99.9% uptime (D&D 5e API is stable)
- **Fallback:** If API fails, BLOCK and ask user for manual lookup

---

## Examples

### Example 1: Missing Monster in Encounter

```
AI: Processing random encounter...
AI: Encounter: 1d4+2 stirges
AI: [Checking encounter pack for stirge stats...]
AI: [Stirge not in encounter pack]
AI: [Calling MCP: lookup_monster("stirge")]
MCP: Returns full stirge stat block
AI: "A swarm of 4 stirges descends from the trees! Roll initiative."
AI: [Uses stirge stats for combat]
```

### Example 2: Player Asks About Condition

```
Player: "What does the Frightened condition do?"
AI: [Calling MCP: lookup_condition("frightened")]
MCP: Returns condition details
AI: "⚠️ **Frightened**

A frightened creature has disadvantage on ability checks and attack rolls while the source of its fear is within line of sight.

The creature can't willingly move closer to the source of its fear."
```

### Example 3: Spell Lookup During Combat

```
AI: NPC wizard casts Fireball...
AI: [Calling MCP: lookup_spell("fireball")]
MCP: Returns spell details
AI: "The wizard hurls a bead of fire that explodes in a 20-foot radius sphere. All creatures in the area must make a DC 15 Dexterity saving throw, taking 8d6 fire damage on a failed save, or half as much on a success."
AI: PLAYER: Roll Dexterity saving throw vs DC 15...
```

---

## Data Coverage

### Included (SRD Content):
✅ Core spells (Fireball, Cure Wounds, etc.)  
✅ Core monsters (Goblin, Dragon, Beholder, etc.)  
✅ All conditions (Frightened, Paralyzed, etc.)  
✅ Core magic items (Bag of Holding, +1 Sword, etc.)  
✅ Core class features (Rage, Sneak Attack, etc.)

### NOT Included (Non-SRD):
❌ Sourcebook-only content (Xanathar's, Tasha's, etc.)  
❌ Campaign-specific content (Phandelver custom NPCs)  
❌ Homebrew content (custom spells, monsters)

**For non-SRD content:** Use chapter packs or ask user.

---

## Fallback Strategy

**Priority Order:**
1. **Chapter Packs** (primary source - campaign-specific)
2. **MCP Lookup** (secondary - SRD content)
3. **Ask User** (last resort - if MCP fails or non-SRD)

**Example:**
- Need goblin stats → Check encounter pack first
- Not in pack → Call MCP lookup
- MCP fails → Ask user for stats

---

## Summary

**MANDATORY RULE:** When pack data is missing and a rule lookup is needed, ALWAYS use the D&D 5e Rules MCP before asking the user.

**Benefits:**
- Instant access to SRD content
- No manual lookups required
- Seamless gameplay integration
- Fast response times
- Complete stat blocks and descriptions

**Limitations:**
- SRD content only (no sourcebooks)
- Requires internet connection
- No custom/homebrew content

---

**Reference Files:**
- `C:\DnD\DnD_Cursor\mcp_servers\dnd5e_rules\README.md` - Tool documentation
- `C:\DnD\DnD_Cursor\.cursor\mcp.json` - MCP configuration
- API Docs: https://www.dnd5eapi.co/docs/

---

**Created:** 2026-01-13  
**Status:** ACTIVE  
**Integration:** Ready for gameplay














