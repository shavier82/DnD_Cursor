#!/usr/bin/env python3
"""
Response Guard - Validates DM output for combat turn authority violations.

Checks that enemy/NPC turns don't delegate control to the player.
Exits with code 1 if violations detected.

Usage:
    python scripts/response_guard.py --is-pc-turn false < response.txt
    python scripts/response_guard.py --is-pc-turn true < response.txt
    python scripts/response_guard.py --combat-status status.json < response.txt
    echo "response text" | python scripts/response_guard.py --is-pc-turn false
"""

import sys
import argparse
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Optional


# Load forbidden phrases from shared config (with fallback)
CONFIG_FILE = Path(__file__).parent / "guard_config.json"
FORBIDDEN_PHRASES = []
ALLOWED_ENEMY_QUESTIONS = []

def load_guard_config() -> tuple[list[str], list[str]]:
    """Load forbidden phrases and allowed enemy questions from shared config.
    
    Returns plain strings (not regex patterns). Regex compilation happens at use site.
    """
    if not CONFIG_FILE.exists():
        # Fallback to hardcoded values (plain strings)
        return [
            "what does",
            "what should",
            "your call",
            "you decide",
            "what do they do",
            "what do you do",  # Only allowed on PC turns
        ], ["any reactions", "reactions"]
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        # Keep as plain strings (config file has plain strings)
        forbidden = config.get("forbidden_phrases", [])
        # Add PC-only phrase that's not in config
        if "what do you do" not in forbidden:
            forbidden.append("what do you do")
        allowed = config.get("allowed_enemy_questions", ["any reactions", "reactions"])
        return forbidden, allowed
    except Exception as e:
        print(f"ERROR: Failed to load guard_config.json: {e}")
        sys.exit(1)

# PC roster - canonical source
ROSTER_FILE = Path(__file__).parent / "pc_roster.json"

# Allowed reaction question patterns (must match entire line/question)
ALLOWED_REACTION_PATTERNS = [
    r"^any\s+reactions?\s*\??\s*$",  # "Any reactions?" or "Any reactions"
    r"^reactions?\s*\??\s*$",  # "Reactions?" or "Reactions"
    r"^any\s+reactions?\s*\(.*\)\s*\??\s*$",  # "Any reactions? (Shield, ...)"
    r"^reactions\?\s*\(.*\)\s*$",  # "Reactions? (Shield/...)"
]


