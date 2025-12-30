# Tool Specifications Directory

Ce dossier contient les spécifications JSON des tools Blender pour Athena MCP.

## 🚀 Nouveau Workflow (Automatisé via MCP Tool)

**Claude Chat** peut maintenant soumettre directement des specs sans intervention manuelle !

```
Claude Chat → [MCP tool: submit-tool-spec] → Fichier créé automatiquement ✅
```

Voir [CLAUDE_CHAT_MCP_WORKFLOW.md](../CLAUDE_CHAT_MCP_WORKFLOW.md) pour le guide complet.

---

## 📂 Structure

```
specs/
├── README.md                     # Ce fichier
├── _from_claude_chat/           # Specs soumises via MCP tool
│   ├── .gitkeep
│   └── YYYYMMDD-HHMMSS-<tool-name>.json
├── validated/                   # Specs validées (prêtes pour génération)
│   ├── .gitkeep
│   └── blender-<category>-<action>.json
└── archive/                     # Specs intégrées (historique)
    ├── .gitkeep
    └── blender-<category>-<action>.json
```

---

## 🔄 Workflow

### Option A : Via MCP Tool (Recommandé)

**1. Claude Chat génère ET soumet**

```
User: "Generate and submit a spec for adding a cylinder primitive"
```

Claude Chat appelle automatiquement le tool MCP `submit-tool-spec`.

**2. Fichier créé automatiquement**

Le fichier est sauvegardé dans `_from_claude_chat/YYYYMMDD-HHMMSS-<tool-name>.json`

**3. Validation (Claude Code)**

```bash
python tools/validator.py tools/specs/_from_claude_chat/20250128-163045-cylinder.json
```

**4. Déplacement si validé**

```powershell
Move-Item tools/specs/_from_claude_chat/20250128-163045-cylinder.json `
          tools/specs/validated/blender-primitives-add-cylinder.json
```

**5. Génération de code**

```bash
python tools/codegen.py tools/specs/validated/blender-primitives-add-cylinder.json tools
```

**6. Intégration**

Suivre `tools/generated/<tool-name>/INTEGRATION_GUIDE.md`

**7. Tests & Commit**

```bash
pytest tests/test_<tool-name>.py -v
git add .
git commit -m "feat(primitives): add cylinder primitive"
```

**8. Archivage**

```powershell
Move-Item tools/specs/validated/blender-primitives-add-cylinder.json `
          tools/specs/archive/
```

---

### Option B : Manuel (Ancien Workflow)

Si le serveur MCP n'est pas disponible, le workflow manuel reste possible :

1. Copier le JSON de Claude Chat
2. Sauvegarder avec `.\tools\save-from-clipboard.ps1 <tool-name>`
3. Continuer à l'étape 3 ci-dessus

---

## 🎯 Avantages du MCP Tool

| Avant | Après |
|-------|-------|
| Copier JSON manuellement | ✅ Automatique |
| Coller dans fichier | ✅ Automatique |
| Sauvegarder avec timestamp | ✅ Automatique |
| Validation | (Inchangé) |
| Génération | (Inchangé) |

**3 étapes manuelles éliminées !** 🎉

---

## 📋 Format des Specs

Voir [TOOL_SPEC_TEMPLATE.json](../TOOL_SPEC_TEMPLATE.json) pour le template complet.

### Champs Requis

```json
{
  "tool_name": "blender-<category>-<action>",
  "category": "primitives|modifiers|materials|macros|collections",
  "priority": "high|medium|low",
  "safe_first": true|false,
  "description": "Description courte",
  "input_schema": { ... },
  "expected_result": { ... },
  "blender_pseudocode": [ ... ],
  "test_cases": [ ... ],
  "example_usage": { ... }
}
```

---

## 🛠️ Catégories

- **primitives** : Formes de base (cube, sphere, cylinder, cone, plane, torus)
- **modifiers** : Modificateurs mesh (subdivision, mirror, array, bevel, solidify)
- **materials** : Opérations matériaux (create, assign, set properties)
- **macros** : Création d'assets (table, chair, bottle, lamp)
- **collections** : Organisation scène (create, link, unlink)

---

## 📖 Documentation

- **Guide MCP Tool** : [CLAUDE_CHAT_MCP_WORKFLOW.md](../CLAUDE_CHAT_MCP_WORKFLOW.md)
- **Guide Manuel** : [WORKFLOW_CLAUDE_CHAT.md](../WORKFLOW_CLAUDE_CHAT.md)
- **Prompt Claude Chat** : [CLAUDE_CHAT_PROMPT.md](../CLAUDE_CHAT_PROMPT.md)
- **Template** : [TOOL_SPEC_TEMPLATE.json](../TOOL_SPEC_TEMPLATE.json)
- **Guide Complet** : [README.md](../README.md)

---

## ✅ Checklist d'Intégration

- [ ] Spec soumise via MCP tool ou sauvegardée manuellement
- [ ] Spec validée avec `validator.py`
- [ ] Spec déplacée vers `validated/`
- [ ] Code généré avec `codegen.py`
- [ ] Schéma ajouté à `src/athena_mcp/tools/<category>.py`
- [ ] Fonction registry ajoutée à `src/athena_mcp/tools/registry.py`
- [ ] Fonction executor ajoutée à `src/athena_mcp/blender_bridge/executor.py`
- [ ] Router entry ajouté à `src/athena_mcp/blender_bridge/provider_http.py`
- [ ] Tool definition ajouté à TOOLS list dans `registry.py`
- [ ] Test file créé `tests/test_<tool-name>.py`
- [ ] Logique Blender implémentée (TODO remplacé)
- [ ] Tests passent (`pytest tests/test_<tool-name>.py -v`)
- [ ] Code committé
- [ ] Spec archivée vers `archive/`

---

## 🔍 Vérification

Pour vérifier que le tool MCP `submit-tool-spec` est disponible :

```bash
# Lancer le serveur MCP
python -m athena_mcp.mcp_core.server --stdio

# Dans Claude Chat, vérifier la liste des tools
# Le tool "submit-tool-spec" devrait être disponible
```

---

## 🚨 Troubleshooting

**Q: Le tool MCP n'est pas disponible dans Claude Chat**
- Vérifier que le serveur MCP est en cours d'exécution
- Vérifier la configuration dans `claude_desktop_config.json`
- Redémarrer Claude Desktop

**Q: La validation échoue**
- Vérifier la syntaxe JSON (trailing commas, guillemets)
- Vérifier que tous les champs requis sont présents
- Utiliser `clean-spec.py` si du markdown est présent

**Q: La génération de code échoue**
- Re-valider la spec avec `validator.py`
- Vérifier les permissions de fichiers
- Vérifier que le dossier `tools/generated/` existe

---

## 📊 Statistiques

**Temps estimé par tool :**
- Avec MCP Tool : ~18 minutes (3 étapes manuelles éliminées)
- Sans MCP Tool : ~22 minutes (workflow manuel complet)

**Gain : ~18% de temps économisé !** ⏱️

---

## 🎉 Conclusion

Le workflow automatisé via MCP tool rend l'intégration de nouveaux tools Blender **plus rapide** et **sans erreur manuelle**.

Claude Chat → MCP Tool → Fichier créé → Validation → Génération → Intégration ✅
