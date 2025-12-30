import threading

import requests

from athena_mcp.mcp_core.transport_http import serve


def test_health_endpoint():
    server = serve("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    try:
        resp = requests.get(f"http://{host}:{port}/health", timeout=2)
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["service"] == "athena-mcp"
    finally:
        server.shutdown()
        thread.join(timeout=2)
