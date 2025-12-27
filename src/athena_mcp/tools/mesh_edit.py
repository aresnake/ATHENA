from __future__ import annotations

from typing import Any, Dict

JSONDict = Dict[str, Any]

SET_MODE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "mode": {"type": "string", "enum": ["OBJECT", "EDIT"]},
    },
    "required": ["mode"],
    "additionalProperties": False,
}

SET_SELECTION_MODE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "mode": {"type": "string", "enum": ["VERT", "EDGE", "FACE"]},
    },
    "required": ["mode"],
    "additionalProperties": False,
}

SELECT_ALL_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {},
    "additionalProperties": False,
}

SELECT_NONE_SCHEMA = SELECT_ALL_SCHEMA
SELECT_INVERT_SCHEMA = SELECT_ALL_SCHEMA

MESH_DELETE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["VERT", "EDGE", "FACE"]},
    },
    "required": ["type"],
    "additionalProperties": False,
}

MESH_EXTRUDE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "x": {"type": "number"},
        "y": {"type": "number"},
        "z": {"type": "number"},
    },
    "required": ["x", "y", "z"],
    "additionalProperties": False,
}

MESH_INSET_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "thickness": {"type": "number"},
        "depth": {"type": "number", "default": 0.0},
    },
    "required": ["thickness"],
    "additionalProperties": False,
}

LOOP_CUT_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "cuts": {"type": "integer", "minimum": 1, "default": 1},
        "smoothness": {"type": "number", "default": 0.0},
    },
    "additionalProperties": False,
}

BEVEL_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "offset": {"type": "number", "default": 0.02},
        "segments": {"type": "integer", "minimum": 1, "default": 1},
        "profile": {"type": "number", "default": 0.5},
    },
    "additionalProperties": False,
}

SUBDIVIDE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "cuts": {"type": "integer", "minimum": 1, "default": 1},
        "smooth": {"type": "number", "default": 0.0},
    },
    "additionalProperties": False,
}

MERGE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["CENTER", "CURSOR", "FIRST", "LAST"]},
    },
    "required": ["type"],
    "additionalProperties": False,
}

SELECT_LOOP_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "extend": {"type": "boolean", "default": False},
    },
    "additionalProperties": False,
}

SELECT_RING_SCHEMA = SELECT_LOOP_SCHEMA

SELECT_LINKED_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "delimit": {"type": "boolean", "default": False},
    },
    "additionalProperties": False,
}

SELECT_MORE_SCHEMA = SELECT_ALL_SCHEMA
SELECT_LESS_SCHEMA = SELECT_ALL_SCHEMA

SELECT_NON_MANIFOLD_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "extend": {"type": "boolean", "default": False},
    },
    "additionalProperties": False,
}

SELECT_BOUNDARY_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "extend": {"type": "boolean", "default": False},
    },
    "additionalProperties": False,
}

SELECT_BY_INDEX_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "element": {"type": "string", "enum": ["VERT", "EDGE", "FACE"]},
        "indices": {"type": "array", "items": {"type": "integer"}},
        "clear": {"type": "boolean", "default": True},
    },
    "required": ["element", "indices"],
    "additionalProperties": False,
}

CAPABILITIES_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {},
    "additionalProperties": False,
}

VALIDATE_TOOL_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
    },
    "required": ["name"],
    "additionalProperties": False,
}

SAFE_SET_SELECTION_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "element": {"type": "string", "enum": ["VERT", "EDGE", "FACE"]},
        "indices": {"type": "array", "items": {"type": "integer"}},
        "clear": {"type": "boolean", "default": True},
    },
    "required": ["element", "indices"],
    "additionalProperties": False,
}

SAFE_BISECT_PLANE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "plane_co": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
        "plane_no": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
        "clear_inner": {"type": "boolean", "default": False},
        "clear_outer": {"type": "boolean", "default": False},
    },
    "required": ["plane_co", "plane_no"],
    "additionalProperties": False,
}

SAFE_DELETE_BY_INDEX_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "element": {"type": "string", "enum": ["VERT", "EDGE", "FACE"]},
        "indices": {"type": "array", "items": {"type": "integer"}},
    },
    "required": ["element", "indices"],
    "additionalProperties": False,
}

TRANSLATE_SELECTION_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "dx": {"type": "number"},
        "dy": {"type": "number"},
        "dz": {"type": "number"},
    },
    "required": ["dx", "dy", "dz"],
    "additionalProperties": False,
}

SCALE_SELECTION_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "sx": {"type": "number"},
        "sy": {"type": "number"},
        "sz": {"type": "number"},
        "pivot": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
    },
    "required": ["sx", "sy", "sz"],
    "additionalProperties": False,
}

EXTRUDE_SELECTION_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "dx": {"type": "number"},
        "dy": {"type": "number"},
        "dz": {"type": "number"},
    },
    "required": ["dx", "dy", "dz"],
    "additionalProperties": False,
}

INSET_SELECTION_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "thickness": {"type": "number", "default": 0.05},
        "depth": {"type": "number", "default": 0.0},
    },
    "additionalProperties": False,
}

SELECT_BY_NORMAL_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "axis": {"type": "string", "enum": ["X", "Y", "Z"]},
        "sign": {"type": "integer", "enum": [1, -1], "default": 1},
        "threshold": {"type": "number", "default": 0.9},
        "extend": {"type": "boolean", "default": False},
    },
    "required": ["axis"],
    "additionalProperties": False,
}

DUPLICATE_SELECTION_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "dx": {"type": "number", "default": 0.0},
        "dy": {"type": "number", "default": 0.0},
        "dz": {"type": "number", "default": 0.0},
    },
    "additionalProperties": False,
}
