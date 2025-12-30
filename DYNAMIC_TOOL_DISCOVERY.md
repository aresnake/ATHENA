# ATHENA MCP - Dynamic Tool Discovery

## 🎯 Problème Résolu

**Avant:** Les outils nécessitaient un câblage manuel dans 3 endroits différents:
1. Implémentation dans `executor.py` ✍️
2. Déclaration dans `registry.py` ✍️
3. Routing dans `provider_http.py` ✍️ ← **Souvent oublié!**

**Résultat:** Erreurs "tool not displayed server-side" fréquentes

**Maintenant:** Câblage automatique! ✨

---

## ⚡ Comment ça Marche

### 1. Implémentation dans executor.py

Créez simplement votre fonction dans `src/athena_mcp/blender_bridge/executor.py`:

```python
def my_new_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Your new tool implementation."""
    # ... implementation
    return ok_response(result={"data": "something"})
```

### 2. Déclaration dans registry.py

Déclarez votre outil dans `src/athena_mcp/tools/registry.py`:

```python
ToolDefinition(
    name="blender-my-new-tool",  # Convention: blender-* ou athena-*
    description="What your tool does",
    input_schema=specs_v2.MY_SCHEMA,
    impl=_tool_blender_my_new_tool,
    category="mesh",  # ou autre catégorie
    tags=["tag1", "tag2"],
    safety_level="safe-first",
)

def _tool_blender_my_new_tool(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-my-new-tool", _clean_args(args))
```

### 3. Routing Automatique ✨

**C'EST TOUT!** Le bridge HTTP découvre automatiquement votre fonction via introspection:

```python
# provider_http.py - AUTOMATIQUE
# La fonction my_new_tool() devient automatiquement:
# - Route: "blender-my-new-tool"
# - Handler: executor.my_new_tool
```

---

## 🔧 Convention de Nommage

### Fonctions Python → Noms d'Outils

Le système convertit automatiquement les noms de fonction en noms d'outils:

| Fonction dans executor.py | Nom d'outil généré | Préfixe |
|----------------------------|-------------------|---------|
| `add_cube()` | `blender-add-cube` | blender- |
| `mesh_extrude()` | `blender-mesh-extrude` | blender- |
| `viewport_screenshot_complete()` | `blender-viewport-screenshot-complete` | blender- |
| `spatial_analyze()` | `athena-blender-spatial-analyze` | athena-blender- |
| `viewport_diff_comparison()` | `athena-viewport-diff-comparison` | athena- |

### Règles de Préfixe

**Outils Blender standard (préfixe `blender-`):**
- Opérations directes sur l'API Blender
- Fonctions bas-niveau (mesh, object, modifier, etc.)
- Exemple: `mesh_extrude()` → `blender-mesh-extrude`

**Outils Athena avancés (préfixe `athena-blender-` ou `athena-`):**
- Outils composites/workflow
- Analyse/validation de haut niveau
- Outils vision/viewport

Configurés dans `_ATHENA_TOOLS` set:

```python
# provider_http.py:66-73
_ATHENA_TOOLS = {
    'spatial_analyze',           # → athena-blender-spatial-analyze
    'topology_validate_complete', # → athena-blender-topology-validate-complete
    'viewport_diff_comparison',   # → athena-viewport-diff-comparison
    'viewport_annotate_markup',   # → athena-viewport-annotate-markup
    # ... etc
}
```

---

## 📝 Ajouter un Nouvel Outil

### Étape 1: Implémenter dans executor.py

```python
# src/athena_mcp/blender_bridge/executor.py

def mesh_smooth_vertices(args: Dict[str, Any]) -> Dict[str, Any]:
    """Smooth selected vertices using Laplacian algorithm."""
    bpy = _require_bpy()

    iterations = args.get('iterations', 1)
    factor = args.get('factor', 0.5)

    try:
        bpy.ops.mesh.vertices_smooth(
            factor=factor,
            repeat=iterations
        )
        return ok_response(result={"smoothed": True})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")
```

### Étape 2: Déclarer dans registry.py

```python
# src/athena_mcp/tools/registry.py

# 1. Ajouter le schema
# src/athena_mcp/tools/specs_v2.py
MESH_SMOOTH_VERTICES_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "iterations": {"type": "integer", "default": 1, "minimum": 1, "maximum": 100},
        "factor": {"type": "number", "default": 0.5, "minimum": 0, "maximum": 1}
    },
    "additionalProperties": False,
}

# 2. Ajouter la fonction wrapper
def _tool_blender_mesh_smooth_vertices(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-smooth-vertices", _clean_args(args))

# 3. Ajouter le ToolDefinition
ToolDefinition(
    name="blender-mesh-smooth-vertices",
    description="Smooth selected vertices using Laplacian algorithm.",
    input_schema=specs_v2.MESH_SMOOTH_VERTICES_SCHEMA,
    impl=_tool_blender_mesh_smooth_vertices,
    category="mesh",
    tags=["smooth", "vertices", "laplacian"],
    safety_level="safe-first",
),
```

