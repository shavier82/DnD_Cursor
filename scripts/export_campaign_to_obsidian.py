"""Export entire Phandelver campaign to Obsidian vault

This script:
1. Reads CURRENT_STATE.json and CAMPAIGN_EVENTS.json
2. Extracts all NPCs, locations, quests, events
3. Creates Campaign Wiki entries
4. Exports everything to Obsidian vault as markdown files
"""

import json
import sys
import io
from pathlib import Path
from datetime import datetime
import uuid

# Fix console encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add campaign_wiki to path
sys.path.insert(0, str(Path(__file__).parent.parent / "mcp_servers" / "campaign_wiki"))

from models.campaign_wiki import CampaignWiki
from models.npc import NPC, NPCRole, NPCRelationship, RelationshipType
from models.location import Location, LocationType
from models.quest import Quest, QuestStatus, QuestType
from models.timeline import TimelineEvent, EventType
from models.player_character import PlayerCharacter, HitPoints, Currency, SpellSlots, ClassResource, InventoryItem, AbilityScores
from utils.obsidian_sync import ObsidianSync
from utils.sheets_reader import SheetsReader

# Paths
CAMPAIGN_PATH = Path("C:/DnD/Campaigns/Phandelver")
CURRENT_STATE_PATH = CAMPAIGN_PATH / "saves" / "CURRENT_STATE.json"
CAMPAIGN_EVENTS_PATH = CAMPAIGN_PATH / "saves" / "CAMPAIGN_EVENTS.json"
WIKI_DATA_PATH = CAMPAIGN_PATH / "wiki" / "campaign_wiki.json"

print("=" * 80)
print("PHANDELVER CAMPAIGN -> OBSIDIAN EXPORT")
print("=" * 80)
print()

# Use default Obsidian vault path
obsidian_vault = Path("C:/Users/ksist/Documents/Obsidian/DnD")

print(f"Enter your Obsidian vault path (or press Enter for default):")
print(f"Default: {obsidian_vault}")

# Try to get user input, fallback to default if non-interactive
try:
    user_path = input("Obsidian Vault Path: ").strip()
    if user_path:
        obsidian_vault = Path(user_path)
except (EOFError, KeyboardInterrupt):
    print("Using default path (non-interactive mode)")

# Create vault directory if it doesn't exist
obsidian_vault.mkdir(parents=True, exist_ok=True)

print(f"\nUsing Obsidian vault: {obsidian_vault}")
print()

# Load campaign data
print("Loading campaign data...")
with open(CURRENT_STATE_PATH, 'r', encoding='utf-8') as f:
    current_state = json.load(f)

with open(CAMPAIGN_EVENTS_PATH, 'r', encoding='utf-8') as f:
    campaign_events = json.load(f)

print(f"✓ Loaded {len(campaign_events.get('events', []))} campaign events")
print()

# Create Campaign Wiki
print("Creating Campaign Wiki...")
wiki = CampaignWiki(
    campaign_name="Phandelver",
    data_path=str(WIKI_DATA_PATH),
    obsidian_vault=str(obsidian_vault),
)

