import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

from athena_mcp.mcp_core.transport_http import serve


class FakeBridgeHandler(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        self.server.last_tool = payload.get("tool")  # type: ignore[attr-defined]
        body = json.dumps({"ok": True, "result": {"echo": payload.get("tool"), "args": payload.get("args")}}).encode(
            "utf-8"
        )
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):  # pragma: no cover - quiet
        return


def start_fake_bridge():
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeBridgeHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def start_mcp():
    server = serve("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_tools_call_uses_bridge_env(monkeypatch):
    bridge_server, bridge_thread = start_fake_bridge()
    host, port = bridge_server.server_address
    monkeypatch.setenv("ATHENA_BRIDGE_URL", f"http://{host}:{port}")

    mcp_server, mcp_thread = start_mcp()
    mcp_host, mcp_port = mcp_server.server_address
    try:
        resp = requests.post(
            f"http://{mcp_host}:{mcp_port}/tools/call",
            json={"name": "blender-move-object", "args": {"name": "Cube", "location": [1, 2, 3]}},
            timeout=2,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["result"]["echo"] == "blender-move-object"
        assert data["result"]["args"]["name"] == "Cube"
        assert getattr(bridge_server, "last_tool") == "blender-move-object"
    finally:
        mcp_server.shutdown()
        mcp_thread.join(timeout=2)
        bridge_server.shutdown()
        bridge_thread.join(timeout=2)
