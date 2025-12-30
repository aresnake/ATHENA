from __future__ import annotations

from typing import List

from ..mcp_core.bridge_client import bridge_request
from .types import ToolDefinition
from ..mcp_core.types import BridgeFunc, JSONDict, error_response, ok_response
from . import devtools, mesh_edit, primitives, object_ops, specs_v2, diagnostics, vision_specs

_bridge_request: BridgeFunc = bridge_request


def set_bridge_request(func: BridgeFunc) -> None:
    global _bridge_request
    _bridge_request = func


def _call_bridge(tool: str, args: JSONDict) -> JSONDict:
    """
    Dispatch a tool call to the Blender bridge with sanitized arguments.

    - Ensure args is always a dict (coerce falsy/None to {}).
    - Strip None values so the bridge never receives explicit nulls that can
      upset downstream JSON->Python->Blender parsing.
    """
    clean_args = _clean_args(args)
    return _bridge_request(tool, clean_args)


def _clean_args(args: JSONDict) -> JSONDict:
    """Drop None values to avoid sending nulls to the bridge."""
    return {k: v for k, v in (args or {}).items() if v is not None}


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


# Removed duplicate definitions that were identical to lines 153-168
# (mesh_loop_cut and mesh_bevel were defined twice)


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


def _tool_blender_diag_capabilities(args: JSONDict) -> JSONDict:
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

# New P0 transforms / modifiers
def _tool_blender_object_scale(args: JSONDict) -> JSONDict:
    payload = {
        "name": args.get("name"),
        "sx": args.get("sx"),
        "sy": args.get("sy"),
        "sz": args.get("sz"),
        "uniform": args.get("uniform", False),
    }
    return _call_bridge("blender-object-scale", payload)


def _tool_blender_object_apply_transform(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-object-apply-transform",
        {
            "name": args.get("name"),
            "location": args.get("location", False),
            "rotation": args.get("rotation", False),
            "scale": args.get("scale", False),
            "properties": args.get("properties", False),
        },
    )


def _tool_blender_object_origin_set(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-object-origin-set",
        {"name": args.get("name"), "type": args.get("type"), "center": args.get("center", "MEDIAN")},
    )


def _tool_blender_object_parent(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-object-parent",
        {
            "child_name": args.get("child_name"),
            "parent_name": args.get("parent_name"),
            "keep_transform": args.get("keep_transform", True),
            "type": args.get("type", "OBJECT"),
        },
    )


def _tool_blender_object_clear_transform(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-object-clear-transform",
        {
            "name": args.get("name"),
            "location": args.get("location", False),
            "rotation": args.get("rotation", False),
            "scale": args.get("scale", False),
            "delta": args.get("delta", False),
        },
    )


def _tool_blender_mesh_rotate_selection(args: JSONDict) -> JSONDict:
    payload = {
        "name": args.get("name"),
        "angle": args.get("angle"),
        "axis": args.get("axis"),
        "pivot": args.get("pivot"),
        "euler_xyz": args.get("euler_xyz"),
    }
    return _call_bridge("blender-mesh-rotate-selection", payload)


def _tool_blender_object_duplicate(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-object-duplicate",
        {
            "name": args.get("name"),
            "new_name": args.get("new_name"),
            "linked": args.get("linked", False),
            "offset": args.get("offset"),
            "collection": args.get("collection"),
        },
    )


def _tool_blender_modifier_add(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-modifier-add",
        {"name": args.get("name"), "modifier_name": args.get("modifier_name"), "modifier_type": args.get("modifier_type")},
    )


def _tool_blender_modifier_configure(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-modifier-configure",
        {"name": args.get("name"), "modifier_name": args.get("modifier_name"), "params": args.get("params", {})},
    )


def _tool_blender_modifier_configure_array(args: JSONDict) -> JSONDict:
    count = args.get("count", 5)
    offset = args.get("offset", [1.2, 0.0, 0.0])
    merge_threshold = args.get("merge_threshold", 0.01)
    return _call_bridge(
        "blender-modifier-configure-array",
        {
            "name": args.get("name"),
            "modifier_name": args.get("modifier_name"),
            "pattern": args.get("pattern", "LINEAR"),
            "count": count,
            "offset": offset,
            "grid_counts": args.get("grid_counts"),
            "use_merge": args.get("use_merge", False),
            "merge_threshold": merge_threshold,
            "offset_object": args.get("offset_object"),
            "curve_object": args.get("curve_object"),
        },
    )


def _tool_blender_modifier_configure_mirror(args: JSONDict) -> JSONDict:
    merge_threshold = args.get("merge_threshold", 0.001)
    mirror_offset_u = args.get("mirror_offset_u", 0.0)
    mirror_offset_v = args.get("mirror_offset_v", 0.0)
    use_clip = args.get("use_clip", True)
    use_mirror_merge = args.get("use_mirror_merge", True)
    return _call_bridge(
        "blender-modifier-configure-mirror",
        {
            "name": args.get("name"),
            "modifier_name": args.get("modifier_name"),
            "use_axis": args.get("use_axis"),
            "use_bisect_axis": args.get("use_bisect_axis"),
            "use_bisect_flip_axis": args.get("use_bisect_flip_axis"),
            "use_clip": use_clip,
            "use_mirror_merge": use_mirror_merge,
            "merge_threshold": merge_threshold,
            "mirror_object": args.get("mirror_object"),
            "use_mirror_u": args.get("use_mirror_u"),
            "use_mirror_v": args.get("use_mirror_v"),
            "mirror_offset_u": mirror_offset_u,
            "mirror_offset_v": mirror_offset_v,
        },
    )


def _tool_blender_mesh_bridge_edge_loops(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-bridge-edge-loops",
        {
            "name": args.get("name"),
            "number_cuts": args.get("number_cuts"),
            "interpolation": args.get("interpolation"),
            "smoothness": args.get("smoothness"),
            "profile_shape": args.get("profile_shape"),
            "profile_factor": args.get("profile_factor"),
            "twist_offset": args.get("twist_offset"),
            "merge": args.get("merge"),
            "merge_threshold": args.get("merge_threshold"),
        },
    )


