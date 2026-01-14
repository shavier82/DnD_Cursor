#!/usr/bin/env python3
"""
Obsidian Sync MCP Server
Real-time sync service for D&D campaign data in Obsidian vault.

Features:
- File system watcher for real-time changes
- Character data CRUD operations
- Combat state synchronization
- Session log integration
- Health status conversion for enemies
"""

import json
import logging
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import frontmatter

# MCP SDK imports
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
from mcp import types

# File watcher
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Suppress verbose MCP library logs
logging.getLogger("mcp.server.session").setLevel(logging.ERROR)
logging.getLogger("mcp.server.stdio").setLevel(logging.ERROR)

# Global configuration
OBSIDIAN_VAULT_PATH = Path("C:/Users/ksist/Documents/Obsidian/DnD")
WATCH_ACTIVE = False
observer = None

app = Server("obsidian-sync")

# ============================================================================
# HEALTH STATUS CONVERTER
# ============================================================================

def hp_to_status(current_hp: int, max_hp: int) -> str:
    """Convert HP to descriptive status for players
    
    Args:
        current_hp: Current HP
        max_hp: Maximum HP
        
    Returns:
        Status string: Healthy, Hurt, Bloodied, Critical, Unconscious, Dead
    """
    if current_hp <= 0:
        return "Dead" if current_hp < 0 else "Unconscious"
    
    percentage = (current_hp / max_hp) * 100
    
    if percentage >= 90:
        return "Healthy"
    elif percentage >= 70:
        return "Hurt"
    elif percentage >= 50:
        return "Bloodied"
    elif percentage >= 25:
        return "Critical"
    else:
        return "Near Death"


# ============================================================================
# MARKDOWN PARSER/WRITER
# ============================================================================

