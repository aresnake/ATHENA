from __future__ import annotations

from typing import Any, Dict

JSONDict = Dict[str, Any]

# Object ops
OBJECT_JOIN_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "target_name": {"type": "string"},
    },
    "required": [],
    "additionalProperties": False,
}

OBJECT_SEPARATE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "type": {"type": "string", "enum": ["SELECTED", "MATERIAL", "LOOSE"], "default": "SELECTED"},
    },
    "required": ["name"],
    "additionalProperties": False,
}

OBJECT_SHADE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "smooth": {"type": "boolean", "default": True},
    },
    "required": ["name"],
    "additionalProperties": False,
}

OBJECT_ROTATE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "angle": {"type": "number", "minimum": -360, "maximum": 360},
        "axis": {"type": "string", "enum": ["X", "Y", "Z"]},
        "pivot": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 3,
            "maxItems": 3,
        },
    },
    "required": ["name", "angle", "axis"],
    "additionalProperties": False,
}

OBJECT_MIRROR_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "axis": {"type": "string", "enum": ["X", "Y", "Z"]},
        "method": {"type": "string", "enum": ["SCALE", "GEOMETRY"], "default": "GEOMETRY"},
    },
    "required": ["name", "axis"],
    "additionalProperties": False,
}

OBJECT_SNAP_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "target": {"type": "string", "enum": ["GRID", "CURSOR", "OBJECT"]},
        "target_name": {"type": "string"},
        "grid_size": {"type": "number", "default": 1.0, "minimum": 0.001},
    },
    "required": ["name", "target"],
    "additionalProperties": False,
}

# Modifiers
MODIFIER_APPLY_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "modifier": {"type": "string"},
    },
    "required": ["name", "modifier"],
    "additionalProperties": False,
}

MODIFIER_MOVE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "modifier": {"type": "string"},
        "direction": {"type": "string", "enum": ["UP", "DOWN"]},
    },
    "required": ["name", "modifier", "direction"],
    "additionalProperties": False,
}

MODIFIER_REMOVE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "modifier": {"type": "string"},
    },
    "required": ["name", "modifier"],
    "additionalProperties": False,
}

# Mesh advanced
MESH_SPIN_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "steps": {"type": "integer", "default": 12, "minimum": 2, "maximum": 512},
        "angle": {"type": "number", "default": 360, "minimum": 0, "maximum": 360},
        "axis": {"type": "string", "enum": ["X", "Y", "Z"], "default": "Z"},
        "center": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 3,
            "maxItems": 3,
            "default": [0, 0, 0],
        },
    },
    "required": ["name"],
    "additionalProperties": False,
}

MESH_SCREW_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "steps": {"type": "integer", "default": 16, "minimum": 2, "maximum": 512},
        "turns": {"type": "integer", "default": 1, "minimum": 1, "maximum": 100},
        "axis": {"type": "string", "enum": ["X", "Y", "Z"], "default": "Z"},
    },
    "required": ["name"],
    "additionalProperties": False,
}

MESH_NORMALS_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "operation": {"type": "string", "enum": ["RECALCULATE", "FLIP"]},
        "inside": {"type": "boolean", "default": False},
    },
    "required": ["name", "operation"],
    "additionalProperties": False,
}

# Materials
MATERIAL_ASSIGN_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "material_name": {"type": "string"},
        "slot_index": {"type": "integer", "minimum": 0},
    },
    "required": ["name", "material_name"],
    "additionalProperties": False,
}

MATERIAL_CREATE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "color": {
            "type": "array",
            "items": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "minItems": 4,
            "maxItems": 4,
            "default": [0.8, 0.8, 0.8, 1.0],
        },
        "metallic": {"type": "number", "default": 0.0, "minimum": 0.0, "maximum": 1.0},
        "roughness": {"type": "number", "default": 0.5, "minimum": 0.0, "maximum": 1.0},
    },
    "required": ["name"],
    "additionalProperties": False,
}

