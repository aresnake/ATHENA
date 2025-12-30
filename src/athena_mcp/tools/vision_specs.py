from __future__ import annotations

from typing import Any, Dict, List

JSONDict = Dict[str, Any]

VIEW_ENUM: List[str] = ["FRONT", "RIGHT", "TOP", "ISO_FRONT_RIGHT", "LEFT", "BACK", "BOTTOM"]
RGBA_SCHEMA: JSONDict = {
    "type": "array",
    "items": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    "minItems": 4,
    "maxItems": 4,
}
VECTOR3_SCHEMA: JSONDict = {
    "type": "array",
    "items": {"type": "number"},
    "minItems": 3,
    "maxItems": 3,
}

VIEWPORT_DIFF_COMPARISON_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "before_snapshot": {"type": "object"},
        "before_screenshot": {
            "oneOf": [
                {"type": "string"},
                {"type": "object", "additionalProperties": {"type": "string"}},
            ]
        },
        "operation_description": {"type": "string"},
        "diff_mode": {"type": "string", "enum": ["overlay", "side_by_side", "split_view", "highlight_only"], "default": "overlay"},
        "highlight_color": RGBA_SCHEMA,
        "geometry_diff": {
            "type": "object",
            "properties": {
                "track_vertices": {"type": "boolean", "default": True},
                "track_edges": {"type": "boolean", "default": False},
                "track_faces": {"type": "boolean", "default": False},
                "threshold": {"type": "number", "default": 0.0001},
                "show_vectors": {"type": "boolean", "default": False},
                "vector_scale": {"type": "number", "default": 1.0},
            },
            "default": {},
            "additionalProperties": False,
        },
        "measurements": {
            "type": "object",
            "properties": {
                "show_distances": {"type": "boolean", "default": False},
                "show_volume_change": {"type": "boolean", "default": False},
                "show_area_change": {"type": "boolean", "default": False},
                "show_stats_overlay": {"type": "boolean", "default": False},
            },
            "default": {},
            "additionalProperties": False,
        },
        "views": {
            "type": "array",
            "items": {"type": "string", "enum": VIEW_ENUM},
            "default": ["FRONT", "RIGHT", "TOP", "ISO_FRONT_RIGHT"],
        },
        "resolution": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2, "default": [1920, 1080]},
        "output_format": {"type": "string", "enum": ["composite_grid", "separate_files", "annotated_only"], "default": "composite_grid"},
        "output_path": {"type": "string"},
    },
    "required": ["before_snapshot", "before_screenshot", "output_path"],
    "additionalProperties": False,
}

ANNOTATION_ITEM_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["arrow", "circle", "box", "text", "line", "highlight", "measurement"]},
        "position": VECTOR3_SCHEMA,
        "screen_position": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
        "content": {"type": "string"},
        "color": RGBA_SCHEMA,
        "size": {"type": "number"},
        "thickness": {"type": "number"},
        "style": {"type": "string", "enum": ["solid", "dashed", "dotted"]},
    },
    "required": ["type"],
    "additionalProperties": False,
}

VIEWPORT_ANNOTATE_MARKUP_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "screenshot_base": {"type": "string"},
        "annotations": {"type": "array", "items": ANNOTATION_ITEM_SCHEMA, "default": []},
        "auto_annotate": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "default": False},
                "detect_issues": {"type": "boolean", "default": False},
                "issues_to_detect": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["non_manifold", "ngons", "overlapping", "degenerate"]},
                    "default": [],
                },
                "label_elements": {"type": "boolean", "default": False},
                "show_normals": {"type": "boolean", "default": False},
                "show_measurements": {"type": "boolean", "default": False},
            },
            "default": {},
            "additionalProperties": False,
        },
        "visual_style": {
            "type": "object",
            "properties": {
                "font_size": {"type": "integer", "default": 16},
                "font_family": {"type": "string", "enum": ["sans-serif", "monospace"], "default": "sans-serif"},
                "background_opacity": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "arrow_head_size": {"type": "number"},
                "marker_size": {"type": "number"},
            },
            "default": {},
            "additionalProperties": False,
        },
        "views": {"type": "array", "items": {"type": "string", "enum": VIEW_ENUM}, "default": ["FRONT"]},
        "resolution": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
        "output_path": {"type": "string"},
        "return_annotation_data": {"type": "boolean", "default": False},
    },
    "required": ["object_name", "output_path"],
    "additionalProperties": False,
}

