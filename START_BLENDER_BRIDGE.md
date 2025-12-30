# 🚀 DÉMARRAGE DU BLENDER BRIDGE

## Le problème
Claude Desktop se connecte au MCP server, mais le bridge Blender n'est pas démarré.
Les outils Blender retournent donc "Unknown tool" ou des erreurs NoneType.

## Solution: Démarrer le bridge dans Blender

### Méthode 1: Via le script dans Blender

1. **Ouvrir Blender**

2. **Aller dans Scripting workspace**
   - Menu en haut: "Scripting"
   - Ou: Workspace dropdown → Scripting

3. **Créer un nouveau script**
   - Text → New

4. **Copier ce code:**

```python
import sys
from pathlib import Path

# Ajouter ATHENA au path Python
athena_path = Path("D:/ATHENA/src")
if str(athena_path) not in sys.path:
    sys.path.insert(0, str(athena_path))

# Importer et démarrer le bridge
from athena_mcp.blender_bridge import provider_http

# Démarrer le serveur HTTP
provider_http.main()
```

5. **Exécuter le script**
   - Cliquer "Run Script" (▶️)
   - Ou: Alt+P

6. **Vérifier le message dans la console:**
   ```
   Blender bridge listening on http://127.0.0.1:8765 (background thread)
   ```

### Méthode 2: Via la console Python de Blender

1. **Ouvrir Blender**

2. **Aller dans Window → Toggle System Console** (Windows)
   - Ou Window → Python Console

3. **Dans la console Python de Blender, taper:**

```python
import sys
sys.path.insert(0, "D:/ATHENA/src")
from athena_mcp.blender_bridge import provider_http
provider_http.main()
```

### Méthode 3: Script startup automatique

Pour démarrer automatiquement à chaque ouverture de Blender:

1. **Créer le fichier:**
   `%APPDATA%\Blender Foundation\Blender\4.x\scripts\startup\athena_bridge.py`

2. **Avec le contenu:**

```python
import bpy
import sys
from pathlib import Path

def start_athena_bridge():
    """Démarre le bridge ATHENA automatiquement"""
    athena_path = Path("D:/ATHENA/src")
    if str(athena_path) not in sys.path:
        sys.path.insert(0, str(athena_path))

    try:
        from athena_mcp.blender_bridge import provider_http
        provider_http.main()
        print("✅ ATHENA Bridge démarré automatiquement")
    except Exception as e:
        print(f"❌ Erreur démarrage ATHENA Bridge: {e}")

# Enregistrer le handler pour démarrer au lancement
bpy.app.timers.register(start_athena_bridge, first_interval=1.0)
```

## Vérification

Une fois le bridge démarré:

1. **Dans Blender, vérifier la console:**
   ```
   Blender bridge listening on http://127.0.0.1:8765 (background thread)
   ```

2. **Tester la connexion:**
   - Ouvrir PowerShell
   - Exécuter:
   ```powershell
   curl http://127.0.0.1:8765/health
   ```
   - Résultat attendu:
   ```json
   {"ok":true,"service":"athena-blender-bridge"}
   ```

3. **Dans Claude Desktop:**
   - Fermer et rouvrir Claude Desktop
   - Le MCP server ATHENA devrait maintenant fonctionner
   - Les outils Blender devraient être disponibles

## Ordre de démarrage

**IMPORTANT:** L'ordre est crucial:

1. ✅ **D'abord:** Démarrer Blender + Bridge (port 8765)
2. ✅ **Ensuite:** Démarrer Claude Desktop (qui lance le MCP server)

Si vous démarrez Claude Desktop avant le bridge:
- Le MCP server démarre ✅
- Mais les appels aux outils Blender échouent ❌
- Solution: Démarrer le bridge, puis **redémarrer Claude Desktop**

## Troubleshooting

### Le bridge ne démarre pas dans Blender

**Erreur:** `ModuleNotFoundError: No module named 'athena_mcp'`

**Solution:** Vérifier que le path est correct dans le script:
```python
sys.path.insert(0, "D:/ATHENA/src")  # Ajuster si nécessaire
```

### Port 8765 déjà utilisé

**Erreur:** `OSError: [WinError 10048] Address already in use`

**Solution:** Le bridge est déjà démarré, ou un autre processus utilise le port 8765.

Vérifier:
```powershell
netstat -ano | findstr :8765
```

### Les outils retournent toujours "Unknown tool"

**Causes possibles:**
1. Le bridge n'est pas démarré
2. Le bridge a crashé
3. Le port 8765 n'est pas accessible

**Solution:**
1. Redémarrer le bridge dans Blender
2. Redémarrer Claude Desktop
3. Vérifier les logs: `C:\Users\adrie\AppData\Roaming\Claude\logs\mcp-server-athena.log`

## Architecture

```
[Claude Desktop]
      ↓
[MCP Server STDIO] (D:/ATHENA/.venv/Scripts/python.exe -m athena_mcp.mcp_core.server)
      ↓ HTTP
[Blender Bridge] (http://127.0.0.1:8765) ← DOIT ÊTRE DÉMARRÉ MANUELLEMENT
      ↓ bpy
[Blender Python API]
```

## Statut actuel

✅ MCP Server: Fonctionnel (se connecte à Claude Desktop)
❌ Blender Bridge: NON démarré (erreurs "Unknown tool")

**Action requise:** Démarrer le bridge dans Blender avant d'utiliser Claude Desktop.
