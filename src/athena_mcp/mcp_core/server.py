from __future__ import annotations

import argparse
import os
import sys
import threading

from .transport_http import serve as serve_http
from .transport_stdio import serve_stdio


def _stdio_hardening() -> None:
    """
    MCP stdio rule:
    - STDOUT must contain ONLY JSON-RPC messages.
    - Any debug/log/print MUST go to STDERR.
    This hardening redirects accidental prints/logs to STDERR.
    """
    # Keep a handle to the real STDOUT for the JSON-RPC writer (transport_stdio should use sys.__stdout__ or sys.stdout.write)
    # Redirect "normal" stdout to stderr to prevent accidental pollution.
    # sys.__stdout__ remains the original stream.
    sys.stdout = sys.stderr  # type: ignore[assignment]

    # Make stderr unbuffered-ish for better logs in Claude Desktop
    try:
        sys.stderr.reconfigure(line_buffering=True)  # py3.7+
    except Exception:
        pass

    os.environ.setdefault("PYTHONUNBUFFERED", "1")


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

    threads: list[tuple[threading.Thread, object]] = []

    if args.http:
        http_server = serve_http(args.host, args.port)
        http_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
        http_thread.start()
        threads.append((http_thread, http_server))

    if args.stdio:
        _stdio_hardening()
        try:
            serve_stdio()
        except KeyboardInterrupt:
            return
    else:
        try:
            while threads:
                for thread, _server in threads:
                    thread.join(timeout=0.5)
        except KeyboardInterrupt:
            for _, server in threads:
                # type: ignore[attr-defined]
                server.shutdown()  # pragma: no cover


if __name__ == "__main__":
    main()
