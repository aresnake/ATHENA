# ATHENA VISION TOOLS - SPECIFICATIONS COMPLETES 0-ERROR
Baseline: Blender 5.0.0 feasibility tests (all passed).

- Date: 2025-01-20
- Status: VALIDATED - Ready for implementation
- Tests: PASSED

---

## TIER S - CRITICAL PRIORITY

### 1. viewport-diff-comparison (5/5)

**Fonction:** Capture comparative avant/apres avec diff visuel automatique

**Tests de faisabilite:**
- PASS Diff geometrique: tracking vertices/edges/faces
- PASS Manipulation images: overlays/compositing
- PASS Calcul distances: mathutils.Vector
- PASS Render multiple views: viewport control

**Parametres:**
```python
{
  # Etats de reference
  "before_snapshot": dict,  # Output de diag-scene-snapshot
  "before_screenshot": str,  # Path image etat avant
  
  # Operation (optionnel, pour tracabilite)
  "operation_description": str,  # Description modifications
  
  # Configuration diff
  "diff_mode": str,  # ["overlay", "side_by_side", "split_view", "highlight_only"]
  "highlight_color": [float, float, float, float],  # RGBA pour zones modifiees
  
  # Geometrie diff
  "geometry_diff": {
    "track_vertices": bool,  # True par defaut
    "track_edges": bool,
    "track_faces": bool,
    "threshold": float,  # Distance minimale pour considerer changement (default: 0.0001)
    "show_vectors": bool,  # Afficher vecteurs deplacement
    "vector_scale": float  # Echelle visuelle vecteurs (default: 1.0)
  },
  
  # Mesures automatiques
  "measurements": {
    "show_distances": bool,  # Distances deplacements
    "show_volume_change": bool,  # Changement volume
    "show_area_change": bool,  # Changement surface
    "show_stats_overlay": bool  # Overlay statistiques
  },
  
  # Vues a comparer
  "views": [str],  # ["FRONT", "RIGHT", "TOP", "ISO_FRONT_RIGHT"] default
  "resolution": [int, int],  # [1920, 1080] default
  
  # Output
  "output_format": str,  # ["composite_grid", "separate_files", "annotated_only"]
  "output_path": str  # Base path pour sauvegardes
}
```

**Output:**
```python
{
  "status": "success",
  "comparison_images": {
    "composite": "/path/to/composite_diff.png",  # Vue combinee
    "before": "/path/to/before.png",
    "after": "/path/to/after.png",
    "diff_overlay": "/path/to/diff_highlighted.png",
    "per_view": {
      "FRONT": "/path/to/front_diff.png",
      "RIGHT": "/path/to/right_diff.png",
      # ...
    }
  },
  "geometry_delta": {
    "vertices": {
      "added": int,
      "removed": int,
      "moved": int,
      "moved_indices": [int],  # Indices vertices deplaces
      "max_displacement": float,
      "avg_displacement": float,
      "displacement_vectors": [
        {"index": int, "delta": [x, y, z], "distance": float}
      ]
    },
    "edges": {"added": int, "removed": int},
    "faces": {"added": int, "removed": int}
  },
  "measurements": {
    "volume_before": float,
    "volume_after": float,
    "volume_change_percent": float,
    "surface_area_before": float,
    "surface_area_after": float,
    "bbox_change": {
      "before": {"min": [x,y,z], "max": [x,y,z]},
      "after": {"min": [x,y,z], "max": [x,y,z]}
    }
  },
  "visual_report": str  # Rapport textuel changements
}
```