VALIDATE_OPERATION_VISUAL_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "operation": {
            "type": "object",
            "properties": {
                "tool_name": {"type": "string"},
                "parameters": {"type": "object", "default": {}},
                "description": {"type": "string"},
            },
            "required": ["tool_name"],
            "additionalProperties": False,
        },
        "validation": {
            "type": "object",
            "properties": {
                "geometry_checks": {"type": "boolean", "default": True},
                "topology_checks": {"type": "boolean", "default": True},
                "visual_diff": {"type": "boolean", "default": True},
                "expected_changes": {"type": "object"},
            },
            "default": {},
            "additionalProperties": False,
        },
        "expectations": {
            "type": "object",
            "properties": {
                "vertices_delta": {"type": "object"},
                "should_be_manifold": {"type": "boolean"},
                "should_be_watertight": {"type": "boolean"},
                "max_ngons": {"type": "integer"},
                "volume_change_percent": {"type": "object"},
            },
            "additionalProperties": False,
        },
        "capture_config": {
            "type": "object",
            "properties": {
                "views": {"type": "array", "items": {"type": "string", "enum": VIEW_ENUM}, "default": ["FRONT", "RIGHT"]},
                "resolution": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2, "default": [1920, 1080]},
                "shading_mode": {"type": "string", "enum": ["SOLID", "WIREFRAME", "MATERIAL", "RENDERED"]},
                "overlays": {"type": "object", "default": {}},
            },
            "required": ["views"],
            "additionalProperties": False,
        },
        "output_path": {"type": "string"},
        "generate_report": {"type": "boolean", "default": True},
        "fail_on_unexpected": {"type": "boolean", "default": False},
    },
    "required": ["operation", "capture_config", "output_path"],
    "additionalProperties": False,
}

VIEWPORT_SELECTION_ISOLATE_CAPTURE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "selection_mode": {"type": "string", "enum": ["VERT", "EDGE", "FACE", "OBJECT"]},
        "selection_indices": {"type": "array", "items": {"type": "integer"}, "default": []},
        "framing": {
            "type": "object",
            "properties": {
                "auto_frame": {"type": "boolean", "default": True},
                "padding_percent": {"type": "number", "default": 10.0},
                "fit_mode": {"type": "string", "enum": ["bbox", "selection_only"], "default": "bbox"},
            },
            "default": {},
            "additionalProperties": False,
        },
        "context_display": {
            "type": "object",
            "properties": {
                "show_unselected": {"type": "boolean", "default": False},
                "unselected_opacity": {"type": "number", "default": 0.2},
                "ghost_mode": {"type": "boolean", "default": False},
            },
            "default": {},
            "additionalProperties": False,
        },
        "views": {"type": "array", "items": {"type": "string", "enum": VIEW_ENUM}, "default": ["FRONT"]},
        "resolution": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2, "default": [1920, 1080]},
        "shading_mode": {"type": "string"},
        "output_path": {"type": "string"},
    },
    "required": ["object_name", "selection_mode", "views", "output_path"],
    "additionalProperties": False,
}

MEASUREMENT_ITEM_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["distance", "angle", "radius", "area", "perimeter"]},
        "points": {"type": "array", "items": VECTOR3_SCHEMA, "minItems": 1},
        "label": {"type": "string"},
        "precision": {"type": "integer", "default": 2},
        "unit": {"type": "string", "enum": ["m", "cm", "mm", "auto"], "default": "auto"},
        "color": RGBA_SCHEMA,
    },
    "required": ["type", "points"],
    "additionalProperties": False,
}

VIEWPORT_MEASUREMENT_OVERLAY_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "screenshot_base": {"type": "string"},
        "measurements": {"type": "array", "items": MEASUREMENT_ITEM_SCHEMA, "default": []},
        "auto_measurements": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "default": False},
                "bbox_dimensions": {"type": "boolean", "default": False},
                "edge_lengths": {"type": "boolean", "default": False},
                "face_areas": {"type": "boolean", "default": False},
                "angles_between_edges": {"type": "boolean", "default": False},
            },
            "default": {},
            "additionalProperties": False,
        },
        "visual_style": {
            "type": "object",
            "properties": {
                "line_thickness": {"type": "number"},
                "font_size": {"type": "integer"},
                "leader_lines": {"type": "boolean"},
                "background_box": {"type": "boolean"},
            },
            "default": {},
            "additionalProperties": False,
        },
        "views": {"type": "array", "items": {"type": "string", "enum": VIEW_ENUM}, "default": ["FRONT"]},
        "output_path": {"type": "string"},
    },
    "required": ["object_name", "output_path"],
    "additionalProperties": False,
}

