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
    },
    "required": ["thickness"],
    "additionalProperties": False,
}
