# Script de démarrage pour Claude Desktop
# Lance Blender avec le bridge HTTP en arrière-plan, puis le serveur MCP

# Activer l'environnement virtuel
& "D:\ATHENA\.venv\Scripts\Activate.ps1"

# Démarrer Blender avec le bridge HTTP en arrière-plan
$blenderProcess = Start-Process -FilePath "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" `
    -ArgumentList "--factory-startup", "--python", "D:\ATHENA\src\athena_mcp\blender_bridge\provider_http.py" `
    -PassThru `
    -NoNewWindow

# Attendre que le bridge soit prêt
Start-Sleep -Seconds 5

# Démarrer le serveur MCP (bloquant)
python -m athena_mcp.mcp_core.server --http --host 127.0.0.1 --port 9000

# Cleanup : tuer Blender quand le serveur MCP s'arrête
Stop-Process -Id $blenderProcess.Id -Force
