import threading

import requests

from athena_mcp.tools import registry
from athena_mcp.mcp_core.transport_http import serve


def start_server():
    server = serve("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_arguments_alias_forwarding(monkeypatch):
    captured = {}

    def _mock_bridge(tool, args):
        captured["tool"] = tool
        captured["args"] = args
        return {"ok": True, "result": {"echo": tool, "args": args}}

    monkeypatch.setattr(registry, "_bridge_request", _mock_bridge)

    server, thread = start_server()
    host, port = server.server_address
    try:
        resp = requests.post(
            f"http://{host}:{port}/tools/call",
            json={"name": "blender-object-move", "arguments": {"name": "Cube", "x": 2, "y": 0, "z": 0}},
            timeout=2,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert captured["tool"] == "blender-object-move"
        assert captured["args"]["name"] == "Cube"
        assert captured["args"]["x"] == 2
    finally:
        server.shutdown()
        thread.join(timeout=2)
