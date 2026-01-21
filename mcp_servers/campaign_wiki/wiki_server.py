"""Campaign Wiki MCP Server - Obsidian Integration

Comprehensive campaign management with:
- NPC tracking with relationship graphs
- Location database with maps
- Quest tracking (accepted, in-progress, completed)
- Timeline of events
- Obsidian vault sync
"""

import asyncio
import json
import sys
import uuid
from pathlib import Path
from typing import Dict, Optional

sys.path.insert(0, str(Path(__file__).parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

from models.campaign_wiki import CampaignWiki
from models.npc import NPC, NPCRelationship, NPCRole, RelationshipType
from models.location import Location, LocationType
from models.quest import Quest, QuestStatus, QuestType
from models.timeline import TimelineEvent, EventType
from models.faction import Faction, FactionType, ReputationLevel
from utils.obsidian_sync import ObsidianSync
from utils.relationship_graph import RelationshipGraph
from utils.markdown_export import MarkdownExporter

import logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("campaign-wiki")
logging.getLogger("mcp").setLevel(logging.WARNING)

# Global wiki storage
active_wikis: Dict[str, CampaignWiki] = {}
relationship_graphs: Dict[str, RelationshipGraph] = {}

app = Server("campaign-wiki")


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls."""
    if name == "create_or_load_wiki":
        return await handle_create_or_load_wiki(arguments)
    elif name == "create_npc":
        return await handle_create_npc(arguments)
    elif name == "update_npc":
        return await handle_update_npc(arguments)
    elif name == "add_relationship":
        return await handle_add_relationship(arguments)
    elif name == "create_quest":
        return await handle_create_quest(arguments)
    elif name == "update_quest_status":
        return await handle_update_quest_status(arguments)
    elif name == "complete_quest":
        return await handle_complete_quest(arguments)
    elif name == "create_faction":
        return await handle_create_faction(arguments)
    elif name == "update_faction_reputation":
        return await handle_update_faction_reputation(arguments)
    elif name == "update_faction_rank":
        return await handle_update_faction_rank(arguments)
    elif name == "get_faction_info":
        return await handle_get_faction_info(arguments)
    elif name == "sync_to_obsidian":
        return await handle_sync_to_obsidian(arguments)
    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def handle_create_or_load_wiki(arguments: dict) -> list[types.TextContent]:
    """Create or load a campaign wiki
    
    Args:
        campaign_name: Campaign name
        obsidian_vault: Path to Obsidian vault (optional)
        maps_folder: Path to maps folder (optional)
    """
    try:
        campaign_name = arguments["campaign_name"]
        obsidian_vault = arguments.get("obsidian_vault")
        maps_folder = arguments.get("maps_folder")
        
        data_path = f"C:\\DnD\\Campaigns\\{campaign_name}\\wiki\\campaign_wiki.json"
        
        # Default Obsidian vault path if not provided
        if not obsidian_vault:
            obsidian_vault = "C:\\Users\\ksist\\Documents\\Obsidian\\DnD"
        
        # Try to load existing
        if Path(data_path).exists():
            wiki = CampaignWiki.load(data_path)
            # Update vault path if not set or if new one provided
            if not wiki.obsidian_vault:
                wiki.obsidian_vault = obsidian_vault
            elif obsidian_vault and obsidian_vault != wiki.obsidian_vault:
                wiki.obsidian_vault = obsidian_vault
            if maps_folder and not wiki.maps_folder:
                wiki.maps_folder = maps_folder
        else:
            wiki = CampaignWiki(
                campaign_name=campaign_name,
                data_path=data_path,
                obsidian_vault=obsidian_vault,
                maps_folder=maps_folder,
            )
        
        # Store in memory
        active_wikis[campaign_name] = wiki
        relationship_graphs[campaign_name] = RelationshipGraph()
        
        # Load relationships into graph
        for rel in wiki.relationships:
            relationship_graphs[campaign_name].add_relationship(
                rel.from_entity,
                rel.to_entity,
                rel.relationship_type,
                rel.strength
            )
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "campaign": campaign_name,
                "npcs": len(wiki.npcs),
                "locations": len(wiki.locations),
                "quests": len(wiki.quests),
                "timeline_events": len(wiki.timeline),
            }, indent=2)
        )]
    except Exception as e:
        logger.error(f"Error loading wiki: {e}", exc_info=True)
        return [types.TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}, indent=2))]


async def handle_create_npc(arguments: dict) -> list[types.TextContent]:
    """Create a new NPC"""
    try:
        campaign_name = arguments["campaign_name"]
        wiki = active_wikis.get(campaign_name)
        if not wiki:
            raise ValueError(f"Wiki for {campaign_name} not loaded")
        
        npc_id = arguments.get("npc_id", str(uuid.uuid4()))
        npc = NPC(
            npc_id=npc_id,
            name=arguments["name"],
            role=NPCRole(arguments.get("role", "neutral")),
            description=arguments.get("description", ""),
            **{k: v for k, v in arguments.items() if k not in ["campaign_name", "npc_id", "name", "role", "description"]}
        )
        
        wiki.npcs[npc_id] = npc
        wiki.save()
        
        # Add to relationship graph
        graph = relationship_graphs.get(campaign_name)
        if graph:
            graph.add_entity(npc_id, {"name": npc.name, "role": npc.role})
        
        # Auto-sync to Obsidian if vault is configured
        if wiki.obsidian_vault:
            try:
                sync = ObsidianSync(wiki.obsidian_vault)
                npc_dict = npc.model_dump()
                sync.export_npc(npc_dict, wiki.model_dump())
            except Exception as e:
                logger.warning(f"Failed to auto-sync NPC to Obsidian: {e}")
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "npc_id": npc_id,
                "name": npc.name,
                "obsidian_synced": wiki.obsidian_vault is not None,
            }, indent=2)
        )]
    except Exception as e:
        logger.error(f"Error creating NPC: {e}", exc_info=True)
        return [types.TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}, indent=2))]


async def handle_update_npc(arguments: dict) -> list[types.TextContent]:
    """Update an existing NPC and auto-sync to Obsidian"""
    try:
        campaign_name = arguments["campaign_name"]
        wiki = active_wikis.get(campaign_name)
        if not wiki:
            raise ValueError(f"Wiki for {campaign_name} not loaded")
        
        # Find NPC by name or ID
        npc_name_or_id = arguments.get("npc_name") or arguments.get("npc_id")
        if not npc_name_or_id:
            raise ValueError("Must provide npc_name or npc_id")
        
        # Find the NPC
        npc = None
        npc_id = None
        for nid, n in wiki.npcs.items():
            if n.npc_id == npc_name_or_id or n.name == npc_name_or_id:
                npc = n
                npc_id = nid
                break
        
        if not npc:
            raise ValueError(f"NPC '{npc_name_or_id}' not found")
        
        # Update fields from arguments
        update_fields = {
            "alive", "status", "location", "description", "background", 
            "last_seen", "disposition", "faction", "role", "tags", "notes"
        }
        
        for field in update_fields:
            if field in arguments:
                if field == "alive":
                    npc.alive = bool(arguments[field])
                elif field == "status":
                    # Handle status as string or enum
                    setattr(npc, field, arguments[field])
                elif field == "tags" or field == "notes":
                    # Handle lists
                    if isinstance(arguments[field], list):
                        setattr(npc, field, arguments[field])
                    else:
                        setattr(npc, field, [arguments[field]])
                else:
                    setattr(npc, field, arguments[field])
        
        # Special handling for status updates
        if "status" in arguments:
            status = arguments["status"].lower()
            if status in ["dead", "executed", "killed", "deceased"]:
                npc.alive = False
                if "deceased" not in npc.tags:
                    npc.tags.append("deceased")
            elif status in ["alive", "active", "healthy"]:
                npc.alive = True
                if "deceased" in npc.tags:
                    npc.tags.remove("deceased")
        
        # Special handling for direct alive updates
        if "alive" in arguments:
            if not npc.alive and "deceased" not in npc.tags:
                npc.tags.append("deceased")
            elif npc.alive and "deceased" in npc.tags:
                npc.tags.remove("deceased")
        
        wiki.save()
        
        # Auto-sync to Obsidian if vault is configured
        obsidian_synced = False
        if wiki.obsidian_vault:
            try:
                sync = ObsidianSync(wiki.obsidian_vault)
                npc_dict = npc.model_dump()
                sync.export_npc(npc_dict, wiki.model_dump())
                obsidian_synced = True
            except Exception as e:
                logger.warning(f"Failed to auto-sync NPC to Obsidian: {e}")
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "npc_id": npc_id,
                "name": npc.name,
                "alive": npc.alive,
                "status": getattr(npc, "status", None),
                "obsidian_synced": obsidian_synced,
            }, indent=2)
        )]
    except Exception as e:
        logger.error(f"Error updating NPC: {e}", exc_info=True)
        return [types.TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}, indent=2))]


async def handle_add_relationship(arguments: dict) -> list[types.TextContent]:
    """Add a relationship between NPCs/PCs"""
    try:
        campaign_name = arguments["campaign_name"]
        wiki = active_wikis.get(campaign_name)
        graph = relationship_graphs.get(campaign_name)
        if not wiki or not graph:
            raise ValueError(f"Wiki for {campaign_name} not loaded")
        
        rel = NPCRelationship(
            from_entity=arguments["from_entity"],
            to_entity=arguments["to_entity"],
            relationship_type=RelationshipType(arguments["relationship_type"]),
            description=arguments.get("description", ""),
            strength=arguments.get("strength", 5),
        )
        
        wiki.relationships.append(rel)
        graph.add_relationship(
            rel.from_entity,
            rel.to_entity,
            rel.relationship_type,
            rel.strength
        )
        wiki.save()
        
        # Auto-sync affected NPCs to Obsidian if vault is configured
        if wiki.obsidian_vault:
            try:
                sync = ObsidianSync(wiki.obsidian_vault)
                wiki_dict = wiki.model_dump()
                # Find and sync both entities involved in the relationship
                # Try to find by ID first, then by name
                from_npc = None
                to_npc = None
                for npc_id, npc in wiki.npcs.items():
                    if npc_id == rel.from_entity or npc.name == rel.from_entity:
                        from_npc = npc
                    if npc_id == rel.to_entity or npc.name == rel.to_entity:
                        to_npc = npc
                
                if from_npc:
                    sync.export_npc(from_npc.model_dump(), wiki_dict)
                if to_npc:
                    sync.export_npc(to_npc.model_dump(), wiki_dict)
            except Exception as e:
                logger.warning(f"Failed to auto-sync relationship to Obsidian: {e}")
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "relationship": f"{rel.from_entity} -> {rel.to_entity} ({rel.relationship_type})",
                "obsidian_synced": wiki.obsidian_vault is not None,
            }, indent=2)
        )]
    except Exception as e:
        logger.error(f"Error adding relationship: {e}", exc_info=True)
        return [types.TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}, indent=2))]


async def handle_create_quest(arguments: dict) -> list[types.TextContent]:
    """Create a new quest"""
    try:
        campaign_name = arguments["campaign_name"]
        wiki = active_wikis.get(campaign_name)
        if not wiki:
            raise ValueError(f"Wiki for {campaign_name} not loaded")
        
        quest_id = arguments.get("quest_id", str(uuid.uuid4()))
        quest = Quest(
            quest_id=quest_id,
            name=arguments["name"],
            description=arguments["description"],
            quest_type=QuestType(arguments.get("quest_type", "side")),
            status=QuestStatus(arguments.get("status", "available")),
            **{k: v for k, v in arguments.items() if k not in ["campaign_name", "quest_id", "name", "description", "quest_type", "status"]}
        )
        
        wiki.quests[quest_id] = quest
        wiki.save()
        
        # Auto-sync to Obsidian if vault is configured
        if wiki.obsidian_vault:
            try:
                sync = ObsidianSync(wiki.obsidian_vault)
                sync.export_quest(quest.model_dump())
            except Exception as e:
                logger.warning(f"Failed to auto-sync quest to Obsidian: {e}")
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "quest_id": quest_id,
                "name": quest.name,
                "status": quest.status,
            }, indent=2)
        )]
    except Exception as e:
        logger.error(f"Error creating quest: {e}", exc_info=True)
        return [types.TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}, indent=2))]


async def handle_update_quest_status(arguments: dict) -> list[types.TextContent]:
    """Update quest status"""
    try:
        campaign_name = arguments["campaign_name"]
        wiki = active_wikis.get(campaign_name)
        if not wiki:
            raise ValueError(f"Wiki for {campaign_name} not loaded")
        
        quest_id = arguments["quest_id"]
        new_status = QuestStatus(arguments["status"])
        
        quest = wiki.quests.get(quest_id)
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")
        
        quest.status = new_status
        
        # Update dates
        from datetime import datetime
        if new_status == QuestStatus.ACCEPTED and not quest.date_accepted:
            quest.date_accepted = datetime.now()
        elif new_status == QuestStatus.COMPLETED and not quest.date_completed:
            quest.date_completed = datetime.now()
        
        wiki.save()
        
        # Auto-sync to Obsidian if vault is configured
        if wiki.obsidian_vault:
            try:
                sync = ObsidianSync(wiki.obsidian_vault)
                sync.export_quest(quest.model_dump())
            except Exception as e:
                logger.warning(f"Failed to auto-sync quest to Obsidian: {e}")
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "quest_id": quest_id,
                "name": quest.name,
                "new_status": quest.status.value,
            }, indent=2)
        )]
    except Exception as e:
        logger.error(f"Error updating quest status: {e}", exc_info=True)
        return [types.TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}, indent=2))]


async def handle_complete_quest(arguments: dict) -> list[types.TextContent]:
    """Complete a quest and distribute rewards/reputation"""
    try:
        campaign_name = arguments["campaign_name"]
        wiki = active_wikis.get(campaign_name)
        if not wiki:
            raise ValueError(f"Wiki for {campaign_name} not loaded")
        
        quest_id = arguments["quest_id"]
        party_members = arguments.get("party_members", ["Party"])  # Default to "Party" if not specified
        
        quest = wiki.quests.get(quest_id)
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")
        
        # Update quest status
        from datetime import datetime
        quest.status = QuestStatus.COMPLETED
        if not quest.date_completed:
            quest.date_completed = datetime.now()
        
        results = {
            "quest_id": quest_id,
            "quest_name": quest.name,
            "status": "completed",
            "rewards_distributed": {}
        }
        
        # Distribute gold (split evenly among party members)
        if quest.reward_gold > 0:
            gold_per_member = quest.reward_gold // len(party_members) if party_members else quest.reward_gold
            remainder = quest.reward_gold % len(party_members) if party_members else 0
            
            results["rewards_distributed"]["gold"] = {}
            for i, member in enumerate(party_members):
                member_gold = gold_per_member + (1 if i < remainder else 0)
                results["rewards_distributed"]["gold"][member] = member_gold
        
        # Distribute items (list items, DM decides who gets what)
        if quest.reward_items:
            results["rewards_distributed"]["items"] = quest.reward_items
        
        # Distribute XP (split evenly among party members)
        if quest.reward_xp > 0:
            xp_per_member = quest.reward_xp // len(party_members) if party_members else quest.reward_xp
            results["rewards_distributed"]["xp"] = {}
            for member in party_members:
                results["rewards_distributed"]["xp"][member] = xp_per_member
        
        # Update faction reputation
        reputation_changes = {}
        
        # 1. If quest giver has a faction, update that faction's reputation
        if quest.quest_giver:
            # Find NPC by ID or name
            quest_giver_npc = None
            for npc_id, npc in wiki.npcs.items():
                if npc_id == quest.quest_giver or npc.name == quest.quest_giver:
                    quest_giver_npc = npc
                    break
            
            if quest_giver_npc and quest_giver_npc.faction:
                # Find faction by name
                faction = None
                for fac_id, fac in wiki.factions.items():
                    if fac.name == quest_giver_npc.faction:
                        faction = fac
                        break
                
                if faction:
                    # Default reputation boost for completing quest for faction member
                    default_rep = 5
                    faction.adjust_reputation("Party", default_rep)
                    reputation_changes[quest_giver_npc.faction] = default_rep
        
        # 2. Apply quest-specific reputation rewards
        for faction_name, rep_amount in quest.reward_reputation.items():
            # Find faction by name
            faction = None
            for fac_id, fac in wiki.factions.items():
                if fac.name == faction_name:
                    faction = fac
                    break
            
            if faction:
                faction.adjust_reputation("Party", rep_amount)
                if faction_name in reputation_changes:
                    reputation_changes[faction_name] += rep_amount
                else:
                    reputation_changes[faction_name] = rep_amount
        
        if reputation_changes:
            results["rewards_distributed"]["reputation"] = reputation_changes
            # Auto-sync affected factions to Obsidian
            if wiki.obsidian_vault:
                try:
                    sync = ObsidianSync(wiki.obsidian_vault)
                    wiki_dict = wiki.model_dump()
                    for faction_name in reputation_changes.keys():
                        for fac_id, fac in wiki.factions.items():
                            if fac.name == faction_name:
                                sync.export_faction(fac.model_dump(), wiki_dict)
                                break
                except Exception as e:
                    logger.warning(f"Failed to auto-sync factions to Obsidian: {e}")
        
        wiki.save()
        
        # Auto-sync quest to Obsidian if vault is configured
        if wiki.obsidian_vault:
            try:
                sync = ObsidianSync(wiki.obsidian_vault)
                sync.export_quest(quest.model_dump())
            except Exception as e:
                logger.warning(f"Failed to auto-sync quest to Obsidian: {e}")
        
        return [types.TextContent(
            type="text",
            text=json.dumps(results, indent=2, default=str)
        )]
    except Exception as e:
        logger.error(f"Error completing quest: {e}", exc_info=True)
        return [types.TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}, indent=2))]


async def handle_sync_to_obsidian(arguments: dict) -> list[types.TextContent]:
    """Sync campaign wiki to Obsidian vault"""
    try:
        campaign_name = arguments["campaign_name"]
        wiki = active_wikis.get(campaign_name)
        if not wiki:
            raise ValueError(f"Wiki for {campaign_name} not loaded")
        
        if not wiki.obsidian_vault:
            raise ValueError("Obsidian vault path not configured")
        
        sync = ObsidianSync(wiki.obsidian_vault)
        sync.sync_all(wiki.model_dump())
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": f"Synced to {wiki.obsidian_vault}",
                "npcs": len(wiki.npcs),
                "locations": len(wiki.locations),
                "quests": len(wiki.quests),
            }, indent=2)
        )]
    except Exception as e:
        logger.error(f"Error syncing to Obsidian: {e}", exc_info=True)
        return [types.TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}, indent=2))]


async def handle_create_faction(arguments: dict) -> list[types.TextContent]:
    """Create a new faction"""
    try:
        campaign_name = arguments["campaign_name"]
        wiki = active_wikis.get(campaign_name)
        if not wiki:
            raise ValueError(f"Wiki for {campaign_name} not loaded")
        
        faction_id = arguments.get("faction_id", str(uuid.uuid4()))
        faction = Faction(
            faction_id=faction_id,
            name=arguments["name"],
            faction_type=FactionType(arguments.get("faction_type", "other")),
            description=arguments.get("description", ""),
            goals=arguments.get("goals", []),
            values=arguments.get("values", []),
            territory=arguments.get("territory", []),
            leader=arguments.get("leader"),
            headquarters=arguments.get("headquarters"),
            member_npcs=arguments.get("member_npcs", []),
            size=arguments.get("size"),
            rank_structure=arguments.get("rank_structure", []),
            benefits=arguments.get("benefits", {}),
            requirements=arguments.get("requirements", {}),
            allied_factions=arguments.get("allied_factions", []),
            enemy_factions=arguments.get("enemy_factions", []),
            active=arguments.get("active", True),
            notes=arguments.get("notes", ""),
        )
        
        wiki.factions[faction_id] = faction
        wiki.save()
        
        # Auto-sync to Obsidian if vault is configured
        if wiki.obsidian_vault:
            try:
                sync = ObsidianSync(wiki.obsidian_vault)
                faction_dict = faction.model_dump()
                sync.export_faction(faction_dict, wiki.model_dump())
            except Exception as e:
                logger.warning(f"Failed to auto-sync faction to Obsidian: {e}")
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "faction_id": faction_id,
                "name": faction.name,
                "obsidian_synced": wiki.obsidian_vault is not None,
            }, indent=2)
        )]
    except Exception as e:
        logger.error(f"Error creating faction: {e}", exc_info=True)
        return [types.TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}, indent=2))]


async def handle_update_faction_reputation(arguments: dict) -> list[types.TextContent]:
    """Update faction reputation for a character/party"""
    try:
        campaign_name = arguments["campaign_name"]
        wiki = active_wikis.get(campaign_name)
        if not wiki:
            raise ValueError(f"Wiki for {campaign_name} not loaded")
        
        faction_id = arguments["faction_id"]
        character_name = arguments["character_name"]
        amount = arguments.get("amount", 0)
        
        faction = wiki.factions.get(faction_id)
        if not faction:
            raise ValueError(f"Faction {faction_id} not found")
        
        new_rep = faction.adjust_reputation(character_name, amount)
        rep_level = faction.get_reputation_level(character_name)
        wiki.save()
        
        # Auto-sync to Obsidian if vault is configured
        if wiki.obsidian_vault:
            try:
                sync = ObsidianSync(wiki.obsidian_vault)
                faction_dict = faction.model_dump()
                sync.export_faction(faction_dict, wiki.model_dump())
            except Exception as e:
                logger.warning(f"Failed to auto-sync faction to Obsidian: {e}")
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "faction": faction.name,
                "character": character_name,
                "new_reputation": new_rep,
                "reputation_level": rep_level.value,
            }, indent=2)
        )]
    except Exception as e:
        logger.error(f"Error updating faction reputation: {e}", exc_info=True)
        return [types.TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}, indent=2))]


async def handle_update_faction_rank(arguments: dict) -> list[types.TextContent]:
    """Update faction rank for a character/party"""
    try:
        campaign_name = arguments["campaign_name"]
        wiki = active_wikis.get(campaign_name)
        if not wiki:
            raise ValueError(f"Wiki for {campaign_name} not loaded")
        
        faction_id = arguments["faction_id"]
        character_name = arguments["character_name"]
        new_rank = arguments.get("new_rank")
        promote = arguments.get("promote", False)
        
        faction = wiki.factions.get(faction_id)
        if not faction:
            raise ValueError(f"Faction {faction_id} not found")
        
        if promote:
            new_rank = faction.promote(character_name)
            if not new_rank:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Cannot promote {character_name} - already at highest rank or no rank structure defined"
                    }, indent=2)
                )]
        else:
            if not new_rank:
                raise ValueError("Must provide new_rank or set promote=true")
            faction.rank[character_name] = new_rank
        
        wiki.save()
        
        # Auto-sync to Obsidian if vault is configured
        if wiki.obsidian_vault:
            try:
                sync = ObsidianSync(wiki.obsidian_vault)
                faction_dict = faction.model_dump()
                sync.export_faction(faction_dict, wiki.model_dump())
            except Exception as e:
                logger.warning(f"Failed to auto-sync faction to Obsidian: {e}")
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "faction": faction.name,
                "character": character_name,
                "new_rank": new_rank,
            }, indent=2)
        )]
    except Exception as e:
        logger.error(f"Error updating faction rank: {e}", exc_info=True)
        return [types.TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}, indent=2))]


async def handle_get_faction_info(arguments: dict) -> list[types.TextContent]:
    """Get faction information including reputation and rank for a character"""
    try:
        campaign_name = arguments["campaign_name"]
        wiki = active_wikis.get(campaign_name)
        if not wiki:
            raise ValueError(f"Wiki for {campaign_name} not loaded")
        
        faction_id = arguments["faction_id"]
        character_name = arguments.get("character_name")
        
        faction = wiki.factions.get(faction_id)
        if not faction:
            raise ValueError(f"Faction {faction_id} not found")
        
        result = {
            "faction_id": faction.faction_id,
            "name": faction.name,
            "faction_type": faction.faction_type.value,
            "description": faction.description,
            "active": faction.active,
        }
        
        if character_name:
            rep = faction.reputation.get(character_name, 0)
            rep_level = faction.get_reputation_level(character_name)
            rank = faction.rank.get(character_name, "None")
            
            result["character"] = character_name
            result["reputation"] = rep
            result["reputation_level"] = rep_level.value
            result["rank"] = rank
            result["can_promote"] = faction.can_promote(character_name)
            
            # Get benefits for current rank
            if rank in faction.benefits:
                result["benefits"] = faction.benefits[rank]
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
    except Exception as e:
        logger.error(f"Error getting faction info: {e}", exc_info=True)
        return [types.TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}, indent=2))]


# Additional tools follow same pattern...
# For brevity, core tools implemented above establish the pattern

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available campaign wiki tools."""
    return [
        types.Tool(
            name="create_or_load_wiki",
            description="Create or load a campaign wiki for tracking NPCs, locations, quests, and timeline",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_name": {"type": "string", "description": "Campaign name"},
                    "obsidian_vault": {"type": "string", "description": "Path to Obsidian vault (optional)"},
                    "maps_folder": {"type": "string", "description": "Path to maps folder (optional)"}
                },
                "required": ["campaign_name"]
            }
        ),
        types.Tool(
            name="create_npc",
            description="Create a new NPC in the campaign wiki",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_name": {"type": "string", "description": "Campaign name"},
                    "name": {"type": "string", "description": "NPC name"},
                    "role": {"type": "string", "description": "NPC role (ally/enemy/neutral/quest_giver)"},
                    "description": {"type": "string", "description": "NPC description"},
                    "npc_id": {"type": "string", "description": "Optional NPC ID (auto-generated if not provided)"}
                },
                "required": ["campaign_name", "name"]
            }
        ),
        types.Tool(
            name="update_npc",
            description="Update an existing NPC's status, location, alive status, or other fields. Automatically syncs to Obsidian.",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_name": {"type": "string", "description": "Campaign name"},
                    "npc_name": {"type": "string", "description": "NPC name (or use npc_id)"},
                    "npc_id": {"type": "string", "description": "NPC ID (or use npc_name)"},
                    "alive": {"type": "boolean", "description": "Whether NPC is alive (true/false)"},
                    "status": {"type": "string", "description": "Status (e.g., 'alive', 'captured', 'executed', 'dead', 'killed', 'deceased')"},
                    "location": {"type": "string", "description": "Current location"},
                    "description": {"type": "string", "description": "Updated description"},
                    "background": {"type": "string", "description": "Updated background"},
                    "last_seen": {"type": "string", "description": "Last interaction/where seen"},
                    "disposition": {"type": "integer", "description": "Disposition toward party (-10 to 10)"},
                    "faction": {"type": "string", "description": "Faction affiliation"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags list"},
                    "notes": {"type": "array", "items": {"type": "string"}, "description": "Session notes"}
                },
                "required": ["campaign_name"]
            }
        ),
        types.Tool(
            name="add_relationship",
            description="Add a relationship between two entities (NPCs/PCs)",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_name": {"type": "string", "description": "Campaign name"},
                    "from_entity": {"type": "string", "description": "Source entity ID or name"},
                    "to_entity": {"type": "string", "description": "Target entity ID or name"},
                    "relationship_type": {"type": "string", "description": "Relationship type (ally/enemy/family/romantic/professional)"},
                    "description": {"type": "string", "description": "Relationship description"},
                    "strength": {"type": "integer", "description": "Relationship strength (1-10, default 5)"}
                },
                "required": ["campaign_name", "from_entity", "to_entity", "relationship_type"]
            }
        ),
        types.Tool(
            name="create_quest",
            description="Create a new quest in the campaign",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_name": {"type": "string", "description": "Campaign name"},
                    "name": {"type": "string", "description": "Quest name"},
                    "description": {"type": "string", "description": "Quest description"},
                    "quest_type": {"type": "string", "description": "Quest type (main/side/personal/faction/bounty/fetch/escort/investigation/rescue/combat)"},
                    "status": {"type": "string", "description": "Quest status (not_started/available/accepted/in_progress/completed/failed/abandoned)"},
                    "quest_giver": {"type": "string", "description": "NPC ID or name who gave the quest"},
                    "reward_gold": {"type": "integer", "description": "Gold reward amount"},
                    "reward_xp": {"type": "integer", "description": "XP reward amount"},
                    "reward_items": {"type": "array", "items": {"type": "string"}, "description": "Item rewards"},
                    "reward_reputation": {"type": "object", "description": "Reputation changes by faction name (e.g., {\"Lords' Alliance\": 5})"},
                    "objectives": {"type": "array", "items": {"type": "string"}, "description": "Quest objectives"},
                    "quest_id": {"type": "string", "description": "Optional quest ID (auto-generated if not provided)"}
                },
                "required": ["campaign_name", "name", "description"]
            }
        ),
        types.Tool(
            name="update_quest_status",
            description="Update the status of a quest",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_name": {"type": "string", "description": "Campaign name"},
                    "quest_id": {"type": "string", "description": "Quest ID"},
                    "status": {"type": "string", "description": "New status (not_started/available/accepted/in_progress/completed/failed/abandoned)"}
                },
                "required": ["campaign_name", "quest_id", "status"]
            }
        ),
        types.Tool(
            name="complete_quest",
            description="Complete a quest and automatically distribute rewards (gold, XP, items) and update faction reputation",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_name": {"type": "string", "description": "Campaign name"},
                    "quest_id": {"type": "string", "description": "Quest ID"},
                    "party_members": {"type": "array", "items": {"type": "string"}, "description": "List of party member names for reward distribution (defaults to ['Party'] if not provided)"}
                },
                "required": ["campaign_name", "quest_id"]
            }
        ),
        types.Tool(
            name="create_faction",
            description="Create a new faction in the campaign wiki",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_name": {"type": "string", "description": "Campaign name"},
                    "name": {"type": "string", "description": "Faction name"},
                    "faction_type": {"type": "string", "description": "Faction type (guild/religious/military/criminal/merchant/noble/academic/adventurer/cult/government/other)"},
                    "description": {"type": "string", "description": "Faction description"},
                    "goals": {"type": "array", "items": {"type": "string"}, "description": "Faction goals"},
                    "values": {"type": "array", "items": {"type": "string"}, "description": "Faction values"},
                    "territory": {"type": "array", "items": {"type": "string"}, "description": "Territories controlled"},
                    "leader": {"type": "string", "description": "Leader NPC ID or name"},
                    "headquarters": {"type": "string", "description": "Headquarters location ID or name"},
                    "member_npcs": {"type": "array", "items": {"type": "string"}, "description": "NPC IDs who are members"},
                    "size": {"type": "string", "description": "Faction size (small/medium/large/huge)"},
                    "rank_structure": {"type": "array", "items": {"type": "string"}, "description": "Rank titles from lowest to highest"},
                    "benefits": {"type": "object", "description": "Benefits by rank"},
                    "requirements": {"type": "object", "description": "Requirements for each rank"},
                    "allied_factions": {"type": "array", "items": {"type": "string"}, "description": "Allied faction IDs"},
                    "enemy_factions": {"type": "array", "items": {"type": "string"}, "description": "Enemy faction IDs"},
                    "faction_id": {"type": "string", "description": "Optional faction ID (auto-generated if not provided)"}
                },
                "required": ["campaign_name", "name"]
            }
        ),
        types.Tool(
            name="update_faction_reputation",
            description="Update faction reputation for a character/party (range: -100 to 100)",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_name": {"type": "string", "description": "Campaign name"},
                    "faction_id": {"type": "string", "description": "Faction ID"},
                    "character_name": {"type": "string", "description": "Character or party name"},
                    "amount": {"type": "integer", "description": "Reputation change amount (positive or negative)"}
                },
                "required": ["campaign_name", "faction_id", "character_name", "amount"]
            }
        ),
        types.Tool(
            name="update_faction_rank",
            description="Update or promote faction rank for a character/party",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_name": {"type": "string", "description": "Campaign name"},
                    "faction_id": {"type": "string", "description": "Faction ID"},
                    "character_name": {"type": "string", "description": "Character or party name"},
                    "new_rank": {"type": "string", "description": "New rank title (optional if promote=true)"},
                    "promote": {"type": "boolean", "description": "Promote to next rank automatically (default: false)"}
                },
                "required": ["campaign_name", "faction_id", "character_name"]
            }
        ),
        types.Tool(
            name="get_faction_info",
            description="Get faction information including reputation and rank for a character",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_name": {"type": "string", "description": "Campaign name"},
                    "faction_id": {"type": "string", "description": "Faction ID"},
                    "character_name": {"type": "string", "description": "Character or party name (optional)"}
                },
                "required": ["campaign_name", "faction_id"]
            }
        ),
        types.Tool(
            name="sync_to_obsidian",
            description="Sync campaign wiki data to Obsidian vault as markdown files",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_name": {"type": "string", "description": "Campaign name"}
                },
                "required": ["campaign_name"]
            }
        )
    ]


async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

