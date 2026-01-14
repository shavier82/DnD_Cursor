#!/usr/bin/env python3
"""
D&D Music & Ambience MCP Server
Provides ambient music and sound effects for D&D sessions using LOCAL audio files.
"""

import asyncio
import json
import logging
import random
import sys
from pathlib import Path
from typing import Any, Dict, List
import threading

# Suppress verbose MCP logging
logging.getLogger("mcp").setLevel(logging.WARNING)
logging.getLogger("mcp.server.stdio").setLevel(logging.WARNING)

# Import MCP SDK
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("ERROR: mcp package not found. Install with: pip install mcp")
    exit(1)

# Import pygame for audio playback
try:
    import pygame
    pygame.mixer.init()
except ImportError:
    print("ERROR: pygame package not found. Install with: pip install pygame")
    exit(1)

# ============================================================
# CONFIGURATION
# ============================================================

MUSIC_DIR = Path(r"C:\Users\ksist\Music\D&D_Ambient")
SFX_DIR = Path(r"C:\Users\ksist\Music\D&D_SFX")
CURRENT_TRACK_PATH = Path(__file__).parent / "current_track.json"

# Scene type mapping (filename keywords → scene names)
SCENE_MAPPING = {
    "tavern": ["tavern"],
    "forest": ["forest"],
    "dungeon": ["dungeon", "cave"],
    "combat": ["combat"],
    "town": ["town", "village", "city", "marketplace"],
    "castle": ["castle", "royal"],
    "temple": ["temple"],
    "wilderness": ["mountains", "desert"],
    "creepy": ["spooky", "graveyard"],
    "peaceful": ["camp"],
    "tense": ["astral"],
    "ocean": ["ocean", "sea", "ship", "underwater", "dock"],
    "storm": ["storm"],
    "swamp": ["swamp"],
    "winter": ["winter"],
    "wagon": ["wagon"]
}

# Load music catalog from local files
def load_local_catalog() -> Dict[str, List[Path]]:
    """Scan local music directory and categorize by scene type."""
    catalog = {scene: [] for scene in SCENE_MAPPING.keys()}
    
    if not MUSIC_DIR.exists():
        print(f"WARNING: Music directory not found: {MUSIC_DIR}", file=sys.stderr)
        return catalog
    
    # Scan all audio files
    for audio_file in MUSIC_DIR.glob("*"):
        if audio_file.suffix.lower() in [".mp3", ".opus", ".wav", ".m4a", ".webm"]:
            filename_lower = audio_file.stem.lower()
            
            # Match to scene type
            for scene, keywords in SCENE_MAPPING.items():
                if any(keyword in filename_lower for keyword in keywords):
                    catalog[scene].append(audio_file)
                    break
    
    return catalog

MUSIC_CATALOG = load_local_catalog()

# Current track state
current_track = {
    "scene": None,
    "track": None,
    "playing": False
}

# Pygame mixer state
music_playing = False

# ============================================================
# MCP SERVER
# ============================================================

