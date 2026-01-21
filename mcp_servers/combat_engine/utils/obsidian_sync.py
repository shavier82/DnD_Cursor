"""Obsidian integration for real-time combat data sync"""

import re
from pathlib import Path
from typing import Optional, Dict, Any, Tuple


class ObsidianSync:
    """Sync combat data to Obsidian character sheets in real-time"""
    
    def __init__(self, vault_path: str = "C:/Users/ksist/Documents/Obsidian"):
        """Initialize Obsidian sync"""
        self.vault_path = Path(vault_path)
        self.characters_path = self.vault_path / "DnD" / "Player Characters"
    
    def _read_character_file(self, character_name: str) -> Optional[str]:
        """Read character markdown file - handles both 'Name Name' and 'Name_Name' formats"""
        # Try original name first
        char_file = self.characters_path / f"{character_name}.md"
        if char_file.exists():
            return char_file.read_text(encoding="utf-8")
        
        # Try with spaces replaced by underscores
        char_file_underscore = self.characters_path / f"{character_name.replace(' ', '_')}.md"
        if char_file_underscore.exists():
            return char_file_underscore.read_text(encoding="utf-8")
        
        # Try with underscores replaced by spaces
        char_file_space = self.characters_path / f"{character_name.replace('_', ' ')}.md"
        if char_file_space.exists():
            return char_file_space.read_text(encoding="utf-8")
        
        return None
    
    def get_spell_slots(self, character_name: str) -> Dict[int, Tuple[int, int]]:
        """Get current spell slots from Obsidian file. Returns dict of {level: (remaining, maximum)}"""
        content = self._read_character_file(character_name)
        if not content:
            return {}
        
        spell_slots = {}
        for level in range(1, 10):
            pattern = rf'\*\*Level {level}:\*\*\s*[●○]+\s*\((\d+)/(\d+)\)'
            match = re.search(pattern, content)
            if match:
                remaining = int(match.group(1))
                maximum = int(match.group(2))
                spell_slots[level] = (remaining, maximum)
        
        return spell_slots
    
    def _write_character_file(self, character_name: str, content: str):
        """Write to character markdown file - handles both 'Name Name' and 'Name_Name' formats"""
        # Try original name first
        char_file = self.characters_path / f"{character_name}.md"
        if char_file.exists():
            char_file.write_text(content, encoding="utf-8")
            return
        
        # Try with spaces replaced by underscores
        char_file_underscore = self.characters_path / f"{character_name.replace(' ', '_')}.md"
        if char_file_underscore.exists():
            char_file_underscore.write_text(content, encoding="utf-8")
            return
        
        # Try with underscores replaced by spaces
        char_file_space = self.characters_path / f"{character_name.replace('_', ' ')}.md"
        if char_file_space.exists():
            char_file_space.write_text(content, encoding="utf-8")
            return
        
        # If none exist, create with underscores (preferred format)
        char_file_underscore = self.characters_path / f"{character_name.replace(' ', '_')}.md"
        char_file_underscore.parent.mkdir(parents=True, exist_ok=True)
        char_file_underscore.write_text(content, encoding="utf-8")
    
    def get_spell_slots(self, character_name: str) -> Dict[int, Tuple[int, int]]:
        """Get current spell slots from Obsidian file. Returns dict of {level: (remaining, maximum)}"""
        content = self._read_character_file(character_name)
        if not content:
            return {}
        
        spell_slots = {}
        for level in range(1, 10):
            pattern = rf'\*\*Level {level}:\*\*\s*[●○]+\s*\((\d+)/(\d+)\)'
            match = re.search(pattern, content)
            if match:
                remaining = int(match.group(1))
                maximum = int(match.group(2))
                spell_slots[level] = (remaining, maximum)
        
        return spell_slots
    
    def update_hp(self, character_name: str, current_hp: int, max_hp: int) -> bool:
        """Update character HP in Obsidian"""
        try:
            content = self._read_character_file(character_name)
            if not content:
                return False
            
            # Update HP line (format: **HP: 35/52)
            content = re.sub(
                r'\*\*HP:\s*\d+/\d+',
                f'**HP: {current_hp}/{max_hp}',
                content
            )
            
            self._write_character_file(character_name, content)
            return True
        except Exception as e:
            print(f"Error updating HP for {character_name}: {e}")
            return False
    
    def add_condition(self, character_name: str, condition: str, duration: str = "") -> bool:
        """Add a condition to character sheet"""
        try:
            content = self._read_character_file(character_name)
            if not content:
                return False
            
            # Find or create Conditions section
            condition_text = f"- **{condition}**" + (f" ({duration})" if duration else "")
            
            if "## Active Conditions" in content:
                # Add to existing section
                content = content.replace(
                    "## Active Conditions",
                    f"## Active Conditions\n{condition_text}"
                )
            else:
                # Create new section after Combat Stats
                content = content.replace(
                    "## Combat Stats",
                    f"## Combat Stats\n\n## Active Conditions\n{condition_text}\n"
                )
            
            self._write_character_file(character_name, content)
            return True
        except Exception as e:
            print(f"Error adding condition for {character_name}: {e}")
            return False
    
    def remove_condition(self, character_name: str, condition: str) -> bool:
        """Remove a condition from character sheet"""
        try:
            content = self._read_character_file(character_name)
            if not content:
                return False
            
            # Remove the condition line
            content = re.sub(
                rf'- \*\*{condition}\*\*[^\n]*\n',
                '',
                content
            )
            
            self._write_character_file(character_name, content)
            return True
        except Exception as e:
            print(f"Error removing condition for {character_name}: {e}")
            return False
    
    def update_spell_slots(self, character_name: str, level: int, slots_remaining: int, slots_max: int = None) -> bool:
        """Update spell slots in Obsidian (## Spell Slots section)"""
        try:
            content = self._read_character_file(character_name)
            if not content:
                return False
            
            # If slots_max not provided, try to read it from the file
            if slots_max is None:
                pattern_read = rf'\*\*Level {level}:\*\*\s*[●○]+\s*\((\d+)/(\d+)\)'
                match = re.search(pattern_read, content)
                if match:
                    slots_max = int(match.group(2))
                else:
                    # Default to slots_remaining if can't find max
                    slots_max = slots_remaining
            
            # Update in ## Spell Slots section (format: **Level X:** ●●● (3/4))
            pattern = rf'\*\*Level {level}:\*\*\s*[●○]+\s*\(\d+/\d+\)'
            
            # Calculate dots: ● for remaining, ○ for used
            dots = "●" * slots_remaining + "○" * (slots_max - slots_remaining)
            replacement = f'**Level {level}:** {dots} ({slots_remaining}/{slots_max})'
            
            content = re.sub(pattern, replacement, content)
            
            self._write_character_file(character_name, content)
            return True
        except Exception as e:
            print(f"Error updating spell slots for {character_name}: {e}")
            return False
    
    def update_resource(self, character_name: str, resource_name: str, current: int, maximum: int) -> bool:
        """Update class resources (Rage, Ki, Channel Divinity, Superiority Dice, etc.)"""
        try:
            content = self._read_character_file(character_name)
            if not content:
                return False
            
            # Normalize resource name: Convert "superiority_dice" → "Superiority Dice" etc.
            # Try both the original name and a title-case space-separated version
            resource_variants = [
                resource_name,  # Original (e.g., "rage")
                resource_name.replace("_", " ").title(),  # "superiority_dice" → "Superiority Dice"
                resource_name.replace("_", " "),  # "superiority_dice" → "superiority dice"
            ]
            
            dots = "●" * current + "○" * (maximum - current)
            updated = False
            
            for variant in resource_variants:
                # Format 1: **Superiority Dice:** ●●●● (4/4, d8s)
                pattern1 = rf'\*\*{re.escape(variant)}:\*\*\s*[●○]+\s*\((\d+)/(\d+)(?:,\s*[^)]+)?\)'
                if re.search(pattern1, content, re.IGNORECASE):
                    def replacer(match):
                        extra_info = match.group(0).split(',', 1)[1].rsplit(')', 1)[0] if ',' in match.group(0) else ''
                        suffix = f', {extra_info.strip()}' if extra_info.strip() else ''
                        return f'**{variant}:** {dots} ({current}/{maximum}{suffix})'
                    content = re.sub(pattern1, replacer, content, flags=re.IGNORECASE)
                    updated = True
                    break
                
                # Format 2: **rage:** ●●● (3/3)
                pattern2 = rf'\*\*{re.escape(variant)}:\*\*\s*[●○]+\s*\((\d+)/(\d+)\)'
                if re.search(pattern2, content, re.IGNORECASE):
                    content = re.sub(pattern2, f'**{variant}:** {dots} ({current}/{maximum})', content, flags=re.IGNORECASE)
                    updated = True
                    break
                
                # Format 3: **rage:** 3/3
                pattern3 = rf'\*\*{re.escape(variant)}:\*\*\s*\d+/\d+'
                if re.search(pattern3, content, re.IGNORECASE):
                    content = re.sub(pattern3, f'**{variant}:** {current}/{maximum}', content, flags=re.IGNORECASE)
                    updated = True
                    break
            
            if not updated:
                print(f"Warning: Could not find resource '{resource_name}' (tried variants: {resource_variants}) in {character_name}'s sheet")
                return False
            
            self._write_character_file(character_name, content)
            return True
        except Exception as e:
            print(f"Error updating {resource_name} for {character_name}: {e}")
            return False


