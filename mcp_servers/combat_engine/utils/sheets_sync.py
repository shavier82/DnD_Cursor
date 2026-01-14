"""Google Sheets integration for character data"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import Optional, Dict, Any
import json
from pathlib import Path

from ..models.creature import Creature, CreatureType


class SheetsSync:
    """Google Sheets synchronization"""
    
    def __init__(self, credentials_path: str = "C:\\DnD\\keys\\google_sheets_key.json"):
        """Initialize Google Sheets client"""
        self.credentials_path = credentials_path
        self.client = None
        self.sheet = None
        
    def connect(self) -> bool:
        """Connect to Google Sheets"""
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_path, scope
            )
            self.client = gspread.authorize(creds)
            
            # Open the D&D Character Sheet
            self.sheet = self.client.open("DnD Character Sheet")
            return True
        except Exception as e:
            print(f"Failed to connect to Google Sheets: {e}")
            return False
    
    def get_character_sheet(self, character_name: str) -> Optional[gspread.Worksheet]:
        """Get worksheet for a specific character"""
        if not self.sheet:
            if not self.connect():
                return None
        
        try:
            # Try to find worksheet by character name
            worksheet = self.sheet.worksheet(character_name)
            return worksheet
        except gspread.WorksheetNotFound:
            print(f"Character sheet not found: {character_name}")
            return None
    
    def load_character_data(self, character_name: str) -> Optional[Dict[str, Any]]:
        """Load character data from Google Sheets
        
        Returns a dict with all character stats suitable for creating a Creature
        """
        worksheet = self.get_character_sheet(character_name)
        if not worksheet:
            return None
        
        try:
            # Standard character sheet layout (adjust based on your actual sheet structure)
            data = {
                "name": worksheet.acell("B1").value or character_name,
                "class": worksheet.acell("B2").value or "Unknown",
                "level": int(worksheet.acell("B3").value or 1),
                
                # Core stats
                "max_hp": int(worksheet.acell("B5").value or 10),
                "current_hp": int(worksheet.acell("B6").value or 10),
                "temp_hp": int(worksheet.acell("B7").value or 0),
                "ac": int(worksheet.acell("B8").value or 10),
                
                # Ability scores
                "strength": int(worksheet.acell("B10").value or 10),
                "dexterity": int(worksheet.acell("B11").value or 10),
                "constitution": int(worksheet.acell("B12").value or 10),
                "intelligence": int(worksheet.acell("B13").value or 10),
                "wisdom": int(worksheet.acell("B14").value or 10),
                "charisma": int(worksheet.acell("B15").value or 10),
                
                # Combat stats
                "speed": int(worksheet.acell("B17").value or 30),
                "initiative_bonus": int(worksheet.acell("B18").value or 0),
                
                # Resources
                "spell_slots": {},  # Would need to parse spell slot info
            }
            
            return data
            
        except Exception as e:
            print(f"Error loading character data: {e}")
            return None
    
    def update_hp(self, character_name: str, current_hp: int, temp_hp: int = 0) -> bool:
        """Update character HP in Google Sheets"""
        worksheet = self.get_character_sheet(character_name)
        if not worksheet:
            return False
        
        try:
            worksheet.update_acell("B6", str(current_hp))
            worksheet.update_acell("B7", str(temp_hp))
            return True
        except Exception as e:
            print(f"Error updating HP: {e}")
            return False
    
    def update_spell_slots(self, character_name: str, spell_slots: Dict[int, int]) -> bool:
        """Update spell slots in Google Sheets"""
        worksheet = self.get_character_sheet(character_name)
        if not worksheet:
            return False
        
        try:
            # Assuming spell slots are in rows 20-29 (levels 1-9)
            # Adjust based on actual sheet layout
            for level, slots in spell_slots.items():
                if 1 <= level <= 9:
                    row = 19 + level
                    worksheet.update_acell(f"B{row}", str(slots))
            return True
        except Exception as e:
            print(f"Error updating spell slots: {e}")
            return False
    
    def batch_update_after_combat(
        self,
        character_name: str,
        hp: int,
        temp_hp: int = 0,
        spell_slots: Optional[Dict[int, int]] = None
    ) -> bool:
        """Batch update character data after combat (more efficient)"""
        worksheet = self.get_character_sheet(character_name)
        if not worksheet:
            return False
        
        try:
            updates = [
                {"range": "B6", "values": [[str(hp)]]},
                {"range": "B7", "values": [[str(temp_hp)]]},
            ]
            
            if spell_slots:
                for level, slots in spell_slots.items():
                    if 1 <= level <= 9:
                        row = 19 + level
                        updates.append({"range": f"B{row}", "values": [[str(slots)]]})
            
            worksheet.batch_update(updates)
            return True
            
        except Exception as e:
            print(f"Error in batch update: {e}")
            return False


# Global singleton
_sheets_sync = None


def get_sheets_sync() -> SheetsSync:
    """Get or create the global SheetsSync instance"""
    global _sheets_sync
    if _sheets_sync is None:
        _sheets_sync = SheetsSync()
    return _sheets_sync


def load_character_from_sheets(character_name: str) -> Optional[Creature]:
    """Load a character from Google Sheets and create a Creature
    
    Args:
        character_name: Name of character sheet in Google Sheets
    
    Returns:
        Creature object or None if failed
    """
    sync = get_sheets_sync()
    data = sync.load_character_data(character_name)
    
    if not data:
        return None
    
    try:
        creature = Creature(
            creature_id=character_name.lower().replace(" ", "_"),
            name=data["name"],
            creature_type=CreatureType.PLAYER,
            max_hp=data["max_hp"],
            current_hp=data["current_hp"],
            temp_hp=data.get("temp_hp", 0),
            ac=data["ac"],
            strength=data["strength"],
            dexterity=data["dexterity"],
            constitution=data["constitution"],
            intelligence=data["intelligence"],
            wisdom=data["wisdom"],
            charisma=data["charisma"],
            initiative_bonus=data.get("initiative_bonus", 0),
            speed=data.get("speed", 30),
            spell_slots=data.get("spell_slots", {}),
            source="google_sheets",
        )
        return creature
    except Exception as e:
        print(f"Error creating Creature from sheets data: {e}")
        return None


def sync_hp_to_sheets(character_name: str, current_hp: int, temp_hp: int = 0) -> bool:
    """Sync HP back to Google Sheets
    
    Args:
        character_name: Name of character sheet
        current_hp: Current HP value
        temp_hp: Temporary HP value
    
    Returns:
        True if successful, False otherwise
    """
    sync = get_sheets_sync()
    return sync.update_hp(character_name, current_hp, temp_hp)


def sync_combat_data_to_sheets(
    character_name: str,
    hp: int,
    temp_hp: int = 0,
    spell_slots: Optional[Dict[int, int]] = None
) -> bool:
    """Batch sync all combat data to sheets after combat ends
    
    Args:
        character_name: Name of character sheet
        hp: Current HP
        temp_hp: Temporary HP
        spell_slots: Remaining spell slots by level
    
    Returns:
        True if successful, False otherwise
    """
    sync = get_sheets_sync()
    return sync.batch_update_after_combat(character_name, hp, temp_hp, spell_slots)