# Curves
CURVE_PRIMITIVE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["BEZIER_CURVE", "BEZIER_CIRCLE", "NURBS_CURVE", "NURBS_CIRCLE"]},
        "location": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 3,
            "maxItems": 3,
            "default": [0, 0, 0],
        },
        "radius": {"type": "number", "default": 1.0, "minimum": 0.001},
        "name": {"type": "string"},
    },
    "required": ["type"],
    "additionalProperties": False,
}

CURVE_CONVERT_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "keep_original": {"type": "boolean", "default": False},
    },
    "required": ["name"],
    "additionalProperties": False,
}

# -----------------------------------------
# P0 batch - advanced transforms & misc
# -----------------------------------------

OBJECT_SCALE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Object name"},
        "sx": {"type": "number", "minimum": 0.001, "maximum": 1000, "description": "Scale X"},
        "sy": {"type": "number", "minimum": 0.001, "maximum": 1000, "description": "Scale Y"},
        "sz": {"type": "number", "minimum": 0.001, "maximum": 1000, "description": "Scale Z"},
        "uniform": {"type": "boolean", "default": False, "description": "If true, use sx for all axes"},
    },
    "required": ["name", "sx"],
    "additionalProperties": False,
}

OBJECT_APPLY_TRANSFORM_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Object name"},
        "location": {"type": "boolean", "default": False, "description": "Apply location"},
        "rotation": {"type": "boolean", "default": False, "description": "Apply rotation"},
        "scale": {"type": "boolean", "default": False, "description": "Apply scale"},
        "properties": {"type": "boolean", "default": False, "description": "Apply properties"},
    },
    "required": ["name"],
    "additionalProperties": False,
}

OBJECT_ORIGIN_SET_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Object name"},
        "type": {
            "type": "string",
            "enum": ["GEOMETRY", "CURSOR", "CENTER_MASS", "CENTER_VOLUME", "GEOMETRY_ORIGIN"],
            "description": "Origin operation",
        },
        "center": {"type": "string", "enum": ["MEDIAN", "BOUNDS"], "default": "MEDIAN"},
    },
    "required": ["name", "type"],
    "additionalProperties": False,
}

OBJECT_PARENT_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "child_name": {"type": "string", "description": "Child object"},
        "parent_name": {"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Parent (null to clear)"},
        "keep_transform": {"type": "boolean", "default": True, "description": "Keep world transform"},
        "type": {"type": "string", "enum": ["OBJECT", "BONE", "VERTEX", "VERTEX_TRI"], "default": "OBJECT"},
    },
    "required": ["child_name"],
    "additionalProperties": False,
}

OBJECT_CLEAR_TRANSFORM_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Object name"},
        "location": {"type": "boolean", "default": False, "description": "Reset location to (0,0,0)"},
        "rotation": {"type": "boolean", "default": False, "description": "Reset rotation to (0,0,0)"},
        "scale": {"type": "boolean", "default": False, "description": "Reset scale to (1,1,1)"},
        "delta": {"type": "boolean", "default": False, "description": "Clear delta transforms too"},
    },
    "required": ["name"],
    "additionalProperties": False,
}

MESH_ROTATE_SELECTION_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Mesh object name"},
        "angle": {"type": "number", "minimum": -360, "maximum": 360, "description": "Angle in degrees"},
        "axis": {"type": "string", "enum": ["X", "Y", "Z"], "description": "Axis of rotation"},
        "pivot": {
            "anyOf": [
                {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                {"type": "null"},
            ],
            "default": None,
        },
        "euler_xyz": {
            "anyOf": [
                {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                {"type": "null"},
            ],
            "default": None,
        },
    },
    "required": ["name"],
    "additionalProperties": False,
}

OBJECT_DUPLICATE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Source object name"},
        "new_name": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
        "linked": {"type": "boolean", "default": False},
        "offset": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 3,
            "maxItems": 3,
            "default": [0, 0, 0],
        },
        "collection": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
    },
    "required": ["name"],
    "additionalProperties": False,
}

