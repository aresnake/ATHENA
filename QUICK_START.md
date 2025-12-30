# ATHENA MCP - Guide de Démarrage Rapide

## 🚀 Ajouter un Nouvel Outil (2 étapes)

### ✅ Méthode Simple (Recommandée)

**1. Implémenter dans executor.py**

```python
# src/athena_mcp/blender_bridge/executor.py

def mesh_my_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Your operation description."""
    bpy = _require_bpy()

    # Your implementation here
    param1 = args.get('param1')
    param2 = args.get('param2', default_value)

    try:
        # Do something with Blender API
        result = {"success": True, "data": "something"}
        return ok_response(result=result)
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")
```

**2. Déclarer dans registry.py**

```python
# A. Créer le schema (src/athena_mcp/tools/specs_v2.py)
MY_OPERATION_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "param1": {"type": "string"},
        "param2": {"type": "number", "default": 1.0}
    },
    "required": ["param1"],
    "additionalProperties": False,
}

# B. Créer la fonction wrapper (src/athena_mcp/tools/registry.py)
def _tool_blender_mesh_my_operation(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-my-operation", _clean_args(args))

# C. Ajouter à la liste TOOLS
ToolDefinition(
    name="blender-mesh-my-operation",
    description="Your operation description",
    input_schema=specs_v2.MY_OPERATION_SCHEMA,
    impl=_tool_blender_mesh_my_operation,
    category="mesh",  # ou: object, modifier, diag, vision, etc.
    tags=["tag1", "tag2"],
    safety_level="safe-first",  # ou: view3d-auto, view3d-required
),
```

**3. Validation**

```bash
python validate_tools.py  # Vérifier que l'outil est enregistré
pytest tests/            # Tous les tests doivent passer
```

**4. Tester dans Blender**

1. Recharger le serveur MCP Blender
2. Appeler: `blender-mesh-my-operation(param1="test")`

**✨ Le routing HTTP est AUTOMATIQUE!**

---

## 🎯 Conventions de Nommage

### Fonction Python → Nom d'Outil

| Fonction | Outil Généré | Catégorie |
|----------|-------------|-----------|
| `mesh_extrude()` | `blender-mesh-extrude` | mesh |
| `object_rotate()` | `blender-object-rotate` | object |
| `modifier_add()` | `blender-modifier-add` | modifier |
| `viewport_screenshot_complete()` | `blender-viewport-screenshot-complete` | vision |

### Outils Athena (avancés)

Pour créer un outil `athena-*`, ajouter au set `_ATHENA_TOOLS`:

```python
# src/athena_mcp/blender_bridge/provider_http.py:66
_ATHENA_TOOLS = {
    'spatial_analyze',
    'my_new_athena_tool',  # ← Ajoutez ici
}
```

---

## 📁 Structure du Projet

```
athena-mcp/
├── src/athena_mcp/
│   ├── blender_bridge/
│   │   ├── executor.py          # Implémentations Blender
│   │   ├── provider_http.py     # Bridge HTTP (routing auto)
│   │   └── validate_registry.py # Validation interne
│   └── tools/
│       ├── registry.py          # Déclarations MCP
│       └── specs_v2.py          # Schemas JSON
├── tests/                       # Tests pytest
├── validate_tools.py            # Script de validation
└── DYNAMIC_TOOL_DISCOVERY.md    # Documentation complète
```

---

## 🔧 Catégories d'Outils

| Catégorie | Description | Exemples |
|-----------|-------------|----------|
| `primitives` | Objets de base | cube, cylinder, sphere |
| `mesh` | Opérations mesh | extrude, inset, bevel |
| `object` | Transformations | move, rotate, scale |
| `modifier` | Modificateurs | array, mirror, subsurf |
| `selection` | Sélection | select-by-index, select-loop |
| `material` | Matériaux | create, assign |
| `uv` | UV mapping | unwrap, pack-islands |
| `vision` | Viewport/screenshots | screenshot, diff, heatmap |
| `diag` | Diagnostic | scene-snapshot, validate |
| `dev` | Développement | exec-python |

---

## 🛡️ Safety Levels

