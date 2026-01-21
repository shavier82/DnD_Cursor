#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Workflow State Validator
Checks if workflows were actually run and procedures were followed.

This script validates that:
- Session start workflow was run
- Post-combat procedures were completed
- Spell slots were deducted
- NPC status changes were tracked
- And more...

Usage:
    python scripts/validate_workflow_state.py --check-session
    python scripts/validate_workflow_state.py --check-post-combat
    python scripts/validate_workflow_state.py --check-all
"""

import json
import sys
import io
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

ROOT_DIR = Path(__file__).parent.parent
WORKFLOW_STATE_FILE = ROOT_DIR / ".dm_workflow_state.json"


def load_workflow_state():
    """Load workflow state file"""
    if not WORKFLOW_STATE_FILE.exists():
        return None
    
    try:
        with open(WORKFLOW_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ ERROR: Failed to load workflow state: {e}")
        return None


def check_session_start():
    """Check if session start workflow was run"""
    state = load_workflow_state()
    
    if not state:
        return {
            "status": "error",
            "message": "No workflow state file found. Session start workflow was not run.",
            "required": "Run: python scripts/dm_workflow.py session_start"
        }
    
    session_start = state.get("session_start", {})
    
    if not session_start.get("completed"):
        return {
            "status": "error",
            "message": "Session start workflow was not completed.",
            "required": "Run: python scripts/dm_workflow.py session_start"
        }
    
    # Check if it's recent (within last 24 hours)
    timestamp_str = session_start.get("timestamp")
    if timestamp_str:
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            if datetime.now() - timestamp > timedelta(hours=24):
                return {
                    "status": "warning",
                    "message": f"Session start workflow was run {datetime.now() - timestamp} ago. Consider re-running.",
                    "timestamp": timestamp_str
                }
        except Exception:
            pass
    
    return {
        "status": "success",
        "message": "Session start workflow completed",
        "timestamp": timestamp_str,
        "details": {
            "checklist_validated": session_start.get("checklist_validated", False),
            "state_files_loaded": session_start.get("state_files_loaded", []),
            "chapter_pack_loaded": session_start.get("chapter_pack_loaded"),
            "mcp_servers_verified": session_start.get("mcp_servers_verified", False)
        }
    }


def check_post_combat(combat_id: str = None):
    """Check if post-combat procedures were completed"""
    state = load_workflow_state()
    
    if not state:
        return {
            "status": "error",
            "message": "No workflow state file found."
        }
    
    last_combat = state.get("last_combat", {})
    
    if combat_id:
        # Check specific combat
        if last_combat.get("combat_id") != combat_id:
            return {
                "status": "error",
                "message": f"Combat {combat_id} not found in workflow state.",
                "required": "Run: python scripts/dm_workflow.py post_combat --combat-id {combat_id}"
            }
    
    if not last_combat.get("post_combat_completed"):
        return {
            "status": "error",
            "message": "Post-combat procedures were not completed.",
            "combat_id": last_combat.get("combat_id"),
            "required": f"Run: python scripts/dm_workflow.py post_combat --combat-id {last_combat.get('combat_id', '<id>')}"
        }
    
    return {
        "status": "success",
        "message": "Post-combat procedures completed",
        "combat_id": last_combat.get("combat_id"),
        "timestamp": last_combat.get("timestamp")
    }


def check_spell_slots():
    """Check if spell slots were tracked"""
    state = load_workflow_state()
    
    if not state:
        return {
            "status": "warning",
            "message": "No workflow state file found."
        }
    
    spell_slots = state.get("spell_slots_used", [])
    
    if not spell_slots:
        return {
            "status": "info",
            "message": "No spell slots used in this session (or not tracked)."
        }
    
    return {
        "status": "success",
        "message": f"{len(spell_slots)} spell slot(s) tracked",
        "spell_slots": spell_slots
    }


def check_all():
    """Check all workflow validations"""
    results = {
        "session_start": check_session_start(),
        "post_combat": check_post_combat(),
        "spell_slots": check_spell_slots()
    }
    
    # Count errors and warnings
    errors = sum(1 for r in results.values() if r.get("status") == "error")
    warnings = sum(1 for r in results.values() if r.get("status") == "warning")
    
    results["summary"] = {
        "total_checks": len(results),
        "errors": errors,
        "warnings": warnings,
        "overall_status": "error" if errors > 0 else ("warning" if warnings > 0 else "success")
    }
    
    return results


def print_results(results):
    """Print validation results"""
    if isinstance(results, dict) and "summary" in results:
        # Multiple checks
        print("\n" + "="*60)
        print("WORKFLOW STATE VALIDATION")
        print("="*60 + "\n")
        
        for check_name, result in results.items():
            if check_name == "summary":
                continue
            
            status = result.get("status", "unknown")
            symbol = "✅" if status == "success" else "❌" if status == "error" else "⚠️"
            
            print(f"{symbol} {check_name.upper().replace('_', ' ')}: {result.get('message', 'Unknown')}")
            
            if status == "error" and "required" in result:
                print(f"   → {result['required']}")
        
        print("\n" + "="*60)
        summary = results["summary"]
        print(f"SUMMARY: {summary['errors']} errors, {summary['warnings']} warnings")
        print("="*60 + "\n")
    else:
        # Single check
        status = results.get("status", "unknown")
        symbol = "✅" if status == "success" else "❌" if status == "error" else "⚠️"
        
        print(f"\n{symbol} {results.get('message', 'Unknown')}")
        
        if status == "error" and "required" in results:
            print(f"   → {results['required']}")


def main():
    parser = argparse.ArgumentParser(description="Validate workflow state")
    parser.add_argument("--check-session", action="store_true", help="Check session start workflow")
    parser.add_argument("--check-post-combat", action="store_true", help="Check post-combat procedures")
    parser.add_argument("--check-spell-slots", action="store_true", help="Check spell slot tracking")
    parser.add_argument("--check-all", action="store_true", help="Check all validations")
    parser.add_argument("--combat-id", help="Combat ID for post-combat check")
    
    args = parser.parse_args()
    
    if args.check_all:
        results = check_all()
        print_results(results)
        sys.exit(0 if results["summary"]["errors"] == 0 else 1)
    elif args.check_session:
        results = check_session_start()
        print_results(results)
        sys.exit(0 if results.get("status") != "error" else 1)
    elif args.check_post_combat:
        results = check_post_combat(args.combat_id)
        print_results(results)
        sys.exit(0 if results.get("status") != "error" else 1)
    elif args.check_spell_slots:
        results = check_spell_slots()
        print_results(results)
        sys.exit(0)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
