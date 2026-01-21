# Post-Combat Procedures - Loot & XP Distribution

**MANDATORY:** Execute these steps after EVERY combat encounter.

---

## ⚔️ Step 1: End Combat & Get Summary

```javascript
end_combat_tool({combat_id: "<id>"})
```

This returns:
- Combat duration
- Rounds elapsed
- Final HP for all combatants
- Obsidian sync status

---

## 💰 Step 2: Calculate & Distribute XP (AUTOMATIC)

### **A. Calculate Total XP**

Use defeated enemy CR to determine XP:

| CR | XP per Enemy |
|----|--------------|
| 0 | 10 XP |
| 1/8 | 25 XP |
| 1/4 | 50 XP |
| 1/2 | 100 XP |
| 1 | 200 XP |
| 2 | 450 XP |
| 3 | 700 XP |
| 4 | 1,100 XP |
| 5 | 1,800 XP |

**Or use MCP:** `lookup_monster(name)` returns XP value.

### **B. Divide Among Party Members**

**Formula:** `XP_per_character = Total_XP / Number_of_PCs_who_participated`

**Example:**
- 2 Goblins defeated (CR 1/4 each) = 100 XP total
- 2 PCs participated
- Each PC gets: 100 / 2 = **50 XP**

### **C. Update Character Sheets (AUTOMATIC)**

```javascript
// For each PC who participated:
update_character_xp("Torgga_Brawnanvil", 50)
update_character_xp("Eglath_Bearkiller", 50)
```

### **D. Narrate XP Gain**

```
NARRATION:
As the last enemy falls, you feel the rush of experience—another battle 
survived, another lesson learned in the art of combat.

**XP EARNED:**
- Torgga Brawnanvil: +50 XP (8,340 / 14,000 to Level 6)
- Eglath Bearkiller: +50 XP (8,340 / 14,000 to Level 6)
```

**CRITICAL:** Always show current XP / next level XP so players know progress!

---

## 🪙 Step 3: Distribute Currency (AUTOMATIC)

### **A. Determine Loot**

Roll for loot or use encounter-specific loot table:

**Example Goblin Loot (per goblin):**
- 1d6 copper pieces (cp)
- 1d4 silver pieces (sp)
- 10% chance: 1d4 gold pieces (gp)

### **B. Roll Currency Loot**

```javascript
roll_dice("2d6", "Goblin copper loot (2 goblins)", "DM")
// Result: 7 cp total

roll_dice("2d4", "Goblin silver loot (2 goblins)", "DM")
// Result: 5 sp total
```

### **C. Divide Currency Among Party**

**Formula:** `Amount_per_PC = Total_Amount / Number_of_PCs`

**Example:**
- 7 cp total, 2 PCs = 3 cp each (1 cp remainder—flip coin or let players decide)
- 5 sp total, 2 PCs = 2 sp each (1 sp remainder)

**For remainders:** Either:
1. Give to party "communal fund"
2. Let players decide who takes it
3. Round up for simplicity

### **D. Update Character Sheets (AUTOMATIC)**

```javascript
// Get current currency first (read from Obsidian)
get_character_combat_stats("Torgga_Brawnanvil")

// Then add new currency
update_character_currency("Torgga_Brawnanvil", {
  gp: 0,  // +0 gold
  sp: 2,  // +2 silver
  cp: 3   // +3 copper
})

update_character_currency("Eglath_Bearkiller", {
  gp: 0,
  sp: 2,
  cp: 3
})
```

**NOTE:** The MCP adds to existing currency, doesn't replace it.

### **E. Narrate Currency Loot**

```
NARRATION:
You search the goblin corpses. Their pockets yield a meager haul—7 copper 
pieces and 5 silver pieces, divided between you.

**CURRENCY GAINED:**
- Torgga: +3 cp, +2 sp (Total: 4,807 gp, 9 sp, 8 cp)
- Eglath: +3 cp, +2 sp (Total: 2,150 gp, 5 sp, 3 cp)
```

---

## 📦 Step 4: Distribute Items (ASK PLAYERS)

### **A. Determine Item Loot**

Roll or use encounter-specific loot:

**Example Goblin Items:**
- 2x Scimitar (1d6 slashing, 2 lb each)
- 2x Shortbow (1d6 piercing, 2 lb each)
- 1d4 arrows per goblin (1 lb per 20 arrows)
- 1x Leather Armor (worn, AC 11, 10 lb)
- 10% chance: Potion of Healing (2d4+2 HP, 0.5 lb)

### **B. List Available Items**

```
ASK:
The goblins carried:
- 2x Scimitar (1d6 slashing, 2 lb each)
- 2x Shortbow (1d6 piercing, 2 lb each)
- 8 arrows total (1 lb per 20)
- 1x Worn Leather Armor (AC 11, 10 lb)

What do you want to take?

ACTIONS:
1. Take everything (distribute among party)
2. Take weapons only (scimitars + bows)
3. Leave it all (not worth the weight)
4. Custom (tell me what you want)
```

### **C. Players Decide**

Wait for player input. Common responses:
- "Take the arrows"
- "Eglath takes the scimitars"
- "Leave it, we don't need goblin junk"

