# Encounter Execution Guide

**Source:** Based on Dungeon Master's Guide 2024, "Running Combat" section (Chapter 2)

This document provides canonical guidance for executing combat encounters in D&D 5e, based on the official Dungeon Master's Guide 2024.

## Core Principles

### Combat Starts When DM Says It Starts
- Combat starts when—and only when—the DM says it does
- Some characters have abilities that trigger on an Initiative roll; the DM, not the players, decides if and when Initiative is rolled
- In any situation where a character's actions initiate combat, the DM can give the acting character Advantage on their Initiative roll

### Initiative
- **Rolling Initiative:** When combat starts, every participant rolls Initiative (Dexterity check)
- **DM Rolls for Monsters:** The DM rolls for all monsters
- **Groups of Identical Creatures:** For a group of identical creatures, the DM makes a single roll, so each member of the group has the same Initiative
- **Initiative Scores (Optional):** The DM can use Initiative scores instead of rolling to speed up combat
  - Character's Initiative score = 10 + all modifiers (Dexterity modifier + special modifiers)
  - Monster's Initiative score is listed in stat block
  - Advantage on Initiative: +5 to score
  - Disadvantage on Initiative: -5 to score
- **Ties:** If a tie occurs, the DM decides the order among tied monsters, and the players decide the order among tied characters. The DM decides if the tie is between a monster and a player character.

### Turn Order
- Combat unfolds in rounds and turns
- A round represents about 6 seconds in the game world
- During a round, each participant in a battle takes a turn
- The order of turns is determined at the beginning of combat when everyone rolls Initiative
- Once everyone has taken a turn, the fight continues to the next round if neither side is defeated
- **The Initiative order remains the same from round to round**

## Combat Flow

### Step 1: Establish Positions
- The DM determines where all the characters and monsters are located
- Given the adventurers' marching order or their stated positions in the room or other location, the DM figures out where the adversaries are—how far away and in what direction

### Step 2: Roll Initiative
- Everyone involved in the combat encounter rolls Initiative
- This determines the order of combatants' turns
- DM tracks Initiative order (see Tracking Initiative below)

### Step 3: Take Turns
- Each participant in the battle takes a turn in Initiative order
- When everyone involved in the combat has had a turn, the round ends
- Repeat this step until the fighting stops

## Tracking Initiative

The DM should track Initiative using one of these methods:

### Hidden List
- Track Initiative on a list players can't see (behind DM screen, spreadsheet, app, index cards)
- Allows tracking combatants who haven't been revealed yet
- Use as place to record current Hit Points of monsters and other useful notes
- Tell players when it's their characters' turn
- When calling out a character whose turn is starting, consider also mentioning who's next

### Open List
- Track Initiative on a list visible to players (whiteboard, battle mat, index cards, virtual tabletop)
- Makes everyone aware of the order of play
- Players know when their characters' turns are coming up so they can plan actions in advance
- Players know when the monsters act, although you can hold off on adding monsters to the list until they take their first turns

## Tracking Monster Hit Points

- During a combat encounter, the DM (or a designated player) should track how much damage each monster takes
- Most DMs track damage in secret so their players don't know how many Hit Points a monster has remaining
- For groups of identical monsters, assign them unique features or identifiers to differentiate them
- Two tracking methods:
  1. **Subtract from Max HP:** Track each monster's current HP, subtracting damage as it's dealt
  2. **Add Damage Taken:** Track how much damage each monster has taken, adding to that number as characters deal damage (generally easier than subtracting)

## Running Turns

### Player Turns
- When it's a player character's turn, ask the player what their character does
- Allow the player to describe their character's action
- The player should explain what their spells and abilities do (the DM has enough to keep track of)
- Resolve the action according to the rules
- Narrate the results (see Narration in Combat below)

### Monster Turns
- **The DM controls all monsters and decides their actions**
- The DM should make monsters act in ways that are:
  - Tactically reasonable (attack nearest threat, retreat when badly wounded, etc.)
  - Based on creature intelligence and nature
  - Consistent with D&D 5e creature behavior patterns
- The DM rolls for the monsters (attack rolls, damage, saves, etc.)
- Process the results immediately
- Move to the next turn in Initiative order

### Keeping Combat Moving
- Process turns efficiently without unnecessary pauses
- For enemy turns, process them automatically without asking players what to do
- Only pause for player input when it's a player character's turn
- If combat becomes a slog, use techniques to get things moving (see "Keeping Combat Moving" in DMG)

## Narration in Combat

- Use flavorful descriptions while clearly communicating what's happening in game terms
- Combine narrative descriptions with game rules
- Avoid using only "gamespeak" - mix narrative and mechanical language
- Describe how hurt creatures are (Bloodied status, visible wounds, etc.) to give players a sense of progress
- Share information about creature characteristics (resistances, immunities, etc.) as they become apparent
- Describe monster actions clearly so players understand what's happening

## Ending Combat

- Combat ends when one side or the other is defeated (killed, knocked out, surrendered, or fled)
- Combat can also end when both sides agree to end it
- When combat ends, the DM should update the game state and continue with the narrative

## State Management

### During Combat
- Track Initiative order throughout the encounter
- Track HP, AC, conditions, and status for all combatants
- Update state after each action (damage, healing, conditions)
- Update CURRENT_STATE.json to reflect combat status

### After Combat
- Mark combat as ended in CURRENT_STATE.json
- Record the encounter in the encounters array
- Update character HP, resources, and conditions
- Award XP and distribute loot
- Continue with the narrative

## Critical Workflow Requirements

1. **Combat Initiation:**
   - Update CURRENT_STATE.json immediately when combat begins
   - Set `/combat/initiated` = true
   - Set `/combat/ended` = false
   - Set `/combat/round` = 1
   - Add `/combat/initiative_order` array with all combatants and their Initiative values
   - Add `/combat/combatants` object with HP, AC, status for all combatants
   - Update `/scene/location` and `/scene/description` to reflect combat location

2. **Turn Processing:**
   - Process turns in Initiative order (highest to lowest)
   - Process ALL enemy turns automatically in sequence (do not pause for player input)
   - Pause ONLY for player character turns (request action)
   - Update HP, spell slots, and resources immediately as they change
   - Update state after each turn

3. **Real-Time Updates:**
   - Update Google Sheets immediately when HP changes
   - Update Google Sheets immediately when spell slots are used
   - Update Google Sheets immediately when resources are used (rage, action surge, etc.)
   - Never proceed with combat using outdated HP/resource values

4. **State Consistency:**
   - Maintain accurate Initiative order throughout combat
   - Track all combatants' HP, status, and conditions
   - Update state file after each significant change
   - Ensure state accurately reflects combat status at all times

## Common Mistakes to Avoid

1. **Don't skip player turns** - Process every turn in Initiative order
2. **Don't pause between enemy turns** - Process all enemy turns automatically, then pause for player input
3. **Don't process turns out of order** - Always follow the Initiative order established at the start of combat
4. **Don't forget to update state** - State must reflect combat status throughout the encounter
5. **Don't proceed with outdated values** - Always update HP/resources before proceeding with combat
6. **Don't ask players what enemies should do** - The DM controls all monsters and decides their actions

