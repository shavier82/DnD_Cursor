# MCP Server Test Command

Write-Host "`n=== MCP SERVER TEST ===" -ForegroundColor Cyan
Write-Host "This command shows you what to test in the chat." -ForegroundColor Gray

Write-Host "`n📋 Copy/paste these commands into the AI chat to test MCP servers:`n" -ForegroundColor Yellow

Write-Host "1️⃣ DICE ROLLER:" -ForegroundColor Cyan
Write-Host '   roll_dice("2d6+3", "Test roll")' -ForegroundColor White

Write-Host "`n2️⃣ MONSTER LOOKUP:" -ForegroundColor Cyan
Write-Host '   lookup_monster("Goblin")' -ForegroundColor White

Write-Host "`n3️⃣ SPELL LOOKUP:" -ForegroundColor Cyan
Write-Host '   lookup_spell("Fireball")' -ForegroundColor White

Write-Host "`n4️⃣ CONDITION LOOKUP:" -ForegroundColor Cyan
Write-Host '   lookup_condition("Grappled")' -ForegroundColor White

Write-Host "`n5️⃣ RULE LOOKUP:" -ForegroundColor Cyan
Write-Host '   lookup_rule("Advantage")' -ForegroundColor White

Write-Host "`n6️⃣ SPELL SEARCH:" -ForegroundColor Cyan
Write-Host '   search_spells("fire damage")' -ForegroundColor White

Write-Host "`n7️⃣ SOURCEBOOK SEARCH:" -ForegroundColor Cyan
Write-Host '   search_sourcebooks("grappling rules", "phb")' -ForegroundColor White

Write-Host "`n✅ All commands should return results within 100ms" -ForegroundColor Green
Write-Host "❌ If any fail, check .cursor/mcp.json configuration`n" -ForegroundColor Red










