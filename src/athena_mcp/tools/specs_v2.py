from __future__ import annotations

from typing import Any, Dict

JSONDict = Dict[str, Any]

# Visual feedback
VIEWPORT_SCREENSHOT_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "views": {
            "type": "array",
            "items": {"type": "string", "enum": ["FRONT", "RIGHT", "TOP", "ISO_FRONT_RIGHT", "LEFT", "BACK", "BOTTOM"]},
            "default": ["FRONT"],
        },
        "projection": {"type": "string", "enum": ["ORTHO", "PERSP"], "default": "ORTHO"},
        "shading_mode": {
            "type": "array",
            "items": {"type": "string", "enum": ["SOLID", "WIREFRAME", "MATERIAL", "RENDERED", "BOUNDBOX", "TEXTURE", "MATCAP"]},
            "default": ["SOLID"],
        },
        "overlay_modes": {
            "type": "object",
            "properties": {
                "show_wireframe": {"type": "boolean", "default": False},
                "show_edges": {"type": "boolean", "default": False},
                "show_face_orientation": {"type": "boolean", "default": False},
                "show_edge_sharp": {"type": "boolean", "default": False},
                "show_edge_seams": {"type": "boolean", "default": False},
                "show_normals": {"type": "boolean", "default": False},
                "show_vertex_normals": {"type": "boolean", "default": False},
                "show_split_normals": {"type": "boolean", "default": False},
                "show_bounds": {"type": "boolean", "default": False},
                "show_grid": {"type": "boolean", "default": True},
                "show_axes": {"type": "boolean", "default": True},
                "show_measurements": {"type": "boolean", "default": False},
            },
            "default": {},
        },
        "diagnostic_overlays": {
            "type": "array",
            "items": {"type": "string", "enum": ["FACE_ORIENTATION", "EDGE_ANGLE", "THICKNESS", "DISTORTION", "INTERSECTIONS"]},
            "default": [],
        },
        "auto_frame_selection": {"type": "boolean", "default": False},
        "highlight_selection": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "default": False},
                "color": {
                    "type": "array",
                    "items": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "minItems": 4,
                    "maxItems": 4,
                },
                "thickness": {"type": "number"},
            },
            "default": {},
            "additionalProperties": False,
        },
        "measurement_overlays": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["distance", "angle", "radius", "area", "perimeter"]},
                    "points": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 3,
                        },
                    },
                    "label": {"type": "string"},
                    "precision": {"type": "integer", "default": 2},
                    "unit": {"type": "string", "enum": ["m", "cm", "mm", "auto"], "default": "auto"},
                    "color": {
                        "type": "array",
                        "items": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "minItems": 4,
                        "maxItems": 4,
                    },
                },
                "required": ["type", "points"],
                "additionalProperties": False,
            },
            "default": [],
        },
        "annotation_overlays": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["text", "arrow", "circle", "box", "line", "highlight"]},
                    "position": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 3,
                    },
                    "content": {"type": "string"},
                    "color": {
                        "type": "array",
                        "items": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "minItems": 4,
                        "maxItems": 4,
                    },
                    "size": {"type": "number"},
                    "thickness": {"type": "number"},
                },
                "required": ["type"],
                "additionalProperties": False,
            },
            "default": [],
        },
        "diff_reference": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "default": False},
                "reference_image": {"type": "string"},
                "blend_mode": {"type": "string", "enum": ["difference", "overlay"]},
            },
            "default": {},
            "additionalProperties": False,
        },
        "quality_preset": {"type": "string", "enum": ["fast", "balanced", "high"], "default": "balanced"},
        "auto_optimize_views": {"type": "boolean", "default": False},
        "edge_display": {
            "type": "object",
            "properties": {
                "mode": {"type": "string", "enum": ["none", "sharp_only", "all", "seams", "creases"], "default": "none"},
                "thickness": {"type": "number"},
                "color": {
                    "type": "array",
                    "items": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "minItems": 4,
                    "maxItems": 4,
                },
            },
            "default": {},
            "additionalProperties": False,
        },
        "matcap_override": {"type": "string"},
        "post_processing": {
            "type": "object",
            "properties": {
                "sharpen": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "contrast": {"type": "number"},
                "brightness": {"type": "number"},
            },
            "default": {},
            "additionalProperties": False,
        },
        "output": {
            "type": "object",
            "properties": {
                "format": {"type": "string", "enum": ["composite_grid", "separate", "layered"], "default": "separate"},
                "resolution": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2, "default": [1920, 1080]},
                "labels": {"type": "boolean", "default": True},
                "compare_wireframe": {"type": "boolean", "default": False},
            },
            "required": ["format"],
            "additionalProperties": False,
        },
    },
    "required": ["object_name"],
    "additionalProperties": False,
}

