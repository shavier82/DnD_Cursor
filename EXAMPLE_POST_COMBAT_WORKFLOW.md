# Example: Complete Post-Combat Workflow

This example shows the FULL post-combat procedure after defeating 2 goblins.

---

## 🎬 Combat Just Ended

**Situation:**
- 2 Goblins defeated (CR 1/4 each)
- Party: Torgga (Cleric) and Eglath (Barbarian)
- Both PCs participated in combat

---

## Step 1: End Combat

```javascript
end_combat_tool({combat_id: "e5489571-5a04-49e6-b5e6-f1212470c51a"})

// Result:
{
  "success": true,
  "message": "Combat ended",
  "rounds": 2,
  "obsidian_sync": [...]
}
```

---

## Step 2: Calculate & Distribute XP (AUTOMATIC)

### A. Calculate Total XP

```
Goblin (CR 1/4) = 50 XP each
2 Goblins × 50 XP = 100 XP total
2 PCs participated
100 XP / 2 = 50 XP per character
```

### B. Update Character Sheets

```javascript
update_character_xp("Torgga_Brawnanvil", 50)
// Result: {"success": true, "character": "Torgga_Brawnanvil", "new_xp": 8340}

update_character_xp("Eglath_Bearkiller", 50)
// Result: {"success": true, "character": "Eglath_Bearkiller", "new_xp": 8340}
```

### C. Narrate XP Gain

```
NARRATION:
As the last goblin falls, the forest grows quiet. You've survived another 
ambush, learned from the experience, and grown stronger.

**XP EARNED:**
- Torgga Brawnanvil: +50 XP → 8,340 / 14,000 (5,660 XP to Level 6)
- Eglath Bearkiller: +50 XP → 8,340 / 14,000 (5,660 XP to Level 6)
```

---

## Step 3: Roll & Distribute Currency (AUTOMATIC)

### A. Roll Currency Loot

```javascript
// Goblins carry: 1d6 cp and 1d4 sp each
roll_dice("2d6", "Goblin copper (2 goblins)", "DM")
// Result: 7 cp total

roll_dice("2d4", "Goblin silver (2 goblins)", "DM")
// Result: 5 sp total
```

### B. Divide Currency

```
7 cp / 2 PCs = 3 cp each (1 cp remainder)
5 sp / 2 PCs = 2 sp each (1 sp remainder)

Decision: Give remainders to Torgga (party treasurer)
Torgga: 4 cp, 3 sp
Eglath: 3 cp, 2 sp
```

### C. Update Character Sheets

```javascript
// Read current currency first (from Obsidian character sheet):
// Torgga currently has: 4,807 gp, 7 sp, 5 cp
// Eglath currently has: 2,150 gp, 3 sp, 0 cp

update_character_currency("Torgga_Brawnanvil", {cp: 4, sp: 3, gp: 0})
// Result: {"success": true, "new_total": "4,807 gp, 10 sp, 9 cp"}

update_character_currency("Eglath_Bearkiller", {cp: 3, sp: 2, gp: 0})
// Result: {"success": true, "new_total": "2,150 gp, 5 sp, 3 cp"}
```

### D. Narrate Currency Loot

```
NARRATION:
You search the goblin corpses, finding a meager haul in their filthy pockets.

**CURRENCY LOOTED:**
- 7 copper pieces total
- 5 silver pieces total

**DISTRIBUTED:**
- Torgga: +4 cp, +3 sp → Total: 4,807 gp, 10 sp, 9 cp
- Eglath: +3 cp, +2 sp → Total: 2,150 gp, 5 sp, 3 cp
```

---

## Step 4: List Items & Ask Players

### A. Determine Item Loot

```
Goblin equipment (2 goblins):
- 2× Scimitar (1d6 slashing, 2 lb each)
- 2× Shortbow (1d6 piercing, 2 lb each)
- 8 arrows total (20 arrows = 1 lb, so 8 arrows = 0.4 lb)
- 2× Leather Armor (worn, AC 11, 10 lb each)
```

### B. Present Options to Players

```
NARRATION:
The goblins' belongings lie scattered on the forest floor.

**LOOT AVAILABLE:**
- 2× Scimitar (1d6 slashing, 2 lb each)
- 2× Shortbow (1d6 piercing, 2 lb each)  
- 8× Arrows (0.4 lb total)
- 2× Leather Armor (worn, 10 lb each)

ASK:
What do you want to take?

ACTIONS:
1. Take the arrows (always useful)
2. Take weapons to sell later
3. Leave it all (goblin gear is worthless)
4. Custom - tell me what you want
```

### C. Player Responds

```
Player: "Take the arrows and one scimitar for backup"
```

### D. Update Inventories

```javascript
// Torgga takes the arrows
add_inventory_item("Torgga_Brawnanvil", "Arrow", 8, 0.4)
// Result: {"success": true, "item": "Arrow", "quantity": 8, "weight": 0.4}

// Eglath takes a scimitar
add_inventory_item("Eglath_Bearkiller", "Scimitar", 1, 2)
// Result: {"success": true, "item": "Scimitar", "quantity": 1, "weight": 2}
```

### E. Obsidian Inventory Tables Updated