### **D. Update Inventory (AUTOMATIC for chosen items)**

```javascript
// Example: Players take arrows and one scimitar
add_inventory_item("Torgga_Brawnanvil", "Arrow", 8, 0.4)  // 8 arrows, ~0.4 lb total
add_inventory_item("Eglath_Bearkiller", "Scimitar", 1, 2)  // 1 scimitar, 2 lb
```

### **E. Update Obsidian Inventory Table**

**Obsidian character sheets have inventory in table format:**

```markdown
## Equipment & Inventory

| Item | Quantity | Weight (lb) | Notes |
|------|----------|-------------|-------|
| Arrow | 8 | 0.4 | Standard arrows |
| Scimitar | 1 | 2 | Looted from goblin |
| Potion of Healing | 4 | 2 | Restores 2d4+2 HP each |
| Rope, Hempen (50 ft) | 1 | 10 | Standard rope |
```

**When adding items:**
- If item exists: Increment quantity, update weight
- If new item: Add new row to table
- Always include quantity and weight

### **F. Check Encumbrance (Optional)**

**Carrying Capacity = STR × 15 lb**

Example:
- Eglath (STR 19): 285 lb capacity
- Torgga (STR 14): 210 lb capacity

Warn if characters exceed capacity:
```
⚠️ Warning: Torgga is now carrying 215 lb (capacity: 210 lb). 
You are encumbered (speed reduced by 10 ft).
```

---

## 🎁 Step 5: Special/Magic Items (ASK + DESCRIBE)

If magic items or special loot is found:

### **A. Use Identify or Investigation**

```
ASK:
You find a ornate dagger with runes etched into the blade. It radiates faint magic.

Do you:
1. Cast Identify (if anyone has it prepared)
2. Make an Arcana check to recognize the runes
3. Attune to it later
4. Leave it for now

ACTIONS:
[Present options]
```

### **B. Reveal Information Based on Check/Spell**

```javascript
// If they cast Identify:
lookup_magic_item("Dagger of Venom")  // Use MCP if available

// Narrate full properties
```

### **C. Add to Inventory with Details**

```javascript
add_inventory_item("Torgga_Brawnanvil", "Dagger of Venom", 1, 1, {
  rarity: "rare",
  attunement: true,
  properties: "+1 weapon, poison damage"
})
```

---

## 🎬 Step 6: Complete Narration

After all loot/XP distributed:

```
NARRATION:
You gather what's useful from the battlefield and press onward. The forest 
is quiet now, but you know more dangers lurk ahead.

**POST-COMBAT SUMMARY:**
✅ XP distributed (+50 XP each)
✅ Currency looted (+3 cp, +2 sp each)
✅ Items taken (8 arrows, 1 scimitar)
✅ Character sheets updated in Obsidian

**PARTY STATUS:**
- Eglath: 27/65 HP, 1/3 Rages remaining
- Torgga: 28/45 HP, 3/4 Level 1 slots remaining

What do you do next?

ACTIONS:
1. Short rest to heal (1 hour, spend Hit Dice)
2. Use healing potions (Torgga has 4)
3. Press onward (no time to rest)
4. Search the area more thoroughly
```

---

## ✅ POST-COMBAT CHECKLIST

After EVERY combat, verify:

- [ ] `end_combat_tool()` called
- [ ] XP calculated and distributed to ALL PCs
- [ ] `update_character_xp()` called for each PC
- [ ] Currency rolled and divided
- [ ] `update_character_currency()` called for each PC
- [ ] Item loot listed (with quantity + weight)
- [ ] Players asked what items to take
- [ ] `add_inventory_item()` called for chosen items
- [ ] Obsidian inventory tables updated
- [ ] Post-combat narration provided
- [ ] Party status shown (HP, resources)
- [ ] "What do you do next?" asked

---

## 🚫 COMMON MISTAKES

❌ **Forgetting to distribute XP** → Always calculate and add after combat  
❌ **Not updating currency in Obsidian** → Use `update_character_currency()` every time  
❌ **Adding items without quantity/weight** → Always include both  
❌ **Not asking players about items** → Let them decide what to take  
❌ **Forgetting remainders** → 7 cp / 2 PCs = 3 each + 1 remainder (address it!)  
❌ **Not showing XP progress** → Always show current XP / next level XP  

---

## 📋 QUICK REFERENCE

```javascript
// 1. End combat
end_combat_tool({combat_id: "..."})

// 2. Distribute XP (automatic)
update_character_xp("Character_Name", xp_amount)

// 3. Distribute currency (automatic)
update_character_currency("Character_Name", {gp: 0, sp: 2, cp: 3})

// 4. List items (ask players)
// → Wait for player decision

// 5. Add chosen items
add_inventory_item("Character_Name", "Item Name", quantity, weight)

// 6. Narrate completion & ask "What next?"
```

---

**REMEMBER:** Post-combat procedures are NOT optional. They ensure:
- Players get rewarded for their efforts
- Character progression is tracked
- Obsidian sheets stay up-to-date
- Nothing is forgotten or lost

**Execute this workflow after EVERY combat!** ⚔️💰📦