VIEWPORT_RENDER_MODES_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "render_engine": {"type": "string", "enum": ["WORKBENCH", "EEVEE", "CYCLES", "BLENDER_OPENGL"], "default": "WORKBENCH"},
        "workbench_lighting": {"type": "string", "enum": ["STUDIO", "MATCAP", "FLAT"], "default": "STUDIO"},
        "color_mode": {"type": "string", "enum": ["MATERIAL", "SINGLE", "OBJECT", "RANDOM", "VERTEX"], "default": "MATERIAL"},
        "use_scene_lights": {"type": "boolean", "default": False},
        "use_scene_world": {"type": "boolean", "default": False},
        "samples": {"type": "integer", "minimum": 1, "maximum": 4096},
        "return_supported": {"type": "boolean", "default": True},
    },
    "required": [],
    "additionalProperties": False,
}

VIEWPORT_DIAGNOSTICS_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {},
    "additionalProperties": False,
}

# Mesh introspection
MESH_QUERY_GEOMETRY_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "get_vertices": {"type": "boolean", "default": True},
        "get_edges": {"type": "boolean", "default": True},
        "get_faces": {"type": "boolean", "default": True},
        "get_loops": {"type": "boolean", "default": False},
        "get_normals": {"type": "boolean", "default": True},
        "get_uvs": {"type": "boolean", "default": False},
        "get_vertex_colors": {"type": "boolean", "default": False},
        "get_weights": {"type": "boolean", "default": False},
        "selection_only": {"type": "boolean", "default": False},
        "visible_only": {"type": "boolean", "default": False},
        "format": {"type": "string", "enum": ["compact", "detailed"], "default": "compact"},
        "limit": {"type": "integer", "minimum": 1, "maximum": 50000, "default": 5000},
        "compute_stats": {"type": "boolean", "default": True},
    },
    "required": ["object_name"],
    "additionalProperties": False,
}

MESH_QUERY_SELECTION_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {"object_name": {"type": "string"}},
    "required": ["object_name"],
    "additionalProperties": False,
}

MESH_QUERY_TOPOLOGY_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "checks": {
            "type": "array",
            "items": {"type": "string", "enum": ["all", "manifold", "watertight", "ngons", "poles"]},
            "default": ["all"],
        },
    },
    "required": ["object_name"],
    "additionalProperties": False,
}

MESH_ANALYZE_QUALITY_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "metrics": {
            "type": "array",
            "items": {"type": "string", "enum": ["all", "edge_length", "face_area", "angles", "distortion"]},
            "default": ["all"],
        },
        "outlier_sigma": {"type": "number", "minimum": 0, "maximum": 10, "default": 3.0},
    },
    "required": ["object_name"],
    "additionalProperties": False,
}

# Advanced selection
MESH_SELECT_BY_POSITION_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "mode": {"type": "string", "enum": ["VERT", "EDGE", "FACE"]},
        "axis": {"type": "string", "enum": ["X", "Y", "Z"]},
        "operator": {"type": "string", "enum": ["GREATER", "LESS", "BETWEEN", "EQUAL"]},
        "value": {"type": "number"},
        "value_max": {"type": "number"},
        "threshold": {"type": "number", "default": 0.001},
        "extend": {"type": "boolean", "default": False},
        "use_local": {"type": "boolean", "default": False},
    },
    "required": ["object_name", "mode", "axis", "operator", "value"],
    "additionalProperties": False,
}

