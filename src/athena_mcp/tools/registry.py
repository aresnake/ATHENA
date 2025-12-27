from __future__ import annotations

from typing import Dict, List

from ..mcp_core.bridge_client import bridge_request
from ..mcp_core.types import BridgeFunc, JSONDict, ToolDefinition, error_response, ok_response
from . import primitives

_bridge_request: BridgeFunc = bridge_request


def set_bridge_request(func: BridgeFunc) -> None:
    global _bridge_request
    _bridge_request = func


def _call_bridge(tool: str, args: JSONDict) -> JSONDict:
    return _bridge_request(tool, args)


def _tool_blender_list_objects(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-list-objects", args or {})


def _tool_blender_add_cube(args: JSONDict) -> JSONDict:
    payload = {"name": args.get("name") or "Cube"}
    if "size" in args:
        payload["size"] = args["size"]
    return _call_bridge("blender-add-cube", payload)


def _tool_blender_move_object(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-move-object", args or {})


TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="blender-list-objects",
        description="List object names in the current Blender scene.",
        input_schema=primitives.LIST_OBJECTS_SCHEMA,
        impl=_tool_blender_list_objects,
    ),
    ToolDefinition(
        name="blender-add-cube",
        description="Add a cube object to the scene.",
        input_schema=primitives.ADD_CUBE_SCHEMA,
        impl=_tool_blender_add_cube,
    ),
    ToolDefinition(
        name="blender-move-object",
        description="Move an object to a new location.",
        input_schema=primitives.MOVE_OBJECT_SCHEMA,
        impl=_tool_blender_move_object,
    ),
]


def list_tools() -> List[JSONDict]:
    return [tool.to_wire() for tool in TOOLS]


def call_tool(name: str, args: JSONDict) -> JSONDict:
    tool_lookup: Dict[str, ToolDefinition] = {tool.name: tool for tool in TOOLS}
    if name not in tool_lookup:
        return error_response(f"Unknown tool '{name}'", code="unknown_tool")
    response: JSONDict
    try:
        response = tool_lookup[name].impl(args or {})
    except Exception as exc:  # pragma: no cover - defensive
        return error_response(str(exc), code="bridge_error")

    if isinstance(response, dict) and "ok" in response:
        if response.get("ok"):
            return ok_response(result=response.get("result", {}))
        error_obj = response.get("error") or {}
        message = error_obj.get("message") if isinstance(error_obj, dict) else "bridge error"
        code = error_obj.get("code") if isinstance(error_obj, dict) else "bridge_error"
        details = error_obj.get("details") if isinstance(error_obj, dict) else {}
        if code == "bridge_tool_error":
            return error_response(message or "bridge tool error", code="bridge_tool_error", details=details or {})
        return error_response(message or "bridge error", code=code or "bridge_error", details=details or {})

    return ok_response(result=response)
