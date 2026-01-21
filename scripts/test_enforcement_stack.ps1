# Test suite for DM enforcement stack
# Run: powershell -ExecutionPolicy Bypass -File scripts/test_enforcement_stack.ps1

Write-Host "`n=== DM Enforcement Stack Test Suite ===" -ForegroundColor Cyan
Write-Host ""

$tests_passed = 0
$tests_failed = 0

function Test-Command {
    param(
        [string]$Name,
        [string]$Command,
        [string]$ExpectedOutput,
        [int]$ExpectedExitCode
    )
    
    Write-Host "Testing: $Name" -ForegroundColor Yellow
    
    $output = Invoke-Expression $Command 2>&1 | Out-String
    $exitCode = $LASTEXITCODE
    
    $outputMatch = $output -match $ExpectedOutput
    $exitMatch = $exitCode -eq $ExpectedExitCode
    
    if ($outputMatch -and $exitMatch) {
        Write-Host "  PASS" -ForegroundColor Green
        $script:tests_passed++
        return $true
    } else {
        Write-Host "  FAIL" -ForegroundColor Red
        Write-Host "    Expected output containing: $ExpectedOutput" -ForegroundColor Gray
        Write-Host "    Expected exit code: $ExpectedExitCode" -ForegroundColor Gray
        Write-Host "    Got output: $($output.Trim())" -ForegroundColor Gray
        Write-Host "    Got exit code: $exitCode" -ForegroundColor Gray
        $script:tests_failed++
        return $false
    }
}

# Test 1: Guard blocks delegation phrase
Test-Command `
    -Name "Guard blocks 'What does X do?'" `
    -Command 'echo "What does Ontharyx do?" | python scripts/response_guard.py --is-pc-turn false' `
    -ExpectedOutput "BLOCKED" `
    -ExpectedExitCode 1

# Test 2: Guard allows reactions question
Test-Command `
    -Name "Guard allows 'Any reactions?'" `
    -Command 'echo "Any reactions?" | python scripts/response_guard.py --is-pc-turn false' `
    -ExpectedOutput "OK" `
    -ExpectedExitCode 0

# Test 3: dmregen blocks and shows instruction
Test-Command `
    -Name "dmregen blocks with instruction" `
    -Command 'echo "What does Ontharyx do?" | python scripts/dmregen.py' `
    -ExpectedOutput "REGEN_INSTRUCTION" `
    -ExpectedExitCode 1

# Test 4: dmregen passes
Test-Command `
    -Name "dmregen passes valid response" `
    -Command 'echo "Any reactions?" | python scripts/dmregen.py' `
    -ExpectedOutput "OK" `
    -ExpectedExitCode 0

# Test 5: Guard verbose shows violations
Test-Command `
    -Name "Guard verbose shows violations" `
    -Command 'echo "What does Ontharyx do?" | python scripts/response_guard.py --is-pc-turn false --verbose' `
    -ExpectedOutput "Violations" `
    -ExpectedExitCode 1

# Test 6: Workflow quiet is one line
$workflowOutput = echo "What does Ontharyx do?" | python scripts/dm_workflow.py respond 2>&1
$lineCount = ($workflowOutput -split "`n" | Where-Object { $_.Trim() }).Count
if ($lineCount -eq 1 -and $workflowOutput -match "BLOCKED") {
    Write-Host "Testing: Workflow quiet is one line" -ForegroundColor Yellow
    Write-Host "  PASS" -ForegroundColor Green
    $tests_passed++
} else {
    Write-Host "Testing: Workflow quiet is one line" -ForegroundColor Yellow
    Write-Host "  FAIL (got $lineCount lines)" -ForegroundColor Red
    $tests_failed++
}

Write-Host ""
Write-Host "=== Test Results ===" -ForegroundColor Cyan
Write-Host "Passed: $tests_passed" -ForegroundColor Green
Write-Host "Failed: $tests_failed" -ForegroundColor $(if ($tests_failed -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($tests_failed -eq 0) {
    exit 0
} else {
    exit 1
}
