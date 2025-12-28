# Quick Fix Summary - Nommage des outils MCP

## Problème identifié

Le serveur MCP expose des outils avec les **nouveaux noms** (ex: `blender-primitive-cube`) mais le bridge Blender HTTP attend les **anciens noms** (ex: `blender-add-cube`).

Résultat : Claude Desktop ne peut pas utiliser les outils car il y a un mismatch de nommage.

## Solution appliquée

J'ai créé un **registry dynamique** dans `provider_http.py` qui accepte **les deux noms** (anciens ET nouveaux) et route vers les bonnes fonctions executor.

**Mais** : il y a des complications avec le worktree vs main repo.

## Pour tester MAINTENANT

1. **Lancer Blender avec le script modifié du worktree** :
```powershell
cd C:\Users\adrie\.claude-worktrees\ATHENA\mystifying-lumiere
"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" --factory-startup --python src\athena_mcp\blender_bridge\provider_http.py
```

2. **Tester avec curl** (nouveau nom) :
```powershell
curl -Method POST -Uri http://127.0.0.1:8765/exec -ContentType "application/json" -Body '{"tool":"blender-primitive-cube","args":{"name":"TestNew","location":[5,0,0]}}'
```

3. **Tester avec curl** (ancien nom) :
```powershell
curl -Method POST -Uri http://127.0.0.1:8765/exec -ContentType "application/json" -Body '{"tool":"blender-add-cube","args":{"name":"TestOld","location":[-5,0,0]}}'
```

Les deux devraient fonctionner !

## Fichiers modifiés

- `src/athena_mcp/blender_bridge/provider_http.py` → Registry dynamique
- `src/athena_mcp/mcp_core/transport_stdio.py` → Logging amélioré pour debug

## Prochaines étapes

1. Tester que le bridge accepte les nouveaux noms
2. Redémarrer Claude Desktop avec le fix
3. Tester "bouge le cube" dans Claude Desktop

## Note importante

Il manque les fonctions `add_cone` et `add_torus` dans `executor.py` du worktree. Elles sont commentées dans le registry.
