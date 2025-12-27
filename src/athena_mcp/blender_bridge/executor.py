from __future__ import annotations

from typing import Any, Dict, List, Optional

from .responses import error_response, ok_response


def _require_bpy():
    try:
        import bpy  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on Blender runtime
        raise RuntimeError("bpy is required inside Blender") from exc
    return bpy


def _active_mesh(bpy):
    obj = bpy.context.view_layer.objects.active
    if obj is None:
        return None, error_response("No active object", code="bad_request")
    if obj.type != "MESH":
        return None, error_response("Active object is not a mesh", code="bad_request")
    return obj, None


def _ensure_mode(bpy, mode: str):
    try:
        bpy.ops.object.mode_set(mode=mode)
        return None
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def list_objects(args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    bpy = _require_bpy()
    names: List[str] = [obj.name for obj in bpy.data.objects]
    return ok_response(result={"objects": names, "count": len(names)})


def add_cube(args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover - Blender runtime

    args = args or {}
    cube_name = args.get("name") or "Cube"
    size_val = args.get("size")
    cube_size = float(size_val) if size_val is not None else 1.0

    try:
        final_name = cube_name
        if bpy.data.objects.get(final_name):
            suffix = 1
            base = cube_name
            while bpy.data.objects.get(f"{base}.{suffix:03d}"):
                suffix += 1
            final_name = f"{base}.{suffix:03d}"

        mesh = bpy.data.meshes.new(f"{final_name}_mesh")
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=cube_size)
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new(final_name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        return ok_response(result={"name": obj.name, "location": list(obj.location), "size": cube_size})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def _extract_location(args: Dict[str, Any]) -> Optional[List[float]]:
    if "location" in args and isinstance(args["location"], list) and len(args["location"]) == 3:
        return args["location"]
    coords = []
    for key in ("x", "y", "z"):
        if key in args:
            coords.append(args[key])
    if len(coords) == 3 and all(isinstance(v, (int, float)) for v in coords):
        return [float(v) for v in coords]
    return None


def move_object(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    name = args.get("name") or args.get("object") or args.get("object_name")
    if not isinstance(name, str):
        return error_response("name must be provided", code="bad_request")
    location = _extract_location(args)
    if location is None:
        return error_response("location must be [x, y, z]", code="bad_request")
    obj = bpy.data.objects.get(name)
    if obj is None:
        return error_response(f"Object '{name}' not found", code="not_found")
    try:
        obj.location = location
        return ok_response(result={"name": obj.name, "location": list(obj.location)})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def set_mode(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    mode = args.get("mode")
    if mode not in ("OBJECT", "EDIT"):
        return error_response("mode must be OBJECT or EDIT", code="bad_request")
    target_name = args.get("name")
    if target_name:
        obj = bpy.data.objects.get(target_name)
        if obj is None:
            return error_response(f"Object '{target_name}' not found", code="not_found")
        bpy.context.view_layer.objects.active = obj
    obj, err = _active_mesh(bpy)
    if err:
        return err
    if mode == "EDIT" and obj.mode != "EDIT":
        error_mode = _ensure_mode(bpy, "EDIT")
        if error_mode:
            return error_mode
    elif mode == "OBJECT":
        error_mode = _ensure_mode(bpy, "OBJECT")
        if error_mode:
            return error_mode
    return ok_response(result={"mode": mode, "active": obj.name})


def set_selection_mode(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    mode = args.get("mode")
    if mode not in ("VERT", "EDGE", "FACE"):
        return error_response("mode must be VERT/EDGE/FACE", code="bad_request")
    obj, err = _active_mesh(bpy)
    if err:
        return err
    if obj.mode != "EDIT":
        ensure = _ensure_mode(bpy, "EDIT")
        if ensure:
            return ensure
    flags = {
        "VERT": (True, False, False),
        "EDGE": (False, True, False),
        "FACE": (False, False, True),
    }
    bpy.context.tool_settings.mesh_select_mode = flags[mode]
    return ok_response(result={"mode": mode})


def _ensure_edit_mode(bpy):
    obj, err = _active_mesh(bpy)
    if err:
        return None, err
    if obj.mode != "EDIT":
        ensure = _ensure_mode(bpy, "EDIT")
        if ensure:
            return None, ensure
    return obj, None


def select_all(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    _, err = _ensure_edit_mode(bpy)
    if err:
        return err
    try:
        bpy.ops.mesh.select_all(action="SELECT")
        return ok_response(result={"selected": "all"})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def select_none(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    _, err = _ensure_edit_mode(bpy)
    if err:
        return err
    try:
        bpy.ops.mesh.select_all(action="DESELECT")
        return ok_response(result={"selected": "none"})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def select_invert(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    _, err = _ensure_edit_mode(bpy)
    if err:
        return err
    try:
        bpy.ops.mesh.select_all(action="INVERT")
        return ok_response(result={"selected": "invert"})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def mesh_delete(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    _, err = _ensure_edit_mode(bpy)
    if err:
        return err
    delete_type = args.get("type")
    if delete_type not in ("VERT", "EDGE", "FACE"):
        return error_response("type must be VERT/EDGE/FACE", code="bad_request")
    try:
        bpy.ops.mesh.delete(type=delete_type)
        return ok_response(result={"deleted": True, "type": delete_type})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def mesh_extrude(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    _, err = _ensure_edit_mode(bpy)
    if err:
        return err
    try:
        delta = (float(args.get("x", 0.0)), float(args.get("y", 0.0)), float(args.get("z", 0.0)))
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": delta})
        return ok_response(result={"extruded": True, "delta": list(delta)})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def mesh_inset(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    _, err = _ensure_edit_mode(bpy)
    if err:
        return err
    try:
        thickness = float(args.get("thickness", 0.05))
        depth = float(args.get("depth", 0.0))
        bpy.ops.mesh.inset(thickness=thickness, depth=depth)
        return ok_response(result={"inset": True, "thickness": thickness, "depth": depth})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def mesh_loop_cut(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    _, err = _ensure_edit_mode(bpy)
    if err:
        return err
    cuts = int(args.get("cuts", 1))
    smoothness = float(args.get("smoothness", 0.0))
    try:
        if hasattr(bpy.ops.mesh, "loopcut_slide"):
            bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={"number_cuts": cuts}, TRANSFORM_OT_edge_slide={"value": smoothness})
        else:
            bpy.ops.mesh.loopcut(number_cuts=cuts, smoothness=smoothness)
        return ok_response(result={"loop_cut": True, "cuts": cuts})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def mesh_bevel(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    _, err = _ensure_edit_mode(bpy)
    if err:
        return err
    offset = float(args.get("offset", 0.02))
    segments = int(args.get("segments", 1))
    profile = float(args.get("profile", 0.5))
    try:
        bpy.ops.mesh.bevel(offset=offset, segments=segments, profile=profile)
        return ok_response(result={"bevel": True, "offset": offset, "segments": segments, "profile": profile})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def mesh_subdivide(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    _, err = _ensure_edit_mode(bpy)
    if err:
        return err
    cuts = int(args.get("cuts", 1))
    smooth = float(args.get("smooth", 0.0))
    try:
        bpy.ops.mesh.subdivide(number_cuts=cuts, smoothness=smooth)
        return ok_response(result={"subdivide": True, "cuts": cuts, "smooth": smooth})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def mesh_merge(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    _, err = _ensure_edit_mode(bpy)
    if err:
        return err
    merge_type = args.get("type")
    if merge_type not in ("CENTER", "CURSOR", "FIRST", "LAST"):
        return error_response("type must be CENTER/CURSOR/FIRST/LAST", code="bad_request")
    try:
        bpy.ops.mesh.merge(type=merge_type)
        return ok_response(result={"merge": True, "type": merge_type})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")