def _tool_blender_mesh_fill(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-fill", {"name": args.get("name"), "use_beauty": args.get("use_beauty", True)})


def _tool_blender_mesh_grid_fill(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-grid-fill",
        {
            "name": args.get("name"),
            "span": args.get("span"),
            "offset": args.get("offset"),
            "use_interp_simple": args.get("use_interp_simple"),
        },
    )


def _tool_blender_mesh_remove_doubles(args: JSONDict) -> JSONDict:
    threshold = args.get("threshold", 0.0001)
    return _call_bridge(
        "blender-mesh-remove-doubles",
        {"name": args.get("name"), "threshold": threshold, "use_unselected": args.get("use_unselected")},
    )


def _tool_blender_mesh_select_similar(args: JSONDict) -> JSONDict:
    threshold = args.get("threshold", 0.01)
    compare = args.get("compare", "EQUAL")
    return _call_bridge(
        "blender-mesh-select-similar",
        {
            "name": args.get("name"),
            "type": args.get("type"),
            "threshold": threshold,
            "compare": compare,
        },
    )


def _tool_blender_mesh_select_by_trait(args: JSONDict) -> JSONDict:
    trait = args.get("trait")
    payload: JSONDict = {"name": args.get("name"), "trait": trait, "extend": args.get("extend", False)}
    if trait == "SHARP_EDGES":
        payload["threshold"] = args.get("threshold", 0.523599)
    elif trait not in ["NON_MANIFOLD_EDGES", "NON_MANIFOLD_VERTS"]:
        if args.get("threshold") is not None:
            payload["threshold"] = args.get("threshold")
    return _call_bridge("blender-mesh-select-by-trait", payload)


def _tool_blender_mesh_select_nth(args: JSONDict) -> JSONDict:
    nth = args.get("nth", 2)
    skip = args.get("skip", 0)
    offset = args.get("offset", 0)
    return _call_bridge(
        "blender-mesh-select-nth",
        {"name": args.get("name"), "nth": nth, "skip": skip, "offset": offset},
    )


def _tool_blender_mesh_select_random(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-select-random",
        {"name": args.get("name"), "ratio": args.get("ratio"), "seed": args.get("seed"), "action": args.get("action")},
    )


def _tool_blender_mesh_select_face_by_sides(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-select-face-by-sides",
        {
            "name": args.get("name"),
            "type": args.get("type"),
            "sides": args.get("sides"),
            "min_sides": args.get("min_sides"),
            "max_sides": args.get("max_sides"),
            "extend": args.get("extend", False),
        },
    )


def _tool_blender_uv_unwrap(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-uv-unwrap",
        {
            "name": args.get("name"),
            "method": args.get("method", "ANGLE_BASED"),
            "fill_holes": args.get("fill_holes", True),
            "correct_aspect": args.get("correct_aspect", True),
            "use_subsurf_data": args.get("use_subsurf_data", False),
            "margin": args.get("margin", 0.001),
        },
    )


def _tool_blender_uv_smart_project(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-uv-smart-project",
        {
            "name": args.get("name"),
            "angle_limit": args.get("angle_limit", 66.0),
            "island_margin": args.get("island_margin", 0.02),
            "area_weight": args.get("area_weight", 0.0),
            "correct_aspect": args.get("correct_aspect", True),
            "scale_to_bounds": args.get("scale_to_bounds", False),
        },
    )


def _tool_blender_uv_cube_project(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-uv-cube-project",
        {
            "name": args.get("name"),
            "cube_size": args.get("cube_size", 2.0),
            "correct_aspect": args.get("correct_aspect", True),
            "clip_to_bounds": args.get("clip_to_bounds", False),
            "scale_to_bounds": args.get("scale_to_bounds", False),
        },
    )


def _tool_blender_uv_cylinder_project(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-uv-cylinder-project",
        {
            "name": args.get("name"),
            "direction": args.get("direction", "ALIGN_TO_OBJECT"),
            "align": args.get("align", "POLAR_ZX"),
            "radius": args.get("radius", 1.0),
            "correct_aspect": args.get("correct_aspect", True),
            "clip_to_bounds": args.get("clip_to_bounds", False),
            "scale_to_bounds": args.get("scale_to_bounds", False),
        },
    )


def _tool_blender_uv_sphere_project(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-uv-sphere-project",
        {
            "name": args.get("name"),
            "direction": args.get("direction", "ALIGN_TO_OBJECT"),
            "align": args.get("align", "POLAR_ZX"),
            "correct_aspect": args.get("correct_aspect", True),
            "clip_to_bounds": args.get("clip_to_bounds", False),
            "scale_to_bounds": args.get("scale_to_bounds", False),
        },
    )


def _tool_blender_collection_create(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-collection-create",
        {
            "name": args.get("name"),
            "parent": args.get("parent"),
            "hide_viewport": bool(args.get("hide_viewport", False)),
            "hide_render": bool(args.get("hide_render", False)),
            "hide_select": bool(args.get("hide_select", False)),
        },
    )


def _tool_blender_collection_add_objects(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-collection-add-objects",
        {
            "collection_name": args.get("collection_name"),
            "object_names": args.get("object_names", []),
            "move": bool(args.get("move", True)),
            "unlink_from": args.get("unlink_from"),
        },
    )


def _tool_blender_collection_remove_objects(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-collection-remove-objects",
        {
            "collection_name": args.get("collection_name"),
            "object_names": args.get("object_names", []),
            "delete_objects": bool(args.get("delete_objects", False)),
        },
    )


def _tool_blender_collection_hide(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-collection-hide",
        {
            "collection_name": args.get("collection_name"),
            "hide_viewport": args.get("hide_viewport"),
            "hide_render": args.get("hide_render"),
            "hide_select": args.get("hide_select"),
            "recursive": bool(args.get("recursive", False)),
        },
    )


def _tool_blender_object_rename(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-object-rename",
        {
            "old_name": args.get("old_name"),
            "new_name": args.get("new_name"),
            "find": args.get("find"),
            "replace": args.get("replace"),
            "prefix": args.get("prefix"),
            "suffix": args.get("suffix"),
            "rename_data": bool(args.get("rename_data", False)),
        },
    )


def _tool_blender_import_file(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-import-file",
        {
            "filepath": args.get("filepath"),
            "format": args.get("format"),
            "forward_axis": args.get("forward_axis", "Y"),
            "up_axis": args.get("up_axis", "Z"),
            "global_scale": args.get("global_scale", 1.0),
            "use_split_objects": args.get("use_split_objects", True),
            "use_split_groups": args.get("use_split_groups", False),
            "collection_name": args.get("collection_name"),
        },
    )


def _tool_blender_export_file(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-export-file",
        {
            "filepath": args.get("filepath"),
            "format": args.get("format"),
            "export_selected": args.get("export_selected", False),
            "forward_axis": args.get("forward_axis", "Y"),
            "up_axis": args.get("up_axis", "Z"),
            "global_scale": args.get("global_scale", 1.0),
            "apply_modifiers": args.get("apply_modifiers", True),
            "export_materials": args.get("export_materials", True),
            "export_animations": args.get("export_animations", True),
        },
    )


def _tool_blender_mesh_recalculate_normals(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-recalculate-normals",
        {"name": args.get("name"), "inside": args.get("inside", False), "operation": args.get("operation", "RECALCULATE")},
    )


def _tool_blender_mesh_validate(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-validate",
        {
            "name": args.get("name"),
            "check_loose_verts": args.get("check_loose_verts", True),
            "check_loose_edges": args.get("check_loose_edges", True),
            "check_non_manifold": args.get("check_non_manifold", True),
            "check_degenerate": args.get("check_degenerate", True),
            "check_doubles": args.get("check_doubles", True),
            "doubles_threshold": args.get("doubles_threshold", 0.0001),
        },
    )


def _tool_blender_mesh_triangulate(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-triangulate",
        {
            "name": args.get("name"),
            "quad_method": args.get("quad_method", "BEAUTY"),
            "ngon_method": args.get("ngon_method", "BEAUTY"),
            "keep_normals": args.get("keep_normals", False),
        },
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


# New tools (object ops, transforms, modifiers, mesh advanced, materials, curves)
def _tool_blender_object_join(args: JSONDict) -> JSONDict:
    payload = {}
    if "target_name" in args:
        payload["target_name"] = args.get("target_name")
    return _call_bridge("blender-object-join", payload)


def _tool_blender_object_separate(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-object-separate", {"name": args.get("name"), "type": args.get("type", "SELECTED")})


def _tool_blender_object_shade(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-object-shade", {"name": args.get("name"), "smooth": args.get("smooth", True)})


def _tool_blender_object_rotate(args: JSONDict) -> JSONDict:
    payload = {
        "name": args.get("name"),
        "angle": args.get("angle"),
        "axis": args.get("axis"),
    }
    if "pivot" in args:
        payload["pivot"] = args.get("pivot")
    return _call_bridge("blender-object-rotate", payload)


def _tool_blender_object_mirror(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-object-mirror",
        {"name": args.get("name"), "axis": args.get("axis"), "method": args.get("method", "GEOMETRY")},
    )


def _tool_blender_object_snap(args: JSONDict) -> JSONDict:
    payload = {
        "name": args.get("name"),
        "target": args.get("target"),
        "target_name": args.get("target_name"),
        "grid_size": args.get("grid_size", 1.0),
    }
    return _call_bridge("blender-object-snap", payload)


def _tool_blender_modifier_apply(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-modifier-apply", {"name": args.get("name"), "modifier": args.get("modifier")})


def _tool_blender_modifier_move(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-modifier-move",
        {"name": args.get("name"), "modifier": args.get("modifier"), "direction": args.get("direction")},
    )


def _tool_blender_modifier_remove(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-modifier-remove", {"name": args.get("name"), "modifier": args.get("modifier")})


def _tool_blender_mesh_spin(args: JSONDict) -> JSONDict:
    payload = {
        "name": args.get("name"),
        "steps": args.get("steps", 12),
        "angle": args.get("angle", 360),
        "axis": args.get("axis", "Z"),
        "center": args.get("center", [0, 0, 0]),
    }
    return _call_bridge("blender-mesh-spin", payload)


def _tool_blender_mesh_screw(args: JSONDict) -> JSONDict:
    payload = {
        "name": args.get("name"),
        "steps": args.get("steps", 16),
        "turns": args.get("turns", 1),
        "axis": args.get("axis", "Z"),
    }
    return _call_bridge("blender-mesh-screw", payload)


def _tool_blender_mesh_normals(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-mesh-normals",
        {"name": args.get("name"), "operation": args.get("operation"), "inside": args.get("inside", False)},
    )


def _tool_blender_material_assign(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-material-assign",
        {
            "name": args.get("name"),
            "material_name": args.get("material_name"),
            "slot_index": args.get("slot_index"),
        },
    )


def _tool_blender_material_create(args: JSONDict) -> JSONDict:
    color = args.get("color", [0.8, 0.8, 0.8, 1.0])
    metallic = args.get("metallic", 0.0)
    roughness = args.get("roughness", 0.5)
    return _call_bridge(
        "blender-material-create",
        {
            "name": args.get("name"),
            "color": color,
            "metallic": metallic,
            "roughness": roughness,
        },
    )


def _tool_blender_curve_primitive(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-curve-primitive",
        {
            "type": args.get("type"),
            "location": args.get("location"),
            "radius": args.get("radius"),
            "name": args.get("name"),
        },
    )


def _tool_blender_curve_convert(args: JSONDict) -> JSONDict:
    return _call_bridge(
        "blender-curve-convert",
        {
            "name": args.get("name"),
            "keep_original": args.get("keep_original", False),
        },
    )


# V2 tools (spec finale)
def _tool_blender_viewport_screenshot_complete(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-viewport-screenshot-complete", _clean_args(args))


def _tool_blender_viewport_render_modes(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-viewport-render-modes", _clean_args(args))


def _tool_blender_mesh_query_geometry(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-query-geometry", _clean_args(args))


def _tool_blender_mesh_query_selection(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-query-selection", _clean_args(args))


def _tool_blender_mesh_query_topology(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-query-topology", _clean_args(args))


def _tool_blender_mesh_analyze_quality(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-analyze-quality", _clean_args(args))


def _tool_blender_mesh_select_by_position(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-select-by-position", _clean_args(args))


def _tool_blender_mesh_select_by_area(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-select-by-area", _clean_args(args))


def _tool_blender_mesh_select_boundary_complete(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-select-boundary-complete", _clean_args(args))


def _tool_blender_mesh_select_island(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-select-island", _clean_args(args))


def _tool_blender_mesh_select_by_vertex_count(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-select-by-vertex-count", _clean_args(args))


def _tool_blender_modifier_subdivision_surface(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-modifier-subdivision-surface", _clean_args(args))


def _tool_blender_modifier_boolean(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-modifier-boolean", _clean_args(args))


def _tool_blender_modifier_array_complete(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-modifier-array-complete", _clean_args(args))


def _tool_blender_modifier_mirror_complete(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-modifier-mirror-complete", _clean_args(args))


def _tool_blender_modifier_bevel(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-modifier-bevel", _clean_args(args))


def _tool_blender_modifier_solidify(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-modifier-solidify", _clean_args(args))


def _tool_blender_mesh_extrude_manifold(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-extrude-manifold", _clean_args(args))


def _tool_blender_mesh_inset_individual(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-inset-individual", _clean_args(args))


def _tool_blender_mesh_poke_faces(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-poke-faces", _clean_args(args))


def _tool_blender_mesh_loop_tools_circle(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-loop-tools-circle", _clean_args(args))


def _tool_blender_mesh_symmetrize(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-symmetrize", _clean_args(args))


def _tool_blender_mesh_knife_project(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-knife-project", _clean_args(args))


def _tool_blender_uv_pack_islands(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-uv-pack-islands", _clean_args(args))


def _tool_blender_material_assign_fixed(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-material-assign-fixed", _clean_args(args))


def _tool_blender_mesh_measure(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-measure", _clean_args(args))


def _tool_blender_mesh_align_selection(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-align-selection", _clean_args(args))


def _tool_blender_mesh_distribute(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-distribute", _clean_args(args))


def _tool_blender_mesh_cleanup_complete(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-cleanup-complete", _clean_args(args))


def _tool_blender_mesh_decimate(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-decimate", _clean_args(args))


def _tool_blender_mesh_remesh(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-mesh-remesh", _clean_args(args))


def _tool_blender_curve_from_vertices(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-curve-from-vertices", _clean_args(args))


def _tool_blender_curve_to_mesh(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-curve-to-mesh", _clean_args(args))


def _tool_blender_batch_operation(args: JSONDict) -> JSONDict:
    return _call_bridge("blender-batch-operation", _clean_args(args))


def _tool_athena_scene_query_complete(args: JSONDict) -> JSONDict:
    return _call_bridge("athena-blender-scene-query-complete", _clean_args(args))


def _tool_athena_spatial_analyze(args: JSONDict) -> JSONDict:
    return _call_bridge("athena-blender-spatial-analyze", _clean_args(args))


def _tool_athena_topology_validate_complete(args: JSONDict) -> JSONDict:
    return _call_bridge("athena-blender-topology-validate-complete", _clean_args(args))


def _tool_athena_measure_batch(args: JSONDict) -> JSONDict:
    return _call_bridge("athena-blender-measure-batch", _clean_args(args))


def _tool_athena_validate_operation(args: JSONDict) -> JSONDict:
    return _call_bridge("athena-blender-validate-operation", _clean_args(args))


def _tool_athena_viewport_diff_comparison(args: JSONDict) -> JSONDict:
    return _call_bridge("athena-viewport-diff-comparison", _clean_args(args))


def _tool_athena_viewport_annotate_markup(args: JSONDict) -> JSONDict:
    return _call_bridge("athena-viewport-annotate-markup", _clean_args(args))


def _tool_athena_validate_operation_visual(args: JSONDict) -> JSONDict:
    return _call_bridge("athena-validate-operation-visual", _clean_args(args))


def _tool_athena_viewport_selection_isolate_capture(args: JSONDict) -> JSONDict:
    return _call_bridge("athena-viewport-selection-isolate-capture", _clean_args(args))


def _tool_athena_viewport_measurement_overlay(args: JSONDict) -> JSONDict:
    return _call_bridge("athena-viewport-measurement-overlay", _clean_args(args))


def _tool_athena_viewport_compare_matrix(args: JSONDict) -> JSONDict:
    return _call_bridge("athena-viewport-compare-matrix", _clean_args(args))


def _tool_athena_viewport_geometry_heatmap(args: JSONDict) -> JSONDict:
    return _call_bridge("athena-viewport-geometry-heatmap", _clean_args(args))


def _tool_athena_viewport_context_aware_capture(args: JSONDict) -> JSONDict:
    return _call_bridge("athena-viewport-context-aware-capture", _clean_args(args))


def _tool_athena_viewport_xray_section_view(args: JSONDict) -> JSONDict:
    return _call_bridge("athena-viewport-xray-section-view", _clean_args(args))


TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="athena-blender-scene-query-complete",
        description="Get complete scene state with geometry, transforms, bounds, and hierarchy metadata.",
        input_schema=specs_v2.SCENE_QUERY_COMPLETE_SCHEMA,
        impl=_tool_athena_scene_query_complete,
        category="scene",
        tags=["query", "diagnostic", "vision"],
        safety_level="safe-first",
    ),
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
        description="Report tool capabilities (safe-first vs view3d-required).",
        input_schema=diagnostics.CAPABILITIES_SCHEMA,
        impl=_tool_blender_diag_capabilities,
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
    # ---- New object operations ----
    ToolDefinition(
        name="blender-object-join",
        description="Join selected mesh objects into the active mesh.",
        input_schema=object_ops.OBJECT_JOIN_SCHEMA,
        impl=_tool_blender_object_join,
        category="object",
        tags=["merge", "topology"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-object-separate",
        description="Separate geometry from an object (SELECTED/MATERIAL/LOOSE).",
        input_schema=object_ops.OBJECT_SEPARATE_SCHEMA,
        impl=_tool_blender_object_separate,
        category="object",
        tags=["split", "topology"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-object-shade",
        description="Shade an object smooth or flat.",
        input_schema=object_ops.OBJECT_SHADE_SCHEMA,
        impl=_tool_blender_object_shade,
        category="object",
        tags=["shading"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-object-rotate",
        description="Rotate an object around an axis, optionally around a pivot.",
        input_schema=object_ops.OBJECT_ROTATE_SCHEMA,
        impl=_tool_blender_object_rotate,
        category="object",
        tags=["transform"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-object-mirror",
        description="Mirror an object using scale or geometry flip.",
        input_schema=object_ops.OBJECT_MIRROR_SCHEMA,
        impl=_tool_blender_object_mirror,
        category="object",
        tags=["transform", "mirror"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-object-snap",
        description="Snap an object to grid, cursor or another object.",
        input_schema=object_ops.OBJECT_SNAP_SCHEMA,
        impl=_tool_blender_object_snap,
        category="object",
        tags=["transform", "align"],
        safety_level="safe-first",
    ),
    # ---- Modifiers ----
    ToolDefinition(
        name="blender-modifier-apply",
        description="Apply a modifier on a mesh object.",
        input_schema=object_ops.MODIFIER_APPLY_SCHEMA,
        impl=_tool_blender_modifier_apply,
        category="object",
        tags=["modifier"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-modifier-move",
        description="Move a modifier up or down the stack.",
        input_schema=object_ops.MODIFIER_MOVE_SCHEMA,
        impl=_tool_blender_modifier_move,
        category="object",
        tags=["modifier"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-modifier-remove",
        description="Remove a modifier from an object.",
        input_schema=object_ops.MODIFIER_REMOVE_SCHEMA,
        impl=_tool_blender_modifier_remove,
        category="object",
        tags=["modifier"],
        safety_level="safe-first",
    ),
    # ---- Mesh advanced ----
    ToolDefinition(
        name="blender-mesh-spin",
        description="Spin (lathe) selected geometry around an axis.",
        input_schema=object_ops.MESH_SPIN_SCHEMA,
        impl=_tool_blender_mesh_spin,
        category="mesh",
        tags=["edit", "geometry"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-screw",
        description="Screw selected geometry to create threads/helix.",
        input_schema=object_ops.MESH_SCREW_SCHEMA,
        impl=_tool_blender_mesh_screw,
        category="mesh",
        tags=["edit", "geometry"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-normals",
        description="Recalculate or flip normals on selected geometry.",
        input_schema=object_ops.MESH_NORMALS_SCHEMA,
        impl=_tool_blender_mesh_normals,
        category="mesh",
        tags=["normals", "cleanup"],
        safety_level="safe-first",
    ),
    # ---- Materials ----
    ToolDefinition(
        name="blender-material-assign",
        description="Assign an existing material to selected faces.",
        input_schema=object_ops.MATERIAL_ASSIGN_SCHEMA,
        impl=_tool_blender_material_assign,
        category="material",
        tags=["assign"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-material-create",
        description="Create a Principled BSDF material.",
        input_schema=object_ops.MATERIAL_CREATE_SCHEMA,
        impl=_tool_blender_material_create,
        category="material",
        tags=["create"],
        safety_level="safe-first",
    ),
    # ---- Curves ----
    ToolDefinition(
        name="blender-curve-primitive",
        description="Create a curve primitive (Bezier/NURBS).",
        input_schema=object_ops.CURVE_PRIMITIVE_SCHEMA,
        impl=_tool_blender_curve_primitive,
        category="primitives",
        tags=["curve", "create"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-curve-convert",
        description="Convert a curve to mesh (optionally keep original).",
        input_schema=object_ops.CURVE_CONVERT_SCHEMA,
        impl=_tool_blender_curve_convert,
        category="curve",
        tags=["convert"],
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
    # ---- P0 transforms advanced ----
    ToolDefinition(
        name="blender-object-scale",
        description="Scale object with independent X/Y/Z (or uniform).",
        input_schema=object_ops.OBJECT_SCALE_SCHEMA,
        impl=_tool_blender_object_scale,
        category="object",
        tags=["transform", "scale"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-object-apply-transform",
        description="Apply location/rotation/scale to object data.",
        input_schema=object_ops.OBJECT_APPLY_TRANSFORM_SCHEMA,
        impl=_tool_blender_object_apply_transform,
        category="object",
        tags=["transform", "apply"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-object-origin-set",
        description="Set object origin (geometry/cursor/center).",
        input_schema=object_ops.OBJECT_ORIGIN_SET_SCHEMA,
        impl=_tool_blender_object_origin_set,
        category="object",
        tags=["origin", "pivot"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-object-parent",
        description="Set or clear parent-child relationship.",
        input_schema=object_ops.OBJECT_PARENT_SCHEMA,
        impl=_tool_blender_object_parent,
        category="object",
        tags=["parent", "hierarchy"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-object-clear-transform",
        description="Reset location/rotation/scale (and delta optionally).",
        input_schema=object_ops.OBJECT_CLEAR_TRANSFORM_SCHEMA,
        impl=_tool_blender_object_clear_transform,
        category="object",
        tags=["transform", "reset"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-rotate-selection",
        description="Rotate selected vertices around axis/pivot (bmesh).",
        input_schema=object_ops.MESH_ROTATE_SELECTION_SCHEMA,
        impl=_tool_blender_mesh_rotate_selection,
        category="mesh",
        tags=["transform", "rotate", "edit"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-object-duplicate",
        description="Duplicate object with linked/data copy and offset.",
        input_schema=object_ops.OBJECT_DUPLICATE_SCHEMA,
        impl=_tool_blender_object_duplicate,
        category="object",
        tags=["duplicate", "copy"],
        safety_level="safe-first",
    ),
    # ---- Modifiers P0 ----
    ToolDefinition(
        name="blender-modifier-add",
        description="Add a modifier to an object.",
        input_schema=object_ops.MODIFIER_ADD_SCHEMA,
        impl=_tool_blender_modifier_add,
        category="modifier",
        tags=["modifier", "add"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-modifier-configure",
        description="Configure modifier parameters (type-specific).",
        input_schema=object_ops.MODIFIER_CONFIGURE_SCHEMA,
        impl=_tool_blender_modifier_configure,
        category="modifier",
        tags=["modifier", "configure"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-modifier-configure-array",
        description="Configure Array modifier with preset patterns.",
        input_schema=object_ops.MODIFIER_CONFIGURE_ARRAY_SCHEMA,
        impl=_tool_blender_modifier_configure_array,
        category="modifier",
        tags=["modifier", "array", "pattern"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-modifier-configure-mirror",
        description="Configure Mirror modifier axes/bisect/clipping.",
        input_schema=object_ops.MODIFIER_CONFIGURE_MIRROR_SCHEMA,
        impl=_tool_blender_modifier_configure_mirror,
        category="modifier",
        tags=["modifier", "mirror"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-bridge-edge-loops",
        description="Bridge between edge loops (faces creation).",
        input_schema=object_ops.MESH_BRIDGE_EDGE_LOOPS_SCHEMA,
        impl=_tool_blender_mesh_bridge_edge_loops,
        category="mesh",
        tags=["mesh", "bridge", "fill"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-fill",
        description="Fill selected edge loops/holes with faces.",
        input_schema=object_ops.MESH_FILL_SCHEMA,
        impl=_tool_blender_mesh_fill,
        category="mesh",
        tags=["mesh", "fill"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-grid-fill",
        description="Grid fill selected quad-like loop.",
        input_schema=object_ops.MESH_GRID_FILL_SCHEMA,
        impl=_tool_blender_mesh_grid_fill,
        category="mesh",
        tags=["mesh", "fill", "grid"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-remove-doubles",
        description="Merge vertices by distance (remove doubles).",
        input_schema=object_ops.MESH_REMOVE_DOUBLES_SCHEMA,
        impl=_tool_blender_mesh_remove_doubles,
        category="mesh",
        tags=["mesh", "merge", "cleanup"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-select-similar",
        description="Select similar elements by property (area/normal/material/etc).",
        input_schema=object_ops.MESH_SELECT_SIMILAR_SCHEMA,
        impl=_tool_blender_mesh_select_similar,
        category="mesh",
        tags=["select", "similar"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-select-by-trait",
        description="Select geometry by topological trait (loose/boundary/non-manifold/sharp).",
        input_schema=object_ops.MESH_SELECT_BY_TRAIT_SCHEMA,
        impl=_tool_blender_mesh_select_by_trait,
        category="mesh",
        tags=["select", "topology"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-select-nth",
        description="Select every Nth element (pattern).",
        input_schema=object_ops.MESH_SELECT_NTH_SCHEMA,
        impl=_tool_blender_mesh_select_nth,
        category="mesh",
        tags=["select", "pattern"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-select-random",
        description="Randomly select elements by percentage.",
        input_schema=object_ops.MESH_SELECT_RANDOM_SCHEMA,
        impl=_tool_blender_mesh_select_random,
        category="mesh",
        tags=["select", "random"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-select-face-by-sides",
        description="Select faces by vertex count (triangles/quads/ngons/custom).",
        input_schema=object_ops.MESH_SELECT_FACE_BY_SIDES_SCHEMA,
        impl=_tool_blender_mesh_select_face_by_sides,
        category="mesh",
        tags=["select", "topology", "faces"],
        safety_level="safe-first",
    ),
    # ---- UV unwrap / projections ----
    ToolDefinition(
        name="blender-uv-unwrap",
        description="Unwrap mesh UVs (angle-based/conformal).",
        input_schema=object_ops.UV_UNWRAP_SCHEMA,
        impl=_tool_blender_uv_unwrap,
        category="uv",
        tags=["uv", "unwrap"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-uv-smart-project",
        description="Smart UV projection (auto cut by angle, no seams required).",
        input_schema=object_ops.UV_SMART_PROJECT_SCHEMA,
        impl=_tool_blender_uv_smart_project,
        category="uv",
        tags=["uv", "projection", "smart"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-uv-cube-project",
        description="Cube mapping projection (6 orthogonal directions).",
        input_schema=object_ops.UV_CUBE_PROJECT_SCHEMA,
        impl=_tool_blender_uv_cube_project,
        category="uv",
        tags=["uv", "projection", "cube"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-uv-cylinder-project",
        description="Cylindrical UV projection.",
        input_schema=object_ops.UV_CYLINDER_PROJECT_SCHEMA,
        impl=_tool_blender_uv_cylinder_project,
        category="uv",
        tags=["uv", "projection", "cylinder"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-uv-sphere-project",
        description="Spherical UV projection.",
        input_schema=object_ops.UV_SPHERE_PROJECT_SCHEMA,
        impl=_tool_blender_uv_sphere_project,
        category="uv",
        tags=["uv", "projection", "sphere"],
        safety_level="safe-first",
    ),
    # Collections (P1)
    ToolDefinition(
        name="blender-collection-create",
        description="Create a collection and optionally parent it.",
        input_schema=object_ops.COLLECTION_CREATE_SCHEMA,
        impl=_tool_blender_collection_create,
        category="scene",
        tags=["collection", "organize"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-collection-add-objects",
        description="Add (move or instance) objects into a collection.",
        input_schema=object_ops.COLLECTION_ADD_OBJECTS_SCHEMA,
        impl=_tool_blender_collection_add_objects,
        category="scene",
        tags=["collection", "organize"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-collection-remove-objects",
        description="Remove objects from a collection (optionally delete).",
        input_schema=object_ops.COLLECTION_REMOVE_OBJECTS_SCHEMA,
        impl=_tool_blender_collection_remove_objects,
        category="scene",
        tags=["collection", "organize"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-collection-hide",
        description="Hide/show collection visibility (viewport/render/select).",
        input_schema=object_ops.COLLECTION_HIDE_SCHEMA,
        impl=_tool_blender_collection_hide,
        category="scene",
        tags=["collection", "visibility"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-object-rename",
        description="Rename object with optional find/replace/prefix/suffix.",
        input_schema=object_ops.OBJECT_RENAME_SCHEMA,
        impl=_tool_blender_object_rename,
        category="scene",
        tags=["rename", "organize"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-import-file",
        description="Import 3D file (OBJ/FBX/GLTF/STL/PLY).",
        input_schema=object_ops.IMPORT_FILE_SCHEMA,
        impl=_tool_blender_import_file,
        category="io",
        tags=["import", "file", "io"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-export-file",
        description="Export scene/objects to file (OBJ/FBX/GLTF/STL/PLY/USD).",
        input_schema=object_ops.EXPORT_FILE_SCHEMA,
        impl=_tool_blender_export_file,
        category="io",
        tags=["export", "file", "io"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-recalculate-normals",
        description="Recalculate/flip face normals.",
        input_schema=object_ops.MESH_RECALCULATE_NORMALS_SCHEMA,
        impl=_tool_blender_mesh_recalculate_normals,
        category="mesh",
        tags=["normals", "cleanup"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-validate",
        description="Validate mesh topology and report issues.",
        input_schema=object_ops.MESH_VALIDATE_SCHEMA,
        impl=_tool_blender_mesh_validate,
        category="mesh",
        tags=["validate", "cleanup"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-triangulate",
        description="Convert quads/ngons to triangles.",
        input_schema=object_ops.MESH_TRIANGULATE_SCHEMA,
        impl=_tool_blender_mesh_triangulate,
        category="mesh",
        tags=["triangulate", "convert"],
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
    # ---- Spec finale P1-P10 ----
    ToolDefinition(
        name="blender-viewport-screenshot-complete",
        description="Capture viewport screenshots across multiple views/shading modes with overlays and diagnostics.",
        input_schema=specs_v2.VIEWPORT_SCREENSHOT_SCHEMA,
        impl=_tool_blender_viewport_screenshot_complete,
        category="diag",
        tags=["viewport", "capture", "render", "overlay"],
        safety_level="view3d-required",
    ),
    ToolDefinition(
        name="blender-viewport-render-modes",
        description="Configure viewport render engine/workbench settings and report supported options.",
        input_schema=specs_v2.VIEWPORT_RENDER_MODES_SCHEMA,
        impl=_tool_blender_viewport_render_modes,
        category="diag",
        tags=["viewport", "render", "workbench"],
        safety_level="view3d-required",
    ),
    ToolDefinition(
        name="blender-mesh-query-geometry",
        description="Inspect mesh geometry (verts/edges/faces) with optional stats and limits.",
        input_schema=specs_v2.MESH_QUERY_GEOMETRY_SCHEMA,
        impl=_tool_blender_mesh_query_geometry,
        category="mesh",
        tags=["query", "diagnostic", "inspect"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-query-selection",
        description="Report selection mode, indices, counts, and bounds for a mesh.",
        input_schema=specs_v2.MESH_QUERY_SELECTION_SCHEMA,
        impl=_tool_blender_mesh_query_selection,
        category="mesh",
        tags=["query", "selection", "diagnostic"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-query-topology",
        description="Run topology checks (manifold, ngons, poles, boundaries).",
        input_schema=specs_v2.MESH_QUERY_TOPOLOGY_SCHEMA,
        impl=_tool_blender_mesh_query_topology,
        category="mesh",
        tags=["diagnostic", "topology", "cleanup"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-analyze-quality",
        description="Compute mesh quality metrics (lengths, areas, angles, distortion).",
        input_schema=specs_v2.MESH_ANALYZE_QUALITY_SCHEMA,
        impl=_tool_blender_mesh_analyze_quality,
        category="mesh",
        tags=["diagnostic", "quality"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-select-by-position",
        description="Select mesh elements by position relative to an axis threshold.",
        input_schema=specs_v2.MESH_SELECT_BY_POSITION_SCHEMA,
        impl=_tool_blender_mesh_select_by_position,
        category="selection",
        tags=["select", "filter", "position"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-select-by-area",
        description="Select faces by area range.",
        input_schema=specs_v2.MESH_SELECT_BY_AREA_SCHEMA,
        impl=_tool_blender_mesh_select_by_area,
        category="selection",
        tags=["select", "area", "faces"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-select-boundary-complete",
        description="Select boundary edges (all or largest loop).",
        input_schema=specs_v2.MESH_SELECT_BOUNDARY_COMPLETE_SCHEMA,
        impl=_tool_blender_mesh_select_boundary_complete,
        category="selection",
        tags=["select", "boundary", "edge"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-select-island",
        description="Select an island by index or size (largest/smallest).",
        input_schema=specs_v2.MESH_SELECT_ISLAND_SCHEMA,
        impl=_tool_blender_mesh_select_island,
        category="selection",
        tags=["select", "island"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-select-by-vertex-count",
        description="Select faces by vertex count (e.g., quads only).",
        input_schema=specs_v2.MESH_SELECT_BY_VERTEX_COUNT_SCHEMA,
        impl=_tool_blender_mesh_select_by_vertex_count,
        category="selection",
        tags=["select", "topology", "faces"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-modifier-subdivision-surface",
        description="Add/configure a Subdivision Surface modifier.",
        input_schema=specs_v2.MOD_SUBSURF_SCHEMA,
        impl=_tool_blender_modifier_subdivision_surface,
        category="modifier",
        tags=["modifier", "subsurf", "subdivision"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-modifier-boolean",
        description="Configure a Boolean modifier with operand and solver options.",
        input_schema=specs_v2.MOD_BOOLEAN_SCHEMA,
        impl=_tool_blender_modifier_boolean,
        category="modifier",
        tags=["modifier", "boolean"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-modifier-array-complete",
        description="Configure an Array modifier (fit, offsets, merge, caps).",
        input_schema=specs_v2.MOD_ARRAY_COMPLETE_SCHEMA,
        impl=_tool_blender_modifier_array_complete,
        category="modifier",
        tags=["modifier", "array"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-modifier-mirror-complete",
        description="Configure a Mirror modifier with bisect/merge/UV options.",
        input_schema=specs_v2.MOD_MIRROR_COMPLETE_SCHEMA,
        impl=_tool_blender_modifier_mirror_complete,
        category="modifier",
        tags=["modifier", "mirror"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-modifier-bevel",
        description="Configure a Bevel modifier (width, segments, profile).",
        input_schema=specs_v2.MOD_BEVEL_SCHEMA,
        impl=_tool_blender_modifier_bevel,
        category="modifier",
        tags=["modifier", "bevel"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-modifier-solidify",
        description="Configure a Solidify modifier (thickness, rim options).",
        input_schema=specs_v2.MOD_SOLIDIFY_SCHEMA,
        impl=_tool_blender_modifier_solidify,
        category="modifier",
        tags=["modifier", "solidify"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-extrude-manifold",
        description="Extrude selection with manifold-safe offset/scale/rotation.",
        input_schema=specs_v2.MESH_EXTRUDE_MANIFOLD_SCHEMA,
        impl=_tool_blender_mesh_extrude_manifold,
        category="mesh",
        tags=["edit", "extrude", "manifold"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-inset-individual",
        description="Inset selected faces individually with even offset control.",
        input_schema=specs_v2.MESH_INSET_INDIVIDUAL_SCHEMA,
        impl=_tool_blender_mesh_inset_individual,
        category="mesh",
        tags=["edit", "inset", "faces"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-poke-faces",
        description="Poke selected faces toward center (fan triangulation).",
        input_schema=specs_v2.MESH_POKE_FACES_SCHEMA,
        impl=_tool_blender_mesh_poke_faces,
        category="mesh",
        tags=["edit", "poke", "faces"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-loop-tools-circle",
        description="Conform selected vertices using LoopTools (circle/flatten/space/curve).",
        input_schema=specs_v2.MESH_LOOP_TOOLS_CIRCLE_SCHEMA,
        impl=_tool_blender_mesh_loop_tools_circle,
        category="mesh",
        tags=["edit", "looptools", "align"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-symmetrize",
        description="Symmetrize mesh geometry across an axis.",
        input_schema=specs_v2.MESH_SYMMETRIZE_SCHEMA,
        impl=_tool_blender_mesh_symmetrize,
        category="mesh",
        tags=["symmetry", "edit"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-knife-project",
        description="Project cutter objects onto a target mesh and cut.",
        input_schema=specs_v2.MESH_KNIFE_PROJECT_SCHEMA,
        impl=_tool_blender_mesh_knife_project,
        category="mesh",
        tags=["knife", "project", "edit"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-uv-pack-islands",
        description="Pack UV islands with margin/rotation options.",
        input_schema=specs_v2.UV_PACK_ISLANDS_SCHEMA,
        impl=_tool_blender_uv_pack_islands,
        category="uv",
        tags=["uv", "pack"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-material-assign-fixed",
        description="Assign a material to selection or entire object, creating slots if needed.",
        input_schema=specs_v2.MATERIAL_ASSIGN_FIXED_SCHEMA,
        impl=_tool_blender_material_assign_fixed,
        category="material",
        tags=["material", "assign"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-measure",
        description="Measure length/area/volume/distance for selection or mesh.",
        input_schema=specs_v2.MESH_MEASURE_SCHEMA,
        impl=_tool_blender_mesh_measure,
        category="mesh",
        tags=["measure", "precision", "diagnostic"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-align-selection",
        description="Align selection to axis/value (local or world).",
        input_schema=specs_v2.MESH_ALIGN_SELECTION_SCHEMA,
        impl=_tool_blender_mesh_align_selection,
        category="mesh",
        tags=["align", "selection"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-distribute",
        description="Distribute selected elements evenly along an axis or surface.",
        input_schema=specs_v2.MESH_DISTRIBUTE_SCHEMA,
        impl=_tool_blender_mesh_distribute,
        category="mesh",
        tags=["distribute", "selection"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-cleanup-complete",
        description="Run cleanup operations (merge by distance, delete loose/degenerate, recalc normals, planarize).",
        input_schema=specs_v2.MESH_CLEANUP_COMPLETE_SCHEMA,
        impl=_tool_blender_mesh_cleanup_complete,
        category="mesh",
        tags=["cleanup", "optimize"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-decimate",
        description="Decimate mesh with ratio/method and optional triangulation.",
        input_schema=specs_v2.MESH_DECIMATE_SCHEMA,
        impl=_tool_blender_mesh_decimate,
        category="mesh",
        tags=["decimate", "optimize"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-mesh-remesh",
        description="Remesh using voxel/quad/sharp modes with adaptivity options.",
        input_schema=specs_v2.MESH_REMESH_SCHEMA,
        impl=_tool_blender_mesh_remesh,
        category="mesh",
        tags=["remesh", "optimize"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-curve-from-vertices",
        description="Create a curve from coordinates or selected mesh vertices.",
        input_schema=specs_v2.CURVE_FROM_VERTICES_SCHEMA,
        impl=_tool_blender_curve_from_vertices,
        category="curve",
        tags=["curve", "create"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="blender-curve-to-mesh",
        description="Convert a curve to mesh with bevel/extrude options.",
        input_schema=specs_v2.CURVE_TO_MESH_SCHEMA,
        impl=_tool_blender_curve_to_mesh,
        category="curve",
        tags=["curve", "convert"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="athena-blender-spatial-analyze",
        description="Analyze spatial relationships (distances, alignments, overlaps, grid snaps) for scene objects.",
        input_schema=specs_v2.SPATIAL_ANALYZE_SCHEMA,
        impl=_tool_athena_spatial_analyze,
        category="scene",
        tags=["analysis", "diagnostic", "vision"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="athena-blender-topology-validate-complete",
        description="Validate mesh topology for manifold, watertightness, ngons, poles, loose geometry, and degenerates.",
        input_schema=specs_v2.TOPOLOGY_VALIDATE_COMPLETE_SCHEMA,
        impl=_tool_athena_topology_validate_complete,
        category="mesh",
        tags=["validation", "topology", "diagnostic"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="athena-blender-measure-batch",
        description="Execute multiple measurements (distance, volume, area, alignment) in one call.",
        input_schema=specs_v2.MEASURE_BATCH_SCHEMA,
        impl=_tool_athena_measure_batch,
        category="measurement",
        tags=["measurement", "analysis", "batch"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="athena-blender-validate-operation",
        description="Validate mesh/object against manifold, watertight, symmetry, alignment, and size expectations.",
        input_schema=specs_v2.VALIDATE_OPERATION_SCHEMA,
        impl=_tool_athena_validate_operation,
        category="validation",
        tags=["validation", "quality", "diagnostic"],
        safety_level="safe-first",
    ),
    ToolDefinition(
        name="athena-viewport-diff-comparison",
        description="Compare before/after viewport captures with geometry diff overlays and measurements.",
        input_schema=vision_specs.VIEWPORT_DIFF_COMPARISON_SCHEMA,
        impl=_tool_athena_viewport_diff_comparison,
        category="vision",
        tags=["viewport", "diff", "diagnostic", "compare"],
        safety_level="view3d-required",
    ),
    ToolDefinition(
        name="athena-viewport-annotate-markup",
        description="Annotate viewport captures with manual/auto overlays and export annotation data.",
        input_schema=vision_specs.VIEWPORT_ANNOTATE_MARKUP_SCHEMA,
        impl=_tool_athena_viewport_annotate_markup,
        category="vision",
        tags=["viewport", "annotation", "overlay"],
        safety_level="view3d-required",
    ),
    ToolDefinition(
        name="athena-validate-operation-visual",
        description="Full visual validation workflow with before/after capture, diff, topology checks, and report.",
        input_schema=vision_specs.VALIDATE_OPERATION_VISUAL_SCHEMA,
        impl=_tool_athena_validate_operation_visual,
        category="validation",
        tags=["validation", "workflow", "vision"],
        safety_level="view3d-required",
    ),
    ToolDefinition(
        name="athena-viewport-selection-isolate-capture",
        description="Capture focused screenshots on a selection with framing and context display options.",
        input_schema=vision_specs.VIEWPORT_SELECTION_ISOLATE_CAPTURE_SCHEMA,
        impl=_tool_athena_viewport_selection_isolate_capture,
        category="vision",
        tags=["viewport", "selection", "capture"],
        safety_level="view3d-required",
    ),
    ToolDefinition(
        name="athena-viewport-measurement-overlay",
        description="Overlay precise measurements on viewport captures (manual or automatic).",
        input_schema=vision_specs.VIEWPORT_MEASUREMENT_OVERLAY_SCHEMA,
        impl=_tool_athena_viewport_measurement_overlay,
        category="vision",
        tags=["viewport", "measurement", "overlay"],
        safety_level="view3d-required",
    ),
    ToolDefinition(
        name="athena-viewport-compare-matrix",
        description="Render comparison matrices across multiple scene states with synced settings.",
        input_schema=vision_specs.VIEWPORT_COMPARE_MATRIX_SCHEMA,
        impl=_tool_athena_viewport_compare_matrix,
        category="vision",
        tags=["viewport", "comparison", "matrix"],
        safety_level="view3d-required",
    ),
    ToolDefinition(
        name="athena-viewport-geometry-heatmap",
        description="Generate heatmaps for geometric properties using vertex colors and legend overlays.",
        input_schema=vision_specs.VIEWPORT_GEOMETRY_HEATMAP_SCHEMA,
        impl=_tool_athena_viewport_geometry_heatmap,
        category="vision",
        tags=["viewport", "diagnostic", "heatmap"],
        safety_level="view3d-required",
    ),
    ToolDefinition(
        name="athena-viewport-context-aware-capture",
        description="Intelligent capture selection based on context hints and auto-detected issues.",
        input_schema=vision_specs.VIEWPORT_CONTEXT_AWARE_CAPTURE_SCHEMA,
        impl=_tool_athena_viewport_context_aware_capture,
        category="vision",
        tags=["viewport", "capture", "auto"],
        safety_level="view3d-required",
    ),
    ToolDefinition(
        name="athena-viewport-xray-section-view",
        description="Produce section and xray captures with interior display options.",
        input_schema=vision_specs.VIEWPORT_XRAY_SECTION_SCHEMA,
        impl=_tool_athena_viewport_xray_section_view,
        category="vision",
        tags=["viewport", "section", "xray"],
        safety_level="view3d-required",
    ),
    ToolDefinition(
        name="blender-batch-operation",
        description="Apply transform/material/modifier/parent operations to multiple objects.",
        input_schema=specs_v2.BATCH_OPERATION_SCHEMA,
        impl=_tool_blender_batch_operation,
        category="object",
        tags=["batch", "transform", "material", "modifier"],
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
