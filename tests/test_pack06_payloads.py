import threading

import requests

from athena_mcp.mcp_core.transport_http import serve
from athena_mcp.tools import registry


def start_server():
    server = serve("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_duplicate_selection_arguments(monkeypatch):
    captured = {}

    def _mock_bridge(tool, args):
        captured["tool"] = tool
        captured["args"] = args
        return {"ok": True, "result": {"duplicated": True, **args}}

    monkeypatch.setattr(registry, "_bridge_request", _mock_bridge)

    server, thread = start_server()
    host, port = server.server_address
    try:
        resp = requests.post(
            f"http://{host}:{port}/tools/call",
            json={"name": "blender-mesh-duplicate-selection", "arguments": {"dx": 1, "dy": 2, "dz": 3}},
            timeout=2,
        )
        data = resp.json()
        assert data["ok"] is True
        assert captured["tool"] == "blender-mesh-duplicate-selection"
        assert captured["args"] == {"dx": 1, "dy": 2, "dz": 3}
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_duplicate_selection_defaults(monkeypatch):
    captured = {}

    def _mock_bridge(tool, args):
        captured["args"] = args
        return {"ok": True, "result": {"duplicated": True, **args}}

    monkeypatch.setattr(registry, "_bridge_request", _mock_bridge)
    result = registry.call_tool("blender-mesh-duplicate-selection", {})
    assert result["ok"] is True
    assert captured["args"] == {"dx": 0.0, "dy": 0.0, "dz": 0.0}
