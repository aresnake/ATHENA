# ATHENA MCP – TOOL REQUEST SPEC V2 (CLEAN)

Source: consolidated from `TOOL_REQUEST_SPEC_V2.md` (batch P0). This is the canonical, cleaned version to drive implementation.

Status: specs provided, not yet implemented for this batch.

---

## Batch P0 – Transformations avancées (7/7)

### blender-object-scale
- Description: Scale object with independent X/Y/Z.
- Mode: OBJECT. No selection required (uses `name`).
- Schema:
```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "sx": {"type": "number", "minimum": 0.001, "maximum": 1000},
    "sy": {"type": "number", "minimum": 0.001, "maximum": 1000},
    "sz": {"type": "number", "minimum": 0.001, "maximum": 1000},
    "uniform": {"type": "boolean", "default": false}
  },
  "required": ["name", "sx"],
  "additionalProperties": false
}
```
- Output: `{ name, scale:[x,y,z], dimensions:[x,y,z] }`
- Guards: object exists + MESH, clamp 0.001–1000, if uniform=true then sy/sz from sx.

### blender-object-apply-transform
- Description: Apply location/rotation/scale to data.
- Mode: OBJECT.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "location": {"type": "boolean", "default": false},
    "rotation": {"type": "boolean", "default": false},
    "scale": {"type": "boolean", "default": false},
    "properties": {"type": "boolean", "default": false}
  },
  "required": ["name"],
  "additionalProperties": false
}
```
- Output: `{ name, applied:{location,rotation,scale}, final_transform:{location,rotation,scale} }`
- Guards: object exists (MESH/CURVE/SURFACE), at least one flag true, OBJECT mode.

### blender-object-origin-set
- Description: Set origin (geometry/cursor/center/geometry_origin).
- Mode: OBJECT.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "type": {"type": "string", "enum": ["GEOMETRY","CURSOR","CENTER_MASS","CENTER_VOLUME","GEOMETRY_ORIGIN"]},
    "center": {"type": "string", "enum": ["MEDIAN","BOUNDS"], "default": "MEDIAN"}
  },
  "required": ["name", "type"],
  "additionalProperties": false
}
```
- Output: `{ name, origin_type, new_location, center }`
- Guards: object exists (MESH/CURVE/SURFACE), OBJECT mode, cursor valid for CURSOR.

### blender-object-parent
- Description: Set/clear parent-child relationship.
- Mode: OBJECT.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "child_name": {"type": "string"},
    "parent_name": {"anyOf": [{"type": "string"},{"type": "null"}]},
    "keep_transform": {"type": "boolean", "default": true},
    "type": {"type": "string", "enum": ["OBJECT","BONE","VERTEX","VERTEX_TRI"], "default": "OBJECT"}
  },
  "required": ["child_name"],
  "additionalProperties": false
}
```
- Output: `{ child, parent, keep_transform, relationship }`
- Guards: child/parent exist, child != parent, OBJECT mode. parent_name=null → clear.

### blender-object-clear-transform
- Description: Reset location/rotation/scale (and delta optionally).
- Mode: OBJECT.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "location": {"type": "boolean", "default": false},
    "rotation": {"type": "boolean", "default": false},
    "scale": {"type": "boolean", "default": false},
    "delta": {"type": "boolean", "default": false}
  },
  "required": ["name"],
  "additionalProperties": false
}
```
- Output: `{ name, cleared:{location,rotation,scale,delta}, final_transform:{location,rotation,scale} }`
- Guards: object exists, at least one flag true, OBJECT mode.

### blender-mesh-rotate-selection
- Description: Rotate selected verts around axis/pivot (EDIT, bmesh).
- Mode: EDIT, selection required (verts).
- Schema:
```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "angle": {"type": "number", "minimum": -360, "maximum": 360},
    "axis": {"type": "string", "enum": ["X","Y","Z"]},
    "pivot": {"anyOf":[{"type":"array","items":{"type":"number"},"minItems":3,"maxItems":3},{"type":"null"}], "default": null},
    "euler_xyz": {"anyOf":[{"type":"array","items":{"type":"number"},"minItems":3,"maxItems":3},{"type":"null"}], "default": null}
  },
  "required": ["name"],
  "additionalProperties": false
}
```
- Output: `{ name, rotated_verts, angle, axis, pivot, euler_xyz }`
- Guards: object exists MESH, selection non-empty, angle clamp, if euler_xyz given override angle+axis, pivot default = selection center.

### blender-object-duplicate
- Description: Duplicate object with linked/offset/collection.
- Mode: OBJECT.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "new_name": {"anyOf":[{"type":"string"},{"type":"null"}], "default": null},
    "linked": {"type": "boolean", "default": false},
    "offset": {"type": "array", "items": {"type":"number"}, "minItems":3, "maxItems":3, "default":[0,0,0]},
    "collection": {"anyOf":[{"type":"string"},{"type":"null"}], "default": null}
  },
  "required": ["name"],
  "additionalProperties": false
}
```
- Output: `{ source, duplicate, linked, location, collection, data_shared }`
- Guards: source exists, OBJECT mode, new_name unique (auto .001), collection exists if provided, linked: share data else copy.

---

## Batch P0 – Modifiers essentiels (en cours)

### blender-modifier-add (Tool 8)
- Description: Add modifier to object (Array/Mirror/Solidify/Boolean/Bevel/Subsurf/etc).
- Mode: OBJECT.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "modifier_name": {"type": "string"},
    "modifier_type": {
      "type": "string",
      "enum": ["ARRAY","BEVEL","BOOLEAN","BUILD","DECIMATE","EDGE_SPLIT","MASK","MIRROR","MULTIRES","REMESH","SCREW","SKIN","SOLIDIFY","SUBSURF","TRIANGULATE","WELD","ARMATURE","CAST","CURVE","DISPLACE","HOOK","LAPLACIANDEFORM","LATTICE","MESH_DEFORM","SHRINKWRAP","SIMPLE_DEFORM","SMOOTH","CORRECTIVE_SMOOTH","LAPLACIANSMOOTH","SURFACE_DEFORM","WARP","WAVE","CLOTH","COLLISION","DYNAMIC_PAINT","EXPLODE","FLUID","OCEAN","PARTICLE_INSTANCE","PARTICLE_SYSTEM","SOFT_BODY","NODES"]
    }
  },
  "required": ["name", "modifier_name", "modifier_type"],
  "additionalProperties": false
}
```
- Output: `{ name, modifier, type, index }`
- Guards: object exists (mesh/curve/lattice…), OBJECT mode, modifier_name unique, modifier_type valid.

