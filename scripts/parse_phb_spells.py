#!/usr/bin/env python3
"""
PHB Spells Parser
Extracts spells from Player's Handbook 2024, organized by class and level.

Parses:
- Spell lists by class (Bard, Cleric, Druid, Paladin, Ranger, Sorcerer, Warlock, Wizard)
- Spell level (0-9, where 0 = Cantrip)
- School of magic
- Components (V, S, M, C, R)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any

class PHBSpellsParser:
    def __init__(self, phb_file: str, output_dir: str):
        self.phb_file = Path(phb_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load PHB content
        self.content = self.phb_file.read_text(encoding='utf-8')
        
        # Spell schools
        self.schools = [
            "Abjuration", "Conjuration", "Divination", "Enchantment",
            "Evocation", "Illusion", "Necromancy", "Transmutation"
        ]
        
        # Classes that have spell lists
        self.spell_classes = [
            "Bard", "Cleric", "Druid", "Paladin", "Ranger",
            "Sorcerer", "Warlock", "Wizard"
        ]
    
    def parse_all(self):
        """Parse all spells from PHB."""
        print("[*] Parsing Player's Handbook 2024 spells...\n")
        
        # Parse spell lists for each class
        all_spells = {}
        spells_by_class = {}
        
        for spell_class in self.spell_classes:
            print(f"[*] Parsing {spell_class} spell list...")
            class_spells = self.parse_class_spell_list(spell_class)
            spells_by_class[spell_class.lower()] = class_spells
            
            # Add spells to all_spells dictionary
            for level, spells in class_spells.items():
                for spell in spells:
                    spell_id = spell["spell_id"]
                    if spell_id not in all_spells:
                        all_spells[spell_id] = spell
                    else:
                        # Add this class to the spell's class list
                        if spell_class not in all_spells[spell_id]["classes"]:
                            all_spells[spell_id]["classes"].append(spell_class)
            
            print(f"   [+] Found {sum(len(spells) for spells in class_spells.values())} spells")
        
        # Save results
        self.save_json("spells.json", all_spells)
        self.save_json("spells_by_class.json", spells_by_class)
        
        # Create summary statistics
        total_unique = len(all_spells)
        by_level = {}
        for spell in all_spells.values():
            level = spell["level"]
            by_level[level] = by_level.get(level, 0) + 1
        
        print(f"\n[+] Spell parsing complete!")
        print(f"   - Total unique spells: {total_unique}")
        print(f"   - Cantrips (Level 0): {by_level.get(0, 0)}")
        print(f"   - Level 1-9 spells: {sum(by_level.get(i, 0) for i in range(1, 10))}")
        
        return all_spells
    
    def parse_class_spell_list(self, spell_class: str) -> Dict[int, List[Dict]]:
        """Parse spell list for a specific class."""
        # Find the spell list section for this class
        pattern = f"{spell_class} Spell List.*?(?=\\n[A-Z][a-z]+ Subclasses|\\n[A-Z][a-z]+ Spell List|$)"
        match = re.search(pattern, self.content, re.DOTALL)
        
        if not match:
            print(f"   [!] Could not find {spell_class} spell list")
            return {}
        
        spell_list_text = match.group(0)
        
        # Parse spells by level
        class_spells = {}
        
        # Parse Cantrips (Level 0)
        cantrips = self.parse_spell_level(spell_list_text, "Cantrips (Level 0", 0, spell_class)
        if cantrips:
            class_spells[0] = cantrips
        
        # Parse Level 1-9 spells
        for level in range(1, 10):
            spells = self.parse_spell_level(spell_list_text, f"Level {level} {spell_class} Spells", level, spell_class)
            if spells:
                class_spells[level] = spells
        
        return class_spells
    
    def parse_spell_level(self, text: str, level_header: str, level: int, spell_class: str) -> List[Dict]:
        """Parse spells from a specific level section."""
        # Find the section for this spell level
        pattern = f"{re.escape(level_header)}.*?\\n(.*?)(?=\\nLevel \\d|\\nCantrips|\\n[A-Z][a-z]+ Subclasses|$)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        
        if not match:
            return []
        
        section_text = match.group(1)
        
        # Parse spell table (Spell | School | Special)
        spells = []
        lines = section_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or 'Spell' in line or 'School' in line or 'Special' in line:
                continue
            
            # Try to parse spell line
            # Format: "Spell Name	School	Special"
            parts = re.split(r'\t+', line)
            if len(parts) >= 2:
                spell_name = parts[0].strip()
                school = parts[1].strip()
                special = parts[2].strip() if len(parts) > 2 else ""
                
                # Check if school is valid
                if school in self.schools:
                    spell_id = spell_name.lower().replace(' ', '_').replace("'", "")
                    
                    # Parse special components
                    concentration = 'C' in special
                    ritual = 'R' in special
                    material = 'M' in special
                    
                    spell = {
                        "spell_id": spell_id,
                        "name": spell_name,
                        "level": level,
                        "school": school,
                        "classes": [spell_class],
                        "concentration": concentration,
                        "ritual": ritual,
                        "material": material,
                        "source": "PHB 2024",
                        "keywords": self.generate_keywords(spell_name, school)
                    }
                    
                    spells.append(spell)
        
        return spells
    
    def generate_keywords(self, *texts: str) -> List[str]:
        """Generate searchable keywords from text."""
        keywords = []
        for text in texts:
            words = re.findall(r'\b\w+\b', text.lower())
            keywords.extend(words)
        return list(set(keywords))
    
    def save_json(self, filename: str, data: Dict[str, Any]):
        """Save data to JSON file."""
        output_file = self.output_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"   [>] Saved {output_file}")

def main():
    """Main entry point."""
    phb_file = r"C:\DnD\Sourcebooks\PlayersHandbook2024.txt"
    output_dir = r"C:\DnD\DnD_Cursor\rules_database"
    
    parser = PHBSpellsParser(phb_file, output_dir)
    all_spells = parser.parse_all()
    
    print("\n[+] Spells database created!")
    print("\nFeatures:")
    print("  - Organized by class and spell level")
    print("  - Includes school of magic")
    print("  - Marks concentration, ritual, and material components")
    print("  - Searchable by spell name and keywords")
    print("\nFiles created:")
    print("  - spells.json (all unique spells)")
    print("  - spells_by_class.json (organized by class)")

if __name__ == "__main__":
    main()












