#!/usr/bin/env python3
"""
Text Normalization - Shared utility for stripping transcript/REPL prefixes.

Used by resource_guard.py and apply_state_delta.py to handle messy input
from PowerShell transcripts, copy/paste operations, etc.
"""

import re

_PREFIX_RE = re.compile(r'^\s*(?:>>+|\|+|>+)\s*')  # >>, |, > prefixes

def normalize_input_text(text: str) -> str:
    """
    Strip common transcript/REPL prefixes:
      - PowerShell continuation prompts: >>, >>> ...
      - quote markers: >, >> (from logs)
      - pipe prettifiers: | (rare but seen in copy/paste)
    Only strips at line start.
    """
    out = []
    for line in text.splitlines():
        out.append(_PREFIX_RE.sub('', line))
    return "\n".join(out)