**Implementation (pseudo):**
```python
def viewport_diff_comparison(**params):
    # 1. Capturer etat actuel
    after_snapshot = capture_scene_state()
    after_screenshots = capture_multi_view(params["views"])
    
    # 2. Comparer geometrie
    geom_diff = compare_geometry(
        params["before_snapshot"],
        after_snapshot,
        params["geometry_diff"]
    )
    
    # 3. Generer overlays visuels
    diff_images = []
    for view in params["views"]:
        before_img = load_image(params["before_screenshot"][view])
        after_img = after_screenshots[view]
        
        # Highlight zones modifiees
        diff_img = create_diff_overlay(
            before_img,
            after_img,
            geom_diff,
            params["highlight_color"]
        )
        
        # Ajouter annotations mesures
        if params["measurements"]["show_distances"]:
            diff_img = overlay_measurements(
                diff_img,
                geom_diff["vertices"]["displacement_vectors"]
            )
        
        diff_images.append(diff_img)
    
    # 4. Composer vue finale
    composite = compose_comparison(
        diff_images,
        params["diff_mode"],
        params["output_format"]
    )
    
    # 5. Sauvegarder et retourner resultats
    return save_and_return_results(composite, geom_diff)
```

**Dependencies (Blender API):**
- `bpy.data.objects` - acces geometrie
- `mathutils.Vector` - calculs distances
- `bpy.data.images` - manipulation images
- `bpy.ops.render.opengl` - captures viewport
- `bmesh` - analyse mesh detaillee

---

### 2. viewport-annotate-markup (5/5)

**Fonction:** Systemes annotations/markup automatiques et manuels sur screenshots

**Tests de faisabilite:**
- PASS GPU shaders: overlays custom
- PASS Text objects: annotations textuelles
- PASS Draw callbacks: SpaceView3D
- PASS Image compositing: fusion overlays

**Parametres:**
```python
{
  # Source
  "object_name": str,
  "screenshot_base": str,  # Path image a annoter (optionnel)
  
  # Annotations manuelles
  "annotations": [
    {
      "type": str,  # ["arrow", "circle", "box", "text", "line", "highlight", "measurement"]
      "position": [float, float, float],  # Position 3D
      "screen_position": [int, int],  # Position 2D (si viewport space)
      "content": str,  # Texte annotation
      "color": [float, float, float, float],  # RGBA
      "size": float,  # Taille marker/text
      "thickness": float,  # Epaisseur ligne (pour arrow/line/box)
      "style": str  # ["solid", "dashed", "dotted"]
    }
  ],
  
  # Annotations automatiques
  "auto_annotate": {
    "enabled": bool,
    "detect_issues": bool,  # Auto-highlight problemes topologie
    "issues_to_detect": [str],  # ["non_manifold", "ngons", "overlapping", "degenerate"]
    "label_elements": bool,  # Labelliser vertices/edges/faces importants
    "show_normals": bool,  # Fleches normales
    "show_measurements": bool  # Distances/angles auto
  },
  
  # Configuration visuelle
  "visual_style": {
    "font_size": int,  # Taille texte (default: 16)
    "font_family": str,  # "sans-serif", "monospace"
    "background_opacity": float,  # Opacite fond texte (0.0-1.0)
    "arrow_head_size": float,
    "marker_size": float
  },
  
  # Vues
  "views": [str],  # Vues a annoter
  "resolution": [int, int],
  
  # Output
  "output_path": str,
  "return_annotation_data": bool  # Retourner donnees pour edition future
}
```

**Output:**
```python
{
  "status": "success",
  "annotated_images": {
    "FRONT": "/path/to/annotated_front.png",
    "RIGHT": "/path/to/annotated_right.png",
    # ...
  },
  "annotation_data": [
    {
      "id": str,  # UUID annotation
      "type": str,
      "position": [x, y, z],
      "screen_coords": {"FRONT": [x, y], "RIGHT": [x, y]},
      "content": str,
      "auto_generated": bool,
      "issue_type": str  # Si auto-detect
    }
  ],
  "auto_detected_issues": {
    "non_manifold_edges": [int],  # Indices
    "ngons": [int],
    "overlapping_faces": [int],
    "total_issues": int
  },
  "report": str  # Description annotations
}
```