MESH_SELECT_BY_AREA_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "min_area": {"type": "number", "default": 0},
        "max_area": {"type": "number"},
        "extend": {"type": "boolean", "default": False},
    },
    "required": ["object_name", "max_area"],
    "additionalProperties": False,
}

MESH_SELECT_BOUNDARY_COMPLETE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "all_boundaries": {"type": "boolean", "default": True},
        "largest_only": {"type": "boolean", "default": False},
        "extend": {"type": "boolean", "default": False},
    },
    "required": ["object_name"],
    "additionalProperties": False,
}

MESH_SELECT_ISLAND_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "island_index": {"anyOf": [{"type": "integer"}, {"type": "null"}], "default": None},
        "by_size": {"anyOf": [{"type": "string", "enum": ["LARGEST", "SMALLEST"]}, {"type": "null"}], "default": None},
        "extend": {"type": "boolean", "default": False},
    },
    "required": ["object_name"],
    "additionalProperties": False,
}

MESH_SELECT_BY_VERTEX_COUNT_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "count": {"type": "integer", "minimum": 3},
        "operator": {"type": "string", "enum": ["EQUAL", "GREATER", "LESS"], "default": "EQUAL"},
        "extend": {"type": "boolean", "default": False},
    },
    "required": ["object_name", "count"],
    "additionalProperties": False,
}

# Modifiers essentials
MOD_SUBSURF_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "modifier_name": {"type": "string", "default": "Subsurf"},
        "levels": {"type": "integer", "minimum": 0, "maximum": 6, "default": 2},
        "render_levels": {"type": "integer", "minimum": 0, "maximum": 6, "default": 3},
        "subdivision_type": {"type": "string", "enum": ["CATMULL_CLARK", "SIMPLE"], "default": "CATMULL_CLARK"},
        "use_creases": {"type": "boolean", "default": True},
        "boundary_smooth": {"type": "string", "enum": ["ALL", "PRESERVE_CORNERS"], "default": "ALL"},
        "use_limit_surface": {"type": "boolean", "default": False},
    },
    "required": ["object_name"],
    "additionalProperties": False,
}

MOD_BOOLEAN_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "modifier_name": {"type": "string", "default": "Boolean"},
        "operation": {"type": "string", "enum": ["DIFFERENCE", "UNION", "INTERSECT"], "default": "DIFFERENCE"},
        "operand_object": {"type": "string"},
        "operand_type": {"type": "string", "enum": ["OBJECT", "COLLECTION"], "default": "OBJECT"},
        "solver": {"type": "string", "enum": ["FAST", "EXACT"], "default": "EXACT"},
        "use_self": {"type": "boolean", "default": False},
        "use_hole_tolerant": {"type": "boolean", "default": False},
        "material_mode": {"type": "string", "enum": ["INDEX", "TRANSFER"], "default": "INDEX"},
    },
    "required": ["object_name", "operand_object"],
    "additionalProperties": False,
}

MOD_ARRAY_COMPLETE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "modifier_name": {"type": "string", "default": "Array"},
        "fit_type": {"type": "string", "enum": ["FIXED_COUNT", "FIT_LENGTH", "FIT_CURVE"], "default": "FIXED_COUNT"},
        "count": {"type": "integer", "minimum": 1, "maximum": 10000, "default": 5},
        "fit_length": {"type": "number", "default": 1.0},
        "curve_object": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
        "offset_mode": {
            "type": "object",
            "properties": {
                "use_relative": {"type": "boolean", "default": True},
                "relative_offset": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 3,
                    "maxItems": 3,
                    "default": [1.0, 0, 0],
                },
                "use_constant": {"type": "boolean", "default": False},
                "constant_offset": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 3,
                    "maxItems": 3,
                    "default": [0, 0, 0],
                },
                "use_object": {"type": "boolean", "default": False},
                "offset_object": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
            },
            "default": {},
        },
        "merge": {
            "type": "object",
            "properties": {
                "use_merge": {"type": "boolean", "default": False},
                "merge_threshold": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.01},
                "first_last": {"type": "boolean", "default": False},
            },
            "default": {},
        },
        "caps": {
            "type": "object",
            "properties": {
                "start_cap": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
                "end_cap": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
            },
            "default": {},
        },
        "uv_offset": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2, "default": [0, 0]},
    },
    "required": ["object_name"],
    "additionalProperties": False,
}

