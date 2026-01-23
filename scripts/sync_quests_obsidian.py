#!/usr/bin/env python3
"""
Sync quests_state.json to Obsidian vault with SHA verification (MCP-only).

This script:
1. Reads local quests_state.json (staging copy)
2. Writes to Obsidian vault via MCP (authoritative copy)
3. Reads back from Obsidian vault via MCP
4. Verifies SHA256 matches
5. If verification fails → BLOCKED

This ensures Obsidian is always the source of truth and sync failures are detected.
MCP-only: All Obsidian operations use MCP tools, no direct filesystem access.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
LOCAL_QUESTS = SCRIPTS / "quests_state.json"
MCP_SHIM = SCRIPTS / "mcp_call_shim.py"

QUESTS_FILE_PATH = "DnD/state/quests_state.json"

def sha256_text(s: str) -> str:
    """Calculate SHA256 hash of text."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def call_mcp_tool(tool: str, args: dict) -> dict:
    """Call an MCP tool via shim and return result."""
    payload = {"tool": tool, "args": args}
    
    try:
        proc = subprocess.run(
            [sys.executable, str(MCP_SHIM)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            encoding='utf-8'
        )
        
        if proc.returncode != 0:
            error_msg = proc.stderr.strip() or proc.stdout.strip() or "MCP call failed"
            raise RuntimeError(error_msg)
        
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"MCP shim returned invalid JSON: {e}")
    except Exception as e:
        raise RuntimeError(f"MCP tool call failed: {e}")

def main() -> int:
    """Sync quests to Obsidian via MCP and verify with SHA."""
    ap = argparse.ArgumentParser(description="Sync quests_state.json to Obsidian (MCP-only, SHA verified)")
    ap.add_argument("--verbose", action="store_true", help="Print OK on success")
    args = ap.parse_args()
    verbose = args.verbose

    if not LOCAL_QUESTS.exists():
        print(f"ERROR: Missing local quests file: {LOCAL_QUESTS}", file=sys.stderr)
        return 1
    
    if not MCP_SHIM.exists():
        print(f"ERROR: Missing MCP shim: {MCP_SHIM}", file=sys.stderr)
        return 1
    
    # Read local staging copy
    try:
        local_content = LOCAL_QUESTS.read_text(encoding="utf-8")
    except Exception as e:
        print(f"ERROR: Failed to read local quests: {e}", file=sys.stderr)
        return 1
    
    # Calculate expected SHA
    wanted_sha = sha256_text(local_content)
    
    # Write to Obsidian vault via MCP
    try:
        write_result = call_mcp_tool("write_vault_file", {
            "file_path": QUESTS_FILE_PATH,
            "content": local_content
        })
        if not write_result.get("success"):
            error = write_result.get("error", "unknown error")
            print(f"BLOCKED: obsidian sync failed (write error): {error}", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"BLOCKED: obsidian sync failed (write error): {e}", file=sys.stderr)
        return 1
    
    # Read back from Obsidian vault via MCP
    try:
        read_result = call_mcp_tool("read_vault_file", {
            "file_path": QUESTS_FILE_PATH
        })
        if not read_result.get("success"):
            error = read_result.get("error", "unknown error")
            print(f"BLOCKED: obsidian sync failed (readback error): {error}", file=sys.stderr)
            return 1
        
        read_content = read_result.get("content")
        if not isinstance(read_content, str):
            print(f"BLOCKED: obsidian sync failed (readback returned non-string)", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"BLOCKED: obsidian sync failed (readback error): {e}", file=sys.stderr)
        return 1
    
    # Verify SHA matches
    got_sha = sha256_text(read_content)
    if got_sha != wanted_sha:
        print(f"BLOCKED: obsidian sync failed (sha mismatch) wanted={wanted_sha[:16]}... got={got_sha[:16]}...", file=sys.stderr)
        return 1
    
    # Verify provenance marker via MCP (proves sync went through MCP server code)
    # Read via MCP tool, not direct filesystem access
    try:
        provenance_result = call_mcp_tool("read_vault_file", {
            "file_path": "DnD/state/quests_state.sync_meta.json"
        })
        if not provenance_result.get("success"):
            error = provenance_result.get("error", "unknown error")
            print(f"BLOCKED: obsidian sync failed (provenance marker missing - sync may not have gone through MCP): {error}", file=sys.stderr)
            return 1
        
        provenance_content = provenance_result.get("content")
        if not isinstance(provenance_content, str):
            print(f"BLOCKED: obsidian sync failed (provenance marker invalid format)", file=sys.stderr)
            return 1
        
        provenance_data = json.loads(provenance_content)
        if provenance_data.get("_synced_via") != "mcp":
            print(f"BLOCKED: obsidian sync failed (invalid provenance marker - _synced_via != 'mcp')", file=sys.stderr)
            return 1
    except json.JSONDecodeError as e:
        print(f"BLOCKED: obsidian sync failed (provenance marker JSON parse error): {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"BLOCKED: obsidian sync failed (provenance check error): {e}", file=sys.stderr)
        return 1

    # Generate and sync dashboard markdown (non-fatal)
    render_script = SCRIPTS / "render_quests_dashboard.py"
    if render_script.exists():
        try:
            rp = subprocess.run(
                [sys.executable, str(render_script)],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            if rp.returncode == 0:
                md_content = rp.stdout
                dash = call_mcp_tool("write_vault_file", {
                    "file_path": "DnD/state/quests_state.md",
                    "content": md_content,
                })
                if not dash.get("success"):
                    err = dash.get("error", "unknown error")
                    if verbose:
                        print(f"WARNING: Dashboard sync failed (non-fatal): {err}", file=sys.stderr)
            else:
                err = (rp.stderr or rp.stdout or "").strip() or "unknown error"
                if verbose:
                    print(f"WARNING: Dashboard render failed (non-fatal): {err}", file=sys.stderr)
        except Exception as e:
            if verbose:
                print(f"WARNING: Dashboard sync error (non-fatal): {e}", file=sys.stderr)

    if verbose:
        print("OK: obsidian quest sync passed (SHA verified)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