**Implementation (pseudo):**
```python
def viewport_annotate_markup(**params):
    # 1. Capturer ou charger image base
    if params.get("screenshot_base"):
        base_images = load_existing_screenshots(params["screenshot_base"])
    else:
        base_images = capture_multi_view(params["views"])
    
    # 2. Detection automatique problemes
    auto_annotations = []
    if params["auto_annotate"]["enabled"]:
        issues = detect_topology_issues(
            params["object_name"],
            params["auto_annotate"]["issues_to_detect"]
        )
        
        auto_annotations = generate_auto_annotations(
            issues,
            params["visual_style"]
        )
    
    # 3. Combiner annotations manuelles + auto
    all_annotations = params["annotations"] + auto_annotations
    
    # 4. Rendu annotations sur chaque vue
    annotated_images = {}
    for view in params["views"]:
        img = base_images[view]
        
        # Projet annotations 3D -> 2D pour cette vue
        view_annotations = project_annotations_to_view(
            all_annotations,
            view
        )
        
        # Draw annotations
        img_annotated = draw_annotations_on_image(
            img,
            view_annotations,
            params["visual_style"]
        )
        
        annotated_images[view] = img_annotated
    
    # 5. Sauvegarder
    return save_annotated_results(annotated_images, all_annotations)
```

**Dependencies (Blender API):**
- `gpu.shader.from_builtin` - rendering annotations
- `gpu_extras.batch.batch_for_shader` - geometry batch
- `bpy.types.SpaceView3D.draw_handler_add` - callbacks
- `bpy.data.images` - compositing
- `bmesh` - detection problemes topologie

---

### 3. validate-operation-visual (5/5)

**Fonction:** Pipeline validation complete avec preuves visuelles

**Tests de faisabilite:**
- PASS Orchestration tools: composition multi-outils
- PASS Etat capture: snapshots + screenshots
- PASS Validation: topology checks
- PASS Rapport: generation automatique

**Parametres:**
```python
{
  # Operation a valider
  "operation": {
    "tool_name": str,  # Tool ATHENA a executer
    "parameters": dict,  # Params du tool
    "description": str  # Description action
  },
  
  # Configuration validation
  "validation": {
    "geometry_checks": bool,  # Validation geometrique (default: True)
    "topology_checks": bool,  # Validation topologie (default: True)
    "visual_diff": bool,  # Diff visuel (default: True)
    "expected_changes": dict,  # Changements attendus (optionnel)
  },
  
  # Expectations (optionnel)
  "expectations": {
    "vertices_delta": {"min": int, "max": int},
    "should_be_manifold": bool,
    "should_be_watertight": bool,
    "max_ngons": int,
    "volume_change_percent": {"min": float, "max": float}
  },
  
  # Capture configuration
  "capture_config": {
    "views": [str],
    "resolution": [int, int],
    "shading_mode": str,  # "SOLID", "WIREFRAME"
    "overlays": dict
  },
  
  # Output
  "output_path": str,
  "generate_report": bool,  # Rapport HTML/MD (default: True)
  "fail_on_unexpected": bool  # Fail si changements inattendus
}
```

**Output:**
```python
{
  "status": str,  # "success", "warning", "failed"
  "validation_passed": bool,
  
  # Etats
  "state_before": {
    "snapshot": dict,
    "screenshots": dict,
    "timestamp": str
  },
  "state_after": {
    "snapshot": dict,
    "screenshots": dict,
    "timestamp": str
  },
  
  # Diff
  "geometry_diff": dict,  # From viewport-diff-comparison
  "visual_diff": {
    "comparison_images": dict,
    "highlighted_changes": str
  },
  
  # Validations
  "topology_validation": {
    "manifold": bool,
    "watertight": bool,
    "ngons_count": int,
    "issues": [str]
  },
  "expectations_met": {
    "vertices_delta": {"expected": str, "actual": int, "passed": bool},
    "manifold": {"expected": bool, "actual": bool, "passed": bool},
    # ...
  },
  
  # Rapport
  "report": {
    "html_path": str,
    "markdown_path": str,
    "summary": str
  },
  
  # Preuves
  "evidence": {
    "before_images": [str],
    "after_images": [str],
    "diff_images": [str],
    "annotated_issues": [str]
  }
}
```