### blender-modifier-configure (Tool 9)
- Description: Configure modifier parameters (type-specific).
- Mode: OBJECT.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "modifier_name": {"type": "string"},
    "params": {"type": "object", "additionalProperties": true}
  },
  "required": ["name", "modifier_name", "params"],
  "additionalProperties": false
}
```
- Params by type (highlights):
  - ARRAY: count (1-10000), relative_offset_displace [3], constant_offset_displace [3], use_constant_offset, use_merge_vertices, merge_threshold.
  - MIRROR: use_axis [3], use_bisect_axis [3], use_clip, use_mirror_merge, merge_threshold, mirror_object.
  - SOLIDIFY: thickness (-10..10), offset (-1..1), use_even_offset, use_quality_normals, use_rim, use_rim_only.
  - BOOLEAN: operation (DIFFERENCE/UNION/INTERSECT), solver (EXACT/FLOAT/MANIFOLD), object, use_self, use_hole_tolerant.
  - SUBSURF: levels/render_levels (0-6), subdivision_type (CATMULL_CLARK/SIMPLE), use_creases, quality (1-6).
  - BEVEL: width (0-1000), segments (1-100), profile (0-1), limit_method (NONE/ANGLE/WEIGHT/VGROUP), angle_limit (0-3.14159), use_clamp_overlap, offset_type (OFFSET/WIDTH/DEPTH/PERCENT).
  - SCREW: angle (-1000..1000), steps/render_steps (2-512), iterations (1-100), screw_offset (-1000..1000), use_smooth_shade, use_merge_vertices, merge_threshold.
  - SIMPLE_DEFORM: deform_method (TWIST/BEND/TAPER/STRETCH), angle (-6.28..6.28), deform_axis (X/Y/Z), lock_x/lock_y, origin.
- Output: `{ name, modifier, type, configured_params }`
- Guards: object exists, modifier exists, params valid per type, referenced objects exist, clamp numeric ranges.

### blender-modifier-configure-array (Tool 10)
- Description: Configure Array modifier with preset patterns (LINEAR/CIRCULAR/GRID/CURVE_FIT/CUSTOM).
- Mode: OBJECT.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "modifier_name": {"type": "string"},
    "pattern": {"type": "string", "enum": ["LINEAR","CIRCULAR","GRID","CURVE_FIT","CUSTOM"], "default": "LINEAR"},
    "count": {"type": "integer", "minimum": 1, "maximum": 10000, "default": 5},
    "offset": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [1.2,0,0]},
    "grid_counts": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
    "use_merge": {"type": "boolean", "default": false},
    "merge_threshold": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.01},
    "offset_object": {"anyOf": [{"type":"string"},{"type":"null"}]},
    "curve_object": {"anyOf": [{"type":"string"},{"type":"null"}]}
  },
  "required": ["name", "modifier_name"],
  "additionalProperties": false
}
```
- Patterns:
  - LINEAR: count copies spaced by offset (relative_offset_displace).
  - CIRCULAR: use_object_offset with offset_object (empty), rotate empty 360/count.
  - GRID: two Array modifiers X then Y, grid_counts [nx, ny], offsets computed.
  - CURVE_FIT: fit_type=FIT_CURVE, curve=curve_object, adjust count by length.
  - CUSTOM: direct params.
- Output: `{ name, modifier, pattern, count, offset, configuration }`
- Guards: object & modifier exist (ARRAY), offset_object exists (EMPTY) for CIRCULAR, curve_object exists (CURVE) for CURVE_FIT, grid safe creation.

---

New priority specs below (visual feedback, diagnostics, selection, modifiers, modeling ops, UV/material, measurement, cleanup, curves, batch ops).

## Batch P1 - Visual feedback (Tier S+++)

