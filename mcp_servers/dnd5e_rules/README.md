# D&D 5e Rules Database MCP Server

**Status:** ACTIVE  
**API Source:** D&D 5e API (https://www.dnd5eapi.co/)

## Overview

Provides instant lookup for D&D 5e rules content:
- Spells (full descriptions with casting details)
- Monsters (complete stat blocks)
- Conditions (mechanical effects)
- Magic items (descriptions and properties)
- Class features (descriptions and mechanics)
- Search functions (find spells by level, monsters by CR)

## Available Tools

### 1. `lookup_spell`
Look up any D&D 5e spell by name.

**Parameters:**
- `spell_name` - Name of spell (e.g., "Fireball", "Cure Wounds")

**Returns:** Full spell details including level, school, casting time, range, components, duration, description, and available classes.

### 2. `lookup_monster`
Look up any D&D 5e monster by name.

**Parameters:**
- `monster_name` - Name of monster (e.g., "Goblin", "Ancient Red Dragon")

**Returns:** Complete stat block with AC, HP, abilities, actions, special abilities, and legendary actions.

### 3. `lookup_condition`
Look up any D&D 5e condition by name.

**Parameters:**
- `condition_name` - Name of condition (e.g., "Frightened", "Paralyzed")

**Returns:** Full condition description and mechanical effects.

### 4. `lookup_magic_item`
Look up any D&D 5e magic item by name.

**Parameters:**
- `item_name` - Name of item (e.g., "Bag of Holding", "Ring of Protection")

**Returns:** Item description, rarity, and magical properties.

### 5. `lookup_feature`
Look up any D&D 5e class feature by name.

**Parameters:**
- `feature_name` - Name of feature (e.g., "Rage", "Sneak Attack")

**Returns:** Feature description and mechanics.

### 6. `search_spells`
Search for spells by level and/or school.

**Parameters:**
- `level` (optional) - Spell level (0-9, where 0 is cantrip)
- `school` (optional) - School of magic (e.g., "Evocation")

**Returns:** List of matching spells.

### 7. `search_monsters`
Search for monsters by challenge rating.

**Parameters:**
- `challenge_rating` - CR (e.g., "0", "1", "5", "0.5")

**Returns:** List of monsters with that CR.

## Use Cases

### During Gameplay
- "What does the Frightened condition do?" → Instant lookup
- "Show me the Goblin stat block" → Complete stats
- "What are the details of Fireball?" → Full spell info

### Adventure Prep
- "Show me all CR 2 monsters" → Get encounter options
- "Search for 3rd level Evocation spells" → Find spell options

### Reference Lookups
- "What does a Bag of Holding do?" → Item properties
- "Explain the Barbarian's Rage feature" → Feature mechanics

## Benefits

✅ **Instant Access** - No manual lookup, no page flipping  
✅ **Always Available** - Online API, no local storage needed  
✅ **Comprehensive** - Full SRD content coverage  
✅ **Formatted** - Clean, readable output optimized for gameplay  
✅ **Fast** - Async requests, <1 second response time

## Data Source

Uses the official D&D 5e API (https://www.dnd5eapi.co/), which provides:
- All SRD (System Reference Document) content
- Free and open source
- Actively maintained
- No authentication required

**Note:** Only SRD content is available (core rules, not all sourcebooks).

---

**Created:** 2026-01-13  
**Integration:** MCP Server for Cursor AI














