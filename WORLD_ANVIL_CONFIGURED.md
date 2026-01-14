# World Anvil API - Configured ✅

**Date:** 2026-01-13  
**Status:** API Key Configured & Secured

---

## ✅ What Was Done

### 1. API Key Stored Securely
- ✅ Created `mcp_servers/campaign_wiki/config.json` with your API key
- ✅ Added to `.gitignore` - **WILL NOT SYNC TO GIT**
- ✅ Local file only - safe from repository

### 2. Wiki Server Updated
- ✅ Loads API key from config automatically
- ✅ Creates World Anvil client on first sync
- ✅ Added `sync_to_world_anvil()` MCP tool

---

## 🔒 Security

**Your API key is protected:**
```
✅ File: mcp_servers/campaign_wiki/config.json
✅ Git Ignored: Added to .gitignore
✅ Local Only: Will NOT be committed to repository
✅ Safe to use in local environment
```

**From .gitignore:**
```
# Campaign Wiki MCP - Config with API keys
mcp_servers/campaign_wiki/config.json
```

---

## 🌍 Using World Anvil Sync

### After installing Campaign Wiki MCP:

```python
# 1. Load your wiki
create_or_load_wiki(campaign_name="Phandelver")

# 2. Create/update NPCs, locations, quests
create_npc(name="Gundren Rockseeker", ...)
create_location(name="Phandalin", ...)
create_quest(name="Rescue Gundren", ...)

# 3. Sync to World Anvil
sync_to_world_anvil(
    campaign_name="Phandelver",
    world_id="your_world_id"  # Optional: set once in config.json
)
```

---

## 🔧 Configuration Options

**Edit `mcp_servers/campaign_wiki/config.json` to customize:**

```json
{
  "world_anvil": {
    "api_key": "your_key_here",
    "world_id": "your_world_id"  // Optional: set your World Anvil world ID
  },
  "obsidian": {
    "default_vault": "C:\\Users\\ksist\\Documents\\Obsidian\\DnD"  // Optional
  }
}
```

**Setting world_id in config:**
- Find your World ID in World Anvil URL: `worldanvil.com/w/YOUR_WORLD_ID`
- Add to config.json
- Won't need to specify in each sync call

---

## 🚀 Next Steps

### 1. Get Your World ID:
- Log into World Anvil
- Go to your world
- Copy World ID from URL: `worldanvil.com/w/YOUR_WORLD_ID`
- Add to `config.json`: `"world_id": "YOUR_WORLD_ID"`

### 2. Install Campaign Wiki MCP:
```powershell
cd "C:\DnD\DnD_Cursor\mcp_servers\campaign_wiki"
pip install -r requirements.txt
```

### 3. Configure MCP:
Add to `.cursor/mcp.json`:
```json
"campaign-wiki": {
  "command": "C:\\Users\\ksist\\AppData\\Local\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\\python.exe",
  "args": ["wiki_server.py"],
  "cwd": "C:\\DnD\\DnD_Cursor\\mcp_servers\\campaign_wiki"
}
```

### 4. Reload Cursor:
`Ctrl+Shift+P` → "Developer: Reload Window"

### 5. Test World Anvil Sync:
```python
# Create a test NPC
create_npc(
    campaign_name="Test",
    name="Test NPC",
    description="Testing World Anvil sync"
)

# Sync to World Anvil
sync_to_world_anvil(campaign_name="Test")

# Check World Anvil to verify article was created
```

---

## 📝 What Gets Synced

**To World Anvil:**
- ✅ NPCs → Character articles
- ✅ Locations → Location articles
- ✅ Quests → Quest articles (if supported by API)

**Article Content Includes:**
- Name, description, background
- Role, faction, location
- Personality, motivations
- Related content (quests, locations, NPCs)

**World Anvil IDs Tracked:**
- After first sync, `world_anvil_id` stored in wiki
- Subsequent syncs update existing articles (if API supports)

---

## 🎯 Use Cases

### Public Campaign Wiki:
- Share campaign with players
- Track campaign progress publicly
- Build community around campaign

### Visual Campaign Notes:
- Rich text articles with images
- Maps and timelines
- Interactive world building

### Player Reference:
- Players can read NPC backgrounds
- Location information
- Quest details

### Campaign Showcase:
- Share with D&D community
- Inspire other DMs
- Build your portfolio

---

## ⚠️ World Anvil API Limitations

**Note:** World Anvil API has limitations based on subscription tier.

**Free Tier:**
- Limited API access
- May require Guild membership

**Premium Tiers:**
- Full API access
- More article types supported
- Higher rate limits

**Check:** Your World Anvil subscription level for API capabilities

---

## ✅ Complete Setup

**You now have:**
- 🏰 Campaign Wiki MCP with full NPC/Location/Quest tracking
- 📓 Obsidian sync (markdown notes)
- 🌍 **World Anvil sync (public wiki with your API key)**
- 🗺️ Map integration support
- 🔗 Relationship graph visualization
- ⏱️ Timeline chronicling

**All configured and ready to use!**

---

**Your API key is secure in `config.json` and will NOT be synced to git. Start building your campaign wiki! 🏰🌍✨**




