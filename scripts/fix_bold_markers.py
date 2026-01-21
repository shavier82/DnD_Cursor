#!/usr/bin/env python3
"""Fix bold markers for spell links in Torgga's spell list"""

import re
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = Path(r"C:\Users\ksist\Documents\Obsidian\DnD\Player Characters\Torgga_Brawnanvil_Spells.md")

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find links without bold markers and add them
# Pattern: - [x] [[link|name]] - rest
pattern = r'- \[([ x])\] \[\[([^\]]+)\|([^\]]+)\]\] - '
replacement = r'- [\1] **[[\2|\3]]** - '

content = re.sub(pattern, replacement, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed bold markers in Torgga's spell list")
