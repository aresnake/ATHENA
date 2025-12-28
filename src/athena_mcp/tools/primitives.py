from __future__ import annotations

from typing import Any, Dict

JSONDict = Dict[str, Any]

LIST_OBJECTS_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {},
    "additionalProperties": False,
}

ADD_CUBE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "size": {"type": "number"},
    },
    "additionalProperties": False,
}

MOVE_OBJECT_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "location": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 3,
            "maxItems": 3,
        },
    },
    "required": ["name", "location"],
    "additionalProperties": False,
}

ADD_CYLINDER_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Name for the new cylinder object"},
        "vertices": {
            "type": "integer",
            "default": 32,
            "minimum": 3,
            "maximum": 512,
            "description": "Number of vertices in the base circle",
        },
        "radius": {
            "type": "number",
            "default": 1,
            "minimum": 0.001,
            "description": "Radius of the cylinder",
        },
        "depth": {
            "type": "number",
            "default": 2,
            "minimum": 0.001,
            "description": "Height/depth of the cylinder along Z axis",
        },
        "location": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 3,
            "maxItems": 3,
            "default": [0, 0, 0],
            "description": "Location [x, y, z] where to place the cylinder",
        },
        "end_fill_type": {
            "type": "string",
            "enum": ["NOTHING", "NGON", "TRIFAN"],
            "default": "NGON",
            "description": "Type of end cap fill",
        },
    },
    "additionalProperties": False,
}

ADD_SPHERE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Name for the new sphere object"},
        "radius": {
            "type": "number",
            "default": 1,
            "minimum": 0.001,
            "description": "Radius of the sphere",
        },
        "location": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 3,
            "maxItems": 3,
            "default": [0, 0, 0],
            "description": "Location [x, y, z] where to place the sphere",
        },
        "segments": {
            "type": "integer",
            "default": 32,
            "minimum": 3,
            "maximum": 512,
            "description": "Number of longitudinal segments",
        },
        "ring_count": {
            "type": "integer",
            "default": 16,
            "minimum": 3,
            "maximum": 512,
            "description": "Number of latitudinal rings",
        },
    },
    "additionalProperties": False,
}

ADD_CONE_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Name for the new cone object"},
        "depth": {
            "type": "number",
            "default": 2,
            "minimum": 0.001,
            "description": "Height/depth of the cone along Z axis",
        },
        "radius1": {
            "type": "number",
            "default": 1,
            "minimum": 0,
            "description": "Radius of the base circle",
        },
        "radius2": {
            "type": "number",
            "default": 0,
            "minimum": 0,
            "description": "Radius of the top circle (0.0 for pure cone, same as radius1 for cylinder)",
        },
        "location": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 3,
            "maxItems": 3,
            "default": [0, 0, 0],
            "description": "Location [x, y, z] where to place the cone",
        },
        "vertices": {
            "type": "integer",
            "default": 32,
            "maximum": 512,
            "minimum": 3,
            "description": "Number of vertices in the base circle",
        },
        "end_fill_type": {
            "enum": ["NOTHING", "NGON", "TRIFAN"],
            "type": "string",
            "default": "NGON",
            "description": "Type of end cap fill",
        },
    },
    "additionalProperties": False,
}

ADD_TORUS_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Name for the new torus object"},
        "location": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 3,
            "maxItems": 3,
            "default": [0, 0, 0],
            "description": "Location [x, y, z] where to place the torus",
        },
        "major_radius": {
            "type": "number",
            "default": 1,
            "minimum": 0.001,
            "description": "Radius from the origin to the center of the tube",
        },
        "minor_radius": {
            "type": "number",
            "default": 0.25,
            "minimum": 0.001,
            "description": "Radius of the tube cross-section",
        },
        "major_segments": {
            "type": "integer",
            "default": 48,
            "maximum": 512,
            "minimum": 3,
            "description": "Number of segments for the main ring",
        },
        "minor_segments": {
            "type": "integer",
            "default": 12,
            "maximum": 512,
            "minimum": 3,
            "description": "Number of segments for the tube cross-section",
        },
    },
    "additionalProperties": False,
}
