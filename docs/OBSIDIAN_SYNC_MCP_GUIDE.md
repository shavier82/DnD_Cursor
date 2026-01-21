# Obsidian Sync MCP - Migration from Google Sheets

## Overview

**Purpose:** The Obsidian Sync MCP replaces Google Sheets as the single source of truth for character data.

**Migration Status:** IN PROGRESS - Transitioning from Google Sheets to Obsidian vault as primary data store.

---

## What This MCP Does

### Primary Functions
1. **Read character data** from Obsidian markdown files
2. **Update character data** in Obsidian when changes occur in-game
3. **Sync character stats** (HP, XP, inventory, conditions, currency)
4. **Replace Google Sheets** as the authoritative data source

### Data Flow (NEW)

```
BEFORE (Google Sheets):
Game Session → Google Sheets API → Character Stats → Read by AI

AFTER (Obsidian):
Game Session → Obsidian Sync MCP → Obsidian Vault → Read by AI
                     ↓
              Obsidian App (live updates)
```

---

## Vault Structure

### Current Obsidian Vault Location
```
C:\Users\ksist\Documents\Obsidian\
└── DnD\
    ├── Player Characters\
    │   ├── Brevin.md
    │   ├── Eglath_Bearkiller.md
    │   ├── Torgga_Brawnanvil.md
    │   ├── Vandross_Ephrates.md
    │   └── Zephyr_Sparkwhistle.md
    ├── NPCs\
    │   ├── Gundren_Rockseeker.md
    │   ├── Sildar_Hallwinter.md
    │   └── ...
    ├── Locations\
    │   ├── Phandalin.md
    │   ├── Wave_Echo_Cave.md
    │   └── ...
    └── Quests\
        ├── Defeat_the_Black_Spider.md
        └── ...
```

### Character File Format

Each character markdown file contains:

```markdown
---
ac: 16
class: Rogue
last_updated: '2026-01-13T21:02:56.545335'
level: 5
player: Player Name
race: Halfling
tags:
  - pc
  - character
type: player_character
xp: 8290
---

# Character Name

## Quick Stats

**Class:** Rogue 5
**Race:** Halfling

## Combat Stats

**HP:** 45/45 (Aid +10 for 8 hours)
**AC:** 16 (Studded Leather +1)
**Initiative:** +6
**Speed:** 30 ft
**Proficiency Bonus:** +3

## Ability Scores

| Stat | Score | Modifier |
|------|-------|----------|
| STR  | 8     | -1       |
| DEX  | 17    | +3       |
...

## Currency
- **4,807 gp, 7 sp, 5 cp**

## Equipment & Inventory
...
```

---

## MCP Functions

### Available Tools

#### 1. `update_character_hp`
Updates character's current HP in Obsidian.

```python
update_character_hp(
    character_name="Brevin",
    new_hp=35,
    max_hp=45
)
```

**Updates line:** `**HP:** 35/45`

#### 2. `update_character_xp`
Adds XP to character's total.

```python
update_character_xp(
    character_name="Brevin",
    xp_to_add=500
)
```

**Updates:** YAML frontmatter `xp: 8790` and text section

#### 3. `update_character_currency`
Updates character's gold, silver, copper, etc.

```python
update_character_currency(
    character_name="Brevin",
    cp=5,
    sp=7,
    gp=4807,
    pp=0
)
```

**Updates line:** `- **4,807 gp, 7 sp, 5 cp**`

#### 4. `add_inventory_item`
Adds items to character inventory.

```python
add_inventory_item(
    character_name="Brevin",
    item_name="Psionic Disruptor",
    quantity=1
)
```

**Appends to Equipment section**

#### 5. `create_npc`
Creates new NPC markdown file.

```python
create_npc(
    npc_name="Vrek Snapjaw",
    race="Goblin",
    role="Psi Commander",
    location="Zorzula's Rest",
    description="Field commander for Lord Ruxithid"
)
```

**Creates:** `DnD/NPCs/Vrek_Snapjaw.md`

---

## Migration Process

### Phase 1: Setup (CURRENT)
- [x] Obsidian vault exists
- [x] Character markdown files created
- [x] MCP server paths configured
- [ ] MCP server tested and working
- [ ] Data format validation

### Phase 2: Parallel Operation
- [ ] Run both Google Sheets AND Obsidian sync
- [ ] Verify data consistency
- [ ] Test all update operations
- [ ] Validate combat HP updates
- [ ] Validate XP/currency updates

### Phase 3: Cutover
- [ ] Disable Google Sheets sync
- [ ] Make Obsidian primary source
- [ ] Update all scripts to use Obsidian MCP
- [ ] Remove Google Sheets dependencies

### Phase 4: Cleanup
- [ ] Archive Google Sheets data
- [ ] Update documentation
- [ ] Remove old scripts
- [ ] Verify all workflows

---

## Why Migrate to Obsidian?

### Advantages Over Google Sheets

1. **Local Control**
   - No API limits or quota issues
   - No network dependency
   - Instant updates

2. **Rich Formatting**
   - Markdown support
   - Links between notes
   - Embedded images
   - Better organization

3. **Integration**
   - Obsidian graph view shows relationships
   - Tags and metadata
   - Search and filtering
   - Plugins and extensions

4. **Version Control**
   - Can be git-tracked
   - Full history
   - Easy rollback

5. **Performance**
   - No API calls
   - File-based (fast)
   - No rate limiting

---

## Current Issues & Fixes Needed

