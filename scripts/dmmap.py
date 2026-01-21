#!/usr/bin/env python3
"""
DM Map Helper — validate battlemap state and, if blocked, print a ready-to-paste instruction.

Usage:
  python scripts/dmmap.py
  python scripts/dmmap.py --verbose

Output:
  OK:        one line (quiet mode) or MAP_RECEIPT (verbose)
  BLOCKED:   BLOCKED + MAP_INSTRUCTION
"""

from __future__ import annotations

import sys
import subprocess
from pathlib import Path


MAP_INSTRUCTION = (
    'MAP_INSTRUCTION: Re-render map from CURRENT_STATE.json and reconcile token positions. '
    'Update scripts/combat_positions_<location>.json with correct integer coordinates. '
    'Ensure all tokens are in-bounds and coordinates match combat engine state.'
)


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    dm_workflow = script_dir / "dm_workflow.py"

    if not dm_workflow.exists():
        print("ERROR: dm_workflow.py not found")
        return 1

    # Check for verbose flag
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    # Run mapcheck
    cmd = [sys.executable, str(dm_workflow), "mapcheck"]
    if verbose:
        cmd.append("--verbose")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        exit_code = result.returncode
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if exit_code == 0:
            # Success - print output
            if stdout:
                print(stdout)
            return 0
        else:
            # Blocked - print instruction
            if stdout:
                print(stdout)
            print(f"\n{MAP_INSTRUCTION}")
            return 1

    except Exception as e:
        print(f"ERROR: Failed to run mapcheck: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
