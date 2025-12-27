from __future__ import annotations

import json
import sys
from typing import TextIO

from ..tools import call_tool, list_tools
from .types import error_response, ok_response


def _read_line(stream: TextIO) -> str | None:
    line = stream.readline()
    return line if line else None


def serve_stdio(stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> None:
    """
    Minimal stdio transport.
    Expects JSON lines with {"action": "..."}.
    """
    for raw in iter(lambda: _read_line(stdin), None):
        raw = raw.strip()
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            stdout.write(json.dumps(error_response("invalid json", code="bad_request")) + "\n")
            stdout.flush()
            continue
        action = payload.get("action")
        if action == "health":
            response = ok_response(service="athena-mcp")
        elif action == "tools/list":
            response = ok_response(tools=list_tools())
        elif action == "tools/call":
            name = payload.get("name")
            args = payload.get("args", {})
            if not isinstance(name, str) or not isinstance(args, dict):
                response = error_response("invalid call payload", code="bad_request")
            else:
                response = call_tool(name, args)
        else:
            response = error_response("unknown action", code="unknown_action")
        stdout.write(json.dumps(response) + "\n")
        stdout.flush()
