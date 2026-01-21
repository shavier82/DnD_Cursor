#!/usr/bin/env python3
"""
Create spell files for all Cleric spells (levels 0-4).
"""

import json
import re
from pathlib import Path
import sys

# Base paths
BASE_PATH = Path(r"C:\Users\ksist\Documents\Obsidian\DnD\Player Characters")
SPELL_DICT_BASE = BASE_PATH / "Spell_Dictionary" / "Cleric"
RULES_DB = Path(r"C:\DnD\DnD_Cursor\rules_database\spells.json")
SPELLS_BY_CLASS = Path(r"C:\DnD\DnD_Cursor\rules_database\spells_by_class.json")

def load_databases():
    """Load spells databases"""
    with open(RULES_DB, 'r', encoding='utf-8') as f:
        spells_db = json.load(f)
    with open(SPELLS_BY_CLASS, 'r', encoding='utf-8') as f:
        spells_by_class = json.load(f)
    return spells_db, spells_by_class

def get_spell_id_from_name(spell_name):
    """Convert spell name to spell_id format"""
    special_cases = {
        "Create or Destroy Water": "create_or_destroy_water",
        "Detect Evil and Good": "detect_evil_and_good",
        "Detect Poison and Disease": "detect_poison_and_disease",
        "Protection from Evil and Good": "protection_from_evil_and_good",
        "Blindness/Deafness": "blindness_deafness",
        "Purify Food and Drink": "purify_food_and_drink",
        "Spare the Dying": "spare_the_dying",
        "Word of Radiance": "word_of_radiance",
        "Sacred Flame": "sacred_flame",
        "Healing Word": "healing_word",
        "Inflict Wounds": "inflict_wounds",
        "Guiding Bolt": "guiding_bolt",
        "Shield of Faith": "shield_of_faith",
        "Lesser Restoration": "lesser_restoration",
        "Prayer of Healing": "prayer_of_healing",
        "Protection from Poison": "protection_from_poison",
        "Spiritual Weapon": "spiritual_weapon",
        "Warding Bond": "warding_bond",
        "Zone of Truth": "zone_of_truth",
        "Aura of Vitality": "aura_of_vitality",
        "Beacon of Hope": "beacon_of_hope",
        "Bestow Curse": "bestow_curse",
        "Create Food and Water": "create_food_and_water",
        "Mass Healing Word": "mass_healing_word",
        "Meld into Stone": "meld_into_stone",
        "Protection from Energy": "protection_from_energy",
        "Remove Curse": "remove_curse",
        "Speak with Dead": "speak_with_dead",
        "Spirit Guardians": "spirit_guardians",
        "Water Walk": "water_walk",
        "Aura of Life": "aura_of_life",
        "Aura of Purity": "aura_of_purity",
        "Death Ward": "death_ward",
        "Freedom of Movement": "freedom_of_movement",
        "Guardian of Faith": "guardian_of_faith",
        "Locate Creature": "locate_creature",
        "Stone Shape": "stone_shape"
    }
    
    if spell_name in special_cases:
        return special_cases[spell_name]
    
    return spell_name.lower().replace(' ', '_').replace("'", "").replace("/", "_")

def create_spell_file(spell_name, spell_info, spells_db, level_folder):
    """Create a spell markdown file"""
    spell_id = get_spell_id_from_name(spell_name)
    
    # Get full spell details
    full_spell = spells_db.get(spell_id)
    if not full_spell:
        # Try to find by name match
        for s_id, spell in spells_db.items():
            if spell['name'].lower() == spell_name.lower():
                full_spell = spell
                break
    
    if not full_spell:
        print(f"Warning: Could not find full details for {spell_name}")
        return False
    
    # Create filename
    filename = spell_name.replace("'", "").replace(" ", "_").replace("/", "_") + ".md"
    filepath = level_folder / filename
    
    # Extract properties
    concentration = full_spell.get('concentration', False)
    ritual = full_spell.get('ritual', False)
    material = full_spell.get('material', False)
    school = full_spell.get('school', 'Unknown')
    level = full_spell.get('level', 0)
    
    # Build components string
    components_list = []
    if concentration:
        components_list.append("Concentration")
    if ritual:
        components_list.append("Ritual")
    if material:
        components_list.append("Material")
    components_str = ", ".join(components_list) if components_list else "None"
    
    # Get spell details
    casting_time = full_spell.get('casting_time', 'Not available')
    range_info = full_spell.get('range', 'Not available')
    components_full = full_spell.get('components', 'Not available')
    duration = full_spell.get('duration', 'Not available')
    description = full_spell.get('description', 'Not available')
    at_higher_levels = full_spell.get('at_higher_levels', '')
    
    # Create frontmatter
    frontmatter = f"""---
spell_name: {spell_name}
spell_level: {level}
spell_school: {school}
spell_class: Cleric
properties: {components_str}
---"""
    
    # Create content
    level_text = "Cantrip" if level == 0 else f"Level {level}"
    concentration_str = 'Yes' if concentration else 'No'
    ritual_str = 'Yes' if ritual else 'No'
    
    content = f"""{frontmatter}

# {spell_name}

**Level:** {level_text}  
**School:** {school}  
**Class:** Cleric

## Properties

- **{components_str}**

## Spell Details

**Casting Time:** {casting_time}

**Range:** {range_info}

**Components:** {components_full}

**Duration:** {duration}

**Description:**

{description}"""

    if at_higher_levels:
        content += f"""

**At Higher Levels:**

{at_higher_levels}"""

    content += f"""

## Quick Reference

- **Concentration:** {concentration_str}
- **Ritual:** {ritual_str}
- **Material Components:** {'Yes' if material else 'No'}

## Quick Links

← **[[Torgga_Brawnanvil_Spells#{"Cantrips" if level == 0 else f"Level {level} Spells"}|Back to Cleric Spell List]]**

---

*This spell file links back to the spellcaster's spell list. Full spell details are available via MCP tools during gameplay.*
"""
    
    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    """Main function"""
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Load databases
    spells_db, spells_by_class = load_databases()
    
    # Get all Cleric spells (levels 0-4)
    cleric_spells = spells_by_class.get('cleric', {})
    
    if not cleric_spells:
        print("No Cleric spells found!")
        return
    
    total_created = 0
    
    # Process each level
    for level in range(0, 5):
        level_str = str(level)
        if level_str not in cleric_spells:
            continue
        
        # Create level folder
        if level == 0:
            level_folder = SPELL_DICT_BASE / "Level_0"
        else:
            level_folder = SPELL_DICT_BASE / f"Level_{level}"
        
        level_folder.mkdir(parents=True, exist_ok=True)
        
        level_spells = cleric_spells[level_str]
        level_name = "Cantrips" if level == 0 else f"Level {level} Spells"
        
        print(f"\nCreating {len(level_spells)} {level_name}...")
        
        created = 0
        for spell_data in level_spells:
            spell_name = spell_data['name']
            if create_spell_file(spell_name, spell_data, spells_db, level_folder):
                created += 1
                print(f"  ✓ {spell_name}")
            else:
                print(f"  ✗ Failed: {spell_name}")
        
        total_created += created
        print(f"  ✅ Created {created}/{len(level_spells)} {level_name}")
    
    print(f"\n✅ Complete! Created {total_created} Cleric spell files.")

if __name__ == "__main__":
    main()