### blender-viewport-screenshot-complete
- Description: Multi-view viewport capture with shading + overlays/diagnostics and optional composite grid.
- Mode: OBJECT (VIEW3D required); frames `object_name` before capture.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "views": {"type": "array", "items": {"type": "string", "enum": ["FRONT","RIGHT","TOP","ISO_FRONT_RIGHT","LEFT","BACK","BOTTOM"]}, "default": ["FRONT"]},
    "projection": {"type": "string", "enum": ["ORTHO","PERSP"], "default": "ORTHO"},
    "shading_mode": {"type": "array", "items": {"type": "string", "enum": ["SOLID","WIREFRAME","MATERIAL","RENDERED","BOUNDBOX","TEXTURE","MATCAP"]}, "default": ["SOLID"]},
    "overlay_modes": {
      "type": "object",
      "properties": {
        "show_wireframe": {"type": "boolean", "default": false},
        "show_edges": {"type": "boolean", "default": false},
        "show_face_orientation": {"type": "boolean", "default": false},
        "show_edge_sharp": {"type": "boolean", "default": false},
        "show_edge_seams": {"type": "boolean", "default": false},
        "show_normals": {"type": "boolean", "default": false},
        "show_vertex_normals": {"type": "boolean", "default": false},
        "show_split_normals": {"type": "boolean", "default": false},
        "show_bounds": {"type": "boolean", "default": false},
        "show_grid": {"type": "boolean", "default": true},
        "show_axes": {"type": "boolean", "default": true},
        "show_measurements": {"type": "boolean", "default": false}
      },
      "default": {}
    },
    "diagnostic_overlays": {"type": "array", "items": {"type": "string", "enum": ["FACE_ORIENTATION","EDGE_ANGLE","THICKNESS","DISTORTION","INTERSECTIONS"]}, "default": []},
    "output": {
      "type": "object",
      "properties": {
        "format": {"type": "string", "enum": ["composite_grid","separate","layered"], "default": "separate"},
        "resolution": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2, "default": [1920,1080]},
        "labels": {"type": "boolean", "default": true},
        "compare_wireframe": {"type": "boolean", "default": false}
      },
      "required": ["format"],
      "additionalProperties": false
    }
  },
  "required": ["object_name"],
  "additionalProperties": false
}
```
- Output: `captures` array with `{view, shading, diagnostics, file}` entries; optional `composite`/`layers` path when format is grid/layered; `meta` containing resolution, projection, overlays applied.
- Guards: object exists (frames view), VIEW3D context available, clamp resolution (max 8K) and total captures (e.g., <=32 combinations), overlays only when supported by shading mode, fails with clear error if render engine unavailable.

### blender-viewport-render-modes
- Description: Apply viewport render engine/workbench settings and return supported options for UI linking.
- Mode: OBJECT (VIEW3D required).
- Schema:
```json
{
  "type": "object",
  "properties": {
    "render_engine": {"type": "string", "enum": ["WORKBENCH","EEVEE","CYCLES","BLENDER_OPENGL"], "default": "WORKBENCH"},
    "workbench_lighting": {"type": "string", "enum": ["STUDIO","MATCAP","FLAT"], "default": "STUDIO"},
    "color_mode": {"type": "string", "enum": ["MATERIAL","SINGLE","OBJECT","RANDOM","VERTEX"], "default": "MATERIAL"},
    "use_scene_lights": {"type": "boolean", "default": false},
    "use_scene_world": {"type": "boolean", "default": false},
    "samples": {"type": "integer", "minimum": 1, "maximum": 4096, "description": "Viewport samples for Eevee/Cycles"},
    "return_supported": {"type": "boolean", "default": true}
  },
  "required": [],
  "additionalProperties": false
}
```
- Output: `{ render_engine, workbench_lighting, color_mode, use_scene_lights, use_scene_world, samples, supported: { render_engine:[...], workbench_lighting:[...], color_mode:[...] } }`
- Guards: VIEW3D context available; fall back to WORKBENCH if engine unsupported headless; color_mode only applied when WORKBENCH; clamp samples; Cycles uses preview settings only (no full render).

## Batch P2 - Mesh introspection (Tier S)

### blender-mesh-query-geometry
- Description: Dump mesh geometry (verts/edges/faces) with optional stats and limits.
- Mode: OBJECT or EDIT (bmesh data-first), selection optional.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "get_vertices": {"type": "boolean", "default": true},
    "get_edges": {"type": "boolean", "default": true},
    "get_faces": {"type": "boolean", "default": true},
    "get_loops": {"type": "boolean", "default": false},
    "get_normals": {"type": "boolean", "default": true},
    "get_uvs": {"type": "boolean", "default": false},
    "get_vertex_colors": {"type": "boolean", "default": false},
    "get_weights": {"type": "boolean", "default": false},
    "selection_only": {"type": "boolean", "default": false},
    "visible_only": {"type": "boolean", "default": false},
    "format": {"type": "string", "enum": ["compact","detailed"], "default": "compact"},
    "limit": {"type": "integer", "minimum": 1, "maximum": 50000, "default": 5000},
    "compute_stats": {"type": "boolean", "default": true}
  },
  "required": ["object_name"],
  "additionalProperties": false
}
```
- Output: `{ vertices:[{i,co,no,sel,uv,vc,weights}], edges:[{i,v,sel,sharp,seam}], faces:[{i,v,no,area,sel,uvs}], loops:[...], stats:{verts,edges,faces,tris,selected:{...}, bounds:{min,max,center,dimensions}} }` with arrays truncated to `limit`.
- Guards: object exists and is MESH; does not change selection; clamps limit to avoid huge payloads; respects visible_only by viewport visibility; returns empty arrays when none requested.

### blender-mesh-query-selection
- Description: Report current selection mode, indices, counts, and bounds.
- Mode: EDIT preferred (falls back to OBJECT selection state when possible).
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"}
  },
  "required": ["object_name"],
  "additionalProperties": false
}
```
- Output: `{ mode: "VERT"|"EDGE"|"FACE", selected_indices: [...], selected_count, total_count, bounds:{min,max,center,dimensions}, islands }`
- Guards: object exists MESH; returns mode inferred from tool settings; if not in EDIT returns OBJECT selection bounds only; empty selection handled gracefully.

### blender-mesh-query-topology
- Description: Topology health checks (manifold, ngons, poles, boundaries).
- Mode: OBJECT or EDIT (read-only).
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "checks": {"type": "array", "items": {"type": "string", "enum": ["all","manifold","watertight","ngons","poles"]}, "default": ["all"]}
  },
  "required": ["object_name"],
  "additionalProperties": false
}
```
- Output: `{ is_manifold, is_watertight, has_boundary, boundary_edges:[], non_manifold_edges:[], non_manifold_verts:[], ngons:{count,indices}, tris:{count,ratio}, poles:{n3,n5,n6_plus}, isolated_verts:[], isolated_edges:[], degenerate_faces:[] }`
- Guards: object exists MESH; checks filtered by requested list; uses fast bmesh queries; large lists trimmed to safe size with counts preserved.

