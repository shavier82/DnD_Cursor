# D&D Music & Ambience MCP Server

Provides ambient music and sound effects for D&D sessions using **LOCAL audio files**.

## Features

- 🎵 **16 Scene Types**: tavern, forest, dungeon, combat, town, castle, temple, wilderness, creepy, peaceful, tense, ocean, storm, swamp, winter, wagon
- 📂 **Local Files**: Uses your music collection from `C:\Users\ksist\Music\D&D_Ambient`
- 🔊 **80+ Sound Effects**: Spells, weapons, traps, environment sounds from `C:\Users\ksist\Music\D&D_SFX`
- 🎲 **Random Selection**: Automatically picks a track for variety
- 🎧 **Windows Media Player**: Plays audio directly on your system

## Available Tools

### `play_ambient(scene: str, auto_open: bool = True)`
Play ambient music for a specific scene from your local files.

**Example:**
```python
play_ambient(scene="tavern")
play_ambient(scene="combat", auto_open=False)
```

### `play_sfx(sfx_name: str)`
Play a sound effect from your local SFX collection.

**Example:**
```python
play_sfx(sfx_name="spell_fireball")
play_sfx(sfx_name="sword_slash")
play_sfx(sfx_name="door_open")
```

### `list_scenes()`
List all available scene types and their audio files.

### `list_sfx()`
List all available sound effects, organized by category.

### `get_current_track()`
Get information about the currently playing track.

### `stop_music()`
Stop the current music.

## Usage in D&D Sessions

**When players enter a tavern:**
```python
play_ambient(scene="tavern")
```

**When combat starts:**
```python
play_ambient(scene="combat")
```

**When exploring a forest:**
```python
play_ambient(scene="forest")
```

**When a storm hits:**
```python
play_ambient(scene="storm")
```

## Available Scenes

- **tavern** - Medieval tavern ambience
- **forest** - Forest and woodland sounds
- **dungeon** - Dark dungeon / cave atmosphere
- **combat** - Epic battle music
- **town** - Villages, cities, marketplaces
- **castle** - Castles and royal courts
- **temple** - Sacred temple atmosphere
- **wilderness** - Mountains, deserts
- **creepy** - Spooky, graveyard ambience
- **peaceful** - Camp and calm music
- **tense** - Suspenseful / astral music
- **ocean** - Ocean, ships, underwater
- **storm** - Thunderstorms
- **swamp** - Swamp ambience
- **winter** - Winter towns
- **wagon** - Wagon travel sounds

## Sound Effect Categories

- **Spells** - All spell types (fire, ice, lightning, healing, etc.)
- **Weapons** - Swords, axes, arrows, daggers, shields
- **Traps** - Darts, pitfalls, snares, spikes
- **Environment** - Doors, chests, footsteps, weather

## Adding Custom Music

Simply add audio files to:
- `C:\Users\ksist\Music\D&D_Ambient\` - For ambient music
- `C:\Users\ksist\Music\D&D_SFX\` - For sound effects

Supported formats: `.mp3`, `.opus`, `.wav`, `.m4a`, `.webm`

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure in Cursor (already done via setup script)

3. Restart Cursor

4. Test:
   ```python
   list_scenes()
   play_ambient(scene="tavern")
   ```

## Notes

- Music plays directly on your system using Windows Media Player
- Automatically scans your local music directories on startup
- No internet connection required
- Supports multiple audio formats (.mp3, .opus, .wav, .m4a, .webm)
- Sound effects play instantly without stopping ambient music
- To stop music, use `stop_music()` or the tool will kill wmplayer.exe


