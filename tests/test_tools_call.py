import threading

import requests

from athena_mcp.mcp_core import transport_http
from athena_mcp.tools import registry


def start_server():
    server = transport_http.serve("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_tools_call_with_mock_bridge(monkeypatch):
    monkeypatch.setattr(
        registry,
        "_bridge_request",
        lambda tool, args: {"echo": tool, "args": args, "marker": "mock"},
    )

    server, thread = start_server()
    host, port = server.server_address
    try:
        payload = {"name": "blender-primitive-cube", "args": {"name": "CubeOne"}}
        resp = requests.post(
            f"http://{host}:{port}/tools/call",
            json=payload,
            timeout=2,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["result"]["echo"] == "blender-primitive-cube"
        assert data["result"]["args"]["name"] == "CubeOne"
        assert data["result"]["marker"] == "mock"
    finally:
        server.shutdown()
        thread.join(timeout=2)