### blender-mesh-analyze-quality
- Description: Quality metrics for lengths/areas/angles/distortion with outlier detection.
- Mode: OBJECT or EDIT (read-only bmesh).
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "metrics": {"type": "array", "items": {"type": "string", "enum": ["all","edge_length","face_area","angles","distortion"]}, "default": ["all"]},
    "outlier_sigma": {"type": "number", "minimum": 0, "maximum": 10, "default": 3.0}
  },
  "required": ["object_name"],
  "additionalProperties": false
}
```
- Output: `{ edge_length:{min,max,avg,outliers:[{edge,length}]}, face_area:{min,max,avg,outliers:[...]} , angles:{min_angle,max_angle,acute_faces,obtuse_faces}, distortion:{avg_stretch,max_stretch,distorted_faces:[{face,stretch}]} }`
- Guards: object exists MESH; clamps sigma/outlier lists; distortion requires UVs else returns warning; no mutation of selection.

## Batch P3 - Advanced selection (Tier A)

### blender-mesh-select-by-position
- Description: Select elements by position relative to axis thresholds (local or world).
- Mode: EDIT; affects selection for verts/edges/faces.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "mode": {"type": "string", "enum": ["VERT","EDGE","FACE"]},
    "axis": {"type": "string", "enum": ["X","Y","Z"]},
    "operator": {"type": "string", "enum": ["GREATER","LESS","BETWEEN","EQUAL"]},
    "value": {"type": "number"},
    "value_max": {"type": "number"},
    "threshold": {"type": "number", "default": 0.001},
    "extend": {"type": "boolean", "default": false},
    "use_local": {"type": "boolean", "default": false}
  },
  "required": ["object_name","mode","axis","operator","value"],
  "additionalProperties": false
}
```
- Output: `{ selected_count, total, mode, bounds:{min,max,center,dimensions} }`
- Guards: object exists MESH; EDIT mode enforced; clears selection unless extend; BETWEEN requires value_max>value; threshold used for EQUAL; respects local/world coordinates.

### blender-mesh-select-by-area
- Description: Select faces by area range.
- Mode: EDIT, face select.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "min_area": {"type": "number", "default": 0},
    "max_area": {"type": "number"},
    "extend": {"type": "boolean", "default": false}
  },
  "required": ["object_name","max_area"],
  "additionalProperties": false
}
```
- Output: `{ selected_count, total_faces, area_range:[min_area,max_area] }`
- Guards: object exists MESH; EDIT mode face selection; max_area>=min_area; clears selection unless extend.

### blender-mesh-select-boundary-complete
- Description: Select all boundary edges (optionally only largest loop).
- Mode: EDIT, edge select.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "all_boundaries": {"type": "boolean", "default": true},
    "largest_only": {"type": "boolean", "default": false},
    "extend": {"type": "boolean", "default": false}
  },
  "required": ["object_name"],
  "additionalProperties": false
}
```
- Output: `{ boundary_edges:[...], loops: count, selected_count }`
- Guards: object exists MESH; EDIT mode edge selection; largest_only picks longest boundary loop; respects extend flag.

### blender-mesh-select-island
- Description: Select island by index or largest/smallest.
- Mode: EDIT; uses island detection on faces.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "island_index": {"anyOf": [{"type": "integer"}, {"type": "null"}], "default": null},
    "by_size": {"anyOf": [{"type": "string", "enum": ["LARGEST","SMALLEST"]}, {"type": "null"}], "default": null},
    "extend": {"type": "boolean", "default": false}
  },
  "required": ["object_name"],
  "additionalProperties": false
}
```
- Output: `{ island_index, island_count, selected_faces, total_faces }`
- Guards: object exists MESH; EDIT mode; either island_index or by_size determines target (index overrides by_size); clears selection unless extend.

### blender-mesh-select-by-vertex-count
- Description: Select faces by vertex count (e.g., only quads).
- Mode: EDIT, face select.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "count": {"type": "integer", "minimum": 3},
    "operator": {"type": "string", "enum": ["EQUAL","GREATER","LESS"], "default": "EQUAL"},
    "extend": {"type": "boolean", "default": false}
  },
  "required": ["object_name","count"],
  "additionalProperties": false
}
```
- Output: `{ selected_count, total_faces, condition: ">=4" }`
- Guards: object exists MESH; EDIT + face mode; clears selection unless extend.

## Batch P4 - Modifiers essentials (Tier S)

