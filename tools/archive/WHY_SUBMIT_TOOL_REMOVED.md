# Pourquoi le système `submit-tool-spec` a été retiré

**Date** : 2025-12-28
**Raison** : Workflow obsolète avec Claude Code

## Contexte

Le système `dev-submit-tool-spec` a été créé pour permettre à **Claude Chat** (interface web) de soumettre des spécifications de tools au repository ATHENA sans intervention manuelle.

### Workflow original (Claude Chat)

```
Claude Chat (Web)
    ↓ Design de l'API
    ↓ Génération de la spec JSON
    ↓ Appel MCP tool: dev-submit-tool-spec
    ↓ Sauvegarde dans tools/specs/_from_claude_chat/

Développeur
    ↓ Validation manuelle
    ↓ Implémentation du code
    ↓ Tests
```

### Problèmes

1. **Friction** : Switch entre Claude Chat et l'éditeur de code
2. **Perte de contexte** : La spec JSON perd la richesse de la conversation
3. **Double validation** : Chat valide → Code valide → Implémentation
4. **Pas d'accès au codebase** : Claude Chat ne peut pas explorer les patterns existants

## Solution : Claude Code uniquement

Avec **Claude Code CLI**, tout le workflow se fait en une seule session conversationnelle :

```
Claude Code (CLI)
    ↓ Exploration du codebase (Grep/Glob/Read)
    ↓ Discussion de l'architecture
    ↓ Écriture du code directement (Edit/Write)
    ↓ Tests (Bash)
    ↓ Itération rapide
    ✅ Terminé !
```

### Avantages

- ✅ **Contexte complet** : Accès à tout le repo
- ✅ **Patterns cohérents** : Voit les implémentations existantes
- ✅ **Itération rapide** : Design + Code + Test dans la même session
- ✅ **Pas de friction** : Pas de switch entre interfaces
- ✅ **Meilleur code** : Refactoring possible si nécessaire

## Fichiers supprimés

1. **`src/athena_mcp/tools/registry.py`** :
   - Fonction `_tool_submit_tool_spec()` (lignes 341-386)
   - ToolDefinition `dev-submit-tool-spec` dans TOOLS

2. **`src/athena_mcp/tools/devtools.py`** :
   - Schema `SUBMIT_TOOL_SPEC_SCHEMA`

3. **`tests/test_submit_tool_spec.py`** :
   - Tests unitaires du tool

4. **Documentation** (archivée) :
   - `tools/CLAUDE_CHAT_MCP_WORKFLOW.md`
   - `tools/CLAUDE_CHAT_PROMPT.md`

## Résultat

- **Avant** : 42 tools MCP (dont 1 obsolète)
- **Après** : 41 tools MCP (tous utiles)
- Simplification du workflow
- Meilleure expérience développeur

## Pour référence

Les specs archivées dans `tools/specs/_from_claude_chat/` sont conservées pour historique mais ne sont plus utilisées.

Le workflow actuel recommandé est :

**Utilisez uniquement Claude Code pour tout :**
- Conception
- Exploration
- Implémentation
- Tests
- Documentation
