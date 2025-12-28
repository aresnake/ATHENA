import threading

import requests

from athena_mcp import tools
from athena_mcp.tools import registry
from athena_mcp.mcp_core.transport_http import serve


def test_schema_includes_name():
    schema = [t for t in registry.TOOLS if t.name == "blender-primitive-cube"][0].input_schema
    assert "name" in schema.get("properties", {})


def test_add_cube_defaults_send_name(monkeypatch):
    calls = {}

    def _mock_bridge(tool, args):
        calls["tool"] = tool
        calls["args"] = args
        return {"ok": True, "result": {"received": args}}

    monkeypatch.setattr(registry, "_bridge_request", _mock_bridge)

    result = tools.call_tool("blender-primitive-cube", {})
    assert result["ok"] is True
    assert calls["tool"] == "blender-primitive-cube"
    assert calls["args"]["name"] == "Cube"


def start_server():
    server = serve("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_add_cube_http_call_with_default_name(monkeypatch):
    def _mock_bridge(tool, args):
        return {"ok": True, "result": {"tool": tool, "name": args.get("name")}}

    monkeypatch.setattr(registry, "_bridge_request", _mock_bridge)

    server, thread = start_server()
    host, port = server.server_address
    try:
        resp = requests.post(f"http://{host}:{port}/tools/call", json={"name": "blender-primitive-cube", "args": {}}, timeout=2)
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["result"]["name"] == "Cube"
    finally:
        server.shutdown()
        thread.join(timeout=2)