**Workflow (pseudo):**
```python
def validate_operation_visual(**params):
    # ETAPE 1: Capture etat AVANT
    print("[1/7] Capture etat initial...")
    state_before = {
        "snapshot": diag_scene_snapshot(),
        "screenshots": viewport_screenshot_complete(
            **params["capture_config"]
        ),
        "timestamp": datetime.now().isoformat()
    }
    
    # ETAPE 2: Execution operation
    print("[2/7] Execution operation...")
    operation_result = execute_tool(
        params["operation"]["tool_name"],
        params["operation"]["parameters"]
    )
    
    if not operation_result["ok"]:
        return {
            "status": "failed",
            "error": "Operation execution failed",
            "details": operation_result
        }
    
    # ETAPE 3: Capture etat APRES
    print("[3/7] Capture etat final...")
    state_after = {
        "snapshot": diag_scene_snapshot(),
        "screenshots": viewport_screenshot_complete(
            **params["capture_config"]
        ),
        "timestamp": datetime.now().isoformat()
    }
    
    # ETAPE 4: Generation diff visuel
    print("[4/7] Generation diff visuel...")
    visual_diff = viewport_diff_comparison(
        before_snapshot=state_before["snapshot"],
        before_screenshot=state_before["screenshots"],
        views=params["capture_config"]["views"],
        geometry_diff={"track_vertices": True, "track_edges": True, "track_faces": True}
    )
    
    # ETAPE 5: Validation topologie
    print("[5/7] Validation topologie...")
    topology_result = topology_validate_complete(
        object_name=params["operation"]["parameters"].get("object_name"),
        checks=["manifold", "watertight", "ngons", "loose"]
    )
    
    # ETAPE 6: Verification expectations
    print("[6/7] Verification expectations...")
    expectations_met = {}
    if params.get("expectations"):
        expectations_met = check_expectations(
            params["expectations"],
            visual_diff["geometry_delta"],
            topology_result
        )
    
    # ETAPE 7: Generation rapport
    print("[7/7] Generation rapport...")
    report = generate_validation_report(
        operation=params["operation"],
        state_before=state_before,
        state_after=state_after,
        visual_diff=visual_diff,
        topology=topology_result,
        expectations=expectations_met,
        output_path=params["output_path"]
    )
    
    # Determination status final
    validation_passed = (
        operation_result["ok"] and
        topology_result["status"] == "OK" and
        all(e["passed"] for e in expectations_met.values())
    )
    
    return {
        "status": "success" if validation_passed else "warning",
        "validation_passed": validation_passed,
        "state_before": state_before,
        "state_after": state_after,
        "geometry_diff": visual_diff["geometry_delta"],
        "visual_diff": visual_diff,
        "topology_validation": topology_result,
        "expectations_met": expectations_met,
        "report": report,
        "evidence": compile_evidence_paths(
            state_before, state_after, visual_diff
        )
    }
```

**Dependencies:**
- `diag-scene-snapshot` - etat scene
- `viewport-screenshot-complete` - captures
- `viewport-diff-comparison` - diff visuel
- `topology-validate-complete` - validation topo
- Tool cible a valider

---

## TIER A - HIGH PRIORITY

### 4. viewport-selection-isolate-capture

**Fonction:** Capture avec auto-zoom sur selection

**Parametres:**
```python
{
  "object_name": str,
  "selection_mode": str,  # "VERT", "EDGE", "FACE", "OBJECT"
  "selection_indices": [int],  # Indices elements (optionnel si tout objet)
  
  "framing": {
    "auto_frame": bool,  # Cadrage auto (default: True)
    "padding_percent": float,  # Marge autour selection (default: 10.0)
    "fit_mode": str  # "bbox", "selection_only"
  },
  
  "context_display": {
    "show_unselected": bool,  # Afficher reste en transparence
    "unselected_opacity": float,  # 0.0-1.0 (default: 0.2)
    "ghost_mode": bool  # Wireframe pour contexte
  },
  
  "views": [str],
  "resolution": [int, int],
  "shading_mode": str,
  "output_path": str
}
```

