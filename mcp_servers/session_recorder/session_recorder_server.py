#!/usr/bin/env python3
"""
Session Logger & Event Tracker MCP Server

Logs text-based D&D gameplay, extracts events, and updates campaign state.
Records narration, choices, rolls, and outcomes during text-based sessions.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

# Suppress verbose logs
logging.basicConfig(level=logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import mcp.types as types

# ============================================================
# CONFIGURATION
# ============================================================

CAMPAIGN_BASE = r"C:\DnD\Campaigns"
SESSION_LOGS_DIR = r"C:\DnD\DnD_Cursor\session_logs"

# Global session state
active_session = None
session_log_buffer = []

# ============================================================
# SESSION LOG MANAGEMENT
# ============================================================

def get_logs_dir():
    """Ensure session logs directory exists"""
    Path(SESSION_LOGS_DIR).mkdir(parents=True, exist_ok=True)
    return SESSION_LOGS_DIR

def start_session_log(campaign_name: str, session_title: str = None) -> dict:
    """Start a new session log"""
    global active_session, session_log_buffer
    
    if active_session is not None:
        return {
            "success": False,
            "error": f"Session already active: {active_session['session_id']}"
        }
    
    # Create session metadata
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = f"session_{timestamp}"
    
    if session_title is None:
        session_title = f"Session {datetime.now().strftime('%Y-%m-%d')}"
    
    active_session = {
        "session_id": session_id,
        "campaign_name": campaign_name,
        "session_title": session_title,
        "start_time": datetime.now().isoformat(),
        "log_file": os.path.join(get_logs_dir(), f"{session_id}.jsonl")
    }
    
    session_log_buffer = []
    
    # Write session header
    header = {
        "type": "session_start",
        "timestamp": active_session["start_time"],
        "campaign": campaign_name,
        "title": session_title,
        "session_id": session_id
    }
    
    with open(active_session["log_file"], "w", encoding="utf-8") as f:
        f.write(json.dumps(header) + "\n")
    
    return {
        "success": True,
        "message": "📝 Session logging started",
        "session_id": session_id,
        "campaign": campaign_name,
        "title": session_title,
        "log_file": active_session["log_file"]
    }

def log_event(event_type: str, content: str, metadata: dict = None) -> dict:
    """
    Log a session event (narration, choice, roll, etc.)
    
    Args:
        event_type: narration|choice|roll|combat|npc_interaction|discovery|gate|consequence
        content: The text content of the event
        metadata: Additional data (character names, roll results, etc.)
    """
    global active_session, session_log_buffer
    
    if active_session is None:
        return {
            "success": False,
            "error": "No active session. Call start_session_log() first."
        }
    
    # Create event entry
    event = {
        "type": event_type,
        "timestamp": datetime.now().isoformat(),
        "content": content
    }
    
    if metadata:
        event["metadata"] = metadata
    
    # Add to buffer
    session_log_buffer.append(event)
    
    # Write to log file
    with open(active_session["log_file"], "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
    
    return {
        "success": True,
        "message": "Event logged",
        "event_type": event_type,
        "events_logged": len(session_log_buffer)
    }

def stop_session_log() -> dict:
    """Stop the current session log"""
    global active_session, session_log_buffer
    
    if active_session is None:
        return {
            "success": False,
            "error": "No active session"
        }
    
    # Write session footer
    footer = {
        "type": "session_end",
        "timestamp": datetime.now().isoformat(),
        "duration_minutes": _calculate_session_duration(),
        "total_events": len(session_log_buffer)
    }
    
    with open(active_session["log_file"], "a", encoding="utf-8") as f:
        f.write(json.dumps(footer) + "\n")
    
    result = {
        "success": True,
        "message": "📝 Session logging stopped",
        "session_id": active_session["session_id"],
        "log_file": active_session["log_file"],
        "total_events": len(session_log_buffer),
        "duration_minutes": _calculate_session_duration()
    }
    
    # Clear session state
    active_session = None
    session_log_buffer = []
    
    return result

def _calculate_session_duration() -> float:
    """Calculate session duration in minutes"""
    if active_session is None:
        return 0
    
    start = datetime.fromisoformat(active_session["start_time"])
    end = datetime.now()
    duration = (end - start).total_seconds() / 60
    return round(duration, 2)

def get_session_status() -> dict:
    """Get current session status"""
    global active_session, session_log_buffer
    
    if active_session is None:
        return {
            "active": False,
            "message": "No active session"
        }
    
    return {
        "active": True,
        "session_id": active_session["session_id"],
        "campaign": active_session["campaign_name"],
        "title": active_session["session_title"],
        "duration_minutes": _calculate_session_duration(),
        "events_logged": len(session_log_buffer),
        "start_time": active_session["start_time"]
    }

def list_session_logs(campaign_name: str = None) -> dict:
    """List all session logs, optionally filtered by campaign"""
    logs_dir = get_logs_dir()
    
    sessions = []
    for file in os.listdir(logs_dir):
        if file.endswith(".jsonl"):
            file_path = os.path.join(logs_dir, file)
            
            # Read session header
            with open(file_path, "r", encoding="utf-8") as f:
                header_line = f.readline()
                if header_line:
                    header = json.loads(header_line)
                    
                    # Filter by campaign if specified
                    if campaign_name and header.get("campaign") != campaign_name:
                        continue
                    
                    # Count events
                    event_count = sum(1 for line in f if line.strip())
                    
                    sessions.append({
                        "session_id": header.get("session_id"),
                        "campaign": header.get("campaign"),
                        "title": header.get("title"),
                        "start_time": header.get("timestamp"),
                        "events": event_count,
                        "file": file_path
                    })
    
    # Sort by start time (newest first)
    sessions.sort(key=lambda x: x["start_time"], reverse=True)
    
    return {
        "success": True,
        "sessions": sessions,
        "total": len(sessions),
        "directory": logs_dir
    }

# ============================================================
# EVENT EXTRACTION & ANALYSIS
# ============================================================

def extract_events_from_log(session_id: str, campaign_name: str) -> dict:
    """
    Extract structured events from a session log.
    Returns a PROMPT for the AI to analyze the session log.
    """
    logs_dir = get_logs_dir()
    log_file = os.path.join(logs_dir, f"{session_id}.jsonl")
    
    if not os.path.exists(log_file):
        return {
            "success": False,
            "error": f"Session log not found: {session_id}"
        }
    
    # Load session log
    session_events = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                session_events.append(json.loads(line))
    
    # Load current campaign context
    campaign_dir = os.path.join(CAMPAIGN_BASE, campaign_name, "saves")
    current_state_file = os.path.join(campaign_dir, "CURRENT_STATE.json")
    campaign_events_file = os.path.join(campaign_dir, "CAMPAIGN_EVENTS.json")
    
    context = {
        "current_state": None,
        "recent_events": []
    }
    
    if os.path.exists(current_state_file):
        with open(current_state_file, "r", encoding="utf-8") as f:
            context["current_state"] = json.load(f)
    
    if os.path.exists(campaign_events_file):
        with open(campaign_events_file, "r", encoding="utf-8") as f:
            all_events = json.load(f)
            context["recent_events"] = all_events[-5:] if len(all_events) > 5 else all_events
    
    # Format session log for analysis
    formatted_log = _format_session_log(session_events)
    
    # Return analysis prompt
    analysis_prompt = f"""