| Level | Description | Quand utiliser |
|-------|-------------|----------------|
| `safe-first` | Pas de View3D requis | Data operations, snapshots, diagnostics |
| `view3d-auto` | Auto-active View3D | Screenshots, renders (tente d'activer) |
| `view3d-required` | View3D obligatoire | Opérations viewport complexes |

---

## ✅ Checklist Nouvel Outil

- [ ] Fonction implémentée dans `executor.py`
- [ ] Schema créé dans `specs_v2.py`
- [ ] Wrapper créé dans `registry.py`
- [ ] ToolDefinition ajouté à TOOLS
- [ ] Catégorie et tags appropriés
- [ ] Safety level correct
- [ ] Description claire
- [ ] `validate_tools.py` passe
- [ ] Tests pytest passent
- [ ] Testé dans Blender

---

## 🚨 Erreurs Communes

### 1. "Tool not displayed server-side"

**Cause:** Fonction manquante dans executor.py
**Solution:** Vérifier que la fonction existe et est publique (pas de `_`)

### 2. Schema validation error

**Cause:** Schema mal formé ou paramètres incorrects
**Solution:** Vérifier le schema dans specs_v2.py

### 3. Bridge connection timeout

**Cause:** Serveur Blender pas démarré ou port incorrect
**Solution:** Relancer le serveur MCP dans Blender

### 4. Import errors

**Cause:** Imports circulaires ou modules manquants
**Solution:** Vérifier les imports dans executor.py

---

## 💡 Tips

### Performance

- Utiliser `_require_bpy()` pour check Blender au début
- Prefer bmesh pour opérations complexes (plus rapide)
- Utiliser `viewport_screenshot_complete` pour screenshots (OpenGL rapide)

### Robustesse

- Toujours utiliser try/except avec `error_response()`
- Valider les arguments au début de la fonction
- Retourner des résultats structurés avec `ok_response()`

### Maintenance

- Documenter avec docstrings claires
- Utiliser des noms explicites (pas d'abréviations)
- Grouper les outils similaires dans même catégorie

---

## 📚 Documentation Complète

- [DYNAMIC_TOOL_DISCOVERY.md](DYNAMIC_TOOL_DISCOVERY.md) - Système de découverte automatique
- [FIXES_APPLIED.md](FIXES_APPLIED.md) - Correctifs de performance
- [VISION_TOOLS_IMPLEMENTATION_PROMPTS.md](VISION_TOOLS_IMPLEMENTATION_PROMPTS.md) - Guide vision tools

---

## 🎯 Exemples Complets

### Outil Simple

```python
# executor.py
def mesh_select_random(args: Dict[str, Any]) -> Dict[str, Any]:
    """Randomly select mesh elements."""
    bpy = _require_bpy()
    ratio = args.get('ratio', 0.5)

    try:
        bpy.ops.mesh.select_random(ratio=ratio)
        return ok_response(result={"selected": True})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")

# specs_v2.py
MESH_SELECT_RANDOM_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "ratio": {"type": "number", "default": 0.5, "minimum": 0, "maximum": 1}
    },
    "additionalProperties": False,
}

# registry.py
def _tool_blender_mesh_select_random(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-select-random", _clean_args(args))

ToolDefinition(
    name="blender-mesh-select-random",
    description="Randomly select mesh elements by ratio",
    input_schema=specs_v2.MESH_SELECT_RANDOM_SCHEMA,
    impl=_tool_blender_mesh_select_random,
    category="selection",
    tags=["random", "select"],
    safety_level="safe-first",
),
```

### Outil Complexe avec Validation

```python
# executor.py
def object_align_to_axis(args: Dict[str, Any]) -> Dict[str, Any]:
    """Align object to specific axis."""
    bpy = _require_bpy()

    obj_name = args.get('object_name')
    axis = args.get('axis')  # 'X', 'Y', or 'Z'
    align_mode = args.get('align_mode', 'CENTER')

    # Validation
    if not obj_name:
        return error_response("object_name required", code="bad_request")

    obj, err = _get_object(bpy, obj_name)
    if err:
        return err

    try:
        # Implementation
        if axis == 'X':
            obj.location.x = 0 if align_mode == 'CENTER' else obj.location.x
        elif axis == 'Y':
            obj.location.y = 0 if align_mode == 'CENTER' else obj.location.y
        elif axis == 'Z':
            obj.location.z = 0 if align_mode == 'CENTER' else obj.location.z

        return ok_response(result={
            "aligned": True,
            "axis": axis,
            "location": list(obj.location)
        })
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")
```

---

## 🏁 C'est Tout!

Le système est maintenant **100% automatique** pour le routing.

**Plus jamais d'erreur "tool not displayed server-side"!** ✨
