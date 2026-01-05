# Travel System

**Source:** Based on Lost Mine of Phandelver Chapter 3: "Travel Time" and "Wilderness Encounters" sections

This document provides canonical guidance for handling travel and random encounters during overland travel.

## Travel Rules

### Travel Pace

- **Distance per day:** 24 miles
- **Travel time:** 10 hours per day
- **Rest time:** 8 hours per day (long rest)
- **Remaining time:** 6 hours for making/breaking camp, preparing meals, foraging, hunting

### Travel Distance Calculation

1. **Determine distance** between locations (check campaign source material or regional map)
2. **Calculate days needed:** Distance ÷ 24 miles per day
3. **Round up** to nearest full day if partial day remains
4. **Long rests:** One long rest per full day of travel (at end of each day)

### Example: Thundertree to Phandalin

- **Distance:** 50 miles (from Chapter 2: "about fifty miles northwest of Phandalin")
- **Days needed:** 50 ÷ 24 = 2.08 days (rounds to 3 days, or 2 full days + partial day)
- **Long rests:** 2 long rests (after day 1 and day 2)
- **Arrival:** Early on day 3 (after traveling remaining 2 miles)

## Random Encounters

### When to Check

- **Once during the day** (after 10 hours of travel)
- **Once at night** (during the 8-hour rest period)
- **Per full day of travel:** 2 checks (1 day + 1 night)

### Encounter Check Process

1. **Roll 1d20**
2. **If result is 17–20:** An encounter occurs
3. **If encounter occurs:** Roll 1d12 and consult the appropriate Random Encounters table
4. **If no encounter (1–16):** Travel continues uneventfully

### Triboar Trail Random Encounters Table

(From Lost Mine of Phandelver Chapter 3)

**Roll 1d12 to determine encounter type:**

| Day Roll | Night Roll | Result |
|----------|------------|--------|
| 1–2 | 1–3 | 1d4 + 2 stirges |
| — | 4 | 1d4 + 1 ghouls |
| 3–4 | — | 1 ogre |
| 5–6 | 5 | Cragmaw goblin band (see below) |
| 7–8 | 6 | Hobgoblin squad (see below) |
| 9–10 | 7–8 | Bugbear scouts (see below) |
| 11 | 9–10 | 1d4 + 2 wolves |
| 12 | 11–12 | 1 owlbear |

**Note:** Some encounters only occur during day (e.g., ogre) or only at night (e.g., ghouls). Use the appropriate column based on when the encounter check is made.

### Special Encounter Details

#### Cragmaw Goblin Band
- **Composition:** 2d4 goblins led by 1 goblin boss
- **Information:** They know the location of Cragmaw Castle and can provide directions if captured and threatened
- **Treasure:** Boss has a pouch containing 1d10 cp and 1d10 sp

#### Hobgoblin Squad
- **Composition:** 1d4 + 3 hobgoblins
- **Purpose:** Seek the adventurers, hoping to collect a bounty set by the Spider
- **Evidence:** One hobgoblin carries a crudely drawn sketch of one party member with "25 gold pieces for this one" and a symbol of a spider scrawled beneath it

#### Bugbear Scouts
- **Composition:** 2 bugbears
- **Origin:** Part of the band based at Wyvern Tor
- **Behavior:** Look for travelers to ambush as they roam

## Running Random Encounters

1. **Roll encounter check** (1d20, 17–20 triggers)
2. **If triggered:** Roll 1d12 for encounter type
3. **Determine composition** (roll dice as specified)
4. **Run encounter** using standard combat/narrative rules
5. **Continue travel** after encounter is resolved
6. **Track time:** Encounters take time (typically 1–6 rounds = 6–36 seconds, but can be longer for complex encounters)

## Long Rests During Travel

- **Duration:** 8 hours
- **Benefits:** Restore all HP, spell slots, and resources (as per D&D 5e long rest rules)
- **When:** At end of each full day of travel (before next day begins)
- **Update Sheets:** After long rest, update CSV_Resources and CSV_SpellSlots to restore all resources to maximum

## State Management

When processing travel:

1. **Update CURRENT_STATE.json:**
   - Set `/scene/location` to destination
   - Set `/scene/area` if applicable
   - Update `/scene/description` to reflect travel completion
   - Add travel event to `/events/` if significant

2. **Update character resources after long rest:**
   - Restore all resources to max (CSV_Resources)
   - Restore all spell slots to max (CSV_SpellSlots)
   - Restore all HP to max (CSV_Characters)

## Campaign-Specific Travel Tables

Different campaigns or regions may have different random encounter tables. Always check the campaign source material for the appropriate table to use.

