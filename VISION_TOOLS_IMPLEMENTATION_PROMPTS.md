# Prompts pour Implémentation des Vision Tools - ATHENA

**Objectif:** Implémenter les 9 outils vision dans `executor.py` pour capturer des screenshots et analyses visuelles de Blender.

---

## Contexte Technique

**Fichiers concernés:**
- `src/athena_mcp/blender_bridge/executor.py` - Implémentations réelles
- `src/athena_mcp/tools/vision_specs.py` - Schemas JSON (déjà fait)
- `src/athena_mcp/tools/registry.py` - Déclarations (déjà fait)

**Architecture actuelle:**
- Les outils sont DÉJÀ enregistrés dans registry.py
- Les schemas JSON sont DÉJÀ définis dans vision_specs.py
- Les stubs existent dans athena_vision_tools/ (peuvent être ignorés)
- Il faut SEULEMENT implémenter les fonctions dans executor.py

**Contraintes Blender:**
- Mode headless (pas de GUI) mais bridge peut être en UI
- Utiliser `bpy.context.scene`, `bpy.data`, etc.
- Pour screenshots: utiliser offscreen rendering ou bpy.ops.render
- Accès au viewport via context override si UI disponible

---

## Prompt 1: viewport-screenshot-complete

**Fonction à implémenter dans executor.py:**

```python
def viewport_screenshot_complete(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Capture viewport screenshots across multiple views/shading modes.

    Args déjà validés par schema:
    - object_name (str): Objet à capturer
    - views (list): ["FRONT", "RIGHT", "TOP", "ISO_FRONT_RIGHT", etc.]
    - shading_mode (list): ["SOLID", "WIREFRAME", "MATERIAL", etc.]
    - projection (str): "ORTHO" ou "PERSP"
    - overlay_modes (dict): Options d'overlay (wireframe, edges, etc.)
    - output (dict): Format de sortie et résolution
    - resolution (list): [width, height]

    Retourne:
    {
        "ok": True,
        "result": {
            "screenshots": ["path1.png", "path2.png", ...],
            "views_captured": ["FRONT", "RIGHT", ...],
            "metadata": {...}
        }
    }
    """
```

**Implémentation requise:**

1. **Setup Scene:**
   - Sélectionner l'objet `object_name`
   - Frame l'objet dans la vue (bpy.ops.view3d.view_selected ou équivalent)

2. **Pour chaque vue dans `views`:**
   - Positionner la caméra selon la vue (FRONT, RIGHT, TOP, ISO)
   - Appliquer le mode de projection (ORTHO/PERSP)
   - Configurer les overlays selon `overlay_modes`

3. **Pour chaque shading_mode:**
   - Appliquer le shading (SOLID, WIREFRAME, MATERIAL, RENDERED)
   - Capturer le screenshot

4. **Méthode de capture:**
   ```python
   # Option A: Offscreen rendering (headless-safe)
   import bpy
   import gpu
   from gpu_extras.presets import draw_texture_2d

   # Créer offscreen buffer
   offscreen = gpu.types.GPUOffScreen(width, height)

   # Option B: Render API (si context disponible)
   bpy.context.scene.render.filepath = output_path
   bpy.ops.render.opengl(write_still=True)
   ```

5. **Gestion des overlays:**
   - `overlay_modes.show_wireframe` → activer wireframe overlay
   - `overlay_modes.show_edges` → activer edge display
   - etc.

6. **Format de sortie:**
   - `output.format = "composite_grid"` → Combiner toutes les vues en grille
   - `output.format = "separate"` → Fichiers séparés
   - Utiliser PIL/Pillow pour composer les images

**Contraintes:**
- Utiliser tempfile pour chemins temporaires si non spécifié
- Restaurer l'état de la scène après capture
- Gérer les erreurs (objet introuvable, contexte manquant, etc.)

---

## Prompt 2: viewport-diff-comparison

**Fonction à implémenter:**