# Global instance
_obsidian_sync = None

def get_obsidian_sync() -> ObsidianSync:
    """Get or create the global Obsidian sync instance"""
    global _obsidian_sync
    if _obsidian_sync is None:
        _obsidian_sync = ObsidianSync()
    return _obsidian_sync


# Convenience functions for combat-engine
def sync_hp_to_obsidian(character_name: str, current_hp: int, max_hp: int) -> bool:
    """Sync HP to Obsidian (replaces Google Sheets sync)"""
    return get_obsidian_sync().update_hp(character_name, current_hp, max_hp)


def sync_condition_to_obsidian(character_name: str, condition: str, duration: str = "") -> bool:
    """Add condition to Obsidian"""
    return get_obsidian_sync().add_condition(character_name, condition, duration)


def remove_condition_from_obsidian(character_name: str, condition: str) -> bool:
    """Remove condition from Obsidian"""
    return get_obsidian_sync().remove_condition(character_name, condition)


def sync_spell_slots_to_obsidian(character_name: str, level: int, slots_remaining: int, slots_max: int = None) -> bool:
    """Sync spell slot usage to Obsidian"""
    return get_obsidian_sync().update_spell_slots(character_name, level, slots_remaining, slots_max)


def sync_resource_to_obsidian(character_name: str, resource_name: str, current: int, maximum: int) -> bool:
    """Sync class resource usage to Obsidian (Rage, Ki, etc.)"""
    return get_obsidian_sync().update_resource(character_name, resource_name, current, maximum)


