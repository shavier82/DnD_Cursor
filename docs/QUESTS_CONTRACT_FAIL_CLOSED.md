# QUEST CONTRACT (FAIL-CLOSED)

**Purpose:** Deterministic quest state. No fuzzy text — use tags only. Guards block repeats and enforce QUEST-DELTA.

---

## Tags (exact)

- **Start/offer:** `[QUESTSTART <id>]` or `[QUESTOFFER <id>]`
- **State changes:** `[QUESTCOMPLETE <id>]`, `[QUESTFAIL <id>]`, `[QUESTACCEPT <id>]`, `[QUESTACTIVATE <id>]`

Any state-change tag **requires** a matching `QUEST-DELTA` block. Offering a completed quest → **BLOCKED**.

---

## QUEST-DELTA format (exact)

```
QUEST-DELTA
- complete: <quest_id>
- fail: <quest_id>
- accept: <quest_id>
- activate: <quest_id>
- deactivate: <quest_id>
END QUEST-DELTA
```

- One line per change: `- <action>: <quest_id>`
- Actions: `complete`, `fail`, `accept`, `activate`, `deactivate`
- `quest_id`: `[a-zA-Z0-9_\-]+` (e.g. `q_t18_cleansing_chamber`)

---

## Examples

**Complete a quest:**
```
NARRATION: You return to town after clearing the chamber.
QUEST-DELTA
- complete: q_t18_cleansing_chamber
END QUEST-DELTA
```

**Re-offer completed (BLOCKED):**
```
NARRATION: The townmaster asks you to clear the chamber again. [QUESTSTART q_t18_cleansing_chamber]
```
→ Quest guard blocks: `q_t18_cleansing_chamber` is in `completed`.

---

## Runtime

- **Local mirror:** `scripts/quests_state.json`
- **Obsidian (authoritative):** `DnD/state/quests_state.json`
- **Prompt context:** `python scripts/dm_workflow.py quest_context` — inject output into DM prompt.
- **Order in respond():** response_guard → **quest_guard** → rest_guard → resource_guard → … → apply_quest_delta + sync_quests_obsidian (only if guard passed).