**Output:**
```python
{
  "status": "success",
  "focused_screenshots": {
    "FRONT": "/path/front_focused.png",
    # ...
  },
  "selection_bounds": {
    "min": [x, y, z],
    "max": [x, y, z],
    "center": [x, y, z],
    "dimensions": [x, y, z]
  },
  "camera_positions": {
    "FRONT": {"location": [x,y,z], "rotation": [x,y,z]},
    # ...
  }
}
```

**Implementation (pseudo):**
```python
def viewport_selection_isolate_capture(**params):
    obj = bpy.data.objects[params["object_name"]]
    
    # 1. Calculer bounds selection
    if params.get("selection_indices"):
        selection_bounds = calculate_selection_bounds(
            obj,
            params["selection_mode"],
            params["selection_indices"]
        )
    else:
        selection_bounds = obj.bound_box
    
    # 2. Pour chaque vue
    screenshots = {}
    camera_positions = {}
    
    for view in params["views"]:
        # Positionner camera pour framing optimal
        cam_pos = calculate_optimal_camera_position(
            selection_bounds,
            view,
            params["framing"]["padding_percent"]
        )
        
        # Setup viewport
        setup_viewport_for_view(view, cam_pos)
        
        # Appliquer context display si demande
        if params["context_display"]["show_unselected"]:
            apply_context_display(
                obj,
                params["selection_indices"],
                params["context_display"]
            )
        
        # Capture
        screenshot = render_viewport(params["resolution"])
        screenshots[view] = screenshot
        camera_positions[view] = cam_pos
    
    return {
        "status": "success",
        "focused_screenshots": screenshots,
        "selection_bounds": selection_bounds,
        "camera_positions": camera_positions
    }
```

---

### 5. viewport-measurement-overlay

**Fonction:** Overlays mesures precises sur screenshots

**Parametres:**
```python
{
  "object_name": str,
  "screenshot_base": str,  # Path image base (optionnel)
  
  "measurements": [
    {
      "type": str,  # "distance", "angle", "radius", "area", "perimeter"
      "points": [[x,y,z], ...],  # Points 3D definissant mesure
      "label": str,  # Label custom (optionnel)
      "precision": int,  # Decimales (default: 2)
      "unit": str,  # "m", "cm", "mm", "auto"
      "color": [r,g,b,a]
    }
  ],
  
  "auto_measurements": {
    "enabled": bool,
    "bbox_dimensions": bool,  # Mesurer bbox
    "edge_lengths": bool,  # Longueurs edges selectionnees
    "face_areas": bool,
    "angles_between_edges": bool
  },
  
  "visual_style": {
    "line_thickness": float,
    "font_size": int,
    "leader_lines": bool,  # Lignes pointeur vers mesure
    "background_box": bool  # Fond pour labels
  },
  
  "views": [str],
  "output_path": str
}
```

**Output:**
```python
{
  "status": "success",
  "measured_screenshots": {
    "FRONT": "/path/measured_front.png"
  },
  "measurement_data": [
    {
      "type": "distance",
      "value": float,
      "unit": str,
      "points": [[x,y,z], [x,y,z]],
      "label": str
    }
  ],
  "report": str
}
```

---

### 6. viewport-compare-matrix

**Fonction:** Matrice comparaison multi-etats

**Parametres:**
```python
{
  "states": [
    {
      "label": str,
      "snapshot": dict,  # State snapshot
      "description": str
    }
  ],
  
  "layout": str,  # "grid", "carousel", "overlay_sequence"
  "views_per_state": [str],  # Vues a capturer par etat
  
  "sync_settings": {
    "sync_camera": bool,  # Meme position camera
    "sync_shading": bool,
    "sync_overlays": bool
  },
  
  "highlight_differences": bool,
  "annotate_changes": bool,
  
  "resolution": [int, int],
  "output_path": str
}
```