VIEWPORT_COMPARE_MATRIX_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "states": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "label": {"type": "string"},
                    "snapshot": {"type": "object"},
                    "description": {"type": "string"},
                },
                "required": ["label", "snapshot"],
                "additionalProperties": False,
            },
            "minItems": 2,
        },
        "layout": {"type": "string", "enum": ["grid", "carousel", "overlay_sequence"], "default": "grid"},
        "views_per_state": {"type": "array", "items": {"type": "string", "enum": VIEW_ENUM}, "default": ["FRONT"]},
        "sync_settings": {
            "type": "object",
            "properties": {
                "sync_camera": {"type": "boolean", "default": True},
                "sync_shading": {"type": "boolean", "default": True},
                "sync_overlays": {"type": "boolean", "default": True},
            },
            "default": {},
            "additionalProperties": False,
        },
        "highlight_differences": {"type": "boolean", "default": True},
        "annotate_changes": {"type": "boolean", "default": False},
        "resolution": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2, "default": [1920, 1080]},
        "output_path": {"type": "string"},
    },
    "required": ["states", "output_path"],
    "additionalProperties": False,
}

VIEWPORT_GEOMETRY_HEATMAP_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "property": {
            "type": "string",
            "enum": ["curvature", "stretch", "distortion", "thickness", "slope", "edge_angle", "face_area"],
        },
        "color_ramp": {
            "type": "object",
            "properties": {
                "min_color": RGBA_SCHEMA,
                "max_color": RGBA_SCHEMA,
                "mid_color": RGBA_SCHEMA,
                "interpolation": {"type": "string", "enum": ["linear", "ease", "sharp"]},
            },
            "required": ["min_color", "max_color"],
            "additionalProperties": False,
        },
        "value_range": {
            "type": "object",
            "properties": {
                "auto": {"type": "boolean", "default": True},
                "min": {"type": "number"},
                "max": {"type": "number"},
                "clamp": {"type": "boolean", "default": False},
            },
            "default": {"auto": True},
            "additionalProperties": False,
        },
        "threshold_highlight": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "default": False},
                "value": {"type": "number"},
                "highlight_mode": {"type": "string", "enum": ["above", "below", "outside_range"]},
            },
            "default": {},
            "additionalProperties": False,
        },
        "legend": {
            "type": "object",
            "properties": {
                "show": {"type": "boolean", "default": False},
                "position": {"type": "string"},
                "format": {"type": "string"},
            },
            "default": {},
            "additionalProperties": False,
        },
        "views": {"type": "array", "items": {"type": "string", "enum": VIEW_ENUM}, "default": ["FRONT"]},
        "resolution": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2, "default": [1920, 1080]},
        "output_path": {"type": "string"},
    },
    "required": ["object_name", "property", "color_ramp", "output_path"],
    "additionalProperties": False,
}

VIEWPORT_CONTEXT_AWARE_CAPTURE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "intelligence": {
            "type": "object",
            "properties": {
                "auto_select_views": {"type": "boolean", "default": True},
                "auto_select_overlays": {"type": "boolean", "default": False},
                "auto_detect_issues": {"type": "boolean", "default": False},
                "focus_mode": {
                    "type": "string",
                    "enum": ["full_object", "selection", "problem_areas", "details"],
                    "default": "full_object",
                },
            },
            "default": {},
            "additionalProperties": False,
        },
        "quality_preset": {"type": "string", "enum": ["draft", "preview", "final"], "default": "preview"},
        "context_hints": {
            "type": "object",
            "properties": {
                "object_type": {"type": "string", "enum": ["mechanical", "organic", "architectural", "character"]},
                "modeling_stage": {"type": "string", "enum": ["blocking", "detailing", "finalizing"]},
                "purpose": {"type": "string", "enum": ["review", "presentation", "documentation", "debugging"]},
            },
            "default": {},
            "additionalProperties": False,
        },
        "output_path": {"type": "string"},
    },
    "required": ["object_name", "output_path"],
    "additionalProperties": False,
}

VIEWPORT_XRAY_SECTION_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "object_name": {"type": "string"},
        "section": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "default": False},
                "plane": {"type": "string", "enum": ["X", "Y", "Z", "CUSTOM"], "default": "X"},
                "custom_normal": VECTOR3_SCHEMA,
                "offset": {"type": "number", "default": 0.0},
                "show_cut_surface": {"type": "boolean", "default": True},
                "fill_cut": {"type": "boolean", "default": True},
            },
            "default": {},
            "additionalProperties": False,
        },
        "xray": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "default": False},
                "opacity": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "mode": {"type": "string", "enum": ["uniform", "depth_based"]},
            },
            "default": {},
            "additionalProperties": False,
        },
        "interior_display": {
            "type": "object",
            "properties": {
                "show": {"type": "boolean", "default": False},
                "different_color": {"type": "boolean", "default": False},
                "interior_color": RGBA_SCHEMA,
            },
            "default": {},
            "additionalProperties": False,
        },
        "views": {"type": "array", "items": {"type": "string", "enum": VIEW_ENUM}, "default": ["FRONT"]},
        "resolution": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2, "default": [1920, 1080]},
        "output_path": {"type": "string"},
    },
    "required": ["object_name", "views", "output_path"],
    "additionalProperties": False,
}

