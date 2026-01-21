# Workflow Enforcement Strategy

**How we ensure the AI DM actually uses the workflow system and doesn't forget critical steps.**

---

## The Problem

The workflow system exists, but there's a risk the AI DM might:
- Forget to run workflows
- Skip workflow steps
- Proceed without completing required procedures
- Ignore workflow reminders

**We need multiple layers of enforcement to prevent this.**

---

## Enforcement Layers

### Layer 1: Instructions in `.cursorrules` (Current)

**What it does:**
- Provides clear instructions to run workflows automatically
- States that workflows are "AUTOMATIC" and "BLOCKING"
- Lists all required workflows

**Limitation:**
- These are just instructions - not code-level enforcement
- AI could still forget or skip them

**Status:** ✅ Implemented

---

### Layer 2: Workflow State Tracking (Current)

**What it does:**
- Tracks what workflows have been run in `.dm_workflow_state.json`
- Records timestamps and completion status
- Logs spell slots used, NPC changes, etc.

**Limitation:**
- Tracks what was done, but doesn't prevent skipping

**Status:** ✅ Implemented

---

### Layer 3: Validation Script (NEW)

**What it does:**
- `scripts/validate_workflow_state.py` checks if workflows were actually run
- Validates session start, post-combat, spell slots, etc.
- Provides clear error messages if workflows were skipped

**Usage:**
```bash
# Check if session start workflow was run
python scripts/validate_workflow_state.py --check-session

# Check if post-combat procedures were completed
python scripts/validate_workflow_state.py --check-post-combat

# Check all validations
python scripts/validate_workflow_state.py --check-all
```

**How to use:**
1. **After session start:** Run `--check-session` to verify workflow ran
2. **After combat:** Run `--check-post-combat` to verify procedures completed
3. **Periodically:** Run `--check-all` to verify everything

**Status:** ✅ Implemented

---

### Layer 4: Pre-Operation Checks (RECOMMENDED - Not Yet Implemented)

**What it would do:**
- Before allowing certain operations, check workflow state
- Block operations if prerequisites not met
- Example: Before ending combat, check if post-combat workflow was run

**Implementation ideas:**
1. **MCP Tool Integration:** MCP tools check workflow state before executing
2. **State File Validation:** Scripts validate workflow state before operations
3. **Pre-Commit Hooks:** Validate workflow state before allowing state changes

**Status:** ⚠️ Recommended for future implementation

---

### Layer 5: User Verification (Manual)

**What it does:**
- User can manually check if workflows were run
- User can run validation script to verify
- User can check workflow state file directly

**How to use:**
```bash
# Quick check
python scripts/validate_workflow_state.py --check-all

# Check specific workflow
python scripts/validate_workflow_state.py --check-session

# View workflow state file
cat .dm_workflow_state.json
```

**Status:** ✅ Available now

---

## Current Enforcement Strategy

### For Session Start

**Automatic (via .cursorrules):**
- Instructions say to run `dm_workflow.py session_start`
- Workflow validates checklist and loads all state

**Verification:**
```bash
python scripts/validate_workflow_state.py --check-session
```

**If workflow not run:**
- Validation script will show error
- User can remind AI to run workflow
- Workflow state file will be missing or incomplete

---

### For Post-Combat

**Automatic (via .cursorrules):**
- Instructions say to run `dm_workflow.py post_combat` when combat ends
- Workflow shows reminders and tracks completion

**Verification:**
```bash
python scripts/validate_workflow_state.py --check-post-combat
```

**If workflow not run:**
- Validation script will show error
- Workflow state will show `post_combat_completed: false`
- User can remind AI to complete procedures

---

### For Spell Casting

**Automatic (via .cursorrules):**
- Instructions say to run `dm_workflow.py spell_cast` when spell is cast
- Workflow reminds to call `use_spell_slot()` immediately

**Verification:**
```bash
python scripts/validate_workflow_state.py --check-spell-slots
```

**If workflow not run:**
- Spell slots won't be tracked in workflow state
- Validation script will show warning
- User can check Obsidian to verify spell slots were deducted

---

## Recommended Workflow

### At Session Start