class ObsidianMarkdown:
    """Parse and write Obsidian markdown with frontmatter"""
    
    @staticmethod
    def read_note(file_path: Path) -> Dict[str, Any]:
        """Read Obsidian note with frontmatter"""
        if not file_path.exists():
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        return {
            'metadata': dict(post.metadata),
            'content': post.content,
            'file_path': str(file_path)
        }
    
    @staticmethod
    def write_note(file_path: Path, metadata: Dict[str, Any], content: str):
        """Write Obsidian note with frontmatter"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        post = frontmatter.Post(content, **metadata)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
    
    @staticmethod
    def update_note(file_path: Path, metadata_updates: Dict[str, Any] = None, 
                    content_append: str = None, content_replace: str = None):
        """Update existing note (merge metadata, append/replace content)"""
        note = ObsidianMarkdown.read_note(file_path)
        if not note:
            raise FileNotFoundError(f"Note not found: {file_path}")
        
        # Update metadata
        if metadata_updates:
            note['metadata'].update(metadata_updates)
        
        # Update content
        if content_replace is not None:
            note['content'] = content_replace
        elif content_append:
            note['content'] += "\n\n" + content_append
        
        ObsidianMarkdown.write_note(file_path, note['metadata'], note['content'])


# ============================================================================
# CHARACTER DATA OPERATIONS
# ============================================================================

class CharacterDataManager:
    """CRUD operations for character data in Obsidian"""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.characters_folder = vault_path / "Player Characters"
    
    def get_character(self, character_name: str) -> Optional[Dict[str, Any]]:
        """Read character data from Obsidian"""
        file_path = self.characters_folder / f"{character_name}.md"
        return ObsidianMarkdown.read_note(file_path)
    
    def get_all_characters(self) -> List[Dict[str, Any]]:
        """Get all player characters"""
        if not self.characters_folder.exists():
            return []
        
        characters = []
        for file_path in self.characters_folder.glob("*.md"):
            note = ObsidianMarkdown.read_note(file_path)
            if note and note['metadata'].get('type') == 'player_character':
                characters.append(note)
        
        return characters
    
    def update_character_hp(self, character_name: str, current_hp: int, 
                           max_hp: int = None, temp_hp: int = 0):
        """Update character HP in Obsidian"""
        file_path = self.characters_folder / f"{character_name}.md"
        note = ObsidianMarkdown.read_note(file_path)
        
        if not note:
            raise FileNotFoundError(f"Character not found: {character_name}")
        
        # Update metadata
        note['metadata']['hp_current'] = current_hp
        if max_hp is not None:
            note['metadata']['hp_max'] = max_hp
        if temp_hp > 0:
            note['metadata']['hp_temp'] = temp_hp
        note['metadata']['last_updated'] = datetime.now().isoformat()
        
        # Update content (HP line in markdown)
        content_lines = note['content'].split('\n')
        for i, line in enumerate(content_lines):
            if line.startswith('**HP:**'):
                temp_str = f" (+{temp_hp} temp)" if temp_hp > 0 else ""
                content_lines[i] = f"**HP:** {current_hp}/{note['metadata'].get('hp_max', max_hp)}{temp_str}"
                break
        
        ObsidianMarkdown.write_note(file_path, note['metadata'], '\n'.join(content_lines))
    
    def update_character_resources(self, character_name: str, 
                                   resources: Dict[str, Dict[str, int]]):
        """Update character resources (spell slots, rage, etc.)"""
        file_path = self.characters_folder / f"{character_name}.md"
        note = ObsidianMarkdown.read_note(file_path)
        
        if not note:
            raise FileNotFoundError(f"Character not found: {character_name}")
        
        # Update metadata
        if 'resources' not in note['metadata']:
            note['metadata']['resources'] = {}
        
        note['metadata']['resources'].update(resources)
        note['metadata']['last_updated'] = datetime.now().isoformat()
        
        # TODO: Update content (resource lines in markdown)
        
        ObsidianMarkdown.write_note(file_path, note['metadata'], note['content'])
    
    def add_condition(self, character_name: str, condition: str):
        """Add condition to character"""
        file_path = self.characters_folder / f"{character_name}.md"
        note = ObsidianMarkdown.read_note(file_path)
        
        if not note:
            raise FileNotFoundError(f"Character not found: {character_name}")
        
        conditions = note['metadata'].get('conditions', [])
        if condition not in conditions:
            conditions.append(condition)
            note['metadata']['conditions'] = conditions
            note['metadata']['last_updated'] = datetime.now().isoformat()
            
            ObsidianMarkdown.write_note(file_path, note['metadata'], note['content'])
    
    def remove_condition(self, character_name: str, condition: str):
        """Remove condition from character"""
        file_path = self.characters_folder / f"{character_name}.md"
        note = ObsidianMarkdown.read_note(file_path)
        
        if not note:
            raise FileNotFoundError(f"Character not found: {character_name}")
        
        conditions = note['metadata'].get('conditions', [])
        if condition in conditions:
            conditions.remove(condition)
            note['metadata']['conditions'] = conditions
            note['metadata']['last_updated'] = datetime.now().isoformat()
            
            ObsidianMarkdown.write_note(file_path, note['metadata'], note['content'])
    
    def update_character_xp(self, character_name: str, xp: int):
        """Update character XP in Obsidian"""
        file_path = self.characters_folder / f"{character_name}.md"
        note = ObsidianMarkdown.read_note(file_path)
        
        if not note:
            raise FileNotFoundError(f"Character not found: {character_name}")
        
        # Update metadata
        note['metadata']['xp'] = xp
        note['metadata']['last_updated'] = datetime.now().isoformat()
        
        # Update content (XP line in markdown)
        content_lines = note['content'].split('\n')
        level = note['metadata'].get('level', 1)
        
        # XP thresholds
        xp_thresholds = {
            1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000,
            8: 34000, 9: 48000, 10: 64000, 11: 85000, 12: 100000,
            13: 120000, 14: 140000, 15: 165000, 16: 195000, 17: 225000,
            18: 265000, 19: 305000, 20: 355000
        }
        
        next_level_xp = xp_thresholds.get(level + 1, 999999)
        xp_needed = next_level_xp - xp
        
        for i, line in enumerate(content_lines):
            if line.startswith('**XP:**'):
                content_lines[i] = f"**XP:** {xp:,} / {next_level_xp:,}"
                break
        
        for i, line in enumerate(content_lines):
            if line.startswith('**Next Level:**'):
                content_lines[i] = f"**Next Level:** {xp_needed:,} XP needed"
                break
        
        ObsidianMarkdown.write_note(file_path, note['metadata'], '\n'.join(content_lines))
    
    def update_character_currency(self, character_name: str, gp: int = None, 
                                  sp: int = None, cp: int = None, ep: int = None, pp: int = None):
        """Update character currency in Obsidian"""
        file_path = self.characters_folder / f"{character_name}.md"
        note = ObsidianMarkdown.read_note(file_path)
        
        if not note:
            raise FileNotFoundError(f"Character not found: {character_name}")
        
        # Update metadata
        note['metadata']['last_updated'] = datetime.now().isoformat()
        
        # Update content (Currency line in markdown)
        content_lines = note['content'].split('\n')
        
        for i, line in enumerate(content_lines):
            if line.startswith('- **') and 'gp' in line.lower() and '### Currency' in '\n'.join(content_lines[max(0,i-10):i]):
                # Build new currency string
                currency_parts = []
                if gp is not None:
                    currency_parts.append(f"{gp:,} gp")
                if sp is not None:
                    currency_parts.append(f"{sp} sp")
                if ep is not None:
                    currency_parts.append(f"{ep} ep")
                if cp is not None:
                    currency_parts.append(f"{cp} cp")
                if pp is not None:
                    currency_parts.append(f"{pp} pp")
                
                if currency_parts:
                    content_lines[i] = f"- **{', '.join(currency_parts)}**"
                break
        
        ObsidianMarkdown.write_note(file_path, note['metadata'], '\n'.join(content_lines))
    
    def update_character_ac(self, character_name: str, ac: int, ac_note: str = None):
        """Update character AC in Obsidian"""
        file_path = self.characters_folder / f"{character_name}.md"
        note = ObsidianMarkdown.read_note(file_path)
        
        if not note:
            raise FileNotFoundError(f"Character not found: {character_name}")
        
        # Update metadata
        note['metadata']['ac'] = ac
        note['metadata']['last_updated'] = datetime.now().isoformat()
        
        # Update content (AC line in markdown)
        content_lines = note['content'].split('\n')
        
        for i, line in enumerate(content_lines):
            if line.startswith('**AC:**'):
                ac_str = str(ac)
                if ac_note:
                    ac_str += f" ({ac_note})"
                content_lines[i] = f"**AC:** {ac_str}"
                break
        
        ObsidianMarkdown.write_note(file_path, note['metadata'], '\n'.join(content_lines))
    
    def add_inventory_item(self, character_name: str, item_name: str, 
                          quantity: int = 1, item_type: str = None, notes: str = None):
        """Add item to character inventory in Obsidian"""
        file_path = self.characters_folder / f"{character_name}.md"
        note = ObsidianMarkdown.read_note(file_path)
        
        if not note:
            raise FileNotFoundError(f"Character not found: {character_name}")
        
        # Format item line
        item_line = f"- **{item_name}**"
        if quantity > 1:
            item_line += f" (×{quantity})"
        if item_type:
            item_line += f" - {item_type}"
        if notes:
            item_line += f" - {notes}"
        
        # Find or create inventory section
        content_lines = note['content'].split('\n')
        inventory_idx = None
        
        for i, line in enumerate(content_lines):
            if '## Equipment & Inventory' in line or '### Special Items' in line:
                inventory_idx = i
                break
        
        if inventory_idx is None:
            # Create inventory section at end
            content_lines.append("\n## Equipment & Inventory\n")
            content_lines.append(item_line)
        else:
            # Add after inventory header
            content_lines.insert(inventory_idx + 1, item_line)
        
        note['metadata']['last_updated'] = datetime.now().isoformat()
        ObsidianMarkdown.write_note(file_path, note['metadata'], '\n'.join(content_lines))
    
    def remove_inventory_item(self, character_name: str, item_name: str):
        """Remove item from character inventory in Obsidian"""
        file_path = self.characters_folder / f"{character_name}.md"
        note = ObsidianMarkdown.read_note(file_path)
        
        if not note:
            raise FileNotFoundError(f"Character not found: {character_name}")
        
        # Find and remove item line
        content_lines = note['content'].split('\n')
        removed = False
        
        for i, line in enumerate(content_lines):
            if f"**{item_name}**" in line and line.strip().startswith('- **'):
                content_lines.pop(i)
                removed = True
                break
        
        if not removed:
            raise ValueError(f"Item '{item_name}' not found in {character_name}'s inventory")
        
        note['metadata']['last_updated'] = datetime.now().isoformat()
        ObsidianMarkdown.write_note(file_path, note['metadata'], '\n'.join(content_lines))


# ============================================================================
# FILE WATCHER (Real-time sync)
# ============================================================================

class ObsidianWatcher(FileSystemEventHandler):
    """Watch Obsidian vault for changes"""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.last_modified = {}
        self.debounce_time = 2  # seconds
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Debounce: ignore rapid repeated events
        now = datetime.now().timestamp()
        last_time = self.last_modified.get(str(file_path), 0)
        
        if now - last_time < self.debounce_time:
            return
        
        self.last_modified[str(file_path)] = now
        
        logger.info(f"Obsidian file modified: {file_path.name}")
        # TODO: Trigger sync to other systems


# ============================================================================
# MCP TOOLS
# ============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Obsidian sync tools"""
    return [
        Tool(
            name="get_character_data",
            description="Read character data from Obsidian vault",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {
                        "type": "string",
                        "description": "Character name (e.g., 'Eglath Bearkiller')"
                    }
                },
                "required": ["character_name"]
            }
        ),
        Tool(
            name="get_all_characters",
            description="Get all player characters from Obsidian vault",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="update_character_hp",
            description="Update character HP in Obsidian (real-time combat sync)",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "current_hp": {"type": "integer"},
                    "max_hp": {"type": "integer"},
                    "temp_hp": {"type": "integer", "default": 0}
                },
                "required": ["character_name", "current_hp"]
            }
        ),
        Tool(
            name="update_character_resources",
            description="Update character resources (spell slots, rage, ki, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "resources": {
                        "type": "object",
                        "description": "Resource updates as {resource_name: {current: X, max: Y}}"
                    }
                },
                "required": ["character_name", "resources"]
            }
        ),
        Tool(
            name="add_condition",
            description="Add condition to character (Poisoned, Stunned, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "condition": {"type": "string"}
                },
                "required": ["character_name", "condition"]
            }
        ),
        Tool(
            name="remove_condition",
            description="Remove condition from character",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "condition": {"type": "string"}
                },
                "required": ["character_name", "condition"]
            }
        ),
        Tool(
            name="convert_hp_to_status",
            description="Convert enemy HP to descriptive status (for players to see)",
            inputSchema={
                "type": "object",
                "properties": {
                    "current_hp": {"type": "integer"},
                    "max_hp": {"type": "integer"}
                },
                "required": ["current_hp", "max_hp"]
            }
        ),
        Tool(
            name="start_vault_watch",
            description="Start watching Obsidian vault for real-time changes",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="stop_vault_watch",
            description="Stop watching Obsidian vault",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="toggle_rage",
            description="Toggle Barbarian rage on/off (automatically manages rage count)",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "activate": {"type": "boolean", "description": "true to activate rage, false to end rage"}
                },
                "required": ["character_name", "activate"]
            }
        ),
        Tool(
            name="use_spell_slot",
            description="Use a spell slot (checks a box) or recover all slots (long rest)",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "spell_level": {"type": "integer", "description": "Spell level (1-9)"},
                    "long_rest": {"type": "boolean", "default": False, "description": "true to recover all spell slots"}
                },
                "required": ["character_name"]
            }
        ),
        Tool(
            name="update_character_xp",
            description="Update character XP (automatically calculates XP to next level)",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "xp": {"type": "integer", "description": "New total XP value"}
                },
                "required": ["character_name", "xp"]
            }
        ),
        Tool(
            name="update_character_currency",
            description="Update character currency (gp, sp, cp, ep, pp)",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "gp": {"type": "integer"},
                    "sp": {"type": "integer"},
                    "cp": {"type": "integer"},
                    "ep": {"type": "integer"},
                    "pp": {"type": "integer"}
                },
                "required": ["character_name"]
            }
        ),
        Tool(
            name="update_character_ac",
            description="Update character AC (armor class)",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "ac": {"type": "integer", "description": "New AC value"},
                    "ac_note": {"type": "string", "description": "Optional note (e.g., 'Studded Leather +1')"}
                },
                "required": ["character_name", "ac"]
            }
        ),
        Tool(
            name="add_inventory_item",
            description="Add item to character inventory",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "item_name": {"type": "string", "description": "Name of the item"},
                    "quantity": {"type": "integer", "default": 1},
                    "item_type": {"type": "string", "description": "Type of item (weapon, armor, potion, etc.)"},
                    "notes": {"type": "string", "description": "Additional notes about the item"}
                },
                "required": ["character_name", "item_name"]
            }
        ),
        Tool(
            name="remove_inventory_item",
            description="Remove item from character inventory",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "item_name": {"type": "string", "description": "Name of the item to remove"}
                },
                "required": ["character_name", "item_name"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    
    char_manager = CharacterDataManager(OBSIDIAN_VAULT_PATH)
    
    try:
        if name == "get_character_data":
            character = char_manager.get_character(arguments["character_name"])
            if character:
                return [TextContent(type="text", text=json.dumps(character, indent=2))]
            else:
                return [TextContent(type="text", text=json.dumps({
                    "error": f"Character '{arguments['character_name']}' not found"
                }, indent=2))]
        
        elif name == "get_all_characters":
            characters = char_manager.get_all_characters()
            summary = []
            for char in characters:
                meta = char['metadata']
                summary.append({
                    'name': meta.get('name', 'Unknown'),
                    'class': meta.get('class', ''),
                    'level': meta.get('level', 1),
                    'hp_current': meta.get('hp_current', 0),
                    'hp_max': meta.get('hp_max', 0),
                    'conditions': meta.get('conditions', [])
                })
            
            return [TextContent(type="text", text=json.dumps({
                'total_characters': len(characters),
                'characters': summary
            }, indent=2))]
        
        elif name == "update_character_hp":
            char_manager.update_character_hp(
                arguments["character_name"],
                arguments["current_hp"],
                arguments.get("max_hp"),
                arguments.get("temp_hp", 0)
            )
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "message": f"Updated HP for {arguments['character_name']}"
            }, indent=2))]
        
        elif name == "update_character_resources":
            char_manager.update_character_resources(
                arguments["character_name"],
                arguments["resources"]
            )
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "message": f"Updated resources for {arguments['character_name']}"
            }, indent=2))]
        
        elif name == "add_condition":
            char_manager.add_condition(
                arguments["character_name"],
                arguments["condition"]
            )
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "message": f"Added '{arguments['condition']}' to {arguments['character_name']}"
            }, indent=2))]
        
        elif name == "remove_condition":
            char_manager.remove_condition(
                arguments["character_name"],
                arguments["condition"]
            )
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "message": f"Removed '{arguments['condition']}' from {arguments['character_name']}"
            }, indent=2))]
        
        elif name == "convert_hp_to_status":
            status = hp_to_status(arguments["current_hp"], arguments["max_hp"])
            return [TextContent(type="text", text=json.dumps({
                "current_hp": arguments["current_hp"],
                "max_hp": arguments["max_hp"],
                "status": status
            }, indent=2))]
        
        elif name == "start_vault_watch":
            global WATCH_ACTIVE
            global observer
            
            if not WATCHDOG_AVAILABLE:
                return [TextContent(type="text", text=json.dumps({
                    "error": "Watchdog library not installed. Run: pip install watchdog"
                }, indent=2))]
            
            if WATCH_ACTIVE:
                return [TextContent(type="text", text=json.dumps({
                    "message": "Vault watcher already active"
                }, indent=2))]
            
            observer = Observer()
            event_handler = ObsidianWatcher(OBSIDIAN_VAULT_PATH)
            observer.schedule(event_handler, str(OBSIDIAN_VAULT_PATH), recursive=True)
            observer.start()
            WATCH_ACTIVE = True
            
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "message": f"Watching Obsidian vault: {OBSIDIAN_VAULT_PATH}"
            }, indent=2))]
        
        elif name == "stop_vault_watch":
            global WATCH_ACTIVE
            global observer
            
            if not WATCH_ACTIVE or not observer:
                return [TextContent(type="text", text=json.dumps({
                    "message": "Vault watcher not active"
                }, indent=2))]
            
            observer.stop()
            observer.join()
            observer = None
            WATCH_ACTIVE = False
            
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "message": "Stopped watching Obsidian vault"
            }, indent=2))]
        
        elif name == "toggle_rage":
            character_name = arguments["character_name"]
            activate = arguments["activate"]
            
            file_path = OBSIDIAN_VAULT_PATH / "Player Characters" / f"{character_name.replace(' ', '_')}.md"
            note = ObsidianMarkdown.read_note(file_path)
            
            if not note:
                return [TextContent(type="text", text=json.dumps({
                    "error": f"Character '{character_name}' not found"
                }, indent=2))]
            
            # Check if character has rage resource
            resources = note['metadata'].get('resources', {})
            if 'rage' not in str(note['content']).lower():
                return [TextContent(type="text", text=json.dumps({
                    "error": f"{character_name} doesn't have Rage ability"
                }, indent=2))]
            
            current_raging = note['metadata'].get('raging', False)
            
            if activate:
                # Activating rage
                if current_raging:
                    return [TextContent(type="text", text=json.dumps({
                        "message": f"{character_name} is already raging!"
                    }, indent=2))]
                
                # Parse rage uses from content
                content_lines = note['content'].split('\n')
                rage_line_idx = None
                current_rages = 0
                max_rages = 0
                
                for i, line in enumerate(content_lines):
                    if '**Rage:**' in line:
                        rage_line_idx = i
                        # Count filled dots (●) for current uses
                        current_rages = line.count('●')
                        # Count total dots for max
                        max_rages = line.count('●') + line.count('○')
                        break
                
                if current_rages <= 0:
                    return [TextContent(type="text", text=json.dumps({
                        "error": "No rage uses remaining! Take a long rest to recover."
                    }, indent=2))]
                
                # Deduct 1 rage use
                new_rages = current_rages - 1
                used = max_rages - new_rages
                dots = "●" * new_rages + "○" * used
                content_lines[rage_line_idx] = f"**Rage:** {dots} ({new_rages}/{max_rages})"
                
                # Check the rage checkbox
                for i, line in enumerate(content_lines):
                    if '- [ ] **RAGE ACTIVE**' in line:
                        content_lines[i] = line.replace('- [ ]', '- [x]')
                        break
                
                # Update metadata
                note['metadata']['raging'] = True
                note['metadata']['last_updated'] = datetime.now().isoformat()
                
                # Write updated file
                ObsidianMarkdown.write_note(file_path, note['metadata'], '\n'.join(content_lines))
                
                return [TextContent(type="text", text=json.dumps({
                    "success": True,
                    "message": f"{character_name} is now RAGING!",
                    "rage_uses_remaining": new_rages,
                    "reminder": "Use 'Raging' weapon variants (+2 damage, resistance to physical damage)"
                }, indent=2))]
            
            else:
                # Ending rage
                if not current_raging:
                    return [TextContent(type="text", text=json.dumps({
                        "message": f"{character_name} is not currently raging"
                    }, indent=2))]
                
                # Uncheck the rage checkbox
                content_lines = note['content'].split('\n')
                for i, line in enumerate(content_lines):
                    if '- [x] **RAGE ACTIVE**' in line:
                        content_lines[i] = line.replace('- [x]', '- [ ]')
                        break
                
                # Update metadata
                note['metadata']['raging'] = False
                note['metadata']['last_updated'] = datetime.now().isoformat()
                
                # Write updated file
                ObsidianMarkdown.write_note(file_path, note['metadata'], '\n'.join(content_lines))
                
                return [TextContent(type="text", text=json.dumps({
                    "success": True,
                    "message": f"{character_name}'s rage has ended",
                "reminder": "Use normal weapon damage (no +2 rage bonus)"
            }, indent=2))]
        
        elif name == "use_spell_slot":
            character_name = arguments["character_name"]
            long_rest = arguments.get("long_rest", False)
            
            file_path = OBSIDIAN_VAULT_PATH / "Player Characters" / f"{character_name.replace(' ', '_')}.md"
            note = ObsidianMarkdown.read_note(file_path)
            
            if not note:
                return [TextContent(type="text", text=json.dumps({
                    "error": f"Character '{character_name}' not found"
                }, indent=2))]
            
            content_lines = note['content'].split('\n')
            
            if long_rest:
                # Long rest: uncheck all spell slot boxes
                for i, line in enumerate(content_lines):
                    if '- [x] Slot' in line:
                        content_lines[i] = line.replace('- [x]', '- [ ]')
                
                note['metadata']['last_updated'] = datetime.now().isoformat()
                ObsidianMarkdown.write_note(file_path, note['metadata'], '\n'.join(content_lines))
                
                return [TextContent(type="text", text=json.dumps({
                    "success": True,
                    "message": f"{character_name} took a long rest - all spell slots recovered!"
                }, indent=2))]
            
            else:
                # Use a spell slot
                spell_level = arguments.get("spell_level")
                if not spell_level:
                    return [TextContent(type="text", text=json.dumps({
                        "error": "Must specify spell_level (1-9) or use long_rest=true"
                    }, indent=2))]
                
                # Find the first unchecked slot for this level
                in_level_section = False
                slot_used = False
                slots_remaining = 0
                total_slots = 0
                
                for i, line in enumerate(content_lines):
                    if f'### Level {spell_level}' in line:
                        in_level_section = True
                        # Extract total slots from heading
                        if '(' in line and 'slots)' in line:
                            total_slots = int(line.split('(')[1].split(' ')[0])
                        continue
                    
                    if in_level_section:
                        if line.startswith('###'):  # Next section
                            break
                        
                        if '- [ ] Slot' in line and not slot_used:
                            # Use this slot
                            content_lines[i] = line.replace('- [ ]', '- [x]')
                            slot_used = True
                        
                        # Count remaining unchecked slots
                        if '- [ ] Slot' in line:
                            slots_remaining += 1
                
                if not slot_used:
                    return [TextContent(type="text", text=json.dumps({
                        "error": f"No level {spell_level} spell slots remaining!"
                    }, indent=2))]
                
                # Adjust count (we just used one)
                slots_remaining -= 1
                
                note['metadata']['last_updated'] = datetime.now().isoformat()
                ObsidianMarkdown.write_note(file_path, note['metadata'], '\n'.join(content_lines))
                
                return [TextContent(type="text", text=json.dumps({
                    "success": True,
                    "message": f"{character_name} used a level {spell_level} spell slot",
                    "slots_remaining": slots_remaining,
                    "total_slots": total_slots
                }, indent=2))]
        
        elif name == "update_character_xp":
            char_manager.update_character_xp(
                arguments["character_name"],
                arguments["xp"]
            )
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "message": f"Updated XP for {arguments['character_name']} to {arguments['xp']:,}"
            }, indent=2))]
        
        elif name == "update_character_currency":
            char_manager.update_character_currency(
                arguments["character_name"],
                arguments.get("gp"),
                arguments.get("sp"),
                arguments.get("cp"),
                arguments.get("ep"),
                arguments.get("pp")
            )
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "message": f"Updated currency for {arguments['character_name']}"
            }, indent=2))]
        
        elif name == "update_character_ac":
            char_manager.update_character_ac(
                arguments["character_name"],
                arguments["ac"],
                arguments.get("ac_note")
            )
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "message": f"Updated AC for {arguments['character_name']} to {arguments['ac']}"
            }, indent=2))]
        
        elif name == "add_inventory_item":
            char_manager.add_inventory_item(
                arguments["character_name"],
                arguments["item_name"],
                arguments.get("quantity", 1),
                arguments.get("item_type"),
                arguments.get("notes")
            )
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "message": f"Added {arguments['item_name']} to {arguments['character_name']}'s inventory"
            }, indent=2))]
        
        elif name == "remove_inventory_item":
            char_manager.remove_inventory_item(
                arguments["character_name"],
                arguments["item_name"]
            )
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "message": f"Removed {arguments['item_name']} from {arguments['character_name']}'s inventory"
            }, indent=2))]
        
        else:
            return [TextContent(type="text", text=json.dumps({
                "error": f"Unknown tool: {name}"
            }, indent=2))]
    
    except Exception as e:
        logger.error(f"Error in {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=json.dumps({
            "error": str(e)
        }, indent=2))]


async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

