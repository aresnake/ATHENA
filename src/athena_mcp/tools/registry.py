from __future__ import annotations

from typing import Dict, List

from ..mcp_core.bridge_client import bridge_request
from ..mcp_core.types import BridgeFunc, JSONDict, ToolDefinition, error_response, ok_response
from . import mesh_edit, primitives

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


def _tool_blender_set_mode(args: JSONDict) -> JSONDict:
    payload = {"mode": args.get("mode")}
    if "name" in args:
        payload["name"] = args.get("name")
    return _call_bridge("blender-set-mode", payload)


def _tool_blender_set_selection_mode(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-set-selection-mode", {"mode": args.get("mode")})


def _tool_blender_select_all(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-select-all", {})


def _tool_blender_select_none(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-select-none", {})


def _tool_blender_select_invert(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-select-invert", {})


def _tool_blender_mesh_delete(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-delete", {"type": args.get("type")})


def _tool_blender_mesh_extrude(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-extrude", {"x": args.get("x"), "y": args.get("y"), "z": args.get("z")})


def _tool_blender_mesh_inset(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-inset", {"thickness": args.get("thickness"), "depth": args.get("depth")})


def _tool_blender_mesh_loop_cut(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-loop-cut",
        {"cuts": args.get("cuts", 1), "smoothness": args.get("smoothness", 0.0)},
    )


def _tool_blender_mesh_bevel(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-bevel",
        {
            "offset": args.get("offset", 0.02),
            "segments": args.get("segments", 1),
            "profile": args.get("profile", 0.5),
        },
    )


def _tool_blender_mesh_subdivide(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-subdivide",
        {
            "cuts": args.get("cuts", 1),
            "smooth": args.get("smooth", 0.0),
        },
    )


def _tool_blender_mesh_merge(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-merge", {"type": args.get("type")})


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
    ToolDefinition(
        name="blender-set-mode",
        description="Set the active object's mode (OBJECT or EDIT).",
        input_schema=mesh_edit.SET_MODE_SCHEMA,
        impl=_tool_blender_set_mode,
    ),
    ToolDefinition(
        name="blender-set-selection-mode",
        description="Set mesh selection mode to VERT/EDGE/FACE.",
        input_schema=mesh_edit.SET_SELECTION_MODE_SCHEMA,
        impl=_tool_blender_set_selection_mode,
    ),
    ToolDefinition(
        name="blender-select-all",
        description="Select all elements in EDIT mode.",
        input_schema=mesh_edit.SELECT_ALL_SCHEMA,
        impl=_tool_blender_select_all,
    ),
    ToolDefinition(
        name="blender-select-none",
        description="Deselect all elements in EDIT mode.",
        input_schema=mesh_edit.SELECT_NONE_SCHEMA,
        impl=_tool_blender_select_none,
    ),
    ToolDefinition(
        name="blender-select-invert",
        description="Invert selection in EDIT mode.",
        input_schema=mesh_edit.SELECT_INVERT_SCHEMA,
        impl=_tool_blender_select_invert,
    ),
    ToolDefinition(
        name="blender-mesh-delete",
        description="Delete mesh components of the selected type.",
        input_schema=mesh_edit.MESH_DELETE_SCHEMA,
        impl=_tool_blender_mesh_delete,
    ),
    ToolDefinition(
        name="blender-mesh-extrude",
        description="Extrude current selection by a delta vector.",
        input_schema=mesh_edit.MESH_EXTRUDE_SCHEMA,
        impl=_tool_blender_mesh_extrude,
    ),
    ToolDefinition(
        name="blender-mesh-inset",
        description="Inset current selection by thickness.",
        input_schema=mesh_edit.MESH_INSET_SCHEMA,
        impl=_tool_blender_mesh_inset,
    ),
    ToolDefinition(
        name="blender-mesh-loop-cut",
        description="Create loop cuts on the mesh.",
        input_schema=mesh_edit.LOOP_CUT_SCHEMA,
        impl=_tool_blender_mesh_loop_cut,
    ),
    ToolDefinition(
        name="blender-mesh-bevel",
        description="Bevel current selection.",
        input_schema=mesh_edit.BEVEL_SCHEMA,
        impl=_tool_blender_mesh_bevel,
    ),
    ToolDefinition(
        name="blender-mesh-subdivide",
        description="Subdivide current selection.",
        input_schema=mesh_edit.SUBDIVIDE_SCHEMA,
        impl=_tool_blender_mesh_subdivide,
    ),
    ToolDefinition(
        name="blender-mesh-merge",
        description="Merge selection elements.",
        input_schema=mesh_edit.MERGE_SCHEMA,
        impl=_tool_blender_mesh_merge,
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