MOD_MIRROR_COMPLETE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "modifier_name": {"type": "string", "default": "Mirror"},
        "use_axis": {"type": "array", "items": {"type": "boolean"}, "minItems": 3, "maxItems": 3, "default": [True, False, False]},
        "use_bisect_axis": {"type": "array", "items": {"type": "boolean"}, "minItems": 3, "maxItems": 3, "default": [True, False, False]},
        "use_bisect_flip_axis": {"type": "array", "items": {"type": "boolean"}, "minItems": 3, "maxItems": 3, "default": [False, False, False]},
        "mirror_object": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
        "use_clip": {"type": "boolean", "default": True},
        "use_mirror_merge": {"type": "boolean", "default": True},
        "merge_threshold": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.001},
        "mirror_uvs": {
            "type": "object",
            "properties": {
                "use_mirror_u": {"type": "boolean", "default": False},
                "use_mirror_v": {"type": "boolean", "default": False},
                "offset_u": {"type": "number", "default": 0.0},
                "offset_v": {"type": "number", "default": 0.0},
            },
            "default": {},
        },
        "use_mirror_vertex_groups": {"type": "boolean", "default": True},
    },
    "required": ["object_name"],
    "additionalProperties": False,
}

MOD_BEVEL_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "modifier_name": {"type": "string", "default": "Bevel"},
        "width": {"type": "number", "minimum": 0, "maximum": 1000, "default": 0.05},
        "width_type": {"type": "string", "enum": ["OFFSET", "WIDTH", "DEPTH", "PERCENT"], "default": "OFFSET"},
        "segments": {"type": "integer", "minimum": 1, "maximum": 100, "default": 3},
        "profile": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.5},
        "limit_method": {"type": "string", "enum": ["NONE", "ANGLE", "WEIGHT", "VGROUP"], "default": "NONE"},
        "angle_limit": {"type": "number", "minimum": 0, "maximum": 180, "default": 30},
        "vertex_group": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
        "miter_outer": {"type": "string", "enum": ["SHARP", "PATCH", "ARC"], "default": "SHARP"},
        "miter_inner": {"type": "string", "enum": ["SHARP", "ARC"], "default": "SHARP"},
        "use_clamp_overlap": {"type": "boolean", "default": True},
        "loop_slide": {"type": "boolean", "default": True},
        "material": {"type": "integer", "default": -1},
    },
    "required": ["object_name"],
    "additionalProperties": False,
}

MOD_SOLIDIFY_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "modifier_name": {"type": "string", "default": "Solidify"},
        "thickness": {"type": "number", "minimum": -10, "maximum": 10, "default": 0.05},
        "offset": {"type": "number", "minimum": -1, "maximum": 1, "default": 0.0},
        "edge_crease_inner": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.0},
        "edge_crease_outer": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.0},
        "edge_crease_rim": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.0},
        "use_even_offset": {"type": "boolean", "default": False},
        "use_quality_normals": {"type": "boolean", "default": False},
        "use_rim": {"type": "boolean", "default": True},
        "use_rim_only": {"type": "boolean", "default": False},
        "material_offset": {"type": "integer", "default": 0},
        "material_offset_rim": {"type": "integer", "default": 0},
    },
    "required": ["object_name"],
    "additionalProperties": False,
}