# Load Player Characters from Google Sheets
print("\nLoading Player Characters from Google Sheets...")
try:
    sheets_config_path = Path("C:/DnD/DnD_Cursor/config/sheets_config.json")
    if sheets_config_path.exists():
        with open(sheets_config_path, 'r') as f:
            sheets_config = json.load(f)
        
        credentials_path = sheets_config.get('credentials_path', 'C:\\DnD\\keys\\google_sheets_key.json')
        spreadsheet_id = sheets_config.get('spreadsheet_id')
        
        if Path(credentials_path).exists() and spreadsheet_id:
            reader = SheetsReader(credentials_path, spreadsheet_id)
            pc_data_list = reader.read_characters()
            
            pc_count = 0
            for pc_data in pc_data_list:
                pc_id = pc_data.get('character_id', str(uuid.uuid4()))
                
                # Create PlayerCharacter object
                pc = PlayerCharacter(
                    character_id=pc_id,
                    name=pc_data['name'],
                    char_class=pc_data.get('char_class', 'Unknown'),
                    level=pc_data.get('level', 1),
                    ac=pc_data.get('ac', 10),
                    hp=HitPoints(**pc_data.get('hp', {'current': 0, 'maximum': 0})),
                    xp=pc_data.get('xp', 0),
                    currency=Currency(**pc_data.get('currency', {})),
                    ability_scores=AbilityScores(),  # Default values, not in sheets currently
                    spell_slots=[SpellSlots(**slot) for slot in pc_data.get('spell_slots', [])],
                    class_resources=[ClassResource(**res) for res in pc_data.get('class_resources', [])],
                    inventory=[InventoryItem(**item) for item in pc_data.get('inventory', [])],
                    notes=pc_data.get('notes', ''),
                    last_synced=pc_data.get('last_synced'),
                )
                
                wiki.player_characters[pc_id] = pc
                pc_count += 1
                print(f"  + {pc.name} (Level {pc.level} {pc.char_class}) - HP: {pc.hp.current}/{pc.hp.maximum}, AC: {pc.ac}")
            
            print(f"✓ Loaded {pc_count} player characters from Google Sheets")
        else:
            print("! Google Sheets not configured - skipping PC import")
            print(f"  Credentials: {credentials_path} (exists: {Path(credentials_path).exists()})")
            print(f"  Spreadsheet ID: {spreadsheet_id}")
    else:
        print("! sheets_config.json not found - skipping PC import")
except Exception as e:
    print(f"! Error loading PCs from Google Sheets: {e}")
    print("! Continuing without PC data...")
print()

# Extract NPCs
print("\nExtracting NPCs...")
npc_count = 0

# Known NPCs from the campaign
known_npcs = {
    "Gundren Rockseeker": {
        "role": "quest_giver",
        "description": "Dwarf prospector who hired the party",
        "faction": "Rockseeker Brothers",
        "location": "Phandalin",
        "status": "alive",
    },
    "Sildar Hallwinter": {
        "role": "ally",
        "description": "Human warrior of the Lords' Alliance",
        "faction": "Lords' Alliance",
        "location": "Phandalin",
        "status": "alive",
    },
    "Mirna Dendrar": {
        "role": "quest_giver",
        "description": "Grateful widow rescued from the Redbrand Hideout",
        "faction": "Phandalin Townsfolk",
        "location": "Phandalin",
        "status": "alive",
    },
    "Iarno 'Glasstaff' Albrek": {
        "role": "enemy",
        "description": "Traitorous wizard and leader of the Redbrands",
        "faction": "Redbrands",
        "location": "Redbrand Hideout",
        "status": "deceased",
    },
    "Nezznar the Black Spider": {
        "role": "enemy",
        "description": "Drow villain seeking the Forge of Spells",
        "faction": "Black Spider Network",
        "location": "Wave Echo Cave",
        "status": "alive",
    },
    "Tharden Rockseeker": {
        "role": "neutral",
        "description": "Gundren's brother, murdered by the Black Spider",
        "faction": "Rockseeker Brothers",
        "location": "Wave Echo Cave",
        "status": "deceased",
    },
    "Nundro Rockseeker": {
        "role": "neutral",
        "description": "Gundren's brother, held captive by the Black Spider",
        "faction": "Rockseeker Brothers",
        "location": "Wave Echo Cave",
        "status": "alive",
    },
    "Venomfang": {
        "role": "enemy",
        "description": "Young green dragon lairng in Thundertree",
        "faction": "None",
        "location": "Thundertree",
        "status": "defeated",
    },
}

for npc_name, npc_data in known_npcs.items():
    npc_id = str(uuid.uuid4())
    npc = NPC(
        npc_id=npc_id,
        name=npc_name,
        role=NPCRole(npc_data["role"]),
        description=npc_data.get("description", ""),
        faction=npc_data.get("faction"),
        location=npc_data.get("location"),
        status=npc_data.get("status", "unknown"),
    )
    wiki.npcs[npc_id] = npc
    npc_count += 1
    print(f"  + {npc_name} ({npc_data['role']})")

print(f"✓ Created {npc_count} NPCs")