1. **AI should:** Run `python scripts/dm_workflow.py session_start`
2. **User can verify:** Run `python scripts/validate_workflow_state.py --check-session`
3. **If failed:** User reminds AI to run workflow

### After Combat

1. **AI should:** Run `python scripts/dm_workflow.py post_combat --combat-id <id>`
2. **AI should:** Complete ALL post-combat procedures
3. **User can verify:** Run `python scripts/validate_workflow_state.py --check-post-combat`
4. **If failed:** User reminds AI to complete procedures

### When Spell is Cast

1. **AI should:** Run `python scripts/dm_workflow.py spell_cast --character <name> --level <level>`
2. **AI should:** Call `use_spell_slot()` immediately
3. **User can verify:** Check Obsidian or run validation script

---

## Future Enhancements

### 1. MCP Tool Integration

**Idea:** MCP tools check workflow state before executing

**Example:**
```python
# In end_combat_tool():
def end_combat_tool(combat_id):
    # Check if post-combat workflow was run
    if not check_workflow_state("post_combat", combat_id):
        return {
            "error": "Post-combat workflow must be run first",
            "required": "Run: python scripts/dm_workflow.py post_combat --combat-id {combat_id}"
        }
    # Proceed with ending combat
```

**Status:** ⚠️ Recommended for future

---

### 2. Pre-Operation Validation

**Idea:** Scripts validate workflow state before allowing operations

**Example:**
```python
# Before ending combat:
if not validate_workflow_state("post_combat_ready"):
    print("ERROR: Post-combat workflow must be run first")
    sys.exit(1)
```

**Status:** ⚠️ Recommended for future

---

### 3. Workflow State Checks in .cursorrules

**Idea:** Add explicit checks in .cursorrules that AI must verify

**Example:**
```markdown
**Before ending combat, you MUST:**
1. Check workflow state: `python scripts/validate_workflow_state.py --check-post-combat`
2. If error → Run post-combat workflow first
3. Only then proceed with ending combat
```

**Status:** ⚠️ Can be added now

---

### 4. Automated Reminders

**Idea:** Script that periodically checks workflow state and reminds AI

**Example:**
```bash
# Run every 5 minutes during session
python scripts/workflow_reminder.py --check-all --notify
```

**Status:** ⚠️ Recommended for future

---

## How to Use Right Now

### For Users

1. **After session start:** Run validation to verify workflow ran
   ```bash
   python scripts/validate_workflow_state.py --check-session
   ```

2. **After combat:** Run validation to verify procedures completed
   ```bash
   python scripts/validate_workflow_state.py --check-post-combat
   ```

3. **Periodically:** Run full validation
   ```bash
   python scripts/validate_workflow_state.py --check-all
   ```

4. **If validation fails:** Remind AI to run the required workflow

### For AI DM

1. **Always run workflows** as instructed in `.cursorrules`
2. **Check workflow state** if unsure if something was done
3. **Run validation script** before proceeding with critical operations
4. **Follow workflow reminders** - they're there for a reason

---

## Success Metrics

**System is working if:**
- ✅ Validation script shows zero errors after sessions
- ✅ Workflow state file is always up-to-date
- ✅ Post-combat procedures are always completed
- ✅ Spell slots are always deducted
- ✅ User doesn't need to remind AI about workflows

**If these aren't met:**
- Add more enforcement layers
- Strengthen .cursorrules instructions
- Add pre-operation checks
- Integrate with MCP tools

---

## Summary

**Current enforcement:**
1. ✅ Instructions in `.cursorrules` (automatic triggers)
2. ✅ Workflow state tracking (`.dm_workflow_state.json`)
3. ✅ Validation script (`validate_workflow_state.py`)
4. ✅ User verification (manual checks)

**Recommended additions:**
1. ⚠️ MCP tool integration (check workflow state before executing)
2. ⚠️ Pre-operation validation (block operations if prerequisites not met)
3. ⚠️ Automated reminders (periodic checks during session)
4. ⚠️ Workflow state checks in .cursorrules (explicit verification steps)

**The validation script is the key tool for ensuring workflows are actually used.**

---

**Last Updated:** 2026-01-16  
**Status:** ✅ Validation script implemented, additional layers recommended
