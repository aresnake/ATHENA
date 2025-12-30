# Vision Tools - Priorités et Décisions

**Date:** 2025-12-30
**Statut Actuel:** 9 outils déclarés, 0 implémentés

---

## Option 1: Retirer les Outils Non Implémentés (Rapide - 15 min)

### Avantages
- ✅ Système immédiatement "production ready" sans fausses promesses
- ✅ Pas de confusion pour les utilisateurs
- ✅ Documentation honnête et claire
- ✅ Tests ne testent que ce qui existe vraiment

### Actions
1. Supprimer les 9 ToolDefinition de registry.py
2. Supprimer les 9 handlers _tool_athena_viewport_* de registry.py
3. Supprimer test_vision_registry.py
4. Mettre à jour les rapports (131 outils au lieu de 140)
5. Documenter dans ROADMAP.md comme "planned features"

### Temps: ~15 minutes

---

## Option 2: Implémenter les Outils (Long - plusieurs heures)

### Difficulté par outil

#### 🟢 FACILE (1-2h chacun)
1. **viewport-screenshot-complete** ⭐ PRIORITÉ
   - Fondation pour tous les autres
   - Screenshots multi-vues simples
   - Pas de post-processing complexe

2. **viewport-annotate-markup**
   - Utilise PIL pour dessiner sur images
   - Projections 3D→2D standard

3. **viewport-compare-matrix**
   - Simple composition d'images en grille
   - Utilise viewport-screenshot-complete

#### 🟡 MOYEN (2-4h chacun)
4. **viewport-diff-comparison**
   - Comparaison d'images pixel par pixel
   - Calculs de différences géométriques optionnels

5. **viewport-selection-isolate-capture**
   - Gestion de sélection BMesh
   - Framing automatique (calculs bbox)

6. **viewport-measurement-overlay**
   - Projections 3D→2D pour mesures
   - Formatage d'unités

#### 🔴 DIFFICILE (4-8h chacun)
7. **validate-operation-visual**
   - Workflow complet (before/after/validate)
   - Dépend de plusieurs autres outils
   - Génération de rapports

8. **viewport-geometry-heatmap**
   - Calculs de métriques géométriques (courbure, etc.)
   - Application de vertex colors
   - Gradient de couleurs

9. **viewport-xray-section-view**
   - Manipulation de géométrie (bisect)
   - Modes de rendu spéciaux
   - Gestion de materials temporaires