# Extract Locations
print("\nExtracting Locations...")
locations_data = {
    "Phandalin": {
        "type": "town",
        "description": "A frontier town on the Triboar Trail, population ~500",
        "region": "Sword Coast",
        "notes": ["Quest hub", "Multiple shops and taverns"],
    },
    "Thundertree": {
        "type": "ruins",
        "description": "Ruined village destroyed by eruption of Mount Hotenow",
        "region": "Neverwinter Wood",
        "notes": ["Dragon's lair (Venomfang)"],
    },
    "Wave Echo Cave": {
        "type": "dungeon",
        "description": "Ancient dwarven mine containing the Forge of Spells",
        "region": "Mountains east of Phandalin",
        "notes": ["Final dungeon", "Black Spider's goal"],
    },
    "Cragmaw Castle": {
        "type": "castle",
        "description": "Ruined castle occupied by goblins",
        "region": "Neverwinter Wood",
        "notes": ["Gundren held captive here"],
    },
    "Redbrand Hideout": {
        "type": "dungeon",
        "description": "Secret hideout beneath Tresendar Manor in Phandalin",
        "region": "Phandalin",
        "notes": ["Glasstaff's base", "Cleared by party"],
    },
}

location_count = 0
for loc_name, loc_data in locations_data.items():
    loc_id = str(uuid.uuid4())
    location = Location(
        location_id=loc_id,
        name=loc_name,
        location_type=LocationType(loc_data["type"]),
        description=loc_data.get("description", ""),
        region=loc_data.get("region"),
        notes=loc_data.get("notes", []),
    )
    wiki.locations[loc_id] = location
    location_count += 1
    print(f"  + {loc_name} ({loc_data['type']})")

print(f"✓ Created {location_count} locations")

# Extract Quests
print("\nExtracting Quests...")
quests_data = {
    "Rescue Gundren Rockseeker": {
        "type": "main",
        "status": "completed",
        "description": "Rescue Gundren from Cragmaw Castle",
        "reward": "Payment and gratitude",
    },
    "Find Wave Echo Cave": {
        "type": "main",
        "status": "completed",
        "description": "Locate the legendary Wave Echo Cave",
        "reward": "Share of the mine's profits",
    },
    "Defeat the Black Spider": {
        "type": "main",
        "status": "in_progress",
        "description": "Stop Nezznar from claiming the Forge of Spells",
        "reward": "Unknown",
    },
    "Mirna's Necklace": {
        "type": "side",
        "status": "completed",
        "description": "Retrieve Mirna's family heirloom from Thundertree",
        "reward": "Emerald necklace",
    },
    "Clear the Redbrand Hideout": {
        "type": "side",
        "status": "completed",
        "description": "Eliminate the Redbrand threat in Phandalin",
        "reward": "Town gratitude and treasure",
    },
}

quest_count = 0
for quest_name, quest_data in quests_data.items():
    quest_id = str(uuid.uuid4())
    quest = Quest(
        quest_id=quest_id,
        name=quest_name,
        description=quest_data["description"],
        quest_type=QuestType(quest_data["type"]),
        status=QuestStatus(quest_data["status"]),
        reward=quest_data.get("reward"),
    )
    wiki.quests[quest_id] = quest
    quest_count += 1
    print(f"  + {quest_name} ({quest_data['status']})")

print(f"✓ Created {quest_count} quests")

# Extract Timeline Events from CAMPAIGN_EVENTS.json
print("\nExtracting Timeline Events...")
timeline_count = 0

