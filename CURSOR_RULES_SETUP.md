# Cursor Rules Setup - Streamlined DM System

## Problem
The original `.cursorrules` file was **1,916 lines** - way too long. This caused the AI to "dictate" rules instead of naturally following them.

## Solution
**Leverage Cursor's multi-level rules system:**
1. **User Rules** (global behavior) - How the AI should act as a DM
2. **Project Rules** (`.cursorrules`) - Core D&D-specific principles
3. **Documentation Files** (referenced) - Detailed guides the AI reads when needed

---

## Step 1: Set Up User Rules (Global AI Behavior)

**What:** Define how the AI behaves as a DM across all D&D projects.

**How:**
1. Open Cursor Settings: `Ctrl+,` (Windows) or `Cmd+,` (Mac)
2. Go to **Features** → **Rules for AI**
3. Click **"Edit User Rules"**
4. Copy the contents of `CURSOR_USER_RULES.md` into the user rules
5. Save

**What this does:**
- Sets global DM communication style
- Defines how the AI should use tools (silently)
- Establishes pacing and error handling
- Prevents meta-commentary about system internals

---

## Step 2: Replace Project Rules (Streamlined)

**What:** Use a concise, principle-based `.cursorrules` file.

**How:**
1. Backup current `.cursorrules`:
   ```powershell
   Copy-Item "C:\DnD\DnD_Cursor\.cursorrules" "C:\DnD\DnD_Cursor\.cursorrules_BACKUP"
   ```

2. Replace with streamlined version:
   ```powershell
   Copy-Item "C:\DnD\DnD_Cursor\.cursorrules_STREAMLINED" "C:\DnD\DnD_Cursor\.cursorrules" -Force
   ```

3. Restart Cursor to reload rules

**What this does:**
- Reduces `.cursorrules` from **1,916 lines → ~150 lines**
- Focuses on core principles, not detailed examples
- References documentation files instead of embedding them
- Makes the AI act naturally instead of reciting rules

---

## Step 3: Test the New Setup

**Verify the AI behaves naturally:**

### Test 1: Session Start
**User says:** "Continue Chapter 5 - Phandelver investigation"

**Expected behavior:**
- AI reads CURRENT_STATE.json and CAMPAIGN_EVENTS.json silently
- AI begins narrating from current state
- No meta-commentary about what files it's reading

### Test 2: Spell Question
**User asks:** "Can Torgga cast Fireball?"

**Expected behavior:**
- AI uses `lookup_spell("Fireball")` silently
- AI responds: "No, Fireball is a Sorcerer/Wizard spell. Torgga (Cleric) cannot cast it."
- No announcement: "Let me check the spell database..."

### Test 3: Combat Encounter
**User says:** "We attack the goblins"

**Expected behavior:**
- AI uses `lookup_monster("Goblin")` silently
- AI narrates: "Roll initiative. The goblins ready their weapons..."
- AI processes enemy turns automatically
- Output follows NARRATION/ASK/ACTIONS format

### Test 4: Missing Data
**Monster not in database:**

**Expected behavior:**
- AI outputs: "BLOCKED: Monster stat block not found: <monster_name>. Use lookup_monster or search_monsters."
- No long error dumps or system logs

---

## Step 4: Optional Workspace Rules (Advanced)

**What:** Cursor also supports workspace-specific rules in `.vscode/settings.json` or workspace files.

**When to use:**
- Campaign-specific rules (e.g., "This campaign uses milestone XP, not standard XP")
- Temporary house rules (e.g., "Critical hits deal maximum damage + roll")
- Player-specific preferences (e.g., "Player prefers detailed combat narration")

**How:**
1. Create `.vscode/settings.json` in workspace root
2. Add:
   ```json
   {
     "cursor.aiRules": "Campaign-specific rules here"
   }
   ```

---

## Comparison: Before vs After

### Before (1,916 lines, prescriptive)
```
## ENEMY STATS (CRITICAL - MANDATORY MCP USAGE)
- **MANDATORY: ALWAYS use `lookup_monster(monster_name)` from rules-database MCP BEFORE running encounters.**
- **NEVER invent, guess, or approximate monster stats.**
- **Workflow:**
  1. **First:** Check `lookup_monster(monster_name)` for AC, HP, abilities, actions, CR
  2. **Second:** If not in rules-database, check encounter packs
  3. **Third:** If still not found, use `search_monsters(query)` to find variants
  4. **Never:** Use "standard stats" or guess - BLOCK if unavailable
- **Example:** Before combat with goblins → `lookup_monster("Goblin")` → AC 15, HP 7 (2d6), +4 to hit, 1d6+2 damage, CR 1/4
- **If monster not found:** Output "BLOCKED: Monster stat block not found: <monster_name>. Use lookup_monster or search_monsters."
```

### After (Streamlined, principle-based)
```
| When you need... | Use this MCP function... |
|------------------|--------------------------|
| Monster stats | `lookup_monster(name)` or `search_monsters(query)` |

**If MCP returns "not found" → BLOCK. Do not proceed with guesses.**
```

**Result:**
- AI follows the same rules
- AI acts naturally instead of reciting
- Rules are internalized, not dictated

---

## Documentation Files (Reference Only)

**The AI reads these when needed, doesn't recite them:**

| File | Purpose |
|------|---------|
| `SESSION_START_GUIDE.md` | Session initialization checklist |
| `CAMPAIGN_PATHS.md` | File locations and paths |
| `docs/ENCOUNTER_EXECUTION_GUIDE.md` | Running combat encounters |
| `docs/MCP_SPELL_DATABASE_QUICK_REFERENCE.md` | Spell lookup functions |
| `docs/GATES_SYSTEM.md` | Information control |
| `docs/CAMPAIGN_EVENTS_SYSTEM.md` | Story tracking |

**These are NOT embedded in `.cursorrules` - they're referenced when needed.**

---

## Benefits of This Approach

### 1. Natural DM Behavior
- AI acts like a DM, not a system administrator
- No meta-commentary about internal processes
- Seamless tool usage

### 2. Better Performance
- Shorter rules file = faster parsing
- Less context overhead
- Clearer decision-making

### 3. Easier Maintenance
- Core principles in `.cursorrules` (rarely change)
- Detailed guides in docs (easy to update)
- User behavior in global rules (consistent across projects)

### 4. Better User Experience
- User plays D&D, doesn't discuss system architecture
- AI focuses on narration and gameplay
- Rules enforcement happens invisibly

---

## Troubleshooting

### AI is still explaining its tooling
- Check that User Rules are set correctly
- Verify `.cursorrules_STREAMLINED` is active
- Restart Cursor to reload rules

### AI is not following rules
- Rules are too vague - add specific examples to User Rules
- Check that documentation files exist and are readable

### AI is reciting documentation
- Ensure documentation is referenced, not embedded in `.cursorrules`
- Verify User Rules prohibit recitation

---

## Next Steps

1. ✅ Set up User Rules (global DM behavior)
2. ✅ Replace `.cursorrules` with streamlined version
3. ✅ Test with sample session
4. ✅ Adjust User Rules as needed based on AI behavior

**Goal:** AI acts as a natural, experienced DM - not a rules-reciting system administrator.












