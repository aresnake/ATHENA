from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Optional, Tuple

from ..tools import call_tool, list_tools
from .types import error_response, ok_response


class MCPHTTPRequestHandler(BaseHTTPRequestHandler):
    server_version = "AthenaMCP/0.1"

    def _read_json(self) -> Tuple[Optional[dict], Optional[str]]:
        length_header = self.headers.get("Content-Length")
        if not length_header:
            return None, "missing content-length"
        try:
            length = int(length_header)
        except ValueError:
            return None, "invalid content-length"
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8")), None
        except json.JSONDecodeError:
            return None, "invalid json"

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:  # pragma: no cover - default quiet
        return

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path == "/health":
            self._send_json(ok_response(service="athena-mcp"))
            return
        if self.path == "/tools/list":
            self._send_json(ok_response(tools=list_tools()))
            return
        self._send_json(error_response("not found", code="not_found"), status=404)

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path != "/tools/call":
            self._send_json(error_response("not found", code="not_found"), status=404)
            return
        payload, error = self._read_json()
        if error or not isinstance(payload, dict):
            self._send_json(error_response(error or "invalid request", code="bad_request"), status=400)
            return
        name = payload.get("name")
        args = payload.get("args", payload.get("arguments", {}))
        if not isinstance(name, str):
            self._send_json(error_response("missing tool name", code="bad_request"), status=400)
            return
        if not isinstance(args, dict):
            self._send_json(error_response("args must be object", code="bad_request"), status=400)
            return
        response = call_tool(name, args)
        if response.get("ok") and isinstance(response.get("result"), dict):
            inner = response["result"]
            if isinstance(inner, dict) and "ok" in inner:
                if inner.get("ok"):
                    response = ok_response(result=inner.get("result", {}))
                else:
                    err = inner.get("error") or {}
                    message = err.get("message") if isinstance(err, dict) else "Bridge tool error"
                    details = err.get("details") if isinstance(err, dict) else {}
                    response = error_response(message or "Bridge tool error", code="bridge_tool_error", details=details or err or {})
        status = 200 if response.get("ok") else 400
        self._send_json(response, status=status)


def serve(host: str, port: int) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), MCPHTTPRequestHandler)
    return server
