from __future__ import annotations

import argparse
import http.client
import json
import threading
from typing import Any, Dict

from ..tools import set_bridge_request
from .transport_http import serve as serve_http
from .transport_stdio import serve_stdio


def _bridge_http(tool: str, args: Dict[str, Any], host: str, port: int) -> Dict[str, Any]:
    payload = json.dumps({"tool": tool, "args": args}).encode("utf-8")
    conn = http.client.HTTPConnection(host, port, timeout=5)
    try:
        conn.request(
            "POST",
            "/exec",
            body=payload,
            headers={"Content-Type": "application/json", "Content-Length": str(len(payload))},
        )
        resp = conn.getresponse()
        body = resp.read()
    finally:
        conn.close()
    try:
        data = json.loads(body.decode("utf-8"))
    except Exception:
        raise RuntimeError("Invalid response from bridge")
    if resp.status != 200 or not isinstance(data, dict):
        raise RuntimeError("Bridge returned non-200")
    if not data.get("ok"):
        error = data.get("error") or {}
        message = error.get("message") if isinstance(error, dict) else "bridge error"
        raise RuntimeError(message or "bridge error")
    return data.get("result", {})


def main() -> None:
    parser = argparse.ArgumentParser(description="Athena MCP server")
    parser.add_argument("--http", action="store_true", help="Run HTTP transport")
    parser.add_argument("--stdio", action="store_true", help="Run stdio transport")
    parser.add_argument("--host", default="127.0.0.1", help="Host for HTTP transport")
    parser.add_argument("--port", type=int, default=9000, help="Port for HTTP transport")
    parser.add_argument("--bridge-host", default="127.0.0.1", help="Blender bridge host")
    parser.add_argument("--bridge-port", type=int, default=8765, help="Blender bridge port")
    args = parser.parse_args()

    set_bridge_request(lambda tool, payload: _bridge_http(tool, payload, args.bridge_host, args.bridge_port))

    threads = []

    if args.http:
        http_server = serve_http(args.host, args.port)
        http_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
        http_thread.start()
        threads.append((http_thread, http_server))

    if args.stdio:
        try:
            serve_stdio()
        except KeyboardInterrupt:
            return
    else:
        try:
            while threads:
                for thread, server in threads:
                    thread.join(timeout=0.5)
        except KeyboardInterrupt:
            for _, server in threads:
                server.shutdown()


if __name__ == "__main__":
    main()