### blender-modifier-subdivision-surface
- Description: Add/configure Subdivision Surface modifier.
- Mode: OBJECT.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "modifier_name": {"type": "string", "default": "Subsurf"},
    "levels": {"type": "integer", "minimum": 0, "maximum": 6, "default": 2},
    "render_levels": {"type": "integer", "minimum": 0, "maximum": 6, "default": 3},
    "subdivision_type": {"type": "string", "enum": ["CATMULL_CLARK","SIMPLE"], "default": "CATMULL_CLARK"},
    "use_creases": {"type": "boolean", "default": true},
    "boundary_smooth": {"type": "string", "enum": ["ALL","PRESERVE_CORNERS"], "default": "ALL"},
    "use_limit_surface": {"type": "boolean", "default": false}
  },
  "required": ["object_name"],
  "additionalProperties": false
}
```
- Output: `{ name, modifier: modifier_name, type: "SUBSURF", levels, render_levels, subdivision_type, use_creases }`
- Guards: object exists, adds modifier if missing else reuses name; clamps levels; OBJECT mode.

### blender-modifier-boolean
- Description: Boolean modifier with solver/operand options.
- Mode: OBJECT.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "modifier_name": {"type": "string", "default": "Boolean"},
    "operation": {"type": "string", "enum": ["DIFFERENCE","UNION","INTERSECT"], "default": "DIFFERENCE"},
    "operand_object": {"type": "string"},
    "operand_type": {"type": "string", "enum": ["OBJECT","COLLECTION"], "default": "OBJECT"},
    "solver": {"type": "string", "enum": ["FAST","EXACT"], "default": "EXACT"},
    "use_self": {"type": "boolean", "default": false},
    "use_hole_tolerant": {"type": "boolean", "default": false},
    "material_mode": {"type": "string", "enum": ["INDEX","TRANSFER"], "default": "INDEX"}
  },
  "required": ["object_name","operand_object"],
  "additionalProperties": false
}
```
- Output: `{ name, modifier: modifier_name, type: "BOOLEAN", operation, operand: operand_object, solver }`
- Guards: object and operand exist; operand_type respected; warns if self-boolean; OBJECT mode; solver FAST only for manifold-safe use cases.

### blender-modifier-array-complete
- Description: Full Array modifier setup (fit modes + offsets + merge/caps).
- Mode: OBJECT.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "modifier_name": {"type": "string", "default": "Array"},
    "fit_type": {"type": "string", "enum": ["FIXED_COUNT","FIT_LENGTH","FIT_CURVE"], "default": "FIXED_COUNT"},
    "count": {"type": "integer", "minimum": 1, "maximum": 10000, "default": 5},
    "fit_length": {"type": "number", "default": 1.0},
    "curve_object": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null},
    "offset_mode": {
      "type": "object",
      "properties": {
        "use_relative": {"type": "boolean", "default": true},
        "relative_offset": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [1.0,0,0]},
        "use_constant": {"type": "boolean", "default": false},
        "constant_offset": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [0,0,0]},
        "use_object": {"type": "boolean", "default": false},
        "offset_object": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null}
      },
      "default": {}
    },
    "merge": {
      "type": "object",
      "properties": {
        "use_merge": {"type": "boolean", "default": false},
        "merge_threshold": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.01},
        "first_last": {"type": "boolean", "default": false}
      },
      "default": {}
    },
    "caps": {
      "type": "object",
      "properties": {
        "start_cap": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null},
        "end_cap": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null}
      },
      "default": {}
    },
    "uv_offset": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2, "default": [0,0]}
  },
  "required": ["object_name"],
  "additionalProperties": false
}
```
- Output: `{ name, modifier: modifier_name, type: "ARRAY", fit_type, count, offsets:{relative,constant,object}, merge, caps }`
- Guards: object exists; OBJECT mode; curve/offset objects validated; merge threshold clamped; caps require mesh objects.

### blender-modifier-mirror-complete
- Description: Mirror modifier with bisect/merge/UV options.
- Mode: OBJECT.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "modifier_name": {"type": "string", "default": "Mirror"},
    "use_axis": {"type": "array", "items": {"type": "boolean"}, "minItems": 3, "maxItems": 3, "default": [true,false,false]},
    "use_bisect_axis": {"type": "array", "items": {"type": "boolean"}, "minItems": 3, "maxItems": 3, "default": [true,false,false]},
    "use_bisect_flip_axis": {"type": "array", "items": {"type": "boolean"}, "minItems": 3, "maxItems": 3, "default": [false,false,false]},
    "mirror_object": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null},
    "use_clip": {"type": "boolean", "default": true},
    "use_mirror_merge": {"type": "boolean", "default": true},
    "merge_threshold": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.001},
    "mirror_uvs": {
      "type": "object",
      "properties": {
        "use_mirror_u": {"type": "boolean", "default": false},
        "use_mirror_v": {"type": "boolean", "default": false},
        "offset_u": {"type": "number", "default": 0.0},
        "offset_v": {"type": "number", "default": 0.0}
      },
      "default": {}
    },
    "use_mirror_vertex_groups": {"type": "boolean", "default": true}
  },
  "required": ["object_name"],
  "additionalProperties": false
}
```
- Output: `{ name, modifier: modifier_name, type: "MIRROR", axes: use_axis, bisect: use_bisect_axis, merge_threshold }`
- Guards: object exists; mirror_object validated if provided; OBJECT mode; merge threshold clamped.

