#!/usr/bin/env python3
"""
Apply Quest Delta - Automatically update quests_state.json based on QUEST-DELTA block.

Parses QUEST-DELTA block from DM response and applies the changes to quests_state.json,
creating a backup before modification.

Usage:
    echo "response text" | python scripts/apply_quest_delta.py
    python scripts/apply_quest_delta.py --text "response text"
    python scripts/apply_quest_delta.py --dry-run  # Preview changes without applying
"""

import argparse
import json
import os
import re
import sys
import shutil
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Import shared normalizer
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from text_normalize import normalize_input_text

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_QUESTS_FILE = ROOT_DIR / "scripts" / "quests_state.json"

DELTA_BLOCK_PAT = re.compile(r"QUEST-DELTA\s*(?P<body>.*?)\s*END QUEST-DELTA", re.IGNORECASE | re.DOTALL)
DELTA_LINE_PAT = re.compile(
    r"^\s*-\s*(?P<action>complete|fail|accept|activate|deactivate)\s*:\s*(?P<quest_id>[a-zA-Z0-9_\-]+)\s*(?:#\s*(?P<note>.*?))?\s*$",
    re.IGNORECASE,
)

def load_quests(path: Path) -> Dict[str, Any]:
    """Load quests state file. Auto-creates from template if missing."""
    if not path.exists():
        # Try to bootstrap from template
        template_path = path.parent / "quests_state.template.json"
        if template_path.exists():
            try:
                # Try utf-8-sig first (handles BOM), fallback to utf-8
                try:
                    template_data = json.loads(template_path.read_text(encoding="utf-8-sig"))
                except Exception:
                    template_data = json.loads(template_path.read_text(encoding="utf-8"))
                # Create the runtime file from template
                save_quests(path, template_data)
                return template_data
            except Exception as e:
                print(f"WARNING: Failed to bootstrap from template: {e}", file=sys.stderr)
        # Fallback to default structure if template missing
        default_data = {"completed": [], "active": [], "notes": {}}
        save_quests(path, default_data)
        return default_data
    try:
        # Try utf-8-sig first (handles BOM), fallback to utf-8
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        # Corruption recovery: try to restore from backup, then bootstrap
        print(f"WARNING: invalid quests JSON: {e}", file=sys.stderr)
        # Try to find and restore from most recent backup
        backup_dir = path.parent / "backups" / "quests_state"
        if backup_dir.exists():
            backups = sorted(backup_dir.glob("quests_state.*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
            if backups:
                try:
                    # Try utf-8-sig first (handles BOM), fallback to utf-8
                    try:
                        backup_data = json.loads(backups[0].read_text(encoding="utf-8-sig"))
                    except Exception:
                        backup_data = json.loads(backups[0].read_text(encoding="utf-8"))
                    # Rename corrupted file for inspection
                    corrupt_path = path.parent / f"quests_state.corrupt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    try:
                        shutil.move(str(path), str(corrupt_path))
                    except Exception:
                        pass  # If move fails, continue anyway
                    # Restore from backup
                    save_quests(path, backup_data)
                    print(f"INFO: Restored quests_state.json from backup: {backups[0].name}", file=sys.stderr)
                    return backup_data
                except Exception as restore_err:
                    print(f"WARNING: Failed to restore from backup: {restore_err}", file=sys.stderr)
        # If backup restore failed, bootstrap from template
        template_path = path.parent / "quests_state.template.json"
        if template_path.exists():
            try:
                try:
                    template_data = json.loads(template_path.read_text(encoding="utf-8-sig"))
                except Exception:
                    template_data = json.loads(template_path.read_text(encoding="utf-8"))
                # Rename corrupted file if it still exists
                if path.exists():
                    corrupt_path = path.parent / f"quests_state.corrupt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    try:
                        shutil.move(str(path), str(corrupt_path))
                    except Exception:
                        pass
                save_quests(path, template_data)
                print(f"INFO: Bootstrapped quests_state.json from template after corruption", file=sys.stderr)
                return template_data
            except Exception as bootstrap_err:
                print(f"WARNING: Failed to bootstrap from template: {bootstrap_err}", file=sys.stderr)
        # Final fallback: default structure
        default_data = {"completed": [], "active": [], "notes": {}}
        if path.exists():
            corrupt_path = path.parent / f"quests_state.corrupt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                shutil.move(str(path), str(corrupt_path))
            except Exception:
                pass
        save_quests(path, default_data)
        print(f"WARNING: Using default quest state after corruption recovery failed", file=sys.stderr)
        return default_data

def save_quests(path: Path, data: Dict[str, Any]) -> None:
    """Save quests state file using atomic write (prevents corruption on partial writes)."""
    try:
        # Atomic write: write to temp file, then replace atomically
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        tmp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        # Atomic replace (works on Windows too)
        os.replace(tmp_path, path)
    except Exception as e:
        # Clean up temp file if it exists
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass
        print(f"ERROR: failed to save quests file: {e}", file=sys.stderr)
        sys.exit(1)

def create_backup(path: Path) -> Path:
    """Create a backup copy of the quests file in a deterministic folder.

    Folder: scripts/backups/quests_state/
    Name:   quests_state.YYYYMMDD_HHMMSS.json
    """
    backup_dir = path.parent / "backups" / "quests_state"
    backup_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"quests_state.{ts}.json"
    shutil.copy2(path, backup_path)
    return backup_path

def parse_delta(text: str) -> tuple[Dict[str, str], Dict[str, str]]:
    """Parse QUEST-DELTA block from text.
    
    Returns tuple of (deltas, notes):
    - deltas: dict mapping quest_id -> action (complete, fail, accept, activate, deactivate)
    - notes: dict mapping quest_id -> note text (optional, only if # note provided)
    """
    m = DELTA_BLOCK_PAT.search(text)
    if not m:
        return {}, {}
    body = m.group("body")
    deltas: Dict[str, str] = {}
    notes: Dict[str, str] = {}
    for line in body.splitlines():
        line = line.rstrip()
        if not line.strip():
            continue
        m2 = DELTA_LINE_PAT.match(line)
        if not m2:
            # Invalid format - skip (quest_guard.py would have caught this)
            continue
        action = m2.group("action").lower()
        quest_id = m2.group("quest_id").lower().strip()
        note = m2.group("note")
        deltas[quest_id] = action
        if note:
            notes[quest_id] = note.strip()
    return deltas, notes

def apply_delta(quests: Dict[str, Any], deltas: Dict[str, str], notes: Dict[str, str], dry_run: bool = False) -> Dict[str, Any]:
    """Apply deltas to quests state.
    
    Returns updated quests dict.
    """
    updated = json.loads(json.dumps(quests))  # Deep copy
    
    # Ensure required keys exist
    if "completed" not in updated:
        updated["completed"] = []
    if "active" not in updated:
        updated["active"] = []
    if "notes" not in updated:
        updated["notes"] = {}
    
    completed = [q.lower() for q in updated["completed"]]
    active = [q.lower() for q in updated["active"]]
    
    for quest_id, action in deltas.items():
        # Normalize quest_id for consistent storage (lowercase + strip)
        quest_id_normalized = quest_id.lower().strip()
        quest_id_lower = quest_id_normalized
        
        if action == "complete":
            # Move from active to completed (if in active), or add to completed
            if quest_id_lower in active:
                updated["active"] = [q for q in updated["active"] if q.lower() != quest_id_lower]
                if dry_run:
                    print(f"DRY-RUN: Quest '{quest_id_normalized}' moved from active to completed")
            if quest_id_lower not in completed:
                updated["completed"].append(quest_id_normalized)
                if dry_run:
                    print(f"DRY-RUN: Quest '{quest_id_normalized}' added to completed")
            # Add optional note if provided (only if different from existing)
            if quest_id_normalized in notes:
                if "notes" not in updated:
                    updated["notes"] = {}
                existing = updated["notes"].get(quest_id_normalized, "")
                new_note = notes[quest_id_normalized]
                # Only append if note is different and not already present
                if existing and new_note not in existing:
                    updated["notes"][quest_id_normalized] = f"{existing}; {new_note}"
                elif not existing:
                    updated["notes"][quest_id_normalized] = new_note
        
        elif action == "fail":
            # Move from active to completed (marked as failed), or add to completed
            if quest_id_lower in active:
                updated["active"] = [q for q in updated["active"] if q.lower() != quest_id_lower]
                if dry_run:
                    print(f"DRY-RUN: Quest '{quest_id_normalized}' moved from active to completed (failed)")
            if quest_id_lower not in completed:
                updated["completed"].append(quest_id_normalized)
                if dry_run:
                    print(f"DRY-RUN: Quest '{quest_id_normalized}' added to completed (failed)")
            # Add note about failure (always) + optional note if provided
            if "notes" not in updated:
                updated["notes"] = {}
            existing = updated["notes"].get(quest_id_normalized, "")
            fail_marker = " (Failed)"
            if quest_id_normalized in notes:
                custom_note = notes[quest_id_normalized]
                updated["notes"][quest_id_normalized] = f"{existing}{fail_marker}; {custom_note}" if existing else f"{fail_marker}; {custom_note}"
            else:
                updated["notes"][quest_id_normalized] = existing + fail_marker if existing else fail_marker
        
        elif action == "accept":
            # Add to active if not already there
            if quest_id_lower not in active and quest_id_lower not in completed:
                updated["active"].append(quest_id_normalized)
                if dry_run:
                    print(f"DRY-RUN: Quest '{quest_id_normalized}' added to active")
            # Add optional note if provided (only if different from existing)
            if quest_id_normalized in notes:
                if "notes" not in updated:
                    updated["notes"] = {}
                existing = updated["notes"].get(quest_id_normalized, "")
                new_note = notes[quest_id_normalized]
                # Only append if note is different and not already present
                if existing and new_note not in existing:
                    updated["notes"][quest_id_normalized] = f"{existing}; {new_note}"
                elif not existing:
                    updated["notes"][quest_id_normalized] = new_note
        
        elif action == "activate":
            # Add to active if not already there
            if quest_id_lower not in active and quest_id_lower not in completed:
                updated["active"].append(quest_id_normalized)
                if dry_run:
                    print(f"DRY-RUN: Quest '{quest_id_normalized}' added to active")
            # Add optional note if provided (only if different from existing)
            if quest_id_normalized in notes:
                if "notes" not in updated:
                    updated["notes"] = {}
                existing = updated["notes"].get(quest_id_normalized, "")
                new_note = notes[quest_id_normalized]
                # Only append if note is different and not already present
                if existing and new_note not in existing:
                    updated["notes"][quest_id_normalized] = f"{existing}; {new_note}"
                elif not existing:
                    updated["notes"][quest_id_normalized] = new_note
        
        elif action == "deactivate":
            # Remove from active
            if quest_id_lower in active:
                updated["active"] = [q for q in updated["active"] if q.lower() != quest_id_lower]
                if dry_run:
                    print(f"DRY-RUN: Quest '{quest_id_normalized}' removed from active")
            # Add optional note if provided (only if different from existing)
            if quest_id_normalized in notes:
                if "notes" not in updated:
                    updated["notes"] = {}
                existing = updated["notes"].get(quest_id_normalized, "")
                new_note = notes[quest_id_normalized]
                # Only append if note is different and not already present
                if existing and new_note not in existing:
                    updated["notes"][quest_id_normalized] = f"{existing}; {new_note}"
                elif not existing:
                    updated["notes"][quest_id_normalized] = new_note
    
    return updated

def main():
    ap = argparse.ArgumentParser(description="Apply QUEST-DELTA changes to quests_state.json")
    ap.add_argument("--quests", default=str(DEFAULT_QUESTS_FILE), help="Path to quests_state.json")
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

    quests_path = Path(args.quests)
    quests = load_quests(quests_path)
    
    deltas, notes = parse_delta(text)
    
    if not deltas:
        # No QUEST-DELTA block - nothing to apply
        # Silent unless verbose or dry-run
        if args.dry_run:
            print("DRY-RUN: No QUEST-DELTA block found, nothing to apply")
        sys.exit(0)
    
    # Apply deltas (with optional notes)
    updated = apply_delta(quests, deltas, notes, dry_run=args.dry_run)
    
    if args.dry_run:
        print("\nDRY-RUN: Changes previewed above. Run without --dry-run to apply.")
        sys.exit(0)
    
    # Create backup unless --no-backup
    if not args.no_backup:
        backup_path = create_backup(quests_path)
        # Silent unless verbose (backup info only printed in verbose mode via dm_workflow)
    
    # Save updated quests
    save_quests(quests_path, updated)
    # Silent unless verbose (update info only printed in verbose mode via dm_workflow)
    sys.exit(0)

if __name__ == "__main__":
    main()