```python
def viewport_diff_comparison(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare before/after viewport captures avec diff overlays.

    Args:
    - before_snapshot (dict): État de la scène avant
    - before_screenshot (str or dict): Screenshot(s) avant
    - output_path (str): Chemin de sortie
    - views (list): Vues à comparer
    - diff_mode (str): "overlay", "side_by_side", "split_view"
    - geometry_diff (dict): Options de diff géométrique
    - highlight_color (list): Couleur RGB pour highlights

    Retourne screenshots annotés avec différences visuelles
    """
```

**Implémentation:**

1. **Capturer l'état actuel (after):**
   - Screenshot de la scène actuelle avec mêmes vues que before
   - Utiliser viewport_screenshot_complete() en interne

2. **Comparer les images:**
   ```python
   from PIL import Image, ImageChops

   before_img = Image.open(before_screenshot)
   after_img = Image.open(after_screenshot)

   # Différence pixel par pixel
   diff = ImageChops.difference(before_img, after_img)

   # Appliquer seuil pour ignorer petites variations
   threshold = 10
   diff = diff.point(lambda p: p > threshold and 255)
   ```

3. **Geometry diff (optionnel):**
   - Comparer vertex positions avant/après
   - Dessiner vecteurs de déplacement sur l'image
   - Utiliser `geometry_diff.track_vertices = True`

4. **Modes de sortie:**
   - `side_by_side`: Concaténer before | after horizontalement
   - `overlay`: Superposer avec transparence
   - `split_view`: Barre de séparation interactive (statique pour image)

5. **Annotations:**
   - Ajouter labels "Before" / "After"
   - Highlight zones modifiées avec `highlight_color`
   - Légende avec stats (pixels changés, etc.)

---

## Prompt 3: viewport-annotate-markup

**Fonction à implémenter:**

```python
def viewport_annotate_markup(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ajouter annotations et mesures visuelles sur screenshots.

    Args:
    - object_name (str)
    - output_path (str)
    - annotations (list): Liste d'annotations à ajouter
      - type: "arrow", "circle", "box", "text", "line", "highlight"
      - position: [x, y, z] en coordonnées 3D
      - content: Texte ou description
    - auto_annotate (dict): Auto-détection d'éléments
    - views (list): Vues à annoter

    Retourne screenshots annotés
    """
```

**Implémentation:**

1. **Capturer screenshot de base:**
   - Utiliser viewport_screenshot_complete()

2. **Pour chaque annotation manuelle:**
   ```python
   from PIL import Image, ImageDraw, ImageFont

   img = Image.open(screenshot_path)
   draw = ImageDraw.Draw(img)

   # Projeter position 3D → 2D viewport
   screen_pos = world_to_screen(annotation['position'], camera, resolution)

   if annotation['type'] == 'arrow':
       draw.line([start, end], fill=color, width=thickness)
       draw.polygon([arrow_head_points], fill=color)

   elif annotation['type'] == 'text':
       font = ImageFont.truetype("arial.ttf", size)
       draw.text(screen_pos, annotation['content'], fill=color, font=font)

   elif annotation['type'] == 'circle':
       bbox = [x-r, y-r, x+r, y+r]
       draw.ellipse(bbox, outline=color, width=thickness)
   ```

3. **Auto-annotations (optionnel):**
   ```python
   if auto_annotate.get('label_elements'):
       # Labelliser tous les objets visibles
       for obj in visible_objects:
           screen_pos = project_3d_to_2d(obj.location)
           draw.text(screen_pos, obj.name)

   if auto_annotate.get('show_measurements'):
       # Ajouter dimensions bbox
       dims = obj.dimensions
       draw.text(pos, f"{dims.x:.2f} × {dims.y:.2f} × {dims.z:.2f}")
   ```

4. **Projection 3D → 2D:**
   ```python
   import mathutils

   def world_to_screen(world_pos, camera, resolution):
       scene = bpy.context.scene
       co_2d = bpy_extras.object_utils.world_to_camera_view(
           scene, camera, mathutils.Vector(world_pos)
       )
       # Convertir normalized coords → pixels
       x = int(co_2d.x * resolution[0])
       y = int((1 - co_2d.y) * resolution[1])  # Flip Y
       return (x, y)
   ```

---

## Prompt 4: validate-operation-visual

**Fonction à implémenter:**

