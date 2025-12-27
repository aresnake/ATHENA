import threading

import requests

from athena_mcp.mcp_core.transport_http import serve


def start_server():
    server = serve("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_tools_list_endpoint():
    server, thread = start_server()
    host, port = server.server_address
    try:
        resp = requests.get(f"http://{host}:{port}/tools/list", timeout=2)
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        tools = data["tools"]
        assert len(tools) == 3
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool
    finally:
        server.shutdown()
        thread.join(timeout=2)
