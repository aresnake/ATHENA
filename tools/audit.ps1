# Audit script for Athena MCP + Blender bridge

Write-Host "== Git Status ==" -ForegroundColor Cyan
git status -sb

Write-Host "`n== Python Version ==" -ForegroundColor Cyan
python --version

Write-Host "`n== Pytest ==" -ForegroundColor Cyan
python -m pytest

Write-Host "`n== Port Checks (9000 MCP / 8765 Blender) ==" -ForegroundColor Cyan
netstat -ano | Select-String ":9000"
netstat -ano | Select-String ":8765"

Write-Host "`n== Example HTTP Calls ==" -ForegroundColor Cyan
Write-Host "Health:     Invoke-RestMethod -Method Get http://127.0.0.1:9000/health"
Write-Host "List tools: Invoke-RestMethod -Method Get http://127.0.0.1:9000/tools/list"
Write-Host "Call tool:  Invoke-RestMethod -Method Post http://127.0.0.1:9000/tools/call -Body '{`"name`":`"blender-list-objects`",`"args`":{}}' -ContentType 'application/json'"
