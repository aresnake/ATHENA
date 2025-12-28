# Test Claude Desktop MCP

## Étape 1 : Redémarrer Claude Desktop

1. Fermer complètement Claude Desktop
2. Vérifier que Blender bridge tourne : `curl http://127.0.0.1:8765/health`
3. Relancer Claude Desktop

## Étape 2 : Vérifier les logs

Ouvrir : `%APPDATA%\Claude\logs\mcp-server-blender.log`

Chercher ces nouvelles lignes :
```
ATHENA MCP stdio transport initialized
stdio transport started (Python MCP server ready)
```

## Étape 3 : Tester dans Claude Desktop

Dans une conversation Claude Desktop, demander :

```
Bouge le cube à la position [10, 0, 0]
```

**Résultat attendu** :
- ✅ Claude Desktop voit les outils MCP
- ✅ Le serveur ne crash pas après 3 minutes
- ✅ Le cube bouge dans Blender

**Si ça ne marche toujours pas** :

Chercher dans les logs :
```
stdio transport EOF received after X lines
ATHENA MCP stdio transport shutting down (processed X lines)
```

Cela indiquera combien de requêtes ont été traitées avant le shutdown.

## Étape 4 : Workaround (si Desktop web ne fonctionne pas)

Utiliser **Claude Code CLI** à la place :

```bash
claude-code
# Puis dans la session :
# "Bouge le cube à la position [10, 0, 0]"
```

Dans Claude Code, j'ai **directement accès** aux outils MCP et tout fonctionne parfaitement.
