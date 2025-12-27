import threading

import requests

from athena_mcp.mcp_core.transport_http import serve
from athena_mcp.tools import registry


def start_server():
    server = serve("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_scene_snapshot_defaults(monkeypatch):
    captured = {}

    def _mock_bridge(tool, args):
        captured["tool"] = tool
        captured["args"] = args
        return {"ok": True, "result": {"objects": []}}

    monkeypatch.setattr(registry, "_bridge_request", _mock_bridge)
    result = registry.call_tool("blender-scene-snapshot", {})
    assert result["ok"] is True
    assert captured["tool"] == "blender-scene-snapshot"
    assert captured["args"]["include_mesh_stats"] is True
    assert captured["args"]["max_objects"] == 200
    assert captured["args"]["max_materials_per_object"] == 32
    assert captured["args"]["max_items_per_list"] == 5000


def test_object_snapshot_arguments_alias(monkeypatch):
    captured = {}

    def _mock_bridge(tool, args):
        captured["tool"] = tool
        captured["args"] = args
        return {"ok": True, "result": {"name": args.get("name")}}

    monkeypatch.setattr(registry, "_bridge_request", _mock_bridge)

    server, thread = start_server()
    host, port = server.server_address
    try:
        resp = requests.post(
            f"http://{host}:{port}/tools/call",
            json={"name": "blender-object-snapshot", "arguments": {"name": "Cube"}},
            timeout=2,
        )
        data = resp.json()
        assert data["ok"] is True
        assert captured["tool"] == "blender-object-snapshot"
        assert captured["args"]["name"] == "Cube"
    finally:
        server.shutdown()
        thread.join(timeout=2)