### blender-modifier-bevel
- Description: Bevel modifier with width/segments/profile controls.
- Mode: OBJECT.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "modifier_name": {"type": "string", "default": "Bevel"},
    "width": {"type": "number", "minimum": 0, "maximum": 1000, "default": 0.05},
    "width_type": {"type": "string", "enum": ["OFFSET","WIDTH","DEPTH","PERCENT"], "default": "OFFSET"},
    "segments": {"type": "integer", "minimum": 1, "maximum": 100, "default": 3},
    "profile": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.5},
    "limit_method": {"type": "string", "enum": ["NONE","ANGLE","WEIGHT","VGROUP"], "default": "NONE"},
    "angle_limit": {"type": "number", "minimum": 0, "maximum": 180, "default": 30},
    "vertex_group": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null},
    "miter_outer": {"type": "string", "enum": ["SHARP","PATCH","ARC"], "default": "SHARP"},
    "miter_inner": {"type": "string", "enum": ["SHARP","ARC"], "default": "SHARP"},
    "use_clamp_overlap": {"type": "boolean", "default": true},
    "loop_slide": {"type": "boolean", "default": true},
    "material": {"type": "integer", "default": -1}
  },
  "required": ["object_name"],
  "additionalProperties": false
}
```
- Output: `{ name, modifier: modifier_name, type: "BEVEL", width, segments, limit_method }`
- Guards: object exists; OBJECT mode; converts angle_limit to radians internally; vertex_group validated if provided.

### blender-modifier-solidify
- Description: Solidify modifier for shell thickness with rim options.
- Mode: OBJECT.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "modifier_name": {"type": "string", "default": "Solidify"},
    "thickness": {"type": "number", "minimum": -10, "maximum": 10, "default": 0.05},
    "offset": {"type": "number", "minimum": -1, "maximum": 1, "default": 0.0},
    "edge_crease_inner": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.0},
    "edge_crease_outer": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.0},
    "edge_crease_rim": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.0},
    "use_even_offset": {"type": "boolean", "default": false},
    "use_quality_normals": {"type": "boolean", "default": false},
    "use_rim": {"type": "boolean", "default": true},
    "use_rim_only": {"type": "boolean", "default": false},
    "material_offset": {"type": "integer", "default": 0},
    "material_offset_rim": {"type": "integer", "default": 0}
  },
  "required": ["object_name"],
  "additionalProperties": false
}
```
- Output: `{ name, modifier: modifier_name, type: "SOLIDIFY", thickness, offset, rim: use_rim }`
- Guards: object exists; OBJECT mode; thickness/offset clamped; warns when rim_only is true without rim.

## Batch P5 - Modeling operations advanced (Tier A)

### blender-mesh-extrude-manifold
- Description: Manifold-safe extrude of current selection with offset/scale/rotation.
- Mode: EDIT, selection required.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "offset": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [0,0,0.5]},
    "scale": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [1,1,1]},
    "rotate": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [0,0,0]},
    "constraint_axis": {"anyOf": [{"type": "string", "enum": ["X","Y","Z"]}, {"type": "null"}], "default": null},
    "dissolve_orthogonal": {"type": "boolean", "default": false}
  },
  "required": ["object_name"],
  "additionalProperties": false
}
```
- Output: `{ name, extruded_faces, offset, scale, rotate, constraint_axis }`
- Guards: object exists MESH; EDIT mode; selection non-empty; ensures manifold option for edges; applies transforms in order translate->rotate->scale; dissolve_orthogonal removes redundant edges when true.

### blender-mesh-inset-individual
- Description: Inset selected faces individually with even offset option.
- Mode: EDIT, face selection required.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "thickness": {"type": "number", "default": 0.1},
    "depth": {"type": "number", "default": 0.05},
    "use_individual": {"type": "boolean", "default": true},
    "use_even_offset": {"type": "boolean", "default": true},
    "use_relative_offset": {"type": "boolean", "default": false},
    "use_interpolate": {"type": "boolean", "default": true}
  },
  "required": ["object_name"],
  "additionalProperties": false
}
```
- Output: `{ name, inset_faces, thickness, depth, individual: use_individual }`
- Guards: object exists; EDIT + face mode; selection non-empty; clamps thickness/depth to safe ranges; respects even/relative offsets.

### blender-mesh-poke-faces
- Description: Poke selected faces to center (fan triangulation).
- Mode: EDIT, face selection required.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "offset": {"type": "number", "default": 0.0},
    "use_relative_offset": {"type": "boolean", "default": false},
    "center_mode": {"type": "string", "enum": ["MEAN_WEIGHTED","MEAN","BOUNDS"], "default": "MEAN_WEIGHTED"}
  },
  "required": ["object_name"],
  "additionalProperties": false
}
```
- Output: `{ name, poked_faces, offset, center_mode }`
- Guards: object exists; EDIT + face mode; selection non-empty; offset clamped; outputs created center vertices count.

### blender-mesh-loop-tools-circle
- Description: Conform selected loop to circle/flatten/space/curve.
- Mode: EDIT; selection required (verts).
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "operation": {"type": "string", "enum": ["CIRCLE","FLATTEN","SPACE","CURVE"]},
    "influence": {"type": "number", "minimum": 0, "maximum": 1, "default": 1.0},
    "interpolation": {"type": "string", "enum": ["LINEAR","CUBIC"], "default": "LINEAR"}
  },
  "required": ["object_name","operation"],
  "additionalProperties": false
}
```
- Output: `{ name, operation, affected_vertices }`
- Guards: object exists; EDIT mode; selection non-empty; requires evenly spaced loop for best results; influence blends original vs target circle.

### blender-mesh-symmetrize
- Description: Symmetrize mesh across chosen axis with threshold.
- Mode: EDIT.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "direction": {"type": "string", "enum": ["NEGATIVE_X","POSITIVE_X","NEGATIVE_Y","POSITIVE_Y","NEGATIVE_Z","POSITIVE_Z"]},
    "threshold": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.001},
    "use_topology": {"type": "boolean", "default": false}
  },
  "required": ["object_name","direction"],
  "additionalProperties": false
}
```
- Output: `{ name, direction, mirrored_verts, removed_faces }`
- Guards: object exists; EDIT mode; selection optional (uses all if none); threshold clamped; use_topology toggles topology-aware mapping.

### blender-mesh-knife-project
- Description: Project cutter objects onto target mesh and cut.
- Mode: EDIT on target.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "target_object": {"type": "string"},
    "cutter_objects": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "cut_through": {"type": "boolean", "default": true},
    "use_occlude_geometry": {"type": "boolean", "default": false}
  },
  "required": ["target_object","cutter_objects"],
  "additionalProperties": false
}
```
- Output: `{ target: target_object, cutters: cutter_objects, projected_edges, cut_faces }`
- Guards: target exists MESH; cutters exist and are mesh/curve/GP; EDIT mode on target; cut_through controls backface cuts; ensures cutters visible in projection.

