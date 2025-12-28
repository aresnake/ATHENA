from __future__ import annotations

from typing import Dict, List

from ..mcp_core.bridge_client import bridge_request
from .types import ToolDefinition
from ..mcp_core.types import BridgeFunc, JSONDict, error_response, ok_response
from . import devtools, mesh_edit, primitives

_bridge_request: BridgeFunc = bridge_request


def set_bridge_request(func: BridgeFunc) -> None:
    global _bridge_request
    _bridge_request = func


def _call_bridge(tool: str, args: JSONDict) -> JSONDict:
    return _bridge_request(tool, args)


def _tool_blender_list_objects(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-scene-list-objects", args or {})


def _tool_blender_add_cube(args: JSONDict) -> JSONDict:
    payload = {"name": args.get("name") or "Cube"}
    if "size" in args:
        payload["size"] = args["size"]
    return _call_bridge("blender-primitive-cube", payload)


def _tool_blender_add_cylinder(args: JSONDict) -> JSONDict:
    payload = {}
    if "name" in args:
        payload["name"] = args["name"]
    if "vertices" in args:
        payload["vertices"] = args["vertices"]
    if "radius" in args:
        payload["radius"] = args["radius"]
    if "depth" in args:
        payload["depth"] = args["depth"]
    if "location" in args:
        payload["location"] = args["location"]
    if "end_fill_type" in args:
        payload["end_fill_type"] = args["end_fill_type"]
    return _call_bridge("blender-primitive-cylinder", payload)


def _tool_blender_add_cone(args: JSONDict) -> JSONDict:
    payload = {}
    if "name" in args:
        payload["name"] = args["name"]
    if "depth" in args:
        payload["depth"] = args["depth"]
    if "radius1" in args:
        payload["radius1"] = args["radius1"]
    if "radius2" in args:
        payload["radius2"] = args["radius2"]
    if "location" in args:
        payload["location"] = args["location"]
    if "vertices" in args:
        payload["vertices"] = args["vertices"]
    if "end_fill_type" in args:
        payload["end_fill_type"] = args["end_fill_type"]
    return _call_bridge("blender-primitive-cone", payload)


def _tool_blender_add_torus(args: JSONDict) -> JSONDict:
    payload = {}
    if "name" in args:
        payload["name"] = args["name"]
    if "location" in args:
        payload["location"] = args["location"]
    if "major_radius" in args:
        payload["major_radius"] = args["major_radius"]
    if "minor_radius" in args:
        payload["minor_radius"] = args["minor_radius"]
    if "major_segments" in args:
        payload["major_segments"] = args["major_segments"]
    if "minor_segments" in args:
        payload["minor_segments"] = args["minor_segments"]
    return _call_bridge("blender-primitive-torus", payload)


def _tool_blender_add_sphere(args: JSONDict) -> JSONDict:
    payload = {}
    if "name" in args:
        payload["name"] = args["name"]
    if "radius" in args:
        payload["radius"] = args["radius"]
    if "location" in args:
        payload["location"] = args["location"]
    if "segments" in args:
        payload["segments"] = args["segments"]
    if "ring_count" in args:
        payload["ring_count"] = args["ring_count"]
    return _call_bridge("blender-primitive-sphere", payload)


def _tool_blender_move_object(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-object-move", args or {})


def _tool_blender_set_mode(args: JSONDict) -> JSONDict:
    payload = {"mode": args.get("mode")}
    if "name" in args:
        payload["name"] = args.get("name")
    return _call_bridge("blender-mode-set", payload)


def _tool_blender_set_selection_mode(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mode-selection-set", {"mode": args.get("mode")})


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


def _tool_blender_mesh_loop_cut(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-loop-cut",
        {"cuts": args.get("cuts", 1), "smoothness": args.get("smoothness", 0.0)},
    )


def _tool_blender_mesh_bevel(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-bevel",
        {"offset": args.get("offset", 0.02), "segments": args.get("segments", 1), "profile": args.get("profile", 0.5)},
    )


def _tool_blender_mesh_select_loop(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-select-loop", {"extend": bool(args.get("extend", False))})


def _tool_blender_mesh_select_ring(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-select-ring", {"extend": bool(args.get("extend", False))})


def _tool_blender_mesh_select_linked(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-select-linked", {"delimit": bool(args.get("delimit", False))})


def _tool_blender_mesh_select_more(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-select-more", {})


def _tool_blender_mesh_select_less(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-select-less", {})


def _tool_blender_mesh_select_non_manifold(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-select-non-manifold", {"extend": bool(args.get("extend", False))})


def _tool_blender_mesh_select_boundary(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-select-boundary", {"extend": bool(args.get("extend", False))})


def _tool_blender_mesh_select_by_index(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-select-by-index",
        {"element": args.get("element"), "indices": args.get("indices", []), "clear": bool(args.get("clear", True))},
    )


def _tool_blender_capabilities(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-diag-capabilities", {})


def _tool_blender_validate_tool(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-diag-validate-tool", {"name": args.get("name")})


def _tool_blender_mesh_set_selection(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-set-selection",
        {
            "element": args.get("element"),
            "indices": args.get("indices", []),
            "clear": bool(args.get("clear", True)),
        },
    )


def _tool_blender_mesh_bisect_plane(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-bisect-plane",
        {
            "plane_co": args.get("plane_co"),
            "plane_no": args.get("plane_no"),
            "clear_inner": bool(args.get("clear_inner", False)),
            "clear_outer": bool(args.get("clear_outer", False)),
        },
    )


def _tool_blender_mesh_delete_by_index(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-delete-by-index",
        {
            "element": args.get("element"),
            "indices": args.get("indices", []),
        },
    )


def _tool_blender_mesh_translate_selection(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-translate-selection",
        {"dx": args.get("dx"), "dy": args.get("dy"), "dz": args.get("dz")},
    )


def _tool_blender_mesh_scale_selection(args: JSONDict) -> JSONDict:
    payload = {
        "sx": args.get("sx"),
        "sy": args.get("sy"),
        "sz": args.get("sz"),
    }
    if "pivot" in args:
        payload["pivot"] = args.get("pivot")
    return _call_bridge("blender-mesh-scale-selection", payload)


def _tool_blender_mesh_extrude_selection(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-extrude-selection",
        {"dx": args.get("dx"), "dy": args.get("dy"), "dz": args.get("dz")},
    )


def _tool_blender_mesh_inset_selection(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-inset-selection",
        {"thickness": args.get("thickness", 0.05), "depth": args.get("depth", 0.0)},
    )


def _tool_blender_mesh_select_by_normal(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-select-by-normal",
        {
            "axis": args.get("axis"),
            "sign": args.get("sign", 1),
            "threshold": args.get("threshold", 0.9),
            "extend": bool(args.get("extend", False)),
        },
    )


def _tool_blender_mesh_duplicate_selection(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-duplicate-selection",
        {"dx": args.get("dx", 0.0), "dy": args.get("dy", 0.0), "dz": args.get("dz", 0.0)},
    )


def _tool_blender_scene_snapshot(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-diag-scene-snapshot",
        {
            "include_mesh_stats": args.get("include_mesh_stats", True),
            "include_materials": args.get("include_materials", True),
            "include_collections": args.get("include_collections", True),
            "max_objects": args.get("max_objects", 200),
            "max_materials_per_object": args.get("max_materials_per_object", 32),
            "max_items_per_list": args.get("max_items_per_list", 5000),
        },
    )


def _tool_blender_object_snapshot(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-diag-object-snapshot",
        {
            "name": args.get("name"),
            "include_mesh_stats": args.get("include_mesh_stats", True),
            "include_materials": args.get("include_materials", True),
            "include_modifiers": args.get("include_modifiers", True),
            "include_collections": args.get("include_collections", True),
            "max_items_per_list": args.get("max_items_per_list", 5000),
        },
    )


def _tool_exec_python(args: JSONDict) -> JSONDict:
    """Execute Python code in Blender (for API testing)."""
    return _call_bridge("blender-exec-python", {"code": args.get("code")})


TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="blender-scene-list-objects",
        description="List object names in the current Blender scene.",
        input_schema=primitives.LIST_OBJECTS_SCHEMA,
        impl=_tool_blender_list_objects,
        category="scene",
        tags=["query", "info"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-primitive-cube",
        description="Add a cube object to the scene.",
        input_schema=primitives.ADD_CUBE_SCHEMA,
        impl=_tool_blender_add_cube,
        category="primitives",
        tags=["create", "mesh"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-primitive-cylinder",
        description="Add a cylinder mesh primitive with customizable geometry parameters.",
        input_schema=primitives.ADD_CYLINDER_SCHEMA,
        impl=_tool_blender_add_cylinder,
        category="primitives",
        tags=["create", "mesh", "geometry"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-primitive-cone",
        description="Add a cone mesh primitive with customizable geometry parameters.",
        input_schema=primitives.ADD_CONE_SCHEMA,
        impl=_tool_blender_add_cone,
        category="primitives",
        tags=["create", "mesh", "geometry"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-primitive-torus",
        description="Add a torus mesh primitive with customizable geometry parameters.",
        input_schema=primitives.ADD_TORUS_SCHEMA,
        impl=_tool_blender_add_torus,
        category="primitives",
        tags=["create", "mesh", "geometry"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-object-move",
        description="Move an object to a new location.",
        input_schema=primitives.MOVE_OBJECT_SCHEMA,
        impl=_tool_blender_move_object,
        category="object",
        tags=["transform"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mode-set",
        description="Set the active object's mode (OBJECT or EDIT).",
        input_schema=mesh_edit.SET_MODE_SCHEMA,
        impl=_tool_blender_set_mode,
        category="mode",
        tags=["context"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mode-selection-set",
        description="Set mesh selection mode to VERT/EDGE/FACE.",
        input_schema=mesh_edit.SET_SELECTION_MODE_SCHEMA,
        impl=_tool_blender_set_selection_mode,
        category="mode",
        tags=["context"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-select-all",
        description="Select all elements in EDIT mode.",
        input_schema=mesh_edit.SELECT_ALL_SCHEMA,
        impl=_tool_blender_select_all,
        category="selection",
        tags=["select"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-select-none",
        description="Deselect all elements in EDIT mode.",
        input_schema=mesh_edit.SELECT_NONE_SCHEMA,
        impl=_tool_blender_select_none,
        category="selection",
        tags=["select"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-select-invert",
        description="Invert selection in EDIT mode.",
        input_schema=mesh_edit.SELECT_INVERT_SCHEMA,
        impl=_tool_blender_select_invert,
        category="selection",
        tags=["select"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-delete",
        description="Delete mesh components of the selected type.",
        input_schema=mesh_edit.MESH_DELETE_SCHEMA,
        impl=_tool_blender_mesh_delete,
        category="mesh",
        tags=["edit"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-extrude",
        description="Extrude current selection by a delta vector.",
        input_schema=mesh_edit.MESH_EXTRUDE_SCHEMA,
        impl=_tool_blender_mesh_extrude,
        category="mesh",
        tags=["edit", "geometry"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-inset",
        description="Inset current selection by thickness.",
        input_schema=mesh_edit.MESH_INSET_SCHEMA,
        impl=_tool_blender_mesh_inset,
        category="mesh",
        tags=["edit", "geometry"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-loop-cut",
        description="Create loop cuts on the mesh.",
        input_schema=mesh_edit.LOOP_CUT_SCHEMA,
        impl=_tool_blender_mesh_loop_cut,
        category="mesh",
        tags=["edit", "topology"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-bevel",
        description="Bevel current selection.",
        input_schema=mesh_edit.BEVEL_SCHEMA,
        impl=_tool_blender_mesh_bevel,
        category="mesh",
        tags=["edit", "geometry"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-subdivide",
        description="Subdivide current selection.",
        input_schema=mesh_edit.SUBDIVIDE_SCHEMA,
        impl=_tool_blender_mesh_subdivide,
        category="mesh",
        tags=["edit", "topology"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-merge",
        description="Merge selection elements.",
        input_schema=mesh_edit.MERGE_SCHEMA,
        impl=_tool_blender_mesh_merge,
        category="mesh",
        tags=["edit"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-select-loop",
        description="Select a loop of mesh elements.",
        input_schema=mesh_edit.SELECT_LOOP_SCHEMA,
        impl=_tool_blender_mesh_select_loop,
        category="mesh",
        tags=["select", "topology"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-select-ring",
        description="Select a ring of mesh elements.",
        input_schema=mesh_edit.SELECT_RING_SCHEMA,
        impl=_tool_blender_mesh_select_ring,
        category="mesh",
        tags=["select", "topology"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-select-linked",
        description="Select linked elements.",
        input_schema=mesh_edit.SELECT_LINKED_SCHEMA,
        impl=_tool_blender_mesh_select_linked,
        category="mesh",
        tags=["select"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-select-more",
        description="Grow selection.",
        input_schema=mesh_edit.SELECT_MORE_SCHEMA,
        impl=_tool_blender_mesh_select_more,
        category="mesh",
        tags=["select"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-select-less",
        description="Shrink selection.",
        input_schema=mesh_edit.SELECT_LESS_SCHEMA,
        impl=_tool_blender_mesh_select_less,
        category="mesh",
        tags=["select"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-select-non-manifold",
        description="Select non-manifold geometry.",
        input_schema=mesh_edit.SELECT_NON_MANIFOLD_SCHEMA,
        impl=_tool_blender_mesh_select_non_manifold,
        category="mesh",
        tags=["select"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-select-boundary",
        description="Select mesh boundary loop.",
        input_schema=mesh_edit.SELECT_BOUNDARY_SCHEMA,
        impl=_tool_blender_mesh_select_boundary,
        category="mesh",
        tags=["select"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-select-by-index",
        description="Select elements by indices.",
        input_schema=mesh_edit.SELECT_BY_INDEX_SCHEMA,
        impl=_tool_blender_mesh_select_by_index,
        category="mesh",
        tags=["select"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-diag-capabilities",
        description="Report Blender capabilities and operator availability.",
        input_schema=mesh_edit.CAPABILITIES_SCHEMA,
        impl=_tool_blender_capabilities,
        category="diag",
        tags=["info", "diagnostic"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-diag-validate-tool",
        description="Validate a tool name and classify execution requirements.",
        input_schema=mesh_edit.VALIDATE_TOOL_SCHEMA,
        impl=_tool_blender_validate_tool,
        category="diag",
        tags=["info", "diagnostic"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-set-selection",
        description="Data-first selection by indices for VERT/EDGE/FACE.",
        input_schema=mesh_edit.SAFE_SET_SELECTION_SCHEMA,
        impl=_tool_blender_mesh_set_selection,
        category="mesh",
        tags=["select"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-bisect-plane",
        description="Data-first bisect by plane with optional clearing.",
        input_schema=mesh_edit.SAFE_BISECT_PLANE_SCHEMA,
        impl=_tool_blender_mesh_bisect_plane,
        category="mesh",
        tags=["edit", "geometry"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-delete-by-index",
        description="Data-first delete elements by indices.",
        input_schema=mesh_edit.SAFE_DELETE_BY_INDEX_SCHEMA,
        impl=_tool_blender_mesh_delete_by_index,
        category="mesh",
        tags=["edit"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-translate-selection",
        description="Translate selected vertices via bmesh (SAFE-FIRST).",
        input_schema=mesh_edit.TRANSLATE_SELECTION_SCHEMA,
        impl=_tool_blender_mesh_translate_selection,
        category="mesh",
        tags=["transform"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-scale-selection",
        description="Scale selected vertices via bmesh (SAFE-FIRST).",
        input_schema=mesh_edit.SCALE_SELECTION_SCHEMA,
        impl=_tool_blender_mesh_scale_selection,
        category="mesh",
        tags=["transform"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-extrude-selection",
        description="Extrude selected geometry via bmesh (SAFE-FIRST).",
        input_schema=mesh_edit.EXTRUDE_SELECTION_SCHEMA,
        impl=_tool_blender_mesh_extrude_selection,
        category="mesh",
        tags=["edit", "geometry"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-inset-selection",
        description="Inset selected faces via bmesh (SAFE-FIRST).",
        input_schema=mesh_edit.INSET_SELECTION_SCHEMA,
        impl=_tool_blender_mesh_inset_selection,
        category="mesh",
        tags=["edit", "geometry"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-select-by-normal",
        description="Select faces by normal direction via bmesh (SAFE-FIRST).",
        input_schema=mesh_edit.SELECT_BY_NORMAL_SCHEMA,
        impl=_tool_blender_mesh_select_by_normal,
        category="mesh",
        tags=["select"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-duplicate-selection",
        description="Duplicate current selection via bmesh (SAFE-FIRST).",
        input_schema=mesh_edit.DUPLICATE_SELECTION_SCHEMA,
        impl=_tool_blender_mesh_duplicate_selection,
        category="mesh",
        tags=["edit"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-diag-scene-snapshot",
        description="SAFE-FIRST scene snapshot (no View3D).",
        input_schema=mesh_edit.SCENE_SNAPSHOT_SCHEMA,
        impl=_tool_blender_scene_snapshot,
        category="diag",
        tags=["info", "diagnostic"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-diag-object-snapshot",
        description="SAFE-FIRST object snapshot (no View3D).",
        input_schema=mesh_edit.OBJECT_SNAPSHOT_SCHEMA,
        impl=_tool_blender_object_snapshot,
        category="diag",
        tags=["info", "diagnostic"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-dev-exec-python",
        description="Execute Python code in Blender for API testing (has access to bpy).",
        input_schema=devtools.EXEC_PYTHON_SCHEMA,
        impl=_tool_exec_python,
        category="dev",
        tags=["diagnostic", "testing"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-primitive-sphere",
        description="Add a UV sphere mesh primitive with customizable geometry parameters (radius, segments, ring_count).",
        input_schema=primitives.ADD_SPHERE_SCHEMA,
        impl=_tool_blender_add_sphere,
        category="primitives",
        tags=["create", "mesh"],
        safety_level="safe-first",
    ),
]

# Build tool bank on module load
from .tool_bank import ToolBank

_TOOL_BANK = ToolBank(TOOLS)


# NEW: Discovery functions
def get_categories() -> List[str]:
    """Get all available tool categories."""
    return _TOOL_BANK.get_categories()


def get_tags() -> List[str]:
    """Get all available tags."""
    return _TOOL_BANK.get_tags()


def search_tools(query: str) -> List[JSONDict]:
    """Full-text search across tool names and descriptions."""
    return [tool.to_wire() for tool in _TOOL_BANK.search(query)]


def filter_tools(category: str = None, tags: List[str] = None) -> List[JSONDict]:
    """Filter tools by category or tags."""
    if category:
        tools = _TOOL_BANK.filter_by_category(category)
    elif tags:
        tools = _TOOL_BANK.filter_by_tags(*tags)
    else:
        tools = _TOOL_BANK.list_all()
    return [tool.to_wire() for tool in tools]


def list_tools() -> List[JSONDict]:
    return [tool.to_wire() for tool in TOOLS]


def call_tool(name: str, args: JSONDict) -> JSONDict:
    tool = _TOOL_BANK.get_tool(name)
    if not tool:
        return error_response(f"Unknown tool '{name}'", code="unknown_tool")
    response: JSONDict
    try:
        response = tool.impl(args or {})
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
