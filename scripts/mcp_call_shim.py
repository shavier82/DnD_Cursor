#!/usr/bin/env python3
"""
MCP Call Shim - Calls Obsidian MCP server code from standalone scripts.

ARCHITECTURE NOTE: This script imports ObsidianSyncServer directly and invokes methods
in-process. This is "shared server code invoked locally," NOT true MCP transport.

For true MCP-only (JSON-RPC over stdio), you would need to:
1. Spawn/connect to the MCP server process
2. Send JSON-RPC tool call messages
3. Parse JSON-RPC responses

This approach is simpler and uses the same code as the MCP server, but bypasses
the MCP transport layer. The write_vault_file tool writes a provenance marker
(resources_state.sync_meta.json) to prove the sync occurred.

Usage:
    echo '{"tool": "read_vault_file", "args": {"file_path": "DnD/state/resources_state.json"}}' | python scripts/mcp_call_shim.py
    
    echo '{"tool": "write_vault_file", "args": {"file_path": "DnD/state/resources_state.json", "content": "..."}}' | python scripts/mcp_call_shim.py
"""

import json
import sys
from pathlib import Path

# Add mcp_servers to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from mcp_servers.obsidian_sync.obsidian_sync_server import ObsidianSyncServer
except ImportError as e:
    print(f"ERROR: Failed to import ObsidianSyncServer: {e}", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    """Call MCP tool and return JSON result."""
    payload_text = sys.stdin.read()
    if not payload_text.strip():
        print("ERROR: No MCP payload provided on stdin.", file=sys.stderr)
        return 1
    
    try:
        payload = json.loads(payload_text)
    except Exception as e:
        print(f"ERROR: Invalid JSON payload: {e}", file=sys.stderr)
        return 1
    
    tool = payload.get("tool")
    args = payload.get("args", {})
    
    if not tool:
        print("ERROR: Missing 'tool' field in payload.", file=sys.stderr)
        return 1
    
    # Initialize server (same as MCP server uses)
    server = ObsidianSyncServer()
    
    # Call tool method
    try:
        if tool == "read_vault_file":
            result = server.read_vault_file(args.get("file_path", ""))
        elif tool == "write_vault_file":
            result = server.write_vault_file(
                args.get("file_path", ""),
                args.get("content", "")
            )
        else:
            print(f"ERROR: Unknown tool: {tool}", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"ERROR: Tool call failed: {e}", file=sys.stderr)
        return 1
    
    # Echo result JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
