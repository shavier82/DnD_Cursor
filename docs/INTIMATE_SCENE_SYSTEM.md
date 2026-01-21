# Intimate Scene System - Turn-Based Collaborative Roleplay

## Overview
A D&D-style turn-based system for collaborative intimate/romantic scenes between two partners. Designed to create a back-and-forth narrative where both partners guide the story.

## Core Mechanics

### 1. Turn Structure
- **Initiative Roll**: Both partners roll 1d20 + Charisma modifier to determine who goes first
- **Alternating Turns**: Partners take turns describing actions
- **Turn Length**: Each turn is 1-3 actions (similar to D&D action/bonus action)
- **Response Time**: Partner has time to respond/react before next turn

### 2. Action Types
Similar to D&D action economy:

**Main Action** (1 per turn):
- Physical action (touch, kiss, undress, position change)
- Verbal action (whisper, command, question)
- Movement (change position, guide partner)

**Bonus Action** (1 per turn, optional):
- Minor touch (hand placement, gentle caress)
- Quick verbal (moan, whisper, encouragement)
- Eye contact, expression

**Reaction** (unlimited, on partner's turn):
- Respond to touch (gasp, arch, pull closer)
- Verbal response (yes, more, please)
- Physical response (guide hand, press closer)

### 3. Intensity System
Track arousal/desire on a scale (0-100 or 0-10):

**Intensity Levels:**
- 0-20: **Building** - Initial attraction, first touches
- 21-40: **Growing** - Clothes coming off, more intimate contact
- 41-60: **Intense** - Foreplay, heavy touching, oral
- 61-80: **Passionate** - Penetration, active sex
- 81-100: **Peak** - Climax, multiple orgasms, intense release

**Mechanics:**
- Actions increase intensity (by 1-5 points based on success)
- Dice rolls can modify intensity gains
- Natural pacing - intensity should build gradually
- Either partner can request intensity check: "How intense is this getting?"

### 4. Optional Dice Mechanics

**When to Roll:**
- Optional, not required
- Adds randomness and excitement
- Can be skipped for pure narrative

**Roll Types:**

**Intensity Roll** (1d10):
- Roll when taking an action
- Result = intensity gained (1-10 points)
- Natural 10 = critical success (double intensity, special moment)
- Natural 1 = fumble (action doesn't land, try something else)

**Pleasure Roll** (1d20 + Charisma):
- DC varies by intensity level (DC 10 at low, DC 15 at high)
- Success = action is very effective, partner responds strongly
- Failure = action is good but could be better, partner still enjoys

**Endurance Roll** (1d20 + Constitution):
- When approaching climax
- DC = current intensity level
- Success = can hold off, continue
- Failure = climax now (or soon)

**Connection Roll** (1d20 + Wisdom):
- For emotional/intimate moments
- Success = deep connection, meaningful moment
- Failure = still good, but more physical than emotional

### 5. Safety & Consent System

**Safeword System:**
- **RED** = Stop immediately, scene ends
- **YELLOW** = Slow down, change direction, less intensity
- **GREEN** = Continue, all good
- **PAUSE** = Take a break, discuss, resume later

**Consent Checks:**
- Before new activities: "Would you like to try [X]?"
- If intensity jumps too fast: "Is this okay?"
- Before explicit actions: "May I [X]?"

**Boundaries:**
- Set before scene starts
- Can be updated during scene (use YELLOW)
- Stored in state file for future sessions

### 6. State Tracking

**Scene State** (in CURRENT_STATE.json):
```json
{
  "intimate_scene": {
    "active": true,
    "intensity": 35,
    "current_turn": "partner1",
    "turn_count": 3,
    "positions": {
      "partner1": "standing",
      "partner2": "standing"
    },
    "clothing": {
      "partner1": "partially_undressed",
      "partner2": "fully_clothed"
    },
    "arousal": {
      "partner1": 40,
      "partner2": 35
    },
    "last_action": "kiss",
    "mood": "passionate",
    "safeword_status": "green"
  }
}
```

**Track:**
- Current intensity level
- Individual arousal levels
- Clothing state
- Positions
- Last actions taken
- Mood/atmosphere
- Turn order

### 7. Turn Flow Example

**Turn 1 - Partner 1:**
- Action: "I pull you close and kiss you deeply"
- Roll (optional): 1d10 = 7 (intensity +7)
- Narrator: Describes the kiss, partner's response
- State: Intensity 0 → 7

**Turn 2 - Partner 2:**
- Reaction: "I moan into the kiss and press my body against yours"
- Action: "My hands find your waist, pulling you closer"
- Roll (optional): 1d10 = 5 (intensity +5)
- Narrator: Describes the response, building tension
- State: Intensity 7 → 12

**Turn 3 - Partner 1:**
- Action: "I break the kiss and whisper in your ear: 'I want you'"
- Bonus Action: "My hand slides up your back"
- Roll (optional): 1d20 + 3 (Cha) = 18 vs DC 12 (Success!)
- Narrator: Describes the intense moment, partner's strong reaction
- State: Intensity 12 → 20 (bonus from success)

### 8. Pacing Control

**Speed Options:**
- **Slow Burn** - Take time, build tension, detailed descriptions
- **Medium** - Balanced pacing, natural progression
- **Fast** - More action per turn, quicker intensity build

**Either partner can:**
- Request slower pace: "Let's slow down"
- Request faster pace: "I need more"
- Pause: "Hold on, let me catch my breath"
- Skip ahead: "We move to the bed"

### 9. Narrative Prompts

**AI Narrator Role:**
- Describes the scene, atmosphere, sensations
- Bridges actions between partners
- Adds sensory details (touch, taste, sound, sight)
- Maintains mood and pacing
- Respects safewords and boundaries

**Partner Actions:**
- Describe what you do
- Describe what you want
- Describe how you feel
- Guide the narrative

**Example:**
- Partner 1: "I kiss your neck"
- AI Narrator: "Your lips find their neck, warm and soft. They tilt their head, giving you better access, and you can feel their pulse quicken beneath your touch. A soft sigh escapes them."
- Partner 2: "I arch into your touch and whisper 'more'"
- AI Narrator: "Their body responds to your touch, pressing closer. The word is barely a whisper, but it sends heat straight to your core. You can feel their desire matching your own."

### 10. Session Management

**Save Points:**
- Can pause at any time
- State saved automatically
- Resume later from same intensity/position
- "We'll continue this later" - saves state

**Session End:**
- Natural conclusion (climax, cuddling, sleep)
- "That's enough for now"
- State saved, can continue next time

### 11. Special Moments

**Critical Success (Natural 10 on intensity roll):**
- Special moment, extra intensity
- Partner has strong reaction
- Opportunity for deeper connection
- "That was incredible"

**Climax Scene:**
- Triggered when intensity reaches 80+
- Either partner can initiate
- Can be mutual or individual
- Narrated with care and passion
- Aftermath: cuddling, talking, sleep

**Emotional Beats:**
- Connection rolls can trigger emotional moments
- "I love you" moments
- Deep intimacy beyond physical
- Relationship building

### 12. Implementation in System

**Commands:**
- `/intimate_start` - Begin intimate scene
- `/intimate_action <description>` - Take an action
- `/intimate_roll <type>` - Optional dice roll
- `/intimate_intensity` - Check current intensity
- `/intimate_pause` - Pause scene
- `/intimate_resume` - Resume from pause
- `/intimate_end` - End scene naturally
- `/safeword <color>` - Use safeword (RED/YELLOW/GREEN)

**State Updates:**
- After each turn, update intensity, arousal, positions
- Track turn count
- Save state automatically
- Log actions for continuity

### 13. Example Session Flow

1. **Setup**: Partners agree to scene, set boundaries, choose characters
2. **Initiative**: Roll to see who goes first
3. **Turn 1**: Partner 1 describes action, optional roll, narrator responds
4. **Turn 2**: Partner 2 reacts and takes action, narrator bridges
5. **Continue**: Alternating turns, building intensity
6. **Pacing**: Either partner can slow/speed up
7. **Climax**: When ready, narrate climax scene
8. **Aftermath**: Cuddling, talking, or end scene
9. **Save**: State saved for next time

### 14. Benefits of This System

- **Collaborative**: Both partners guide the story
- **Structured**: Clear turn order prevents confusion
- **Flexible**: Can use dice or pure narrative
- **Safe**: Built-in safeword and consent checks
- **Paced**: Intensity system ensures natural progression
- **Continuable**: Can pause and resume later
- **Fun**: D&D mechanics add excitement and randomness

### 15. Customization Options

- **Dice Optional**: Can skip all rolls for pure narrative
- **Intensity Scale**: Adjust scale (0-10, 0-100, etc.)
- **Turn Length**: Adjust actions per turn
- **Pacing**: Set default speed preference
- **Narrative Style**: Adjust AI narrator verbosity
- **Mechanics**: Add/remove roll types as desired
































