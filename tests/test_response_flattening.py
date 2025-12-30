import threading

import requests

from athena_mcp.tools import registry
from athena_mcp.mcp_core.transport_http import serve


def start_server():
    server = serve("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_tools_call_flatten_nested_ok(monkeypatch):
    def _mock_bridge(tool, args):
        return {"ok": True, "result": {"ok": True, "result": {"hello": "world"}}}

    monkeypatch.setattr(registry, "_bridge_request", _mock_bridge)

    server, thread = start_server()
    host, port = server.server_address
    try:
        resp = requests.post(
            f"http://{host}:{port}/tools/call",
            json={"name": "blender-primitive-cube", "args": {}},
            timeout=2,
        )
        data = resp.json()
        assert data["ok"] is True
        assert data["result"] == {"hello": "world"}
    finally:
        server.shutdown()
        thread.join(timeout=2)
