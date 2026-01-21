# Campaign Wiki Auto-Sync to Obsidian

## Overview

The Campaign Wiki MCP server now **automatically syncs NPCs and relationships to Obsidian** when they are created or updated. No manual sync step required!

## How It Works

### Automatic NPC Sync

When you create a new NPC using `create_npc`:
1. NPC is saved to the campaign wiki JSON file
2. **Automatically exported to Obsidian** (if vault is configured)
3. NPC file created in `Obsidian/NPCs/` folder

### Automatic Relationship Sync

When you add a relationship using `add_relationship`:
1. Relationship is saved to the campaign wiki
2. **Both NPCs involved are automatically re-synced to Obsidian**
3. Relationship links appear in both NPC files

## Default Obsidian Vault Path

If no vault path is specified when loading the wiki, it defaults to:
```
C:\Users\ksist\Documents\Obsidian\DnD
```

## Usage

### 1. Load Wiki (with auto-sync enabled)

```python
create_or_load_wiki(
    campaign_name="Phandelver"
    # Obsidian vault defaults to C:\Users\ksist\Documents\Obsidian\DnD
)
```

### 2. Create NPC (auto-syncs to Obsidian)

```python
create_npc(
    campaign_name="Phandelver",
    name="New NPC Name",
    role="enemy",
    description="NPC description here"
)
# ✅ Automatically synced to Obsidian/NPCs/New_NPC_Name.md
```

### 3. Add Relationship (auto-syncs both NPCs)

```python
add_relationship(
    campaign_name="Phandelver",
    from_entity="NPC1",
    to_entity="NPC2",
    relationship_type="professional",
    description="They work together"
)
# ✅ Both NPC1 and NPC2 files updated in Obsidian with relationship links
```

## File Structure

NPCs are automatically created in:
```
C:\Users\ksist\Documents\Obsidian\DnD\NPCs\
├── Vrek_Snapjaw.md
├── Ruxithid_the_Chosen.md
├── Krazka.md
└── ...
```

## Features

- ✅ **Auto-sync on create** - NPCs automatically appear in Obsidian
- ✅ **Auto-sync on relationship** - Both NPCs updated when relationship added
- ✅ **Wiki links** - NPCs link to each other and locations automatically
- ✅ **Frontmatter metadata** - Type, role, faction, location, status tracked
- ✅ **Relationship sections** - All relationships displayed with descriptions

## Error Handling

If auto-sync fails (e.g., Obsidian vault not accessible), the NPC is still created in the wiki JSON file. The error is logged as a warning but doesn't stop the operation.

## Manual Sync (if needed)

You can still manually sync everything:

```python
sync_to_obsidian(campaign_name="Phandelver")
```

This syncs all NPCs, locations, quests, and relationships to Obsidian.

---

**Result:** When the team meets or hears of new people, simply call `create_npc()` and the NPC will automatically appear in Obsidian! 🎉
