#!/usr/bin/env python3
"""
D&D Sourcebook Parser
Extracts structured data from sourcebook text files into JSON database.

This parser handles:
- Monster stat blocks (MM 2024)
- Spell descriptions (PHB 2024)
- Rules and mechanics (PHB 2024, DMG 2024)
- Conditions (PHB 2024)
- Actions (PHB 2024)
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

class SourcebookParser:
    def __init__(self, sourcebooks_dir: str, output_dir: str):
        self.sourcebooks_dir = Path(sourcebooks_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.phb_file = self.sourcebooks_dir / "PlayersHandbook2024.txt"
        self.dmg_file = self.sourcebooks_dir / "DungeonMaster2024.txt"
        self.mm_file = self.sourcebooks_dir / "MonstersManual2024.txt"
    
    def parse_all(self):
        """Parse all sourcebooks and create JSON database files."""
        print("[*] Starting sourcebook parsing...")
        
        # Parse each content type
        print("\n[*] Parsing monsters from Monster Manual...")
        monsters = self.parse_monsters()
        self.save_json("monsters.json", monsters)
        print(f"   [+] Parsed {len(monsters)} monsters")
        
        print("\n[*] Parsing rules from Player's Handbook...")
        rules = self.parse_rules()
        self.save_json("rules.json", rules)
        print(f"   [+] Parsed {len(rules)} rules")
        
        print("\n[*] Parsing conditions from Player's Handbook...")
        conditions = self.parse_conditions()
        self.save_json("conditions.json", conditions)
        print(f"   [+] Parsed {len(conditions)} conditions")
        
        print("\n[*] Parsing spells from Player's Handbook...")
        spells = self.parse_spells()
        self.save_json("spells.json", spells)
        print(f"   [+] Parsed {len(spells)} spells")
        
        print("\n[*] Parsing actions from Player's Handbook...")
        actions = self.parse_actions()
        self.save_json("actions.json", actions)
        print(f"   [+] Parsed {len(actions)} actions")
        
        print("\n[*] Magic items parsing (placeholder for future)...")
        magic_items = {}  # TODO: Implement magic item parsing
        self.save_json("magic_items.json", magic_items)
        
        print("\n[+] Parsing complete! Database created at:", self.output_dir)
        print("\nDatabase files:")
        for file in self.output_dir.glob("*.json"):
            if file.name != "schema.json":
                size = file.stat().st_size
                print(f"  - {file.name} ({size:,} bytes)")
    
    def parse_monsters(self) -> Dict[str, Any]:
        """Parse monster stat blocks from Monster Manual."""
        if not self.mm_file.exists():
            print(f"   [!] Monster Manual not found at {self.mm_file}")
            return {}
        
        monsters = {}
        content = self.mm_file.read_text(encoding='utf-8')
        
        # Split into sections by monster name headers
        # Pattern: Monster name followed by stat block
        # Example: "Aarakocra Aeromancer\nMedium Elemental, Neutral\n\nAC 16"
        
        # Find all monster entries (name + type line + stat block)
        pattern = r'^([A-Z][A-Za-z\' -]+)\n(Tiny|Small|Medium|Large|Huge|Gargantuan) ([^,\n]+)(?:, ([^\n]+))?\n\nAC (\d+)'
        matches = re.finditer(pattern, content, re.MULTILINE)
        
        for match in matches:
            monster_name = match.group(1).strip()
            size = match.group(2)
            creature_type = match.group(3)
            alignment = match.group(4) or "Unaligned"
            ac = int(match.group(5))
            
            # Extract monster_id
            monster_id = monster_name.lower().replace(' ', '_').replace("'", "")
            
            # Extract full stat block (next ~500 characters after match)
            start_pos = match.start()
            end_pos = min(start_pos + 2000, len(content))
            stat_block_text = content[start_pos:end_pos]
            
            # Parse HP
            hp_match = re.search(r'HP (\d+) \(([^\)]+)\)', stat_block_text)
            hp_avg = int(hp_match.group(1)) if hp_match else 0
            hp_dice = hp_match.group(2) if hp_match else ""
            
            # Parse Speed
            speed_match = re.search(r'Speed ([^\n]+)', stat_block_text)
            speed_text = speed_match.group(1) if speed_match else "30 ft."
            speed = self.parse_speed(speed_text)
            
            # Parse CR
            cr_match = re.search(r'CR ([^\s]+)', stat_block_text)
            cr = cr_match.group(1) if cr_match else "0"
            
            # Create monster entry
            monsters[monster_id] = {
                "monster_id": monster_id,
                "name": monster_name,
                "source": "MM 2024",
                "type": creature_type,
                "size": size,
                "alignment": alignment,
                "ac": ac,
                "hp": hp_dice,
                "hp_average": hp_avg,
                "speed": speed,
                "cr": cr,
                "keywords": self.generate_keywords(monster_name, creature_type)
            }
        
        return monsters
    
    def parse_speed(self, speed_text: str) -> Dict[str, int]:
        """Parse speed string into structured format."""
        speeds = {}
        
        # Extract walk speed (first number)
        walk_match = re.search(r'(\d+) ft\.?(?:,|$)', speed_text)
        if walk_match:
            speeds['walk'] = int(walk_match.group(1))
        
        # Extract other speeds
        for speed_type in ['fly', 'swim', 'climb', 'burrow']:
            pattern = f'{speed_type.capitalize()} (\\d+) ft\\.?'
            match = re.search(pattern, speed_text, re.IGNORECASE)
            if match:
                speeds[speed_type] = int(match.group(1))
        
        return speeds
    
    def parse_rules(self) -> Dict[str, Any]:
        """Parse core rules from Player's Handbook."""
        # Start with manual entry for Grapple (since we know it's important)
        rules = {
            "grapple": {
                "rule_id": "grapple",
                "name": "Grapple",
                "type": "combat_action",
                "source": "PHB 2024",
                "category": "Combat",
                "summary": "Attempt to grab and restrain a creature using an Unarmed Strike.",
                "mechanics": {
                    "action_type": "Unarmed Strike option",
                    "target_restriction": "Target must be no more than one size larger than you",
                    "save_dc": "8 + Strength modifier + proficiency bonus",
                    "effect": "Target gains Grappled condition",
                    "escape": "Target can use Action to escape (Athletics or Acrobatics vs your save DC)"
                },
                "full_text": "When you use the Grapple option of an Unarmed Strike, the target must be no more than one size larger than you. The target must succeed on a saving throw (DC = 8 + your Strength modifier + your proficiency bonus) or gain the Grappled condition. While Grappled, the target's speed is 0 and they cannot benefit from bonuses to speed. The condition ends if you are incapacitated or if the target is moved away from you.",
                "related_rules": ["grappled_condition", "unarmed_strike"],
                "keywords": ["grapple", "grab", "restrain", "unarmed", "size", "strength", "athletics"]
            },
            "shove": {
                "rule_id": "shove",
                "name": "Shove",
                "type": "combat_action",
                "source": "PHB 2024",
                "category": "Combat",
                "summary": "Push a creature away or knock it prone using an Unarmed Strike.",
                "mechanics": {
                    "action_type": "Unarmed Strike option",
                    "target_restriction": "Target must be no more than one size larger than you",
                    "save_dc": "8 + Strength modifier + proficiency bonus",
                    "effect": "Target is pushed 5 feet or knocked Prone",
                    "choice": "You choose whether to push or knock prone"
                },
                "full_text": "When you use the Shove option of an Unarmed Strike, the target must be no more than one size larger than you. The target must succeed on a saving throw (DC = 8 + your Strength modifier + your proficiency bonus) or be pushed up to 5 feet away from you or knocked Prone (your choice).",
                "related_rules": ["prone_condition", "unarmed_strike"],
                "keywords": ["shove", "push", "knock prone", "unarmed", "size", "strength"]
            }
        }
        
        # TODO: Parse more rules from PHB (Initiative, Advantage/Disadvantage, etc.)
        # This is a complex parsing task that would require sophisticated pattern matching
        
        return rules
    
    def parse_conditions(self) -> Dict[str, Any]:
        """Parse status conditions from Player's Handbook."""
        conditions = {
            "grappled": {
                "condition_id": "grappled",
                "name": "Grappled",
                "source": "PHB 2024",
                "summary": "Your speed is 0, and you can't benefit from bonuses to speed.",
                "effects": [
                    "Speed becomes 0",
                    "Cannot benefit from bonuses to speed"
                ],
                "ends_when": "The grappler is incapacitated, you are moved out of reach, or you escape using an Action",
                "full_text": "While Grappled, your speed is 0 and you can't benefit from bonuses to speed. The condition ends if your grappler is incapacitated or if you are moved out of your grappler's reach. You can also use your Action to attempt to escape by making an Athletics or Acrobatics check against the grappler's save DC.",
                "keywords": ["grappled", "restrained", "grabbed", "speed", "movement", "escape"]
            },
            "prone": {
                "condition_id": "prone",
                "name": "Prone",
                "source": "PHB 2024",
                "summary": "You are lying on the ground, disadvantaged on attacks and vulnerable to melee attacks.",
                "effects": [
                    "Disadvantage on attack rolls",
                    "Attack rolls against you have Advantage if attacker is within 5 feet",
                    "Attack rolls against you have Disadvantage if attacker is farther than 5 feet",
                    "Costs half movement to stand up"
                ],
                "ends_when": "You stand up (costs half your movement)",
                "full_text": "While Prone, you have Disadvantage on attack rolls. Attack rolls against you have Advantage if the attacker is within 5 feet of you; otherwise, they have Disadvantage. You can end the condition by standing up, which costs an amount of movement equal to half your speed.",
                "keywords": ["prone", "knocked down", "lying", "ground", "disadvantage", "advantage", "stand"]
            }
        }
        
        # TODO: Parse remaining conditions (Blinded, Charmed, Deafened, etc.)
        
        return conditions
    
    def parse_spells(self) -> Dict[str, Any]:
        """Parse spell descriptions from Player's Handbook."""
        spells = {}
        
        # TODO: Implement spell parsing
        # Spells have a consistent format:
        # Spell Name
        # Level School (e.g., "1st-level Evocation")
        # Casting Time, Range, Components, Duration
        # Description
        
        return spells
    
    def parse_actions(self) -> Dict[str, Any]:
        """Parse standard actions from Player's Handbook."""
        actions = {
            "attack": {
                "action_id": "attack",
                "name": "Attack",
                "source": "PHB 2024",
                "action_type": "Action",
                "summary": "Make one or more weapon attacks or Unarmed Strikes.",
                "full_text": "When you take the Attack action, you can make one attack. Various features (such as Extra Attack) can let you make more than one attack with this action. An attack can be a weapon attack or an Unarmed Strike.",
                "keywords": ["attack", "weapon", "unarmed", "strike", "combat"]
            },
            "dash": {
                "action_id": "dash",
                "name": "Dash",
                "source": "PHB 2024",
                "action_type": "Action",
                "summary": "Gain extra movement equal to your speed for the turn.",
                "full_text": "When you take the Dash action, you gain extra movement for the current turn. The increase equals your speed, after applying any modifiers. With a speed of 30 feet, for example, you can move up to 60 feet on your turn if you dash.",
                "keywords": ["dash", "movement", "speed", "run", "move"]
            },
            "dodge": {
                "action_id": "dodge",
                "name": "Dodge",
                "source": "PHB 2024",
                "action_type": "Action",
                "summary": "Focus entirely on avoiding attacks.",
                "full_text": "When you take the Dodge action, you focus entirely on avoiding attacks. Until the start of your next turn, attack rolls against you have Disadvantage, and you make Dexterity saving throws with Advantage. You lose this benefit if you are Incapacitated or if your speed is 0.",
                "keywords": ["dodge", "avoid", "defense", "disadvantage", "advantage", "dexterity"]
            },
            "help": {
                "action_id": "help",
                "name": "Help",
                "source": "PHB 2024",
                "action_type": "Action",
                "summary": "Aid another creature in completing a task or give advantage on an attack.",
                "full_text": "When you take the Help action, you can help another creature complete a task or aid a friendly creature in attacking a creature within 5 feet of you. If you help with a task, the creature you help gains Advantage on the next ability check it makes to perform that task. If you help in combat, the creature you help gains Advantage on the next attack roll against that target.",
                "keywords": ["help", "aid", "assist", "advantage", "support", "teamwork"]
            }
        }
        
        # TODO: Parse remaining actions (Hide, Search, Ready, Disengage, etc.)
        
        return actions
    
    def generate_keywords(self, *texts: str) -> List[str]:
        """Generate searchable keywords from text."""
        keywords = []
        for text in texts:
            # Split on spaces, lowercase, remove punctuation
            words = re.findall(r'\b\w+\b', text.lower())
            keywords.extend(words)
        # Return unique keywords
        return list(set(keywords))
    
    def save_json(self, filename: str, data: Dict[str, Any]):
        """Save data to JSON file."""
        output_file = self.output_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"   [>] Saved {output_file}")

def main():
    """Main entry point for sourcebook parser."""
    sourcebooks_dir = r"C:\DnD\Sourcebooks"
    output_dir = r"C:\DnD\DnD_Cursor\rules_database"
    
    parser = SourcebookParser(sourcebooks_dir, output_dir)
    parser.parse_all()
    
    print("\n[+] Rules database created successfully!")
    print("\nNext steps:")
    print("1. Review the generated JSON files")
    print("2. Run the Rules Database MCP server to enable instant lookups")
    print("3. Test with queries like 'grapple', 'goblin', or 'fireball'")

if __name__ == "__main__":
    main()