app = Server("dnd-music-ambience")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available music/ambience tools."""
    return [
        Tool(
            name="play_ambient",
            description="Play ambient music for a specific scene type using local audio files",
            inputSchema={
                "type": "object",
                "properties": {
                    "scene": {
                        "type": "string",
                        "description": "Scene type (tavern, forest, dungeon, combat, town, castle, temple, wilderness, creepy, peaceful, tense, ocean, storm, swamp, winter, wagon)",
                        "enum": ["tavern", "forest", "dungeon", "combat", "town", "castle", "temple", "wilderness", "creepy", "peaceful", "tense", "ocean", "storm", "swamp", "winter", "wagon"]
                    },
                    "auto_open": {
                        "type": "boolean",
                        "description": "Automatically start playing the audio (default: true)",
                        "default": True
                    }
                },
                "required": ["scene"]
            }
        ),
        Tool(
            name="play_sfx",
            description="Play a sound effect (spell, weapon, trap, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "sfx_name": {
                        "type": "string",
                        "description": "Sound effect name (e.g., 'spell_fireball', 'sword_slash', 'door_open')"
                    }
                },
                "required": ["sfx_name"]
            }
        ),
        Tool(
            name="list_scenes",
            description="List all available scene types and their music files",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_sfx",
            description="List all available sound effects",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_current_track",
            description="Get information about the currently playing track",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="stop_music",
            description="Stop the current music",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    
    if name == "play_ambient":
        return await handle_play_ambient(arguments)
    elif name == "play_sfx":
        return await handle_play_sfx(arguments)
    elif name == "list_scenes":
        return await handle_list_scenes(arguments)
    elif name == "list_sfx":
        return await handle_list_sfx(arguments)
    elif name == "get_current_track":
        return await handle_get_current_track(arguments)
    elif name == "stop_music":
        return await handle_stop_music(arguments)
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

# ============================================================
# AUDIO PLAYBACK (PYGAME)
# ============================================================

def play_audio_file(file_path: Path, loop: bool = True):
    """Play an audio file using pygame mixer with looping."""
    global music_playing
    try:
        pygame.mixer.music.load(str(file_path))
        # -1 means loop forever, 0 means play once
        pygame.mixer.music.play(loops=-1 if loop else 0)
        music_playing = True
        return True
    except Exception as e:
        print(f"ERROR playing audio: {e}", file=sys.stderr)
        return False

def stop_audio():
    """Stop any currently playing audio."""
    global music_playing
    try:
        pygame.mixer.music.stop()
        music_playing = False
    except Exception as e:
        print(f"ERROR stopping audio: {e}", file=sys.stderr)

# ============================================================
# TOOL HANDLERS
# ============================================================

async def handle_play_ambient(args: dict) -> list[TextContent]:
    """Play ambient music for a scene."""
    scene = args.get("scene")
    auto_open = args.get("auto_open", True)
    
    if scene not in MUSIC_CATALOG:
        available = ", ".join([s for s in MUSIC_CATALOG.keys() if MUSIC_CATALOG[s]])
        return [TextContent(
            type="text",
            text=f"❌ Scene '{scene}' not found.\n\nAvailable scenes: {available}"
        )]
    
    tracks = MUSIC_CATALOG[scene]
    if not tracks:
        return [TextContent(
            type="text",
            text=f"❌ No audio files found for scene '{scene}'."
        )]
    
    # Get random track for this scene
    track_path = random.choice(tracks)
    
    # Stop any currently playing music
    stop_audio()
    
    # Update current track
    current_track["scene"] = scene
    current_track["track"] = str(track_path)
    current_track["playing"] = True
    
    # Save current track to file
    with open(CURRENT_TRACK_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "scene": scene,
            "track": str(track_path),
            "playing": True
        }, f, indent=2)
    
    # Play the audio if requested (with looping)
    if auto_open:
        success = play_audio_file(track_path, loop=True)
        play_status = "✅ Now playing (looping)" if success else "❌ Failed to play"
    else:
        play_status = "📂 Track selected (not playing)"
    
    result = f"""🎵 **Now Playing: {scene.upper()}**

**File:** {track_path.name}
**Path:** {track_path}

{play_status}
"""
    
    return [TextContent(type="text", text=result)]

async def handle_play_sfx(args: dict) -> list[TextContent]:
    """Play a sound effect."""
    sfx_name = args.get("sfx_name", "").lower()
    
    if not SFX_DIR.exists():
        return [TextContent(
            type="text",
            text=f"❌ SFX directory not found: {SFX_DIR}"
        )]
    
    # Search for matching SFX file
    matching_files = []
    for sfx_file in SFX_DIR.glob("*"):
        if sfx_file.suffix.lower() in [".mp3", ".wav", ".opus"]:
            if sfx_name in sfx_file.stem.lower():
                matching_files.append(sfx_file)
    
    if not matching_files:
        return [TextContent(
            type="text",
            text=f"❌ Sound effect '{sfx_name}' not found.\n\nUse `list_sfx()` to see available effects."
        )]
    
    # Play the first matching file (no loop for SFX)
    sfx_path = matching_files[0]
    success = play_audio_file(sfx_path, loop=False)
    
    status = "✅ Played" if success else "❌ Failed to play"
    result = f"""🔊 **Sound Effect: {status}**

