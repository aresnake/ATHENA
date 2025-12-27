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
    if tool == "blender-list-objects":
        return executor.list_objects(args)
    if tool == "blender-add-cube":
        if not isinstance(args, dict):
            return error_response("args must be object", code="bad_request")
        if "name" in args and not isinstance(args.get("name"), str):
            return error_response("name must be a string", code="bad_request")
        if "size" in args and not isinstance(args.get("size"), (int, float)):
            return error_response("size must be a number", code="bad_request")
        return executor.add_cube(args)
    if tool == "blender-move-object":
        if not isinstance(args, dict):
            return error_response("args must be object", code="bad_request")
        return executor.move_object(args)
    if tool == "blender-set-mode":
        if not isinstance(args, dict):
            return error_response("args must be object", code="bad_request")
        return executor.set_mode(args)
    if tool == "blender-set-selection-mode":
        if not isinstance(args, dict):
            return error_response("args must be object", code="bad_request")
        return executor.set_selection_mode(args)
    if tool == "blender-select-all":
        return executor.select_all(args)
    if tool == "blender-select-none":
        return executor.select_none(args)
    if tool == "blender-select-invert":
        return executor.select_invert(args)
    if tool == "blender-mesh-delete":
        if not isinstance(args, dict):
            return error_response("args must be object", code="bad_request")
        return executor.mesh_delete(args)
    if tool == "blender-mesh-extrude":
        if not isinstance(args, dict):
            return error_response("args must be object", code="bad_request")
        return executor.mesh_extrude(args)
    if tool == "blender-mesh-inset":
        if not isinstance(args, dict):
            return error_response("args must be object", code="bad_request")
        return executor.mesh_inset(args)
    if tool == "blender-mesh-loop-cut":
        if not isinstance(args, dict):
            return error_response("args must be object", code="bad_request")
        return executor.mesh_loop_cut(args)
    if tool == "blender-mesh-bevel":
        if not isinstance(args, dict):
            return error_response("args must be object", code="bad_request")
        return executor.mesh_bevel(args)
    if tool == "blender-mesh-subdivide":
        if not isinstance(args, dict):
            return error_response("args must be object", code="bad_request")
        return executor.mesh_subdivide(args)
    if tool == "blender-mesh-merge":
        if not isinstance(args, dict):
            return error_response("args must be object", code="bad_request")
        return executor.mesh_merge(args)
    if tool == "blender-mesh-select-loop":
        return executor.mesh_select_loop(args)
    if tool == "blender-mesh-select-ring":
        return executor.mesh_select_ring(args)
    if tool == "blender-mesh-select-linked":
        return executor.mesh_select_linked(args)
    if tool == "blender-mesh-select-more":
        return executor.mesh_select_more(args)
    if tool == "blender-mesh-select-less":
        return executor.mesh_select_less(args)
    if tool == "blender-mesh-select-non-manifold":
        return executor.mesh_select_non_manifold(args)
    if tool == "blender-mesh-select-boundary":
        return executor.mesh_select_boundary(args)
    if tool == "blender-mesh-select-by-index":
        if not isinstance(args, dict):
            return error_response("args must be object", code="bad_request")
        return executor.mesh_select_by_index(args)
    if tool == "blender-capabilities":
        return executor.capabilities(args)
    if tool == "blender-validate-tool":
        if not isinstance(args, dict):
            return error_response("args must be object", code="bad_request")
        return executor.validate_tool(args)
    return error_response(f"Unknown tool '{tool}'", code="unknown_tool")


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
        args = payload.get("args", payload.get("arguments", {}))
        if not isinstance(tool, str):
            self._send_json(error_response("missing tool", code="bad_request"), status=400)
            return
        if not isinstance(args, dict):
            self._send_json(error_response("args must be object", code="bad_request"), status=400)
            return

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
