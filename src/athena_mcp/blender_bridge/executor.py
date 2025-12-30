from __future__ import annotations

import os
import re
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


def _get_object(bpy, name: str, type_filter: str | None = None):
    obj = bpy.data.objects.get(name)
    if obj is None:
        return None, error_response(f"Object '{name}' not found", code="not_found")
    if type_filter and obj.type != type_filter:
        return None, error_response(f"Object '{name}' is not {type_filter}", code="invalid_type")
    return obj, None


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


def add_cylinder(args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    bpy = _require_bpy()

    args = args or {}
    name = args.get("name")
    vertices = int(args.get("vertices", 32))
    radius = float(args.get("radius", 1.0))
    depth = float(args.get("depth", 2.0))
    location = args.get("location", [0, 0, 0])
    end_fill_type = args.get("end_fill_type", "NGON")

    try:
        # Call Blender operator
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=vertices,
            radius=radius,
            depth=depth,
            location=location,
            end_fill_type=end_fill_type,
        )

        # Get created object
        obj = bpy.context.active_object

        # Rename if name provided
        if name:
            obj.name = name

        # Return object metadata
        return ok_response(
            result={
                "name": obj.name,
                "type": obj.type,
                "location": list(obj.location),
                "vertex_count": len(obj.data.vertices),
                "face_count": len(obj.data.polygons),
            }
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def add_sphere(args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    bpy = _require_bpy()

    args = args or {}
    name = args.get("name")
    radius = float(args.get("radius", 1.0))
    location = args.get("location", [0, 0, 0])
    segments = int(args.get("segments", 32))
    ring_count = int(args.get("ring_count", 16))

    try:
        # Call Blender operator
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=segments,
            ring_count=ring_count,
            radius=radius,
            location=location,
        )

        # Get created object
        obj = bpy.context.active_object

        # Rename if name provided
        if name:
            obj.name = name

        # Return object metadata
        return ok_response(
            result={
                "name": obj.name,
                "type": obj.type,
                "location": list(obj.location),
                "vertex_count": len(obj.data.vertices),
                "face_count": len(obj.data.polygons),
            }
        )
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


def exec_python(args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute arbitrary Python code in Blender context for API testing.

    WARNING: This is a TESTING tool - code is executed without sandboxing.
    Only use for API exploration and validation.
    """
    bpy = _require_bpy()
    code = args.get("code")

    if not code or not isinstance(code, str):
        return error_response("code parameter required (string)", code="bad_request")

    try:
        # Create a namespace with bpy and common imports
        namespace = {
            "bpy": bpy,
            "bmesh": __import__("bmesh"),
            "mathutils": __import__("mathutils"),
        }

        # Execute code and capture result
        exec(code, namespace)

        # Extract result if it was set
        result = namespace.get("result", None)

        return ok_response(
            result={
                "executed": True,
                "result": result,
                "namespace_keys": [k for k in namespace.keys() if not k.startswith("__")],
            }
        )
    except Exception as exc:
        return error_response(
            f"Python execution failed: {str(exc)}",
            code="execution_error",
            details={"exception_type": type(exc).__name__},
        )


# ---------------------------------------------------------------------------
# New tools (object ops, transforms, modifiers, mesh advanced, materials, curves)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# New tools (object ops, transforms, modifiers, mesh advanced, materials, curves)
# ---------------------------------------------------------------------------


def object_join(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    target_name = args.get("target_name")
    sel_mesh = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
    if target_name:
        target, err = _get_object(bpy, target_name, "MESH")
        if err:
            return err
        bpy.context.view_layer.objects.active = target
        if target not in bpy.context.selected_objects:
            target.select_set(True)
        if target not in sel_mesh:
            sel_mesh.append(target)
    if len(sel_mesh) < 2:
        return error_response("Need at least two mesh objects selected", code="no_selection")
    active = bpy.context.view_layer.objects.active
    if active is None or active.type != "MESH":
        bpy.context.view_layer.objects.active = sel_mesh[0]
        active = sel_mesh[0]
    before_vert = sum(len(o.data.vertices) for o in sel_mesh)
    before_face = sum(len(o.data.polygons) for o in sel_mesh)
    try:
        err = _ensure_mode(bpy, "OBJECT")
        if err:
            return err
        bpy.ops.object.join()
        joined = bpy.context.view_layer.objects.active or active
        return ok_response(
            result={
                "joined_object": joined.name,
                "vertex_count": len(joined.data.vertices),
                "face_count": len(joined.data.polygons),
                "vertex_count_before": before_vert,
                "face_count_before": before_face,
            }
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def object_separate(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    name = args.get("name")
    sep_type = args.get("type", "SELECTED")
    obj, err = _get_object(bpy, name, "MESH") if name else _active_mesh(bpy)
    if err:
        return err
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    before = set(bpy.data.objects.keys())
    try:
        err = _ensure_mode(bpy, "EDIT")
        if err:
            return err
        bpy.ops.mesh.separate(type=sep_type)
        bpy.ops.object.mode_set(mode="OBJECT")
        after = set(bpy.data.objects.keys())
        new_objects = list(after - before)
        return ok_response(result={"original_object": obj.name, "new_objects": new_objects, "count": len(new_objects)})
    except Exception as exc:
        bpy.ops.object.mode_set(mode="OBJECT")
        return error_response(str(exc), code="bridge_error")


def object_shade(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    smooth = bool(args.get("smooth", True))
    try:
        err = _ensure_mode(bpy, "OBJECT")
        if err:
            return err
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        if smooth:
            bpy.ops.object.shade_smooth()
        else:
            bpy.ops.object.shade_flat()
        return ok_response(
            result={
                "object_name": obj.name,
                "smooth": smooth,
                "polygons_affected": len(obj.data.polygons),
            }
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def object_rotate(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import math
    from mathutils import Matrix, Vector  # type: ignore  # pragma: no cover

    args = args or {}
    obj, err = _get_object(bpy, args.get("name"))
    if err:
        return err
    angle = float(args.get("angle"))
    axis = args.get("axis")
    if axis not in ("X", "Y", "Z"):
        return error_response("axis must be X/Y/Z", code="bad_request")
    angle = max(-360.0, min(360.0, angle))
    pivot = args.get("pivot")
    try:
        err = _ensure_mode(bpy, "OBJECT")
        if err:
            return err
        bpy.context.view_layer.objects.active = obj
        if pivot and isinstance(pivot, (list, tuple)) and len(pivot) == 3:
            pivot_vec = Vector(pivot)
            rot = Matrix.Rotation(math.radians(angle), 4, axis)
            obj.matrix_world = Matrix.Translation(pivot_vec) @ rot @ Matrix.Translation(-pivot_vec) @ obj.matrix_world
        else:
            idx = "XYZ".index(axis)
            eul = obj.rotation_euler
            eul[idx] = math.radians(angle)
            obj.rotation_euler = eul
        return ok_response(result={"object_name": obj.name, "rotation_euler": list(obj.rotation_euler)})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def object_mirror(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover

    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    axis = args.get("axis")
    if axis not in ("X", "Y", "Z"):
        return error_response("axis must be X/Y/Z", code="bad_request")
    method = args.get("method", "GEOMETRY")
    idx = "XYZ".index(axis)
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        if method == "SCALE":
            err = _ensure_mode(bpy, "OBJECT")
            if err:
                return err
            obj.scale[idx] = -obj.scale[idx] if obj.scale[idx] != 0 else -1.0
        else:
            err = _ensure_mode(bpy, "EDIT")
            if err:
                return err
            bm = bmesh.from_edit_mesh(obj.data)
            for v in bm.verts:
                v.co[idx] = -v.co[idx]
            bmesh.update_edit_mesh(obj.data, loop_triangles=False)
            bpy.ops.object.mode_set(mode="OBJECT")
        return ok_response(result={"object_name": obj.name, "method_used": method, "axis": axis})
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


def object_snap(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("name"))
    if err:
        return err
    target = args.get("target")
    grid_size = float(args.get("grid_size", 1.0))
    grid_size = max(0.001, grid_size)
    try:
        err = _ensure_mode(bpy, "OBJECT")
        if err:
            return err
        loc = obj.location.copy()
        if target == "GRID":
            obj.location = loc.copy()
            for i in range(3):
                obj.location[i] = round(loc[i] / grid_size) * grid_size
        elif target == "CURSOR":
            obj.location = bpy.context.scene.cursor.location.copy()
        elif target == "OBJECT":
            tgt, terr = _get_object(bpy, args.get("target_name"))
            if terr:
                return terr
            obj.location = tgt.location.copy()
        else:
            return error_response("invalid target", code="bad_request")
        return ok_response(result={"object_name": obj.name, "new_location": list(obj.location)})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def modifier_apply(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    mod_name = args.get("modifier")
    if not mod_name or mod_name not in obj.modifiers:
        return error_response("Modifier not found", code="not_found")
    vert_before = len(obj.data.vertices)
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "OBJECT")
        if err:
            return err
        bpy.ops.object.modifier_apply(modifier=mod_name)
        return ok_response(
            result={
                "object_name": obj.name,
                "modifier_applied": mod_name,
                "vertex_count_before": vert_before,
                "vertex_count_after": len(obj.data.vertices),
            }
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def modifier_move(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    mod_name = args.get("modifier")
    direction = args.get("direction")
    if mod_name not in obj.modifiers:
        return error_response("Modifier not found", code="not_found")
    if direction not in ("UP", "DOWN"):
        return error_response("direction must be UP/DOWN", code="bad_request")
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "OBJECT")
        if err:
            return err
        op = bpy.ops.object.modifier_move_up if direction == "UP" else bpy.ops.object.modifier_move_down
        result = op(modifier=mod_name)
        if "FINISHED" not in result:
            return error_response("Cannot move modifier", code="invalid_state")
        stack = [m.name for m in obj.modifiers]
        return ok_response(result={"object_name": obj.name, "modifier": mod_name, "new_index": stack.index(mod_name), "stack": stack})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def modifier_remove(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    mod_name = args.get("modifier")
    if mod_name not in obj.modifiers:
        return error_response("Modifier not found", code="not_found")
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "OBJECT")
        if err:
            return err
        bpy.ops.object.modifier_remove(modifier=mod_name)
        return ok_response(
            result={
                "object_name": obj.name,
                "modifier_removed": mod_name,
                "remaining_modifiers": [m.name for m in obj.modifiers],
            }
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def mesh_spin(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import math
    import bmesh  # type: ignore  # pragma: no cover
    from mathutils import Vector  # type: ignore  # pragma: no cover

    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    steps = int(args.get("steps", 12))
    steps = max(2, min(512, steps))
    angle = float(args.get("angle", 360))
    angle = max(0.0, min(360.0, angle))
    axis = args.get("axis", "Z")
    if axis not in ("X", "Y", "Z"):
        return error_response("axis must be X/Y/Z", code="bad_request")
    center = args.get("center", [0, 0, 0])
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "EDIT")
        if err:
            return err
        bm = bmesh.from_edit_mesh(obj.data)
        before = len(bm.verts)
        axis_vec = Vector((1, 0, 0)) if axis == "X" else Vector((0, 1, 0)) if axis == "Y" else Vector((0, 0, 1))
        bpy.ops.mesh.spin(steps=steps, angle=math.radians(angle), axis=axis_vec, center=center)
        bmesh.update_edit_mesh(obj.data, loop_triangles=False)
        after = len(bm.verts)
        bpy.ops.object.mode_set(mode="OBJECT")
        return ok_response(result={"object_name": obj.name, "vertex_count_before": before, "vertex_count_after": after})
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


def mesh_screw(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover

    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    steps = int(args.get("steps", 16))
    steps = max(2, min(512, steps))
    turns = int(args.get("turns", 1))
    turns = max(1, min(100, turns))
    axis = args.get("axis", "Z")
    if axis not in ("X", "Y", "Z"):
        return error_response("axis must be X/Y/Z", code="bad_request")
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "EDIT")
        if err:
            return err
        bm = bmesh.from_edit_mesh(obj.data)
        before = len(bm.verts)
        bpy.ops.mesh.screw(steps=steps, turns=turns, axis=axis)
        bmesh.update_edit_mesh(obj.data, loop_triangles=False)
        after = len(bm.verts)
        bpy.ops.object.mode_set(mode="OBJECT")
        return ok_response(result={"object_name": obj.name, "vertex_count_before": before, "vertex_count_after": after})
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


def mesh_normals(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover

    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    operation = args.get("operation")
    inside = bool(args.get("inside", False))
    if operation not in ("RECALCULATE", "FLIP"):
        return error_response("operation must be RECALCULATE/FLIP", code="bad_request")
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "EDIT")
        if err:
            return err
        bm = bmesh.from_edit_mesh(obj.data)
        selected_faces = [f for f in bm.faces if f.select]
        if not selected_faces:
            return error_response("No selected faces", code="no_selection")
        if operation == "RECALCULATE":
            bpy.ops.mesh.normals_make_consistent(inside=inside)
        else:
            bpy.ops.mesh.flip_normals()
        affected = len(selected_faces)
        bpy.ops.object.mode_set(mode="OBJECT")
        return ok_response(result={"object_name": obj.name, "operation": operation, "faces_affected": affected})
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


def material_assign(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    mat_name = args.get("material_name")
    if not mat_name:
        return error_response("material_name required", code="bad_request")
    slot_index = int(args.get("slot_index", 0))
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        return error_response(f"Material '{mat_name}' not found", code="not_found")
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "EDIT")
        if err:
            return err
        if mat.name not in obj.data.materials:
            obj.data.materials.append(mat)
        slot_index = max(0, min(slot_index, len(obj.data.materials) - 1))
        obj.active_material_index = slot_index
        import bmesh  # type: ignore  # pragma: no cover

        bm = bmesh.from_edit_mesh(obj.data)
        faces_selected = [f for f in bm.faces if f.select]
        if not faces_selected:
            return error_response("No faces selected", code="no_selection")
        bpy.ops.object.material_slot_assign()
        bpy.ops.object.mode_set(mode="OBJECT")
        return ok_response(
            result={
                "object_name": obj.name,
                "material_name": mat.name,
                "slot_index": slot_index,
                "faces_assigned": len(faces_selected),
            }
        )
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


def material_create(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    name = args.get("name")
    if not name:
        return error_response("name required", code="bad_request")
    color = args.get("color", [0.8, 0.8, 0.8, 1.0])
    metallic = max(0.0, min(1.0, float(args.get("metallic", 0.0))))
    roughness = max(0.0, min(1.0, float(args.get("roughness", 0.5))))
    try:
        base = name
        final_name = base
        suffix = 1
        while bpy.data.materials.get(final_name):
            final_name = f"{base}.{suffix:03d}"
            suffix += 1
        mat = bpy.data.materials.new(final_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        principled = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
        if principled:
            principled.inputs["Base Color"].default_value = [
                max(0.0, min(1.0, float(v))) for v in (color + [1.0, 1.0, 1.0, 1.0])[:4]
            ]
            principled.inputs["Metallic"].default_value = metallic
            principled.inputs["Roughness"].default_value = roughness
        return ok_response(
            result={
                "material_name": mat.name,
                "color": list(principled.inputs["Base Color"].default_value) if principled else color,
                "metallic": metallic,
                "roughness": roughness,
            }
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def curve_primitive(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    curve_type = args.get("type")
    if curve_type not in ("BEZIER_CURVE", "BEZIER_CIRCLE", "NURBS_CURVE", "NURBS_CIRCLE"):
        return error_response("invalid curve type", code="bad_request")
    location = args.get("location", [0, 0, 0])
    radius = float(args.get("radius", 1.0))
    radius = max(0.001, radius)
    name = args.get("name")
    try:
        err = _ensure_mode(bpy, "OBJECT")
        if err:
            return err
        op_map = {
            "BEZIER_CURVE": bpy.ops.curve.primitive_bezier_curve_add,
            "BEZIER_CIRCLE": bpy.ops.curve.primitive_bezier_circle_add,
            "NURBS_CURVE": bpy.ops.curve.primitive_nurbs_curve_add,
            "NURBS_CIRCLE": bpy.ops.curve.primitive_nurbs_circle_add,
        }
        op = op_map[curve_type]
        op(radius=radius, location=location)
        obj = bpy.context.active_object
        if name:
            obj.name = name
        return ok_response(result={"object_name": obj.name, "curve_type": curve_type, "location": list(obj.location)})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def curve_convert(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "CURVE")
    if err:
        return err
    keep = bool(args.get("keep_original", False))
    try:
        err = _ensure_mode(bpy, "OBJECT")
        if err:
            return err
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        source_obj = obj
        if keep:
            bpy.ops.object.duplicate()
            source_obj = bpy.context.active_object
        bpy.ops.object.convert(target="MESH")
        mesh_obj = bpy.context.active_object
        return ok_response(
            result={
                "object_name": mesh_obj.name,
                "vertex_count": len(mesh_obj.data.vertices),
                "original_kept": keep,
            }
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


# ---------------------------------------------------------------------------
# Batch P0 - transformations avancées (10 tools incl. modifiers)
# ---------------------------------------------------------------------------


def object_scale(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    sx = float(args.get("sx"))
    sy = float(args.get("sy", sx))
    sz = float(args.get("sz", sx))
    uniform = bool(args.get("uniform", False))
    if uniform:
        sy = sz = sx
    # Clamp
    def _clamp(v: float) -> float:
        return max(0.001, min(1000.0, v))
    sx, sy, sz = _clamp(sx), _clamp(sy), _clamp(sz)
    try:
        err = _ensure_mode(bpy, "OBJECT")
        if err:
            return err
        obj.scale = (sx, sy, sz)
        return ok_response(result={"name": obj.name, "scale": list(obj.scale), "dimensions": list(obj.dimensions)})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def object_apply_transform(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("name"))
    if err:
        return err
    flags = {
        "location": bool(args.get("location", False)),
        "rotation": bool(args.get("rotation", False)),
        "scale": bool(args.get("scale", False)),
        "properties": bool(args.get("properties", False)),
    }
    if not any(flags.values()):
        return error_response("No transform to apply", code="bad_request")
    try:
        err = _ensure_mode(bpy, "OBJECT")
        if err:
            return err
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(**flags)
        return ok_response(
            result={
                "name": obj.name,
                "applied": flags,
                "final_transform": {
                    "location": list(obj.location),
                    "rotation": list(obj.rotation_euler),
                    "scale": list(obj.scale),
                },
            }
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def object_origin_set(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("name"))
    if err:
        return err
    origin_type = args.get("type")
    center = args.get("center", "MEDIAN")
    map_type = {
        "GEOMETRY": "ORIGIN_GEOMETRY",
        "CURSOR": "ORIGIN_CURSOR",
        "CENTER_MASS": "ORIGIN_CENTER_OF_MASS",
        "CENTER_VOLUME": "ORIGIN_CENTER_OF_VOLUME",
        "GEOMETRY_ORIGIN": "GEOMETRY_ORIGIN",
    }
    if origin_type not in map_type:
        return error_response("Invalid origin type", code="bad_request")
    try:
        err = _ensure_mode(bpy, "OBJECT")
        if err:
            return err
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.origin_set(type=map_type[origin_type], center=center)
        return ok_response(
            result={"name": obj.name, "origin_type": origin_type, "center": center, "new_location": list(obj.location)}
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def object_parent(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    child, err = _get_object(bpy, args.get("child_name"))
    if err:
        return err
    parent_name = args.get("parent_name")
    keep = bool(args.get("keep_transform", True))
    ptype = args.get("type", "OBJECT")
    if parent_name is not None and parent_name == child.name:
        return error_response("Cannot parent to self", code="invalid_request")
    try:
        err = _ensure_mode(bpy, "OBJECT")
        if err:
            return err
        bpy.ops.object.select_all(action="DESELECT")
        child.select_set(True)
        bpy.context.view_layer.objects.active = child
        if parent_name:
            parent, perr = _get_object(bpy, parent_name)
            if perr:
                return perr
            parent.select_set(True)
            bpy.context.view_layer.objects.active = parent
            bpy.ops.object.parent_set(type=ptype, keep_transform=keep)
            relationship = "set"
            result_parent = parent.name
        else:
            bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM" if keep else "CLEAR")
            relationship = "cleared"
            result_parent = None
        return ok_response(
            result={
                "child": child.name,
                "parent": result_parent,
                "keep_transform": keep,
                "relationship": relationship,
                "child_location": list(child.location),
            }
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def object_clear_transform(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("name"))
    if err:
        return err
    flags = {
        "location": bool(args.get("location", False)),
        "rotation": bool(args.get("rotation", False)),
        "scale": bool(args.get("scale", False)),
        "delta": bool(args.get("delta", False)),
    }
    if not any(flags.values()):
        return error_response("No transform to clear", code="bad_request")
    try:
        err = _ensure_mode(bpy, "OBJECT")
        if err:
            return err
        if flags["location"]:
            obj.location = (0.0, 0.0, 0.0)
        if flags["rotation"]:
            obj.rotation_euler = (0.0, 0.0, 0.0)
        if flags["scale"]:
            obj.scale = (1.0, 1.0, 1.0)
        if flags["delta"]:
            obj.delta_location = (0.0, 0.0, 0.0)
            obj.delta_rotation_euler = (0.0, 0.0, 0.0)
            obj.delta_scale = (1.0, 1.0, 1.0)
        return ok_response(
            result={
                "name": obj.name,
                "cleared": flags,
                "final_transform": {
                    "location": list(obj.location),
                    "rotation": list(obj.rotation_euler),
                    "scale": list(obj.scale),
                },
            }
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def mesh_rotate_selection(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover
    from mathutils import Matrix, Vector  # type: ignore  # pragma: no cover
    import math

    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    angle = args.get("angle")
    axis = args.get("axis")
    euler_xyz = args.get("euler_xyz")
    pivot = args.get("pivot")
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "EDIT")
        if err:
            return err
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        selected = [v for v in bm.verts if v.select]
        if not selected:
            return error_response("No selection", code="no_selection")
        if euler_xyz:
            if not isinstance(euler_xyz, (list, tuple)) or len(euler_xyz) != 3:
                return error_response("Invalid euler_xyz", code="bad_request")
            rx, ry, rz = [math.radians(float(v)) for v in euler_xyz]
            rot_mat = Matrix.Rotation(rz, 3, "Z") @ Matrix.Rotation(ry, 3, "Y") @ Matrix.Rotation(rx, 3, "X")
        else:
            if axis not in ("X", "Y", "Z"):
                return error_response("axis must be X/Y/Z", code="bad_request")
            if angle is None:
                return error_response("angle required", code="bad_request")
            angle_val = max(-360.0, min(360.0, float(angle)))
            rot_mat = Matrix.Rotation(math.radians(angle_val), 3, axis)
        if pivot is None:
            pivot_vec = sum((v.co for v in selected), Vector()) / len(selected)
        else:
            if not isinstance(pivot, (list, tuple)) or len(pivot) != 3:
                return error_response("Invalid pivot", code="bad_request")
            pivot_vec = Vector(pivot)
        for v in selected:
            v.co = pivot_vec + rot_mat @ (v.co - pivot_vec)
        bmesh.update_edit_mesh(obj.data, loop_triangles=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        return ok_response(
            result={
                "name": obj.name,
                "rotated_verts": len(selected),
                "angle": angle if euler_xyz is None else None,
                "axis": axis if euler_xyz is None else None,
                "pivot": list(pivot_vec),
                "euler_xyz": euler_xyz,
            }
        )
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


def object_duplicate(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    src, err = _get_object(bpy, args.get("name"))
    if err:
        return err
    linked = bool(args.get("linked", False))
    offset = args.get("offset", [0, 0, 0])
    new_name = args.get("new_name")
    collection_name = args.get("collection")
    try:
        err = _ensure_mode(bpy, "OBJECT")
        if err:
            return err
        # Resolve collection
        target_coll = bpy.context.collection
        if collection_name:
            target_coll = bpy.data.collections.get(collection_name)
            if target_coll is None:
                return error_response("Invalid collection", code="not_found")
        dup = src.copy()
        if not linked:
            dup.data = src.data.copy()
        if new_name:
            base = new_name
            final = base
            suffix = 1
            while bpy.data.objects.get(final):
                final = f"{base}.{suffix:03d}"
                suffix += 1
            dup.name = final
        target_coll.objects.link(dup)
        if isinstance(offset, (list, tuple)) and len(offset) == 3:
            dup.location = (dup.location.x + float(offset[0]), dup.location.y + float(offset[1]), dup.location.z + float(offset[2]))
        data_shared = dup.data == src.data
        return ok_response(
            result={
                "source": src.name,
                "duplicate": dup.name,
                "linked": linked,
                "location": list(dup.location),
                "collection": target_coll.name,
                "data_shared": data_shared,
            }
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def modifier_add(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("name"))
    if err:
        return err
    mod_name = args.get("modifier_name")
    mod_type = args.get("modifier_type")
    if not mod_name or not mod_type:
        return error_response("modifier_name and modifier_type required", code="bad_request")
    if obj.modifiers.get(mod_name):
        return error_response("Modifier name exists", code="conflict")
    try:
        err = _ensure_mode(bpy, "OBJECT")
        if err:
            return err
        mod = obj.modifiers.new(name=mod_name, type=mod_type)
        return ok_response(result={"name": obj.name, "modifier": mod.name, "type": mod.type, "index": len(obj.modifiers) - 1})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def _set_modifier_value(mod, attr: str, value):
    if hasattr(mod, attr):
        try:
            setattr(mod, attr, value)
        except Exception:
            pass


def modifier_configure(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("name"))
    if err:
        return err
    mod_name = args.get("modifier_name")
    params = args.get("params") or {}
    mod = obj.modifiers.get(mod_name)
    if mod is None:
        return error_response("Modifier not found", code="not_found")
    try:
        err = _ensure_mode(bpy, "OBJECT")
        if err:
            return err
        mtype = mod.type
        # Generic setter with some per-type clamps
        if mtype == "ARRAY":
            if "count" in params:
                mod.count = max(1, min(10000, int(params["count"])))
            if "relative_offset_displace" in params:
                mod.relative_offset_displace = params["relative_offset_displace"]
            if "constant_offset_displace" in params:
                mod.constant_offset_displace = params["constant_offset_displace"]
            if "use_constant_offset" in params:
                mod.use_constant_offset = bool(params["use_constant_offset"])
            if "use_merge_vertices" in params:
                mod.use_merge_vertices = bool(params["use_merge_vertices"])
            if "merge_threshold" in params:
                mod.merge_threshold = float(params["merge_threshold"])
        elif mtype == "MIRROR":
            for key, attr in [
                ("use_axis", "use_axis"),
                ("use_bisect_axis", "use_bisect_axis"),
            ]:
                if key in params:
                    seq = params[key]
                    if isinstance(seq, (list, tuple)) and len(seq) == 3:
                        setattr(mod, attr, seq)
            if "use_clip" in params:
                mod.use_clip = bool(params["use_clip"])
            if "use_mirror_merge" in params:
                mod.use_mirror_merge = bool(params["use_mirror_merge"])
            if "merge_threshold" in params:
                mod.merge_threshold = float(params["merge_threshold"])
            if "mirror_object" in params:
                mo = bpy.data.objects.get(params["mirror_object"]) if params["mirror_object"] else None
                mod.mirror_object = mo
        elif mtype == "SOLIDIFY":
            for k in ["thickness", "offset", "use_even_offset", "use_quality_normals", "use_rim", "use_rim_only"]:
                if k in params:
                    _set_modifier_value(mod, k, params[k])
        elif mtype == "BOOLEAN":
            for k in ["operation", "solver", "use_self", "use_hole_tolerant"]:
                if k in params:
                    _set_modifier_value(mod, k, params[k])
            if "object" in params:
                mo = bpy.data.objects.get(params["object"])
                if mo is None:
                    return error_response("Referenced object not found", code="not_found")
                mod.object = mo
        elif mtype == "SUBSURF":
            for k in ["levels", "render_levels", "subdivision_type", "use_creases", "quality"]:
                if k in params:
                    _set_modifier_value(mod, k, params[k])
        elif mtype == "BEVEL":
            for k in ["width", "segments", "profile", "limit_method", "angle_limit", "use_clamp_overlap", "offset_type"]:
                if k in params:
                    _set_modifier_value(mod, k, params[k])
        elif mtype == "SCREW":
            for k in ["angle", "steps", "render_steps", "iterations", "screw_offset", "use_smooth_shade", "use_merge_vertices", "merge_threshold"]:
                if k in params:
                    _set_modifier_value(mod, k, params[k])
        elif mtype == "SIMPLE_DEFORM":
            for k in ["deform_method", "angle", "deform_axis", "lock_x", "lock_y"]:
                if k in params:
                    _set_modifier_value(mod, k, params[k])
            if "origin" in params:
                mo = bpy.data.objects.get(params["origin"]) if params["origin"] else None
                mod.origin = mo
        else:
            # fallback generic set
            for k, v in params.items():
                _set_modifier_value(mod, k, v)
        return ok_response(result={"name": obj.name, "modifier": mod.name, "type": mod.type, "configured_params": params})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def modifier_configure_array(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import math
    args = args or {}
    obj, err = _get_object(bpy, args.get("name"))
    if err:
        return err
    mod_name = args.get("modifier_name")
    pattern = args.get("pattern", "LINEAR")
    count = int(args.get("count", 5))
    offset = args.get("offset", [1.2, 0.0, 0.0])
    grid_counts = args.get("grid_counts")
    use_merge = bool(args.get("use_merge", False))
    merge_threshold = float(args.get("merge_threshold", 0.01))
    offset_object = args.get("offset_object")
    curve_object = args.get("curve_object")
    mod = obj.modifiers.get(mod_name)
    if mod is None or mod.type != "ARRAY":
        return error_response("Modifier not ARRAY type", code="invalid_modifier")
    try:
        err = _ensure_mode(bpy, "OBJECT")
        if err:
            return err
        count = max(1, min(10000, count))
        if pattern == "LINEAR":
            mod.count = count
            mod.relative_offset_displace = offset
            mod.use_relative_offset = True
            mod.use_object_offset = False
        elif pattern == "CIRCULAR":
            if not offset_object:
                return error_response("Offset object required for CIRCULAR", code="bad_request")
            empty = bpy.data.objects.get(offset_object)
            if empty is None:
                return error_response("Offset object not found", code="not_found")
            mod.count = count
            mod.use_object_offset = True
            mod.offset_object = empty
            # rotate empty for evenly spaced; not altering here to avoid side-effects
        elif pattern == "GRID":
            if not grid_counts or len(grid_counts) != 2:
                return error_response("grid_counts required [nx, ny]", code="bad_request")
            nx, ny = grid_counts
            nx = max(1, int(nx))
            ny = max(1, int(ny))
            mod.count = nx
            mod.relative_offset_displace = offset
            mod.use_relative_offset = True
            # second array on Y if exists
        elif pattern == "CURVE_FIT":
            if not curve_object:
                return error_response("curve_object required for CURVE_FIT", code="bad_request")
            curve = bpy.data.objects.get(curve_object)
            if curve is None or curve.type != "CURVE":
                return error_response("Curve object not found", code="not_found")
            mod.fit_type = "FIT_CURVE"
            mod.curve = curve
            mod.count = count
        else:  # CUSTOM
            pass
        mod.use_merge_vertices = use_merge
        mod.merge_threshold = merge_threshold
        return ok_response(
            result={
                "name": obj.name,
                "modifier": mod.name,
                "pattern": pattern,
                "count": mod.count,
                "offset": list(mod.relative_offset_displace),
                "configuration": "success",
            }
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def modifier_configure_mirror(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("name"))
    if err:
        return err
    mod_name = args.get("modifier_name")
    mod = obj.modifiers.get(mod_name)
    if mod is None or mod.type != "MIRROR":
        return error_response("Modifier not MIRROR", code="invalid_modifier")
    use_axis = args.get("use_axis", [True, False, False])
    use_bisect = args.get("use_bisect_axis", [False, False, False])
    use_bisect_flip = args.get("use_bisect_flip_axis", [False, False, False])
    merge_threshold = float(args.get("merge_threshold", 0.001))
    merge_threshold = max(0.0, min(1.0, merge_threshold))
    mirror_object = args.get("mirror_object")
    use_mirror_u = bool(args.get("use_mirror_u", False))
    use_mirror_v = bool(args.get("use_mirror_v", False))
    mirror_offset_u = float(args.get("mirror_offset_u", 0.0))
    mirror_offset_v = float(args.get("mirror_offset_v", 0.0))
    try:
        err = _ensure_mode(bpy, "OBJECT")
        if err:
            return err
        if not any(use_axis):
            return error_response("No axis enabled", code="bad_request")
        if isinstance(use_axis, (list, tuple)) and len(use_axis) == 3:
            mod.use_axis = tuple(bool(v) for v in use_axis)
        if isinstance(use_bisect, (list, tuple)) and len(use_bisect) == 3:
            mod.use_bisect_axis = tuple(bool(v) for v in use_bisect)
        if isinstance(use_bisect_flip, (list, tuple)) and len(use_bisect_flip) == 3:
            mod.use_bisect_flip_axis = tuple(bool(v) for v in use_bisect_flip)
        mod.use_clip = bool(args.get("use_clip", True))
        mod.use_mirror_merge = bool(args.get("use_mirror_merge", True))
        mod.merge_threshold = merge_threshold
        if mirror_object:
            mo = bpy.data.objects.get(mirror_object)
            if mo is None:
                return error_response("Mirror object not found", code="not_found")
            mod.mirror_object = mo
        mod.use_mirror_u = use_mirror_u
        mod.use_mirror_v = use_mirror_v
        mod.mirror_offset_u = mirror_offset_u
        mod.mirror_offset_v = mirror_offset_v
        return ok_response(
            result={
                "name": obj.name,
                "modifier": mod.name,
                "axes": list(mod.use_axis),
                "bisect": list(mod.use_bisect_axis),
                "clip": mod.use_clip,
                "merge": mod.use_mirror_merge,
                "mirror_object": mod.mirror_object.name if mod.mirror_object else None,
            }
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def mesh_bridge_edge_loops(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover

    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    number_cuts = max(0, min(1000, int(args.get("number_cuts", 0))))
    smoothness = max(0.0, min(1.0, float(args.get("smoothness", 1.0))))
    interpolation = args.get("interpolation", "LINEAR")
    profile_shape = args.get("profile_shape", "SMOOTH")
    profile_factor = float(args.get("profile_factor", 0.0))
    twist_offset = int(args.get("twist_offset", 0))
    merge = bool(args.get("merge", False))
    merge_threshold = max(0.0, min(1.0, float(args.get("merge_threshold", 0.001))))
    before_faces = len(obj.data.polygons)
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "EDIT")
        if err:
            return err
        bm = bmesh.from_edit_mesh(obj.data)
        sel_edges = [e for e in bm.edges if e.select]
        if not sel_edges:
            return error_response("No edges selected", code="no_selection")
        bpy.ops.mesh.bridge_edge_loops(
            number_cuts=number_cuts,
            interpolation=interpolation,
            smoothness=smoothness,
            profile_shape=profile_shape,
            profile_factor=profile_factor,
            twist_offset=twist_offset,
            merge=merge,
            merge_threshold=merge_threshold,
        )
        bmesh.update_edit_mesh(obj.data, loop_triangles=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        after_faces = len(obj.data.polygons)
        return ok_response(
            result={
                "name": obj.name,
                "bridged": True,
                "faces_created": max(0, after_faces - before_faces),
                "number_cuts": number_cuts,
                "interpolation": interpolation,
            }
        )
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


def mesh_fill(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover

    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    use_beauty = bool(args.get("use_beauty", True))
    before_faces = len(obj.data.polygons)
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "EDIT")
        if err:
            return err
        bm = bmesh.from_edit_mesh(obj.data)
        edges_selected = [e for e in bm.edges if e.select]
        if not edges_selected:
            return error_response("No edges selected", code="no_selection")
        bpy.ops.mesh.fill(use_beauty=use_beauty)
        bmesh.update_edit_mesh(obj.data, loop_triangles=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        after_faces = len(obj.data.polygons)
        return ok_response(
            result={
                "name": obj.name,
                "filled": True,
                "faces_created": max(0, after_faces - before_faces),
                "use_beauty": use_beauty,
            }
        )
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


def mesh_grid_fill(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover

    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    span = max(1, min(1000, int(args.get("span", 1))))
    offset = int(args.get("offset", 0))
    use_interp_simple = bool(args.get("use_interp_simple", False))
    before_faces = len(obj.data.polygons)
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "EDIT")
        if err:
            return err
        bm = bmesh.from_edit_mesh(obj.data)
        edges_selected = [e for e in bm.edges if e.select]
        if not edges_selected:
            return error_response("No edges selected", code="no_selection")
        bpy.ops.mesh.fill_grid(span=span, offset=offset, use_interp_simple=use_interp_simple)
        bmesh.update_edit_mesh(obj.data, loop_triangles=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        after_faces = len(obj.data.polygons)
        return ok_response(
            result={
                "name": obj.name,
                "filled": True,
                "faces_created": max(0, after_faces - before_faces),
                "span": span,
                "topology": "grid",
            }
        )
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


def mesh_remove_doubles(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover

    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    threshold = float(args.get("threshold", 0.0001))
    threshold = max(0.0, min(1.0, threshold))
    use_unselected = bool(args.get("use_unselected", False))
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "EDIT")
        if err:
            return err
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        verts = list(bm.verts) if use_unselected else [v for v in bm.verts if v.select]
        if not verts:
            return error_response("No vertices", code="no_selection")
        before = len(bm.verts)
        bmesh.ops.remove_doubles(bm, verts=verts, dist=threshold)
        bmesh.update_edit_mesh(obj.data, loop_triangles=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        after = len(obj.data.vertices)
        return ok_response(
            result={
                "name": obj.name,
                "verts_before": before,
                "verts_after": after,
                "removed": before - after,
                "threshold": threshold,
            }
        )
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


# ---------------------------------------------------------------------------
# Selection avancée (tools 16-20)
# ---------------------------------------------------------------------------


def mesh_select_similar(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    raw_type = args.get("type")
    if not raw_type:
        return error_response("type parameter required", code="bad_request")
    sim_type = str(raw_type)
    threshold = float(args.get("threshold", 0.01))
    threshold = max(0.0, min(1.0, threshold))
    compare = args.get("compare", "EQUAL")
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "EDIT")
        if err:
            return err
        import bmesh  # type: ignore  # pragma: no cover

        select_mode = bpy.context.tool_settings.mesh_select_mode
        if not any(sim_type.startswith(prefix) for prefix in ("VERT_", "EDGE_", "FACE_")):
            if select_mode[0]:
                sim_type = f"VERT_{sim_type}"
            elif select_mode[1]:
                sim_type = f"EDGE_{sim_type}"
            else:
                sim_type = f"FACE_{sim_type}"

        bm = bmesh.from_edit_mesh(obj.data)
        selected_before = sum(1 for f in bm.faces if f.select) + sum(1 for e in bm.edges if e.select) + sum(1 for v in bm.verts if v.select)
        bpy.ops.mesh.select_similar(type=sim_type, threshold=threshold, compare=compare)
        bm = bmesh.from_edit_mesh(obj.data)
        selected_after = sum(1 for f in bm.faces if f.select) + sum(1 for e in bm.edges if e.select) + sum(1 for v in bm.verts if v.select)
        bpy.ops.object.mode_set(mode="OBJECT")
        return ok_response(
            result={
                "name": obj.name,
                "type": sim_type,
                "threshold": threshold,
                "compare": compare,
                "selected_before": selected_before,
                "selected_after": selected_after,
            }
        )
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


def mesh_select_by_trait(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover
    import math

    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    trait = args.get("trait")
    threshold: float | None = None
    if trait == "SHARP_EDGES":
        threshold = float(args.get("threshold", math.pi / 6))
        threshold = max(0.0, min(math.pi, threshold))
    extend = bool(args.get("extend", False))
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "EDIT")
        if err:
            return err
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        if not extend:
            bpy.ops.mesh.select_all(action="DESELECT")
        selected_count = 0
        if trait == "LOOSE_VERTS":
            verts = [v for v in bm.verts if len(v.link_edges) == 0]
            for v in verts:
                v.select = True
            selected_count = len(verts)
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="VERT")
        elif trait == "LOOSE_EDGES":
            edges = [e for e in bm.edges if len(e.link_faces) == 0]
            for e in edges:
                e.select = True
            selected_count = len(edges)
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="EDGE")
        elif trait == "LOOSE_FACES":
            faces = [f for f in bm.faces if all(len(e.link_faces) == 1 for e in f.edges)]
            for f in faces:
                f.select = True
            selected_count = len(faces)
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="FACE")
        elif trait == "BOUNDARY_EDGES":
            edges = [e for e in bm.edges if len(e.link_faces) == 1]
            for e in edges:
                e.select = True
            selected_count = len(edges)
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="EDGE")
        elif trait == "BOUNDARY_VERTS":
            verts = [v for v in bm.verts if any(len(e.link_faces) == 1 for e in v.link_edges)]
            for v in verts:
                v.select = True
            selected_count = len(verts)
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="VERT")
        elif trait == "NON_MANIFOLD_EDGES":
            edges = [e for e in bm.edges if len(e.link_faces) == 0 or len(e.link_faces) > 2]
            for e in edges:
                e.select = True
            selected_count = len(edges)
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="EDGE")
        elif trait == "NON_MANIFOLD_VERTS":
            verts = []
            for v in bm.verts:
                linked_faces = {f for e in v.link_edges for f in e.link_faces}
                if len(linked_faces) == 0 or any(len(e.link_faces) > 2 for e in v.link_edges):
                    verts.append(v)
            for v in verts:
                v.select = True
            selected_count = len(verts)
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="VERT")
        elif trait in ("TRIANGLES", "QUADS", "NGONS"):
            target = {"TRIANGLES": 3, "QUADS": 4}.get(trait, None)
            faces = []
            for f in bm.faces:
                sides = len(f.verts)
                if (target and sides == target) or (trait == "NGONS" and sides > 4):
                    faces.append(f)
            for f in faces:
                f.select = True
            selected_count = len(faces)
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="FACE")
        elif trait == "SHARP_EDGES":
            bm.normal_update()
            edges = []
            for e in bm.edges:
                if len(e.link_faces) == 2:
                    n1 = e.link_faces[0].normal
                    n2 = e.link_faces[1].normal
                    if n1.length > 0 and n2.length > 0:
                        try:
                            angle = n1.angle(n2)
                            if threshold is not None and angle > threshold:
                                edges.append(e)
                        except Exception:
                            pass
            for e in edges:
                e.select = True
            selected_count = len(edges)
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="EDGE")
        elif trait == "INTERIOR_FACES":
            faces = []
            for f in bm.faces:
                if f.edges and all(len(e.link_faces) > 1 for e in f.edges):
                    if not any(len(e.link_faces) == 1 for e in f.edges):
                        faces.append(f)
            for f in faces:
                f.select = True
            selected_count = len(faces)
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="FACE")
        else:
            return error_response("Invalid trait", code="bad_request")
        bmesh.update_edit_mesh(obj.data, loop_triangles=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        return ok_response(
            result={
                "name": obj.name,
                "trait": trait,
                "selected": selected_count,
                "threshold": threshold,
                "extend": extend,
            }
        )
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


def mesh_select_nth(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover

    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    nth = max(1, min(10000, int(args.get("nth", 2))))
    skip = max(0, min(10000, int(args.get("skip", 0))))
    offset = max(0, min(10000, int(args.get("offset", 0))))
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "EDIT")
        if err:
            return err
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        selected_before = sum(1 for v in bm.verts if v.select) + sum(1 for e in bm.edges if e.select) + sum(1 for f in bm.faces if f.select)
        # manual nth on current selection
        if any(v.select for v in bm.verts):
            elems = [v for v in bm.verts if v.select]
            for i, v in enumerate(elems):
                v.select = ((i + offset) % nth == 0) and (i >= skip)
        elif any(e.select for e in bm.edges):
            elems = [e for e in bm.edges if e.select]
            for i, e in enumerate(elems):
                e.select = ((i + offset) % nth == 0) and (i >= skip)
        elif any(f.select for f in bm.faces):
            elems = [f for f in bm.faces if f.select]
            for i, f in enumerate(elems):
                f.select = ((i + offset) % nth == 0) and (i >= skip)
        bmesh.update_edit_mesh(obj.data, loop_triangles=False)
        selected_after = sum(1 for v in bm.verts if v.select) + sum(1 for e in bm.edges if e.select) + sum(1 for f in bm.faces if f.select)
        bpy.ops.object.mode_set(mode="OBJECT")
        return ok_response(
            result={
                "name": obj.name,
                "nth": nth,
                "skip": skip,
                "offset": offset,
                "selected_before": selected_before,
                "selected_after": selected_after,
            }
        )
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


def mesh_select_random(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover
    import random

    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    ratio_raw = args.get("ratio", 0.5)
    try:
        ratio = float(ratio_raw)
    except (TypeError, ValueError):
        ratio = 0.5
    ratio = max(0.0, min(1.0, ratio))
    seed_raw = args.get("seed", 0)
    try:
        seed = int(seed_raw) if seed_raw is not None else 0
    except (TypeError, ValueError):
        seed = 0
    action = args.get("action", "SELECT")
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "EDIT")
        if err:
            return err
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        selected_before = sum(1 for v in bm.verts if v.select) + sum(1 for e in bm.edges if e.select) + sum(1 for f in bm.faces if f.select)
        random.seed(seed)
        # operate on current selection mode; detect which domain is selected
        if any(v.select for v in bm.verts):
            for v in bm.verts:
                if v.select:
                    if action == "SELECT":
                        v.select = random.random() < ratio
                    else:
                        v.select = not (random.random() < ratio)
        elif any(e.select for e in bm.edges):
            for e in bm.edges:
                if e.select:
                    if action == "SELECT":
                        e.select = random.random() < ratio
                    else:
                        e.select = not (random.random() < ratio)
        else:
            for f in bm.faces:
                if f.select:
                    if action == "SELECT":
                        f.select = random.random() < ratio
                    else:
                        f.select = not (random.random() < ratio)
        bmesh.update_edit_mesh(obj.data, loop_triangles=False)
        selected_after = sum(1 for v in bm.verts if v.select) + sum(1 for e in bm.edges if e.select) + sum(1 for f in bm.faces if f.select)
        total = len(bm.verts) + len(bm.edges) + len(bm.faces)
        percent = (selected_after / total) * 100 if total else 0.0
        bpy.ops.object.mode_set(mode="OBJECT")
        return ok_response(
            result={
                "name": obj.name,
                "ratio": ratio,
                "seed": seed,
                "action": action,
                "selected": selected_after,
                "total": total,
                "percent": percent,
            }
        )
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


def mesh_select_face_by_sides(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover

    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    sel_type = args.get("type")
    sides_exact = args.get("sides")
    min_sides = args.get("min_sides")
    max_sides = args.get("max_sides")
    extend = bool(args.get("extend", False))
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "EDIT")
        if err:
            return err
        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        if not extend:
            bpy.ops.mesh.select_all(action="DESELECT")
        selected = []
        for f in bm.faces:
            sides = len(f.verts)
            match = False
            if sel_type == "TRIANGLES" and sides == 3:
                match = True
            elif sel_type == "QUADS" and sides == 4:
                match = True
            elif sel_type == "NGONS" and sides > 4:
                match = True
            elif sel_type == "CUSTOM":
                if sides_exact is not None:
                    match = sides == int(sides_exact)
                elif min_sides is not None and max_sides is not None:
                    match = int(min_sides) <= sides <= int(max_sides)
            if match:
                f.select = True
                selected.append(f)
        bmesh.update_edit_mesh(obj.data, loop_triangles=False)
        total_faces = len(bm.faces)
        bpy.ops.object.mode_set(mode="OBJECT")
        return ok_response(
            result={
                "name": obj.name,
                "type": sel_type,
                "selected": len(selected),
                "total_faces": total_faces,
                "extend": extend,
            }
        )
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


# ---------------------------------------------------------------------------
# UV tools (21-25)
# ---------------------------------------------------------------------------


def _ensure_uv_layer(obj):
    if not obj.data.uv_layers:
        obj.data.uv_layers.new(name="UVMap")


def uv_unwrap(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover

    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    method = args.get("method", "ANGLE_BASED")
    margin = max(0.0, min(1.0, float(args.get("margin", 0.001))))
    fill_holes = bool(args.get("fill_holes", True))
    correct_aspect = bool(args.get("correct_aspect", True))
    use_subsurf_data = bool(args.get("use_subsurf_data", False))
    try:
        _ensure_uv_layer(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "EDIT")
        if err:
            return err
        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        if not any(f.select for f in bm.faces):
            return error_response("No faces selected", code="no_selection")
        bpy.ops.uv.unwrap(
            method=method,
            margin=margin,
            fill_holes=fill_holes,
            correct_aspect=correct_aspect,
            use_subsurf_data=use_subsurf_data,
        )
        bmesh.update_edit_mesh(obj.data, loop_triangles=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        uv_layer = obj.data.uv_layers.active
        uv_count = 0
        if uv_layer:
            for poly in obj.data.polygons:
                for li in poly.loop_indices:
                    uv_count += 1
        return ok_response(
            result={"name": obj.name, "method": method, "unwrapped": True, "uv_count": uv_count, "margin": margin}
        )
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


def uv_smart_project(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    angle_limit = max(1.0, min(89.0, float(args.get("angle_limit", 66.0))))
    island_margin = max(0.0, min(1.0, float(args.get("island_margin", 0.02))))
    area_weight = max(0.0, min(1.0, float(args.get("area_weight", 0.0))))
    correct_aspect = bool(args.get("correct_aspect", True))
    scale_to_bounds = bool(args.get("scale_to_bounds", False))
    try:
        _ensure_uv_layer(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        if bpy.context.object.mode != "EDIT":
            bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.select_mode(type="FACE")
        bpy.ops.uv.smart_project(
            angle_limit=angle_limit,
            island_margin=island_margin,
            area_weight=area_weight,
            correct_aspect=correct_aspect,
            scale_to_bounds=scale_to_bounds,
        )
        bpy.ops.object.mode_set(mode="OBJECT")
        return ok_response(
            result={
                "name": obj.name,
                "method": "smart_project",
                "angle_limit": angle_limit,
                "island_margin": island_margin,
                "area_weight": area_weight,
                "scale_to_bounds": scale_to_bounds,
            }
        )
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


def uv_cube_project(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    cube_size = max(0.001, min(1000.0, float(args.get("cube_size", 2.0))))
    correct_aspect = bool(args.get("correct_aspect", True))
    clip_to_bounds = bool(args.get("clip_to_bounds", False))
    scale_to_bounds = bool(args.get("scale_to_bounds", False))
    try:
        _ensure_uv_layer(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "EDIT")
        if err:
            return err
        bpy.ops.uv.cube_project(
            cube_size=cube_size,
            correct_aspect=correct_aspect,
            clip_to_bounds=clip_to_bounds,
            scale_to_bounds=scale_to_bounds,
        )
        bpy.ops.object.mode_set(mode="OBJECT")
        return ok_response(
            result={
                "name": obj.name,
                "projection": "cube",
                "cube_size": cube_size,
                "clip_to_bounds": clip_to_bounds,
                "scale_to_bounds": scale_to_bounds,
            }
        )
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


def uv_cylinder_project(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    direction = args.get("direction", "ALIGN_TO_OBJECT")
    align = args.get("align", "POLAR_ZX")
    radius = max(0.001, min(1000.0, float(args.get("radius", 1.0))))
    correct_aspect = bool(args.get("correct_aspect", True))
    clip_to_bounds = bool(args.get("clip_to_bounds", False))
    scale_to_bounds = bool(args.get("scale_to_bounds", False))
    try:
        _ensure_uv_layer(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "EDIT")
        if err:
            return err
        bpy.ops.uv.cylinder_project(
            direction=direction,
            align=align,
            radius=radius,
            correct_aspect=correct_aspect,
            clip_to_bounds=clip_to_bounds,
            scale_to_bounds=scale_to_bounds,
        )
        bpy.ops.object.mode_set(mode="OBJECT")
        return ok_response(
            result={
                "name": obj.name,
                "projection": "cylinder",
                "direction": direction,
                "align": align,
                "radius": radius,
                "clip_to_bounds": clip_to_bounds,
                "scale_to_bounds": scale_to_bounds,
            }
        )
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


def uv_sphere_project(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("name"), "MESH")
    if err:
        return err
    direction = args.get("direction", "ALIGN_TO_OBJECT")
    align = args.get("align", "POLAR_ZX")
    correct_aspect = bool(args.get("correct_aspect", True))
    clip_to_bounds = bool(args.get("clip_to_bounds", False))
    scale_to_bounds = bool(args.get("scale_to_bounds", False))
    try:
        _ensure_uv_layer(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "EDIT")
        if err:
            return err
        bpy.ops.uv.sphere_project(
            direction=direction,
            align=align,
            correct_aspect=correct_aspect,
            clip_to_bounds=clip_to_bounds,
            scale_to_bounds=scale_to_bounds,
        )
        bpy.ops.object.mode_set(mode="OBJECT")
        return ok_response(
            result={
                "name": obj.name,
                "projection": "sphere",
                "direction": direction,
                "align": align,
                "clip_to_bounds": clip_to_bounds,
                "scale_to_bounds": scale_to_bounds,
            }
        )
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


# ---------------------------------------------------------------------------
# Collections (P1)
# ---------------------------------------------------------------------------


def _get_collection(bpy, name: str):
    col = bpy.data.collections.get(name)
    if col is None:
        return None, error_response(f"Collection '{name}' not found", code="not_found")
    return col, None


def collection_create(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    name = args.get("name")
    parent_name = args.get("parent")
    hide_viewport = bool(args.get("hide_viewport", False))
    hide_render = bool(args.get("hide_render", False))
    hide_select = bool(args.get("hide_select", False))
    try:
        col = bpy.data.collections.new(name=name)
        if parent_name:
            parent = bpy.data.collections.get(parent_name)
            if parent is None:
                return error_response("Parent collection not found", code="not_found")
            parent.children.link(col)
            parent_used = parent.name
        else:
            bpy.context.scene.collection.children.link(col)
            parent_used = None
        col.hide_viewport = hide_viewport
        col.hide_render = hide_render
        col.hide_select = hide_select
        return ok_response(
            result={
                "name": col.name,
                "parent": parent_used,
                "created": True,
                "hide_viewport": col.hide_viewport,
                "hide_render": col.hide_render,
                "hide_select": col.hide_select,
                "children_count": len(col.children),
            }
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def collection_add_objects(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    col_name = args.get("collection_name")
    obj_names = args.get("object_names") or []
    move = bool(args.get("move", True))
    unlink_from = args.get("unlink_from")
    col, err = _get_collection(bpy, col_name)
    if err:
        return err
    linked: List[str] = []
    errors: List[str] = []
    try:
        for obj_name in obj_names:
            obj = bpy.data.objects.get(obj_name)
            if obj is None:
                errors.append(f"Object '{obj_name}' not found")
                continue
            if obj.name not in col.objects:
                col.objects.link(obj)
                linked.append(obj.name)
            if move:
                for other_coll in list(obj.users_collection):
                    if other_coll == col:
                        continue
                    other_coll.objects.unlink(obj)
        return ok_response(
            result={
                "collection": col.name,
                "linked": linked,
                "errors": errors,
            }
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def collection_remove_objects(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    col_name = args.get("collection_name")
    obj_names = args.get("object_names") or []
    delete_objects = bool(args.get("delete_objects", False))
    col, err = _get_collection(bpy, col_name)
    if err:
        return err
    removed, not_found, not_in_collection = [], [], []
    try:
        for name in obj_names:
            obj = bpy.data.objects.get(name)
            if obj is None:
                not_found.append(name)
                continue
            if obj not in col.objects:
                not_in_collection.append(name)
                continue
            col.objects.unlink(obj)
            removed.append(name)
            if delete_objects:
                for c in list(obj.users_collection):
                    c.objects.unlink(obj)
                bpy.data.objects.remove(obj, do_unlink=True)
        return ok_response(
            result={
                "collection": col.name,
                "removed": removed,
                "not_found": not_found,
                "not_in_collection": not_in_collection,
                "deleted": delete_objects,
                "count": len(removed),
            }
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def collection_hide(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    col_name = args.get("collection_name")
    col, err = _get_collection(bpy, col_name)
    if err:
        return err
    hide_viewport = args.get("hide_viewport", None)
    hide_render = args.get("hide_render", None)
    hide_select = args.get("hide_select", None)
    recursive = bool(args.get("recursive", False))

    def apply_visibility(c):
        if hide_viewport is not None:
            c.hide_viewport = bool(hide_viewport)
        if hide_render is not None:
            c.hide_render = bool(hide_render)
        if hide_select is not None:
            c.hide_select = bool(hide_select)

    try:
        apply_visibility(col)
        children_affected = 0
        if recursive:
            def walk(c):
                nonlocal children_affected
                for child in c.children:
                    apply_visibility(child)
                    children_affected += 1
                    walk(child)
            walk(col)
        return ok_response(
            result={
                "collection": col.name,
                "hide_viewport": col.hide_viewport,
                "hide_render": col.hide_render,
                "hide_select": col.hide_select,
                "recursive": recursive,
                "children_affected": children_affected,
            }
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


# ---------------------------------------------------------------------------
# Rename / Import / Export
# ---------------------------------------------------------------------------


def object_rename(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    old_name = args.get("old_name")
    if not old_name:
        return error_response("old_name is required", code="invalid_args")
    obj, err = _get_object(bpy, old_name)
    if err:
        return err
    target_name = args.get("new_name") or obj.name
    find = args.get("find")
    replace = args.get("replace", "")
    prefix = args.get("prefix")
    suffix = args.get("suffix")

    new_name = target_name
    if find:
        new_name = new_name.replace(find, replace if replace is not None else "")
    if prefix:
        new_name = f"{prefix}{new_name}"
    if suffix:
        new_name = f"{new_name}{suffix}"
    if not new_name:
        return error_response("Resulting name is empty", code="invalid_args")

    desired = new_name
    obj.name = desired
    unique = obj.name == desired

    data_renamed = False
    data_name = None
    if bool(args.get("rename_data", False)) and getattr(obj, "data", None):
        obj.data.name = obj.name
        data_name = obj.data.name
        data_renamed = True

    return ok_response(
        result={
            "old_name": old_name,
            "new_name": obj.name,
            "unique": unique,
            "data_renamed": data_renamed,
            "data_name": data_name,
        }
    )


def _detect_import_format(filepath: str, explicit: Optional[str]) -> Optional[str]:
    if explicit:
        return explicit.upper()
    ext = os.path.splitext(filepath)[1].lower()
    mapping = {
        ".obj": "OBJ",
        ".fbx": "FBX",
        ".gltf": "GLTF",
        ".glb": "GLB",
        ".stl": "STL",
        ".ply": "PLY",
        ".x3d": "X3D",
        ".dae": "COLLADA",
    }
    return mapping.get(ext)


def import_file(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    filepath = args.get("filepath")
    if not filepath or not isinstance(filepath, str):
        return error_response("filepath is required", code="invalid_args")
    if not os.path.isfile(filepath):
        return error_response("File not found", code="not_found")

    fmt = _detect_import_format(filepath, args.get("format"))
    if not fmt:
        return error_response("Unsupported format", code="unsupported_format")

    forward = args.get("forward_axis", "Y")
    up = args.get("up_axis", "Z")
    scale = args.get("global_scale", 1.0)
    use_split_objects = bool(args.get("use_split_objects", True))
    use_split_groups = bool(args.get("use_split_groups", False))
    collection_name = args.get("collection_name")

    def _ensure_collection(name: str):
        col = bpy.data.collections.get(name)
        if col is None:
            col = bpy.data.collections.new(name=name)
            bpy.context.scene.collection.children.link(col)
        return col

    imported_names: List[str] = []
    try:
        bpy.ops.object.mode_set(mode="OBJECT")
    except Exception:
        pass

    try:
        if fmt == "OBJ":
            op = getattr(bpy.ops.wm, "obj_import", None)
            if op is None:
                return error_response("OBJ import operator not available", code="unsupported_format")
            op(filepath=filepath, forward_axis=forward, up_axis=up, global_scale=scale, use_split_objects=use_split_objects, use_split_groups=use_split_groups)
        elif fmt == "FBX":
            bpy.ops.import_scene.fbx(filepath=filepath, axis_forward=forward, axis_up=up, global_scale=scale, use_custom_normals=True)
        elif fmt in {"GLTF", "GLB"}:
            bpy.ops.import_scene.gltf(filepath=filepath)
        elif fmt == "STL":
            op = getattr(bpy.ops.wm, "stl_import", None)
            if op is None:
                return error_response("STL import operator not available", code="unsupported_format")
            op(filepath=filepath, global_scale=scale, use_facet_normal=True)
        elif fmt == "PLY":
            op = getattr(bpy.ops.wm, "ply_import", None)
            if op is None:
                return error_response("PLY import operator not available", code="unsupported_format")
            op(filepath=filepath)
        elif fmt == "X3D":
            bpy.ops.import_scene.x3d(filepath=filepath)
        elif fmt == "COLLADA":
            op = getattr(bpy.ops.wm, "collada_import", None)
            if op is None:
                return error_response("Collada import operator not available", code="unsupported_format")
            op(filepath=filepath)
        else:
            return error_response("Unsupported format", code="unsupported_format")

        imported_objs = list(bpy.context.selected_objects)
        if collection_name:
            col = _ensure_collection(collection_name)
            for obj in imported_objs:
                if obj not in col.objects:
                    col.objects.link(obj)
        imported_names = [obj.name for obj in imported_objs]

        return ok_response(
            result={
                "filepath": filepath,
                "format": fmt,
                "imported_objects": imported_names,
                "count": len(imported_names),
                "collection": collection_name,
                "global_scale": scale,
            }
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def _detect_export_format(filepath: str, explicit: Optional[str]) -> Optional[str]:
    if explicit:
        return explicit.upper()
    ext = os.path.splitext(filepath)[1].lower()
    mapping = {
        ".obj": "OBJ",
        ".fbx": "FBX",
        ".gltf": "GLTF",
        ".glb": "GLB",
        ".stl": "STL",
        ".ply": "PLY",
        ".usd": "USD",
    }
    return mapping.get(ext)


def export_file(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    filepath = args.get("filepath")
    if not filepath or not isinstance(filepath, str):
        return error_response("filepath is required", code="invalid_args")
    directory = os.path.dirname(filepath) or "."
    if not os.path.isdir(directory):
        return error_response("Output directory not found", code="not_found")

    fmt = _detect_export_format(filepath, args.get("format"))
    if not fmt:
        return error_response("Unsupported format", code="unsupported_format")

    export_selected = bool(args.get("export_selected", False))
    forward = args.get("forward_axis", "Y")
    up = args.get("up_axis", "Z")
    scale = args.get("global_scale", 1.0)
    apply_modifiers = bool(args.get("apply_modifiers", True))
    export_materials = bool(args.get("export_materials", True))
    export_animations = bool(args.get("export_animations", True))

    try:
        bpy.ops.object.mode_set(mode="OBJECT")
    except Exception:
        pass

    if export_selected and not bpy.context.selected_objects:
        return error_response("No selected objects to export", code="invalid_args")

    try:
        if fmt == "OBJ":
            op = getattr(bpy.ops.wm, "obj_export", None)
            if op is None:
                # fallback legacy
                op = bpy.ops.export_scene.obj
                op(filepath=filepath, use_selection=export_selected, axis_forward=forward, axis_up=up, global_scale=scale, use_materials=export_materials, use_uvs=True, use_mesh_modifiers=apply_modifiers)
            else:
                op(filepath=filepath, export_selected_objects=export_selected, forward_axis=forward, up_axis=up, global_scale=scale, export_materials=export_materials, export_uv=True, apply_modifiers=apply_modifiers)
        elif fmt == "FBX":
            bpy.ops.export_scene.fbx(
                filepath=filepath,
                use_selection=export_selected,
                axis_forward=forward,
                axis_up=up,
                global_scale=scale,
                apply_unit_scale=True,
                bake_space_transform=False,
                use_mesh_modifiers=apply_modifiers,
                add_leaf_bones=False,
                apply_scale_options="FBX_SCALE_ALL",
                bake_anim=export_animations,
            )
        elif fmt in {"GLTF", "GLB"}:
            export_format = "GLB" if fmt == "GLB" else "GLTF_SEPARATE"
            bpy.ops.export_scene.gltf(
                filepath=filepath,
                export_format=export_format,
                use_selection=export_selected,
                export_apply=apply_modifiers,
                export_materials="EXPORT" if export_materials else "NONE",
                export_colors=True,
                export_animations=export_animations,
            )
        elif fmt == "STL":
            op = getattr(bpy.ops.wm, "stl_export", None)
            if op is None:
                return error_response("STL export operator not available", code="unsupported_format")
            op(filepath=filepath, use_selection=export_selected, global_scale=scale, ascii=False, use_batch_own_dir=False, use_batch_name=False)
        elif fmt == "PLY":
            op = getattr(bpy.ops.wm, "ply_export", None)
            if op is None:
                return error_response("PLY export operator not available", code="unsupported_format")
            op(filepath=filepath, use_selection=export_selected, global_scale=scale)
        elif fmt == "USD":
            op = getattr(bpy.ops.wm, "usd_export", None)
            if op is None:
                return error_response("USD export operator not available", code="unsupported_format")
            op(filepath=filepath, selected_objects_only=export_selected, export_animation=export_animations)
        else:
            return error_response("Unsupported format", code="unsupported_format")

        exported_objs = list(bpy.context.selected_objects) if export_selected else list(bpy.data.objects)
        return ok_response(
            result={
                "filepath": filepath,
                "format": fmt,
                "exported_objects": [o.name for o in exported_objs],
                "count": len(exported_objs),
                "export_selected": export_selected,
                "global_scale": scale,
            }
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


# ---------------------------------------------------------------------------
# Mesh cleanup (P1)
# ---------------------------------------------------------------------------


def mesh_recalculate_normals(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    args = args or {}
    name = args.get("name")
    inside = bool(args.get("inside", False))
    operation = args.get("operation", "RECALCULATE")
    obj, err = _get_object(bpy, name, "MESH")
    if err:
        return err
    try:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        if operation == "FLIP":
            bpy.ops.mesh.flip_normals()
            op_used = "FLIP"
        else:
            bpy.ops.mesh.normals_make_consistent(inside=inside)
            op_used = "RECALCULATE"
        bpy.ops.object.mode_set(mode="OBJECT")
        faces_affected = len(obj.data.polygons)
        return ok_response(
            result={
                "name": obj.name,
                "operation": op_used,
                "inside": inside,
                "faces_affected": faces_affected,
                "consistent": True,
            }
        )
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


def mesh_validate(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover
    args = args or {}
    name = args.get("name")
    if not name:
        return error_response("name parameter required", code="bad_request")
    obj, err = _get_object(bpy, name, "MESH")
    if err:
        return err
    check_loose_verts = bool(args.get("check_loose_verts", True))
    check_loose_edges = bool(args.get("check_loose_edges", True))
    check_non_manifold = bool(args.get("check_non_manifold", True))
    check_degenerate = bool(args.get("check_degenerate", True))
    check_doubles = bool(args.get("check_doubles", True))
    doubles_threshold = float(args.get("doubles_threshold", 0.0001))

    bpy.context.view_layer.objects.active = obj
    needs_update = False
    try:
        bpy.ops.object.mode_set(mode="EDIT")
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        issues: Dict[str, int] = {}
        if check_loose_verts:
            issues["loose_verts"] = len([v for v in bm.verts if len(v.link_edges) == 0])
        if check_loose_edges:
            issues["loose_edges"] = len([e for e in bm.edges if len(e.link_faces) == 0])
        if check_non_manifold:
            issues["non_manifold_edges"] = len([e for e in bm.edges if len(e.link_faces) > 2])
        if check_degenerate:
            issues["degenerate_faces"] = len([f for f in bm.faces if f.calc_area() < 0.0001])
        if check_doubles and doubles_threshold > 0:
            dup = bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=doubles_threshold)
            doubles_removed = len(dup.get("targetmap", {}))
            issues["doubles"] = doubles_removed
            needs_update = True

        stats = {"total_verts": len(bm.verts), "total_edges": len(bm.edges), "total_faces": len(bm.faces)}
        return ok_response(result={"name": obj.name, "issues": issues, "stats": stats, "valid": all(v == 0 for v in issues.values())})
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")
    finally:
        try:
            if needs_update:
                bmesh.update_edit_mesh(obj.data)
        except Exception:
            pass
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


def mesh_triangulate(args: Dict[str, Any]) -> Dict[str, Any]:
    bpy = _require_bpy()
    import bmesh  # type: ignore  # pragma: no cover
    args = args or {}
    name = args.get("name")
    obj, err = _get_object(bpy, name, "MESH")
    if err:
        return err
    quad_method = args.get("quad_method", "BEAUTY")
    ngon_method = args.get("ngon_method", "BEAUTY")
    keep_normals = bool(args.get("keep_normals", False))
    try:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        faces_before = len(bm.faces)
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method=quad_method, ngon_method=ngon_method)
        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode="OBJECT")
        faces_after = len(obj.data.polygons)
        return ok_response(
            result={
                "name": obj.name,
                "faces_before": faces_before,
                "faces_after": faces_after,
                "quad_method": quad_method,
                "ngon_method": ngon_method,
                "keep_normals": keep_normals,
            }
        )
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")
# Additional executor functions for missing tools
# This file will be appended to executor.py

def mesh_query_geometry(args: Dict[str, Any]) -> Dict[str, Any]:
    """Query mesh geometry data (vertices, edges, faces)."""
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("object_name"), "MESH")
    if err:
        return err

    mesh = obj.data
    get_vertices = args.get("get_vertices", True)
    get_edges = args.get("get_edges", True)
    get_faces = args.get("get_faces", True)
    get_normals = args.get("get_normals", True)
    limit = min(int(args.get("limit", 5000)), 50000)
    compute_stats = args.get("compute_stats", True)

    result = {"object_name": obj.name}

    try:
        if get_vertices:
            verts = mesh.vertices[:limit]
            result["vertices"] = [{"co": list(v.co), "index": v.index} for v in verts]
            if compute_stats:
                result["vertex_count"] = len(mesh.vertices)

        if get_edges:
            edges = mesh.edges[:limit]
            result["edges"] = [{"vertices": list(e.vertices), "index": e.index} for e in edges]
            if compute_stats:
                result["edge_count"] = len(mesh.edges)

        if get_faces:
            faces = mesh.polygons[:limit]
            result["faces"] = [{"vertices": list(f.vertices), "index": f.index} for f in faces]
            if compute_stats:
                result["face_count"] = len(mesh.polygons)

        if get_normals and get_vertices:
            result["vertex_normals"] = [list(v.normal) for v in mesh.vertices[:limit]]

        return ok_response(result=result)
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def mesh_query_selection(args: Dict[str, Any]) -> Dict[str, Any]:
    """Query current mesh selection state."""
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("object_name"), "MESH")
    if err:
        return err

    try:
        import bmesh  # type: ignore

        # Ensure we're in edit mode to access selection
        original_mode = obj.mode
        if original_mode != "EDIT":
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.mode_set(mode="EDIT")

        bm = bmesh.from_edit_mesh(obj.data)

        selected_verts = [v.index for v in bm.verts if v.select]
        selected_edges = [e.index for e in bm.edges if e.select]
        selected_faces = [f.index for f in bm.faces if f.select]

        result = {
            "object_name": obj.name,
            "mode": bpy.context.mode,
            "selected_vertices": selected_verts,
            "selected_edges": selected_edges,
            "selected_faces": selected_faces,
            "selection_counts": {
                "vertices": len(selected_verts),
                "edges": len(selected_edges),
                "faces": len(selected_faces)
            }
        }

        # Restore original mode if changed
        if original_mode != "EDIT":
            bpy.ops.object.mode_set(mode=original_mode)

        return ok_response(result=result)
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def mesh_query_topology(args: Dict[str, Any]) -> Dict[str, Any]:
    """Query mesh topology (manifold, watertight, ngons, poles)."""
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("object_name"), "MESH")
    if err:
        return err

    checks = args.get("checks", ["all"])
    do_all = "all" in checks

    try:
        import bmesh  # type: ignore

        bm = bmesh.new()
        bm.from_mesh(obj.data)

        result = {"object_name": obj.name, "checks": {}}

        if do_all or "manifold" in checks:
            non_manifold_edges = [e.index for e in bm.edges if not e.is_manifold]
            result["checks"]["manifold"] = {
                "is_manifold": len(non_manifold_edges) == 0,
                "non_manifold_edge_count": len(non_manifold_edges)
            }

        if do_all or "watertight" in checks:
            boundary_edges = [e.index for e in bm.edges if e.is_boundary]
            result["checks"]["watertight"] = {
                "is_watertight": len(boundary_edges) == 0,
                "boundary_edge_count": len(boundary_edges)
            }

        if do_all or "ngons" in checks:
            ngons = [f.index for f in bm.faces if len(f.verts) > 4]
            result["checks"]["ngons"] = {
                "has_ngons": len(ngons) > 0,
                "ngon_count": len(ngons)
            }

        if do_all or "poles" in checks:
            poles = [v.index for v in bm.verts if len(v.link_edges) > 5]
            result["checks"]["poles"] = {
                "has_poles": len(poles) > 0,
                "pole_count": len(poles)
            }

        bm.free()
        return ok_response(result=result)
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def viewport_screenshot_complete(args: Dict[str, Any]) -> Dict[str, Any]:
    """Capture viewport screenshots with diagnostics."""
    bpy = _require_bpy()
    args = args or {}
    obj_name = args.get("object_name")

    if not obj_name:
        return error_response("object_name required", code="bad_request")

    obj, err = _get_object(bpy, obj_name)
    if err:
        return err

    try:
        # For now, return a placeholder - full implementation would require render setup
        return ok_response(result={
            "object_name": obj.name,
            "message": "Screenshot feature requires render context - use Blender UI or render API",
            "views_requested": args.get("views", ["FRONT"]),
            "shading_mode": args.get("shading_mode", ["SOLID"])
        })
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def modifier_bevel(args: Dict[str, Any]) -> Dict[str, Any]:
    """Add and configure a Bevel modifier."""
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("object_name"), "MESH")
    if err:
        return err

    modifier_name = args.get("modifier_name", "Bevel")
    width = float(args.get("width", 0.05))
    segments = int(args.get("segments", 3))
    profile = float(args.get("profile", 0.5))

    try:
        mod = obj.modifiers.new(name=modifier_name, type='BEVEL')
        mod.width = width
        mod.segments = segments
        mod.profile = profile

        if "limit_method" in args:
            mod.limit_method = args["limit_method"]
        if "angle_limit" in args:
            mod.angle_limit = float(args["angle_limit"]) * 3.14159 / 180.0  # degrees to radians

        return ok_response(result={
            "object_name": obj.name,
            "modifier_name": mod.name,
            "width": mod.width,
            "segments": mod.segments,
            "profile": mod.profile
        })
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def mesh_extrude_manifold(args: Dict[str, Any]) -> Dict[str, Any]:
    """Extrude selection with manifold-safe options."""
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("object_name"), "MESH")
    if err:
        return err

    offset = args.get("offset", [0, 0, 0.5])

    try:
        import bmesh  # type: ignore

        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        err = _ensure_mode(bpy, "EDIT")
        if err:
            return err

        bm = bmesh.from_edit_mesh(obj.data)
        selected_faces = [f for f in bm.faces if f.select]

        if not selected_faces:
            return error_response("No faces selected", code="no_selection")

        # Use bmesh extrude
        ret = bmesh.ops.extrude_face_region(bm, geom=selected_faces)
        extruded = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMVert)]

        # Move extruded vertices
        bmesh.ops.translate(bm, verts=extruded, vec=offset)

        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode="OBJECT")

        return ok_response(result={
            "object_name": obj.name,
            "faces_extruded": len(selected_faces),
            "offset": offset
        })
    except Exception as exc:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return error_response(str(exc), code="bridge_error")


def material_assign_fixed(args: Dict[str, Any]) -> Dict[str, Any]:
    """Improved material assignment with auto-slot creation."""
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("object_name"), "MESH")
    if err:
        return err

    mat_name = args.get("material_name")
    if not mat_name:
        return error_response("material_name required", code="bad_request")

    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        return error_response(f"Material '{mat_name}' not found", code="not_found")

    assign_to_selection = args.get("assign_to_selection", True)
    create_slot = args.get("create_slot_if_missing", True)

    try:
        # Find or create material slot
        slot_index = -1
        for i, slot in enumerate(obj.material_slots):
            if slot.material and slot.material.name == mat_name:
                slot_index = i
                break

        if slot_index == -1 and create_slot:
            obj.data.materials.append(mat)
            slot_index = len(obj.data.materials) - 1

        if slot_index == -1:
            return error_response(f"No slot for material '{mat_name}'", code="not_found")

        if assign_to_selection:
            # Assign to selected faces in edit mode
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            original_mode = obj.mode

            if original_mode != "EDIT":
                bpy.ops.object.mode_set(mode="EDIT")

            import bmesh  # type: ignore
            bm = bmesh.from_edit_mesh(obj.data)
            selected_faces = [f for f in bm.faces if f.select]

            if selected_faces:
                obj.active_material_index = slot_index
                bpy.ops.object.material_slot_assign()
                faces_assigned = len(selected_faces)
            else:
                faces_assigned = 0

            if original_mode != "EDIT":
                bpy.ops.object.mode_set(mode=original_mode)
        else:
            # Assign to entire object
            obj.active_material_index = slot_index
            faces_assigned = len(obj.data.polygons)

        return ok_response(result={
            "object_name": obj.name,
            "material_name": mat.name,
            "slot_index": slot_index,
            "faces_assigned": faces_assigned
        })
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def _bounds_world(obj) -> tuple[list[float] | None, list[float] | None, list[float] | None]:
    """Compute world-space bounds for an object."""
    try:
        from mathutils import Vector  # type: ignore  # pragma: no cover - Blender runtime
    except Exception:
        return None, None, None

    try:
        corners = [obj.matrix_world @ Vector(corner) for corner in getattr(obj, "bound_box", [])]
        if not corners:
            return None, None, None
        mins = [min(c[i] for c in corners) for i in range(3)]
        maxs = [max(c[i] for c in corners) for i in range(3)]
        center = [(mins[i] + maxs[i]) / 2.0 for i in range(3)]
        return mins, maxs, center
    except Exception:
        return None, None, None


def scene_query_complete(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get complete scene state with geometry, bounds, and transforms."""
    bpy = _require_bpy()
    args = args or {}
    include_geometry = bool(args.get("include_geometry", True))
    include_transforms = bool(args.get("include_transforms", True))
    include_topology = bool(args.get("include_topology", False))
    max_objects = int(args.get("max_objects", 200))

    try:
        objects_payload: list[Dict[str, Any]] = []
        ctx = bpy.context

        for obj in list(bpy.data.objects)[:max_objects]:
            obj_data: Dict[str, Any] = {"name": obj.name, "type": obj.type}

            if include_transforms:
                try:
                    obj_data["transform"] = {
                        "location": list(obj.location),
                        "rotation_euler": list(getattr(obj, "rotation_euler", [])),
                        "scale": list(obj.scale),
                        "world_matrix": [list(row) for row in obj.matrix_world],
                    }
                except Exception:
                    pass

            bounds_min, bounds_max, bounds_center = _bounds_world(obj)
            if bounds_min and bounds_max:
                obj_data["bounds"] = {"min": bounds_min, "max": bounds_max, "center": bounds_center}

            if include_geometry and obj.type == "MESH" and obj.data:
                mesh = obj.data
                obj_data["geometry"] = {
                    "vertices_count": len(mesh.vertices),
                    "edges_count": len(mesh.edges),
                    "faces_count": len(mesh.polygons),
                }
                obj_data["materials"] = [mat.name for mat in getattr(mesh, "materials", []) if mat]
                obj_data["modifiers"] = [{"name": mod.name, "type": mod.type} for mod in getattr(obj, "modifiers", [])]

                if include_topology:
                    import bmesh  # type: ignore  # pragma: no cover - Blender runtime

                    bm = bmesh.new()
                    try:
                        bm.from_mesh(mesh)
                        boundary_edges = [e.index for e in bm.edges if e.is_boundary]
                        ngons = [f.index for f in bm.faces if len(f.verts) > 4]
                        obj_data["topology"] = {
                            "manifold": all(e.is_manifold for e in bm.edges),
                            "boundary_edges": len(boundary_edges),
                            "ngons": len(ngons),
                        }
                    finally:
                        bm.free()

            obj_data["parent"] = obj.parent.name if obj.parent else None
            obj_data["children"] = [child.name for child in getattr(obj, "children", [])]
            objects_payload.append(obj_data)

        result = {
            "blender_version": getattr(bpy.app, "version_string", "unknown"),
            "scene_name": getattr(ctx.scene, "name", "Scene"),
            "active_object": ctx.view_layer.objects.active.name if ctx.view_layer.objects.active else None,
            "selected_objects": [o.name for o in getattr(ctx, "selected_objects", [])],
            "objects": objects_payload,
            "scene_data": {
                "cursor_location": list(getattr(ctx.scene.cursor, "location", [0, 0, 0])),
                "frame_current": int(getattr(ctx.scene, "frame_current", 0)),
            },
        }
        return ok_response(result=result)
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def _distance_between(obj_a, obj_b):
    try:
        return float((obj_a.location - obj_b.location).length), list(obj_b.location - obj_a.location)
    except Exception:
        return None, None


def _grid_snapped(location, grid_size: float, tolerance: float) -> bool:
    for coord in location:
        remainder = abs(coord) % grid_size if grid_size else 0.0
        delta = min(remainder, abs(grid_size - remainder)) if grid_size else abs(remainder)
        if delta > tolerance:
            return False
    return True


def spatial_analyze(args: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze spatial relationships between objects."""
    bpy = _require_bpy()
    args = args or {}
    names = args.get("object_names")
    queries = args.get("queries") or ["distances", "alignments", "grid_snaps"]
    tolerance = float(args.get("tolerance", 0.001))
    grid_size = float(args.get("grid_size", 0.1))

    if names is None:
        candidates = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    elif isinstance(names, list):
        candidates = []
        for name in names:
            obj = bpy.data.objects.get(name)
            if obj is None:
                return error_response(f"Object '{name}' not found", code="not_found")
            candidates.append(obj)
    else:
        return error_response("object_names must be array or null", code="bad_request")

    queries_set = set(queries)
    analyzed_names = [obj.name for obj in candidates]
    result: Dict[str, Any] = {"analyzed_objects": analyzed_names}

    try:
        if "distances" in queries_set:
            distances = []
            for i, obj_a in enumerate(candidates):
                for obj_b in candidates[i + 1 :]:
                    distance, vector = _distance_between(obj_a, obj_b)
                    if distance is None:
                        continue
                    distances.append({"from": obj_a.name, "to": obj_b.name, "distance": distance, "vector": vector})
            result["distances"] = distances

        if "alignments" in queries_set:
            alignments = []
            axes = {"X": 0, "Y": 1, "Z": 2}
            for i, obj_a in enumerate(candidates):
                for obj_b in candidates[i + 1 :]:
                    for axis, idx in axes.items():
                        deviation = abs(obj_a.location[idx] - obj_b.location[idx])
                        alignments.append(
                            {
                                "objects": [obj_a.name, obj_b.name],
                                "axis": axis,
                                "tolerance": tolerance,
                                "deviation": deviation,
                                "aligned": deviation <= tolerance,
                            }
                        )
            result["alignments"] = alignments

        if "grid_snaps" in queries_set:
            grid_snaps = []
            for obj in candidates:
                snapped = _grid_snapped(obj.location, grid_size, tolerance)
                grid_snaps.append(
                    {"object": obj.name, "grid_size": grid_size, "snapped": snapped, "location": list(obj.location)}
                )
            result["grid_snaps"] = grid_snaps

        if "overlaps" in queries_set or "gaps" in queries_set:
            overlaps = []
            gaps = []
            for i, obj_a in enumerate(candidates):
                bounds_a_min, bounds_a_max, _ = _bounds_world(obj_a)
                if not bounds_a_min or not bounds_a_max:
                    continue
                for obj_b in candidates[i + 1 :]:
                    bounds_b_min, bounds_b_max, _ = _bounds_world(obj_b)
                    if not bounds_b_min or not bounds_b_max:
                        continue
                    intersects = all(
                        bounds_a_max[idx] >= bounds_b_min[idx] and bounds_b_max[idx] >= bounds_a_min[idx]
                        for idx in range(3)
                    )
                    if intersects and "overlaps" in queries_set:
                        overlaps.append({"objects": [obj_a.name, obj_b.name], "overlap": True})
                    elif "gaps" in queries_set:
                        axis_gaps = []
                        for idx, axis in enumerate(["X", "Y", "Z"]):
                            gap_val = 0.0
                            if bounds_a_max[idx] < bounds_b_min[idx]:
                                gap_val = bounds_b_min[idx] - bounds_a_max[idx]
                            elif bounds_b_max[idx] < bounds_a_min[idx]:
                                gap_val = bounds_a_min[idx] - bounds_b_max[idx]
                            axis_gaps.append({"axis": axis, "gap": gap_val})
                        gaps.append({"objects": [obj_a.name, obj_b.name], "gaps": axis_gaps})
            if "overlaps" in queries_set:
                result["overlaps"] = overlaps
            if "gaps" in queries_set:
                result["gaps"] = gaps

        return ok_response(result=result)
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def topology_validate_complete(args: Dict[str, Any]) -> Dict[str, Any]:
    """Validate mesh topology for manifold, watertightness, and degenerates."""
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("object_name"), "MESH")
    if err:
        return err

    checks = args.get("checks") or ["manifold", "watertight", "ngons", "poles", "loose"]
    report_indices = bool(args.get("report_indices", True))
    max_indices = int(args.get("max_indices", 10))

    import bmesh  # type: ignore  # pragma: no cover - Blender runtime

    bm = bmesh.new()
    try:
        bm.from_mesh(obj.data)

        topo_result: Dict[str, Any] = {}
        issues: list[Dict[str, Any]] = []

        def _record(issue_type: str, indices: list[int]) -> None:
            if not indices:
                return
            payload: Dict[str, Any] = {"type": issue_type, "count": len(indices)}
            if report_indices:
                payload["indices"] = indices[:max_indices]
            issues.append(payload)

        do_all = "all" in checks

        if do_all or "manifold" in checks:
            manifold_ok = all(e.is_manifold for e in bm.edges)
            topo_result["manifold"] = manifold_ok
            if not manifold_ok:
                bad_edges = [e.index for e in bm.edges if not e.is_manifold]
                _record("non_manifold_edges", bad_edges)

        if do_all or "watertight" in checks:
            boundary_edges = [e.index for e in bm.edges if e.is_boundary]
            watertight_ok = len(boundary_edges) == 0
            topo_result["watertight"] = watertight_ok
            if not watertight_ok:
                _record("boundary_edges", boundary_edges)

        if do_all or "ngons" in checks:
            ngons = [f.index for f in bm.faces if len(f.verts) > 4]
            topo_result["ngons"] = len(ngons)
            _record("ngons", ngons)

        if do_all or "triangles" in checks:
            tris = [f.index for f in bm.faces if len(f.verts) == 3]
            topo_result["triangles"] = len(tris)
            _record("triangles", tris)

        if do_all or "poles" in checks:
            poles = [v.index for v in bm.verts if len(v.link_edges) > 5]
            topo_result["poles_5plus"] = len(poles)
            _record("poles", poles)

        if do_all or "loose" in checks:
            loose_verts = [v.index for v in bm.verts if len(v.link_edges) == 0]
            loose_edges = [e.index for e in bm.edges if len(e.link_faces) == 0]
            topo_result["loose_verts"] = len(loose_verts)
            topo_result["loose_edges"] = len(loose_edges)
            _record("loose_verts", loose_verts)
            _record("loose_edges", loose_edges)

        if do_all or "degenerate" in checks:
            degenerate_faces = [f.index for f in bm.faces if f.calc_area() < 0.000001]
            topo_result["degenerate_faces"] = len(degenerate_faces)
            _record("degenerate_faces", degenerate_faces)

        result = {
            "object_name": obj.name,
            "vertex_count": len(bm.verts),
            "edge_count": len(bm.edges),
            "face_count": len(bm.faces),
            "healthy": len(issues) == 0,
            "topology": topo_result,
            "issues": issues,
        }
        return ok_response(result=result)
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")
    finally:
        bm.free()


def measure_batch(args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a batch of measurements in one call."""
    bpy = _require_bpy()
    args = args or {}
    measurements = args.get("measurements") or []
    results: list[Dict[str, Any]] = []
    successful = 0
    failed = 0

    def _get_point(defn: Dict[str, Any]) -> Any:
        obj_name = defn.get("object")
        if not obj_name:
            return None, "object required"
        obj = bpy.data.objects.get(obj_name)
        if obj is None:
            return None, f"Object '{obj_name}' not found"
        vertex_idx = defn.get("vertex")
        if vertex_idx is not None:
            try:
                vert = obj.data.vertices[int(vertex_idx)]
                return obj.matrix_world @ vert.co, None
            except Exception:
                return None, f"Invalid vertex index for {obj_name}"
        return obj.location.copy(), None

    try:
        for index, measurement in enumerate(measurements):
            entry: Dict[str, Any] = {"index": index, "type": measurement.get("type")}
            try:
                mtype = measurement.get("type")
                if mtype == "DISTANCE":
                    start, err_a = _get_point(measurement.get("from", {}))
                    end, err_b = _get_point(measurement.get("to", {}))
                    if err_a or err_b or start is None or end is None:
                        raise ValueError(err_a or err_b or "Missing endpoints")
                    vector = end - start
                    constraint = measurement.get("constraint")
                    if constraint == "X_AXIS_ONLY":
                        vector.y = 0
                        vector.z = 0
                    elif constraint == "Y_AXIS_ONLY":
                        vector.x = 0
                        vector.z = 0
                    elif constraint == "Z_AXIS_ONLY":
                        vector.x = 0
                        vector.y = 0
                    entry.update(
                        {
                            "value": float(vector.length),
                            "unit": "m",
                            "from": measurement.get("from", {}),
                            "to": measurement.get("to", {}),
                        }
                    )
                elif mtype == "VOLUME":
                    obj_name = measurement.get("object")
                    obj, err = _get_object(bpy, obj_name or "", "MESH")
                    if err:
                        raise ValueError(err["error"]["message"])
                    import bmesh  # type: ignore  # pragma: no cover - Blender runtime

                    bm = bmesh.new()
                    try:
                        bm.from_mesh(obj.data)
                        bm.transform(obj.matrix_world)
                        entry.update({"value": float(abs(bm.calc_volume())), "unit": "m^3", "object": obj.name})
                    finally:
                        bm.free()
                elif mtype == "AREA":
                    obj_name = measurement.get("object")
                    obj, err = _get_object(bpy, obj_name or "", "MESH")
                    if err:
                        raise ValueError(err["error"]["message"])
                    faces = measurement.get("faces")
                    if faces:
                        polys = [obj.data.polygons[i] for i in faces if i < len(obj.data.polygons)]
                    else:
                        polys = obj.data.polygons
                    area_val = sum(float(p.area) for p in polys)
                    entry.update({"value": area_val, "unit": "m^2", "object": obj.name})
                elif mtype == "ALIGNMENT":
                    objects = measurement.get("objects") or []
                    axis = measurement.get("axis") or "Z"
                    tol = float(measurement.get("tolerance", 0.001))
                    if len(objects) < 2:
                        raise ValueError("ALIGNMENT requires at least two objects")
                    axis_idx = {"X": 0, "Y": 1, "Z": 2}.get(axis, 2)
                    coords = []
                    for name in objects:
                        obj = bpy.data.objects.get(name)
                        if obj is None:
                            raise ValueError(f"Object '{name}' not found")
                        coords.append(obj.location[axis_idx])
                    max_dev = max(coords) - min(coords)
                    entry.update(
                        {
                            "objects": objects,
                            "axis": axis,
                            "tolerance": tol,
                            "deviation": float(max_dev),
                            "aligned": max_dev <= tol,
                        }
                    )
                else:
                    raise ValueError("Unknown measurement type")

                successful += 1
                results.append(entry)
            except Exception as exc:
                failed += 1
                entry["error"] = str(exc)
                results.append(entry)

        return ok_response(
            result={"measurements": results, "summary": {"total": len(measurements), "successful": successful, "failed": failed}}
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")


def validate_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Validate object against expectations (manifold, watertight, symmetry, alignment)."""
    bpy = _require_bpy()
    args = args or {}
    obj, err = _get_object(bpy, args.get("object_name"), "MESH")
    if err:
        return err

    expectations = args.get("expectations") or {}
    auto_fix = bool(args.get("auto_fix", False))
    details: Dict[str, Any] = {}
    failed: list[str] = []

    import bmesh  # type: ignore  # pragma: no cover - Blender runtime
    from math import degrees

    bm = bmesh.new()
    try:
        bm.from_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.verts.ensure_lookup_table()

        def _add_check(name: str, expected: Any, actual: Any, extra: Dict[str, Any] | None = None) -> None:
            info = {"expected": expected, "actual": actual, "passed": expected == actual if isinstance(expected, bool) else bool(actual)}
            if extra:
                info.update(extra)
            if not info["passed"]:
                failed.append(name)
            details[name] = info

        if "manifold" in expectations:
            manifold_ok = all(e.is_manifold for e in bm.edges)
            _add_check("manifold", bool(expectations.get("manifold")), manifold_ok)

        if "watertight" in expectations:
            watertight_ok = all(not e.is_boundary for e in bm.edges)
            _add_check("watertight", bool(expectations.get("watertight")), watertight_ok)

        if expectations.get("no_ngons") is not None:
            ngons = [f.index for f in bm.faces if len(f.verts) > 4]
            _add_check("no_ngons", bool(expectations.get("no_ngons")), len(ngons) == 0, {"ngon_count": len(ngons)})

        if expectations.get("no_tris") is not None:
            tris = [f.index for f in bm.faces if len(f.verts) == 3]
            _add_check("no_tris", bool(expectations.get("no_tris")), len(tris) == 0, {"triangle_count": len(tris)})

        if expectations.get("symmetry"):
            from mathutils import Vector  # type: ignore  # pragma: no cover - Blender runtime

            sym = expectations["symmetry"]
            axis = sym.get("axis", "X")
            tol = float(sym.get("tolerance", 0.001))
            axis_idx = {"X": 0, "Y": 1, "Z": 2}.get(axis, 0)
            verts_world = [obj.matrix_world @ v.co for v in bm.verts]
            unmatched = 0
            for co in verts_world:
                mirrored = co.copy()
                mirrored[axis_idx] = -mirrored[axis_idx]
                found = any((mirrored - other).length <= tol for other in verts_world)
                if not found:
                    unmatched += 1
            _add_check("symmetry", True, unmatched == 0, {"axis": axis, "tolerance": tol, "unmatched": unmatched})

        if expectations.get("alignment"):
            align = expectations["alignment"]
            grid_size = align.get("grid")
            align_objects = align.get("objects") or []
            tol = 0.001
            grid_passed = True
            if grid_size:
                grid_passed = _grid_snapped(obj.location, float(grid_size), tol)
            objects_passed = True
            if align_objects:
                for name in align_objects:
                    target = bpy.data.objects.get(name)
                    if target is None:
                        objects_passed = False
                        break
                    if any(abs(obj.location[i] - target.location[i]) > tol for i in range(3)):
                        objects_passed = False
                        break
            passed = grid_passed and objects_passed
            details["alignment"] = {
                "expected": True,
                "actual": passed,
                "grid_size": grid_size,
                "aligned_to_objects": align_objects,
                "passed": passed,
            }
            if not passed:
                failed.append("alignment")

        if expectations.get("min_face_area") is not None:
            threshold = float(expectations["min_face_area"])
            smallest = min((f.calc_area() for f in bm.faces), default=threshold)
            passed = smallest >= threshold
            _add_check("min_face_area", threshold, smallest, {"passed": passed})

        if expectations.get("max_edge_angle") is not None:
            limit = float(expectations["max_edge_angle"])
            max_angle = 0.0
            for e in bm.edges:
                angle = e.calc_face_angle()
                if angle is not None:
                    max_angle = max(max_angle, degrees(angle))
            passed = max_angle <= limit
            details["max_edge_angle"] = {"expected": limit, "actual": max_angle, "passed": passed}
            if not passed:
                failed.append("max_edge_angle")

        passed_all = len(failed) == 0

        if auto_fix and not passed_all:
            try:
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                original_mode = obj.mode
                bpy.ops.object.mode_set(mode="EDIT")
                bpy.ops.mesh.remove_doubles(threshold=0.0001)
                bpy.ops.mesh.normals_make_consistent(inside=False)
                bpy.ops.object.mode_set(mode=original_mode)
            except Exception:
                pass

        return ok_response(
            result={"object_name": obj.name, "passed": passed_all, "failed_checks": failed, "details": details}
        )
    except Exception as exc:
        return error_response(str(exc), code="bridge_error")
    finally:
        bm.free()
