#!/usr/bin/env python3
"""
Quest Guard - Validates DM output for quest state enforcement (FAIL-CLOSED).

Uses deterministic tags only (no fuzzy text):
- [QUESTSTART <id>] / [QUESTOFFER <id>]: offering or starting a quest
- [QUESTCOMPLETE <id>], [QUESTFAIL <id>], [QUESTACCEPT <id>], [QUESTACTIVATE <id>]: state changes

Rules:
1. If [QUESTSTART <id>] or [QUESTOFFER <id>] and id is in completed → BLOCKED
2. Any state-change tag requires a matching QUEST-DELTA block

QUEST-DELTA format (exact):
  QUEST-DELTA
  - complete: <quest_id>
  - fail: <quest_id>
  - accept: <quest_id>
  - activate: <quest_id>
  - deactivate: <quest_id>
  END QUEST-DELTA

Reads scripts/quests_state.json (local mirror) every run.
"""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Set

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from text_normalize import normalize_input_text

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_QUESTS_FILE = ROOT_DIR / "scripts" / "quests_state.json"

# Deterministic tags: [QUESTSTART id], [QUESTOFFER id], [QUESTCOMPLETE id], etc.
TAG_PAT = re.compile(
    r"\[(?:QUESTSTART|QUESTOFFER|QUESTCOMPLETE|QUESTFAIL|QUESTACCEPT|QUESTACTIVATE)\s+([a-zA-Z0-9_\-]+)\s*\]",
    re.IGNORECASE,
)
QUEST_START_TAG = re.compile(r"\[(?:QUESTSTART|QUESTOFFER)\s+([a-zA-Z0-9_\-]+)\s*\]", re.IGNORECASE)
QUEST_COMPLETE_TAG = re.compile(r"\[QUESTCOMPLETE\s+([a-zA-Z0-9_\-]+)\s*\]", re.IGNORECASE)
QUEST_FAIL_TAG = re.compile(r"\[QUESTFAIL\s+([a-zA-Z0-9_\-]+)\s*\]", re.IGNORECASE)
QUEST_ACCEPT_TAG = re.compile(r"\[QUESTACCEPT\s+([a-zA-Z0-9_\-]+)\s*\]", re.IGNORECASE)
QUEST_ACTIVATE_TAG = re.compile(r"\[QUESTACTIVATE\s+([a-zA-Z0-9_\-]+)\s*\]", re.IGNORECASE)

DELTA_BLOCK_PAT = re.compile(r"QUEST-DELTA\s*(?P<body>.*?)\s*END QUEST-DELTA", re.IGNORECASE | re.DOTALL)
DELTA_LINE_PAT = re.compile(
    r"^\s*-\s*(?P<action>complete|fail|accept|activate|deactivate)\s*:\s*(?P<quest_id>[a-zA-Z0-9_\-]+)\s*(?:#\s*(?P<note>.*?))?\s*$",
    re.IGNORECASE,
)


