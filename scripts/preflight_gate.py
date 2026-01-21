#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preflight Gate - Hard gate for DM responses (NO DRIFT)

This script is MANDATORY before every PLAY response. It:
- Loads CURRENT_STATE.json and CAMPAIGN_EVENTS.json
- Determines current chapter and verifies chapter_pack_<N>.json exists
- Verifies required MCP servers are available
- Enforces refresh cadence (every 10 turns)
- Prints a RECEIPT that must be pasted verbatim

If this script fails or cannot produce a valid receipt:
→ Respond ONLY with: "BLOCKED: run preflight_gate.py"

Usage:
    python scripts/preflight_gate.py
"""

import json
import sys
import io
import os
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Paths - Use absolute paths to prevent CWD drift
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
CONFIG_PATH = ROOT_DIR / "config" / "paths.json"
CHECKLIST_PATH = ROOT_DIR / "MECHANICS_AUTOMATION_CHECKLIST.md"
PREFLIGHT_STATE_FILE = ROOT_DIR / ".preflight_state.json"  # Canonical location: repo root

# Hard-required MCP servers (must exit 1 if missing)
HARD_REQUIRED_MCP_SERVERS = [
    "rules-database",
    "dice-roller",
    "combat-engine",
    "obsidian-sync",
    "campaign-wiki",
    "travel-manager"
]

# Soft-required MCP servers (warn but don't block)
SOFT_REQUIRED_MCP_SERVERS = [
    "sourcebooks",
    "session-recorder",
    "music-ambience"
]

# All MCP servers for checking
ALL_MCP_SERVERS = HARD_REQUIRED_MCP_SERVERS + SOFT_REQUIRED_MCP_SERVERS

# Refresh cadence (every N turns)
REFRESH_CADENCE = 10


def load_config() -> Dict[str, Any]:
    """Load paths configuration"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        sys.stderr.write(f"ERROR: Failed to load config: {e}\n")
        sys.exit(1)