**Output:**
```python
{
  "status": "success",
  "comparison_matrix": "/path/matrix_comparison.png",
  "individual_states": {
    "state_0": {
      "FRONT": "/path/state0_front.png"
    }
  },
  "difference_report": {
    "state_pairs": [
      {
        "from_state": 0,
        "to_state": 1,
        "geometry_changes": dict,
        "visual_similarity": float  # 0.0-1.0
      }
    ]
  }
}
```

---

### 7. viewport-screenshot-complete -> extensions

**Ajouts au tool existant:**
```python
# Nouveaux parametres a ajouter:
{
  # ... parametres existants ...
  
  # NOUVEAUX:
  "auto_frame_selection": bool,  # Auto-frame sur selection
  "highlight_selection": {
    "enabled": bool,
    "color": [r,g,b,a],
    "thickness": float
  },
  
  "measurement_overlays": [  # Comme viewport-measurement-overlay
    {"type": "distance", "points": [...], ...}
  ],
  
  "annotation_overlays": [  # Comme viewport-annotate-markup
    {"type": "text", "position": [...], ...}
  ],
  
  "diff_reference": {
    "enabled": bool,
    "reference_image": str,  # Path pour overlay comparaison
    "blend_mode": str  # "difference", "overlay"
  },
  
  "quality_preset": str,  # "fast", "balanced", "high"
  
  "auto_optimize_views": bool,  # Detection auto vues pertinentes
  
  "edge_display": {
    "mode": str,  # "none", "sharp_only", "all", "seams", "creases"
    "thickness": float,
    "color": [r,g,b,a]
  },
  
  "matcap_override": str,  # Path to custom matcap
  
  "post_processing": {
    "sharpen": float,  # 0.0-1.0
    "contrast": float,
    "brightness": float
  }
}
```

---

## TIER B - IMPORTANT

### 8. viewport-geometry-heatmap

**Fonction:** Visualisation proprietes geometriques via heatmap

**Tests faisabilite:**
- PASS Calcul proprietes: bmesh analysis
- PASS Vertex colors: bpy.data.meshes[].vertex_colors
- PASS Gradient colors: mathutils interpolation

**Parametres:**
```python
{
  "object_name": str,
  
  "property": str,  # "curvature", "stretch", "distortion", "thickness", 
                    # "slope", "edge_angle", "face_area"
  
  "color_ramp": {
    "min_color": [r,g,b,a],
    "max_color": [r,g,b,a],
    "mid_color": [r,g,b,a],  # Optionnel
    "interpolation": str  # "linear", "ease", "sharp"
  },
  
  "value_range": {
    "auto": bool,  # Auto-detect min/max
    "min": float,
    "max": float,
    "clamp": bool  # Clamp valeurs hors range
  },
  
  "threshold_highlight": {
    "enabled": bool,
    "value": float,
    "highlight_mode": str  # "above", "below", "outside_range"
  },
  
  "legend": {
    "show": bool,
    "position": str,  # "top_right", "bottom_left", etc.
    "format": str  # Format nombres
  },
  
  "views": [str],
  "resolution": [int, int],
  "output_path": str
}
```

**Output:**
```python
{
  "status": "success",
  "heatmap_screenshots": {
    "FRONT": "/path/heatmap_front.png"
  },
  "statistics": {
    "property": str,
    "min_value": float,
    "max_value": float,
    "mean": float,
    "std_dev": float,
    "histogram": {
      "bins": [float],
      "counts": [int]
    }
  },
  "highlighted_elements": [int],  # Si threshold active
  "legend_image": "/path/legend.png"
}
```

