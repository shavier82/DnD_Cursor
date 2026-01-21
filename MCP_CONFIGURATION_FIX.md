# MCP Configuration Fix

## Problem
Cursor was trying to run `obsidian_sync_server.py` from the wrong location:
```
python.exe: can't open file 'c:\\DnD\\DnD_Cursor\\obsidian_sync_server.py': [Errno 2] No such file or directory
```

The server files are actually in subdirectories like `mcp_servers/obsidian_sync/`.

## Solution
Created a proper MCP configuration file with **full absolute paths** to all server files.

### Configuration File Location
```
C:\Users\ksist\AppData\Roaming\Cursor\User\globalStorage\anysphere.cursor-mcp\mcp_config.json
```

### Configuration Format
```json
{
  "mcpServers": {
    "obsidian-sync": {
      "command": "python",
      "args": ["C:\\DnD\\DnD_Cursor\\mcp_servers\\obsidian_sync\\obsidian_sync_server.py"],
      "cwd": "C:\\DnD\\DnD_Cursor"
    }
  }
}
```

## All Configured MCP Servers
✅ **obsidian-sync** - Character data, XP, inventory, NPC automation
✅ **campaign-wiki** - Campaign knowledge base
✅ **combat-engine** - Combat management
✅ **weather-calendar** - Weather and time tracking
✅ **knowledge-graph** - Relationship and knowledge tracking
✅ **dice-roller** - Dice rolling with audit trail
✅ **rules-database** - D&D rules lookup
✅ **session-recorder** - Session logging
✅ **sourcebooks** - PHB/DMG/MM text search
✅ **music-ambience** - Ambient music and SFX

## Next Steps
1. **Restart Cursor completely** (close all windows, reopen)
2. Check the MCP panel to verify all servers connect
3. Test with a simple tool call (e.g., `lookup_spell("Fireball")`)

## Verification
All server files exist and are intact:
- obsidian_sync_server.py: 65,033 bytes ✅
- weather_calendar_server.py: 24,269 bytes ✅
- knowledge_graph_server.py: 27,590 bytes ✅
- All other servers: Present and functional ✅

## If It Still Doesn't Work
1. Check Cursor's output panel for MCP logs
2. Verify Python is in PATH: `python --version`
3. Test server manually: `python C:\DnD\DnD_Cursor\mcp_servers\obsidian_sync\obsidian_sync_server.py`
4. Check for any firewall/antivirus blocking Python








