# How to Enable Custom MCP Servers in Cursor

**Problem:** The Obsidian Sync MCP (and other custom MCPs) are not accessible as tools because they're not configured in Cursor.

**Solution:** Configure Cursor to connect to your custom MCP servers.

---

## Option 1: Configure via Cursor Settings (RECOMMENDED)

1. **Open Cursor Settings**
   - Press `Ctrl+,` (Windows/Linux) or `Cmd+,` (Mac)
   - Or: Click gear icon → Settings

2. **Navigate to MCP Settings**
   - Search for "MCP" in settings
   - Or look for "Model Context Protocol" section

3. **Add MCP Server Configuration**
   - Look for "MCP Servers" or "Model Context Protocol Servers"
   - Click "Edit in settings.json" or "Add Server"

4. **Paste This Configuration:**

```json
{
  "mcp.servers": {
    "obsidian-sync": {
      "command": "python",
      "args": ["-m", "mcp_servers.obsidian_sync.obsidian_sync_server"],
      "cwd": "C:\\DnD\\DnD_Cursor",
      "env": {
        "PYTHONPATH": "C:\\DnD\\DnD_Cursor"
      }
    },
    "campaign-wiki": {
      "command": "python",
      "args": ["-m", "mcp_servers.campaign_wiki.wiki_server"],
      "cwd": "C:\\DnD\\DnD_Cursor",
      "env": {
        "PYTHONPATH": "C:\\DnD\\DnD_Cursor"
      }
    },
    "combat-engine": {
      "command": "python",
      "args": ["-m", "mcp_servers.combat_engine.combat_server"],
      "cwd": "C:\\DnD\\DnD_Cursor",
      "env": {
        "PYTHONPATH": "C:\\DnD\\DnD_Cursor"
      }
    },
    "weather-calendar": {
      "command": "python",
      "args": ["-m", "mcp_servers.weather_calendar.weather_calendar_server"],
      "cwd": "C:\\DnD\\DnD_Cursor",
      "env": {
        "PYTHONPATH": "C:\\DnD\\DnD_Cursor"
      }
    },
    "knowledge-graph": {
      "command": "python",
      "args": ["-m", "mcp_servers.knowledge_graph.knowledge_graph_server"],
      "cwd": "C:\\DnD\\DnD_Cursor",
      "env": {
        "PYTHONPATH": "C:\\DnD\\DnD_Cursor"
      }
    }
  }
}
```

5. **Restart Cursor**
   - Close and reopen Cursor
   - Or: `Ctrl+Shift+P` → "Reload Window"

---

## Option 2: Manually Place Config File

If Cursor doesn't have an MCP settings UI, you can manually create the config:

**Location:** `%APPDATA%\Cursor\User\globalStorage\rooveterinaryinc.roo-cline\settings\cline_mcp_settings.json`

**Full Path:** `C:\Users\ksist\AppData\Roaming\Cursor\User\globalStorage\rooveterinaryinc.roo-cline\settings\cline_mcp_settings.json`

**Steps:**
1. Create the directories if they don't exist
2. Copy `cursor_mcp_config.json` to that location
3. Rename it to `cline_mcp_settings.json`
4. Restart Cursor

---

## Option 3: Use Cursor's MCP Config File (Alternative Location)

Some versions of Cursor use a different location:

**Location:** `%APPDATA%\Cursor\User\settings.json`

Add the MCP configuration to your existing `settings.json`:

```json
{
  "...": "... your existing settings ...",
  
  "mcp.servers": {
    "obsidian-sync": {
      "command": "python",
      "args": ["-m", "mcp_servers.obsidian_sync.obsidian_sync_server"],
      "cwd": "C:\\DnD\\DnD_Cursor",
      "env": {
        "PYTHONPATH": "C:\\DnD\\DnD_Cursor"
      }
    }
    // ... add other servers ...
  }
}
```

---

## Verify It's Working

After configuration and restart:

1. **Check Available Tools**
   - Ask me: "What MCP tools do you have access to?"
   - I should list: `obsidian_sync_create_npc`, `obsidian_sync_update_npc_knowledge`, etc.

2. **Test create_npc**
   - I should be able to call it directly
   - No need for Python workarounds

---

## Troubleshooting

### "MCP server failed to start"
- Check Python is in your PATH
- Verify `mcp_servers/obsidian_sync/obsidian_sync_server.py` exists
- Check dependencies: `pip install -r mcp_servers/obsidian_sync/requirements.txt`

### "Tool not found"
- MCP server might not be running
- Check Cursor's output panel for errors
- Try restarting Cursor

### "Cannot find module"
- Verify `PYTHONPATH` is set correctly in config
- Check `cwd` path points to `C:\DnD\DnD_Cursor`

---

## Expected Result

Once configured, I'll have access to these tools:

### Obsidian Sync MCP (7 tools)
- `create_npc`
- `update_npc_knowledge`
- `log_npc_interaction`
- `update_npc_disposition`
- `update_faction_reputation`
- `propagate_consequence`
- `get_npc_data`

### Campaign Wiki MCP
- `create_npc` (campaign wiki version)
- `add_relationship`
- `create_quest`
- `sync_to_obsidian`

### Combat Engine MCP
- `start_combat`
- `attack_tool`
- `end_turn`
- `end_combat`

### Weather/Calendar MCP
- `get_current_date_time`
- `advance_time`
- `long_rest`
- `get_weather`

### Knowledge Graph MCP
- `add_entity`
- `add_relationship`
- `find_connection_path`
- `analyze_consequence_chain`

---

**Once this is set up, I'll be able to call `create_npc()` directly during the campaign!** 🎉