# Modeling operations
MESH_EXTRUDE_MANIFOLD_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "offset": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [0, 0, 0.5]},
        "scale": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [1, 1, 1]},
        "rotate": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [0, 0, 0]},
        "constraint_axis": {"anyOf": [{"type": "string", "enum": ["X", "Y", "Z"]}, {"type": "null"}], "default": None},
        "dissolve_orthogonal": {"type": "boolean", "default": False},
    },
    "required": ["object_name"],
    "additionalProperties": False,
}

MESH_INSET_INDIVIDUAL_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "thickness": {"type": "number", "default": 0.1},
        "depth": {"type": "number", "default": 0.05},
        "use_individual": {"type": "boolean", "default": True},
        "use_even_offset": {"type": "boolean", "default": True},
        "use_relative_offset": {"type": "boolean", "default": False},
        "use_interpolate": {"type": "boolean", "default": True},
    },
    "required": ["object_name"],
    "additionalProperties": False,
}

MESH_POKE_FACES_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "offset": {"type": "number", "default": 0.0},
        "use_relative_offset": {"type": "boolean", "default": False},
        "center_mode": {"type": "string", "enum": ["MEAN_WEIGHTED", "MEAN", "BOUNDS"], "default": "MEAN_WEIGHTED"},
    },
    "required": ["object_name"],
    "additionalProperties": False,
}

MESH_LOOP_TOOLS_CIRCLE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "operation": {"type": "string", "enum": ["CIRCLE", "FLATTEN", "SPACE", "CURVE"]},
        "influence": {"type": "number", "minimum": 0, "maximum": 1, "default": 1.0},
        "interpolation": {"type": "string", "enum": ["LINEAR", "CUBIC"], "default": "LINEAR"},
    },
    "required": ["object_name", "operation"],
    "additionalProperties": False,
}

MESH_SYMMETRIZE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "direction": {
            "type": "string",
            "enum": ["NEGATIVE_X", "POSITIVE_X", "NEGATIVE_Y", "POSITIVE_Y", "NEGATIVE_Z", "POSITIVE_Z"],
        },
        "threshold": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.001},
        "use_topology": {"type": "boolean", "default": False},
    },
    "required": ["object_name", "direction"],
    "additionalProperties": False,
}

MESH_KNIFE_PROJECT_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "target_object": {"type": "string"},
        "cutter_objects": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "cut_through": {"type": "boolean", "default": True},
        "use_occlude_geometry": {"type": "boolean", "default": False},
    },
    "required": ["target_object", "cutter_objects"],
    "additionalProperties": False,
}

# UV & materials
UV_PACK_ISLANDS_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "margin": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.02},
        "rotate": {"type": "boolean", "default": True},
        "rotate_method": {"type": "string", "enum": ["ANY", "AXIS_ALIGNED", "CARDINAL"], "default": "ANY"},
        "shape_method": {"type": "string", "enum": ["AABB", "CONVEX"], "default": "AABB"},
        "merge_overlap": {"type": "boolean", "default": False},
        "scale": {"type": "boolean", "default": True},
        "target_udim": {"type": "integer", "default": 1001},
    },
    "required": ["object_name"],
    "additionalProperties": False,
}

MATERIAL_ASSIGN_FIXED_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "material_name": {"type": "string"},
        "slot_index": {"anyOf": [{"type": "integer"}, {"type": "null"}], "default": None},
        "assign_to_selection": {"type": "boolean", "default": True},
        "create_slot_if_missing": {"type": "boolean", "default": True},
    },
    "required": ["object_name", "material_name"],
    "additionalProperties": False,
}

# Measurement & alignment
MESH_MEASURE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "measure_type": {"type": "string", "enum": ["LENGTH", "AREA", "VOLUME", "DISTANCE"]},
        "selection_only": {"type": "boolean", "default": True},
        "unit_system": {"type": "string", "enum": ["METRIC", "IMPERIAL", "NONE"], "default": "NONE"},
    },
    "required": ["object_name", "measure_type"],
    "additionalProperties": False,
}

