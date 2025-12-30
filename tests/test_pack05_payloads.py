import threading

import requests

from athena_mcp.tools import registry
from athena_mcp.mcp_core.transport_http import serve


def start_server():
    server = serve("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_translate_selection_arguments(monkeypatch):
    captured = {}

    def _mock_bridge(tool, args):
        captured["tool"] = tool
        captured["args"] = args
        return {"ok": True, "result": {"translated": True, **args}}

    monkeypatch.setattr(registry, "_bridge_request", _mock_bridge)

    server, thread = start_server()
    host, port = server.server_address
    try:
        resp = requests.post(
            f"http://{host}:{port}/tools/call",
            json={"name": "blender-mesh-translate-selection", "arguments": {"dx": 1, "dy": 0, "dz": 0}},
            timeout=2,
        )
        data = resp.json()
        assert data["ok"] is True
        assert captured["tool"] == "blender-mesh-translate-selection"
        assert captured["args"] == {"dx": 1, "dy": 0, "dz": 0}
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_schema_defaults_pack05():
    tools = {t.name: t for t in registry.TOOLS}
    inset_schema = tools["blender-mesh-inset-selection"].input_schema
    props = inset_schema["properties"]
    assert props["thickness"]["default"] == 0.05
    assert props["depth"]["default"] == 0.0

    normal_schema = tools["blender-mesh-select-by-normal"].input_schema
    props_n = normal_schema["properties"]
    assert props_n["sign"]["default"] == 1
    assert props_n["threshold"]["default"] == 0.9
    assert props_n["extend"]["default"] is False