for event_data in campaign_events.get("events", []):
    event_id = str(uuid.uuid4())
    
    # Parse timestamp
    timestamp_str = event_data.get("timestamp", "")
    try:
        # Handle different timestamp formats
        if '.' in timestamp_str:
            timestamp_str = timestamp_str.split('.')[0]  # Remove fractional seconds
        event_date = datetime.fromisoformat(timestamp_str)
    except:
        event_date = datetime.now()
    
    # Map event type to valid EventType enum
    event_type_str = event_data.get("event_type", "other").lower()
    if "combat" in event_type_str:
        event_type = EventType.COMBAT
    elif "quest" in event_type_str or "complete" in event_type_str:
        event_type = EventType.QUEST_COMPLETE
    elif "discover" in event_type_str or "found" in event_type_str:
        event_type = EventType.DISCOVERY
    elif "npc" in event_type_str or "met" in event_type_str:
        event_type = EventType.NPC_MET
    elif "choice" in event_type_str:
        event_type = EventType.CHOICE
    elif "consequence" in event_type_str:
        event_type = EventType.CONSEQUENCE
    else:
        event_type = EventType.STORY_MILESTONE
    
    event = TimelineEvent(
        event_id=event_id,
        real_date=event_date,
        title=event_data.get("event_type", "Unknown Event"),
        description=event_data.get("description", ""),
        event_type=event_type,
        participants=event_data.get("participants", []),
        location=event_data.get("location"),
    )
    
    wiki.timeline.append(event)
    timeline_count += 1

print(f"✓ Created {timeline_count} timeline events")

# Add Relationships
print("\nAdding Relationships...")
relationships = [
    ("Gundren Rockseeker", "Tharden Rockseeker", "family", "Brothers"),
    ("Gundren Rockseeker", "Nundro Rockseeker", "family", "Brothers"),
    ("Gundren Rockseeker", "Sildar Hallwinter", "friend", "Travel companions"),
    ("Nezznar the Black Spider", "Tharden Rockseeker", "enemy", "Murdered him"),
    ("Nezznar the Black Spider", "Nundro Rockseeker", "enemy", "Holds him captive"),
    ("Iarno 'Glasstaff' Albrek", "Sildar Hallwinter", "enemy", "Former friends turned enemies"),
    ("Mirna Dendrar", "Iarno 'Glasstaff' Albrek", "enemy", "Imprisoned by Redbrands"),
    ("Gundren Rockseeker", "Nezznar the Black Spider", "enemy", "Kidnapped by his agents"),
]

relationship_count = 0
for from_name, to_name, rel_type, description in relationships:
    # Find NPC IDs
    from_id = None
    to_id = None
    
    for npc_id, npc in wiki.npcs.items():
        if npc.name == from_name:
            from_id = npc_id
        if npc.name == to_name:
            to_id = npc_id
    
    if from_id and to_id:
        rel = NPCRelationship(
            from_entity=from_id,
            to_entity=to_id,
            relationship_type=RelationshipType(rel_type),
            description=description,
            strength=5,
        )
        wiki.relationships.append(rel)
        relationship_count += 1
        print(f"  + {from_name} -> {to_name} ({rel_type})")

print(f"✓ Created {relationship_count} relationships")

# Save Campaign Wiki
print("\nSaving Campaign Wiki...")
WIKI_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
wiki.save()
print(f"✓ Saved to {WIKI_DATA_PATH}")

# Export to Obsidian
print("\nExporting to Obsidian...")
obsidian_sync = ObsidianSync(str(obsidian_vault))
obsidian_sync.sync_all(wiki.model_dump())

print(f"\n✓ Exported to Obsidian vault: {obsidian_vault}")
print()

# Summary
print("=" * 80)
print("EXPORT COMPLETE!")
print("=" * 80)
print(f"""
Campaign Wiki created with:
  • {len(wiki.player_characters)} Player Characters (from Google Sheets!)
  • {npc_count} NPCs
  • {location_count} Locations
  • {quest_count} Quests
  • {timeline_count} Timeline Events
  • {relationship_count} Relationships

Obsidian Vault: {obsidian_vault}

Next Steps:
1. Open Obsidian
2. Open the vault at: {obsidian_vault}
3. Explore your campaign wiki!

Vault Structure:
  📁 Player Characters/  ← Your PCs with full character sheets!
  📁 NPCs/               ← Campaign NPCs
  📁 Locations/          ← Phandalin, Wave Echo Cave, etc.
  📁 Quests/             ← Active and completed quests

Features in Obsidian:
  • Graph View (see all relationships)
  • Search across all notes
  • Link between PCs, NPCs, locations, quests
  • Full character sheets (HP, XP, inventory, currency)
  • Markdown editing
  • Free forever!
""")