### Issue 1: MCP Not Finding Characters
**Problem:** MCP returns "Character not found"

**Root Cause:** MCP server needs restart after path changes

**Fix:** 
```bash
# Restart Cursor to reload MCP servers
# Or restart MCP service in Cursor settings
```

### Issue 2: Data Format Mismatch
**Problem:** MCP regex patterns don't match current markdown format

**Current Format:** `**HP:** 45/45`

**MCP Expects:** `HP: 45/45` (no bold)

**Fix Options:**
1. Update MCP regex to handle bold markdown `**HP:**`
2. Standardize markdown format to match MCP expectations
3. Create bidirectional parser

### Issue 3: YAML Frontmatter
**Problem:** Some data is in YAML frontmatter, some in markdown body

**Solution:** Define clear data location rules
- HP: Markdown body (Combat Stats section)
- XP: YAML frontmatter
- Level: YAML frontmatter
- Currency: Markdown body (Currency section)
- Inventory: Markdown body (Equipment section)

---

## Usage in Play Mode

### When HP Changes
```python
# OLD (Google Sheets):
python scripts/update_sheets_data.py hp "Brevin" 35 45

# NEW (Obsidian MCP):
mcp_obsidian-sync_update_character_hp(
    character_name="Brevin",
    new_hp=35,
    max_hp=45
)
```

### When XP is Awarded
```python
# OLD (Google Sheets):
python scripts/update_sheets_data.py xp "Brevin" 500

# NEW (Obsidian MCP):
mcp_obsidian-sync_update_character_xp(
    character_name="Brevin",
    xp_to_add=500
)
```

### When Loot is Found
```python
# OLD (Google Sheets):
python scripts/update_sheets_data.py currency "Brevin" --gp 150

# NEW (Obsidian MCP):
mcp_obsidian-sync_update_character_currency(
    character_name="Brevin",
    gp=4957  # Current + 150
)
```

---

## Integration with Other MCPs

### Combat Engine
```python
# Combat Engine reads HP from Obsidian
combat_engine.get_character_hp("Brevin")
  → Calls obsidian_sync.read_character_file()
  → Parses HP from markdown

# Combat Engine updates HP after damage
combat_engine.apply_damage("Brevin", 10)
  → Calls obsidian_sync.update_character_hp()
  → Updates markdown file
```

### Session Recorder
```python
# Session Recorder logs XP awards
session_recorder.log_event("xp_awarded", ...)
  → Triggers obsidian_sync.update_character_xp()
  → Updates character files
```

### Campaign Wiki
```python
# Campaign Wiki creates NPCs
campaign_wiki.create_npc(...)
  → Calls obsidian_sync.create_npc()
  → Creates markdown file in NPCs folder
```

---

## Testing Checklist

### Before Migration
- [ ] All character files exist in Obsidian
- [ ] Data is current and accurate
- [ ] MCP server paths are correct
- [ ] Backup of Google Sheets data
- [ ] Backup of Obsidian vault

### During Testing
- [ ] Test HP update (damage in combat)
- [ ] Test HP update (healing)
- [ ] Test XP award
- [ ] Test currency update (spending)
- [ ] Test currency update (loot)
- [ ] Test inventory add
- [ ] Test NPC creation
- [ ] Test concurrent updates
- [ ] Test Obsidian app live refresh

### After Migration
- [ ] All data migrated successfully
- [ ] No data loss
- [ ] Combat updates work
- [ ] Session logging works
- [ ] Character sheets accurate
- [ ] Obsidian app reflects changes

---

## Rollback Plan

If migration fails:

1. **Stop using Obsidian MCP**
2. **Revert to Google Sheets scripts**
3. **Restore Google Sheets data from backup**
4. **Document issues encountered**
5. **Fix issues before retry**

---

## Future Enhancements

### Planned Features
- [ ] Two-way sync (Obsidian → Game)
- [ ] Condition tracking in Obsidian
- [ ] Spell slot management
- [ ] Inventory weight calculation
- [ ] Auto-level up support
- [ ] Death saves tracking
- [ ] Inspiration tracking

### Nice-to-Have
- [ ] Character portraits
- [ ] Campaign timeline
- [ ] Session notes integration
- [ ] Quest tracking
- [ ] Loot distribution
- [ ] Party treasury

---

## Support & Troubleshooting

### Common Errors

**"Character not found"**
- Check character name spelling
- Verify file exists: `C:\Users\ksist\Documents\Obsidian\DnD\Player Characters\{name}.md`
- Restart MCP server

**"Failed to update HP"**
- Check markdown format matches MCP regex
- Verify file is not locked by Obsidian
- Check file permissions

**"XP not updating"**
- Verify YAML frontmatter format
- Check for syntax errors
- Ensure numeric values only

### Debug Mode

Enable MCP debug logging:
```json
// .cursor/mcp.json
{
  "mcpServers": {
    "obsidian-sync": {
      "command": "python",
      "args": ["-u", "mcp_servers/obsidian_sync/obsidian_sync_server.py"],
      "env": {
        "DEBUG": "true"
      }
    }
  }
}
```

---

## Summary

**Obsidian Sync MCP** replaces Google Sheets as the authoritative data source for character information. It provides:

✅ Real-time updates to Obsidian vault
✅ Local file-based storage (no API limits)
✅ Rich markdown formatting
✅ Integration with Obsidian app
✅ Version control friendly
✅ Faster performance

**Status:** Migration in progress. Test thoroughly before full cutover.
