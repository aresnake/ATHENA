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
