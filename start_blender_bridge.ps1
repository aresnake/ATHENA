# Script pour lancer Blender avec le bridge HTTP ATHENA
# Usage: .\start_blender_bridge.ps1

$BlenderPath = "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
$BridgeScript = "D:\ATHENA\src\athena_mcp\blender_bridge\provider_http.py"

Write-Host "Lancement de Blender avec le bridge ATHENA HTTP..." -ForegroundColor Green
Write-Host "Bridge HTTP: http://127.0.0.1:8765" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pour arreter : Fermez Blender ou appuyez sur Ctrl+C" -ForegroundColor Yellow
Write-Host ""

& $BlenderPath --factory-startup --python $BridgeScript