## Batch P6 - UV & material tools (Tier B)

### blender-uv-pack-islands
- Description: Pack UV islands with margin/rotation options.
- Mode: EDIT (UV context) or OBJECT with UV layer; uses bmesh UV.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "margin": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.02},
    "rotate": {"type": "boolean", "default": true},
    "rotate_method": {"type": "string", "enum": ["ANY","AXIS_ALIGNED","CARDINAL"], "default": "ANY"},
    "shape_method": {"type": "string", "enum": ["AABB","CONVEX"], "default": "AABB"},
    "merge_overlap": {"type": "boolean", "default": false},
    "scale": {"type": "boolean", "default": true},
    "target_udim": {"type": "integer", "default": 1001}
  },
  "required": ["object_name"],
  "additionalProperties": false
}
```
- Output: `{ name, islands, margin, rotated: rotate, target_udim }`
- Guards: object exists MESH with UVs; selection optional (packs selected faces when in EDIT); margin clamped; merge_overlap toggles Weld/Pack; respects active UV map.

### blender-material-assign-fixed
- Description: Assign material to selection or whole object, creating slot if needed.
- Mode: OBJECT or EDIT (faces) depending on assign_to_selection.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "material_name": {"type": "string"},
    "slot_index": {"anyOf": [{"type": "integer"}, {"type": "null"}], "default": null},
    "assign_to_selection": {"type": "boolean", "default": true},
    "create_slot_if_missing": {"type": "boolean", "default": true}
  },
  "required": ["object_name","material_name"],
  "additionalProperties": false
}
```
- Output: `{ name, material: material_name, slot_index, assigned_faces }`
- Guards: object exists; material created if absent; EDIT mode required when assigning to selection; slot index validated or auto-created.

## Batch P7 - Precision & measurement (Tier B)

### blender-mesh-measure
- Description: Measure length/area/volume/distance for current selection or whole mesh.
- Mode: EDIT (preferred) or OBJECT.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "measure_type": {"type": "string", "enum": ["LENGTH","AREA","VOLUME","DISTANCE"]},
    "selection_only": {"type": "boolean", "default": true},
    "unit_system": {"type": "string", "enum": ["METRIC","IMPERIAL","NONE"], "default": "NONE"}
  },
  "required": ["object_name","measure_type"],
  "additionalProperties": false
}
```
- Output: `{ measure_type, value, unit, selection_only, details:{segments,faces,verts} }`
- Guards: object exists MESH; volume requires closed mesh else returns warning with signed volume; distance uses pairwise bounds when selection has two verts/objects.

### blender-mesh-align-selection
- Description: Align selection to axis or value (local/world).
- Mode: EDIT; selection required.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "axis": {"type": "string", "enum": ["X","Y","Z"]},
    "align_mode": {"type": "string", "enum": ["MIN","MAX","CENTER","CURSOR","VALUE"]},
    "value": {"type": "number", "default": 0.0},
    "use_local": {"type": "boolean", "default": false}
  },
  "required": ["object_name","axis","align_mode"],
  "additionalProperties": false
}
```
- Output: `{ name, axis, align_mode, value_applied, moved_vertices }`
- Guards: object exists; EDIT mode; selection non-empty; CURSOR uses 3D cursor coord; VALUE ignored unless align_mode=VALUE.

### blender-mesh-distribute
- Description: Distribute selected elements evenly along an axis or surface spacing.
- Mode: EDIT; works on verts/edges/faces depending on selection mode.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "axis": {"type": "string", "enum": ["X","Y","Z"]},
    "distribution": {"type": "string", "enum": ["EVEN","LINEAR","SURFACE"]},
    "spacing": {"type": "number", "default": 0.5},
    "start_offset": {"type": "number", "default": 0.0},
    "end_offset": {"type": "number", "default": 0.0}
  },
  "required": ["object_name","axis","distribution"],
  "additionalProperties": false
}
```
- Output: `{ name, distribution, axis, spacing, affected }`
- Guards: object exists; EDIT mode; selection >=2 elements; SURFACE uses area-weighted scatter; spacing clamped to positive.

## Batch P8 - Cleanup & optimization (Tier B)

### blender-mesh-cleanup-complete
- Description: Run cleanup pipeline (remove doubles, delete loose/degenerate, recalc normals, planarize, etc).
- Mode: EDIT.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "operations": {
      "type": "object",
      "properties": {
        "remove_doubles": {"type": "boolean", "default": true},
        "merge_threshold": {"type": "number", "default": 0.0001},
        "delete_loose": {"type": "boolean", "default": true},
        "delete_degenerate": {"type": "boolean", "default": true},
        "dissolve_degenerate": {"type": "boolean", "default": true},
        "recalculate_normals": {"type": "boolean", "default": true},
        "make_planar_faces": {"type": "boolean", "default": false},
        "planar_threshold": {"type": "number", "default": 0.001},
        "delete_interior_faces": {"type": "boolean", "default": false},
        "split_non_planar": {"type": "boolean", "default": false}
      },
      "default": {}
    },
    "report_changes": {"type": "boolean", "default": true}
  },
  "required": ["object_name"],
  "additionalProperties": false
}
```
- Output: `{ name, removed:{verts,edges,faces}, merged:{count,threshold}, normals_recalculated, planarized_faces, interior_deleted }`
- Guards: object exists; EDIT mode; thresholds clamped; operations run in safe order (select->operate); report summarises counts.