# Modifiers (P0)
MODIFIER_ADD_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "modifier_name": {"type": "string"},
        "modifier_type": {
            "type": "string",
            "enum": [
                "ARRAY",
                "BEVEL",
                "BOOLEAN",
                "BUILD",
                "DECIMATE",
                "EDGE_SPLIT",
                "MASK",
                "MIRROR",
                "MULTIRES",
                "REMESH",
                "SCREW",
                "SKIN",
                "SOLIDIFY",
                "SUBSURF",
                "TRIANGULATE",
                "WELD",
                "ARMATURE",
                "CAST",
                "CURVE",
                "DISPLACE",
                "HOOK",
                "LAPLACIANDEFORM",
                "LATTICE",
                "MESH_DEFORM",
                "SHRINKWRAP",
                "SIMPLE_DEFORM",
                "SMOOTH",
                "CORRECTIVE_SMOOTH",
                "LAPLACIANSMOOTH",
                "SURFACE_DEFORM",
                "WARP",
                "WAVE",
                "CLOTH",
                "COLLISION",
                "DYNAMIC_PAINT",
                "EXPLODE",
                "FLUID",
                "OCEAN",
                "PARTICLE_INSTANCE",
                "PARTICLE_SYSTEM",
                "SOFT_BODY",
                "NODES",
            ],
        },
    },
    "required": ["name", "modifier_name", "modifier_type"],
    "additionalProperties": False,
}

MODIFIER_CONFIGURE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "modifier_name": {"type": "string"},
        "params": {"type": "object", "additionalProperties": True},
    },
    "required": ["name", "modifier_name", "params"],
    "additionalProperties": False,
}

MODIFIER_CONFIGURE_ARRAY_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "modifier_name": {"type": "string"},
        "pattern": {"type": "string", "enum": ["LINEAR", "CIRCULAR", "GRID", "CURVE_FIT", "CUSTOM"], "default": "LINEAR"},
        "count": {"type": "integer", "minimum": 1, "maximum": 10000, "default": 5},
        "offset": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 3,
            "maxItems": 3,
            "default": [1.2, 0.0, 0.0],
        },
        "grid_counts": {
            "type": "array",
            "items": {"type": "integer"},
            "minItems": 2,
            "maxItems": 2,
        },
        "use_merge": {"type": "boolean", "default": False},
        "merge_threshold": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.01},
        "offset_object": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "curve_object": {"anyOf": [{"type": "string"}, {"type": "null"}]},
    },
    "required": ["name", "modifier_name"],
    "additionalProperties": False,
}

MODIFIER_CONFIGURE_MIRROR_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Object name"},
        "modifier_name": {"type": "string", "description": "Mirror modifier name"},
        "use_axis": {
            "type": "array",
            "items": {"type": "boolean"},
            "minItems": 3,
            "maxItems": 3,
            "default": [True, False, False],
            "description": "Mirror axes [X,Y,Z]",
        },
        "use_bisect_axis": {
            "type": "array",
            "items": {"type": "boolean"},
            "minItems": 3,
            "maxItems": 3,
            "default": [False, False, False],
            "description": "Bisect axes [X,Y,Z]",
        },
        "use_bisect_flip_axis": {
            "type": "array",
            "items": {"type": "boolean"},
            "minItems": 3,
            "maxItems": 3,
            "default": [False, False, False],
            "description": "Bisect flip axes [X,Y,Z]",
        },
        "use_clip": {"type": "boolean", "default": True},
        "use_mirror_merge": {"type": "boolean", "default": True},
        "merge_threshold": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.001},
        "mirror_object": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
        "use_mirror_u": {"type": "boolean", "default": False},
        "use_mirror_v": {"type": "boolean", "default": False},
        "mirror_offset_u": {"type": "number", "default": 0.0},
        "mirror_offset_v": {"type": "number", "default": 0.0},
    },
    "required": ["name", "modifier_name"],
    "additionalProperties": False,
}

