#!/usr/bin/env python3
"""
Create individual spell files in Spell_Dictionary folder structure
and update spell list files to link to them.
"""

import os
import re
from pathlib import Path

# Base paths
BASE_PATH = Path(r"C:\Users\ksist\Documents\Obsidian\DnD\Player Characters")
SPELL_DICT_PATH = BASE_PATH / "Spell_Dictionary"

# Spell list files
TORGGA_SPELLS = BASE_PATH / "Torgga_Brawnanvil_Spells.md"
ZEPHYR_SPELLS = BASE_PATH / "Zephyr_Sparkwhistle_Spells.md"

def sanitize_filename(name):
    """Convert spell name to filename-safe format"""
    # Replace special characters and spaces
    name = name.replace("'", "").replace("/", "_").replace(" ", "_")
    # Remove any remaining special characters
    name = re.sub(r'[^\w\-_]', '', name)
    return name

def extract_spells_from_file(file_path, class_name):
    """Extract spells from spell list file"""
    spells = []
    current_level = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        
        for line in lines:
            # Check for level headers
            level_match = re.match(r'^## (Level \d+ Spells|Cantrips)', line)
            if level_match:
                if "Cantrips" in line:
                    current_level = 0
                else:
                    level_match2 = re.search(r'Level (\d+)', line)
                    if level_match2:
                        current_level = int(level_match2.group(1))
                continue
            
            # Extract spell names from list items
            # Format: - [x] **Spell Name** - School (properties)
            # OR: - [x] [[link|Spell Name]] - School (properties) (after linking)
            spell_match = re.match(r'^-\s+\[[x\s]\]\s+(?:\*\*([^*]+)\*\*|\[\[[^\]]+\|([^\]]+)\]\])', line)
            if spell_match:
                spell_name = spell_match.group(1) or spell_match.group(2)
                spell_name = spell_name.strip()
                # Extract school - text after "]] - " or "** - " and before " (" or "⭐"
                # Handle both linked and unlinked formats
                # Fix regex: escape special characters properly
                school_match = re.search(r'(?:\]\]|\*\*)\s+-\s+([^(⭐]+?)(?:\s*\(|⭐|$)', line)
                if school_match:
                    school = school_match.group(1).strip()
                else:
                    # Fallback: try to get text after " - "
                    school_match2 = re.search(r'-\s+([^(⭐]+?)(?:\s*\(|⭐|$)', line)
                    school = school_match2.group(1).strip() if school_match2 else ""
                
                properties = []
                if "(C)" in line:
                    properties.append("Concentration")
                if "(R)" in line:
                    properties.append("Ritual")
                if "⭐" in line:
                    properties.append("Life Domain")
                
                spells.append({
                    'name': spell_name,
                    'level': current_level,
                    'school': school,
                    'properties': properties,
                    'class': class_name
                })
    
    return spells

def get_spell_details(spell_name):
    """Get spell details from MCP lookup"""
    try:
        # This would need to be called via MCP, but for now return formatted info
        # In actual implementation, you'd call: mcp_rules-database_lookup_spell(spell_name)
        return None  # Will be populated by actual MCP call
    except:
        return None

def create_spell_file(spell, spell_list_file):
    """Create individual spell file"""
    class_folder = "Cleric" if spell['class'] == "Cleric" else "Wizard"
    level_folder = f"Level_{spell['level']}"
    spell_filename = sanitize_filename(spell['name']) + ".md"
    spell_path = SPELL_DICT_PATH / class_folder / level_folder / spell_filename
    
    # Create spell file content
    properties_text = ", ".join(spell['properties']) if spell['properties'] else "None"
    level_text = "Cantrip" if spell['level'] == 0 else f"Level {spell['level']}"
    
    spell_list_link = "Torgga_Brawnanvil_Spells" if spell['class'] == "Cleric" else "Zephyr_Sparkwhistle_Spells"
    level_section = "Cantrips" if spell['level'] == 0 else f"Level {spell['level']} Spells"
    
    # Format properties list
    properties_list = ""
    if spell['properties']:
        properties_list = "\n".join(f"- **{prop}**" for prop in spell['properties'])
    else:
        properties_list = "- None"
    
    # Determine concentration and ritual from properties
    concentration = "Yes" if "Concentration" in spell['properties'] else "No"
    ritual = "Yes" if "Ritual" in spell['properties'] else "No"
    
    content = f"""---
spell_name: {spell['name']}
spell_level: {spell['level']}
spell_school: {spell['school']}
spell_class: {spell['class']}
properties: {properties_text}
---

# {spell['name']}

**Level:** {level_text}  
**School:** {spell['school']}  
**Class:** {spell['class']}

## Properties

{properties_list}

## Spell Details

**Full spell details (casting time, range, components, duration, description) are available via MCP tools during gameplay.**

**To look up this spell:**
1. Use MCP tool: `lookup_spell("{spell['name']}")`
2. Or search sourcebooks: `search_sourcebooks("{spell['name']}", "phb")`

**Quick Reference:**
- **Concentration:** {concentration}
- **Ritual:** {ritual}
- **Source:** PHB 2024

**Note:** The DM will use MCP spell lookup tools during gameplay to provide complete spell information including casting time, range, components, duration, and full description from the PHB 2024.

## Quick Links

← **[[{spell_list_link}#{level_section}|Back to {spell['class']} Spell List]]**

---

*This spell file links back to the spellcaster's spell list. Full spell details are available via MCP tools during gameplay.*
"""
    
    # Write file
    spell_path.parent.mkdir(parents=True, exist_ok=True)
    with open(spell_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return spell_path

def update_spell_list_file(file_path, spells, class_name):
    """Update spell list file to link to individual spell files"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace spell names with links
    for spell in spells:
        spell_name = spell['name']
        spell_filename = sanitize_filename(spell['name'])
        class_folder = "Cleric" if class_name == "Cleric" else "Wizard"
        level_folder = f"Level_{spell['level']}"
        
        # Create link path
        link_path = f"Spell_Dictionary/{class_folder}/{level_folder}/{spell_filename}"
        
        # Replace pattern: **Spell Name** with [[link|Spell Name]]
        pattern = rf'\*\*{re.escape(spell_name)}\*\*'
        replacement = f'[[{link_path}|{spell_name}]]'
        
        content = re.sub(pattern, replacement, content)
    
    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print("Extracting spells from Torgga's spell list...")
    torgga_spells = extract_spells_from_file(TORGGA_SPELLS, "Cleric")
    print(f"Found {len(torgga_spells)} Cleric spells")
    
    print("Extracting spells from Zephyr's spell list...")
    zephyr_spells = extract_spells_from_file(ZEPHYR_SPELLS, "Wizard")
    print(f"Found {len(zephyr_spells)} Wizard spells")
    
    print("\nCreating spell files...")
    for spell in torgga_spells + zephyr_spells:
        spell_list_file = TORGGA_SPELLS if spell['class'] == "Cleric" else ZEPHYR_SPELLS
        spell_path = create_spell_file(spell, spell_list_file)
        print(f"  Created: {spell_path.relative_to(BASE_PATH)}")
    
    print("\nUpdating spell list files with links...")
    update_spell_list_file(TORGGA_SPELLS, torgga_spells, "Cleric")
    print("  Updated: Torgga_Brawnanvil_Spells.md")
    
    update_spell_list_file(ZEPHYR_SPELLS, zephyr_spells, "Wizard")
    print("  Updated: Zephyr_Sparkwhistle_Spells.md")
    
    print("\nComplete! All spell files created and spell lists updated.")

if __name__ == "__main__":
    main()
