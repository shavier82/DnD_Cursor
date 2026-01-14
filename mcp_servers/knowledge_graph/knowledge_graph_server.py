#!/usr/bin/env python3
"""
Knowledge Graph MCP Server
Track NPC relationships, faction connections, quest dependencies, and consequence chains.

Features:
- Entity tracking (NPCs, factions, quests, events, choices)
- Relationship mapping (all types of connections)
- Consequence chain analysis
- Quest dependency tracking
- Graph visualization export
- Impact analysis
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict

# MCP SDK imports
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
from mcp import types

# Graph library
try:
    import networkx as nx
except ImportError:
    nx = None

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Suppress verbose MCP library logs
logging.getLogger("mcp.server.session").setLevel(logging.ERROR)
logging.getLogger("mcp.server.stdio").setLevel(logging.ERROR)

# Knowledge graph state file
GRAPH_STATE_FILE = Path("C:/DnD/Campaigns/knowledge_graph.json")
CAMPAIGN_EVENTS_FILE = Path("C:/DnD/Campaigns/CAMPAIGN_EVENTS.json")

app = Server("knowledge-graph")

# ============================================================================
# ENTITY TYPES
# ============================================================================

ENTITY_TYPES = ["npc", "faction", "quest", "event", "choice", "location", "item", "pc"]

RELATIONSHIP_TYPES = [
    # NPC relationships
    "ally", "enemy", "friend", "rival", "family", "mentor", "student", "employer", "employee",
    # Faction relationships
    "member_of", "leads", "allied_with", "at_war_with", "neutral_to", "controls",
    # Quest relationships
    "requires", "unlocks", "blocks", "related_to", "rewards",
    # Consequence relationships
    "caused_by", "leads_to", "prevents", "enables", "affects",
    # Location relationships
    "located_in", "controls_location", "owns",
    # Other
    "knows_about", "seeks", "protects", "threatens"
]

# ============================================================================
# KNOWLEDGE GRAPH CLASS
# ============================================================================

class KnowledgeGraph:
    """Knowledge graph for tracking campaign entities and relationships"""
    
    def __init__(self):
        self.nodes = {}  # {node_id: {type, name, data}}
        self.edges = []  # [{from, to, type, weight, data}]
        self.last_updated = None
    
    def add_node(self, node_id: str, node_type: str, name: str, data: Dict[str, Any] = None):
        """Add a node to the graph"""
        if node_type not in ENTITY_TYPES:
            raise ValueError(f"Invalid node type: {node_type}. Must be one of {ENTITY_TYPES}")
        
        self.nodes[node_id] = {
            "type": node_type,
            "name": name,
            "data": data or {},
            "created": datetime.now().isoformat()
        }
        self.last_updated = datetime.now().isoformat()
    
    def add_edge(self, from_id: str, to_id: str, edge_type: str, weight: float = 1.0, data: Dict[str, Any] = None):
        """Add an edge (relationship) to the graph"""
        if from_id not in self.nodes:
            raise ValueError(f"Node {from_id} does not exist")
        if to_id not in self.nodes:
            raise ValueError(f"Node {to_id} does not exist")
        if edge_type not in RELATIONSHIP_TYPES:
            raise ValueError(f"Invalid edge type: {edge_type}. Must be one of {RELATIONSHIP_TYPES}")
        
        self.edges.append({
            "from": from_id,
            "to": to_id,
            "type": edge_type,
            "weight": weight,
            "data": data or {},
            "created": datetime.now().isoformat()
        })
        self.last_updated = datetime.now().isoformat()
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a node by ID"""
        return self.nodes.get(node_id)
    
    def get_connections(self, node_id: str, edge_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all connections for a node"""
        connections = []
        for edge in self.edges:
            if edge["from"] == node_id or edge["to"] == node_id:
                if edge_type is None or edge["type"] == edge_type:
                    # Determine direction
                    is_outgoing = edge["from"] == node_id
                    other_id = edge["to"] if is_outgoing else edge["from"]
                    other_node = self.nodes.get(other_id)
                    
                    connections.append({
                        "direction": "outgoing" if is_outgoing else "incoming",
                        "relationship": edge["type"],
                        "connected_to": other_id,
                        "connected_name": other_node["name"] if other_node else "Unknown",
                        "connected_type": other_node["type"] if other_node else "Unknown",
                        "weight": edge["weight"],
                        "data": edge["data"]
                    })
        return connections
    
    def find_path(self, from_id: str, to_id: str) -> List[Tuple[str, str, str]]:
        """Find shortest path between two nodes (BFS)"""
        if from_id not in self.nodes or to_id not in self.nodes:
            return []
        
        # Build adjacency list
        adj = defaultdict(list)
        for edge in self.edges:
            adj[edge["from"]].append((edge["to"], edge["type"]))
            adj[edge["to"]].append((edge["from"], edge["type"]))  # Treat as undirected
        
        # BFS
        queue = [(from_id, [])]
        visited = {from_id}
        
        while queue:
            current, path = queue.pop(0)
            
            if current == to_id:
                return path
            
            for neighbor, edge_type in adj[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [(current, neighbor, edge_type)]))
        
        return []  # No path found
    
    def get_consequence_chain(self, choice_id: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """Get consequence chain starting from a choice"""
        if choice_id not in self.nodes:
            return []
        
        chain = []
        visited = set()
        queue = [(choice_id, 0)]
        
        while queue and len(chain) < max_depth:
            current, depth = queue.pop(0)
            
            if current in visited:
                continue
            visited.add(current)
            
            node = self.nodes[current]
            chain.append({
                "id": current,
                "name": node["name"],
                "type": node["type"],
                "depth": depth
            })
            
            # Find all "leads_to" or "caused_by" relationships
            for edge in self.edges:
                if edge["from"] == current and edge["type"] in ["leads_to", "caused_by", "enables", "affects"]:
                    queue.append((edge["to"], depth + 1))
        
        return chain
    
    def get_faction_relationships(self) -> List[Dict[str, Any]]:
        """Get all faction-to-faction relationships"""
        relationships = []
        
        for edge in self.edges:
            from_node = self.nodes.get(edge["from"])
            to_node = self.nodes.get(edge["to"])
            
            if from_node and to_node and from_node["type"] == "faction" and to_node["type"] == "faction":
                relationships.append({
                    "from": from_node["name"],
                    "to": to_node["name"],
                    "relationship": edge["type"],
                    "weight": edge["weight"]
                })
        
        return relationships
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        type_counts = defaultdict(int)
        for node in self.nodes.values():
            type_counts[node["type"]] += 1
        
        edge_type_counts = defaultdict(int)
        for edge in self.edges:
            edge_type_counts[edge["type"]] += 1
        
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": dict(type_counts),
            "edge_types": dict(edge_type_counts),
            "last_updated": self.last_updated
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary"""
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "last_updated": self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeGraph':
        """Load graph from dictionary"""
        graph = cls()
        graph.nodes = data.get("nodes", {})
        graph.edges = data.get("edges", [])
        graph.last_updated = data.get("last_updated")
        return graph


def load_graph() -> KnowledgeGraph:
    """Load knowledge graph from file"""
    if GRAPH_STATE_FILE.exists():
        with open(GRAPH_STATE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return KnowledgeGraph.from_dict(data)
    else:
        return KnowledgeGraph()


def save_graph(graph: KnowledgeGraph):
    """Save knowledge graph to file"""
    GRAPH_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(GRAPH_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(graph.to_dict(), indent=2, fp=f)


def import_from_campaign_events(graph: KnowledgeGraph) -> int:
    """Import entities and relationships from CAMPAIGN_EVENTS.json"""
    if not CAMPAIGN_EVENTS_FILE.exists():
        return 0
    
    with open(CAMPAIGN_EVENTS_FILE, 'r', encoding='utf-8') as f:
        events = json.load(f)
    
    imported_count = 0
    
    for event in events:
        # Add event node
        event_id = event.get("event_id", f"event_{imported_count}")
        event_type = event.get("event_type", "event")
        description = event.get("description", "Unknown event")
        
        if event_id not in graph.nodes:
            graph.add_node(event_id, "event", description, {
                "timestamp": event.get("timestamp"),
                "location": event.get("location"),
                "outcome": event.get("outcome")
            })
            imported_count += 1
        
        # Add participants as nodes and connections
        participants = event.get("participants", [])
        for participant in participants:
            participant_id = participant.lower().replace(" ", "_")
            if participant_id not in graph.nodes:
                graph.add_node(participant_id, "npc", participant)
                imported_count += 1
            
            # Connect participant to event
            try:
                graph.add_edge(participant_id, event_id, "participated_in")
            except:
                pass
        
        # Handle choices and consequences
        if "choice" in event.get("description", "").lower():
            choice_id = f"choice_{event_id}"
            if choice_id not in graph.nodes:
                graph.add_node(choice_id, "choice", event.get("description", ""), {
                    "timestamp": event.get("timestamp")
                })
                imported_count += 1
            
            # Connect choice to event
            try:
                graph.add_edge(choice_id, event_id, "leads_to")
            except:
                pass
    
    save_graph(graph)
    return imported_count


def export_for_visualization(graph: KnowledgeGraph, format: str = "json") -> str:
    """Export graph for visualization"""
    if format == "json":
        # D3.js compatible format
        nodes = []
        for node_id, node_data in graph.nodes.items():
            nodes.append({
                "id": node_id,
                "name": node_data["name"],
                "type": node_data["type"],
                "group": ENTITY_TYPES.index(node_data["type"])
            })
        
        links = []
        for edge in graph.edges:
            links.append({
                "source": edge["from"],
                "target": edge["to"],
                "type": edge["type"],
                "weight": edge["weight"]
            })
        
        return json.dumps({"nodes": nodes, "links": links}, indent=2)
    
    elif format == "dot":
        # GraphViz DOT format
        lines = ["digraph KnowledgeGraph {"]
        lines.append('  rankdir=LR;')
        lines.append('  node [shape=box];')
        
        # Add nodes
        for node_id, node_data in graph.nodes.items():
            label = f"{node_data['name']}\\n({node_data['type']})"
            lines.append(f'  "{node_id}" [label="{label}"];')
        
        # Add edges
        for edge in graph.edges:
            label = edge["type"]
            lines.append(f'  "{edge["from"]}" -> "{edge["to"]}" [label="{label}"];')
        
        lines.append("}")
        return "\n".join(lines)
    
    else:
        return json.dumps(graph.to_dict(), indent=2)


# ============================================================================
# MCP TOOLS
# ============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available knowledge graph tools"""
    return [
        Tool(
            name="add_entity",
            description="Add an entity (NPC, faction, quest, event, choice, etc.) to the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Unique ID (e.g., 'gundren_rockseeker')"},
                    "entity_type": {"type": "string", "enum": ENTITY_TYPES},
                    "name": {"type": "string", "description": "Display name"},
                    "data": {"type": "object", "description": "Additional data (optional)"}
                },
                "required": ["entity_id", "entity_type", "name"]
            }
        ),
        Tool(
            name="add_relationship",
            description="Add a relationship (edge) between two entities",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_id": {"type": "string"},
                    "to_id": {"type": "string"},
                    "relationship_type": {"type": "string", "enum": RELATIONSHIP_TYPES},
                    "weight": {"type": "number", "default": 1.0},
                    "data": {"type": "object", "description": "Additional data (optional)"}
                },
                "required": ["from_id", "to_id", "relationship_type"]
            }
        ),
        Tool(
            name="get_entity_connections",
            description="Get all connections for an entity",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string"},
                    "relationship_type": {"type": "string", "description": "Filter by type (optional)"}
                },
                "required": ["entity_id"]
            }
        ),
        Tool(
            name="find_connection_path",
            description="Find the shortest path between two entities",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_id": {"type": "string"},
                    "to_id": {"type": "string"}
                },
                "required": ["from_id", "to_id"]
            }
        ),
        Tool(
            name="analyze_consequence_chain",
            description="Analyze consequence chain from a choice or event",
            inputSchema={
                "type": "object",
                "properties": {
                    "choice_id": {"type": "string"},
                    "max_depth": {"type": "integer", "default": 10}
                },
                "required": ["choice_id"]
            }
        ),
        Tool(
            name="get_faction_relationships",
            description="Get all faction-to-faction relationships",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_quest_dependencies",
            description="Get quest dependency tree",
            inputSchema={
                "type": "object",
                "properties": {
                    "quest_id": {"type": "string", "description": "Quest ID (optional, shows all if omitted)"}
                }
            }
        ),
        Tool(
            name="import_from_campaign",
            description="Import entities and relationships from CAMPAIGN_EVENTS.json",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="export_graph",
            description="Export graph for visualization (JSON, DOT, or raw)",
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {"type": "string", "enum": ["json", "dot", "raw"], "default": "json"},
                    "output_file": {"type": "string", "description": "Output file path (optional)"}
                }
            }
        ),
        Tool(
            name="get_graph_stats",
            description="Get knowledge graph statistics",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="search_entities",
            description="Search for entities by name or type",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "entity_type": {"type": "string", "enum": ENTITY_TYPES, "description": "Filter by type (optional)"}
                },
                "required": ["query"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    
    try:
        graph = load_graph()
        
        if name == "add_entity":
            entity_id = arguments["entity_id"]
            entity_type = arguments["entity_type"]
            entity_name = arguments["name"]
            data = arguments.get("data", {})
            
            graph.add_node(entity_id, entity_type, entity_name, data)
            save_graph(graph)
            
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "message": f"Added {entity_type} '{entity_name}' (ID: {entity_id})",
                "entity": {
                    "id": entity_id,
                    "type": entity_type,
                    "name": entity_name
                }
            }, indent=2))]
        
        elif name == "add_relationship":
            from_id = arguments["from_id"]
            to_id = arguments["to_id"]
            rel_type = arguments["relationship_type"]
            weight = arguments.get("weight", 1.0)
            data = arguments.get("data", {})
            
            graph.add_edge(from_id, to_id, rel_type, weight, data)
            save_graph(graph)
            
            from_node = graph.get_node(from_id)
            to_node = graph.get_node(to_id)
            
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "message": f"Added relationship: {from_node['name']} --[{rel_type}]--> {to_node['name']}",
                "relationship": {
                    "from": from_node["name"],
                    "to": to_node["name"],
                    "type": rel_type,
                    "weight": weight
                }
            }, indent=2))]
        
        elif name == "get_entity_connections":
            entity_id = arguments["entity_id"]
            rel_type = arguments.get("relationship_type")
            
            node = graph.get_node(entity_id)
            if not node:
                return [TextContent(type="text", text=json.dumps({
                    "error": f"Entity '{entity_id}' not found"
                }, indent=2))]
            
            connections = graph.get_connections(entity_id, rel_type)
            
            return [TextContent(type="text", text=json.dumps({
                "entity": node["name"],
                "type": node["type"],
                "total_connections": len(connections),
                "connections": connections
            }, indent=2))]
        
        elif name == "find_connection_path":
            from_id = arguments["from_id"]
            to_id = arguments["to_id"]
            
            path = graph.find_path(from_id, to_id)
            
            if not path:
                return [TextContent(type="text", text=json.dumps({
                    "message": "No path found",
                    "from": from_id,
                    "to": to_id
                }, indent=2))]
            
            # Format path
            path_description = []
            for from_node_id, to_node_id, edge_type in path:
                from_node = graph.get_node(from_node_id)
                to_node = graph.get_node(to_node_id)
                path_description.append(f"{from_node['name']} --[{edge_type}]--> {to_node['name']}")
            
            return [TextContent(type="text", text=json.dumps({
                "path_found": True,
                "length": len(path),
                "path": path_description
            }, indent=2))]
        
        elif name == "analyze_consequence_chain":
            choice_id = arguments["choice_id"]
            max_depth = arguments.get("max_depth", 10)
            
            chain = graph.get_consequence_chain(choice_id, max_depth)
            
            return [TextContent(type="text", text=json.dumps({
                "choice_id": choice_id,
                "chain_length": len(chain),
                "consequence_chain": chain
            }, indent=2))]
        
        elif name == "get_faction_relationships":
            relationships = graph.get_faction_relationships()
            
            return [TextContent(type="text", text=json.dumps({
                "total_faction_relationships": len(relationships),
                "relationships": relationships
            }, indent=2))]
        
        elif name == "get_quest_dependencies":
            quest_id = arguments.get("quest_id")
            
            # Get all quest-related edges
            quest_deps = []
            for edge in graph.edges:
                from_node = graph.get_node(edge["from"])
                to_node = graph.get_node(edge["to"])
                
                if from_node and to_node:
                    if (from_node["type"] == "quest" or to_node["type"] == "quest"):
                        if edge["type"] in ["requires", "unlocks", "blocks", "related_to"]:
                            if quest_id is None or edge["from"] == quest_id or edge["to"] == quest_id:
                                quest_deps.append({
                                    "from": from_node["name"],
                                    "to": to_node["name"],
                                    "dependency": edge["type"]
                                })
            
            return [TextContent(type="text", text=json.dumps({
                "quest_id": quest_id or "all",
                "total_dependencies": len(quest_deps),
                "dependencies": quest_deps
            }, indent=2))]
        
        elif name == "import_from_campaign":
            imported = import_from_campaign_events(graph)
            
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "imported_count": imported,
                "message": f"Imported {imported} entities from CAMPAIGN_EVENTS.json"
            }, indent=2))]
        
        elif name == "export_graph":
            format_type = arguments.get("format", "json")
            output_file = arguments.get("output_file")
            
            exported_data = export_for_visualization(graph, format_type)
            
            if output_file:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(exported_data)
                
                return [TextContent(type="text", text=json.dumps({
                    "success": True,
                    "message": f"Exported graph to {output_file}",
                    "format": format_type
                }, indent=2))]
            else:
                return [TextContent(type="text", text=exported_data)]
        
        elif name == "get_graph_stats":
            stats = graph.get_stats()
            
            return [TextContent(type="text", text=json.dumps(stats, indent=2))]
        
        elif name == "search_entities":
            query = arguments["query"].lower()
            entity_type = arguments.get("entity_type")
            
            results = []
            for node_id, node_data in graph.nodes.items():
                if entity_type and node_data["type"] != entity_type:
                    continue
                
                if query in node_data["name"].lower():
                    results.append({
                        "id": node_id,
                        "name": node_data["name"],
                        "type": node_data["type"]
                    })
            
            return [TextContent(type="text", text=json.dumps({
                "query": query,
                "entity_type": entity_type or "all",
                "total_results": len(results),
                "results": results
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



