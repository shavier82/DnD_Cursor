# Combat Engine MCP - Configuration

## Add to .cursor/mcp.json

Add this server configuration to your `.cursor/mcp.json` file:

```json
"combat-engine": {
  "command": "C:\\Users\\ksist\\AppData\\Local\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\\python.exe",
  "args": ["combat_server.py"],
  "cwd": "C:\\DnD\\DnD_Cursor\\mcp_servers\\combat_engine"
}
```

## Install Dependencies

Before using, install required packages:

```powershell
cd "C:\DnD\DnD_Cursor\mcp_servers\combat_engine"
pip install -r requirements.txt
```

## Reload Cursor

After adding to mcp.json:
1. Press `Ctrl+Shift+P`
2. Type "Developer: Reload Window"
3. Cursor will reconnect with the new combat-engine MCP server

## Verify Installation

After reload, check MCP servers panel for:
- ✅ combat-engine

## Available Tools

The combat-engine MCP provides 9 core tools (pattern established for 25 total):

1. `start_combat` - Initialize combat with characters and monsters
2. `roll_initiative_tool` - Roll and sort initiative
3. `load_battlefield` - Set up terrain and obstacles
4. `next_turn_tool` - Advance to next turn
5. `get_combat_status` - Get full combat state
6. `attack_tool` - Process attacks
7. `move_creature` - Move creatures on battlefield
8. `get_ai_action` - Get AI-decided actions for enemies
9. `end_combat_tool` - End combat and sync to Google Sheets

Additional tools follow the same pattern (spell casting, condition management, distance checks, AoE calculations, etc.)




