# Claude Chat → MCP Tool → Automatic Integration

Guide pour utiliser le tool MCP `submit-tool-spec` qui permet à **Claude Chat** de soumettre directement des spécifications de tools dans le repo **sans intervention manuelle**.

---

## 🎯 Nouveau Workflow (Automatisé)

```
Claude Chat
    ↓ [appelle MCP tool: submit-tool-spec]
    ↓ [écrit JSON automatiquement]
D:\ATHENA\tools\specs\_from_claude_chat\<timestamp>-<tool-name>.json
    ↓ [Claude Code valide et génère]
Code intégré ✅
```

**Fini le copier-coller manuel !** 🚀

---

## 📋 Instructions pour Claude Chat

### Étape 1 : Charger le Prompt Système

Copie le contenu de `tools/CLAUDE_CHAT_PROMPT.md` dans Claude Chat pour configurer la génération de specs.

### Étape 2 : Générer ET Soumettre la Spec

Au lieu de simplement retourner le JSON, **utilise le tool MCP** :

```
Utilisateur: "Generate and submit a spec for adding a cylinder primitive"
```

**Claude Chat doit :**

1. Générer la spec JSON complète
2. Appeler le tool MCP `submit-tool-spec` avec :
   ```json
   {
     "spec": {
       "tool_name": "blender-primitives-add-cylinder",
       "category": "primitives",
       ...
     },
     "tool_name": "cylinder"
   }
   ```

### Étape 3 : Confirmation Automatique

Le tool MCP retourne :

```json
{
  "status": "saved",
  "saved_to": "tools/specs/_from_claude_chat/20250128-163045-cylinder.json",
  "timestamp": "20250128-163045",
  "tool_name": "cylinder",
  "next_steps": [
    "1. Validate: python tools/validator.py tools/specs/_from_claude_chat/20250128-163045-cylinder.json",
    "2. If valid, move to validated/: Move-Item ...",
    "3. Generate code: python tools/codegen.py ..."
  ]
}
```

**Le fichier est créé automatiquement dans le repo !** ✅

---

## 🔧 Paramètres du Tool `submit-tool-spec`

| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `spec` | object | Spec JSON complète | `{"tool_name": "blender-...", ...}` |
| `tool_name` | string | Nom court pour le fichier | `"cylinder"`, `"mirror-modifier"` |

---

## 💡 Exemples d'Utilisation

### Exemple 1 : Primitive Cylinder

**Requête utilisateur :**
```
Generate and submit a spec for adding a cylinder primitive with radius, depth, and vertices
```

**Claude Chat génère la spec, puis appelle :**
```json
{
  "tool": "submit-tool-spec",
  "args": {
    "spec": {
      "tool_name": "blender-primitives-add-cylinder",
      "category": "primitives",
      "priority": "high",
      "safe_first": true,
      "description": "Add a cylinder primitive to the scene with configurable radius, depth, and vertex count.",
      "input_schema": {
        "type": "object",
        "properties": {
          "name": {"type": "string", "default": "Cylinder", "description": "Name of the cylinder"},
          "radius": {"type": "number", "default": 1.0, "minimum": 0.001, "description": "Cylinder radius"},
          "depth": {"type": "number", "default": 2.0, "minimum": 0.001, "description": "Cylinder depth"},
          "vertices": {"type": "integer", "default": 32, "minimum": 3, "maximum": 512, "description": "Number of vertices"}
        },
        "additionalProperties": false
      },
      "expected_result": {
        "name": "string - actual object name",
        "location": "[x, y, z]",
        "radius": "number",
        "depth": "number"
      },
      "blender_pseudocode": [
        "1. Extract parameters: name, radius, depth, vertices",
        "2. Generate unique name",
        "3. Create bmesh with create_cone (radius1=radius2 for cylinder)",
        "4. Link to scene",
        "5. Return ok_response with details"
      ],
      "test_cases": [
        {"name": "test_default", "args": {}, "expected_ok": true, "validates": "Default cylinder created"},
        {"name": "test_custom", "args": {"radius": 2.0, "depth": 5.0, "vertices": 64}, "expected_ok": true, "validates": "Custom parameters applied"}
      ],
      "example_usage": {
        "name": "blender-primitives-add-cylinder",
        "args": {"radius": 1.5, "depth": 3.0, "vertices": 48}
      }
    },
    "tool_name": "cylinder"
  }
}
```

**Résultat :** Fichier créé automatiquement à `tools/specs/_from_claude_chat/20250128-163045-cylinder.json`

---

### Exemple 2 : Mirror Modifier

**Requête utilisateur :**
```
Generate and submit a spec for mirror modifier with X/Y/Z axis selection
```