**Torgga's Inventory (in Obsidian):**

```markdown
## Equipment & Inventory

| Item | Quantity | Weight (lb) | Notes |
|------|----------|-------------|-------|
| Potion of Healing | 4 | 2 | Restores 2d4+2 HP each |
| Arrow | 8 | 0.4 | Standard arrows |
| Rope, Hempen (50 ft) | 1 | 10 | Standard rope |
```

**Eglath's Inventory (in Obsidian):**

```markdown
## Equipment & Inventory

| Item | Quantity | Weight (lb) | Notes |
|------|----------|-------------|-------|
| Greataxe (Dragon Battleaxe) | 1 | 7 | Primary weapon |
| Scimitar | 1 | 2 | Looted from goblin |
| Potion of Healing | 2 | 1 | Restores 2d4+2 HP each |
```

### F. Narrate Item Distribution

```
NARRATION:
Torgga gathers the arrows, adding them to his quiver. "Never know when 
we'll need more ammunition."

Eglath picks up one of the scimitars, testing its balance. "Backup weapon. 
Mine might break." He straps it to his belt.

The rest of the goblin gear—bent bows, torn leather armor—isn't worth 
carrying.
```

---

## Step 5: Complete Post-Combat Narration

```
NARRATION:
You stand over the goblin corpses, catching your breath. The forest is 
quiet now, but the smell of blood will attract scavengers—or worse. 
You need to keep moving.

**POST-COMBAT SUMMARY:**
✅ Combat ended (2 rounds)
✅ XP distributed: +50 XP each (8,340 / 14,000 to Level 6)
✅ Currency looted: 7 cp, 5 sp total (distributed)
✅ Items taken: 8 arrows, 1 scimitar
✅ Obsidian sheets updated in real-time

**PARTY STATUS:**
- **Eglath Bearkiller**: 27/65 HP ⚠️ (heavily wounded)
  - Resources: 1/3 Rages remaining
  - Currency: 2,150 gp, 5 sp, 3 cp
  
- **Torgga Brawnanvil**: 28/45 HP ⚠️ (wounded)
  - Resources: 3/4 Level 1 slots, 1/1 Channel Divinity
  - Currency: 4,807 gp, 10 sp, 9 cp

Both of you are badly hurt from the dawn siege and this ambush. You need 
healing—soon.

ASK:
What do you do next?

ACTIONS:
1. **Short Rest** (1 hour) - Spend Hit Dice to heal, Eglath recovers rage
2. **Use Healing Potions** - Torgga has 4, Eglath has 2 (2d4+2 HP each)
3. **Channel Divinity: Preserve Life** - Torgga heals up to 25 HP total
4. **Press On** - No time to rest, must reach Phandalin before dark
5. **Search the Area** - Look for tracks, signs of more goblins
```

---

## 🎯 Summary: What Happened

**Automatic Actions (AI does these):**
1. ✅ Ended combat with `end_combat_tool()`
2. ✅ Calculated XP (100 XP total, 50 per PC)
3. ✅ Called `update_character_xp()` for each PC
4. ✅ Rolled currency loot (7 cp, 5 sp)
5. ✅ Divided currency among party
6. ✅ Called `update_character_currency()` for each PC
7. ✅ Determined item loot
8. ✅ Listed items with quantity + weight

**Player Actions (AI asks, players decide):**
9. ❓ Asked what items to take
10. ✅ Players chose: arrows + scimitar
11. ✅ Called `add_inventory_item()` for chosen items
12. ✅ Updated Obsidian inventory tables

**Final Steps:**
13. ✅ Provided complete post-combat narration
14. ✅ Showed party status (HP, resources, currency)
15. ✅ Asked "What do you do next?"

---

## ⏱️ Time Investment

**Total time for post-combat procedure:** ~2-3 minutes
- XP calculation: 10 seconds
- Currency rolls: 20 seconds
- Player item choice: 1-2 minutes
- MCP tool calls: 30 seconds
- Narration: 30 seconds

**Result:** Characters are fully updated in Obsidian, players know their status, game continues smoothly!

---

## 🔧 MCP Tools Used

```javascript
// 1. End combat
end_combat_tool({combat_id})

// 2. Distribute XP
update_character_xp(character_name, xp_amount)  // Called 2× (once per PC)

// 3. Distribute currency
update_character_currency(character_name, {cp, sp, gp})  // Called 2× (once per PC)

// 4. Add items
add_inventory_item(character_name, item_name, quantity, weight)  // Called 2× (arrows + scimitar)

// 5. Roll dice for loot
roll_dice(expression, reason, character)  // Called 2× (cp + sp)
```

---

## ✅ Verification Checklist

After post-combat procedure, verify:

- [ ] XP added to all participating PCs ✅
- [ ] Currency rolled and distributed ✅
- [ ] Currency updated in Obsidian ✅
- [ ] Items listed with quantity + weight ✅
- [ ] Players asked what to take ✅
- [ ] Chosen items added to Obsidian inventory tables ✅
- [ ] Post-combat narration provided ✅
- [ ] Party status shown (HP, resources) ✅
- [ ] "What do you do next?" asked ✅

**All done! Ready for the next adventure!** 🎲⚔️
