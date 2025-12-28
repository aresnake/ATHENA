# ATHENA MCP - Guide de démarrage rapide

**Mis à jour** : 2025-12-28
**Statut** : Projet consolidé - Worktrees nettoyés ✅

---

## 🎯 Configuration actuelle

### Dossier unique
```
D:\ATHENA  (main repo - utilisez UNIQUEMENT celui-ci)
```

Les worktrees ont été supprimés pour éviter la confusion.

---

## 🚀 Lancer Blender + MCP

### 1. Activer l'environnement virtuel
```powershell
D:\ATHENA\.venv\Scripts\Activate.ps1
```

### 2. Lancer Blender avec le bridge HTTP
```powershell
cd D:\ATHENA
"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" --factory-startup --python src\athena_mcp\blender_bridge\provider_http.py
```

### 3. Vérifier que le bridge fonctionne
```powershell
curl http://127.0.0.1:8765/health
# Attendu : {"ok": true, "service": "athena-blender-bridge"}
```

### 4. Tester un outil
```powershell
curl -Method POST -Uri http://127.0.0.1:8765/exec -ContentType "application/json" -Body '{"tool":"blender-scene-list-objects","args":{}}'
```

---

## 🖥️ Utiliser Claude Desktop

### Configuration MCP
Fichier : `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "blender": {
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
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Workflow
1. Lancer Blender (étape 2 ci-dessus)
2. Lancer Claude Desktop
3. Tester : "Bouge le cube à la position [10, 5, 0]"

**Si ça ne marche pas** : voir `CLAUDE_DESKTOP_MCP_BUG.md`

---

## 💻 Utiliser Claude Code (RECOMMANDÉ)

Claude Code a **accès direct** aux outils MCP sans les problèmes de Desktop.

```bash
cd D:\ATHENA
claude-code
```

Dans la session Claude Code :
```
> Crée un cube à la position [5, 0, 0]
> Bouge-le vers [10, 5, 0]
> Extrude la face du haut de 2 unités
```

**Tout fonctionne directement !**

---

## 📊 État du projet

| Métrique | Valeur |
|----------|--------|
| Tools MCP | 41 (submit-tool supprimé) |
| Tests | 36/38 passent |
| Architecture | Refactorisée avec ToolBank |
| Worktrees | Nettoyés ✅ |

### Derniers commits
```
ef05168 - refactor: cleanup + dynamic tool routing + remove submit-tool workflow
9308bad - fix(mcp): strict stdio JSON-RPC transport + e2e subprocess test
```

---

## 📁 Structure importante

```
D:\ATHENA\
├── src/athena_mcp/
│   ├── tools/              # Tool registry (41 tools)
│   │   ├── registry.py     # Central tool registry
│   │   ├── tool_bank.py    # Indexed lookup
│   │   ├── primitives.py   # Primitive schemas
│   │   └── mesh_edit.py    # Mesh edit schemas
│   ├── blender_bridge/
│   │   ├── provider_http.py  # HTTP bridge (port 8765)
│   │   └── executor.py       # Blender operations
│   └── mcp_core/
│       ├── server.py         # MCP server entry
│       └── transport_stdio.py # Stdio transport (fixed!)
├── tests/                  # 38 tests
├── tools/
│   ├── ARCHITECTURE.md     # Documentation architecture
│   └── archive/            # Docs archivées
└── start_desktop.ps1       # Script de démarrage rapide
```

---

## 🛠️ Développement

### Ajouter un nouvel outil

**Utilisez Claude Code** :
```
"Ajoute un outil pour créer un array circulaire de cubes"
```

Claude Code va :
1. Explorer les outils existants
2. Proposer une API cohérente
3. Implémenter le code
4. Ajouter les tests
5. Mettre à jour la doc

**Tout en une session !**

### Tester
```powershell
python -m pytest
python -m pytest tests/test_tool_bank.py -v
```

---

## 📝 Documentation utile

- `README.md` - Vue d'ensemble du projet
- `tools/ARCHITECTURE.md` - Organisation des tools
- `CLAUDE_DESKTOP_MCP_BUG.md` - Debug Desktop
- `CLEANUP_SUMMARY.md` - Nettoyage submit-tool
- `tools/archive/WHY_SUBMIT_TOOL_REMOVED.md` - Pourquoi submit-tool a été retiré

---

## 🎯 Prochaines étapes recommandées

1. ✅ **Tester Claude Desktop** avec "bouge le cube"
2. ✅ **Vérifier les logs** si problème : `%APPDATA%\Claude\logs\mcp-server-blender.log`
3. 🔄 **Utiliser principalement Claude Code** pour le dev
4. 📦 **Commit réguliers** sur `dev/core-01`

---

## ⚠️ Important

- **NE PLUS utiliser les worktrees** - tout est dans `D:\ATHENA`
- **NE PLUS utiliser Claude Chat** pour les specs - utilisez Claude Code
- **Toujours lancer Blender** avant d'utiliser les tools MCP

---

Bon dev ! 🚀
