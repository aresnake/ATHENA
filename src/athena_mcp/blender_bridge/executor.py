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
        return None, error_response("No active object", code="no_active_object")
    if obj.type != "MESH":
        return None, error_response("Active object is not a mesh", code="not_mesh")
    return obj, None


def _ensure_mode(bpy, mode: str):
    try:
        bpy.ops.object.mode_set(mode=mode)
        return None
    except Exception as exc:
        return error_response(str(exc), code="invalid_context")


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
        return error_response(str(exc), code="internal_error")


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
        return error_response(str(exc), code="internal_error")


def select_none(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    _, err = _ensure_edit_mode(bpy)
    if err:
        return err
    try:
        bpy.ops.mesh.select_all(action="DESELECT")
        return ok_response(result={"selected": "none"})
    except Exception as exc:
        return error_response(str(exc), code="internal_error")


def select_invert(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    _, err = _ensure_edit_mode(bpy)
    if err:
        return err
    try:
        bpy.ops.mesh.select_all(action="INVERT")
        return ok_response(result={"selected": "invert"})
    except Exception as exc:
        return error_response(str(exc), code="internal_error")


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
        return error_response(str(exc), code="internal_error")


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
        return error_response(str(exc), code="internal_error")


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
        return error_response(str(exc), code="internal_error")


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
    except AttributeError as exc:
        return error_response(
            "Loop cut not supported in this context",
            code="not_supported",
            details={"reason": str(exc), "tool": "blender-mesh-loop-cut", "op": "mesh.loopcut", "hint": "Requires View3D context or unavailable in this Blender build."},
        )
    except Exception as exc:
        msg = str(exc)
        if "view3d" in msg.lower() or "context" in msg.lower():
            return error_response(
                "Loop cut not supported in this context",
                code="not_supported",
                details={"reason": msg, "tool": "blender-mesh-loop-cut", "op": "mesh.loopcut", "hint": "Requires View3D context or unavailable in this Blender build."},
            )
        return error_response(str(exc), code="internal_error")


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
        return error_response(str(exc), code="internal_error")


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
        return error_response(str(exc), code="internal_error")


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
        return error_response(str(exc), code="internal_error")


def mesh_select_loop(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    _, err = _ensure_edit_mode(bpy)
    if err:
        return err
    extend = bool(args.get("extend", False))
    try:
        bpy.ops.mesh.loop_select(extend=extend)
        return ok_response(result={"select_loop": True, "extend": extend})
    except AttributeError as exc:
        return error_response(
            "Loop select not supported",
            code="not_supported",
            details={"reason": str(exc), "tool": "blender-mesh-select-loop", "op": "mesh.loop_select", "hint": "Requires View3D context or unavailable in this Blender build."},
        )
    except Exception as exc:
        msg = str(exc)
        if "view3d" in msg.lower() or "context" in msg.lower():
            return error_response(
                "Loop select not supported in this context",
                code="not_supported",
                details={"reason": msg, "tool": "blender-mesh-select-loop", "op": "mesh.loop_select", "hint": "Requires View3D context or unavailable in this Blender build."},
            )
        return error_response(str(exc), code="internal_error")


def mesh_select_ring(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    _, err = _ensure_edit_mode(bpy)
    if err:
        return err
    extend = bool(args.get("extend", False))
    try:
        bpy.ops.mesh.ring_select(extend=extend)
        return ok_response(result={"select_ring": True, "extend": extend})
    except AttributeError as exc:
        return error_response(
            "Ring select not supported",
            code="not_supported",
            details={"reason": str(exc), "tool": "blender-mesh-select-ring", "op": "mesh.ring_select", "hint": "Requires View3D context or unavailable in this Blender build."},
        )
    except Exception as exc:
        msg = str(exc)
        if "view3d" in msg.lower() or "context" in msg.lower():
            return error_response(
                "Ring select not supported in this context",
                code="not_supported",
                details={"reason": msg, "tool": "blender-mesh-select-ring", "op": "mesh.ring_select", "hint": "Requires View3D context or unavailable in this Blender build."},
            )
        return error_response(str(exc), code="internal_error")


def mesh_select_linked(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    _, err = _ensure_edit_mode(bpy)
    if err:
        return err
    try:
        bpy.ops.mesh.select_linked()
        return ok_response(result={"select_linked": True})
    except Exception as exc:
        msg = str(exc)
        if "view3d" in msg.lower() or "context" in msg.lower():
            return error_response(
                "Select linked not supported in this context",
                code="not_supported",
                details={"reason": msg, "tool": "blender-mesh-select-linked", "op": "mesh.select_linked", "hint": "Requires View3D context or unavailable in this Blender build."},
            )
        return error_response(str(exc), code="internal_error")


def mesh_select_more(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    _, err = _ensure_edit_mode(bpy)
    if err:
        return err
    try:
        bpy.ops.mesh.select_more()
        return ok_response(result={"select_more": True})
    except Exception as exc:
        return error_response(str(exc), code="internal_error")


def mesh_select_less(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    _, err = _ensure_edit_mode(bpy)
    if err:
        return err
    try:
        bpy.ops.mesh.select_less()
        return ok_response(result={"select_less": True})
    except Exception as exc:
        return error_response(str(exc), code="internal_error")


def mesh_select_non_manifold(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    _, err = _ensure_edit_mode(bpy)
    if err:
        return err
    extend = bool(args.get("extend", False))
    try:
        bpy.ops.mesh.select_non_manifold(extend=extend)
        return ok_response(result={"select_non_manifold": True, "extend": extend})
    except Exception as exc:
        msg = str(exc)
        if "view3d" in msg.lower() or "context" in msg.lower():
            return error_response(
                "Select non-manifold not supported in this context",
                code="not_supported",
                details={"reason": msg, "tool": "blender-mesh-select-non-manifold", "op": "mesh.select_non_manifold", "hint": "Requires View3D context or unavailable in this Blender build."},
            )
        return error_response(str(exc), code="internal_error")


def mesh_select_boundary(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    _, err = _ensure_edit_mode(bpy)
    if err:
        return err
    extend = bool(args.get("extend", False))
    try:
        if hasattr(bpy.ops.mesh, "select_boundary_loop"):
            bpy.ops.mesh.select_boundary_loop()
            return ok_response(result={"select_boundary": True, "extend": extend})
        return error_response("boundary selection not supported", code="not_supported")
    except Exception as exc:
        msg = str(exc)
        if "view3d" in msg.lower() or "context" in msg.lower():
            return error_response(
                "Boundary select not supported in this context",
                code="not_supported",
                details={"reason": msg, "tool": "blender-mesh-select-boundary", "op": "mesh.select_boundary_loop", "hint": "Requires View3D context or unavailable in this Blender build."},
            )
        return error_response(str(exc), code="internal_error")


def mesh_select_by_index(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover

    obj, err = _ensure_edit_mode(bpy)
    if err:
        return err
    element = args.get("element")
    indices = args.get("indices", [])
    clear_sel = bool(args.get("clear", True))

    if element not in ("VERT", "EDGE", "FACE"):
        return error_response("element must be VERT/EDGE/FACE", code="bad_request")
    if not isinstance(indices, list) or not all(isinstance(i, int) for i in indices):
        return error_response("indices must be a list of integers", code="bad_request")

    bm = bmesh.from_edit_mesh(obj.data)
    try:
        if clear_sel:
            for v in bm.verts:
                v.select_set(False)
            for e in bm.edges:
                e.select_set(False)
            for f in bm.faces:
                f.select_set(False)
        count = 0
        if element == "VERT":
            for idx in indices:
                if 0 <= idx < len(bm.verts):
                    bm.verts[idx].select_set(True)
                    count += 1
        elif element == "EDGE":
            for idx in indices:
                if 0 <= idx < len(bm.edges):
                    bm.edges[idx].select_set(True)
                    count += 1
        elif element == "FACE":
            for idx in indices:
                if 0 <= idx < len(bm.faces):
                    bm.faces[idx].select_set(True)
                    count += 1
        bmesh.update_edit_mesh(obj.data)
        return ok_response(result={"select_by_index": True, "element": element, "count": count})
    except Exception as exc:
        return error_response(str(exc), code="internal_error")


def mesh_set_selection(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover

    obj, err = _ensure_edit_mode(bpy)
    if err:
        return err
    element = args.get("element")
    indices = args.get("indices", [])
    clear_sel = bool(args.get("clear", True))
    if element not in ("VERT", "EDGE", "FACE"):
        return error_response("element must be VERT/EDGE/FACE", code="bad_request")
    if not isinstance(indices, list) or not all(isinstance(i, int) for i in indices):
        return error_response("indices must be a list of integers", code="bad_request")
    bm = bmesh.from_edit_mesh(obj.data)
    try:
        if clear_sel:
            for v in bm.verts:
                v.select_set(False)
            for e in bm.edges:
                e.select_set(False)
            for f in bm.faces:
                f.select_set(False)
        count = 0
        if element == "VERT":
            for idx in indices:
                if 0 <= idx < len(bm.verts):
                    bm.verts[idx].select_set(True)
                    count += 1
        elif element == "EDGE":
            for idx in indices:
                if 0 <= idx < len(bm.edges):
                    bm.edges[idx].select_set(True)
                    count += 1
        elif element == "FACE":
            for idx in indices:
                if 0 <= idx < len(bm.faces):
                    bm.faces[idx].select_set(True)
                    count += 1
        bmesh.update_edit_mesh(obj.data)
        return ok_response(result={"selected": True, "element": element, "count": count})
    except Exception as exc:
        return error_response(str(exc), code="internal_error")


def mesh_bisect_plane(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover

    obj, err = _ensure_edit_mode(bpy)
    if err:
        return err
    plane_co = args.get("plane_co")
    plane_no = args.get("plane_no")
    if not (isinstance(plane_co, list) and len(plane_co) == 3 and all(isinstance(v, (int, float)) for v in plane_co)):
        return error_response("plane_co must be [x, y, z]", code="bad_request")
    if not (isinstance(plane_no, list) and len(plane_no) == 3 and all(isinstance(v, (int, float)) for v in plane_no)):
        return error_response("plane_no must be [nx, ny, nz]", code="bad_request")
    clear_inner = bool(args.get("clear_inner", False))
    clear_outer = bool(args.get("clear_outer", False))
    bm = bmesh.from_edit_mesh(obj.data)
    try:
        res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=plane_co, plane_no=plane_no)
        geom_cut = res.get("geom_split", []) + res.get("geom", [])
        delete_geom = []
        if clear_inner or clear_outer:
            for elem in geom_cut:
                if hasattr(elem, "calc_center_median"):
                    center = elem.calc_center_median()
                elif hasattr(elem, "vert"):
                    center = elem.vert.co
                else:
                    continue
                side = (center.x - plane_co[0]) * plane_no[0] + (center.y - plane_co[1]) * plane_no[1] + (center.z - plane_co[2]) * plane_no[2]
                if clear_inner and side < 0:
                    delete_geom.append(elem)
                if clear_outer and side > 0:
                    delete_geom.append(elem)
        if delete_geom:
            bmesh.ops.delete(bm, geom=delete_geom, context="VERTS")
        bmesh.update_edit_mesh(obj.data)
        return ok_response(result={"bisect": True, "clear_inner": clear_inner, "clear_outer": clear_outer})
    except Exception as exc:
        return error_response(str(exc), code="internal_error")


def mesh_delete_by_index(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover

    obj, err = _ensure_edit_mode(bpy)
    if err:
        return err
    element = args.get("element")
    indices = args.get("indices", [])
    if element not in ("VERT", "EDGE", "FACE"):
        return error_response("element must be VERT/EDGE/FACE", code="bad_request")
    if not isinstance(indices, list) or not all(isinstance(i, int) for i in indices):
        return error_response("indices must be a list of integers", code="bad_request")
    bm = bmesh.from_edit_mesh(obj.data)
    try:
        delete_geom = []
        if element == "VERT":
            for idx in indices:
                if 0 <= idx < len(bm.verts):
                    delete_geom.append(bm.verts[idx])
        elif element == "EDGE":
            for idx in indices:
                if 0 <= idx < len(bm.edges):
                    delete_geom.append(bm.edges[idx])
        elif element == "FACE":
            for idx in indices:
                if 0 <= idx < len(bm.faces):
                    delete_geom.append(bm.faces[idx])
        bmesh.ops.delete(bm, geom=delete_geom, context="VERTS")
        bmesh.update_edit_mesh(obj.data)
        return ok_response(result={"deleted": True, "element": element, "count": len(delete_geom)})
    except Exception as exc:
        return error_response(str(exc), code="internal_error")


def mesh_translate_selection(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover

    obj, err = _ensure_edit_mode(bpy)
    if err:
        return err
    dx, dy, dz = args.get("dx"), args.get("dy"), args.get("dz")
    if not all(isinstance(v, (int, float)) for v in (dx, dy, dz)):
        return error_response("dx, dy, dz required", code="bad_request")
    delta = (float(dx), float(dy), float(dz))
    bm = bmesh.from_edit_mesh(obj.data)
    try:
        verts = [v for v in bm.verts if v.select]
        if not verts:
            return error_response("No selection", code="no_selection")
        for v in verts:
            v.co.x += delta[0]
            v.co.y += delta[1]
            v.co.z += delta[2]
        bmesh.update_edit_mesh(obj.data)
        return ok_response(result={"translated": True, "delta": list(delta), "selected_verts": len(verts)})
    except Exception as exc:
        return error_response(str(exc), code="internal_error")


def mesh_scale_selection(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover

    obj, err = _ensure_edit_mode(bpy)
    if err:
        return err
    sx, sy, sz = args.get("sx"), args.get("sy"), args.get("sz")
    if not all(isinstance(v, (int, float)) for v in (sx, sy, sz)):
        return error_response("sx, sy, sz required", code="bad_request")
    bm = bmesh.from_edit_mesh(obj.data)
    try:
        verts = [v for v in bm.verts if v.select]
        if not verts:
            return error_response("No selection", code="no_selection")
        if isinstance(args.get("pivot"), list) and len(args.get("pivot")) == 3:
            pivot = [float(x) for x in args["pivot"]]
        else:
            pivot = [sum(v.co[i] for v in verts) / len(verts) for i in range(3)]
        for v in verts:
            for i, scale in enumerate((float(sx), float(sy), float(sz))):
                v.co[i] = pivot[i] + (v.co[i] - pivot[i]) * scale
        bmesh.update_edit_mesh(obj.data)
        return ok_response(
            result={"scaled": True, "scale": [float(sx), float(sy), float(sz)], "pivot": pivot, "selected_verts": len(verts)}
        )
    except Exception as exc:
        return error_response(str(exc), code="internal_error")


def mesh_extrude_selection(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover

    obj, err = _ensure_edit_mode(bpy)
    if err:
        return err
    dx, dy, dz = args.get("dx"), args.get("dy"), args.get("dz")
    if not all(isinstance(v, (int, float)) for v in (dx, dy, dz)):
        return error_response("dx, dy, dz required", code="bad_request")
    delta = (float(dx), float(dy), float(dz))
    bm = bmesh.from_edit_mesh(obj.data)
    try:
        faces = [f for f in bm.faces if f.select]
        if not faces:
            return error_response("Unsupported selection (no faces)", code="unsupported_selection")
        res = bmesh.ops.extrude_face_region(bm, geom=faces)
        verts = [ele for ele in res["geom"] if isinstance(ele, bmesh.types.BMVert)]
        for v in verts:
            v.co.x += delta[0]
            v.co.y += delta[1]
            v.co.z += delta[2]
        bmesh.update_edit_mesh(obj.data)
        return ok_response(result={"extruded": True, "delta": list(delta)})
    except Exception as exc:
        return error_response(str(exc), code="internal_error")


def mesh_inset_selection(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover

    obj, err = _ensure_edit_mode(bpy)
    if err:
        return err
    thickness = float(args.get("thickness", 0.05))
    depth = float(args.get("depth", 0.0))
    bm = bmesh.from_edit_mesh(obj.data)
    try:
        faces = [f for f in bm.faces if f.select]
        if not faces:
            return error_response("No faces selected", code="no_selection")
        res = bmesh.ops.inset_region(bm, faces=faces, thickness=thickness, depth=0.0)
        new_faces = [f for f in res.get("faces", []) if isinstance(f, bmesh.types.BMFace)]
        if depth != 0.0:
            for f in new_faces:
                for v in f.verts:
                    v.co += f.normal.normalized() * depth
        bmesh.update_edit_mesh(obj.data)
        return ok_response(result={"inset": True, "thickness": thickness, "depth": depth})
    except Exception as exc:
        return error_response(str(exc), code="internal_error")


def mesh_select_by_normal(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover

    obj, err = _ensure_edit_mode(bpy)
    if err:
        return err
    axis = args.get("axis")
    if axis not in ("X", "Y", "Z"):
        return error_response("axis must be X/Y/Z", code="bad_request")
    sign = args.get("sign", 1)
    threshold = float(args.get("threshold", 0.9))
    extend = bool(args.get("extend", False))
    bm = bmesh.from_edit_mesh(obj.data)
    try:
        if not extend:
            for f in bm.faces:
                f.select_set(False)
        target = {"X": (1, 0, 0), "Y": (0, 1, 0), "Z": (0, 0, 1)}[axis]
        count = 0
        for f in bm.faces:
            dot = f.normal.x * target[0] + f.normal.y * target[1] + f.normal.z * target[2]
            if sign < 0:
                dot *= -1
            if dot >= threshold:
                f.select_set(True)
                count += 1
        bmesh.update_edit_mesh(obj.data)
        return ok_response(result={"selected": True, "element": "FACE", "count": count, "axis": axis, "sign": sign, "threshold": threshold})
    except Exception as exc:
        return error_response(str(exc), code="internal_error")


def mesh_duplicate_selection(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover

    obj, err = _ensure_edit_mode(bpy)
    if err:
        return err
    dx = float(args.get("dx", 0.0))
    dy = float(args.get("dy", 0.0))
    dz = float(args.get("dz", 0.0))
    bm = bmesh.from_edit_mesh(obj.data)
    try:
        geom = [v for v in bm.verts if v.select] + [e for e in bm.edges if e.select] + [f for f in bm.faces if f.select]
        if not geom:
            return error_response(
                "nothing selected",
                code="invalid_args",
                details={"tool": "blender-mesh-duplicate-selection", "reason": "nothing selected", "hint": "Select geometry before duplicating."},
            )
        res = bmesh.ops.duplicate(bm, geom=geom)
        geom_dupe = res.get("geom", [])
        verts_dupe = [g for g in geom_dupe if isinstance(g, bmesh.types.BMVert)]
        edges_dupe = [g for g in geom_dupe if isinstance(g, bmesh.types.BMEdge)]
        faces_dupe = [g for g in geom_dupe if isinstance(g, bmesh.types.BMFace)]
        if dx or dy or dz:
            bmesh.ops.translate(bm, vec=(dx, dy, dz), verts=verts_dupe)
        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)
        return ok_response(
            result={
                "duplicated": True,
                "delta": [dx, dy, dz],
                "new_verts": len(verts_dupe),
                "new_edges": len(edges_dupe),
                "new_faces": len(faces_dupe),
            }
        )
    except Exception as exc:
        return error_response(
            str(exc),
            code="internal_error",
            details={"tool": "blender-mesh-duplicate-selection", "reason": str(exc)},
        )


def _mesh_stats(mesh, max_items: int, include_selected: bool = True) -> Dict[str, Any]:
    stats: Dict[str, Any] = {
        "verts": len(mesh.vertices),
        "edges": len(mesh.edges),
        "faces": len(mesh.polygons),
    }
    try:
        mesh.calc_loop_triangles()
        stats["tris"] = len(mesh.loop_triangles)
    except Exception:
        pass
    if include_selected:
        stats["selected"] = {
            "verts": sum(1 for v in mesh.vertices[: max_items] if getattr(v, "select", False)),
            "edges": sum(1 for e in mesh.edges[: max_items] if getattr(e, "select", False)),
            "faces": sum(1 for p in mesh.polygons[: max_items] if getattr(p, "select", False)),
        }
    return stats


def _object_snapshot(obj, include_mesh_stats: bool, include_materials: bool, include_modifiers: bool, include_collections: bool, max_items: int, max_materials: int | None = None) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "name": obj.name,
        "type": obj.type,
        "visible_viewport": bool(getattr(obj, "visible_get", lambda: True)()),
        "hide_viewport": bool(getattr(obj, "hide_viewport", False)),
        "location": list(obj.location) if hasattr(obj, "location") else None,
        "rotation_euler": list(obj.rotation_euler) if hasattr(obj, "rotation_euler") else None,
        "scale": list(obj.scale) if hasattr(obj, "scale") else None,
        "dimensions": list(obj.dimensions) if hasattr(obj, "dimensions") else None,
    }
    if include_mesh_stats and obj.type == "MESH" and obj.data:
        try:
            data.setdefault("data", {})["mesh_stats"] = _mesh_stats(obj.data, max_items)
        except Exception:
            pass
    if include_materials:
        mats = []
        for slot in list(getattr(obj, "material_slots", []))[: (max_materials or max_items)]:
            mat = getattr(slot, "material", None)
            if mat:
                mats.append({"name": mat.name})
        data["materials"] = mats
    if include_modifiers:
        mods = []
        for mod in list(getattr(obj, "modifiers", []))[: max_items]:
            mods.append({"name": mod.name, "type": mod.type})
        data["modifiers"] = mods
    if include_collections:
        cols = [c.name for c in list(getattr(obj, "users_collection", []))[: max_items]]
        data["collections"] = cols
    return data


def scene_snapshot(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    include_mesh_stats = bool(args.get("include_mesh_stats", True))
    include_materials = bool(args.get("include_materials", True))
    include_collections = bool(args.get("include_collections", True))
    max_objects = int(args.get("max_objects", 200))
    max_materials = int(args.get("max_materials_per_object", 32))
    max_items = int(args.get("max_items_per_list", 5000))
    try:
        objs_payload = []
        for obj in list(bpy.data.objects)[:max_objects]:
            objs_payload.append(
                _object_snapshot(
                    obj,
                    include_mesh_stats=include_mesh_stats,
                    include_materials=include_materials,
                    include_modifiers=False,
                    include_collections=include_collections,
                    max_items=max_items,
                    max_materials=max_materials,
                )
            )
        ctx = bpy.context
        result = {
            "blender_version": getattr(bpy.app, "version_string", "unknown"),
            "is_background": bool(getattr(bpy.app, "background", False)),
            "has_window": bool(getattr(ctx, "window", None)),
            "context": {"mode": getattr(ctx, "mode", None), "active_object": ctx.view_layer.objects.active.name if ctx.view_layer.objects.active else None},
            "objects": objs_payload,
        }
        return ok_response(result=result)
    except Exception as exc:
        return error_response(
            str(exc),
            code="internal_error",
            details={"tool": "blender-scene-snapshot", "reason": str(exc)},
        )


def object_snapshot(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    name = args.get("name")
    if not isinstance(name, str):
        return error_response("name is required", code="bad_request")
    include_mesh_stats = bool(args.get("include_mesh_stats", True))
    include_materials = bool(args.get("include_materials", True))
    include_modifiers = bool(args.get("include_modifiers", True))
    include_collections = bool(args.get("include_collections", True))
    max_items = int(args.get("max_items_per_list", 5000))
    obj = bpy.data.objects.get(name)
    if obj is None:
        return error_response(
            f"Object '{name}' not found",
            code="not_found",
            details={"code": "not_found", "name": name},
        )
    try:
        snapshot = _object_snapshot(
            obj,
            include_mesh_stats=include_mesh_stats,
            include_materials=include_materials,
            include_modifiers=include_modifiers,
            include_collections=include_collections,
            max_items=max_items,
            max_materials=max_items,
        )
        return ok_response(result=snapshot)
    except Exception as exc:
        return error_response(
            str(exc),
            code="internal_error",
            details={"tool": "blender-object-snapshot", "reason": str(exc)},
        )


def capabilities(args: Dict[str, Any] | None = None) -> Dict[str, Any]:
    bpy = _require_bpy()

    def _op_status(op_id: str) -> Dict[str, Any]:
        parts = op_id.split(".")
        exists = False
        poll_ok = False
        reason: Optional[str] = None
        if len(parts) == 2:
            space, name = parts
            target = getattr(getattr(bpy.ops, space, None), name, None)
            exists = target is not None
            if exists and hasattr(target, "poll"):
                try:
                    poll_ok = bool(target.poll())
                except Exception as exc:  # pragma: no cover - runtime dependent
                    poll_ok = False
                    reason = str(exc)
        else:
            reason = "invalid op id"
        return {"id": op_id, "exists": exists, "poll_ok": poll_ok, "reason": reason}

    try:
        ctx = bpy.context
        result = {
            "blender_version": getattr(bpy.app, "version_string", "unknown"),
            "is_background": bool(getattr(bpy.app, "background", False)),
            "has_window": bool(getattr(ctx, "window", None)),
            "context": {
                "mode": getattr(ctx, "mode", "UNKNOWN"),
                "active_object": ctx.view_layer.objects.active.name if ctx.view_layer.objects.active else None,
            },
            "ops": [
                _op_status("mesh.loop_select"),
                _op_status("mesh.ring_select"),
                _op_status("mesh.select_linked"),
                _op_status("mesh.bevel"),
                _op_status("mesh.loopcut_slide"),
            ],
        }
        return ok_response(result=result)
    except Exception as exc:  # pragma: no cover - defensive
        return error_response(str(exc), code="internal_error")


def validate_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    name = args.get("name")
    if not isinstance(name, str):
        return error_response("name is required", code="bad_request")

    tool_to_ops = {
        "blender-mesh-select-loop": ["mesh.loop_select"],
        "blender-mesh-select-ring": ["mesh.ring_select"],
        "blender-mesh-select-boundary": ["mesh.select_boundary_loop"],
        "blender-mesh-select-linked": ["mesh.select_linked"],
        "blender-mesh-select-non-manifold": ["mesh.select_non_manifold"],
        "blender-mesh-loop-cut": ["mesh.loopcut_slide"],
        "blender-mesh-bevel": ["mesh.bevel"],
        "blender-mesh-extrude": ["mesh.extrude_region_move"],
        "blender-mesh-inset": ["mesh.inset"],
        "blender-mesh-subdivide": ["mesh.subdivide"],
        "blender-mesh-delete": ["mesh.delete"],
    }

    ops = tool_to_ops.get(name, [])
    if not ops:
        return ok_response(
            result={
                "name": name,
                "supported": False,
                "class": "OPS_MISSING",
                "details": {"reason": "unknown tool"},
            }
        )

    def _op_exists(op_id: str) -> Dict[str, Any]:
        space, op_name = op_id.split(".")
        target = getattr(getattr(bpy.ops, space, None), op_name, None)
        exists = target is not None
        poll_ok = False
        reason = None
        if exists and hasattr(target, "poll"):
            try:
                poll_ok = bool(target.poll())
            except Exception as exc:  # pragma: no cover
                poll_ok = False
                reason = str(exc)
        return {"id": op_id, "exists": exists, "poll_ok": poll_ok, "reason": reason}

    statuses = [_op_exists(op) for op in ops]
    any_missing = any(not s["exists"] for s in statuses)
    any_poll_fail = any(s["exists"] and not s["poll_ok"] for s in statuses)

    if any_missing:
        classification = "OPS_MISSING"
        supported = False
        reason = "operator missing"
    elif any_poll_fail:
        classification = "OPS_VIEW3D_REQUIRED"
        supported = False
        reason = "operator poll failed (likely needs View3D)"
    else:
        classification = "OPS_SAFE"
        supported = True
        reason = "operators available"

    return ok_response(
        result={
            "name": name,
            "supported": supported,
            "class": classification,
            "details": {"ops": statuses, "reason": reason},
        }
    )