**Implementation (pseudo):**
```python
def viewport_geometry_heatmap(**params):
    obj = bpy.data.objects[params["object_name"]]
    mesh = obj.data
    
    # 1. Calculer propriete pour chaque vertex/face
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    if params["property"] == "curvature":
        values = calculate_vertex_curvature(bm)
    elif params["property"] == "stretch":
        values = calculate_uv_stretch(bm)
    elif params["property"] == "face_area":
        values = [f.calc_area() for f in bm.faces]
    # ... autres proprietes
    
    # 2. Normaliser et mapper couleurs
    value_range = params["value_range"]
    if value_range["auto"]:
        vmin, vmax = min(values), max(values)
    else:
        vmin, vmax = value_range["min"], value_range["max"]
    
    colors = map_values_to_colors(
        values,
        vmin,
        vmax,
        params["color_ramp"]
    )
    
    # 3. Appliquer vertex colors
    if not mesh.vertex_colors:
        mesh.vertex_colors.new()
    vcol = mesh.vertex_colors.active
    
    for poly in mesh.polygons:
        for loop_idx in poly.loop_indices:
            vert_idx = mesh.loops[loop_idx].vertex_index
            vcol.data[loop_idx].color = colors[vert_idx]
    
    # 4. Configurer viewport pour vertex colors
    areas = [a for a in bpy.context.screen.areas if a.type == 'VIEW_3D']
    if areas:
        space = areas[0].spaces.active
        space.shading.type = 'SOLID'
        space.shading.color_type = 'VERTEX'
    
    # 5. Capturer screenshots
    screenshots = {}
    for view in params["views"]:
        setup_viewport_for_view(view)
        screenshot = render_viewport(params["resolution"])
        
        # Overlay legend si demande
        if params["legend"]["show"]:
            screenshot = overlay_legend(
                screenshot,
                params["color_ramp"],
                vmin,
                vmax,
                params["legend"]
            )
        
        screenshots[view] = screenshot
    
    # 6. Statistiques
    stats = {
        "property": params["property"],
        "min_value": vmin,
        "max_value": vmax,
        "mean": sum(values) / len(values),
        "std_dev": calculate_std_dev(values)
    }
    
    bm.free()
    
    return {
        "status": "success",
        "heatmap_screenshots": screenshots,
        "statistics": stats
    }
```

---

### 9. viewport-context-aware-capture

**Fonction:** Capture intelligente selon contexte

**Parametres:**
```python
{
  "object_name": str,
  
  "intelligence": {
    "auto_select_views": bool,  # Choisit vues pertinentes selon geometrie
    "auto_select_overlays": bool,  # Active overlays utiles
    "auto_detect_issues": bool,  # Scan problemes topo
    "focus_mode": str  # "full_object", "selection", "problem_areas", "details"
  },
  
  "quality_preset": str,  # "draft", "preview", "final"
  
  "context_hints": {
    "object_type": str,  # "mechanical", "organic", "architectural", "character"
    "modeling_stage": str,  # "blocking", "detailing", "finalizing"
    "purpose": str  # "review", "presentation", "documentation", "debugging"
  },
  
  "output_path": str
}
```

**Output:**
```python
{
  "status": "success",
  "captures": {
    "primary_view": "/path/main_capture.png",
    "detail_views": ["/path/detail1.png", ...],
    "problem_highlights": ["/path/issue1.png", ...]
  },
  "context_analysis": {
    "detected_type": str,
    "complexity_score": float,
    "recommended_views": [str],
    "detected_issues": [str]
  },
  "decisions": {
    "views_chosen": [str],
    "overlays_enabled": [str],
    "focus_areas": [str],
    "reasoning": str
  }
}
```

---

### 10. viewport-xray-section-view

**Fonction:** Vues en coupe et transparence

**Parametres:**
```python
{
  "object_name": str,
  
  "section": {
    "enabled": bool,
    "plane": str,  # "X", "Y", "Z", "CUSTOM"
    "custom_normal": [x,y,z],  # Si CUSTOM
    "offset": float,  # Position plan coupe
    "show_cut_surface": bool,
    "fill_cut": bool
  },
  
  "xray": {
    "enabled": bool,
    "opacity": float,  # 0.0-1.0
    "mode": str  # "uniform", "depth_based"
  },
  
  "interior_display": {
    "show": bool,
    "different_color": bool,
    "interior_color": [r,g,b,a]
  },
  
  "views": [str],
  "resolution": [int, int],
  "output_path": str
}
```

