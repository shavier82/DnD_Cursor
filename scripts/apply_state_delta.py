#!/usr/bin/env python3
"""
Apply State Delta - Automatically update resources_state.json based on STATE-DELTA block.

Parses STATE-DELTA block from DM response and applies the changes to resources_state.json,
creating a backup before modification.

Usage:
    echo "response text" | python scripts/apply_state_delta.py
    python scripts/apply_state_delta.py --text "response text"
    python scripts/apply_state_delta.py --dry-run  # Preview changes without applying
"""

import argparse
import json
import re
import sys
import shutil
from pathlib import Path
from typing import Dict, Any, Tuple
from datetime import datetime

# Import shared normalizer
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from text_normalize import normalize_input_text

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_RESOURCES_FILE = ROOT_DIR / "scripts" / "resources_state.json"

DELTA_BLOCK_PAT = re.compile(r"STATE-DELTA\s*(?P<body>.*?)\s*END STATE-DELTA", re.IGNORECASE | re.DOTALL)
DELTA_LINE_PAT = re.compile(
    r"^\s*-\s*(?P<actor>[a-zA-Z0-9_\-]+)\s*:\s*(?P<key>[a-zA-Z0-9_\.\-]+)\s*-\=\s*(?P<amt>\d+)\s*$",
    re.IGNORECASE,
)

def load_resources(path: Path) -> Dict[str, Any]:
    """Load resources state file."""
    if not path.exists():
        print(f"ERROR: resources file not found: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: invalid resources JSON: {e}", file=sys.stderr)
        sys.exit(1)

def save_resources(path: Path, data: Dict[str, Any]) -> None:
    """Save resources state file."""
    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except Exception as e:
        print(f"ERROR: failed to save resources file: {e}", file=sys.stderr)
        sys.exit(1)

def create_backup(path: Path) -> Path:
    """Create a backup copy of the resources file in a deterministic folder.

    Folder: scripts/backups/resources_state/
    Name:   resources_state.YYYYMMDD_HHMMSS.json
    """
    # path should be scripts/resources_state.json
    backup_dir = path.parent / "backups" / "resources_state"
    backup_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"resources_state.{ts}.json"
    shutil.copy2(path, backup_path)
    return backup_path

def parse_delta(text: str) -> Dict[Tuple[str, str, int], int]:
    """Parse STATE-DELTA block from text.
    
    Returns dict mapping (actor, resource, level) -> amount to subtract.
    """
    m = DELTA_BLOCK_PAT.search(text)
    if not m:
        return {}
    body = m.group("body")
    deltas: Dict[Tuple[str, str, int], int] = {}
    for line in body.splitlines():
        line = line.rstrip()
        if not line.strip():
            continue
        m2 = DELTA_LINE_PAT.match(line)
        if not m2:
            # Invalid format - skip (resource_guard.py would have caught this)
            continue
        actor = m2.group("actor")
        key = m2.group("key").lower()
        amt = int(m2.group("amt"))

        # key supports: spell_slot.2 or rage, ki, etc.
        if key.startswith("spell_slot."):
            level = int(key.split(".", 1)[1])
            k = (actor, "spell_slot", level)
        else:
            k = (actor, key, 0)

        deltas[k] = deltas.get(k, 0) + amt
    return deltas

def apply_delta(resources: Dict[str, Any], deltas: Dict[Tuple[str, str, int], int], dry_run: bool = False) -> Dict[str, Any]:
    """Apply deltas to resources state.
    
    Returns updated resources dict.
    """
    updated = json.loads(json.dumps(resources))  # Deep copy
    
    for (actor, res, level), amount in deltas.items():
        if actor not in updated:
            # Actor doesn't exist - create entry
            if not dry_run:
                updated[actor] = {
                    "spell_slots": {},
                    "rage": 0,
                    "superiority_die": 0,
                    "ki": 0,
                    "channel_divinity": 0,
                    "bardic_inspiration": 0,
                    "sorcery_point": 0,
                    "wild_shape": 0,
                    "maneuver": 0
                }
            else:
                print(f"DRY-RUN: Would create actor {actor}")
        
        actor_obj = updated[actor]
        
        if res == "spell_slot":
            if "spell_slots" not in actor_obj:
                actor_obj["spell_slots"] = {}
            level_str = str(level)
            current = actor_obj["spell_slots"].get(level_str, 0)
            new_value = max(0, current - amount)  # Prevent negative
            
            if dry_run:
                print(f"DRY-RUN: {actor} spell_slot.{level}: {current} -> {new_value} (subtract {amount})")
            else:
                actor_obj["spell_slots"][level_str] = new_value
        else:
            current = actor_obj.get(res, 0)
            new_value = max(0, current - amount)  # Prevent negative
            
            if dry_run:
                print(f"DRY-RUN: {actor} {res}: {current} -> {new_value} (subtract {amount})")
            else:
                actor_obj[res] = new_value
    
    return updated

def main():
    ap = argparse.ArgumentParser(description="Apply STATE-DELTA changes to resources_state.json")
    ap.add_argument("--resources", default=str(DEFAULT_RESOURCES_FILE), help="Path to resources_state.json")
    ap.add_argument("--text", default=None, help="Response text (if omitted, read stdin)")
    ap.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    ap.add_argument("--no-backup", action="store_true", help="Skip creating backup file")
    args = ap.parse_args()

    text = args.text if args.text is not None else sys.stdin.read()
    if not text.strip():
        print("ERROR: No text provided", file=sys.stderr)
        sys.exit(1)

    # Normalize input to strip transcript prefixes
    text = normalize_input_text(text)

    resources_path = Path(args.resources)
    resources = load_resources(resources_path)
    
    deltas = parse_delta(text)
    
    if not deltas:
        # No STATE-DELTA block - nothing to apply
        # Silent unless verbose or dry-run
        if args.dry_run:
            print("DRY-RUN: No STATE-DELTA block found, nothing to apply")
        sys.exit(0)
    
    # Apply deltas
    updated = apply_delta(resources, deltas, dry_run=args.dry_run)
    
    if args.dry_run:
        print("\nDRY-RUN: Changes previewed above. Run without --dry-run to apply.")
        sys.exit(0)
    
    # Create backup unless --no-backup
    if not args.no_backup:
        backup_path = create_backup(resources_path)
        # Silent unless verbose (backup info only printed in verbose mode via dm_workflow)
    
    # Save updated resources
    save_resources(resources_path, updated)
    # Silent unless verbose (update info only printed in verbose mode via dm_workflow)
    sys.exit(0)

if __name__ == "__main__":
    main()