def load_pc_roster() -> list[str]:
    """Load PC roster from canonical file. Fail-closed if file missing/invalid."""
    if not ROSTER_FILE.exists():
        print(f"ERROR: PC roster file not found: {ROSTER_FILE}")
        print("  Create scripts/pc_roster.json with 'pc_roster' array")
        sys.exit(1)
    
    try:
        with open(ROSTER_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        roster = data.get("pc_roster", [])
        if not roster:
            print(f"ERROR: pc_roster array is empty or missing in {ROSTER_FILE}")
            sys.exit(1)
        
        return roster
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in PC roster file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to load PC roster: {e}")
        sys.exit(1)


def is_allowed_reaction_question(text: str) -> bool:
    """Check if question is an allowed reactions prompt."""
    text_stripped = text.strip()
    
    # Check each line for allowed patterns
    for line in text_stripped.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Remove common prefixes like "ASK:" or "- "
        line = re.sub(r'^(ask|action|actions)[:\-]?\s*', '', line, flags=re.IGNORECASE).strip()
        
        # Check if line contains question mark and reaction keywords
        if '?' in line:
            line_lower = line.lower()
            # Must contain "reaction" keyword
            if 'reaction' in line_lower:
                # Check for parenthetical examples (allowed)
                if re.search(r'\(.*(shield|counter|absorb|opportunity)', line_lower):
                    return True
                # Check for simple "Any reactions?" pattern
                if re.match(r'^any\s+reactions?\s*\??\s*$', line_lower):
                    return True
                # Check for just "Reactions?" pattern
                if re.match(r'^reactions?\s*\??\s*$', line_lower):
                    return True
    
    return False


def check_enemy_turn_violations(text: str) -> list[str]:
    """Check for forbidden phrases in enemy turn responses."""
    violations = []
    text_lower = text.lower()
    
    # Check for question marks (not allowed on enemy turns except specific reactions prompts)
    if "?" in text:
        if not is_allowed_reaction_question(text):
            # Extract the question line for context
            questions = [line.strip() for line in text.split('\n') if '?' in line]
            for q in questions[:3]:  # Limit to first 3 questions
                violations.append(f"Forbidden question on enemy turn: '{q}' (only 'Any reactions?' allowed)")
    
    # Check for forbidden phrases (compile regex with word boundaries at use site)
    for phrase in FORBIDDEN_PHRASES:
        # Compile regex with word boundaries for exact matches (phrase is plain string)
        pattern = re.compile(r"\b" + re.escape(phrase) + r"\b", re.IGNORECASE)
        matches = pattern.finditer(text_lower)
        for match in matches:
            # Get context around the match
            start = max(0, match.start() - 20)
            end = min(len(text_lower), match.end() + 20)
            context = text_lower[start:end].strip()
            # Use original phrase (plain string) in violation message, not regex pattern
            violations.append(f"Forbidden phrase '{phrase}' found: ...{context}...")
    
    return violations


def detect_turn_type_from_combat_status(combat_status: dict, fail_closed: bool = True) -> tuple[bool, Optional[str]]:
    """
    Detect if current turn is a PC turn from combat status JSON.
    
    Returns:
        (is_pc_turn, error_message)
    """
    current_turn = combat_status.get("current_turn", {})
    creature_id = current_turn.get("creature_id")
    
    if not creature_id:
        if fail_closed:
            return None, "combat status missing current_turn.creature_id"
        # Fail-open default (safer for non-combat)
        return True, None
    
    # Load roster
    try:
        pc_roster = load_pc_roster()
    except SystemExit:
        # load_pc_roster already printed error and exited
        raise
    
    is_pc = creature_id.lower() in [pc.lower() for pc in pc_roster]
    return is_pc, None


def validate_response(text: str, is_pc_turn: bool) -> tuple[bool, list[str]]:
    """
    Validate response text based on turn type.
    
    Returns:
        (is_valid, violations_list)
    """
    violations = []
    
    if not is_pc_turn:
        # Enemy/NPC turn - check for forbidden phrases
        enemy_violations = check_enemy_turn_violations(text)
        violations.extend(enemy_violations)
        
        # Additional check: "What do you do?" should NEVER appear on enemy turns
        if re.search(r"what do you do\?", text, re.IGNORECASE):
            violations.append("CRITICAL: 'What do you do?' appeared on enemy turn (PC-only phrase)")
    
    return len(violations) == 0, violations


def main():
    import uuid
    RUN_ID = str(uuid.uuid4())[:8]
    
    parser = argparse.ArgumentParser(
        description="Validate DM response for combat turn authority violations"
    )
    parser.add_argument(
        "--is-pc-turn",
        type=str,
        default=None,
        choices=["true", "false", "True", "False", "1", "0"],
        help="Whether current turn is a PC turn (true/false). Overrides --combat-status if provided."
    )
    parser.add_argument(
        "--combat-status",
        type=str,
        default=None,
        help="Path to combat status JSON file. Auto-detects is_pc_turn from current_turn.creature_id."
    )
    parser.add_argument(
        "--text",
        type=str,
        default=None,
        help="Response text to validate (if not provided, reads from stdin)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed violation information"
    )
    
    args = parser.parse_args()
    
    # Load guard config (fail-closed if config file exists but invalid)
    global FORBIDDEN_PHRASES, ALLOWED_ENEMY_QUESTIONS
    FORBIDDEN_PHRASES, ALLOWED_ENEMY_QUESTIONS = load_guard_config()
    
    # Load PC roster (fail-closed)
    global PC_ROSTER
    PC_ROSTER = load_pc_roster()
    
    # Determine is_pc_turn
    is_pc_turn = None
    turn_detection_error = None
    
    if args.is_pc_turn:
        # Explicit flag takes precedence
        is_pc_turn = args.is_pc_turn.lower() in ("true", "1")
    elif args.combat_status:
        # Auto-detect from combat status file
        try:
            status_path = Path(args.combat_status)
            if not status_path.exists():
                print(f"ERROR: Combat status file not found: {status_path}")
                sys.exit(1)
            
            with open(status_path, 'r', encoding='utf-8') as f:
                combat_status = json.load(f)
            
            # Check if combat is active
            is_active = combat_status.get("is_active", True)
            
            if is_active:
                # Fail-closed: must have current_turn
                is_pc_turn, error = detect_turn_type_from_combat_status(combat_status, fail_closed=True)
                if error:
                    print(f"BLOCKED: combat active but {error}")
                    if args.verbose:
                        print(f"  Run get_combat_status and update CURRENT_STATE.json")
                    sys.exit(1)
            else:
                # Combat not active - default to PC turn (fail-open for non-combat)
                is_pc_turn = True
            
            # Verbose details only shown on failure (not here)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in combat status file: {e}")
            sys.exit(1)
        except SystemExit:
            raise  # Re-raise if load_pc_roster exited
        except Exception as e:
            print(f"ERROR: Failed to read combat status file: {e}")
            sys.exit(1)
    else:
        # No turn detection method provided
        print("ERROR: Must provide either --is-pc-turn or --combat-status")
        sys.exit(1)
    
    # Get text
    if args.text:
        text = args.text
    else:
        text = sys.stdin.read()
    
    if not text.strip():
        print("ERROR: No text provided")
        sys.exit(1)
    
    # Validate
    is_valid, violations = validate_response(text, is_pc_turn)
    
    # Always print run id in verbose mode only (for debugging double-invocation)
    if args.verbose:
        print(f"DEBUG: response_guard RUN_ID={RUN_ID}")
    
    # Output results
    if is_valid:
        # Success - print to stdout only (copy/paste friendly, no stderr noise)
        print("OK: response_guard passed")
        # No verbose output on success (only show details on failure)
        sys.exit(0)
    
    # Violations found - block
    # Main message to stdout (copy/paste friendly)
    print("BLOCKED: monster turn delegation detected")
    # Details to stdout (only in verbose mode, no stderr to avoid PowerShell errors)
    if args.verbose and violations:
        print("\nViolations:")
        for violation in violations:
            print(f"  - {violation}")
    sys.exit(1)


if __name__ == "__main__":
    main()