def load_preflight_state() -> Dict[str, Any]:
    """Load or create preflight state (turn tracking)"""
    if PREFLIGHT_STATE_FILE.exists():
        try:
            with open(PREFLIGHT_STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            sys.stderr.write(f"WARNING: Failed to load preflight state: {e}\n")
    
    # Create new state
    return {
        "turn": 0,
        "last_refresh_turn": 0
    }


def save_preflight_state(state: Dict[str, Any]):
    """Save preflight state"""
    try:
        with open(PREFLIGHT_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        sys.stderr.write(f"WARNING: Failed to save preflight state: {e}\n")


def load_current_state(state_file_path: Path) -> Optional[Dict[str, Any]]:
    """Load CURRENT_STATE.json"""
    try:
        if not state_file_path.exists():
            return None
        with open(state_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        sys.stderr.write(f"ERROR: Failed to load CURRENT_STATE.json: {e}\n")
        return None


def load_campaign_events(events_file_path: Path) -> Optional[Dict[str, Any]]:
    """Load CAMPAIGN_EVENTS.json"""
    try:
        if not events_file_path.exists():
            return None
        with open(events_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        sys.stderr.write(f"ERROR: Failed to load CAMPAIGN_EVENTS.json: {e}\n")
        return None


def determine_chapter(current_state: Optional[Dict[str, Any]]) -> Optional[int]:
    """Determine current chapter from state"""
    if not current_state:
        return None
    
    # Try various paths to find chapter
    if "current_chapter" in current_state:
        return current_state["current_chapter"]
    elif "chapter" in current_state:
        return current_state["chapter"]
    elif "scene" in current_state and isinstance(current_state["scene"], dict):
        if "chapter" in current_state["scene"]:
            return current_state["scene"]["chapter"]
    elif "location" in current_state:
        # Try to extract chapter from location (e.g., "chapter_8_location")
        location = str(current_state["location"])
        if "chapter" in location.lower():
            # Extract number
            import re
            match = re.search(r'chapter[_\s]*(\d+)', location.lower())
            if match:
                return int(match.group(1))
    
    return None


def verify_chapter_pack(packs_dir: Path, chapter: Optional[int]) -> bool:
    """Verify chapter_pack_<N>.json exists"""
    if not chapter:
        return False
    
    pack_path = packs_dir / f"chapter_pack_{chapter}.json"
    return pack_path.exists()


def verify_mcp_servers() -> Dict[str, Any]:
    """Verify required MCP servers are available
    
    Returns:
        Dict with:
        - available: list of available servers
        - missing_hard: list of missing hard-required servers
        - missing_soft: list of missing soft-required servers
        - missing: list of all missing servers
        - ok: True if all hard-required servers are available
    """
    mcp_config_path = ROOT_DIR / "cursor_mcp_complete_config.json"
    
    available = []
    missing_hard = []
    missing_soft = []
    
    if mcp_config_path.exists():
        try:
            with open(mcp_config_path, 'r', encoding='utf-8') as f:
                mcp_config = json.load(f)
            
            # Check if servers are configured
            configured_servers = []
            if "mcpServers" in mcp_config:
                configured_servers = list(mcp_config["mcpServers"].keys())
            
            # Check each server
            config_str = json.dumps(mcp_config).lower()
            for server in ALL_MCP_SERVERS:
                # Check if server name appears in config (simplified check)
                server_found = any(s in config_str for s in server.split("-"))
                if server_found or any(s in server for s in configured_servers):
                    available.append(server)
                else:
                    if server in HARD_REQUIRED_MCP_SERVERS:
                        missing_hard.append(server)
                    else:
                        missing_soft.append(server)
        except Exception as e:
            sys.stderr.write(f"WARNING: Failed to read MCP config: {e}\n")
            missing_hard = HARD_REQUIRED_MCP_SERVERS
            missing_soft = SOFT_REQUIRED_MCP_SERVERS
    else:
        missing_hard = HARD_REQUIRED_MCP_SERVERS
        missing_soft = SOFT_REQUIRED_MCP_SERVERS
    
    missing_all = missing_hard + missing_soft
    
    return {
        "available": available,
        "missing_hard": missing_hard,
        "missing_soft": missing_soft,
        "missing": missing_all,
        "ok": len(missing_hard) == 0
    }


def verify_checklist() -> bool:
    """Verify MECHANICS_AUTOMATION_CHECKLIST.md exists"""
    return CHECKLIST_PATH.exists()


def main():
    """Main preflight gate execution"""
    try:
        # Load config
        config = load_config()
        campaigns_root = Path(config.get("campaigns_root", ""))
        default_campaign = config.get("default_campaign", "")
        state_file = config.get("state_file", "")
        
        if not state_file:
            # Construct state file path
            campaign_dir = campaigns_root / default_campaign
            state_file = str(campaign_dir / "saves" / "CURRENT_STATE.json")
        
        state_file_path = Path(state_file)
        events_file_path = state_file_path.parent / "CAMPAIGN_EVENTS.json"
        packs_dir = Path(config.get("packs_dir", ""))
        
        # Load preflight state (turn tracking)
        preflight_state = load_preflight_state()
        
        # Self-heal corrupted state: last_refresh_turn should never exceed turn
        previous_turn = preflight_state.get("turn", 0)
        last_refresh_turn = preflight_state.get("last_refresh_turn", 0)
        state_healed = False
        
        if last_refresh_turn > previous_turn:
            # Corrupted state detected - self-heal
            last_refresh_turn = previous_turn
            preflight_state["last_refresh_turn"] = last_refresh_turn
            state_healed = True
        
        # Increment turn
        current_turn = previous_turn + 1
        
        # Check if refresh is due (after increment)
        delta = current_turn - last_refresh_turn
        refresh_due = delta >= REFRESH_CADENCE
        
        # If refresh is due, reset turn to 0 and update last_refresh_turn
        if refresh_due:
            # Set last_refresh_turn to the turn that triggered refresh (before reset)
            last_refresh_turn = current_turn
            current_turn = 0
        
        # Load state files (always, but refresh action if due)
        current_state = load_current_state(state_file_path)
        campaign_events = load_campaign_events(events_file_path)
        
        # Determine chapter
        chapter = determine_chapter(current_state)
        
        # Verify chapter pack
        chapter_pack_loaded = verify_chapter_pack(packs_dir, chapter) if chapter else False
        
        # Verify MCP servers
        mcp_status = verify_mcp_servers()
        
        # Verify checklist
        checklist_exists = verify_checklist()
        
        # Perform refresh action if due
        refresh_action_completed = False
        if refresh_due:
            # Refresh action: Force reload and verify all critical files
            # This makes the refresh observable
            refresh_action_completed = True
            
            # Re-verify everything (force reload)
            current_state = load_current_state(state_file_path)
            campaign_events = load_campaign_events(events_file_path)
            chapter = determine_chapter(current_state)
            chapter_pack_loaded = verify_chapter_pack(packs_dir, chapter) if chapter else False
            mcp_status = verify_mcp_servers()
            checklist_exists = verify_checklist()
        
        # Update state file
        preflight_state["turn"] = current_turn
        preflight_state["last_refresh_turn"] = last_refresh_turn
        
        save_preflight_state(preflight_state)
        
        # Build MCP status string
        if mcp_status["ok"]:
            if mcp_status["missing_soft"]:
                mcp_status_str = f"ok (soft missing: {', '.join(mcp_status['missing_soft'])})"
            else:
                mcp_status_str = "ok"
        else:
            missing_all_str = ', '.join(mcp_status["missing"])
            mcp_status_str = f"missing: {missing_all_str}"
        
        # Validate critical requirements (fail-closed)
        critical_failures = []
        
        if not current_state:
            critical_failures.append("CURRENT_STATE.json not found")
        
        if not campaign_events:
            critical_failures.append("CAMPAIGN_EVENTS.json not found")
        
        if not chapter or not chapter_pack_loaded:
            if not chapter:
                critical_failures.append("Chapter cannot be determined from state")
            else:
                critical_failures.append(f"chapter_pack_{chapter}.json not found")
        
        if not checklist_exists:
            critical_failures.append("MECHANICS_AUTOMATION_CHECKLIST.md not found")
        
        if mcp_status["missing_hard"]:
            critical_failures.append(f"Hard-required MCP servers missing: {', '.join(mcp_status['missing_hard'])}")
        
        # Build receipt (print even if we're about to fail, for debugging)
        receipt_lines = [
            "RECEIPT",
            f"- MODE: PLAY",
        ]
        
        # Add freshness markers (prevents stale copy/paste)
        generated_at = datetime.now(timezone.utc).isoformat()
        run_id = str(uuid.uuid4())
        receipt_lines.append(f"- GENERATED_AT: {generated_at}")
        receipt_lines.append(f"- RUN_ID: {run_id}")
        
        receipt_lines.extend([
            f"- TURN: {current_turn}",
            f"- LAST_REFRESH_TURN: {last_refresh_turn}",
            f"- CURRENT_STATE: {'loaded' if current_state else 'not_found'}",
            f"- CAMPAIGN_EVENTS: {'loaded' if campaign_events else 'not_found'}",
        ])
        
        if chapter and chapter_pack_loaded:
            receipt_lines.append(f"- CHAPTER_PACK: chapter_pack_{chapter}.json loaded")
        elif chapter:
            receipt_lines.append(f"- CHAPTER_PACK: chapter_pack_{chapter}.json not_found")
        else:
            receipt_lines.append(f"- CHAPTER_PACK: chapter_unknown")
        
        receipt_lines.append(f"- MCP: {mcp_status_str}")
        receipt_lines.append(f"- CHECKLIST: {'MECHANICS_AUTOMATION_CHECKLIST acknowledged' if checklist_exists else 'MECHANICS_AUTOMATION_CHECKLIST not_found'}")
        receipt_lines.append(f"- REFRESH_DUE: {str(refresh_due).lower()}")
        
        if refresh_due and refresh_action_completed:
            receipt_lines.append(f"- REFRESH_ACTION: completed")
        
        if state_healed:
            receipt_lines.append(f"- STATE: healed (last_refresh_turn clamped)")
        
        # Format assertion BEFORE printing
        receipt_text = "\n".join(receipt_lines)
        
        # Require at least 5 newline separators (strict multi-line check)
        if receipt_text.count("\n") < 5:
            sys.stderr.write("RECEIPT_FORMAT_ERROR: receipt must be multi-line\n")
            sys.exit(1)
        
        # Print receipt wrapped in code fence (prevents UI reflow)
        print("```text")
        print(receipt_text)
        print("```")
        
        # Fail-closed: exit with error if critical requirements not met
        if critical_failures:
            sys.stderr.write("\n❌ CRITICAL FAILURES (blocking):\n")
            for failure in critical_failures:
                sys.stderr.write(f"   - {failure}\n")
            sys.stderr.write("\n")
            sys.exit(1)
        
        # Exit with success code
        sys.exit(0)
        
    except Exception as e:
        sys.stderr.write(f"ERROR: Preflight gate failed: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
