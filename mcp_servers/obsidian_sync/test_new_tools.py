#!/usr/bin/env python3
"""
Test script for new Obsidian Sync MCP tools
"""

import sys
from pathlib import Path
from obsidian_sync_server import CharacterDataManager, OBSIDIAN_VAULT_PATH

def main():
    print("=" * 60)
    print("TESTING NEW OBSIDIAN SYNC MCP TOOLS")
    print("=" * 60)
    
    char_manager = CharacterDataManager(OBSIDIAN_VAULT_PATH)
    test_character = "Brevin"
    
    # Test 1: Get initial state
    print(f"\n1. Getting current state for {test_character}...")
    char = char_manager.get_character(test_character)
    if char:
        print(f"   ✓ Character found")
        print(f"   Current XP: {char['metadata'].get('xp', 'N/A')}")
        print(f"   Current AC: {char['metadata'].get('ac', 'N/A')}")
    else:
        print(f"   ✗ Character not found!")
        return
    
    # Test 2: Update XP
    print(f"\n2. Testing update_character_xp...")
    try:
        new_xp = 9000
        char_manager.update_character_xp(test_character, new_xp)
        print(f"   ✓ Updated XP to {new_xp}")
        
        # Verify
        char = char_manager.get_character(test_character)
        if char['metadata']['xp'] == new_xp:
            print(f"   ✓ Verified: XP is now {char['metadata']['xp']}")
        else:
            print(f"   ✗ Verification failed: Expected {new_xp}, got {char['metadata']['xp']}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Update Currency
    print(f"\n3. Testing update_character_currency...")
    try:
        char_manager.update_character_currency(test_character, gp=5000, sp=10, cp=25)
        print(f"   ✓ Updated currency to 5000 gp, 10 sp, 25 cp")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 4: Update AC
    print(f"\n4. Testing update_character_ac...")
    try:
        char_manager.update_character_ac(test_character, 17, "Studded Leather +1 (TEST)")
        print(f"   ✓ Updated AC to 17")
        
        # Verify
        char = char_manager.get_character(test_character)
        if char['metadata']['ac'] == 17:
            print(f"   ✓ Verified: AC is now {char['metadata']['ac']}")
        else:
            print(f"   ✗ Verification failed: Expected 17, got {char['metadata']['ac']}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 5: Add Inventory Item
    print(f"\n5. Testing add_inventory_item...")
    try:
        char_manager.add_inventory_item(
            test_character,
            "TEST ITEM - Scroll of Fireball",
            quantity=1,
            item_type="Spell Scroll",
            notes="TESTING - Please ignore"
        )
        print(f"   ✓ Added test item to inventory")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 6: Remove Inventory Item
    print(f"\n6. Testing remove_inventory_item...")
    try:
        char_manager.remove_inventory_item(test_character, "TEST ITEM - Scroll of Fireball")
        print(f"   ✓ Removed test item from inventory")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 7: Restore original values
    print(f"\n7. Restoring original values...")
    try:
        char_manager.update_character_xp(test_character, 8290)
        char_manager.update_character_currency(test_character, gp=4807, sp=7, cp=5)
        char_manager.update_character_ac(test_character, 16, "Studded Leather +1")
        print(f"   ✓ Restored to original state")
    except Exception as e:
        print(f"   ✗ Error restoring: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nCheck Brevin.md in Obsidian to verify changes were applied correctly!")

if __name__ == "__main__":
    main()

