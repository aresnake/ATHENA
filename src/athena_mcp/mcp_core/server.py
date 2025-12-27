from __future__ import annotations

import argparse
import os
import threading

from .transport_http import serve as serve_http
from .transport_stdio import serve_stdio


def main() -> None:
    parser = argparse.ArgumentParser(description="Athena MCP server")
    parser.add_argument("--http", action="store_true", help="Run HTTP transport")
    parser.add_argument("--stdio", action="store_true", help="Run stdio transport")
    parser.add_argument("--host", default="127.0.0.1", help="Host for HTTP transport")
    parser.add_argument("--port", type=int, default=9000, help="Port for HTTP transport")
    parser.add_argument("--bridge-host", default="127.0.0.1", help="Blender bridge host")
    parser.add_argument("--bridge-port", type=int, default=8765, help="Blender bridge port")
    args = parser.parse_args()

    os.environ["ATHENA_BRIDGE_URL"] = f"http://{args.bridge_host}:{args.bridge_port}"

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