**Output:**
```python
{
  "status": "success",
  "section_screenshots": {
    "FRONT": "/path/section_front.png"
  },
  "section_data": {
    "plane_position": [x,y,z],
    "plane_normal": [x,y,z],
    "cut_vertices": int,
    "interior_volume": float
  }
}
```

---

## IMPLEMENTATION GUIDELINES

### Architecture generale
```
athena_vision_tools/
|-- core/
|   |-- viewport_controller.py    # Controle viewport/camera
|   |-- image_processor.py        # Manipulation images
|   |-- geometry_analyzer.py      # Analyse geometrique
|   `-- compositor.py             # Composition multi-images
|-- tools/
|   |-- diff_comparison.py        # viewport-diff-comparison
|   |-- annotate_markup.py        # viewport-annotate-markup
|   |-- validate_visual.py        # validate-operation-visual
|   |-- isolate_capture.py        # viewport-selection-isolate-capture
|   |-- measurement_overlay.py    # viewport-measurement-overlay
|   |-- compare_matrix.py         # viewport-compare-matrix
|   |-- geometry_heatmap.py       # viewport-geometry-heatmap
|   |-- context_capture.py        # viewport-context-aware-capture
|   `-- xray_section.py           # viewport-xray-section-view
|-- utils/
|   |-- math_helpers.py
|   |-- color_utils.py
|   `-- file_handlers.py
`-- tests/
    `-- test_all_vision_tools.py
```

### Standards 0-error

1. **Validation entrees:**
   - Verifier existence objets avant operation
   - Valider ranges numeriques
   - Checks types stricts

2. **Gestion erreurs:**
   ```python
   try:
       # Operation
   except SpecificError as e:
       return {
           "ok": false,
           "error": {
               "message": str(e),
               "code": "error_code",
               "recoverable": bool
           }
       }
   ```

3. **Cleanup systematique:**
   - Restore viewport state apres captures
   - Liberer bmesh instances
   - Remove temporary objects

4. **Documentation inline:**
   - Docstrings complets
   - Type hints
   - Exemples usage

5. **Tests unitaires:**
   - Test chaque tool isole
   - Test workflows composes
   - Test edge cases

---

## ROADMAP IMPLEMENTATION

### Phase 1: TIER S (Priorite absolue)
- Semaine 1-2: `viewport-diff-comparison`
- Semaine 3: `viewport-annotate-markup`
- Semaine 4-5: `validate-operation-visual`

### Phase 2: TIER A
- Semaine 6: `viewport-selection-isolate-capture`
- Semaine 7: `viewport-measurement-overlay`
- Semaine 8: `viewport-compare-matrix`
- Semaine 9: Extensions `viewport-screenshot-complete`

### Phase 3: TIER B
- Semaine 10: `viewport-geometry-heatmap`
- Semaine 11: `viewport-context-aware-capture`
- Semaine 12: `viewport-xray-section-view`

---

## VALIDATION FINALE

**Tests de faisabilite:** PASSED
- Diff geometrique tracking
- Image manipulation
- GPU shaders/overlays
- Viewport control
- Mesh analysis
- Annotations systems

**APIs Blender validees:**
- `bpy.data.images` - manipulation images (validated)
- `gpu` / `gpu_extras` - rendering custom (validated)
- `mathutils` - calculs geometriques (validated)
- `bmesh` - analyse mesh (validated)
- `bpy.ops.render.opengl` - captures viewport (validated)
- `SpaceView3D` - controle viewport (validated)

**Pret pour implementation:** OUI

Document approuve pour developpement ATHENA MCP Server (ARES - Agent chef BLADE).
