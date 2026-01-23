#!/usr/bin/env python3
"""
Render Quests Dashboard - Generate human-readable markdown from quests_state.json

Reads quests_state.json and generates DnD/state/quests_state.md for Obsidian.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
QUESTS = SCRIPT_DIR / "quests_state.json"


def render(quests: dict) -> str:
    completed = quests.get("completed", []) or []
    active = quests.get("active", []) or []
    notes = quests.get("notes", {}) or {}

    lines = [
        "# Quests (AUTO)",
        "",
        f"_Last generated: {datetime.now().isoformat(timespec='seconds')}_",
        "",
        "> Source of truth: `DnD/state/quests_state.json`",
        "",
        "## Completed",
        "",
    ]
    if completed:
        for q in completed:
            note = notes.get(q, "")
            if note:
                lines.append(f"- **{q}** — {note}")
            else:
                lines.append(f"- **{q}**")
        lines.append("")
    else:
        lines.append("_None_")
        lines.append("")

    lines.append("## Active")
    lines.append("")
    if active:
        for q in active:
            note = notes.get(q, "")
            if note:
                lines.append(f"- **{q}** — {note}")
            else:
                lines.append(f"- **{q}**")
        lines.append("")
    else:
        lines.append("_None_")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main():
    if not QUESTS.exists():
        print(f"ERROR: Missing {QUESTS}", file=sys.stderr)
        sys.exit(1)
    try:
        quests = json.loads(QUESTS.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: Failed to load quests: {e}", file=sys.stderr)
        sys.exit(1)
    md = render(quests)
    print(md, end="")


if __name__ == "__main__":
    main()
