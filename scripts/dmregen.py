#!/usr/bin/env python3
"""
DM Regen Helper — validate a DM response and, if blocked, print a ready-to-paste regen instruction.

Usage:
  Get-Clipboard | python scripts/dmregen.py
  python scripts/dmregen.py < response.txt
  echo "response text" | python scripts/dmregen.py

Output:
  OK:        one line
  BLOCKED:   two lines (BLOCKED + REGEN_INSTRUCTION)
"""

from __future__ import annotations

import sys
import subprocess
from pathlib import Path


REGEN_INSTRUCTION_COMBAT = (
    'REGEN_INSTRUCTION: Regenerate the enemy/NPC turn using combat-engine. '
    'Do not delegate enemy decisions. Resolve full enemy turn. '
    'Ask only: "Any reactions?" then proceed to next PC turn.'
)

REGEN_INSTRUCTION_RESOURCE = (
    'REGEN_INSTRUCTION: Regenerate with SPEND tags + STATE-DELTA block. '
    'Every resource spend must include: [SPEND <actor> <resource> <level?> <amount>] '
    'and a STATE-DELTA block at the end reconciling all spends. '
    'Format: STATE-DELTA\n- actor: resource.level -= amount\nEND STATE-DELTA'
)


def read_stdin_text() -> str:
    # Read full stdin; allow empty/whitespace to error cleanly
    return sys.stdin.read()


def first_line(text: str) -> str:
    text = (text or "").strip("\n")
    if not text:
        return ""
    return text.splitlines()[0].strip()


def main() -> int:
    text = read_stdin_text()
    if not text.strip():
        print("ERROR: No input provided")
        return 1

    script_dir = Path(__file__).resolve().parent
    dm_workflow = script_dir / "dm_workflow.py"

    if not dm_workflow.exists():
        print(f"ERROR: Missing dm_workflow.py at: {dm_workflow}")
        return 1

    # Run dm_workflow.py respond in quiet mode (default)
    proc = subprocess.run(
        [sys.executable, str(dm_workflow), "respond"],
        input=text,
        text=True,
        capture_output=True,
    )

    # dm_workflow.py prints the status to stdout; we enforce our own minimal output here.
    status = first_line(proc.stdout)

    if not status:
        print("ERROR: Guard produced no output")
        return 1

    if proc.returncode == 0:
        print(status)  # OK: guards passed
        return 0

    # Blocked/error path
    print(status)  # BLOCKED: ...
    
    # Choose appropriate regeneration instruction based on error type
    status_lower = status.lower()
    if "resource" in status_lower or "spend" in status_lower or "state-delta" in status_lower:
        print(REGEN_INSTRUCTION_RESOURCE)
    else:
        print(REGEN_INSTRUCTION_COMBAT)
    
    return proc.returncode if proc.returncode != 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