```python
def validate_operation_visual(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Workflow complet: capture avant, exécute opération, capture après, compare.

    Args:
    - operation (dict): Opération à exécuter
      - tool_name (str): Nom du tool à appeler
      - parameters (dict): Paramètres du tool
    - capture_config (dict): Config des captures
    - output_path (str)
    - validation (dict): Checks à effectuer
    - expectations (dict): Résultats attendus

    Retourne rapport de validation avec screenshots avant/après
    """
```

**Implémentation:**

1. **Capture BEFORE:**
   ```python
   before_screenshot = viewport_screenshot_complete({
       'object_name': operation.get('target_object'),
       'views': capture_config['views'],
       'output': {'format': 'separate'}
   })

   before_snapshot = {
       'vertex_count': len(obj.data.vertices),
       'face_count': len(obj.data.polygons),
       'volume': calculate_volume(obj),
       'bounds': obj.bound_box
   }
   ```

2. **Exécuter l'opération:**
   ```python
   # Appeler le tool spécifié
   tool_func = globals()[operation['tool_name']]
   result = tool_func(operation.get('parameters', {}))

   if not result.get('ok'):
       return error_response("Operation failed", details=result)
   ```

3. **Capture AFTER:**
   ```python
   after_screenshot = viewport_screenshot_complete(...)
   after_snapshot = { ... }  # Mêmes métriques
   ```

4. **Validation:**
   ```python
   validation_results = {}

   if validation.get('topology_checks'):
       validation_results['manifold'] = is_manifold(obj)
       validation_results['watertight'] = is_watertight(obj)

   if validation.get('geometry_checks'):
       validation_results['vertex_delta'] = after - before vertex count
       validation_results['volume_change'] = volume_after - volume_before

   # Comparer avec expectations
   if expectations:
       for key, expected in expectations.items():
           actual = validation_results.get(key)
           validation_results[f'{key}_match'] = actual == expected
   ```

5. **Générer rapport:**
   ```python
   # Créer diff comparison
   diff_images = viewport_diff_comparison({
       'before_screenshot': before_screenshot,
       'before_snapshot': before_snapshot,
       'output_path': output_path
   })

   # Compiler rapport
   report = {
       'operation': operation['tool_name'],
       'before': before_snapshot,
       'after': after_snapshot,
       'validation': validation_results,
       'screenshots': {
           'before': before_screenshot,
           'after': after_screenshot,
           'diff': diff_images
       }
   }

   # Sauver rapport JSON
   import json
   with open(f"{output_path}/report.json", 'w') as f:
       json.dump(report, f, indent=2)
   ```

---

## Prompt 5: viewport-selection-isolate-capture

**Fonction à implémenter:**

```python
def viewport_selection_isolate_capture(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Capture focused sur une sélection avec framing automatique.

    Args:
    - object_name (str)
    - selection_mode (str): "VERT", "EDGE", "FACE", "OBJECT"
    - selection_indices (list): Indices des éléments sélectionnés
    - framing (dict): Options de cadrage
    - context_display (dict): Affichage du reste de la scène
    - views (list)
    - output_path (str)
    """
```

**Implémentation:**

1. **Sélectionner les éléments:**
   ```python
   import bmesh

   obj = bpy.data.objects[object_name]
   bm = bmesh.from_edit_mesh(obj.data) if obj.mode == 'EDIT' else bmesh.new()

   if selection_mode == 'VERT':
       for idx in selection_indices:
           bm.verts[idx].select = True
   elif selection_mode == 'FACE':
       for idx in selection_indices:
           bm.faces[idx].select = True
   ```

2. **Calculer bounding box de la sélection:**
   ```python
   selected_verts = [v for v in bm.verts if v.select]
   coords = [obj.matrix_world @ v.co for v in selected_verts]

   min_x = min(c.x for c in coords)
   max_x = max(c.x for c in coords)
   # ... idem pour y, z

   bbox_center = Vector([
       (min_x + max_x) / 2,
       (min_y + max_y) / 2,
       (min_z + max_z) / 2
   ])
   bbox_size = Vector([max_x - min_x, max_y - min_y, max_z - min_z])
   ```

