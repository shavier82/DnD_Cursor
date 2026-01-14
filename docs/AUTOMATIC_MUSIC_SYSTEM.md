# Automatic Music System

## Overview

The Music/Ambience MCP automatically changes background music based on:
1. **Location changes** (tavern → dungeon → wilderness)
2. **Combat state** (ambient → combat → ambient)
3. **Scene atmosphere** (peaceful → tense → creepy)

## Music Triggers

### Location-Based Music

| Location Type | Music Scene | Examples |
|--------------|-------------|----------|
| Underground/Caves | `dungeon` | Barthen's Well tunnels, Zorzula's Rest |
| Town/Settlement | `town` | Phandalin streets, marketplace |
| Tavern/Inn | `tavern` | Sleeping Giant, Stonehill Inn |
| Wilderness | `wilderness` | Traveling between towns |
| Forest | `forest` | Neverwinter Wood |
| Ocean/Water | `ocean` | Coastal areas, ships |
| Temple/Shrine | `temple` | Shrine of Luck |
| Castle/Fort | `castle` | Major fortifications |
| Swamp | `swamp` | Marsh areas |
| Creepy/Haunted | `creepy` | Graveyards, haunted areas |

### Combat Music

**When combat starts:**
- Roll initiative → Switch to `combat` music
- High-energy, tense combat theme

**When combat ends:**
- Last enemy defeated → Switch back to **location-appropriate ambient**
- Example: After dungeon combat → back to `dungeon` ambient

### Atmospheric Music

**Special scenes:**
- `peaceful` - Camp, long rest, safe areas
- `tense` - Stealth, danger approaching, investigation
- `creepy` - Horror elements, undead encounters

## Implementation

### Automatic Triggers

**DM AI automatically calls music changes when:**

1. **Scene transitions:**
   ```
   Party enters tunnels → play_ambient("dungeon")
   Party exits to town → play_ambient("town")
   ```

2. **Combat state changes:**
   ```
   Roll initiative → play_ambient("combat")
   Combat ends → play_ambient(<previous_location_music>)
   ```

3. **Atmosphere shifts:**
   ```
   Entering graveyard → play_ambient("creepy")
   Making camp → play_ambient("peaceful")
   ```

### Music State Tracking

The `CURRENT_STATE.json` tracks:
```json
{
  "scene": {
    "location": "Barthen's Well - Underground Tunnels",
    "music_scene": "dungeon",
    "in_combat": false
  }
}
```

### Combat Music Flow

```
1. Party explores dungeon (dungeon ambient playing)
2. Encounter triggered → Roll initiative
3. DM calls: play_ambient("combat")
4. Combat proceeds with combat music
5. Last enemy defeated
6. DM calls: play_ambient("dungeon")
7. Exploration continues with dungeon ambient
```

## DM Workflow

**The DM AI should:**

1. **On location change:**
   - Determine appropriate music scene
   - Call `play_ambient(scene=<appropriate_scene>)`
   - Update `CURRENT_STATE.json` with `music_scene`

2. **On combat start:**
   - Save current music scene
   - Call `play_ambient(scene="combat")`
   - Set `in_combat: true`

3. **On combat end:**
   - Call `play_ambient(scene=<saved_location_music>)`
   - Set `in_combat: false`

4. **Silent operation:**
   - Don't announce music changes to players
   - Just make the calls in the background

## Examples

### Example 1: Dungeon Exploration → Combat → Exploration

```
NARRATION: You descend into the dark tunnels beneath Barthen's Well...
[DM calls: play_ambient("dungeon")]

(Later)
NARRATION: Three goblins leap from the shadows! Roll initiative!
[DM calls: play_ambient("combat")]

(Combat happens)
NARRATION: The last goblin falls. The tunnels are quiet once more.
[DM calls: play_ambient("dungeon")]
```

### Example 2: Travel Day

```
NARRATION: You leave Phandalin at dawn, heading into the wilderness...
[DM calls: play_ambient("wilderness")]

(8 hours later)
NARRATION: As evening falls, you make camp in a small clearing.
[DM calls: play_ambient("peaceful")]
```

### Example 3: Town Investigation

```
NARRATION: You enter the bustling marketplace of Phandalin.
[DM calls: play_ambient("town")]

NARRATION: Torgga pushes open the door to the Sleeping Giant tavern.
[DM calls: play_ambient("tavern")]

NARRATION: You step back outside into the town square.
[DM calls: play_ambient("town")]
```

## Music Volume Control

**User can control:**
- Volume via their system mixer
- Mute/unmute via system controls
- Stop music with `stop_music()` MCP tool

**Music loops infinitely** until:
- New music is triggered
- User calls `stop_music()`
- Session ends

## Technical Details

**Backend:** pygame.mixer
**Format:** MP3, OPUS, WAV, M4A, WEBM
**Loop:** Infinite (`loops=-1`)
**Playback:** Background, non-blocking
**Control:** MCP Music/Ambience server

## Best Practices

1. **Change music on major location shifts**, not every room
2. **Always switch to combat music** when initiative is rolled
3. **Return to ambient** after combat ends
4. **Use tense music** for stealth/danger buildup
5. **Don't over-trigger** - let scenes breathe with consistent music