### blender-mesh-decimate
- Description: Decimate mesh with ratio/method and optional triangulate.
- Mode: OBJECT (modifier) or EDIT (bmesh collapse) depending on implementation.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "ratio": {"type": "number", "minimum": 0.0, "maximum": 1.0, "default": 0.5},
    "method": {"type": "string", "enum": ["COLLAPSE","UNSUBDIVIDE","PLANAR"], "default": "COLLAPSE"},
    "triangulate": {"type": "boolean", "default": false},
    "use_symmetry": {"type": "boolean", "default": false},
    "symmetry_axis": {"type": "string", "enum": ["X","Y","Z"], "default": "X"}
  },
  "required": ["object_name"],
  "additionalProperties": false
}
```
- Output: `{ name, method, ratio_applied, face_count_before, face_count_after }`
- Guards: object exists MESH; warns if ratio too low for manifold; symmetry only for COLLAPSE; triangulate optional post-pass.

### blender-mesh-remesh
- Description: Remesh to voxel/quad/sharp with adaptivity and boundary preservation.
- Mode: OBJECT (modifier-like op) to avoid edit conflicts.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "object_name": {"type": "string"},
    "mode": {"type": "string", "enum": ["VOXEL","QUAD","SHARP"], "default": "VOXEL"},
    "voxel_size": {"type": "number", "default": 0.05},
    "adaptivity": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.0},
    "smooth_normals": {"type": "boolean", "default": true},
    "preserve_sharp": {"type": "boolean", "default": true},
    "preserve_boundary": {"type": "boolean", "default": true}
  },
  "required": ["object_name"],
  "additionalProperties": false
}
```
- Output: `{ name, mode, voxel_size, face_count_before, face_count_after }`
- Guards: object exists; mode determines params used (adaptivity ignored for voxel); preserves scale by applying transforms first if needed; OBJECT mode only.

## Batch P9 - Curve tools (Tier B)

### blender-curve-from-vertices
- Description: Create curve from list of coords or selected verts of mesh.
- Mode: OBJECT (reads EDIT selection when vertices="SELECTED").
- Schema:
```json
{
  "type": "object",
  "properties": {
    "source_object": {"type": "string"},
    "vertices": {"anyOf": [{"type": "string", "enum": ["SELECTED"]}, {"type": "array", "items": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3}}]},
    "curve_name": {"type": "string", "default": "ProfileCurve"},
    "curve_type": {"type": "string", "enum": ["BEZIER","NURBS","POLY"], "default": "BEZIER"},
    "cyclic": {"type": "boolean", "default": false},
    "resolution": {"type": "integer", "default": 12},
    "handle_type": {"type": "string", "enum": ["AUTO","VECTOR","ALIGNED"], "default": "AUTO"}
  },
  "required": ["source_object","vertices"],
  "additionalProperties": false
}
```
- Output: `{ curve: curve_name, curve_type, points, cyclic }`
- Guards: source exists; if vertices="SELECTED" requires EDIT selection on mesh; handle_type applied when curve_type=BEZIER; duplicates curve name resolved with .001 suffix.

### blender-curve-to-mesh
- Description: Convert curve to mesh with bevel/extrude options.
- Mode: OBJECT.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "curve_name": {"type": "string"},
    "extrude": {"type": "number", "default": 0.1},
    "bevel_depth": {"type": "number", "default": 0.05},
    "bevel_resolution": {"type": "integer", "minimum": 0, "maximum": 16, "default": 4},
    "use_fill_caps": {"type": "boolean", "default": true},
    "resolution_u": {"type": "integer", "default": 12},
    "resolution_v": {"type": "integer", "default": 4}
  },
  "required": ["curve_name"],
  "additionalProperties": false
}
```
- Output: `{ source_curve: curve_name, mesh_object: "<name>_Mesh", extrude, bevel_depth }`
- Guards: curve exists; OBJECT mode; creates new mesh object (non-destructive) unless conversion target already mesh; clamps bevel/extrude to safe values.

## Batch P10 - Batch operations (Tier C)

### blender-batch-operation
- Description: Apply transform/material/modifier/parent operations to multiple objects with shared payload.
- Mode: OBJECT.
- Schema:
```json
{
  "type": "object",
  "properties": {
    "objects": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "operation": {
      "type": "object",
      "properties": {
        "type": {"type": "string", "enum": ["transform","material","modifier","parent"]},
        "transform": {
          "type": "object",
          "properties": {
            "move": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [0,0,0]},
            "rotate": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [0,0,0]},
            "scale": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [1,1,1]}
          },
          "default": {}
        },
        "material": {"type": "string"},
        "modifier": {"type": "object", "additionalProperties": true},
        "parent": {"type": "string"}
      },
      "required": ["type"],
      "additionalProperties": false
    },
    "individual_origins": {"type": "boolean", "default": true}
  },
  "required": ["objects","operation"],
  "additionalProperties": false
}
```
- Output: `{ objects:[{name,status,error?}], operation:{type,...}, applied_count }`
- Guards: all objects exist; OBJECT mode; transform uses individual origins flag; modifier payload forwarded to relevant modifier tool; parent requires parent object exists; stops per-object on first error but continues others with status.