# Mesh fill/bridge/cleanup
MESH_BRIDGE_EDGE_LOOPS_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "number_cuts": {"type": "integer", "minimum": 0, "maximum": 1000, "default": 0},
        "interpolation": {"type": "string", "enum": ["LINEAR", "PATH", "SURFACE"], "default": "LINEAR"},
        "smoothness": {"type": "number", "minimum": 0, "maximum": 1, "default": 1.0},
        "profile_shape": {"type": "string", "enum": ["SMOOTH", "SPHERE", "ROOT", "SHARP", "LINEAR"], "default": "SMOOTH"},
        "profile_factor": {"type": "number", "minimum": -1000, "maximum": 1000, "default": 0.0},
        "twist_offset": {"type": "integer", "default": 0},
        "merge": {"type": "boolean", "default": False},
        "merge_threshold": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.001},
    },
    "required": ["name"],
    "additionalProperties": False,
}

MESH_FILL_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "use_beauty": {"type": "boolean", "default": True},
    },
    "required": ["name"],
    "additionalProperties": False,
}

MESH_GRID_FILL_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "span": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 1},
        "offset": {"type": "integer", "minimum": -1000, "maximum": 1000, "default": 0},
        "use_interp_simple": {"type": "boolean", "default": False},
    },
    "required": ["name"],
    "additionalProperties": False,
}

MESH_REMOVE_DOUBLES_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "threshold": {"type": "number", "minimum": 0.0, "maximum": 1.0, "default": 0.0001},
        "use_unselected": {"type": "boolean", "default": False},
    },
    "required": ["name"],
    "additionalProperties": False,
}

# Selection avancée (P0 suite)
MESH_SELECT_SIMILAR_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "type": {
            "type": "string",
            "enum": [
                "AREA",
                "PERIMETER",
                "NORMAL",
                "COPLANAR",
                "SIDES",
                "MATERIAL",
                "IMAGE",
                "SHAPE",
                "VGROUP",
                "CREASE",
                "BEVEL",
                "SEAM",
                "SHARP",
                "FREESTYLE_FACE",
                "FACE_MAP",
                "LENGTH",
                "DIRECTION",
            ],
        },
        "threshold": {"type": "number", "minimum": 0.0, "maximum": 1.0, "default": 0.01},
        "compare": {"type": "string", "enum": ["EQUAL", "GREATER", "LESS"], "default": "EQUAL"},
    },
    "required": ["name", "type"],
    "additionalProperties": False,
}

MESH_SELECT_BY_TRAIT_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "trait": {
            "type": "string",
            "enum": [
                "LOOSE_VERTS",
                "LOOSE_EDGES",
                "LOOSE_FACES",
                "BOUNDARY_EDGES",
                "BOUNDARY_VERTS",
                "NON_MANIFOLD_EDGES",
                "NON_MANIFOLD_VERTS",
                "TRIANGLES",
                "QUADS",
                "NGONS",
                "SHARP_EDGES",
                "INTERIOR_FACES",
            ],
        },
        "threshold": {"type": "number", "minimum": 0, "maximum": 3.14159, "default": 0.523599},
        "extend": {"type": "boolean", "default": False},
    },
    "required": ["name", "trait"],
    "additionalProperties": False,
}

MESH_SELECT_NTH_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "nth": {"type": "integer", "minimum": 1, "maximum": 10000, "default": 2},
        "skip": {"type": "integer", "minimum": 0, "maximum": 10000, "default": 0},
        "offset": {"type": "integer", "minimum": 0, "maximum": 10000, "default": 0},
    },
    "required": ["name"],
    "additionalProperties": False,
}

MESH_SELECT_RANDOM_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "ratio": {"type": "number", "minimum": 0.0, "maximum": 1.0, "default": 0.5},
        "seed": {"type": "integer", "minimum": 0, "default": 0},
        "action": {"type": "string", "enum": ["SELECT", "DESELECT"], "default": "SELECT"},
    },
    "required": ["name"],
    "additionalProperties": False,
}

MESH_SELECT_FACE_BY_SIDES_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "type": {"type": "string", "enum": ["TRIANGLES", "QUADS", "NGONS", "CUSTOM"]},
        "sides": {"type": "integer", "minimum": 3, "maximum": 100},
        "min_sides": {"type": "integer", "minimum": 3, "maximum": 100},
        "max_sides": {"type": "integer", "minimum": 3, "maximum": 100},
        "extend": {"type": "boolean", "default": False},
    },
    "required": ["name", "type"],
    "additionalProperties": False,
}

