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
        "depth": {"type": "number"},
    },
    "required": ["thickness"],
    "additionalProperties": False,
}

LOOP_CUT_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "cuts": {"type": "integer", "minimum": 1},
        "smoothness": {"type": "number"},
    },
    "additionalProperties": False,
}

BEVEL_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "offset": {"type": "number"},
        "segments": {"type": "integer", "minimum": 1},
        "profile": {"type": "number"},
    },
    "additionalProperties": False,
}

SUBDIVIDE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "cuts": {"type": "integer", "minimum": 1},
        "smooth": {"type": "number"},
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
