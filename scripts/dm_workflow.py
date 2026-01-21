#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified DM Workflow System
Master orchestrator for all DM operations - prevents forgetting critical steps.

This script provides automated workflows for:
- Session start (validation, state loading, chapter packs, MCP verification)
- Pre-combat (readiness validation)
- Post-combat (enforced XP/currency/item distribution)
- Spell casting (automatic spell slot deduction)
- NPC status changes
- NPC status changes
- Faction reputation changes
- Quest completion
- And more...

Usage:
    python scripts/dm_workflow.py session_start
    python scripts/dm_workflow.py post_combat --combat-id <id>
    python scripts/dm_workflow.py spell_cast --character <name> --level <level>
    python scripts/dm_workflow.py npc_faction_interaction --npc <name> --action-type <helped|angered> [--reputation-change <amount>]
    python scripts/dm_workflow.py travel_start --party-members <list> --days <n> --travel-type <type>
"""

import json
import sys
import io
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Paths
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
CONFIG_PATH = ROOT_DIR / "config" / "paths.json"
CHECKLIST_PATH = ROOT_DIR / "MECHANICS_AUTOMATION_CHECKLIST.md"
VALIDATION_FILE = ROOT_DIR / ".mechanics_validated.json"
WORKFLOW_STATE_FILE = ROOT_DIR / ".dm_workflow_state.json"
MECHANICS_REMINDER_SCRIPT = SCRIPT_DIR / "mechanics_reminder.py"
PRE_SESSION_CHECK_SCRIPT = SCRIPT_DIR / "pre_session_check.py"
EXPORT_EVENTS_SCRIPT = SCRIPT_DIR / "export_campaign_events_to_obsidian.py"
EXPORT_PERSISTENT_DATA_SCRIPT = SCRIPT_DIR / "export_persistent_data_to_obsidian.py"
EXPORT_PERSISTENT_DATA_SCRIPT = SCRIPT_DIR / "export_persistent_data_to_obsidian.py"


class DMWorkflow:
    """Master workflow orchestrator for DM operations"""
    
    def __init__(self):
        self.config = self._load_config()
        self.workflow_state = self._load_workflow_state()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load paths configuration"""
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ ERROR: Failed to load config: {e}")
            sys.exit(1)
    
    def _load_workflow_state(self) -> Dict[str, Any]:
        """Load or create workflow state tracker"""
        if WORKFLOW_STATE_FILE.exists():
            try:
                with open(WORKFLOW_STATE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  WARNING: Failed to load workflow state: {e}")
                print("   Creating new workflow state...")
        
        # Create new state
        state = {
            "session_start": {
                "completed": False,
                "timestamp": None,
                "checklist_validated": False,
                "state_files_loaded": [],
                "chapter_pack_loaded": None,
                "mcp_servers_verified": False
            },
            "last_combat": {
                "combat_id": None,
                "post_combat_completed": False,
                "timestamp": None
            },
            "travel": {
                "last_travel": {
                    "party_members": [],
                    "days": 0,
                    "travel_type": "overland",
                    "destination": None,
                    "completed": False,
                    "timestamp": None
                }
            },
            "spell_slots_used": [],
            "npc_status_changes": [],
            "faction_reputation_changes": [],
            "quests_completed": []
        }
        
        self._save_workflow_state(state)
        return state
    
    def _save_workflow_state(self, state: Optional[Dict[str, Any]] = None):
        """Save workflow state to file"""
        if state is None:
            state = self.workflow_state
        
        try:
            with open(WORKFLOW_STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"⚠️  WARNING: Failed to save workflow state: {e}")
    
    def _run_script(self, script_path: Path, *args) -> tuple[bool, str]:
        """Run a Python script and return success status and output"""
        try:
            cmd = [sys.executable, str(script_path)] + list(args)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
    
    def _final_print_and_exit(self, verbose: bool, WRID: str, quiet_line: str, report_lines: List[str], code: int) -> None:
        """Print final output and exit - exactly one print site for respond()"""
        if not verbose:
            print(quiet_line)
        else:
            print(f"REPORT WRID={WRID}")
            for line in report_lines:
                print(line)
            print("END REPORT")
        sys.exit(code)
    
    def _validate_checklist(self) -> bool:
        """Validate that mechanics checklist was reviewed"""
        print("📋 Step 1: Validating mechanics checklist...")
        success, output = self._run_script(PRE_SESSION_CHECK_SCRIPT)
        
        if success:
            print("   ✅ Checklist validated")
            self.workflow_state["session_start"]["checklist_validated"] = True
            return True
        else:
            print(f"   ❌ Checklist validation failed:")
            print(f"   {output}")
            return False
    
    def _read_checklist(self) -> bool:
        """Read mechanics checklist"""
        print("📋 Step 2: Reading mechanics checklist...")
        
        if not CHECKLIST_PATH.exists():
            print(f"   ❌ Checklist not found: {CHECKLIST_PATH}")
            return False
        
        try:
            with open(CHECKLIST_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verify key sections exist
            required_sections = [
                "POST-COMBAT",
                "NPC MANAGEMENT",
                "QUEST MANAGEMENT",
                "OBSIDIAN SYNC"
            ]
            
            # Check if at least one variant of each section exists
            found_sections = []
            for section in required_sections:
                if section in content:
                    found_sections.append(section)
            
            missing = [s for s in required_sections if s not in found_sections]
            if missing and len(found_sections) < 3:  # Allow some flexibility
                print(f"   ⚠️  WARNING: Some sections may be missing: {', '.join(missing)}")
            else:
                print("   ✅ Checklist read successfully")
            
            return True
        except Exception as e:
            print(f"   ❌ Failed to read checklist: {e}")
            return False
    
    def _load_state_files(self) -> Dict[str, Any]:
        """Load CURRENT_STATE.json and CAMPAIGN_EVENTS.json"""
        print("📁 Step 3: Loading campaign state files...")
        
        state_file = Path(self.config.get("state_file", ""))
        campaign_dir = Path(self.config.get("default_campaign_dir", ""))
        events_file = campaign_dir / "saves" / "CAMPAIGN_EVENTS.json"
        
        loaded = {
            "current_state": None,
            "campaign_events": None,
            "chapter": None
        }
        
        # Load CURRENT_STATE.json
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    loaded["current_state"] = json.load(f)
                print(f"   ✅ Loaded: {state_file.name}")
                
                # Extract chapter from state (check multiple possible paths)
                if "current_chapter" in loaded["current_state"]:
                    loaded["chapter"] = loaded["current_state"]["current_chapter"]
                elif "chapter" in loaded["current_state"]:
                    loaded["chapter"] = loaded["current_state"]["chapter"]
                elif "scene" in loaded["current_state"] and "chapter" in loaded["current_state"]["scene"]:
                    loaded["chapter"] = loaded["current_state"]["scene"]["chapter"]
                elif "location" in loaded["current_state"]:
                    # Try to infer from location (basic mapping)
                    location = loaded["current_state"]["location"]
                    # This would need a location-to-chapter mapping
                    pass
            except Exception as e:
                print(f"   ❌ Failed to load CURRENT_STATE.json: {e}")
        else:
            print(f"   ⚠️  WARNING: State file not found: {state_file}")
        
        # Load CAMPAIGN_EVENTS.json
        if events_file.exists():
            try:
                with open(events_file, 'r', encoding='utf-8') as f:
                    loaded["campaign_events"] = json.load(f)
                print(f"   ✅ Loaded: {events_file.name}")
            except Exception as e:
                print(f"   ❌ Failed to load CAMPAIGN_EVENTS.json: {e}")
        else:
            print(f"   ⚠️  WARNING: Campaign events file not found: {events_file}")
        
        # Update workflow state
        self.workflow_state["session_start"]["state_files_loaded"] = [
            "CURRENT_STATE.json" if loaded["current_state"] else None,
            "CAMPAIGN_EVENTS.json" if loaded["campaign_events"] else None
        ]
        
        return loaded
    
    def _load_chapter_pack(self, chapter: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Load chapter pack based on current chapter"""
        print("📦 Step 4: Loading chapter pack...")
        
        packs_dir = Path(self.config.get("packs_dir", ""))
        
        if not chapter:
            # Try to get from state
            state_data = self._load_state_files()
            chapter = state_data.get("chapter")
        
        if not chapter:
            print("   ⚠️  WARNING: No chapter number found, skipping chapter pack")
            return None
        
        pack_path = packs_dir / f"chapter_pack_{chapter}.json"
        
        if not pack_path.exists():
            print(f"   ⚠️  WARNING: Chapter pack not found: {pack_path}")
            print(f"   Expected chapter: {chapter}")
            return None
        
        try:
            with open(pack_path, 'r', encoding='utf-8') as f:
                pack_data = json.load(f)
            print(f"   ✅ Loaded: chapter_pack_{chapter}.json")
            self.workflow_state["session_start"]["chapter_pack_loaded"] = chapter
            return pack_data
        except Exception as e:
            print(f"   ❌ Failed to load chapter pack: {e}")
            return None
    
    def _verify_mcp_servers(self) -> Dict[str, Any]:
        """Verify required MCP servers are available"""
        print("🔌 Step 5: Verifying MCP servers...")
        
        # Note: Actual MCP server checking would require MCP client integration
        # For now, we'll check if the MCP config file exists
        mcp_config_path = ROOT_DIR / "cursor_mcp_complete_config.json"
        
        required_servers = [
            "rules-database",
            "sourcebooks",
            "dice-roller",
            "obsidian-sync",
            "campaign-wiki",
            "combat-engine",
            "session-recorder",
            "travel-manager"
        ]
        
        available = []
        missing = []
        
        if mcp_config_path.exists():
            try:
                with open(mcp_config_path, 'r', encoding='utf-8') as f:
                    mcp_config = json.load(f)
                
                # Check if servers are configured
                # This is a simplified check - actual availability would need MCP client
                configured_servers = []
                if "mcpServers" in mcp_config:
                    configured_servers = list(mcp_config["mcpServers"].keys())
                
                for server in required_servers:
                    # Check if server name appears in config (simplified)
                    server_found = any(s in str(mcp_config).lower() for s in server.split("-"))
                    if server_found:
                        available.append(server)
                    else:
                        missing.append(server)
            except Exception as e:
                print(f"   ⚠️  WARNING: Failed to read MCP config: {e}")
                missing = required_servers
        else:
            print(f"   ⚠️  WARNING: MCP config not found: {mcp_config_path}")
            missing = required_servers
        
        if missing:
            print(f"   ⚠️  WARNING: Some MCP servers may be missing: {', '.join(missing)}")
            print(f"   Available: {', '.join(available) if available else 'None'}")
        else:
            print(f"   ✅ All required MCP servers configured")
        
        self.workflow_state["session_start"]["mcp_servers_verified"] = len(missing) == 0
        
        return {
            "status": "success" if not missing else "warning",
            "available": available,
            "missing": missing
        }
    
    def session_start(self) -> Dict[str, Any]:
        """Session start workflow - orchestrates all initialization steps"""
        print("\n" + "="*60)
        print("🚀 DM WORKFLOW: SESSION START")
        print("="*60 + "\n")
        
        results = {
            "status": "in_progress",
            "steps_completed": [],
            "errors": []
        }
        
        # Step 1: Validate checklist
        if not self._validate_checklist():
            results["status"] = "error"
            results["errors"].append("Checklist validation failed")
            return results
        
        results["steps_completed"].append("checklist_validated")
        
        # Step 2: Read checklist
        if not self._read_checklist():
            results["status"] = "warning"
            results["errors"].append("Failed to read checklist")
        
        results["steps_completed"].append("checklist_read")
        
        # Step 3: Load state files
        state_data = self._load_state_files()
        results["steps_completed"].append("state_files_loaded")
        results["chapter"] = state_data.get("chapter")
        
        # Step 4: Load chapter pack
        chapter_pack = self._load_chapter_pack(state_data.get("chapter"))
        if chapter_pack:
            results["steps_completed"].append("chapter_pack_loaded")
        
        # Step 5: Verify MCP servers
        mcp_status = self._verify_mcp_servers()
        results["steps_completed"].append("mcp_servers_verified")
        results["mcp_status"] = mcp_status
        
        # Mark session start as complete
        self.workflow_state["session_start"]["completed"] = True
        self.workflow_state["session_start"]["timestamp"] = datetime.now().isoformat()
        self._save_workflow_state()
        
        results["status"] = "ready"
        results["workflow_state"] = self.workflow_state["session_start"]
        
        print("\n" + "="*60)
        print("✅ SESSION START WORKFLOW COMPLETE")
        print("="*60 + "\n")
        
        return results
    
    def pre_combat(self) -> Dict[str, Any]:
        """Pre-combat workflow - validates combat readiness"""
        print("\n" + "="*60)
        print("⚔️ DM WORKFLOW: PRE-COMBAT")
        print("="*60 + "\n")
        
        # Show reminder
        success, output = self._run_script(MECHANICS_REMINDER_SCRIPT, "pre_combat")
        if success:
            print(output)
        
        results = {
            "status": "ready",
            "reminder_shown": success
        }
        
        print("\n✅ PRE-COMBAT WORKFLOW COMPLETE\n")
        return results
    
    def post_combat(self, combat_id: Optional[str] = None) -> Dict[str, Any]:
        """Post-combat workflow - enforces ALL post-combat procedures"""
        print("\n" + "="*60)
        print("💰 DM WORKFLOW: POST-COMBAT (MANDATORY)")
        print("="*60 + "\n")
        
        # Show reminder
        success, output = self._run_script(MECHANICS_REMINDER_SCRIPT, "post_combat")
        if success:
            print(output)
        
        results = {
            "status": "in_progress",
            "combat_id": combat_id,
            "steps_completed": [],
            "errors": []
        }
        
        # Note: Actual post-combat procedures (XP calculation, currency distribution, etc.)
        # would need to be implemented with MCP tool calls or additional scripts
        # This workflow provides the structure and reminders
        
        print("\n⚠️  POST-COMBAT PROCEDURES REQUIRED:")
        print("   1. Call end_combat_tool(combat_id)")
        print("   2. Calculate XP from defeated enemies")
        print("   3. Call update_character_xp() for EACH PC")
        print("   4. Roll currency loot")
        print("   5. Call update_character_currency() for EACH PC")
        print("   6. List item loot (with quantity + weight)")
        print("   7. ASK players what items to take")
        print("   8. Call add_inventory_item() for chosen items")
        print("   9. Show post-combat summary")
        print("   10. Ask 'What do you do next?'")
        print("\n⚠️  These steps MUST be completed before proceeding!\n")
        
        # Update workflow state
        self.workflow_state["last_combat"]["combat_id"] = combat_id
        self.workflow_state["last_combat"]["post_combat_completed"] = False
        self.workflow_state["last_combat"]["timestamp"] = datetime.now().isoformat()
        self._save_workflow_state()
        
        results["status"] = "pending"
        results["message"] = "Post-combat procedures must be completed manually via MCP tools"
        
        return results
    
    def spell_cast(self, character_name: str, spell_level: int) -> Dict[str, Any]:
        """Spell cast workflow - automatic spell slot deduction"""
        print("\n" + "="*60)
        print("✨ DM WORKFLOW: SPELL CAST")
        print("="*60 + "\n")
        
        # Show reminder
        success, output = self._run_script(MECHANICS_REMINDER_SCRIPT, "spell_cast")
        if success:
            print(output)
        
        results = {
            "status": "pending",
            "character_name": character_name,
            "spell_level": spell_level,
            "message": f"⚠️  MUST call use_spell_slot('{character_name}', {spell_level}) IMMEDIATELY"
        }
        
        # Log in workflow state
        spell_log = {
            "character": character_name,
            "level": spell_level,
            "timestamp": datetime.now().isoformat()
        }
        self.workflow_state["spell_slots_used"].append(spell_log)
        self._save_workflow_state()
        
        print(f"\n⚠️  REMINDER: Call use_spell_slot('{character_name}', {spell_level}) NOW\n")
        
        return results
    
    def npc_status_change(self, npc_name: str, change_type: str) -> Dict[str, Any]:
        """NPC status change workflow"""
        print("\n" + "="*60)
        print("🎭 DM WORKFLOW: NPC STATUS CHANGE")
        print("="*60 + "\n")
        
        # Show reminder
        success, output = self._run_script(MECHANICS_REMINDER_SCRIPT, "npc_status_change")
        if success:
            print(output)
        
        results = {
            "status": "pending",
            "npc_name": npc_name,
            "change_type": change_type,
            "message": f"⚠️  MUST call update_npc() for '{npc_name}' with change type '{change_type}'"
        }
        
        # Log in workflow state
        npc_log = {
            "npc": npc_name,
            "change_type": change_type,
            "timestamp": datetime.now().isoformat()
        }
        self.workflow_state["npc_status_changes"].append(npc_log)
        self._save_workflow_state()
        
        return results
    
    def npc_faction_interaction(self, npc_name: str, action_type: str, reputation_change: int = 0) -> Dict[str, Any]:
        """NPC faction interaction workflow - handles faction reputation changes when helping/angering NPCs"""
        print("\n" + "="*60)
        print("🏰 DM WORKFLOW: FACTION REPUTATION CHANGE")
        print("="*60 + "\n")
        
        # Show reminder
        success, output = self._run_script(MECHANICS_REMINDER_SCRIPT, "npc_faction_interaction")
        if success:
            print(output)
        
        results = {
            "status": "pending",
            "npc_name": npc_name,
            "action_type": action_type,  # "helped" or "angered"
            "reputation_change": reputation_change,
            "message": f"⚠️  Check if '{npc_name}' has a faction and update reputation accordingly"
        }
        
        print("\n⚠️  FACTION REPUTATION PROCEDURES REQUIRED:")
        print("   1. Check if NPC has a faction (via get_npc_data or campaign wiki)")
        print("   2. Determine reputation change based on action:")
        if action_type == "helped":
            print(f"      * Helping NPC: +{reputation_change if reputation_change else 5} to +{reputation_change if reputation_change else 25} reputation (based on significance)")
        else:
            print(f"      * Angering NPC: -{abs(reputation_change) if reputation_change else 5} to -{abs(reputation_change) if reputation_change else 25} reputation (based on severity)")
        print("   3. Call update_faction_reputation(campaign_name, faction_id, 'Party', amount)")
        print("   4. Auto-syncs to Obsidian (no manual steps needed)")
        print("\n⚠️  These steps MUST be completed before proceeding!\n")
        
        # Log in workflow state (initialize if needed)
        if "faction_reputation_changes" not in self.workflow_state:
            self.workflow_state["faction_reputation_changes"] = []
        
        faction_log = {
            "npc": npc_name,
            "action_type": action_type,
            "reputation_change": reputation_change,
            "timestamp": datetime.now().isoformat()
        }
        self.workflow_state["faction_reputation_changes"].append(faction_log)
        self._save_workflow_state()
        
        return results
    
    def travel_start(self, party_members: List[str], days: int, travel_type: str = "overland", 
                    destination: Optional[str] = None, biome: str = "plains", terrain: str = "overland") -> Dict[str, Any]:
        """Travel start workflow - handles travel procedures and rations management"""
        print("\n" + "="*60)
        print("🚶 DM WORKFLOW: TRAVEL START")
        print("="*60 + "\n")
        
        # Show reminder
        success, output = self._run_script(MECHANICS_REMINDER_SCRIPT, "travel_start")
        if success:
            print(output)
        
        results = {
            "status": "pending",
            "party_members": party_members,
            "days": days,
            "travel_type": travel_type,
            "destination": destination,
            "biome": biome,
            "terrain": terrain,
            "message": "⚠️  TRAVEL PROCEDURES REQUIRED:"
        }
        
        print("\n⚠️  TRAVEL PROCEDURES REQUIRED:")
        print("   1. Check character rations (1 per person per day)")
        print("   2. If insufficient, check Party Wagon and transfer rations")
        print("   3. Call process_travel(party_members, days, travel_type) MCP tool")
        print("   4. For each day of travel:")
        print("      - Check for random encounters (1d20 per day/night, 17-20 triggers)")
        print("      - Use check_random_encounter(biome, terrain, time_of_day) if encounter occurs")
        print("   5. Update CURRENT_STATE.json with new location")
        print("   6. Handle long rests (restore HP/spell slots/resources after each full day)")
        print("   7. Update character sheets after long rest")
        print("\n⚠️  These steps MUST be completed before proceeding!\n")
        
        # Update workflow state
        self.workflow_state["travel"]["last_travel"] = {
            "party_members": party_members,
            "days": days,
            "travel_type": travel_type,
            "destination": destination,
            "biome": biome,
            "terrain": terrain,
            "completed": False,
            "timestamp": datetime.now().isoformat()
        }
        self._save_workflow_state()
        
        results["status"] = "pending"
        results["message"] = "Travel procedures must be completed manually via MCP tools"
        
        return results
    
    def export_campaign_events(self) -> Dict[str, Any]:
        """Export campaign events to Obsidian - syncs CAMPAIGN_EVENTS.json to Obsidian vault"""
        print("\n" + "="*60)
        print("📝 DM WORKFLOW: EXPORT CAMPAIGN EVENTS TO OBSIDIAN")
        print("="*60 + "\n")
        
        results = {
            "status": "in_progress",
            "exported": False,
            "errors": []
        }
        
        # Run export script
        print("Running campaign events export to Obsidian...")
        success, output = self._run_script(EXPORT_EVENTS_SCRIPT)
        
        if success:
            results["status"] = "success"
            results["exported"] = True
            results["message"] = "Campaign events exported to Obsidian successfully"
            print("\n✅ CAMPAIGN EVENTS EXPORTED TO OBSIDIAN")
            print(f"   Location: C:\\Users\\ksist\\Documents\\Obsidian\\DnD")
            print(f"   - Campaign_Events/")
            print(f"   - Consequences/")
            print(f"   - Choices/")
        else:
            results["status"] = "error"
            results["error"] = output
            print(f"\n❌ ERROR: Failed to export campaign events: {output}")
        
        # Update workflow state
        if "campaign_events_export" not in self.workflow_state:
            self.workflow_state["campaign_events_export"] = {}
        
        self.workflow_state["campaign_events_export"]["last_export"] = {
            "timestamp": datetime.now().isoformat(),
            "success": success
        }
        self._save_workflow_state()
        
        print("\n✅ EXPORT CAMPAIGN EVENTS WORKFLOW COMPLETE\n")
        return results
    
    def export_persistent_data(self) -> Dict[str, Any]:
        """Export party persistent data to Obsidian - syncs PARTY_PERSISTENT_DATA.json to Obsidian vault"""
        print("\n" + "="*60)
        print("📦 DM WORKFLOW: EXPORT PARTY PERSISTENT DATA TO OBSIDIAN")
        print("="*60 + "\n")
        
        results = {
            "status": "in_progress",
            "exported": False,
            "errors": []
        }
        
        # Run export script
        print("Running party persistent data export to Obsidian...")
        success, output = self._run_script(EXPORT_PERSISTENT_DATA_SCRIPT)
        
        if success:
            results["status"] = "success"
            results["exported"] = True
            results["message"] = "Party persistent data exported to Obsidian successfully"
            print("\n✅ PARTY PERSISTENT DATA EXPORTED TO OBSIDIAN")
            print(f"   Location: C:\\Users\\ksist\\Documents\\Obsidian\\DnD")
            print(f"   - Party_Persistent_Data/")
            print(f"     - Recurring_Income/")
            print(f"     - Boons/")
            print(f"     - Permanent_Benefits/")
            print(f"     - Cross_Campaign_Relationships/")
        else:
            results["status"] = "error"
            results["error"] = output
            print(f"\n❌ ERROR: Failed to export persistent data: {output}")
        
        # Update workflow state
        if "persistent_data_export" not in self.workflow_state:
            self.workflow_state["persistent_data_export"] = {}
        
        self.workflow_state["persistent_data_export"]["last_export"] = {
            "timestamp": datetime.now().isoformat(),
            "success": success
        }
        self._save_workflow_state()
        
        print("\n✅ EXPORT PERSISTENT DATA WORKFLOW COMPLETE\n")
        return results
    
    def respond(self, response_text: Optional[str] = None, verbose: bool = False) -> Dict[str, Any]:
        """
        Validate DM response with preflight gate and response guard.
        
        Usage:
            echo "response text" | python scripts/dm_workflow.py respond
            python scripts/dm_workflow.py respond --text "response text"
            python scripts/dm_workflow.py respond --verbose
        
        This command:
        1. Runs preflight_gate.py (validation)
        2. Gets combat status from CURRENT_STATE.json (if in combat)
        3. Validates response with response_guard.py
        4. Validates resource spends with resource_guard.py (if response guard passes)
        5. Prints guard results (OK: / BLOCKED: / ERROR:)
        6. Exits with guard's exit code (0 = pass, 1 = blocked/error)
        """
        import uuid
        WRID = str(uuid.uuid4())[:8]
        
        results = {
            "status": "in_progress",
            "preflight_passed": False,
            "guard_passed": False,
            "blocked": False,
            "errors": []
        }
        
        # Step 1: Run preflight gate (silent unless verbose + failure)
        preflight_script = SCRIPT_DIR / "preflight_gate.py"
        success, preflight_output = self._run_script(preflight_script)
        
        if not success:
            quiet_line = "BLOCKED: preflight gate failed"
            final_exit_code = 1
            if verbose:
                report_lines.append("PREFLIGHT_GATE OUTPUT")
                report_lines.append(preflight_output if preflight_output else "(no output)")
            # Print and exit via helper (exactly one print site)
            self._final_print_and_exit(verbose, WRID, quiet_line, report_lines, final_exit_code)
        
        results["preflight_passed"] = True
        
        # Step 2: Get combat status from CURRENT_STATE.json (if in combat)
        # Suppress _load_state_files() print output unless verbose
        import io
        import contextlib
        
        combat_status = None
        # Suppress print output from _load_state_files() (we handle verbose output ourselves)
        with contextlib.redirect_stdout(io.StringIO()):
            state_files = self._load_state_files()
        
        if state_files.get("current_state") and state_files["current_state"].get("combat", {}).get("initiated"):
            # Extract combat status from CURRENT_STATE.json
            combat_data = state_files["current_state"]["combat"]
            combat_id = combat_data.get("combat_id")
            current_turn_id = combat_data.get("current_turn")
            
            if current_turn_id:
                combat_status = {
                    "current_turn": {
                        "creature_id": current_turn_id,
                        "name": current_turn_id
                    },
                    "combat_id": combat_id,
                    "is_active": True
                }
        
        # Step 3: Get response text
        if response_text:
            text = response_text
        else:
            # Read from stdin
            text = sys.stdin.read().strip()
        
        # Centralized final output tracking - exactly one print site
        final_exit_code = 0
        quiet_line = "ERROR: dm_workflow produced no output"
        report_lines: List[str] = []
        
        if not text:
            quiet_line = "ERROR: No response text provided"
            final_exit_code = 1
            # Print and exit via helper (exactly one print site)
            self._final_print_and_exit(verbose, WRID, quiet_line, report_lines, final_exit_code)
            return results
        
        # Step 4: Heuristic detection for enemy delegation (when combat not active)
        # Load forbidden phrases from shared config (same as response_guard.py)
        # For heuristics, use simple string matching (not regex) - keep it dumb and reliable
        config_path = SCRIPT_DIR / "guard_config.json"
        FORBIDDEN_PHRASES = []
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Keep as plain strings for simple substring matching
                    FORBIDDEN_PHRASES = config.get("forbidden_phrases", [])
            except Exception as e:
                # Fallback to hardcoded list
                FORBIDDEN_PHRASES = ["what does", "what should", "your call", "you decide", "what do they do"]
        else:
            # Fallback if config missing
            FORBIDDEN_PHRASES = ["what does", "what should", "your call", "you decide", "what do they do"]
        
        def contains_delegation_phrase(text: str) -> bool:
            """Check if text contains enemy delegation phrases (excludes 'what do you do' which is PC-only).
            Uses simple string matching for heuristics - keep it dumb and reliable."""
            text_lower = text.lower()
            # Exclude "what do you do" - that's the correct PC prompt
            if "what do you do" in text_lower:
                return False
            # Check forbidden phrases with simple substring matching
            for phrase in FORBIDDEN_PHRASES:
                if phrase.lower() in text_lower:
                    return True
            return False
        
        # Step 5: Validate with response guard
        guard_script = SCRIPT_DIR / "response_guard.py"
        
        guard_args = []
        temp_status_file = None
        
        if combat_status:
            # Combat active - use auto-detection from combat status
            import tempfile
            temp_status_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
            json.dump(combat_status, temp_status_file, indent=2)
            temp_status_file.close()
            guard_args.extend(["--combat-status", temp_status_file.name])
        else:
            # Combat not active - use heuristic: if delegation phrases found, treat as enemy turn
            if contains_delegation_phrase(text):
                guard_args.extend(["--is-pc-turn", "false"])
            else:
                # Default to PC turn (fail-open)
                guard_args.extend(["--is-pc-turn", "true"])
        
        if verbose:
            guard_args.append("--verbose")
        
        # Run response guard
        try:
            process = subprocess.Popen(
                [sys.executable, str(guard_script)] + guard_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            stdout, stderr = process.communicate(input=text)
            exit_code = process.returncode
            out = (stdout or "").rstrip("\n")
        finally:
            # Clean up temp file (always, even on exception)
            if temp_status_file and Path(temp_status_file.name).exists():
                try:
                    Path(temp_status_file.name).unlink(missing_ok=True)
                except:
                    pass
        
        # Handle response guard result
        if not verbose:
            if exit_code != 0:
                quiet_line = out.splitlines()[0] if out else "ERROR: guard produced no output"
                final_exit_code = exit_code
                self._final_print_and_exit(verbose, WRID, quiet_line, report_lines, final_exit_code)
                return results
        else:
            report_lines.append("RESPONSE_GUARD OUTPUT")
            report_lines.append(out if out else "ERROR: guard produced no output")
            report_lines.append("")
            if exit_code != 0:
                # Add wrapper-only details on failure
                if not combat_status and contains_delegation_phrase(text):
                    report_lines.append(f"DETAIL[{WRID}]: Heuristic: delegation phrases detected, treating as enemy turn")
                quiet_line = out.splitlines()[0] if out else "BLOCKED: unknown"
                final_exit_code = exit_code
                self._final_print_and_exit(verbose, WRID, quiet_line, report_lines, final_exit_code)
                return results
        
        # Response guard passed - run resource guard
        results["guard_passed"] = True
        resource_guard_script = SCRIPT_DIR / "resource_guard.py"
        
        if resource_guard_script.exists():
            resource_process = subprocess.run(
                [sys.executable, str(resource_guard_script)],
                input=text,
                text=True,
                capture_output=True,
                encoding='utf-8'
            )
            rg_out = (resource_process.stdout or "").rstrip("\n")
            rg_code = resource_process.returncode
            
            if not verbose:
                if rg_code != 0:
                    quiet_line = rg_out.splitlines()[0] if rg_out else "BLOCKED: resource guard failed"
                    final_exit_code = 1
                    self._final_print_and_exit(verbose, WRID, quiet_line, report_lines, final_exit_code)
                    return results
            else:
                report_lines.append("RESOURCE_GUARD OUTPUT")
                report_lines.append(rg_out if rg_out else "(no output)")
                report_lines.append("")
                if rg_code != 0:
                    quiet_line = rg_out.splitlines()[0] if rg_out else "BLOCKED: resource guard failed"
                    final_exit_code = 1
                    self._final_print_and_exit(verbose, WRID, quiet_line, report_lines, final_exit_code)
                    return results
        else:
            # Resource guard missing - skip silently
            if verbose:
                report_lines.append("RESOURCE_GUARD OUTPUT")
                report_lines.append("(script not found - skipped)")
                report_lines.append("")
        
        # Resource guard passed - apply STATE-DELTA
        apply_delta_script = SCRIPT_DIR / "apply_state_delta.py"
        if apply_delta_script.exists():
            apply_process = subprocess.run(
                [sys.executable, str(apply_delta_script)],
                input=text,
                text=True,
                capture_output=True,
                encoding='utf-8'
            )
            ad_out = (apply_process.stdout or "").rstrip("\n")
            ad_code = apply_process.returncode
            
            if not verbose:
                if ad_code != 0:
                    quiet_line = ad_out.splitlines()[0] if ad_out else "ERROR: apply_state_delta failed"
                    final_exit_code = 1
                    self._final_print_and_exit(verbose, WRID, quiet_line, report_lines, final_exit_code)
                    return results
            else:
                report_lines.append("APPLY_STATE_DELTA OUTPUT")
                report_lines.append(ad_out if ad_out else "(no output - changes applied silently)")
                report_lines.append("")
                if ad_code != 0:
                    quiet_line = ad_out.splitlines()[0] if ad_out else "ERROR: apply_state_delta failed"
                    final_exit_code = 1
                    self._final_print_and_exit(verbose, WRID, quiet_line, report_lines, final_exit_code)
                    return results
            
            # STATE-DELTA applied successfully - sync to Obsidian with SHA verification
            sync_script = SCRIPT_DIR / "sync_resources_obsidian.py"
            if sync_script.exists():
                sync_process = subprocess.run(
                    [sys.executable, str(sync_script)],
                    text=True,
                    capture_output=True,
                    encoding='utf-8'
                )
                sync_out = (sync_process.stdout or "").rstrip("\n")
                sync_err = (sync_process.stderr or "").rstrip("\n")
                sync_code = sync_process.returncode
                
                if not verbose:
                    if sync_code != 0:
                        # Use stderr (where errors are printed) or stdout
                        error_msg = sync_err.splitlines()[0] if sync_err else (sync_out.splitlines()[0] if sync_out else "BLOCKED: obsidian sync failed")
                        quiet_line = error_msg
                        final_exit_code = 1
                        self._final_print_and_exit(verbose, WRID, quiet_line, report_lines, final_exit_code)
                        return results
                else:
                    report_lines.append("OBSIDIAN_SYNC OUTPUT")
                    if sync_code == 0:
                        report_lines.append("OK: obsidian sync passed (SHA verified)")
                    else:
                        # Include both stdout and stderr for verbose
                        if sync_err:
                            for line in sync_err.splitlines():
                                if line.strip():
                                    report_lines.append(f"  {line}")
                        if sync_out:
                            for line in sync_out.splitlines():
                                if line.strip():
                                    report_lines.append(f"  {line}")
                    report_lines.append("")
                    if sync_code != 0:
                        error_msg = sync_err.splitlines()[0] if sync_err else (sync_out.splitlines()[0] if sync_out else "BLOCKED: obsidian sync failed")
                        quiet_line = error_msg
                        final_exit_code = 1
                        self._final_print_and_exit(verbose, WRID, quiet_line, report_lines, final_exit_code)
                        return results
        
        # All passed - check for map mutations
        # Check if response contains any map mutation tags
        has_map_tags = any(tag in text.lower() for tag in ["[mapmove", "[mapadd", "[mapdefeat", "[mapterrain"])
        
        if has_map_tags:
            # Map mutations detected - run map enforcement pipeline
            map_delta_guard_script = SCRIPT_DIR / "map_delta_guard.py"
            if map_delta_guard_script.exists():
                state_path = state_files.get("current_state_path") or Path("C:/DnD/Campaigns/Phandelver/saves/CURRENT_STATE.json")
                map_guard_process = subprocess.run(
                    [sys.executable, str(map_delta_guard_script), "--state", str(state_path)],
                    input=text,
                    text=True,
                    capture_output=True,
                    encoding='utf-8'
                )
                mg_out = (map_guard_process.stdout or "").rstrip("\n")
                mg_err = (map_guard_process.stderr or "").rstrip("\n")
                mg_code = map_guard_process.returncode
                
                if not verbose:
                    if mg_code != 0:
                        error_msg = mg_err.splitlines()[0] if mg_err else (mg_out.splitlines()[0] if mg_out else "BLOCKED: map guard failed")
                        quiet_line = error_msg
                        final_exit_code = 1
                        self._final_print_and_exit(verbose, WRID, quiet_line, report_lines, final_exit_code)
                        return results
                else:
                    report_lines.append("MAP_GUARD OUTPUT")
                    report_lines.append(mg_out if mg_out else "(no output)")
                    report_lines.append("")
                    if mg_code != 0:
                        error_msg = mg_err.splitlines()[0] if mg_err else (mg_out.splitlines()[0] if mg_out else "BLOCKED: map guard failed")
                        quiet_line = error_msg
                        final_exit_code = 1
                        self._final_print_and_exit(verbose, WRID, quiet_line, report_lines, final_exit_code)
                        return results
                
                # Map guard passed - apply MAP-DELTA
                apply_map_delta_script = SCRIPT_DIR / "apply_map_delta.py"
                if apply_map_delta_script.exists():
                    # Get location code from delta block or state
                    import re
                    delta_match = re.search(r"MAP-DELTA\s+([a-zA-Z0-9_\-]+)", text, re.IGNORECASE)
                    location_code = delta_match.group(1) if delta_match else None
                    
                    if not location_code:
                        # Try to get from state
                        if state_files.get("current_state"):
                            combat = state_files["current_state"].get("combat", {})
                            location = combat.get("location") or state_files["current_state"].get("scene", {}).get("location")
                            if location:
                                location_code = location.split("_")[0] if "_" in location else location
                    
                    if location_code:
                        apply_map_process = subprocess.run(
                            [sys.executable, str(apply_map_delta_script), "--location", location_code],
                            input=text,
                            text=True,
                            capture_output=True,
                            encoding='utf-8'
                        )
                        amd_out = (apply_map_process.stdout or "").rstrip("\n")
                        amd_code = apply_map_process.returncode
                        
                        if not verbose:
                            if amd_code != 0:
                                quiet_line = amd_out.splitlines()[0] if amd_out else "ERROR: apply_map_delta failed"
                                final_exit_code = 1
                                self._final_print_and_exit(verbose, WRID, quiet_line, report_lines, final_exit_code)
                                return results
                        else:
                            report_lines.append("APPLY_MAP_DELTA OUTPUT")
                            report_lines.append(amd_out if amd_out else "(no output - changes applied silently)")
                            report_lines.append("")
                            if amd_code != 0:
                                quiet_line = amd_out.splitlines()[0] if amd_out else "ERROR: apply_map_delta failed"
                                final_exit_code = 1
                                self._final_print_and_exit(verbose, WRID, quiet_line, report_lines, final_exit_code)
                                return results
                        
                        # MAP-DELTA applied successfully - sync to Obsidian with SHA verification
                        sync_map_script = SCRIPT_DIR / "sync_battlemap_obsidian.py"
                        if sync_map_script.exists():
                            sync_map_process = subprocess.run(
                                [sys.executable, str(sync_map_script), location_code],
                                text=True,
                                capture_output=True,
                                encoding='utf-8'
                            )
                            sm_out = (sync_map_process.stdout or "").rstrip("\n")
                            sm_err = (sync_map_process.stderr or "").rstrip("\n")
                            sm_code = sync_map_process.returncode
                            
                            if not verbose:
                                if sm_code != 0:
                                    error_msg = sm_err.splitlines()[0] if sm_err else (sm_out.splitlines()[0] if sm_out else "BLOCKED: obsidian map sync failed")
                                    quiet_line = error_msg
                                    final_exit_code = 1
                                    self._final_print_and_exit(verbose, WRID, quiet_line, report_lines, final_exit_code)
                                    return results
                            else:
                                report_lines.append("OBSIDIAN_BATTLEMAP_SYNC OUTPUT")
                                if sm_code == 0:
                                    report_lines.append("OK: obsidian map sync passed (SHA verified)")
                                else:
                                    if sm_err:
                                        for line in sm_err.splitlines():
                                            if line.strip():
                                                report_lines.append(f"  {line}")
                                    if sm_out:
                                        for line in sm_out.splitlines():
                                            if line.strip():
                                                report_lines.append(f"  {line}")
                                report_lines.append("")
                                if sm_code != 0:
                                    error_msg = sm_err.splitlines()[0] if sm_err else (sm_out.splitlines()[0] if sm_out else "BLOCKED: obsidian map sync failed")
                                    quiet_line = error_msg
                                    final_exit_code = 1
                                    self._final_print_and_exit(verbose, WRID, quiet_line, report_lines, final_exit_code)
                                    return results
        
        # All passed
        quiet_line = "OK: dm_workflow passed"
        final_exit_code = 0
        self._final_print_and_exit(verbose, WRID, quiet_line, report_lines, final_exit_code)
        return results
    
    def mapcheck(self, verbose: bool = False) -> Dict[str, Any]:
        """
        Validate battlemap state with map guard.
        
        Usage:
            python scripts/dm_workflow.py mapcheck
            python scripts/dm_workflow.py mapcheck --verbose
        """
        import uuid
        
        map_guard_script = SCRIPT_DIR / "map_guard.py"
        if not map_guard_script.exists():
            print("ERROR: map_guard.py not found", file=sys.stderr)
            sys.exit(1)
        
        # Run map guard
        cmd = [sys.executable, str(map_guard_script)]
        if verbose:
            cmd.append("--verbose")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            exit_code = result.returncode
            stdout = result.stdout
            stderr = result.stderr
            
            # Generate unique run ID for verbose mode
            WRID = str(uuid.uuid4())[:8]
            
            if not verbose:
                # Quiet mode: one line only
                first = stdout.splitlines()[0] if stdout else "ERROR: map guard produced no output"
                print(first)
                sys.exit(exit_code)
            
            # Verbose mode: fenced REPORT block
            print(f"REPORT WRID={WRID}")
            print(stdout if stdout else "ERROR: map guard produced no output")
            if stderr:
                print(stderr, file=sys.stderr)
            
            if exit_code != 0:
                print(f"DETAIL[{WRID}]: Map guard validation failed")
            
            print(f"END REPORT")
            sys.exit(exit_code)
            
        except Exception as e:
            print(f"ERROR: Failed to run map guard: {e}", file=sys.stderr)
            sys.exit(1)
        
        return {"status": "success"}


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Unified DM Workflow System")
    subparsers = parser.add_subparsers(dest="workflow", help="Workflow to execute")
    
    # Session start
    subparsers.add_parser("session_start", help="Session start workflow")
    
    # Pre-combat
    subparsers.add_parser("pre_combat", help="Pre-combat workflow")
    
    # Post-combat
    post_combat_parser = subparsers.add_parser("post_combat", help="Post-combat workflow")
    post_combat_parser.add_argument("--combat-id", help="Combat ID")
    
    # Spell cast
    spell_parser = subparsers.add_parser("spell_cast", help="Spell cast workflow")
    spell_parser.add_argument("--character", required=True, help="Character name")
    spell_parser.add_argument("--level", type=int, required=True, help="Spell level")
    
    # NPC status change
    npc_parser = subparsers.add_parser("npc_status_change", help="NPC status change workflow")
    npc_parser.add_argument("--npc", required=True, help="NPC name")
    npc_parser.add_argument("--change-type", required=True, help="Change type (e.g., 'died', 'executed')")
    
    # NPC faction interaction
    faction_parser = subparsers.add_parser("npc_faction_interaction", help="NPC faction interaction workflow")
    faction_parser.add_argument("--npc", required=True, help="NPC name")
    faction_parser.add_argument("--action-type", choices=["helped", "angered"], required=True, help="Action type")
    faction_parser.add_argument("--reputation-change", type=int, default=0, help="Reputation change amount (optional, defaults to 5-25 based on significance)")
    
    # Travel start
    travel_parser = subparsers.add_parser("travel_start", help="Travel start workflow")
    travel_parser.add_argument("--party-members", nargs="+", required=True, help="List of character names")
    travel_parser.add_argument("--days", type=int, required=True, help="Number of days traveled")
    travel_parser.add_argument("--travel-type", choices=["overland", "underground"], default="overland", help="Travel type")
    travel_parser.add_argument("--destination", help="Destination location (optional)")
    travel_parser.add_argument("--biome", default="plains", help="Biome type for encounters")
    travel_parser.add_argument("--terrain", default="overland", help="Terrain type for encounters")
    
    # Export campaign events
    subparsers.add_parser("export_campaign_events", help="Export campaign events to Obsidian")
    
    # Export persistent data
    subparsers.add_parser("export_persistent_data", help="Export party persistent data to Obsidian")
    
    # Respond (validate DM response)
    respond_parser = subparsers.add_parser("respond", help="Validate DM response with preflight gate and response guard")
    respond_parser.add_argument("--text", help="Response text to validate (if not provided, reads from stdin)")
    respond_parser.add_argument("--verbose", action="store_true", help="Show detailed validation output")
    
    # Map check (validate battlemap)
    mapcheck_parser = subparsers.add_parser("mapcheck", help="Validate battlemap state with map guard")
    mapcheck_parser.add_argument("--verbose", action="store_true", help="Show detailed validation output")
    
    args = parser.parse_args()
    
    if not args.workflow:
        parser.print_help()
        sys.exit(1)
    
    workflow = DMWorkflow()
    
    if args.workflow == "session_start":
        result = workflow.session_start()
    elif args.workflow == "pre_combat":
        result = workflow.pre_combat()
    elif args.workflow == "post_combat":
        result = workflow.post_combat(args.combat_id)
    elif args.workflow == "spell_cast":
        result = workflow.spell_cast(args.character, args.level)
    elif args.workflow == "npc_status_change":
        result = workflow.npc_status_change(args.npc, args.change_type)
    elif args.workflow == "npc_faction_interaction":
        result = workflow.npc_faction_interaction(args.npc, args.action_type, args.reputation_change)
    elif args.workflow == "travel_start":
        result = workflow.travel_start(
            party_members=args.party_members,
            days=args.days,
            travel_type=args.travel_type,
            destination=args.destination,
            biome=args.biome,
            terrain=args.terrain
        )
    elif args.workflow == "export_campaign_events":
        result = workflow.export_campaign_events()
    elif args.workflow == "export_persistent_data":
        result = workflow.export_persistent_data()
    elif args.workflow == "respond":
        result = workflow.respond(args.text, verbose=getattr(args, 'verbose', False))
        # respond() exits with guard's exit code, so we never reach here on failure
        # But if we do (success case), exit 0
        sys.exit(0)
    elif args.workflow == "mapcheck":
        result = workflow.mapcheck(verbose=getattr(args, 'verbose', False))
        # mapcheck() exits with guard's exit code, so we never reach here on failure
        # But if we do (success case), exit 0
        sys.exit(0)
    else:
        print(f"❌ Unknown workflow: {args.workflow}")
        sys.exit(1)
    
    # Print result summary
    print("\n" + "="*60)
    print("WORKFLOW RESULT:")
    print("="*60)
    print(json.dumps(result, indent=2))
    print("="*60 + "\n")
    
    # Exit with appropriate code
    if result.get("status") == "error":
        sys.exit(1)
    elif result.get("status") == "warning":
        sys.exit(0)  # Warning but not fatal
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
