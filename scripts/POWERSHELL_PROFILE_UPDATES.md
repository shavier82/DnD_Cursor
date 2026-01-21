# PowerShell Profile Updates

## dmreport and dmregen Functions

Add these functions to your PowerShell profile (`$PROFILE`). They always run from the repo root, so they work from any directory.

### Location
```powershell
notepad $PROFILE
```

### Functions

```powershell
# dmreport: verbose forensics
function dmreport {
  Push-Location C:\DnD\DnD_Cursor
  try { 
    Get-Clipboard | python .\scripts\dm_workflow.py respond --verbose 
  }
  finally { 
    Pop-Location 
  }
}

# dmregen: fast check + auto-copy REGEN_INSTRUCTION on BLOCKED
function dmregen {
  Push-Location C:\DnD\DnD_Cursor
  try {
    $out = Get-Clipboard | python .\scripts\dmregen.py
    $lines = $out -split "`n"
    if ($lines.Count -ge 2 -and $lines[0] -like "BLOCKED:*") {
      $lines[1].Trim() | Set-Clipboard
    }
    $out
  }
  finally { 
    Pop-Location 
  }
}
```

### Why This Works

- `Push-Location C:\DnD\DnD_Cursor` - Always runs from repo root
- `.\scripts\dm_workflow.py` - Uses relative path from repo root
- `try/finally` - Ensures we return to original directory even on error
- Works from any directory (C:\, scripts\, anywhere)

### Alternative: Select-String -Recurse Fix

If `Select-String -Recurse` doesn't work in your PowerShell version:

```powershell
Get-ChildItem -Path . -File -Recurse | Select-String -Pattern "META-END" -List
```
