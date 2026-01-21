# System Changelog

## 2026-01-08: Suggested Actions System Implementation

### Overview
Implemented automatic suggested actions generation when entering locations to improve gameplay flow and reduce player uncertainty about available options.

### Changes Made

#### 1. Output Contract Update
- **Changed**: Final output format from 2 blocks to 3 blocks
- **Previous**: `NARRATION`, `ASK`, `PATCH` (PATCH was displayed)
- **New**: `NARRATION`, `ASK`, `ACTIONS` (PATCH is applied but hidden)
- **Location**: `.cursorrules` PLAY CHAT OUTPUT CONTRACT section

#### 2. NARRATOR Agent Enhancement
- **Added**: `suggested_actions` optional field to NARRATOR output schema
- **Responsibility**: NARRATOR must generate suggested actions when entering locations
- **Parsing**: NARRATOR parses location cards for actionable elements:
  - Locked containers (chests, doors, strongboxes) with DC and tool requirements
  - Gates requiring checks (from `mechanics` field)
  - Treasure/loot to search for
  - Items to examine (records, texts, objects)
  - Nearby areas to explore
- **Format**: Array of strings, one action per string
- **Location**: `.cursorrules` ROLE LANES section, `docs/PARALLEL_AGENTS.md`

#### 3. Merge Script Updates
- **File**: `C:\DnD\DnD_Cursor\scripts\merge_outputs.ps1`
- **Changes**:
  - Added extraction of `suggested_actions` from NARRATOR output
  - Added ACTIONS block to final output
  - Removed PATCH from displayed output (still applies to state)
  - Fixed PSObject indexing issues for nested combat state paths
  - Improved hashtable handling for state patches

#### 4. Validation Updates
- **File**: `C:\DnD\DnD_Cursor\scripts\validate_agent_outputs.ps1`
- **Changes**:
  - Added `suggested_actions` as optional field for NARRATOR schema
  - Updated validation to accept optional fields

#### 5. Helper Script Created
- **File**: `C:\DnD\DnD_Cursor\scripts\extract_suggested_actions.ps1`
- **Purpose**: Utility script for parsing location cards to extract actionable elements
- **Usage**: Can be called standalone or integrated into agent workflow

#### 6. Documentation Updates
- **New File**: `docs/SUGGESTED_ACTIONS_SYSTEM.md` - Complete documentation of the suggested actions system
- **Updated**: `docs/PARALLEL_AGENTS.md` - Updated NARRATOR schema and output format
- **Updated**: `docs/TESTING_CHAPTER_1.md` - Changed PATCH to ACTIONS in test checklist
- **Updated**: `VERIFICATION.md` - Updated verification checklist
- **Updated**: `README.md` - Updated output format documentation
- **Updated**: `.cursorrules` - Added suggested actions to ROLE LANES and PLAY CHAT OUTPUT CONTRACT

### Technical Details

#### State Patch Handling Improvements
- Fixed PSObject indexing issues when applying nested patches
- Improved hashtable conversion for combat state updates
- Better handling of turn_narratives array appends
- More robust array handling for patches array

#### Output Format
```
NARRATION:
<text or "(none)">

ASK:
<roll request or "(none)">

ACTIONS:
- Action 1 with requirements
- Action 2 with requirements
(or "(none)" if no actions)
```

### Backward Compatibility
- `suggested_actions` is optional - system works without it
- If NARRATOR doesn't provide suggested_actions, ACTIONS block shows "(none)"
- PATCH is still applied to state, just not displayed (improves UX)
- All existing functionality preserved

### Future Enhancements
- Action priorities/ordering
- Action categories (examine, interact, explore, combat)
- Character-specific actions
- Context-aware suggestions based on party composition
- Dynamic action updates based on completed actions

### Files Modified
1. `.cursorrules` - Added suggested actions rules and updated output contract
2. `scripts/merge_outputs.ps1` - Added ACTIONS block and improved state patching
3. `scripts/validate_agent_outputs.ps1` - Added optional field support
4. `docs/PARALLEL_AGENTS.md` - Updated schemas and workflows
5. `docs/SUGGESTED_ACTIONS_SYSTEM.md` - New comprehensive documentation
6. `docs/TESTING_CHAPTER_1.md` - Updated test checklist
7. `VERIFICATION.md` - Updated verification steps
8. `README.md` - Updated output format

### Files Created
1. `scripts/extract_suggested_actions.ps1` - Helper script for parsing location cards
2. `docs/SUGGESTED_ACTIONS_SYSTEM.md` - Complete system documentation

### Testing
- All existing tests should pass
- New functionality is optional and doesn't break existing workflows
- Validation accepts optional `suggested_actions` field
- Merge script handles missing `suggested_actions` gracefully
































