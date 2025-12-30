from __future__ import annotations

import atexit
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
import sys

if __package__ is None or __package__ == "":  # pragma: no cover - Blender script execution
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    __package__ = "athena_mcp.blender_bridge"

from athena_mcp.blender_bridge import executor, queue as task_queue  # type: ignore  # noqa: E402
from athena_mcp.blender_bridge.responses import error_response, ok_response  # type: ignore  # noqa: E402

try:
    import bpy  # type: ignore
except Exception:  # pragma: no cover - import guarded for non-Blender environments
    bpy = None


def _ensure_bpy() -> Any:
    if bpy is None:  # pragma: no cover - runtime check
        raise RuntimeError("This bridge must run inside Blender (bpy unavailable)")
    return bpy


_WAIT_TIMEOUT = 2.0
_DEFAULT_HOST = "127.0.0.1"
_DEFAULT_PORT = 8765

# Tool registry: maps both old and new tool names to executor functions
_TOOL_REGISTRY: Dict[str, Any] = {
    # Scene tools
    "blender-list-objects": executor.list_objects,
    "blender-scene-list-objects": executor.list_objects,
    # Primitives
    "blender-add-cube": executor.add_cube,
    "blender-primitive-cube": executor.add_cube,
    "blender-add-cylinder": executor.add_cylinder,
    "blender-primitive-cylinder": executor.add_cylinder,
    "blender-add-sphere": executor.add_sphere,
    "blender-primitive-sphere": executor.add_sphere,
    # Object operations
    "blender-move-object": executor.move_object,
    "blender-object-move": executor.move_object,
    # Mode operations
    "blender-set-mode": executor.set_mode,
    "blender-mode-set": executor.set_mode,
    "blender-set-selection-mode": executor.set_selection_mode,
    "blender-mode-selection-set": executor.set_selection_mode,
    # Selection
    "blender-select-all": executor.select_all,
    "blender-select-none": executor.select_none,
    "blender-select-invert": executor.select_invert,
    # Mesh editing
    "blender-mesh-delete": executor.mesh_delete,
    "blender-mesh-extrude": executor.mesh_extrude,
    "blender-mesh-inset": executor.mesh_inset,
    "blender-mesh-loop-cut": executor.mesh_loop_cut,
    "blender-mesh-bevel": executor.mesh_bevel,
    "blender-mesh-subdivide": executor.mesh_subdivide,
    "blender-mesh-merge": executor.mesh_merge,
    # Mesh selection
    "blender-mesh-select-loop": executor.mesh_select_loop,
    "blender-mesh-select-ring": executor.mesh_select_ring,
    "blender-mesh-select-linked": executor.mesh_select_linked,
    "blender-mesh-select-more": executor.mesh_select_more,
    "blender-mesh-select-less": executor.mesh_select_less,
    "blender-mesh-select-non-manifold": executor.mesh_select_non_manifold,
    "blender-mesh-select-boundary": executor.mesh_select_boundary,
    "blender-mesh-select-by-index": executor.mesh_select_by_index,
    # Diagnostics
    "blender-capabilities": executor.capabilities,
    "blender-validate-tool": executor.validate_tool,
    "blender-diag-validate-tool": executor.validate_tool,
    # Safe-first mesh operations
    "blender-mesh-set-selection": executor.mesh_set_selection,
    "blender-mesh-bisect-plane": executor.mesh_bisect_plane,
    "blender-mesh-delete-by-index": executor.mesh_delete_by_index,
    "blender-mesh-translate-selection": executor.mesh_translate_selection,
    "blender-mesh-scale-selection": executor.mesh_scale_selection,
    "blender-mesh-extrude-selection": executor.mesh_extrude_selection,
    "blender-mesh-inset-selection": executor.mesh_inset_selection,
    "blender-mesh-select-by-normal": executor.mesh_select_by_normal,
    "blender-mesh-duplicate-selection": executor.mesh_duplicate_selection,
    "blender-diag-scene-snapshot": executor.scene_snapshot,
    "blender-diag-object-snapshot": executor.object_snapshot,
    "blender-exec-python": executor.exec_python,
    # New object ops
    "blender-object-join": executor.object_join,
    "blender-object-separate": executor.object_separate,
    "blender-object-shade": executor.object_shade,
    "blender-object-rotate": executor.object_rotate,
    "blender-object-mirror": executor.object_mirror,
    "blender-object-snap": executor.object_snap,
    # Modifiers
    "blender-modifier-apply": executor.modifier_apply,
    "blender-modifier-move": executor.modifier_move,
    "blender-modifier-remove": executor.modifier_remove,
    # Mesh advanced
    "blender-mesh-spin": executor.mesh_spin,
    "blender-mesh-screw": executor.mesh_screw,
    "blender-mesh-normals": executor.mesh_normals,
    # Materials
    "blender-material-assign": executor.material_assign,
    "blender-material-create": executor.material_create,
    # Curves
    "blender-curve-primitive": executor.curve_primitive,
    "blender-curve-convert": executor.curve_convert,
    # P0 transforms
    "blender-object-scale": executor.object_scale,
    "blender-object-apply-transform": executor.object_apply_transform,
    "blender-object-origin-set": executor.object_origin_set,
    "blender-object-parent": executor.object_parent,
    "blender-object-clear-transform": executor.object_clear_transform,
    "blender-mesh-rotate-selection": executor.mesh_rotate_selection,
    "blender-object-duplicate": executor.object_duplicate,
    # Modifiers P0
    "blender-modifier-add": executor.modifier_add,
    "blender-modifier-configure": executor.modifier_configure,
    "blender-modifier-configure-array": executor.modifier_configure_array,
    "blender-modifier-configure-mirror": executor.modifier_configure_mirror,
    "blender-mesh-bridge-edge-loops": executor.mesh_bridge_edge_loops,
    "blender-mesh-fill": executor.mesh_fill,
    "blender-mesh-grid-fill": executor.mesh_grid_fill,
    "blender-mesh-remove-doubles": executor.mesh_remove_doubles,
    # Selection avancée
    "blender-mesh-select-similar": executor.mesh_select_similar,
    "blender-mesh-select-by-trait": executor.mesh_select_by_trait,
    "blender-mesh-select-nth": executor.mesh_select_nth,
    "blender-mesh-select-random": executor.mesh_select_random,
    "blender-mesh-select-face-by-sides": executor.mesh_select_face_by_sides,
    # UV unwrap / projections
    "blender-uv-unwrap": executor.uv_unwrap,
    "blender-uv-smart-project": executor.uv_smart_project,
    "blender-uv-cube-project": executor.uv_cube_project,
    "blender-uv-cylinder-project": executor.uv_cylinder_project,
    "blender-uv-sphere-project": executor.uv_sphere_project,
    # Collections
    "blender-collection-create": executor.collection_create,
    "blender-collection-add-objects": executor.collection_add_objects,
    "blender-collection-remove-objects": executor.collection_remove_objects,
    "blender-collection-hide": executor.collection_hide,
    # Rename / IO
    "blender-object-rename": executor.object_rename,
    "blender-import-file": executor.import_file,
    "blender-export-file": executor.export_file,
    # Mesh cleanup P1
    "blender-mesh-recalculate-normals": executor.mesh_recalculate_normals,
    "blender-mesh-validate": executor.mesh_validate,
    "blender-mesh-triangulate": executor.mesh_triangulate,
    # Missing tools - now implemented
    "blender-mesh-query-geometry": executor.mesh_query_geometry,
    "blender-mesh-query-selection": executor.mesh_query_selection,
    "blender-mesh-query-topology": executor.mesh_query_topology,
    "blender-viewport-screenshot-complete": executor.viewport_screenshot_complete,
    "blender-modifier-bevel": executor.modifier_bevel,
    "blender-mesh-extrude-manifold": executor.mesh_extrude_manifold,
    "blender-material-assign-fixed": executor.material_assign_fixed,
}