**File:** {sfx_path.name}
"""
    
    return [TextContent(type="text", text=result)]

async def handle_list_scenes(args: dict) -> list[TextContent]:
    """List all available scenes and their tracks."""
    if not any(MUSIC_CATALOG.values()):
        return [TextContent(type="text", text="❌ No ambient music available.")]
    
    result = "🎵 **Available Ambient Scenes**\n\n"
    
    for scene, tracks in sorted(MUSIC_CATALOG.items()):
        if tracks:
            result += f"**{scene.upper()}** ({len(tracks)} file{'s' if len(tracks) > 1 else ''})\n"
            for track in tracks[:3]:  # Show first 3 files
                result += f"  • {track.name}\n"
            if len(tracks) > 3:
                result += f"  • ... and {len(tracks) - 3} more\n"
            result += "\n"
    
    result += f"\n**Usage:** `play_ambient(scene=\"tavern\")`"
    
    return [TextContent(type="text", text=result)]

async def handle_list_sfx(args: dict) -> list[TextContent]:
    """List all available sound effects."""
    if not SFX_DIR.exists():
        return [TextContent(
            type="text",
            text=f"❌ SFX directory not found: {SFX_DIR}"
        )]
    
    # Categorize SFX by type
    categories = {
        "Spells": [],
        "Weapons": [],
        "Traps": [],
        "Environment": [],
        "Other": []
    }
    
    for sfx_file in sorted(SFX_DIR.glob("*")):
        if sfx_file.suffix.lower() in [".mp3", ".wav", ".opus"]:
            name = sfx_file.stem
            if "spell" in name.lower():
                categories["Spells"].append(name)
            elif any(w in name.lower() for w in ["sword", "axe", "arrow", "dagger", "hammer", "weapon", "shield"]):
                categories["Weapons"].append(name)
            elif "trap" in name.lower():
                categories["Traps"].append(name)
            elif any(w in name.lower() for w in ["door", "chest", "footsteps", "water", "wind", "rain"]):
                categories["Environment"].append(name)
            else:
                categories["Other"].append(name)
    
    result = "🔊 **Available Sound Effects**\n\n"
    
    for category, sfx_list in categories.items():
        if sfx_list:
            result += f"**{category}** ({len(sfx_list)})\n"
            for sfx in sfx_list[:5]:  # Show first 5
                result += f"  • {sfx}\n"
            if len(sfx_list) > 5:
                result += f"  • ... and {len(sfx_list) - 5} more\n"
            result += "\n"
    
    result += f"\n**Usage:** `play_sfx(sfx_name=\"spell_fireball\")`"
    
    return [TextContent(type="text", text=result)]

async def handle_get_current_track(args: dict) -> list[TextContent]:
    """Get the currently playing track."""
    if not current_track["playing"]:
        return [TextContent(type="text", text="🔇 No music currently playing.")]
    
    track_path = Path(current_track["track"])
    scene = current_track["scene"]
    
    result = f"""🎵 **Currently Playing: {scene.upper()}**

**File:** {track_path.name}
**Path:** {track_path}
"""
    
    return [TextContent(type="text", text=result)]

async def handle_stop_music(args: dict) -> list[TextContent]:
    """Stop the current music."""
    if not current_track["playing"]:
        return [TextContent(type="text", text="🔇 No music currently playing.")]
    
    # Stop audio playback
    stop_audio()
    
    # Clear current track
    current_track["scene"] = None
    current_track["track"] = None
    current_track["playing"] = False
    
    # Save state
    with open(CURRENT_TRACK_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "scene": None,
            "track": None,
            "playing": False
        }, f, indent=2)
    
    return [TextContent(
        type="text",
        text="🔇 **Music stopped.**"
    )]

# ============================================================
# MAIN
# ============================================================

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())