def load_character_from_obsidian(character_name: str):
    """Load a character from Obsidian and create a Creature
    
    Args:
        character_name: Name of character file in Obsidian (e.g., 'Torgga_Brawnanvil')
    
    Returns:
        Creature object or None if failed
    """
    from models.creature import Creature, CreatureType
    
    sync = get_obsidian_sync()
    content = sync._read_character_file(character_name)
    if not content:
        return None
    
    try:
        stats = {}
        
        # Extract name
        name_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if name_match:
            stats["name"] = name_match.group(1).strip()
        else:
            stats["name"] = character_name.replace("_", " ")
        
        # Extract HP (format: **HP: 35/52)
        hp_match = re.search(r'\*\*HP:\s*(\d+)/(\d+)', content)
        if hp_match:
            stats["current_hp"] = int(hp_match.group(1))
            stats["max_hp"] = int(hp_match.group(2))
        else:
            return None  # HP is required
        
        # Extract AC
        ac_match = re.search(r'\*\*AC:\*\*\s*(\d+)', content)
        if ac_match:
            stats["ac"] = int(ac_match.group(1))
        else:
            stats["ac"] = 10  # Default
        
        # Extract Speed
        speed_match = re.search(r'\*\*Speed:\*\*\s*(\d+)', content)
        if speed_match:
            stats["speed"] = int(speed_match.group(1))
        else:
            stats["speed"] = 30  # Default
        
        # Extract Initiative bonus
        init_match = re.search(r'\*\*Initiative:\*\*\s*([+-]?\d+)', content)
        if init_match:
            stats["initiative_bonus"] = int(init_match.group(1))
        else:
            stats["initiative_bonus"] = 0  # Default
        
        # Extract ability scores from table
        ability_pattern = r'\|\s*(\w{3})\s*\|\s*(\d+)\s*\|\s*([+-]?\d+)\s*\|'
        for match in re.finditer(ability_pattern, content):
            ability = match.group(1).lower()
            score = int(match.group(2))
            if ability == 'str':
                stats["strength"] = score
            elif ability == 'dex':
                stats["dexterity"] = score
            elif ability == 'con':
                stats["constitution"] = score
            elif ability == 'int':
                stats["intelligence"] = score
            elif ability == 'wis':
                stats["wisdom"] = score
            elif ability == 'cha':
                stats["charisma"] = score
        
        # Set defaults for missing abilities
        if "strength" not in stats:
            stats["strength"] = 10
        if "dexterity" not in stats:
            stats["dexterity"] = 10
        if "constitution" not in stats:
            stats["constitution"] = 10
        if "intelligence" not in stats:
            stats["intelligence"] = 10
        if "wisdom" not in stats:
            stats["wisdom"] = 10
        if "charisma" not in stats:
            stats["charisma"] = 10
        
        # Get spell slots (optional)
        spell_slots_dict = sync.get_spell_slots(character_name)
        spell_slots = {}
        for level, (remaining, maximum) in spell_slots_dict.items():
            spell_slots[level] = remaining  # Store remaining slots
        
        creature = Creature(
            creature_id=character_name.lower().replace(" ", "_"),
            name=stats["name"],
            creature_type=CreatureType.PLAYER,
            max_hp=stats["max_hp"],
            current_hp=stats["current_hp"],
            temp_hp=0,
            ac=stats["ac"],
            strength=stats["strength"],
            dexterity=stats["dexterity"],
            constitution=stats["constitution"],
            intelligence=stats["intelligence"],
            wisdom=stats["wisdom"],
            charisma=stats["charisma"],
            initiative_bonus=stats["initiative_bonus"],
            speed=stats["speed"],
            spell_slots=spell_slots,
            source="obsidian",
        )
        return creature
    except Exception as e:
        print(f"Error creating Creature from Obsidian data for {character_name}: {e}")
        return None