3. **Framing automatique:**
   ```python
   if framing.get('auto_frame'):
       # Positionner caméra pour voir toute la sélection
       padding = framing.get('padding_percent', 10) / 100

       if framing.get('fit_mode') == 'bbox':
           # Inclure bbox entière
           camera_distance = max(bbox_size) * (1 + padding) / tan(fov/2)
       else:
           # Fit exact sur sélection
           camera_distance = calculate_optimal_distance(selected_verts, fov)

       camera.location = bbox_center + direction * camera_distance
       camera.rotation_euler = direction_to_euler(direction)
   ```

4. **Context display:**
   ```python
   if context_display.get('show_unselected'):
       opacity = context_display.get('unselected_opacity', 0.2)

       # Créer material transparent pour non-sélectionnés
       for face in bm.faces:
           if not face.select:
               # Appliquer transparence (shader nodes)
               pass

   elif context_display.get('ghost_mode'):
       # Afficher reste en wireframe fantôme
       pass
   ```

---

## Prompt 6: viewport-measurement-overlay

**Fonction à implémenter:**

```python
def viewport_measurement_overlay(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Superposer mesures précises sur screenshots.

    Args:
    - object_name (str)
    - measurements (list): Mesures manuelles
      - type: "distance", "angle", "radius", "area"
      - points: Liste de coordonnées 3D
    - auto_measurements (dict): Mesures automatiques
    - output_path (str)
    """
```

**Implémentation:**

1. **Capturer screenshot de base**

2. **Pour chaque mesure manuelle:**
   ```python
   from PIL import ImageDraw

   if measurement['type'] == 'distance':
       p1_3d, p2_3d = measurement['points']
       distance = (Vector(p2_3d) - Vector(p1_3d)).length

       # Projeter en 2D
       p1_2d = world_to_screen(p1_3d, camera, resolution)
       p2_2d = world_to_screen(p2_3d, camera, resolution)

       # Dessiner ligne
       draw.line([p1_2d, p2_2d], fill=color, width=2)

       # Label
       mid = ((p1_2d[0]+p2_2d[0])//2, (p1_2d[1]+p2_2d[1])//2)
       unit = measurement.get('unit', 'm')
       draw.text(mid, f"{distance:.2f} {unit}", fill=color)

   elif measurement['type'] == 'angle':
       # Calculer angle entre 3 points
       p1, p2, p3 = [Vector(p) for p in measurement['points']]
       v1 = p1 - p2
       v2 = p3 - p2
       angle = v1.angle(v2) * 180 / pi

       # Dessiner arc
       draw_arc(p2_2d, radius, start_angle, end_angle)
       draw.text(label_pos, f"{angle:.1f}°")
   ```

3. **Mesures automatiques:**
   ```python
   if auto_measurements.get('bbox_dimensions'):
       dims = obj.dimensions
       # Dessiner dimensions sur les arêtes du bbox
       draw_dimension_lines(bbox_edges, dims)

   if auto_measurements.get('edge_lengths'):
       for edge in obj.data.edges:
           v1, v2 = [obj.data.vertices[i].co for i in edge.vertices]
           length = (v2 - v1).length
           # Annoter chaque edge
   ```

---

## Prompt 7-9: Outils Restants (Plus Simples)

### Prompt 7: viewport-compare-matrix

Créer grille de comparaison de plusieurs états de scène.
- Utiliser viewport_screenshot_complete pour chaque état
- Composer en grille avec PIL
- Ajouter labels pour chaque état

### Prompt 8: viewport-geometry-heatmap

Créer heatmap de propriétés géométriques (courbure, étirement, etc.)
- Calculer métrique pour chaque vertex
- Appliquer vertex colors avec gradient
- Capturer avec viewport_screenshot_complete en mode SOLID

### Prompt 9: viewport-xray-section-view

Vue en coupe X-Ray.
- Utiliser bisect plane pour créer coupe
- Activer X-Ray mode
- Optionnel: Colorer l'intérieur différemment

---

## Utilities Communes à Implémenter

**Dans executor.py, ajouter ces helpers:**