📝 **Session Log Analysis Required**

**Session ID:** {session_id}
**Campaign:** {campaign_name}
**Events Logged:** {len(session_events)}

**Session Log:**
{formatted_log}

**Current Campaign Context:**
- Location: {context["current_state"].get("current_location", "Unknown") if context["current_state"] else "Unknown"}
- Chapter: {context["current_state"].get("chapter", 0) if context["current_state"] else 0}
- Recent Events: {len(context["recent_events"])} events on record

**Task:**
Extract the following from the session log:
1. **Key Events** - Major story developments, encounters, discoveries
2. **Player Choices** - Important decisions made by the party
3. **NPCs Encountered** - Names and interactions
4. **Locations Visited** - New or significant locations
5. **Consequences** - Results of player actions
6. **Gates Passed** - Any checks/saves that revealed information

**Format as JSON array of events:**
```json
[
  {{
    "timestamp": "2026-01-13T13:45:00",
    "event_type": "encounter|choice|discovery|consequence|gate",
    "description": "What happened",
    "location": "Where it happened",
    "participants": ["NPC1", "NPC2"],
    "outcome": "Result of the event",
    "gates_passed": ["gate_name"],
    "significance": "high|medium|low"
  }}
]
```

Once you've extracted the events, call `update_campaign_events()` with the structured data.
"""
    
    return {
        "success": True,
        "message": "📊 Ready for AI analysis",
        "analysis_prompt": analysis_prompt,
        "session_id": session_id,
        "campaign": campaign_name,
        "events_count": len(session_events),
        "log_file": log_file
    }

def _format_session_log(events: List[dict]) -> str:
    """Format session events into readable text"""
    lines = []
    
    for event in events:
        event_type = event.get("type", "unknown")
        timestamp = event.get("timestamp", "")
        content = event.get("content", "")
        
        if event_type == "session_start":
            lines.append(f"=== SESSION START: {event.get('title', 'Untitled')} ===")
            lines.append(f"Campaign: {event.get('campaign', 'Unknown')}")
            lines.append(f"Time: {timestamp}")
            lines.append("")
        elif event_type == "session_end":
            lines.append("")
            lines.append(f"=== SESSION END ===")
            lines.append(f"Duration: {event.get('duration_minutes', 0)} minutes")
            lines.append(f"Total Events: {event.get('total_events', 0)}")
        elif event_type == "narration":
            lines.append(f"[NARRATION] {content}")
        elif event_type == "choice":
            lines.append(f"[CHOICE] {content}")
            if "metadata" in event:
                lines.append(f"  → {event['metadata']}")
        elif event_type == "roll":
            lines.append(f"[ROLL] {content}")
            if "metadata" in event:
                lines.append(f"  → Result: {event['metadata']}")
        elif event_type == "combat":
            lines.append(f"[COMBAT] {content}")
        elif event_type == "npc_interaction":
            lines.append(f"[NPC] {content}")
        elif event_type == "discovery":
            lines.append(f"[DISCOVERY] {content}")
        elif event_type == "gate":
            lines.append(f"[GATE] {content}")
        elif event_type == "consequence":
            lines.append(f"[CONSEQUENCE] {content}")
        else:
            lines.append(f"[{event_type.upper()}] {content}")
        
        lines.append("")
    
    return "\n".join(lines)

def update_campaign_events(campaign_name: str, events: list) -> dict:
    """
    Update CAMPAIGN_EVENTS.json with extracted events
    """
    campaign_dir = os.path.join(CAMPAIGN_BASE, campaign_name, "saves")
    campaign_events_file = os.path.join(campaign_dir, "CAMPAIGN_EVENTS.json")
    
    if not os.path.exists(campaign_dir):
        return {
            "success": False,
            "error": f"Campaign directory not found: {campaign_dir}"
        }
    
    try:
        # Load existing events
        existing_events = []
        if os.path.exists(campaign_events_file):
            with open(campaign_events_file, "r", encoding="utf-8") as f:
                existing_events = json.load(f)
        
        # Append new events
        existing_events.extend(events)
        
        # Create backup
        backup_file = campaign_events_file.replace(".json", f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        if os.path.exists(campaign_events_file):
            import shutil
            shutil.copy2(campaign_events_file, backup_file)
        
        # Save updated events
        with open(campaign_events_file, "w", encoding="utf-8") as f:
            json.dump(existing_events, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "message": f"✅ Added {len(events)} events to campaign log",
            "events_added": len(events),
            "total_events": len(existing_events),
            "file": campaign_events_file,
            "backup": backup_file
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to update campaign events: {str(e)}"
        }

# ============================================================
# MCP SERVER
# ============================================================

server = Server("session-recorder")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="start_session_log",
            description="Start logging a new D&D session (text-based gameplay)",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_name": {
                        "type": "string",
                        "description": "Campaign name (folder name in C:\\DnD\\Campaigns\\)"
                    },
                    "session_title": {
                        "type": "string",
                        "description": "Optional session title (default: 'Session YYYY-MM-DD')"
                    }
                },
                "required": ["campaign_name"]
            }
        ),
        types.Tool(
            name="log_event",
            description="Log a session event (narration, choice, roll, combat, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_type": {
                        "type": "string",
                        "description": "Event type: narration|choice|roll|combat|npc_interaction|discovery|gate|consequence",
                        "enum": ["narration", "choice", "roll", "combat", "npc_interaction", "discovery", "gate", "consequence"]
                    },
                    "content": {
                        "type": "string",
                        "description": "The text content of the event"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Optional additional data (character names, roll results, etc.)"
                    }
                },
                "required": ["event_type", "content"]
            }
        ),
        types.Tool(
            name="stop_session_log",
            description="Stop the current session log",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get_session_status",
            description="Get current session logging status",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="list_session_logs",
            description="List all session logs, optionally filtered by campaign",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_name": {
                        "type": "string",
                        "description": "Optional: Filter by campaign name"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="extract_events",
            description="Extract structured events from a session log for AI analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID (e.g., 'session_20260113_140000')"
                    },
                    "campaign_name": {
                        "type": "string",
                        "description": "Campaign name"
                    }
                },
                "required": ["session_id", "campaign_name"]
            }
        ),
        types.Tool(
            name="update_campaign_events",
            description="Update CAMPAIGN_EVENTS.json with extracted events",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_name": {
                        "type": "string",
                        "description": "Campaign name"
                    },
                    "events": {
                        "type": "array",
                        "description": "Array of event objects to add",
                        "items": {
                            "type": "object",
                            "properties": {
                                "timestamp": {"type": "string"},
                                "event_type": {"type": "string"},
                                "description": {"type": "string"},
                                "location": {"type": "string"},
                                "participants": {"type": "array", "items": {"type": "string"}},
                                "outcome": {"type": "string"},
                                "gates_passed": {"type": "array", "items": {"type": "string"}},
                                "significance": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["campaign_name", "events"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution"""
    
    if name == "start_session_log":
        campaign_name = arguments.get("campaign_name", "")
        session_title = arguments.get("session_title")
        result = start_session_log(campaign_name, session_title)
    elif name == "log_event":
        event_type = arguments.get("event_type", "")
        content = arguments.get("content", "")
        metadata = arguments.get("metadata")
        result = log_event(event_type, content, metadata)
    elif name == "stop_session_log":
        result = stop_session_log()
    elif name == "get_session_status":
        result = get_session_status()
    elif name == "list_session_logs":
        campaign_name = arguments.get("campaign_name")
        result = list_session_logs(campaign_name)
    elif name == "extract_events":
        session_id = arguments.get("session_id", "")
        campaign_name = arguments.get("campaign_name", "")
        result = extract_events_from_log(session_id, campaign_name)
    elif name == "update_campaign_events":
        campaign_name = arguments.get("campaign_name", "")
        events = arguments.get("events", [])
        result = update_campaign_events(campaign_name, events)
    else:
        result = {"error": f"Unknown tool: {name}"}
    
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

async def main():
    """Main entry point"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="session-recorder",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