def _schedule_timer_once() -> None:
    _ensure_bpy()

    def _process_queue():  # pragma: no cover - requires Blender runtime
        task = task_queue.pop()
        if task:
            try:
                task()
            except Exception:
                pass
        return 0.05

    bpy.app.timers.register(_process_queue, persistent=True)


def _execute_tool(tool: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool using the dynamic registry (supports old and new names)."""
    if not isinstance(args, dict):
        args = {}

    executor_func = _TOOL_REGISTRY.get(tool)
    if executor_func is None:
        return error_response(f"Unknown tool '{tool}'", code="unknown_tool")

    try:
        return executor_func(args)
    except Exception as exc:
        return error_response(f"Tool execution failed: {str(exc)}", code="execution_error")


class BridgeRequestHandler(BaseHTTPRequestHandler):
    server_version = "AthenaBlenderBridge/0.1"

    def _read_json(self) -> Optional[Dict[str, Any]]:
        length_header = self.headers.get("Content-Length")
        if not length_header:
            return None
        try:
            length = int(length_header)
        except ValueError:
            return None
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return None

    def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:  # pragma: no cover - silence default logging
        return

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send_json(ok_response(service="athena-blender-bridge"))
        else:
            self._send_json(error_response("not found", code="not_found"), status=404)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/exec":
            self._send_json(error_response("not found", code="not_found"), status=404)
            return
        payload = self._read_json()
        if not isinstance(payload, dict):
            self._send_json(error_response("invalid json", code="bad_request"), status=400)
            return
        tool = payload.get("tool") or payload.get("name")
        raw_args = payload.get("args")
        if raw_args is None:
            raw_args = payload.get("arguments")
        if raw_args is None:
            raw_args = payload.get("params") or payload.get("parameters")
        if raw_args is None:
            raw_args = {}
        if not isinstance(tool, str):
            self._send_json(error_response("missing tool", code="bad_request"), status=400)
            return
        if not isinstance(raw_args, dict):
            self._send_json(error_response("args must be object", code="bad_request"), status=400)
            return
        args = raw_args

        done = threading.Event()
        result_box: Dict[str, Any] = {}

        def _job() -> None:
            try:
                result_box["result"] = _execute_tool(tool, args)
                result_box["status"] = "ok"
            except Exception as exc:
                result_box["status"] = "error"
                result_box["error"] = str(exc)
            finally:
                done.set()

        task_queue.push(_job)
        # Wait for main-thread execution signalled by timer.
        finished = done.wait(timeout=_WAIT_TIMEOUT)
        if not finished:
            self._send_json(error_response("execution timeout", code="timeout"), status=504)
            return
        if result_box.get("status") != "ok":
            error_payload = result_box.get("error", "bridge error")
            self._send_json(error_response(str(error_payload), code="bridge_error"), status=200)
            return
        self._send_json(ok_response(result=result_box.get("result", {})))


def main() -> None:
    _ensure_bpy()
    _schedule_timer_once()
    host = _DEFAULT_HOST
    port = _DEFAULT_PORT

    server = ThreadingHTTPServer((host, port), BridgeRequestHandler)
    server.daemon_threads = True

    def _serve() -> None:  # pragma: no cover - requires runtime
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass

    thread = threading.Thread(target=_serve, daemon=True, name="athena-bridge-http")
    thread.start()
    atexit.register(server.shutdown)
    print(f"Blender bridge listening on http://{host}:{port} (background thread)")  # pragma: no cover - console hint
    # Do not block Blender UI thread; the timer will keep processing jobs.


if __name__ == "__main__":  # pragma: no cover - entrypoint
    main()
