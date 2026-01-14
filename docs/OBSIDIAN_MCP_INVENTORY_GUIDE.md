# Obsidian MCP - Inventory & Progression Tools

**Quick Reference for Character Management**

---

## New Tools (Phase 2)

### 1. Update Character XP

**Purpose:** Award XP and track progression

**Usage:**
```python
update_character_xp(character_name, xp)
```

**Example:**
```python
update_character_xp("Eglath Bearkiller", 8290)
```

**What it does:**
- Updates XP in frontmatter metadata
- Updates "**XP:**" line with formatted numbers
- Auto-calculates XP needed for next level
- Updates "**Next Level:**" line

**XP Thresholds:**
- Level 6: 14,000 XP
- Level 7: 23,000 XP
- Level 8: 34,000 XP
- Level 9: 48,000 XP
- Level 10: 64,000 XP

---

### 2. Update Character Currency

**Purpose:** Manage gold, silver, copper, etc.

**Usage:**
```python
update_character_currency(character_name, gp, sp, cp, ep, pp)
```

**Example:**
```python
update_character_currency(
    character_name="Brevin",
    gp=4807,
    sp=7,
    cp=5
)
```

**What it does:**
- Finds the currency line under "### Currency"
- Updates with new values
- Formats numbers with commas for thousands (gp only)
- Only updates provided currencies (leave others as None to keep unchanged)

**Output in Obsidian:**
```markdown
### Currency
- **4,807 gp, 7 sp, 5 cp**
```

---

### 3. Update Character AC

**Purpose:** Update Armor Class when equipment changes

**Usage:**
```python
update_character_ac(character_name, ac, ac_note)
```

**Example:**
```python
update_character_ac(
    character_name="Brevin",
    ac=16,
    ac_note="Studded Leather +1"
)
```

**What it does:**
- Updates AC in frontmatter metadata
- Updates "**AC:**" line in content
- Optionally adds note in parentheses

**Output in Obsidian:**
```markdown
**AC:** 16 (Studded Leather +1)
```

---

### 4. Add Inventory Item

**Purpose:** Add new items to character inventory

**Usage:**
```python
add_inventory_item(character_name, item_name, quantity, item_type, notes)
```

**Example:**
```python
add_inventory_item(
    character_name="Brevin",
    item_name="Psionic Disruptor Wand",
    quantity=1,
    item_type="Magic Item",
    notes="3 charges, 30 ft range, suppresses psionic abilities"
)
```

**What it does:**
- Finds "## Equipment & Inventory" section
- Adds new item line with proper formatting
- Includes quantity if > 1
- Includes type and notes if provided

**Output in Obsidian:**
```markdown
- **Psionic Disruptor Wand** - Magic Item - 3 charges, 30 ft range, suppresses psionic abilities
```

**With Quantity:**
```python
add_inventory_item("Brevin", "Potion of Healing", quantity=3, item_type="Consumable")
```

Output:
```markdown
- **Potion of Healing** (×3) - Consumable
```

---

### 5. Remove Inventory Item

**Purpose:** Remove consumed/lost items

**Usage:**
```python
remove_inventory_item(character_name, item_name)
```

**Example:**
```python
remove_inventory_item("Brevin", "Potion of Healing")
```

**What it does:**
- Searches for line containing `**{item_name}**`
- Removes the entire line
- Raises error if item not found

**Error Handling:**
```python
# If item doesn't exist:
ValueError: Item 'Potion of Healing' not found in Brevin's inventory
```

---

## Workflow Example: Loot Distribution

### After Combat:
```python
# 1. Award XP to all party members
update_character_xp("Brevin", 8290)
update_character_xp("Eglath Bearkiller", 8290)
update_character_xp("Torgga Brawnanvil", 8290)
update_character_xp("Vandross Ephrates", 8290)
update_character_xp("Zephyr Sparkwhistle", 8290)

# 2. Distribute currency
for character in ["Brevin", "Eglath Bearkiller", "Torgga Brawnanvil", "Vandross Ephrates", "Zephyr Sparkwhistle"]:
    update_character_currency(character, gp=4807, sp=7, cp=5)

# 3. Distribute special items
add_inventory_item(
    "Brevin",
    "Psionic Disruptor Wand",
    item_type="Magic Item",
    notes="3 charges, 30 ft range"
)

# 4. Update equipment (if attuned)
update_character_ac("Brevin", 16, "Vrek's Studded Leather +1")
add_inventory_item("Brevin", "Vrek's Studded Leather +1", item_type="Armor", notes="Attuned, psychically attuned")

# 5. Remove consumed items
remove_inventory_item("Torgga Brawnanvil", "Potion of Healing")
```

---

## Integration with Other Tools

### With Combat Engine:
```python
# After combat ends:
update_character_hp("Eglath Bearkiller", 21, 65)  # Update HP
update_character_xp("Eglath Bearkiller", 8290)    # Award XP
```

### With Session Recorder:
```python
# Log loot acquisition
log_event(
    event_type="discovery",
    content="Party looted Vrek's Studded Leather +1, Obsidian Commander's Medallion, 8× Psionic Crystal Shards"
)

# Then update inventories
add_inventory_item("Brevin", "Obsidian Commander's Medallion", ...)
```

---

## Best Practices

### 1. Batch Updates
When updating multiple characters, use a loop:
```python
for char in party_members:
    update_character_xp(char, new_xp)
    update_character_currency(char, gp=share_amount)
```

### 2. Descriptive Notes
Always include notes for special items:
```python
add_inventory_item(
    "Zephyr",
    "Psionic Catalyst Crystal",
    quantity=3,
    item_type="Arcane Component",
    notes="Extracted from psionic goblins, valuable for research"
)
```

### 3. Update AC When Equipment Changes
```python
# When character attunes to new armor:
update_character_ac("Brevin", 16, "Studded Leather +1")
add_inventory_item("Brevin", "Studded Leather +1", item_type="Armor", notes="Attuned")

# When unequipping:
update_character_ac("Brevin", 14, "Regular Studded Leather")
```

### 4. Track Consumables
```python
# Add stack:
add_inventory_item("Brevin", "Potion of Healing", quantity=3)

# Use one:
remove_inventory_item("Brevin", "Potion of Healing")
add_inventory_item("Brevin", "Potion of Healing", quantity=2)
```

---

## Error Handling

All tools return JSON with success/error messages:

**Success:**
```json
{
  "success": true,
  "message": "Updated XP for Brevin to 8,290"
}
```

**Error:**
```json
{
  "error": "Character 'Bob the Builder' not found"
}
```

**Character Not Found:**
- Ensure character file exists in `Obsidian/DnD/Player Characters/`
- Use exact name with underscores: `Eglath_Bearkiller.md`

**Item Not Found (for removal):**
- Check exact spelling and capitalization
- Item name must match exactly: `Potion of Healing` ≠ `potion of healing`

---

## Quick Command Reference

```python
# XP & Progression
update_character_xp(name, xp)

# Currency
update_character_currency(name, gp=X, sp=Y, cp=Z, ep=W, pp=V)

# AC
update_character_ac(name, ac, ac_note="optional")

# Inventory
add_inventory_item(name, item_name, quantity=1, item_type="", notes="")
remove_inventory_item(name, item_name)
```

---

**Now you can manage complete character progression through the Obsidian MCP!** 🎒💰📈

