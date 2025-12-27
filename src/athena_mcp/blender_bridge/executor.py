from __future__ import annotations

from typing import Any, Dict, List, Optional

from .responses import error_response, ok_response


def _require_bpy():
    try:
        import bpy  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on Blender runtime
        raise RuntimeError("bpy is required inside Blender") from exc
    return bpy


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