**Claude Chat appelle :**
```json
{
  "tool": "submit-tool-spec",
  "args": {
    "spec": {
      "tool_name": "blender-modifiers-add-mirror",
      ...
    },
    "tool_name": "mirror-modifier"
  }
}
```

**Résultat :** Fichier créé à `tools/specs/_from_claude_chat/20250128-164512-mirror-modifier.json`

---

## 🔄 Workflow Complet (Côté Claude Code)

Une fois que Claude Chat a soumis la spec via le tool MCP :

### 1. Validation (Claude Code)

```bash
python tools/validator.py tools/specs/_from_claude_chat/20250128-163045-cylinder.json
```

### 2. Déplacement si Validé

```powershell
Move-Item tools/specs/_from_claude_chat/20250128-163045-cylinder.json `
          tools/specs/validated/blender-primitives-add-cylinder.json
```

### 3. Génération de Code

```bash
python tools/codegen.py tools/specs/validated/blender-primitives-add-cylinder.json tools
```

### 4. Intégration

Suivre le guide `tools/generated/blender-primitives-add-cylinder/INTEGRATION_GUIDE.md`

### 5. Tests & Commit

```bash
pytest tests/test_blender_primitives_add_cylinder.py -v
git add .
git commit -m "feat(primitives): add cylinder primitive"
```

---

## ✨ Avantages

| Avant | Après |
|-------|-------|
| 1. Claude Chat génère JSON | 1. Claude Chat génère ET soumet |
| 2. Copier JSON manuellement | ~~2. Copier manuellement~~ ✅ Automatique |
| 3. Coller dans fichier | ~~3. Coller~~ ✅ Automatique |
| 4. Sauvegarder avec timestamp | ~~4. Timestamp~~ ✅ Automatique |
| 5. Valider | 5. Valider (inchangé) |
| 6. Générer | 6. Générer (inchangé) |
| 7. Intégrer | 7. Intégrer (inchangé) |

**Gain : 3 étapes manuelles éliminées !** 🎉

---

## 🛠️ Template pour Claude Chat

Voici un template de requête pour Claude Chat :

```
Generate and submit a spec for [DESCRIPTION]

Tool details:
- Category: [primitives|modifiers|materials|macros|collections]
- Parameters: [LIST PARAMETERS]
- Constraints: [MIN/MAX VALUES]
- Defaults: [DEFAULT VALUES]

Use the submit-tool-spec MCP tool to save it directly to the repo.
```

**Exemple concret :**
```
Generate and submit a spec for adding a torus primitive

Tool details:
- Category: primitives
- Parameters: major_radius, minor_radius, major_segments, minor_segments
- Constraints: radii > 0.001, segments between 3-512
- Defaults: major_radius=1.0, minor_radius=0.25, major_segments=48, minor_segments=12

Use the submit-tool-spec MCP tool to save it directly to the repo.
```

---

## 🔍 Vérification

Pour vérifier que le tool MCP est disponible dans Claude Chat :

1. Ouvrir Claude Chat
2. Vérifier que le serveur MCP `blender` est connecté
3. Lister les tools disponibles (devrait inclure `submit-tool-spec`)

---

## 📂 Structure des Fichiers

```
tools/specs/
├── _from_claude_chat/           # Specs soumises via MCP tool
│   ├── .gitkeep
│   └── 20250128-163045-cylinder.json
├── validated/                   # Specs validées (prêtes pour génération)
│   └── .gitkeep
└── archive/                     # Specs intégrées (historique)
    └── .gitkeep
```

---

## ⚠️ Important

- Le tool `submit-tool-spec` est **standalone** : pas besoin de lancer Blender !
- Le serveur MCP doit être en cours d'exécution
- Le fichier est créé avec un timestamp automatique pour éviter les collisions
- Le `tool_name` court (ex: `"cylinder"`) est utilisé pour le nom de fichier
- Le `tool_name` complet (ex: `"blender-primitives-add-cylinder"`) est dans la spec

---

## 🚀 Prochaines Étapes

Possibilités d'amélioration futures :

1. **Auto-validation** : Le tool MCP pourrait appeler `validator.py` automatiquement
2. **Auto-génération** : Si validé, lancer `codegen.py` automatiquement
3. **Notification** : Notifier Claude Code qu'une nouvelle spec est prête
4. **Batch submission** : Soumettre plusieurs specs d'un coup

---

## 🎯 Résumé

**Avant :** Claude Chat → Clipboard → Script manuel → Validation

**Maintenant :** Claude Chat → MCP Tool `submit-tool-spec` → Fichier créé ✅

**Gain :** Workflow automatisé, zéro copier-coller, zéro erreur manuelle ! 🚀
