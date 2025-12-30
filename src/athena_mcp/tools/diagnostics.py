from __future__ import annotations

from typing import Any, Dict

JSONDict = Dict[str, Any]

CAPABILITIES_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {},
    "additionalProperties": False,
}

VALIDATE_TOOL_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {"name": {"type": "string"}},
    "required": ["name"],
    "additionalProperties": False,
}