### Ordre Recommandé
1. viewport-screenshot-complete (fondation)
2. viewport-annotate-markup (simple, utile)
3. viewport-diff-comparison (utilise #1)
4. viewport-measurement-overlay (utilise #1)
5. viewport-compare-matrix (utilise #1)
6. viewport-selection-isolate-capture (utilise #1)
7. validate-operation-visual (utilise #1, #3)
8. viewport-geometry-heatmap (complexe)
9. viewport-xray-section-view (complexe)

### Temps Total Estimé: 20-40 heures

---

## Option 3: Implémentation Partielle (Compromis - 4-8h)

### Stratégie: Implémenter seulement les 3-4 outils les plus utiles

**Outils à garder:**
1. ✅ **viewport-screenshot-complete** (fondation, très utile)
2. ✅ **viewport-annotate-markup** (utile pour documentation)
3. ✅ **viewport-diff-comparison** (utile pour validation)
4. ⚠️ **validate-operation-visual** (si temps disponible)

**Outils à retirer:**
- viewport-selection-isolate-capture
- viewport-measurement-overlay
- viewport-compare-matrix
- viewport-geometry-heatmap
- viewport-xray-section-view

### Avantages
- ✅ Fonctionnalités core disponibles
- ✅ Temps raisonnable (4-8h)
- ✅ Système utilisable pour cas d'usage principaux

### Actions
1. Implémenter 3-4 outils prioritaires
2. Retirer les 5-6 autres de registry.py
3. Documenter les outils disponibles vs roadmap

---

## Recommandation

**Pour un système "production ready" MAINTENANT:**
→ **Option 1** (retirer tout)

**Pour avoir des fonctionnalités vision utiles rapidement:**
→ **Option 3** (3-4 outils core)

**Pour un système complet:**
→ **Option 2** (tout implémenter, ~40h)

---

## Considérations Techniques

### Mode Headless vs UI

**Problème actuel:**
- MCP tourne en headless (pas de GUI Blender)
- Beaucoup d'outils vision nécessitent context.area (viewport)

**Solutions:**

1. **Offscreen Rendering** (headless-safe)
   ```python
   import gpu
   offscreen = gpu.types.GPUOffScreen(width, height)
   with offscreen.bind():
       # Render ici
   ```
   - ✅ Fonctionne en headless
   - ⚠️ Pas d'overlays Blender natifs
   - ⚠️ Nécessite setup manuel de tout

2. **Bridge avec UI Blender**
   - ✅ Accès à vrais viewports
   - ✅ Overlays natifs Blender
   - ⚠️ Nécessite Blender avec GUI ouvert

3. **Hybrid:** Détection du mode
   ```python
   if bpy.app.background:
       # Mode headless: offscreen rendering
       use_offscreen_render()
   else:
       # Mode UI: utiliser context.area
       use_viewport_render()
   ```

**Recommandation:** Approche hybrid

### Dépendances

**Requises:**
- Pillow (PIL) - pour manipulation d'images
  ```bash
  pip install Pillow
  ```

**Optionnelles:**
- numpy - pour calculs de différences optimisés
- matplotlib - pour heatmaps (alternative: PIL seulement)

### Performance

**Considérations:**
- Screenshots haute résolution (4K) = lents
- Offscreen rendering = coûteux en GPU
- Composer plusieurs vues = multiplier le temps

**Optimisations:**
- Résolution par défaut raisonnable (1920x1080)
- Cache des caméras temporaires
- Réutilisation des offscreen buffers
- Parallélisation possible pour multi-vues

---

## Tests

### Tests Actuels
- test_vision_registry.py vérifie seulement l'enregistrement
- Pas de tests d'intégration réels

### Tests à Ajouter (si implémentation)

```python
# tests/test_vision_integration.py

def test_viewport_screenshot_basic():
    """Test capture simple d'un cube"""
    # Créer cube
    result = call_tool('blender-primitive-cube', {'name': 'TestCube'})

    # Capturer
    result = call_tool('athena-viewport-screenshot-complete', {
        'object_name': 'TestCube',
        'views': ['FRONT'],
        'output': {'format': 'separate'}
    })

    assert result['ok']
    assert os.path.exists(result['result']['screenshots'][0])

def test_viewport_diff_comparison():
    """Test comparaison avant/après"""
    # Setup
    create_cube()
    before = screenshot()

    # Modifier
    scale_object('Cube', 2.0)

    # Comparer
    result = diff_comparison(before, after)
    assert result['differences_detected'] == True
```

**Stratégie de tests:**
- Tests unitaires pour helpers (world_to_screen, etc.)
- Tests d'intégration pour workflow complets
- Tests visuels manuels (vérifier images générées)

---

## Documentation

### À Mettre à Jour

Si **Option 1** (retrait):
- ❌ Supprimer section Vision Tools de AUDIT_REPORT.md
- ❌ Supprimer mention dans MCP_COMPLIANCE_REPORT.md
- ✅ Créer ROADMAP.md avec vision tools comme "planned"
- ✅ README: Mentionner comme feature future

Si **Option 2/3** (implémentation):
- ✅ Garder ATHENA_VISION_TOOLS_SPEC.md
- ✅ Ajouter exemples d'utilisation
- ✅ Screenshots de démo
- ✅ Guide de troubleshooting (contexte manquant, etc.)

---

## Décision Finale

**À toi de décider:**

1. **Retirer maintenant, implémenter plus tard?**
   - Système clean et honnête
   - Pas de promesses non tenues
   - Roadmap claire pour futures features

2. **Implémenter minimum viable (3 outils)?**
   - Fonctionnalités utiles rapidement
   - Démo possible des capacités
   - Compromis temps/valeur

3. **Implémenter tout (9 outils)?**
   - Système complet comme promis
   - Beaucoup de temps nécessaire
   - Maximum de valeur finale

**Ma recommandation personnelle:** Option 1 pour maintenant, puis Option 3 progressivement.

---

## Next Steps

### Si Option 1 (Retrait)
```bash
# 1. Retirer de registry.py
# 2. Retirer test_vision_registry.py
# 3. Mettre à jour rapports
# 4. Créer ROADMAP.md
# 5. Commit
```

### Si Option 2/3 (Implémentation)
```bash
# 1. Installer Pillow
pip install Pillow

# 2. Implémenter dans executor.py
# Utiliser les prompts de VISION_TOOLS_IMPLEMENTATION_PROMPTS.md

# 3. Tester chaque outil

# 4. Ajouter tests d'intégration

# 5. Mettre à jour documentation avec exemples

# 6. Commit par outil (commits atomiques)
```

---

**Choix à faire maintenant:** 1, 2 ou 3?