```python
def world_to_screen(world_pos, camera, resolution):
    """Convertir coordonnées 3D → 2D viewport"""
    import bpy_extras
    scene = bpy.context.scene
    co_2d = bpy_extras.object_utils.world_to_camera_view(
        scene, camera, mathutils.Vector(world_pos)
    )
    x = int(co_2d.x * resolution[0])
    y = int((1 - co_2d.y) * resolution[1])
    return (x, y)

def setup_camera_for_view(view_name, target_object):
    """Positionner caméra selon vue (FRONT, RIGHT, etc.)"""
    camera = bpy.data.cameras.new("TempCamera")
    camera_obj = bpy.data.objects.new("TempCameraObj", camera)
    bpy.context.scene.collection.objects.link(camera_obj)

    # Positions prédéfinies
    positions = {
        'FRONT': (0, -10, 0),
        'RIGHT': (10, 0, 0),
        'TOP': (0, 0, 10),
        'ISO_FRONT_RIGHT': (7, -7, 7),
    }

    camera_obj.location = positions.get(view_name, (0, -10, 0))
    # Point vers target
    direction = target_object.location - camera_obj.location
    camera_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    return camera_obj

def capture_offscreen(camera, resolution, scene):
    """Capturer screenshot offscreen (headless-safe)"""
    import gpu
    from gpu_extras.presets import draw_texture_2d

    width, height = resolution
    offscreen = gpu.types.GPUOffScreen(width, height)

    with offscreen.bind():
        # Render
        bpy.ops.render.opengl(write_still=False)

        # Lire pixels
        buffer = gpu.state.active_framebuffer_get()
        pixels = buffer.read_color(0, 0, width, height, 4, 0, 'UBYTE')

    # Convertir en PIL Image
    from PIL import Image
    import numpy as np
    pixels = np.frombuffer(pixels.to_list(), dtype=np.uint8)
    pixels = pixels.reshape((height, width, 4))
    pixels = np.flipud(pixels)  # Flip vertical
    img = Image.fromarray(pixels, 'RGBA')

    return img
```

---

## Ordre d'Implémentation Recommandé

1. **viewport-screenshot-complete** (fondation)
2. **viewport-annotate-markup** (annotations simples)
3. **viewport-diff-comparison** (utilise #1)
4. **validate-operation-visual** (utilise #1 + #3)
5. **viewport-selection-isolate-capture** (utilise #1)
6. **viewport-measurement-overlay** (utilise #1)
7. **viewport-compare-matrix** (utilise #1)
8. **viewport-geometry-heatmap** (utilise #1)
9. **viewport-xray-section-view** (utilise #1)

---

## Tests à Ajouter

Pour chaque outil, ajouter test dans `tests/test_vision_integration.py`:

```python
def test_viewport_screenshot_complete():
    # Créer cube
    result = call_tool('blender-primitive-cube', {'name': 'TestCube'})
    assert result['ok']

    # Capturer screenshots
    result = call_tool('athena-viewport-screenshot-complete', {
        'object_name': 'TestCube',
        'views': ['FRONT', 'RIGHT'],
        'output': {'format': 'separate'}
    })

    assert result['ok']
    assert 'screenshots' in result['result']
    assert len(result['result']['screenshots']) == 2

    # Vérifier fichiers existent
    for path in result['result']['screenshots']:
        assert os.path.exists(path)
```

---

## Notes Importantes

1. **Dépendances:** Ajouter Pillow au requirements.txt
   ```
   pip install Pillow
   ```

2. **Chemins temporaires:** Utiliser tempfile.mkdtemp() si output_path non fourni

3. **Cleanup:** Supprimer caméras/objets temporaires après capture

4. **Contexte Blender:**
   - En mode headless: Utiliser offscreen rendering
   - En mode UI: Peut utiliser bpy.ops.render.opengl
   - Vérifier `bpy.app.background` pour détecter le mode

5. **Performance:**
   - Mettre en cache les caméras temporaires si possible
   - Réutiliser offscreen buffers
   - Optimiser résolution par défaut (1920x1080 peut être lourd)

---

## Ressources

- Blender API: https://docs.blender.org/api/current/
- bpy_extras: https://docs.blender.org/api/current/bpy_extras.html
- GPU module: https://docs.blender.org/api/current/gpu.html
- Pillow docs: https://pillow.readthedocs.io/

---

**Bon courage Codex! 🚀**
