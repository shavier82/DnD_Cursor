# Validate State Files Command
param(
    [string]$Campaign = "Phandelver"
)

Write-Host "`n=== VALIDATING STATE FILES ===" -ForegroundColor Cyan

$savesDir = "C:\DnD\Campaigns\$Campaign\saves"
$files = @("CURRENT_STATE.json", "CAMPAIGN_EVENTS.json")

$allValid = $true

foreach ($file in $files) {
    $filePath = Join-Path $savesDir $file
    Write-Host "`nChecking: $file" -ForegroundColor Yellow
    
    if (-not (Test-Path $filePath)) {
        Write-Host "  ❌ File not found" -ForegroundColor Red
        $allValid = $false
        continue
    }
    
    try {
        $content = Get-Content $filePath -Raw
        $json = $content | ConvertFrom-Json
        Write-Host "  ✅ Valid JSON" -ForegroundColor Green
        
        $sizeKB = [math]::Round((Get-Item $filePath).Length / 1KB, 2)
        Write-Host "  📊 Size: $sizeKB KB" -ForegroundColor Gray
        
        $lastWrite = (Get-Item $filePath).LastWriteTime
        Write-Host "  🕒 Last modified: $lastWrite" -ForegroundColor Gray
    } catch {
        Write-Host "  ❌ Invalid JSON: $_" -ForegroundColor Red
        $allValid = $false
    }
}

if ($allValid) {
    Write-Host "`n✅ All state files valid!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Some state files have errors!" -ForegroundColor Red
}