### Étape 3: C'est Tout! ✨

Le bridge HTTP découvre automatiquement la fonction `mesh_smooth_vertices()` et crée la route `blender-mesh-smooth-vertices`.

**Aucun code manuel dans provider_http.py nécessaire!**

---

## 🔍 Validation

### Vérifier que votre outil est enregistré

```bash
python validate_tools.py
```

Sortie attendue:
```
======================================================================
ATHENA MCP - Tool Registry Validation
======================================================================

✅ Total tools registered: 143  # +1 pour votre nouvel outil

📊 Tools by Category:
  mesh                :  58 tools  # +1
  ...
```

### Tester depuis Blender

1. Recharger le serveur MCP dans Blender
2. Appeler votre outil:
```python
blender-mesh-smooth-vertices(iterations=5, factor=0.7)
```

---

## 🚨 Outils Athena Spéciaux

Pour créer un outil Athena (préfixe `athena-*`), ajoutez le nom de fonction au set `_ATHENA_TOOLS`:

```python
# src/athena_mcp/blender_bridge/provider_http.py:66

_ATHENA_TOOLS = {
    'spatial_analyze',
    'topology_validate_complete',
    # ... existing tools ...
    'my_new_athena_tool',  # ← Ajoutez ici
}
```

Votre fonction `my_new_athena_tool()` deviendra automatiquement:
- `athena-blender-my-new-athena-tool` (si c'est un outil général)
- `athena-my-new-athena-tool` (si c'est un outil viewport - commence par `viewport_`)

---

## 📊 Statistiques Actuelles

```
Total tools: 142
  - Primitives: 6
  - Mesh ops: 57
  - Object ops: 17
  - Modifiers: 10
  - Vision: 8 (athena-viewport-*)
  - Diagnostics: 8
  - Autres: 36
```

**100% des outils sont automatiquement routés!** ✅

---

## 🔧 Dépannage

### Mon outil n'apparaît pas

**Vérifications:**

1. ✅ La fonction est publique (pas de `_` au début)
2. ✅ La fonction existe dans `executor.py`
3. ✅ Le serveur Blender a été rechargé
4. ✅ Le nom de fonction respecte la convention (snake_case)

### Erreur "tool not displayed server-side"

**Solutions:**

1. Vérifier que la fonction existe dans `executor.py`:
   ```bash
   grep "^def my_tool" src/athena_mcp/blender_bridge/executor.py
   ```

2. Si la fonction utilise un préfixe `athena-*`, l'ajouter au set `_ATHENA_TOOLS`

3. Redémarrer le serveur MCP Blender

---

## 💡 Avantages du Système Dynamique

### Avant (Manuel)
```diff
- 3 fichiers à modifier
- Risque d'oubli de routing
- Incohérence naming possible
- Maintenance difficile
```

### Maintenant (Automatique)
```diff
+ 2 fichiers seulement (executor + registry)
+ Routing automatique garanti
+ Convention naming imposée
+ Maintenance simplifiée
+ Validation automatique possible
```

---

## 🎯 Prochaines Améliorations Possibles

1. **Auto-génération des schemas** depuis docstrings
2. **Auto-génération des registry entries** depuis decorator
3. **Tests de validation automatiques** en CI/CD
4. **Documentation auto-générée** depuis code

**Exemple futur possible:**
```python
@mcp_tool(category="mesh", tags=["smooth"])
def mesh_smooth_vertices(iterations: int = 1, factor: float = 0.5):
    """Smooth selected vertices using Laplacian algorithm.

    Args:
        iterations: Number of smoothing iterations (1-100)
        factor: Smoothing strength (0.0-1.0)
    """
    # Implementation...
```

Et tout serait généré automatiquement! 🚀

---

## 📚 Références

- [provider_http.py:50-95](src/athena_mcp/blender_bridge/provider_http.py#L50-L95) - Système de découverte dynamique
- [registry.py](src/athena_mcp/tools/registry.py) - Déclarations d'outils
- [executor.py](src/athena_mcp/blender_bridge/executor.py) - Implémentations
- [validate_tools.py](validate_tools.py) - Script de validation
