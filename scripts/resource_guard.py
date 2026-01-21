#!/usr/bin/env python3
"""
Resource Guard - Validates DM output for resource spend enforcement.

Checks that every resource spend has:
1. Inline SPEND tags: [SPEND <actor> <resource> <level?> <amount>]
2. STATE-DELTA block that reconciles every SPEND tag
3. No underflow (resource count can't go negative)

Exits with code 1 if violations detected.

Usage:
    echo "response text" | python scripts/resource_guard.py
    python scripts/resource_guard.py --text "response text"
    python scripts/resource_guard.py --verbose
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_RESOURCES_FILE = ROOT_DIR / "scripts" / "resources_state.json"

SPEND_PAT = re.compile(
    r"\[SPEND\s+(?P<actor>[a-zA-Z0-9_\-]+)\s+(?P<res>[a-zA-Z0-9_\-]+)\s+(?:(?P<level>\d+)\s+)?(?P<amt>\d+)\s*\]",
    re.IGNORECASE,
)

DELTA_BLOCK_PAT = re.compile(r"STATE-DELTA\s*(?P<body>.*?)\s*END STATE-DELTA", re.IGNORECASE | re.DOTALL)
DELTA_LINE_PAT = re.compile(
    r"^\s*-\s*(?P<actor>[a-zA-Z0-9_\-]+)\s*:\s*(?P<key>[a-zA-Z0-9_\.\-]+)\s*-\=\s*(?P<amt>\d+)\s*$",
    re.IGNORECASE,
)

ALLOWED_RESOURCES = {
    "spell_slot",
    "rage",
    "superiority_die",
    "ki",
    "maneuver",
    "wild_shape",
    "channel_divinity",
    "bardic_inspiration",
    "sorcery_point",
}

def load_resources(path: Path) -> Dict[str, Any]:
    """Load resources state file. Fail-closed if file missing/invalid."""
    if not path.exists():
        print(f"ERROR: resources file not found: {path}")
        sys.exit(1)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: invalid resources JSON: {e}")
        sys.exit(1)

def parse_spends(text: str) -> List[Tuple[str, str, int, int]]:
    """Parse all [SPEND ...] tags from text.
    
    Returns list of (actor, resource, level, amount) tuples.
    For non-spell-slot resources, level is 0.
    """
    spends = []
    for m in SPEND_PAT.finditer(text):
        actor = m.group("actor")
        res = m.group("res").lower()
        level = int(m.group("level")) if m.group("level") else None
        amt = int(m.group("amt"))
        # normalize spell slots format: spell_slot <level> <amt>
        if res == "spell_slot":
            if level is None:
                raise ValueError(f"spell_slot spend missing level for actor={actor}")
            spends.append((actor, "spell_slot", level, amt))
        else:
            spends.append((actor, res, 0, amt))
    return spends

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
            print(f"BLOCKED: invalid STATE-DELTA line format: {line}")
            sys.exit(1)
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

def get_resource_value(resources: Dict[str, Any], actor: str, res: str, level: int) -> int:
    """Get current value of a resource for an actor."""
    actor_obj = resources.get(actor, {})
    if res == "spell_slot":
        slots = actor_obj.get("spell_slots", {})
        return int(slots.get(str(level), 0))
    return int(actor_obj.get(res, 0))

def main():
    ap = argparse.ArgumentParser(description="Validate resource spends in DM output")
    ap.add_argument("--resources", default=str(DEFAULT_RESOURCES_FILE), help="Path to resources_state.json")
    ap.add_argument("--text", default=None, help="Response text (if omitted, read stdin)")
    ap.add_argument("--verbose", action="store_true", help="Verbose output")
    args = ap.parse_args()

    text = args.text if args.text is not None else sys.stdin.read()
    if not text.strip():
        print("ERROR: No text provided")
        sys.exit(1)

    resources_path = Path(args.resources)
    resources = load_resources(resources_path)

    try:
        spends = parse_spends(text)
    except ValueError as e:
        print(f"BLOCKED: {e}")
        sys.exit(1)

    deltas = parse_delta(text)

    # If any spends exist, STATE-DELTA must exist and reconcile every spend.
    if spends and not deltas:
        print("BLOCKED: resource spend detected but STATE-DELTA block is missing")
        sys.exit(1)

    violations = []

    for actor, res, level, amt in spends:
        if res not in ALLOWED_RESOURCES:
            violations.append(f"Unknown resource '{res}' in SPEND tag for {actor}")
            continue

        delta_key = (actor, res, level)
        if delta_key not in deltas:
            if res == "spell_slot":
                violations.append(f"Missing STATE-DELTA for {actor}: spell_slot.{level} -= {amt}")
            else:
                violations.append(f"Missing STATE-DELTA for {actor}: {res} -= {amt}")
            continue

        if deltas[delta_key] != amt:
            violations.append(f"Mismatch: SPEND {actor} {res}{'.'+str(level) if res=='spell_slot' else ''} {amt} but STATE-DELTA subtracts {deltas[delta_key]}")

        current = get_resource_value(resources, actor, res, level)
        if current - amt < 0:
            violations.append(f"Underflow: {actor} {res}{'.'+str(level) if res=='spell_slot' else ''} has {current}, cannot spend {amt}")

    if violations:
        print("BLOCKED: resource spend not reconciled")
        if args.verbose:
            print("\nViolations:")
            for v in violations:
                print(f"  - {v}")
        sys.exit(1)

    print("OK: resource_guard passed")
    sys.exit(0)

if __name__ == "__main__":
    main()
