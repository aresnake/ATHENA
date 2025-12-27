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
        names = {t["name"] for t in tools}
        expected = {
            "blender-list-objects",
            "blender-add-cube",
            "blender-move-object",
            "blender-set-mode",
            "blender-set-selection-mode",
            "blender-select-all",
            "blender-select-none",
            "blender-select-invert",
            "blender-mesh-delete",
            "blender-mesh-extrude",
            "blender-mesh-inset",
            "blender-mesh-loop-cut",
            "blender-mesh-bevel",
            "blender-mesh-subdivide",
            "blender-mesh-merge",
            "blender-mesh-select-loop",
            "blender-mesh-select-ring",
            "blender-mesh-select-linked",
            "blender-mesh-select-more",
            "blender-mesh-select-less",
            "blender-mesh-select-non-manifold",
            "blender-mesh-select-boundary",
            "blender-mesh-select-by-index",
            "blender-mesh-set-selection",
            "blender-mesh-bisect-plane",
            "blender-mesh-delete-by-index",
            "blender-capabilities",
            "blender-validate-tool",
            "blender-mesh-translate-selection",
            "blender-mesh-scale-selection",
            "blender-mesh-extrude-selection",
            "blender-mesh-inset-selection",
            "blender-mesh-select-by-normal",
            "blender-mesh-duplicate-selection",
        }
        assert expected.issubset(names)
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool
    finally:
        server.shutdown()
        thread.join(timeout=2)
