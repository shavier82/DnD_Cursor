#!/usr/bin/env python3
"""
Rest Guard - Fail-closed detector for rest tags.

Validates that rest-ish narration includes explicit [LONGREST] or [SHORTREST] tags.
If rest-ish language is detected but no tag is present → BLOCKED.

This prevents accidental state resets from fuzzy keyword matching.

Usage:
    echo "response text" | python scripts/rest_guard.py
    python scripts/rest_guard.py --text "response text"
"""

import argparse
import re
import sys
from typing import Optional, Tuple

LONGREST_TAG_PAT = re.compile(r'\[LONGREST\]', re.IGNORECASE)
SHORTREST_TAG_PAT = re.compile(r'\[SHORTREST\]', re.IGNORECASE)

# Rest-ish language patterns (these trigger the requirement for tags)
LONGREST_PHRASES = [
    r'\blong rest\b',
    r'\brest until dawn\b',
    r'\bsleep until dawn\b',
    r'\bsleeps until dawn\b',
    r'\bsleep until morning\b',
    r'\bsleeps until morning\b',
    r'\bcamp for the night\b',
    r'\bsleep through the night\b',
    r'\bsleeps through the night\b',
    r'\b8 hours of rest\b',
    r'\beight hours of rest\b',
    r'\bfull night\'?s rest\b',
    r'\bcomplete rest\b',
    r'\bfinish.*long rest\b',
    r'\btake.*long rest\b',
    r'\bcomplete.*long rest\b',
]

SHORTREST_PHRASES = [
    r'\bshort rest\b',
    r'\brest.*hour\b',  # "rest for an hour", "take an hour to rest"
    r'\btake a break\b',
    r'\bquick rest\b',
    r'\bbrief rest\b',
    r'\b1 hour rest\b',
    r'\bone hour rest\b',
    r'\ban hour\'?s rest\b',
]

def detect_rest_language(text: str) -> Tuple[bool, bool]:
    """Detect if text contains rest-ish language.
    
    Returns:
        (has_long_rest_language, has_short_rest_language)
    """
    text_lower = text.lower()
    
    has_long = any(re.search(pattern, text_lower) for pattern in LONGREST_PHRASES)
    has_short = any(re.search(pattern, text_lower) for pattern in SHORTREST_PHRASES)
    
    return has_long, has_short

def detect_rest_tags(text: str) -> Tuple[bool, bool]:
    """Detect if text contains explicit rest tags.
    
    Returns:
        (has_longrest_tag, has_shortrest_tag)
    """
    has_longrest = bool(LONGREST_TAG_PAT.search(text))
    has_shortrest = bool(SHORTREST_TAG_PAT.search(text))
    
    return has_longrest, has_shortrest

def main() -> int:
    """Validate rest tags in response text."""
    ap = argparse.ArgumentParser(description="Rest guard - validates explicit rest tags")
    ap.add_argument("--text", default=None, help="Response text (if omitted, read stdin)")
    ap.add_argument("--verbose", action="store_true", help="Show detailed output")
    args = ap.parse_args()
    
    text = args.text if args.text is not None else sys.stdin.read()
    if not text.strip():
        print("ERROR: No text provided", file=sys.stderr)
        sys.exit(1)
    
    # Detect rest-ish language
    has_long_lang, has_short_lang = detect_rest_language(text)
    
    # Detect explicit tags
    has_longrest_tag, has_shortrest_tag = detect_rest_tags(text)
    
    # Fail-closed validation
    violations = []
    
    if has_long_lang and not has_longrest_tag:
        violations.append("Long rest language detected but [LONGREST] tag is missing")
    
    if has_short_lang and not has_shortrest_tag:
        violations.append("Short rest language detected but [SHORTREST] tag is missing")
    
    # If both tags present, that's OK (tags take precedence over language)
    # If both language types detected but only one tag, warn
    if has_long_lang and has_short_lang:
        if has_longrest_tag and not has_shortrest_tag:
            if args.verbose:
                print("NOTE: Both long and short rest language detected, but only [LONGREST] tag found")
        elif has_shortrest_tag and not has_longrest_tag:
            if args.verbose:
                print("NOTE: Both long and short rest language detected, but only [SHORTREST] tag found")
    
    if violations:
        print("BLOCKED: rest implied but missing rest tag", file=sys.stderr)
        if args.verbose:
            for v in violations:
                print(f"  - {v}", file=sys.stderr)
        sys.exit(1)
    
    # Success - output which rest type to trigger (if any)
    if has_longrest_tag:
        print("OK: long_rest")
    elif has_shortrest_tag:
        print("OK: short_rest")
    else:
        print("OK: no_rest")
    
    sys.exit(0)

if __name__ == "__main__":
    main()