MESH_ALIGN_SELECTION_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "axis": {"type": "string", "enum": ["X", "Y", "Z"]},
        "align_mode": {"type": "string", "enum": ["MIN", "MAX", "CENTER", "CURSOR", "VALUE"]},
        "value": {"type": "number", "default": 0.0},
        "use_local": {"type": "boolean", "default": False},
    },
    "required": ["object_name", "axis", "align_mode"],
    "additionalProperties": False,
}

MESH_DISTRIBUTE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "axis": {"type": "string", "enum": ["X", "Y", "Z"]},
        "distribution": {"type": "string", "enum": ["EVEN", "LINEAR", "SURFACE"]},
        "spacing": {"type": "number", "default": 0.5},
        "start_offset": {"type": "number", "default": 0.0},
        "end_offset": {"type": "number", "default": 0.0},
    },
    "required": ["object_name", "axis", "distribution"],
    "additionalProperties": False,
}

# Cleanup & optimization
MESH_CLEANUP_COMPLETE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "operations": {
            "type": "object",
            "properties": {
                "remove_doubles": {"type": "boolean", "default": True},
                "merge_threshold": {"type": "number", "default": 0.0001},
                "delete_loose": {"type": "boolean", "default": True},
                "delete_degenerate": {"type": "boolean", "default": True},
                "dissolve_degenerate": {"type": "boolean", "default": True},
                "recalculate_normals": {"type": "boolean", "default": True},
                "make_planar_faces": {"type": "boolean", "default": False},
                "planar_threshold": {"type": "number", "default": 0.001},
                "delete_interior_faces": {"type": "boolean", "default": False},
                "split_non_planar": {"type": "boolean", "default": False},
            },
            "default": {},
        },
        "report_changes": {"type": "boolean", "default": True},
    },
    "required": ["object_name"],
    "additionalProperties": False,
}

MESH_DECIMATE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "ratio": {"type": "number", "minimum": 0.0, "maximum": 1.0, "default": 0.5},
        "method": {"type": "string", "enum": ["COLLAPSE", "UNSUBDIVIDE", "PLANAR"], "default": "COLLAPSE"},
        "triangulate": {"type": "boolean", "default": False},
        "use_symmetry": {"type": "boolean", "default": False},
        "symmetry_axis": {"type": "string", "enum": ["X", "Y", "Z"], "default": "X"},
    },
    "required": ["object_name"],
    "additionalProperties": False,
}

MESH_REMESH_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "mode": {"type": "string", "enum": ["VOXEL", "QUAD", "SHARP"], "default": "VOXEL"},
        "voxel_size": {"type": "number", "default": 0.05},
        "adaptivity": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.0},
        "smooth_normals": {"type": "boolean", "default": True},
        "preserve_sharp": {"type": "boolean", "default": True},
        "preserve_boundary": {"type": "boolean", "default": True},
    },
    "required": ["object_name"],
    "additionalProperties": False,
}

# Curves
CURVE_FROM_VERTICES_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "source_object": {"type": "string"},
        "vertices": {
            "anyOf": [
                {"type": "string", "enum": ["SELECTED"]},
                {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 3,
                    },
                },
            ]
        },
        "curve_name": {"type": "string", "default": "ProfileCurve"},
        "curve_type": {"type": "string", "enum": ["BEZIER", "NURBS", "POLY"], "default": "BEZIER"},
        "cyclic": {"type": "boolean", "default": False},
        "resolution": {"type": "integer", "default": 12},
        "handle_type": {"type": "string", "enum": ["AUTO", "VECTOR", "ALIGNED"], "default": "AUTO"},
    },
    "required": ["source_object", "vertices"],
    "additionalProperties": False,
}

CURVE_TO_MESH_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "curve_name": {"type": "string"},
        "extrude": {"type": "number", "default": 0.1},
        "bevel_depth": {"type": "number", "default": 0.05},
        "bevel_resolution": {"type": "integer", "minimum": 0, "maximum": 16, "default": 4},
        "use_fill_caps": {"type": "boolean", "default": True},
        "resolution_u": {"type": "integer", "default": 12},
        "resolution_v": {"type": "integer", "default": 4},
    },
    "required": ["curve_name"],
    "additionalProperties": False,
}

