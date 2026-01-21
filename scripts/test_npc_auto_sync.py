"""Test NPC auto-sync functionality"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "mcp_servers" / "campaign_wiki"))

from models.campaign_wiki import CampaignWiki
from models.npc import NPCRelationship, RelationshipType
from utils.obsidian_sync import ObsidianSync

# Load wiki
wiki = CampaignWiki.load("C:/DnD/Campaigns/Phandelver/wiki/campaign_wiki.json")

# Find NPCs by name
test_npc_id = None
vrek_id = None
for npc_id, npc in wiki.npcs.items():
    if npc.name == "Test NPC Auto-Sync":
        test_npc_id = npc_id
    if npc.name == "Vrek Snapjaw":
        vrek_id = npc_id

if test_npc_id and vrek_id:
    # Add relationship
    rel = NPCRelationship(
        from_entity=test_npc_id,
        to_entity=vrek_id,
        relationship_type=RelationshipType.PROFESSIONAL,
        description="Test relationship for auto-sync",
        strength=5
    )
    wiki.relationships.append(rel)
    wiki.save()
    
    # Sync both NPCs
    sync = ObsidianSync(wiki.obsidian_vault)
    wiki_dict = wiki.model_dump()
    
    test_npc = wiki.npcs[test_npc_id]
    vrek = wiki.npcs[vrek_id]
    
    sync.export_npc(test_npc.model_dump(), wiki_dict)
    sync.export_npc(vrek.model_dump(), wiki_dict)
    
    print("SUCCESS: Relationship added and both NPCs synced to Obsidian!")
    print(f"   Test NPC: {test_npc.name}")
    print(f"   Vrek Snapjaw: {vrek.name}")
else:
    print(f"ERROR: Could not find NPCs. Test NPC ID: {test_npc_id}, Vrek ID: {vrek_id}")
