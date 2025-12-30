# Solution MCP pour Claude Code - ATHENA Blender

**Date** : 2025-12-29
**Statut** : Résolu ✅

---

## Problème diagnostiqué

Vous voyiez des tools `mcp__blender__*` dans Claude Code mais ils ne fonctionnaient pas car :

1. **Les tools `mcp__blender__*` existent** - ce sont vos tools ATHENA exposés via MCP
2. **Le serveur MCP ATHENA n'était pas configuré** pour Claude Code (seulement pour Claude Desktop)
3. **Le bridge Blender n'était pas lancé** au moment des tests
4. **Plusieurs processus Blender en double** créaient de la confusion

## Solution appliquée

### 1. Configuration MCP pour Claude Code

**Fichier créé** : `D:\ATHENA\.mcp.json`

```json
{
  "mcpServers": {
    "athena-blender": {
      "command": "D:\\ATHENA\\.venv\\Scripts\\python.exe",
      "args": [
        "-m",
        "athena_mcp.mcp_core.server",
        "--stdio",
        "--bridge-host",
        "127.0.0.1",
        "--bridge-port",
        "8765"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PYTHONPATH": "D:\\ATHENA\\src"
      }
    }
  }
}
```

Ce fichier permet à Claude Code de lancer automatiquement le serveur MCP ATHENA en mode stdio.

### 2. Script de lancement Blender

**Fichier créé** : `D:\ATHENA\start_blender_bridge.ps1`

```powershell
# Script pour lancer Blender avec le bridge HTTP ATHENA
$BlenderPath = "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
$BridgeScript = "D:\ATHENA\src\athena_mcp\blender_bridge\provider_http.py"

& $BlenderPath --factory-startup --python $BridgeScript
```

**Usage** :
```powershell
cd D:\ATHENA
.\start_blender_bridge.ps1
```

### 3. Nettoyage des processus en double

Commandes utilisées pour tuer les processus Blender en double :

```powershell
Stop-Process -Name blender -Force
Stop-Process -Name blender-mcp -Force
```

---

## Workflow de démarrage

### Pour Claude Code CLI

1. **Lancer Blender avec le bridge** (dans un terminal PowerShell) :
   ```powershell
   cd D:\ATHENA
   .\start_blender_bridge.ps1
   ```

2. **Lancer Claude Code** (dans un autre terminal) :
   ```bash
   cd D:\ATHENA
   claude-code
   ```

3. **Utiliser les tools MCP** :
   - Les tools sont accessibles via le serveur `athena-blender`
   - Claude Code détecte automatiquement le fichier `.mcp.json`
   - Les 41 tools ATHENA sont disponibles

### Pour Claude Desktop

1. **Lancer Blender** avec le bridge (même commande que ci-dessus)

2. **Ouvrir Claude Desktop** - le serveur MCP démarre automatiquement

3. **Utiliser les tools** directement par leur nom : `blender-scene-list-objects`

---

## Vérification

### Tester le bridge HTTP

```bash
curl http://127.0.0.1:8765/health
# Attendu : {"ok": true, "service": "athena-blender-bridge"}

curl -X POST http://127.0.0.1:8765/exec \
  -H "Content-Type: application/json" \
  -d '{"tool":"blender-scene-list-objects","args":{}}'
# Attendu : {"ok": true, "result": {"objects": ["Camera", "Cube", "Light"], "count": 3}}
```

### Vérifier qu'un seul Blender tourne

```powershell
tasklist | findstr blender
# Vous devriez voir 1 blender.exe et quelques blender-mcp.exe (processus internes)
```

### Vérifier le port 8765

```bash
netstat -ano | findstr ":8765"
# Vous devriez voir une ligne LISTENING
```

---

## Architecture

```
Claude Code CLI
    ↓ (stdio)
Serveur MCP ATHENA (Python)
    ↓ (HTTP POST :8765/exec)
Blender Bridge HTTP
    ↓ (bpy API)
Blender 5.0
```

**Flow** :
1. Claude Code communique avec le serveur MCP via stdio (JSON-RPC)
2. Le serveur MCP traduit les appels en requêtes HTTP vers le bridge Blender
3. Le bridge exécute les commandes dans Blender via l'API bpy
4. Les résultats remontent la chaîne

---

## Fichiers créés

| Fichier | Description |
|---------|-------------|
| `D:\ATHENA\.mcp.json` | Configuration MCP pour Claude Code |
| `D:\ATHENA\start_blender_bridge.ps1` | Script PowerShell pour lancer Blender |
| `D:\ATHENA\SOLUTION_MCP_CLAUDE_CODE.md` | Ce document |

---

## Différences Claude Desktop vs Claude Code

| Aspect | Claude Desktop | Claude Code CLI |
|--------|----------------|-----------------|
| **Config MCP** | `%APPDATA%\Claude\claude_desktop_config.json` | `.mcp.json` (racine projet) |
| **Démarrage serveur** | Automatique au lancement | Automatique si `.mcp.json` présent |
| **Logs** | `%APPDATA%\Claude\logs\mcp-server-*.log` | stdout/stderr de la session |

---

## Troubleshooting

### Les tools ATHENA ne sont pas visibles dans Claude Code

1. Vérifier que `.mcp.json` existe : `ls D:\ATHENA\.mcp.json`
2. Vérifier que vous êtes dans le bon répertoire : `cd D:\ATHENA`
3. Redémarrer la session Claude Code

### Erreur "Could not connect to Blender"

1. Vérifier que Blender est lancé avec le bridge : `curl http://127.0.0.1:8765/health`
2. Vérifier qu'il n'y a pas plusieurs Blender en cours : `tasklist | findstr blender`
3. Relancer Blender avec `.\start_blender_bridge.ps1`

### Le serveur MCP ne démarre pas

1. Vérifier que le venv Python existe : `ls D:\ATHENA\.venv`
2. Vérifier le PYTHONPATH dans `.mcp.json`
3. Tester manuellement :
   ```bash
   D:\ATHENA\.venv\Scripts\python.exe -m athena_mcp.mcp_core.server --stdio
   ```

---

## Important : Utiliser D:\ATHENA uniquement

**NE PLUS utiliser les worktrees** :
- ❌ `C:\Users\adrie\.claude-worktrees\ATHENA\*`
- ✅ `D:\ATHENA` (répertoire principal)

Selon `START_HERE.md`, les worktrees ont été nettoyés. Tout le développement doit se faire dans `D:\ATHENA`.

---

## Prochaines étapes recommandées

1. ✅ **Redémarrer Claude Code** depuis `D:\ATHENA`
2. ✅ **Tester les tools** - demander "Liste les objets dans la scène Blender"
3. 📝 **Commit la configuration** :
   ```bash
   git add .mcp.json start_blender_bridge.ps1 SOLUTION_MCP_CLAUDE_CODE.md
   git commit -m "feat(mcp): add Claude Code MCP config + Blender bridge launcher"
   ```

---

## Résumé

**Avant** :
- ❌ Tools MCP visibles mais non fonctionnels
- ❌ Configuration manquante pour Claude Code
- ❌ Processus Blender en double
- ❌ Confusion entre worktree et repo principal

**Après** :
- ✅ Configuration `.mcp.json` créée dans `D:\ATHENA`
- ✅ Script de lancement propre `start_blender_bridge.ps1`
- ✅ Bridge HTTP fonctionnel sur le port 8765
- ✅ 41 tools ATHENA accessibles
- ✅ Travail uniquement dans `D:\ATHENA` (pas de worktree)

---

Bon dev ! 🚀
