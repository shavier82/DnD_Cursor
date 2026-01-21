#!/usr/bin/env python3
"""
Knowledge Graph MCP Server for D&D Campaigns
Tracks entities, relationships, and lore connections.
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    from mcp.server.stdio import stdio_server
except ImportError:
    print("ERROR: mcp package not found. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

class KnowledgeGraphServer:
    def __init__(self):
        self.campaign_path = Path("C:/DnD/Campaigns")
        self.entities = {}
        self.relationships = []
    
    def add_entity(self, name: str, entity_type: str, description: str) -> dict:
        """Add a new entity to the knowledge graph."""
        self.entities[name] = {
            "type": entity_type,
            "description": description
        }
        return {
            "success": True,
            "entity": name,
            "type": entity_type
        }
    
    def add_relationship(self, from_entity: str, to_entity: str, relationship: str) -> dict:
        """Add a relationship between two entities."""
        rel = {
            "from": from_entity,
            "to": to_entity,
            "type": relationship
        }
        self.relationships.append(rel)
        return {
            "success": True,
            "relationship": rel
        }
    
    def query_entity(self, name: str) -> dict:
        """Get information about an entity."""
        if name in self.entities:
            # Find relationships
            related = [
                r for r in self.relationships
                if r["from"] == name or r["to"] == name
            ]
            return {
                "entity": name,
                "info": self.entities[name],
                "relationships": related
            }
        return {
            "error": f"Entity '{name}' not found"
        }


# Initialize MCP server
app = Server("knowledge-graph")
server = KnowledgeGraphServer()


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="add_entity",
            description="Add a new entity (NPC, location, item, faction) to the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Entity name"},
                    "entity_type": {"type": "string", "description": "Type: npc, location, item, faction"},
                    "description": {"type": "string", "description": "Brief description"}
                },
                "required": ["name", "entity_type", "description"]
            }
        ),
        Tool(
            name="add_relationship",
            description="Add a relationship between two entities",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_entity": {"type": "string"},
                    "to_entity": {"type": "string"},
                    "relationship": {"type": "string", "description": "Type: ally, enemy, member_of, located_in, etc."}
                },
                "required": ["from_entity", "to_entity", "relationship"]
            }
        ),
        Tool(
            name="query_entity",
            description="Get information about an entity and its relationships",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Entity name to query"}
                },
                "required": ["name"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "add_entity":
            result = server.add_entity(
                arguments["name"],
                arguments["entity_type"],
                arguments["description"]
            )
        elif name == "add_relationship":
            result = server.add_relationship(
                arguments["from_entity"],
                arguments["to_entity"],
                arguments["relationship"]
            )
        elif name == "query_entity":
            result = server.query_entity(arguments["name"])
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


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


