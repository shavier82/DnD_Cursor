<#  scripts/test_quests_stack.ps1
    Smoke tests for QUEST CONTRACT fail-closed enforcement + state IO hardening.
    Run from repo root:  powershell -ExecutionPolicy Bypass -File scripts\test_quests_stack.ps1
#>

$ErrorActionPreference = "Stop"

function Fail($msg) {
  Write-Host "FAIL: $msg" -ForegroundColor Red
  exit 1
}

function Ok($msg) {
  Write-Host "OK: $msg" -ForegroundColor Green
}

function Run-DmWorkflowRespond([string]$text) {
  # Pipe-only to avoid the $input/--text collision
  return ($text | python scripts/dm_workflow.py respond --verbose 2>&1) -join "`n"
}

function Run-DmWorkflowQuestContext() {
  return (python scripts/dm_workflow.py quest_context 2>&1) -join "`n"
}

# ---- Setup / reset runtime state (keep backups clean) ----
$statePath = "scripts/quests_state.json"
$backupRoot = "scripts/backups/quests_state"
$testQuestId = "q_smoke_" + (Get-Date -Format "yyyyMMdd_HHmmss")
$testQuestOfferId = "q_offer_smoke_" + (Get-Date -Format "yyyyMMdd_HHmmss")

if (Test-Path $backupRoot) {
  # Keep existing backups, but don't let them confuse this run
  # (Nothing to do — just informational)
}

# Ensure we start from "no local state" so bootstrap is exercised.
Remove-Item $statePath -ErrorAction SilentlyContinue

# ---- 1) Bootstrap creates quests_state.json ----
$qc = Run-DmWorkflowQuestContext
if (-not (Test-Path $statePath)) { Fail "Bootstrap did not create $statePath" }
Ok "Bootstrap created quests_state.json"

# ---- 2) ACTIONS offer without tag => BLOCKED ----
$offerNoTag = @"
NARRATION: Harbin offers a job clearing the old well.
ASK: Do you accept?
ACTIONS:
1. Accept the quest
2. Decline
"@

$out = Run-DmWorkflowRespond $offerNoTag
if ($out -notmatch "BLOCKED:\s*quest state violation") { Fail "Expected quest guard BLOCKED for offer-without-tag. Output:`n$out" }
if ($out -notmatch "ACTIONS contains quest acceptance option but missing \[QUESTOFFER <id>\] or \[QUESTSTART <id>\]") { Fail "Blocked reason mismatch for offer-without-tag. Output:`n$out" }
Ok "Offer without tag is BLOCKED (ACTIONS enforcement)"

# ---- 3) Offer with [QUESTOFFER] => passes quest_guard (should not BLOCK) ----
$offerWithTag = @"
NARRATION: Harbin offers a job clearing the old well. [QUESTOFFER $testQuestOfferId]
ASK: Do you accept?
ACTIONS:
1. Accept the quest
2. Decline
"@

$out = Run-DmWorkflowRespond $offerWithTag
if ($out -match "BLOCKED:\s*quest state violation") { Fail "Did not expect BLOCKED for offer-with-tag. Output:`n$out" }
if ($out -notmatch "OK:\s*quest_guard passed") { Fail "Expected quest_guard passed for offer-with-tag. Output:`n$out" }
Ok "Offer with tag passes quest_guard"

# ---- 4) Completion tag without QUEST-DELTA => BLOCKED ----
$completeNoDelta = @"
NARRATION: You complete a quest. [QUESTCOMPLETE $testQuestId]
ASK: What do you do next?
ACTIONS:
1. Continue
"@

$out = Run-DmWorkflowRespond $completeNoDelta
if ($out -notmatch "BLOCKED:\s*quest state violation") { Fail "Expected BLOCKED for complete-without-delta. Output:`n$out" }
if ($out -notmatch "QUEST-DELTA block missing") { Fail "Blocked reason mismatch for complete-without-delta. Output:`n$out" }
Ok "Completion without QUEST-DELTA is BLOCKED"

# ---- 5) Completion with QUEST-DELTA + note => applied + visible in quest_context ----
$completeWithDelta = @"
NARRATION: You complete a new quest. [QUESTCOMPLETE $testQuestId]
QUEST-DELTA
- complete: $testQuestId # smoke test note
END QUEST-DELTA
ASK: What do you do next?
ACTIONS:
1. Continue
"@

$out = Run-DmWorkflowRespond $completeWithDelta
if ($out -match "BLOCKED:") { Fail "Did not expect BLOCKED for complete-with-delta. Output:`n$out" }
if ($out -notmatch "APPLY_QUEST_DELTA OUTPUT") { Fail "Expected APPLY_QUEST_DELTA section. Output:`n$out" }
if ($out -notmatch "OK:\s*obsidian quest sync passed") { Fail "Expected obsidian quest sync ok. Output:`n$out" }
Ok "QUEST-DELTA applied and synced"

$qc = Run-DmWorkflowQuestContext
if ($qc -notmatch [regex]::Escape($testQuestId)) { Fail "quest_context missing completed quest id '$testQuestId'. Output:`n$qc" }
if ($qc -notmatch "smoke test note") { Fail "quest_context missing note text. Output:`n$qc" }
Ok "quest_context shows completed quest + note"

# ---- Optional: quick JSON sanity read (BOM safe) ----
try {
  $jsonText = Get-Content -Raw -Encoding UTF8 $statePath
  # PowerShell Get-Content may include BOM; JSON conversion should still work if file is valid.
  $q = $jsonText | ConvertFrom-Json
  if (-not $q.completed) { Fail "quests_state.json parsed but missing 'completed' field." }
  Ok "quests_state.json parses cleanly"
}
catch {
  Fail "quests_state.json failed to parse: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "ALL QUEST SMOKE TESTS PASSED ✅" -ForegroundColor Cyan
exit 0
