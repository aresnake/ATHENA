import threading

import requests

from athena_mcp.tools import registry
from athena_mcp.mcp_core.transport_http import serve


def start_server():
    server = serve("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_set_mode_payload(monkeypatch):
    captured = {}

    def _mock_bridge(tool, args):
        captured["tool"] = tool
        captured["args"] = args
        return {"ok": True, "result": {"mode": args.get("mode"), "active": args.get("name", "Cube")}}

    monkeypatch.setattr(registry, "_bridge_request", _mock_bridge)
    result = registry.call_tool("blender-set-mode", {"mode": "EDIT", "name": "Cube"})
    assert result["ok"] is True
    assert captured["tool"] == "blender-set-mode"
    assert captured["args"]["mode"] == "EDIT"
    assert captured["args"]["name"] == "Cube"


def test_mesh_extrude_http_payload(monkeypatch):
    def _mock_bridge(tool, args):
        return {"ok": True, "result": {"tool": tool, "delta": [args.get("x"), args.get("y"), args.get("z")]}}

    monkeypatch.setattr(registry, "_bridge_request", _mock_bridge)

    server, thread = start_server()
    host, port = server.server_address
    try:
        resp = requests.post(
            f"http://{host}:{port}/tools/call",
            json={"name": "blender-mesh-extrude", "arguments": {"x": 0, "y": 0, "z": 1}},
            timeout=2,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["result"]["delta"] == [0, 0, 1]
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_select_loop_http_arguments(monkeypatch):
    captured = {}

    def _mock_bridge(tool, args):
        captured["tool"] = tool
        captured["args"] = args
        return {"ok": True, "result": {"select_loop": True, **args}}

    monkeypatch.setattr(registry, "_bridge_request", _mock_bridge)

    server, thread = start_server()
    host, port = server.server_address
    try:
        resp = requests.post(
            f"http://{host}:{port}/tools/call",
            json={"name": "blender-mesh-select-loop", "arguments": {"extend": True}},
            timeout=2,
        )
        data = resp.json()
        assert data["ok"] is True
        assert captured["tool"] == "blender-mesh-select-loop"
        assert captured["args"]["extend"] is True
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_safe_delete_by_index_forwarding(monkeypatch):
    captured = {}

    def _mock_bridge(tool, args):
        captured["tool"] = tool
        captured["args"] = args
        return {"ok": True, "result": {"deleted": True, **args}}

    monkeypatch.setattr(registry, "_bridge_request", _mock_bridge)

    server, thread = start_server()
    host, port = server.server_address
    try:
        resp = requests.post(
            f"http://{host}:{port}/tools/call",
            json={"name": "blender-mesh-delete-by-index", "arguments": {"element": "VERT", "indices": [1, 2]}},
            timeout=2,
        )
        data = resp.json()
        assert data["ok"] is True
        assert captured["tool"] == "blender-mesh-delete-by-index"
        assert captured["args"]["element"] == "VERT"
        assert captured["args"]["indices"] == [1, 2]
    finally:
        server.shutdown()
        thread.join(timeout=2)
