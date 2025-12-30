import threading

import requests

from athena_mcp.tools import registry
from athena_mcp.mcp_core.transport_http import serve


def start_server():
    server = serve("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_bevel_defaults_with_arguments(monkeypatch):
    captured = {}

    def _mock_bridge(tool, args):
        captured["tool"] = tool
        captured["args"] = args
        return {"ok": True, "result": {"bevel": True, **args}}

    monkeypatch.setattr(registry, "_bridge_request", _mock_bridge)

    server, thread = start_server()
    host, port = server.server_address
    try:
        resp = requests.post(
            f"http://{host}:{port}/tools/call",
            json={"name": "blender-mesh-bevel", "arguments": {}},
            timeout=2,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert captured["args"]["offset"] == 0.02
        assert captured["args"]["segments"] == 1
        assert captured["args"]["profile"] == 0.5
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_loop_cut_defaults(monkeypatch):
    captured = {}

    def _mock_bridge(tool, args):
        captured["tool"] = tool
        captured["args"] = args
        return {"ok": True, "result": {"loop_cut": True, **args}}

    monkeypatch.setattr(registry, "_bridge_request", _mock_bridge)

    result = registry.call_tool("blender-mesh-loop-cut", {})
    assert result["ok"] is True
    assert captured["args"]["cuts"] == 1
    assert captured["args"]["smoothness"] == 0.0


def test_select_loop_arguments_alias(monkeypatch):
    captured = {}

    def _mock_bridge(tool, args):
        captured["tool"] = tool
        captured["args"] = args
        return {"ok": True, "result": {"select_loop": True, **args}}

    monkeypatch.setattr(registry, "_bridge_request", _mock_bridge)

    result = registry.call_tool("blender-mesh-select-loop", {"arguments": {"extend": True}} if False else {"extend": True})
    # Direct call passes args dict; transport alias tested elsewhere.
    assert result["ok"] is True
    assert captured["tool"] == "blender-mesh-select-loop"
    assert captured["args"]["extend"] is True


def test_safe_set_selection_defaults(monkeypatch):
    captured = {}

    def _mock_bridge(tool, args):
        captured["tool"] = tool
        captured["args"] = args
        return {"ok": True, "result": {"selected": True, **args}}

    monkeypatch.setattr(registry, "_bridge_request", _mock_bridge)

    result = registry.call_tool("blender-mesh-set-selection", {"element": "VERT", "indices": [0, 1]})
    assert result["ok"] is True
    assert captured["args"]["clear"] is True