# UV - Unwrap & projections (P0)
UV_UNWRAP_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "method": {"type": "string", "enum": ["ANGLE_BASED", "CONFORMAL"], "default": "ANGLE_BASED"},
        "fill_holes": {"type": "boolean", "default": True},
        "correct_aspect": {"type": "boolean", "default": True},
        "use_subsurf_data": {"type": "boolean", "default": False},
        "margin": {"type": "number", "minimum": 0.0, "maximum": 1.0, "default": 0.001},
    },
    "required": ["name"],
    "additionalProperties": False,
}

UV_SMART_PROJECT_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "angle_limit": {"type": "number", "minimum": 1.0, "maximum": 89.0, "default": 66.0},
        "island_margin": {"type": "number", "minimum": 0.0, "maximum": 1.0, "default": 0.02},
        "area_weight": {"type": "number", "minimum": 0.0, "maximum": 1.0, "default": 0.0},
        "correct_aspect": {"type": "boolean", "default": True},
        "scale_to_bounds": {"type": "boolean", "default": False},
    },
    "required": ["name"],
    "additionalProperties": False,
}

UV_CUBE_PROJECT_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "cube_size": {"type": "number", "minimum": 0.001, "maximum": 1000.0, "default": 2.0},
        "correct_aspect": {"type": "boolean", "default": True},
        "clip_to_bounds": {"type": "boolean", "default": False},
        "scale_to_bounds": {"type": "boolean", "default": False},
    },
    "required": ["name"],
    "additionalProperties": False,
}

UV_CYLINDER_PROJECT_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "direction": {
            "type": "string",
            "enum": ["VIEW_ON_EQUATOR", "VIEW_ON_POLES", "ALIGN_TO_OBJECT"],
            "default": "ALIGN_TO_OBJECT",
        },
        "align": {"type": "string", "enum": ["POLAR_ZX", "POLAR_ZY"], "default": "POLAR_ZX"},
        "radius": {"type": "number", "minimum": 0.001, "maximum": 1000.0, "default": 1.0},
        "correct_aspect": {"type": "boolean", "default": True},
        "clip_to_bounds": {"type": "boolean", "default": False},
        "scale_to_bounds": {"type": "boolean", "default": False},
    },
    "required": ["name"],
    "additionalProperties": False,
}

UV_SPHERE_PROJECT_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "direction": {
            "type": "string",
            "enum": ["VIEW_ON_EQUATOR", "VIEW_ON_POLES", "ALIGN_TO_OBJECT"],
            "default": "ALIGN_TO_OBJECT",
        },
        "align": {"type": "string", "enum": ["POLAR_ZX", "POLAR_ZY"], "default": "POLAR_ZX"},
        "correct_aspect": {"type": "boolean", "default": True},
        "clip_to_bounds": {"type": "boolean", "default": False},
        "scale_to_bounds": {"type": "boolean", "default": False},
    },
    "required": ["name"],
    "additionalProperties": False,
}

# Collections (P1)
COLLECTION_CREATE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Collection name"},
        "parent": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None, "description": "Parent collection name or null"},
        "hide_viewport": {"type": "boolean", "default": False},
        "hide_render": {"type": "boolean", "default": False},
        "hide_select": {"type": "boolean", "default": False},
    },
    "required": ["name"],
    "additionalProperties": False,
}

COLLECTION_ADD_OBJECTS_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "collection_name": {"type": "string", "description": "Target collection name"},
        "object_names": {"type": "array", "items": {"type": "string"}, "description": "Objects to add"},
        "move": {"type": "boolean", "default": True, "description": "Move (unlink from others) or instance"},
        "unlink_from": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None, "description": "Specific collection to unlink from"},
    },
    "required": ["collection_name", "object_names"],
    "additionalProperties": False,
}

COLLECTION_REMOVE_OBJECTS_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "collection_name": {"type": "string"},
        "object_names": {"type": "array", "items": {"type": "string"}},
        "delete_objects": {"type": "boolean", "default": False},
    },
    "required": ["collection_name", "object_names"],
    "additionalProperties": False,
}

