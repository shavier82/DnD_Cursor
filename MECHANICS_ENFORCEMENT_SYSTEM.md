# 🔒 MECHANICS ENFORCEMENT SYSTEM
**Prevents AI from skipping mechanics checklist**

---

## 🎯 THE PROBLEM

AI agents forget to check the mechanics checklist, requiring constant reminders like "dementia patients."

## ✅ THE SOLUTION

**Automated enforcement system that forces checklist review:**

---

## 📋 SYSTEM COMPONENTS

### 1. **Pre-Session Validation Script**
**File:** `scripts/pre_session_check.py`

**What it does:**
- Validates checklist exists and is readable
- Creates validation token (`.mechanics_validated.json`)
- Token expires after 24 hours (forces re-validation)

**Usage:**
```bash
# Before every session (automatic):
python scripts/pre_session_check.py

# Check if validated:
python scripts/pre_session_check.py --check
```

**Integration:** Add to session start workflow - AI MUST run this first.

---

### 2. **Context-Aware Reminders**
**File:** `scripts/mechanics_reminder.py`

**What it does:**
- Provides specific reminders based on context
- Triggers automatically before critical operations
- Shows relevant checklist items for the situation

**Contexts:**
- `pre_combat` - Before combat starts
- `post_combat` - After combat ends (MANDATORY)
- `npc_status_change` - When NPC dies/changes
- `quest_completion` - When quest completes
- `spell_cast` - When spell is cast
- `inventory_change` - When items change
- `session_start` - At session start

**Usage:**
```bash
python scripts/mechanics_reminder.py post_combat
python scripts/mechanics_reminder.py npc_status_change
```

---

### 3. **Workflow Integration**

**At Session Start:**
```python
# AI MUST do this automatically:
1. Run: python scripts/pre_session_check.py
2. If fails → BLOCK and show error
3. If passes → Read MECHANICS_AUTOMATION_CHECKLIST.md
4. Then proceed with session
```

**Before Critical Operations:**
```python
# AI MUST do this automatically:
1. Run: python scripts/mechanics_reminder.py <context>
2. Review reminder output
3. Follow checklist procedures
4. Then execute operation
```

---

## 🔧 IMPLEMENTATION

### **Option 1: Automatic Pre-Flight Check**

Add to `.cursorrules`:
```markdown
# -------------------------
# MANDATORY PRE-SESSION CHECK
# -------------------------
**Before starting ANY session, AI MUST:**
1. Run: `python scripts/pre_session_check.py`
2. If validation fails → BLOCK and show error
3. If validation passes → Read MECHANICS_AUTOMATION_CHECKLIST.md
4. Then proceed with session initialization
```

### **Option 2: Context Triggers**

Add automatic reminders at key moments:

**Before Combat:**
```python
# AI automatically runs:
python scripts/mechanics_reminder.py pre_combat
# Then follows checklist for combat procedures
```

**After Combat:**
```python
# AI automatically runs:
python scripts/mechanics_reminder.py post_combat
# Then follows checklist for post-combat procedures
```

**When NPC Dies:**
```python
# AI automatically runs:
python scripts/mechanics_reminder.py npc_status_change
# Then uses update_npc() tool
```

---

## 🚀 AUTOMATED WORKFLOW

### **Session Start (Automatic)**
```
User: "Continue the campaign"
AI:
  1. Run: python scripts/pre_session_check.py
  2. If fails → Show error, block session
  3. If passes → Read MECHANICS_AUTOMATION_CHECKLIST.md
  4. Read CURRENT_STATE.json
  5. Read CAMPAIGN_EVENTS.json
  6. Begin session
```

### **Before Combat**
```
AI detects combat starting:
  1. Run: python scripts/mechanics_reminder.py pre_combat
  2. Review reminder
  3. Start combat with checklist in mind
```

### **After Combat**
```
AI detects combat ended:
  1. Run: python scripts/mechanics_reminder.py post_combat
  2. Review reminder
  3. Follow ALL post-combat procedures from checklist
  4. Verify completion
```

### **NPC Status Change**
```
AI detects NPC died/changed:
  1. Run: python scripts/mechanics_reminder.py npc_status_change
  2. Review reminder
  3. Use update_npc() tool (auto-syncs)
```

---

## 📝 UPDATED SESSION START GUIDE

**New mandatory first step:**
```markdown
### 0. Pre-Session Validation (MANDATORY)
- **MUST run first:** `python scripts/pre_session_check.py`
- If validation fails → BLOCK session and show error
- If validation passes → Continue to step 1
- Validation token expires after 24 hours (forces re-check)
```

---

## ✅ VALIDATION

**After each session, verify:**
```bash
# Check if checklist was validated:
python scripts/pre_session_check.py --check

# Validate mechanics were followed:
python scripts/validate_mechanics.py --all
```

---

## 🎯 SUCCESS CRITERIA

**System is successful if:**
- ✅ AI cannot start session without validation
- ✅ AI automatically gets reminders at key moments
- ✅ AI follows checklist procedures without being told
- ✅ Validation script finds zero errors
- ✅ No manual reminders needed from user

---

## 🔄 FUTURE ENHANCEMENTS

1. **Auto-trigger reminders** - Scripts run automatically via hooks
2. **Checklist acknowledgment** - AI must explicitly check off items
3. **Blocking system** - Operations blocked until checklist verified
4. **Integration with MCP** - MCP tools check validation before executing

---

**Last Updated:** 2026-01-14  
**Status:** ✅ Ready for Implementation
