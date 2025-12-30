# Claude Desktop MCP Bug - Diagnostic & Fix

## Symptôme

Lorsque vous demandez à Claude Desktop (via l'interface web claude.ai) d'utiliser les outils Blender MCP, il répond :

> "Je ne peux pas accéder directement à votre instance Blender depuis cette interface web claude.ai."

**Même si** :
- ✅ Le serveur MCP est configuré dans `claude_desktop_config.json`
- ✅ Claude Desktop est lancé
- ✅ Les outils MCP fonctionnent parfaitement dans Claude Code CLI

## Root Cause

Claude Desktop utilise **le modèle web (claude.ai backend)** au lieu d'une instance locale qui aurait accès aux serveurs MCP configurés localement.

Cependant, il y a un **second bug** : même si Claude Desktop lance bien le serveur MCP en stdio, celui-ci **se ferme prématurément** (~3 minutes après le démarrage) à cause de :

1. stdin closed par Claude Desktop (raison inconnue)
2. Timeout silencieux en attendant le Blender bridge (port 8765) si Blender n'est pas lancé
3. Manque de logging stderr pour debugger

## Logs observés

```
2025-12-28T18:51:26.643Z [blender] [info] Server started and connected successfully
2025-12-28T18:51:26.912Z [blender] [info] Message from server: {"tools":[...42 outils...]}
2025-12-28T18:54:46.536Z [blender] [info] Client transport closed
2025-12-28T18:54:46.536Z [blender] [error] Server disconnected
```

Le serveur MCP liste bien les 42 outils Blender, puis se ferme 3 minutes plus tard.

## Fix appliqué

### 1. Amélioration du logging stderr (`transport_stdio.py`)

```python
def serve_stdio(stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> None:
    """JSON-RPC 2.0 stdio transport for Claude Desktop MCP."""
    _setup_logging()
    LOGGER.info("stdio transport started (Python MCP server ready)")
    print("ATHENA MCP stdio transport initialized", file=sys.stderr, flush=True)

    line_count = 0
    for raw in iter(lambda: _read_line(stdin), None):
        line_count += 1
        # ... processing ...

    LOGGER.info(f"stdio transport EOF received after {line_count} lines, shutting down gracefully")
    print(f"ATHENA MCP stdio transport shutting down (processed {line_count} lines)", file=sys.stderr, flush=True)
```

### 2. Support ping/pong keepalive

```python
if method == "ping":
    response = jsonrpc_result(request_id, {"status": "ok"})
```

## Workaround

**Utiliser Claude Code CLI au lieu de Claude Desktop web** :

```powershell
# Terminal 1 : Lancer Blender bridge
blender.exe --factory-startup --python D:\ATHENA\src\athena_mcp\blender_bridge\provider_http.py

# Terminal 2 : Utiliser Claude Code
claude-code
```

Dans Claude Code, les outils MCP Blender sont **directement disponibles** et fonctionnent parfaitement.

## Prochaines étapes

1. **Vérifier si les nouveaux logs stderr apparaissent** dans `%APPDATA%\Claude\logs\mcp-server-blender.log`
2. **Redémarrer Claude Desktop** pour charger le nouveau code avec logging
3. **Investiguer pourquoi stdin se ferme** après 3 minutes (probablement un timeout Claude Desktop)
4. **Tester avec Blender lancé** pour voir si le bridge connecté empêche le shutdown

## Références

- Config MCP : `%APPDATA%\Claude\claude_desktop_config.json`
- Logs MCP : `%APPDATA%\Claude\logs\mcp-server-blender.log`
- Tests : `python -m pytest tests/test_stdio_transport.py -v`
