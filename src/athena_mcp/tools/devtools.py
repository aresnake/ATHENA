from __future__ import annotations

from typing import Any, Dict

JSONDict = Dict[str, Any]

# Removed SUBMIT_TOOL_SPEC_SCHEMA - workflow obsolete with Claude Code

EXEC_PYTHON_SCHEMA: JSONDict = {
    "type": "object",
    "properties": {
        "code": {
            "type": "string",
            "description": "Python code to execute in Blender context (has access to bpy)",
        },
    },
    "required": ["code"],
    "additionalProperties": False,
}
