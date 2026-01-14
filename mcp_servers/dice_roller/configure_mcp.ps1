# configure_mcp.ps1
# This script configures the Dice Roller MCP server in Cursor's settings.

$mcpServerName = "dice-roller"
$serverScriptPath = "C:\DnD\DnD_Cursor\mcp_servers\dice_roller\dice_roller_server.py"
$pythonExecutable = "python"
$settingsPath = "$env:APPDATA\Cursor\User\settings.json"

Write-Host "=== Dice Roller MCP Configuration ===" -ForegroundColor Cyan

# Verify Python executable
try {
    $pythonPath = (Get-Command python -ErrorAction Stop).Source
    Write-Host "Python found at: $pythonPath" -ForegroundColor Green
} catch {
    Write-Error "Python not found in PATH. Please ensure Python is installed and in your system PATH."
    exit 1
}

# Verify server script
if (-not (Test-Path $serverScriptPath)) {
    Write-Error "Server script not found at $serverScriptPath."
    exit 1
}
Write-Host "Server script found at: $serverScriptPath" -ForegroundColor Green

# Verify settings file exists
if (-not (Test-Path $settingsPath)) {
    Write-Error "Cursor settings.json not found at: $settingsPath"
    exit 1
}
Write-Host "Settings file found at: $settingsPath" -ForegroundColor Green

# Backup settings
$backupPath = "$settingsPath.backup"
Copy-Item $settingsPath $backupPath -Force
Write-Host "Settings backup created at: $backupPath" -ForegroundColor Yellow

# Load and update settings
try {
    $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
    
    # Ensure mcp.servers exists
    if (-not $settings.mcp) {
        $settings | Add-Member -MemberType NoteProperty -Name "mcp" -Value @{ servers = @{} }
    }
    if (-not $settings.mcp.servers) {
        $settings.mcp | Add-Member -MemberType NoteProperty -Name "servers" -Value @{}
    }
    
    # Add/Update dice-roller server
    $serverConfig = @{
        command = $pythonExecutable
        args = @($serverScriptPath)
    }
    
    if ($settings.mcp.servers.PSObject.Properties.Name -contains $mcpServerName) {
        Write-Host "Updating existing '$mcpServerName' server configuration..." -ForegroundColor Yellow
        $settings.mcp.servers.$mcpServerName = $serverConfig
    } else {
        Write-Host "Adding new '$mcpServerName' server configuration..." -ForegroundColor Yellow
        $settings.mcp.servers | Add-Member -MemberType NoteProperty -Name $mcpServerName -Value $serverConfig -Force
    }
    
    # Save settings
    $settings | ConvertTo-Json -Depth 10 | Set-Content $settingsPath -Encoding UTF8
    Write-Host "`nConfiguration complete!" -ForegroundColor Green
    
} catch {
    Write-Error "Failed to update settings: $_"
    Write-Host "Restoring backup..." -ForegroundColor Yellow
    Copy-Item $backupPath $settingsPath -Force
    exit 1
}

Write-Host "`nMCP Server Configuration:" -ForegroundColor Cyan
Write-Host "  Server: $mcpServerName"
Write-Host "  Command: $pythonExecutable"
Write-Host "  Script: $serverScriptPath"

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Restart Cursor to load the MCP server"
Write-Host "2. Check 'MCP' section in Cursor settings UI"
Write-Host "3. Test by asking AI to roll dice: 'Roll 2d6+3 for damage'"
Write-Host "4. Check audit log at: $(Join-Path (Split-Path $serverScriptPath) 'dice_roll_audit.log')"