def load_quests(path: Path) -> Dict[str, Any]:
    """Load quests state file. Fail-closed if file missing/invalid. Auto-creates from template if missing."""
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
                path.write_text(json.dumps(template_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                return template_data
            except Exception as e:
                print(f"WARNING: Failed to bootstrap from template: {e}")
        # Fallback to default structure if template missing
        default_data = {"completed": [], "active": [], "notes": {}}
        try:
            path.write_text(json.dumps(default_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except Exception:
            pass  # If we can't write, continue with in-memory default
        return default_data
    try:
        # Try utf-8-sig first (handles BOM), fallback to utf-8
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        # Corruption recovery: try to restore from backup, then bootstrap
        print(f"WARNING: invalid quests JSON: {e}")
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
                    # Restore from backup (atomic write)
                    tmp_path = path.with_suffix(path.suffix + ".tmp")
                    tmp_path.write_text(json.dumps(backup_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                    os.replace(tmp_path, path)
                    print(f"INFO: Restored quests_state.json from backup: {backups[0].name}")
                    return backup_data
                except Exception as restore_err:
                    print(f"WARNING: Failed to restore from backup: {restore_err}")
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
                # Atomic write
                tmp_path = path.with_suffix(path.suffix + ".tmp")
                tmp_path.write_text(json.dumps(template_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                os.replace(tmp_path, path)
                print(f"INFO: Bootstrapped quests_state.json from template after corruption")
                return template_data
            except Exception as bootstrap_err:
                print(f"WARNING: Failed to bootstrap from template: {bootstrap_err}")
        # Final fallback: default structure (in-memory only, don't write if we're in guard)
        # Guard should fail-closed, so return default but warn
        default_data = {"completed": [], "active": [], "notes": {}}
        print(f"WARNING: Using default quest state after corruption recovery failed (guard will use empty state)")
        return default_data


def extract_tag_ids(text: str, pattern: re.Pattern) -> Set[str]:
    out: Set[str] = set()
    for m in pattern.finditer(text):
        q = m.group(1).lower().strip()
        if q:
            out.add(q)
    return out


def parse_quest_delta(text: str) -> Dict[str, str]:
    """Parse QUEST-DELTA block. Returns quest_id -> action."""
    m = DELTA_BLOCK_PAT.search(text)
    if not m:
        return {}
    body = m.group("body")
    deltas: Dict[str, str] = {}
    for line in body.splitlines():
        line = line.rstrip()
        if not line.strip():
            continue
        m2 = DELTA_LINE_PAT.match(line)
        if not m2:
            continue
        action = m2.group("action").lower()
        quest_id = m2.group("quest_id").lower().strip()
        deltas[quest_id] = action
    return deltas


def main():
    ap = argparse.ArgumentParser(description="Validate quest state (tags + QUEST-DELTA)")
    ap.add_argument("--quests", default=str(DEFAULT_QUESTS_FILE), help="Path to quests_state.json")
    ap.add_argument("--text", default=None, help="Response text (if omitted, read stdin)")
    ap.add_argument("--verbose", action="store_true", help="Verbose output")
    args = ap.parse_args()

    text = args.text if args.text is not None else sys.stdin.read()
    if not text.strip():
        print("ERROR: No text provided")
        sys.exit(1)

    text = normalize_input_text(text)

    quests_path = Path(args.quests)
    quests = load_quests(quests_path)
    if args.verbose:
        print(f"loaded quests_state.json: {quests_path}")

    completed = set(q.lower() for q in quests.get("completed", []))
    violations: List[str] = []

    # 0) ACTIONS-based quest offer detection: if ACTIONS contains quest acceptance options, require [QUESTOFFER/QUESTSTART]
    # This enforces deterministic tag usage when quest offers are present in structured output.
    # Rationale: If the DM presents a quest choice in ACTIONS, they must have already tagged it in NARRATION.
    actions_section = re.search(r"ACTIONS?:?\s*\n((?:[0-9]+\.\s*.*\n?)+)", text, re.IGNORECASE | re.MULTILINE)
    if actions_section:
        actions_text = actions_section.group(1).lower()
        # Detect quest acceptance patterns in ACTIONS (deterministic, not fuzzy story text)
        quest_accept_patterns = [
            r"accept\s+(?:the\s+)?quest",
            r"take\s+(?:the\s+)?(?:job|quest|mission)",
            r"accept\s+(?:the\s+)?(?:job|mission)",
            r"agree\s+to\s+(?:help|the\s+quest)",
        ]
        has_quest_accept_action = any(re.search(pattern, actions_text, re.IGNORECASE) for pattern in quest_accept_patterns)
        
        if has_quest_accept_action:
            # If ACTIONS contains quest acceptance, require [QUESTOFFER] or [QUESTSTART] tag
            start_ids = extract_tag_ids(text, QUEST_START_TAG)
            if not start_ids:
                violations.append("BLOCKED: ACTIONS contains quest acceptance option but missing [QUESTOFFER <id>] or [QUESTSTART <id>] tag in NARRATION")

    # 1) [QUESTSTART id] / [QUESTOFFER id]: block if id in completed
    start_ids = extract_tag_ids(text, QUEST_START_TAG)
    for qid in start_ids:
        if qid in completed:
            violations.append(f"BLOCKED: [QUESTSTART/QUESTOFFER] quest '{qid}' is already completed")

    # 2) State-change tags require QUEST-DELTA
    complete_ids = extract_tag_ids(text, QUEST_COMPLETE_TAG)
    fail_ids = extract_tag_ids(text, QUEST_FAIL_TAG)
    accept_ids = extract_tag_ids(text, QUEST_ACCEPT_TAG)
    activate_ids = extract_tag_ids(text, QUEST_ACTIVATE_TAG)
    all_state = complete_ids | fail_ids | accept_ids | activate_ids

    if all_state:
        deltas = parse_quest_delta(text)
        if not deltas:
            violations.append("BLOCKED: quest state-change tag(s) present but QUEST-DELTA block missing")
        else:
            for qid in all_state:
                if qid not in deltas:
                    violations.append(f"BLOCKED: quest '{qid}' has state-change tag but missing from QUEST-DELTA")
            for qid, action in deltas.items():
                if qid in complete_ids and action != "complete":
                    violations.append(f"BLOCKED: quest '{qid}' [QUESTCOMPLETE] but QUEST-DELTA has '{action}'")
                elif qid in fail_ids and action != "fail":
                    violations.append(f"BLOCKED: quest '{qid}' [QUESTFAIL] but QUEST-DELTA has '{action}'")
                elif qid in accept_ids and action != "accept":
                    violations.append(f"BLOCKED: quest '{qid}' [QUESTACCEPT] but QUEST-DELTA has '{action}'")
                elif qid in activate_ids and action != "activate":
                    violations.append(f"BLOCKED: quest '{qid}' [QUESTACTIVATE] but QUEST-DELTA has '{action}'")

    if violations:
        print("BLOCKED: quest state violation")
        if args.verbose:
            for v in violations:
                print(f"  - {v}")
        sys.exit(1)

    print("OK: quest_guard passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