# Batch ops
BATCH_OPERATION_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "objects": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "operation": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["transform", "material", "modifier", "parent"]},
                "transform": {
                    "type": "object",
                    "properties": {
                        "move": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [0, 0, 0]},
                        "rotate": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [0, 0, 0]},
                        "scale": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [1, 1, 1]},
                    },
                    "default": {},
                },
                "material": {"type": "string"},
                "modifier": {"type": "object", "additionalProperties": True},
                "parent": {"type": "string"},
            },
            "required": ["type"],
            "additionalProperties": False,
        },
        "individual_origins": {"type": "boolean", "default": True},
    },
    "required": ["objects", "operation"],
    "additionalProperties": False,
}

# Vision / validation tools
SCENE_QUERY_COMPLETE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "include_geometry": {"type": "boolean", "default": True},
        "include_transforms": {"type": "boolean", "default": True},
        "include_topology": {"type": "boolean", "default": False},
        "max_objects": {"type": "integer", "minimum": 1, "maximum": 2000, "default": 200},
    },
    "required": [],
    "additionalProperties": False,
}

SPATIAL_ANALYZE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_names": {
            "anyOf": [
                {"type": "array", "items": {"type": "string"}, "minItems": 1},
                {"type": "null"},
            ],
            "default": None,
        },
        "queries": {
            "type": "array",
            "items": {"enum": ["distances", "alignments", "overlaps", "gaps", "grid_snaps"]},
            "default": ["distances", "alignments", "grid_snaps"],
        },
        "tolerance": {"type": "number", "default": 0.001},
        "grid_size": {"type": "number", "default": 0.1},
    },
    "required": [],
    "additionalProperties": False,
}

TOPOLOGY_VALIDATE_COMPLETE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "checks": {
            "type": "array",
            "items": {"enum": ["manifold", "watertight", "ngons", "triangles", "poles", "loose", "degenerate"]},
            "default": ["manifold", "watertight", "ngons", "poles", "loose"],
        },
        "report_indices": {"type": "boolean", "default": True},
        "max_indices": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 10},
    },
    "required": ["object_name"],
    "additionalProperties": False,
}

MEASURE_BATCH_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "measurements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"enum": ["DISTANCE", "VOLUME", "AREA", "ANGLE", "ALIGNMENT"]},
                    "from": {"type": "object"},
                    "to": {"type": "object"},
                    "object": {"type": "string"},
                    "faces": {"type": "array"},
                    "objects": {"type": "array"},
                    "axis": {"enum": ["X", "Y", "Z"]},
                    "tolerance": {"type": "number"},
                    "constraint": {"enum": ["X_AXIS_ONLY", "Y_AXIS_ONLY", "Z_AXIS_ONLY"]},
                },
                "required": ["type"],
                "additionalProperties": True,
            },
            "default": [],
        }
    },
    "required": ["measurements"],
    "additionalProperties": False,
}

VALIDATE_OPERATION_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "expectations": {
            "type": "object",
            "properties": {
                "manifold": {"type": "boolean"},
                "watertight": {"type": "boolean"},
                "no_ngons": {"type": "boolean"},
                "no_tris": {"type": "boolean"},
                "symmetry": {
                    "type": "object",
                    "properties": {
                        "axis": {"enum": ["X", "Y", "Z"]},
                        "tolerance": {"type": "number", "default": 0.001},
                    },
                    "required": ["axis"],
                    "additionalProperties": False,
                },
                "alignment": {
                    "type": "object",
                    "properties": {
                        "grid": {"type": "number"},
                        "objects": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": False,
                },
                "min_face_area": {"type": "number"},
                "max_edge_angle": {"type": "number"},
            },
            "default": {},
            "additionalProperties": False,
        },
        "auto_fix": {"type": "boolean", "default": False},
    },
    "required": ["object_name"],
    "additionalProperties": False,
}
