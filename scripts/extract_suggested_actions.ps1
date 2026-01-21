# Extract Suggested Actions from Location Cards
# Parses location card text to generate actionable suggestions for players

param(
    [Parameter(Mandatory=$true)]
    [string]$LocationCardPath,
    
    [Parameter(Mandatory=$false)]
    [string]$StateFile = ""
)

$ErrorActionPreference = "Stop"

# Load location card
if (-not (Test-Path $LocationCardPath)) {
    Write-Output "[]"
    exit 0
}

try {
    $card = Get-Content $LocationCardPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $boxedText = $card.boxed_text
    $mechanics = $card.mechanics
    
    $actions = @()
    
    # Parse mechanics/gates for checks/saves
    if ($mechanics -and $mechanics -ne "") {
        try {
            $gates = $mechanics | ConvertFrom-Json
            if ($gates -is [System.Array]) {
                foreach ($gate in $gates) {
                    if ($gate.type -eq "check") {
                        $skill = if ($gate.skill) { "$($gate.ability) ($($gate.skill))" } else { $gate.ability }
                        $actions += "Make a DC $($gate.dc) $skill check" + $(if ($gate.note) { " - $($gate.note)" } else { "" })
                    } elseif ($gate.type -eq "save") {
                        $actions += "Make a DC $($gate.dc) $($gate.ability) saving throw" + $(if ($gate.note) { " - $($gate.note)" } else { "" })
                    }
                }
            }
        } catch {
            # Invalid mechanics JSON, skip
        }
    }
    
    # Parse boxed_text for common actionable elements
    $textLower = $boxedText.ToLower()
    
    # Locked containers (strongbox, chest, door, etc.)
    if ($textLower -match "locked.*strongbox|locked.*chest|locked.*door") {
        if ($textLower -match "requir.*thieves.*tools.*dc\s+(\d+).*dexterity") {
            $dc = $matches[1]
            $actions += "Attempt to pick the lock (Requires thieves' tools and a DC $dc Dexterity check)"
        } elseif ($textLower -match "requir.*dc\s+(\d+).*dexterity") {
            $dc = $matches[1]
            $actions += "Attempt to pick the lock (Requires a DC $dc Dexterity check)"
        } elseif ($textLower -match "locked") {
            $actions += "Attempt to unlock the lock (Requires thieves' tools and a Dexterity check)"
        }
    }
    
    # Treasure mentioned
    if ($textLower -match "treasure\.|contains.*gp|contains.*sp|contains.*cp") {
        if ($textLower -notmatch "locked|requires.*dc") {
            $actions += "Search for treasure or loot"
        }
    }
    
    # Reading/examining records or texts
    if ($textLower -match "read.*dwarvish|read.*elvish|examine.*record|examine.*paper|examine.*text") {
        $actions += "Examine the old records or texts"
    }
    
    # Searching areas
    if ($textLower -match "search|investigate|examine.*room") {
        $actions += "Search the room thoroughly"
    }
    
    # Opening doors/entering areas (from mechanics or text)
    if ($textLower -match "door.*lead|entrance|passage.*to") {
        # Extract area references like "W6", "W7", etc.
        if ($textLower -match "(w\d+|h\d+|a\d+):") {
            $areaRefs = [regex]::Matches($textLower, "(w\d+|h\d+|a\d+):") | ForEach-Object { $_.Value.TrimEnd(':') }
            foreach ($area in $areaRefs) {
                $actions += "Continue exploring (move to $area)"
            }
        }
    }
    
    # Remove duplicates
    $actions = $actions | Select-Object -Unique
    
    # Convert to JSON array
    $actionsJson = $actions | ConvertTo-Json -Compress
    Write-Output $actionsJson
    
} catch {
    Write-Output "[]"
}
