COLLECTION_HIDE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "collection_name": {"type": "string"},
        "hide_viewport": {"anyOf": [{"type": "boolean"}, {"type": "null"}], "default": None},
        "hide_render": {"anyOf": [{"type": "boolean"}, {"type": "null"}], "default": None},
        "hide_select": {"anyOf": [{"type": "boolean"}, {"type": "null"}], "default": None},
        "recursive": {"type": "boolean", "default": False},
    },
    "required": ["collection_name"],
    "additionalProperties": False,
}

# Rename / IO
OBJECT_RENAME_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "old_name": {"type": "string", "description": "Current object name"},
        "new_name": {"type": "string", "description": "New object name"},
        "find": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
        "replace": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
        "prefix": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
        "suffix": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
        "rename_data": {"type": "boolean", "default": False, "description": "Also rename data block"},
    },
    "required": ["old_name"],
    "additionalProperties": False,
}

IMPORT_FILE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "filepath": {"type": "string", "description": "Absolute path to file"},
        "format": {
            "type": "string",
            "enum": ["OBJ", "FBX", "GLTF", "GLB", "STL", "PLY", "X3D", "COLLADA"],
            "description": "Optional explicit format; otherwise inferred from extension",
        },
        "forward_axis": {"type": "string", "enum": ["X", "Y", "Z", "-X", "-Y", "-Z"], "default": "Y"},
        "up_axis": {"type": "string", "enum": ["X", "Y", "Z", "-X", "-Y", "-Z"], "default": "Z"},
        "global_scale": {"type": "number", "minimum": 0.001, "maximum": 1000.0, "default": 1.0},
        "use_split_objects": {"type": "boolean", "default": True},
        "use_split_groups": {"type": "boolean", "default": False},
        "collection_name": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
    },
    "required": ["filepath"],
    "additionalProperties": False,
}

EXPORT_FILE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "filepath": {"type": "string", "description": "Absolute output path"},
        "format": {
            "type": "string",
            "enum": ["OBJ", "FBX", "GLTF", "GLB", "STL", "PLY", "USD"],
            "description": "Optional explicit format; otherwise inferred from extension",
        },
        "export_selected": {"type": "boolean", "default": False},
        "forward_axis": {"type": "string", "enum": ["X", "Y", "Z", "-X", "-Y", "-Z"], "default": "Y"},
        "up_axis": {"type": "string", "enum": ["X", "Y", "Z", "-X", "-Y", "-Z"], "default": "Z"},
        "global_scale": {"type": "number", "minimum": 0.001, "maximum": 1000.0, "default": 1.0},
        "apply_modifiers": {"type": "boolean", "default": True},
        "export_materials": {"type": "boolean", "default": True},
        "export_animations": {"type": "boolean", "default": True},
    },
    "required": ["filepath"],
    "additionalProperties": False,
}

# Mesh cleanup P1
MESH_RECALCULATE_NORMALS_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "inside": {"type": "boolean", "default": False, "description": "Recalculate normals inside"},
        "operation": {"type": "string", "enum": ["RECALCULATE", "FLIP"], "default": "RECALCULATE"},
    },
    "required": ["name"],
    "additionalProperties": False,
}

MESH_VALIDATE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "check_loose_verts": {"type": "boolean", "default": True},
        "check_loose_edges": {"type": "boolean", "default": True},
        "check_non_manifold": {"type": "boolean", "default": True},
        "check_degenerate": {"type": "boolean", "default": True},
        "check_doubles": {"type": "boolean", "default": True},
        "doubles_threshold": {"type": "number", "default": 0.0001, "minimum": 0},
    },
    "required": ["name"],
    "additionalProperties": False,
}

MESH_TRIANGULATE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "quad_method": {
            "type": "string",
            "enum": ["BEAUTY", "FIXED", "FIXED_ALTERNATE", "SHORTEST_DIAGONAL"],
            "default": "BEAUTY",
        },
        "ngon_method": {"type": "string", "enum": ["BEAUTY", "CLIP"], "default": "BEAUTY"},
        "keep_normals": {"type": "boolean", "default": False},
    },
    "required": ["name"],
    "additionalProperties": False,
}
