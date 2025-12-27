from __future__ import annotations

import http.client
import json
import os
import socket
import urllib.parse
from typing import Any, Dict

JSONDict = Dict[str, Any]


def _error(code: str, message: str, **details: Any) -> JSONDict:
    payload: JSONDict = {"ok": False, "error": {"code": code, "message": message}}
    if details:
        payload["error"]["details"] = details
    return payload


def bridge_request(tool: str, args: JSONDict, timeout: float = 2.0) -> JSONDict:
    base_url = os.getenv("ATHENA_BRIDGE_URL", "http://127.0.0.1:8765")
    parsed = urllib.parse.urlparse(base_url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return _error("invalid_bridge_url", f"Invalid ATHENA_BRIDGE_URL: {base_url}")

    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    path = (parsed.path.rstrip("/") or "") + "/exec"

    payload = {"tool": tool, "args": args or {}}
    body = json.dumps(payload).encode("utf-8")

    try:
        conn = http.client.HTTPConnection(host, port, timeout=timeout)
        conn.request(
            "POST",
            path,
            body=body,
            headers={"Content-Type": "application/json", "Content-Length": str(len(body))},
        )
        resp = conn.getresponse()
        data_bytes = resp.read()
    except (socket.timeout, ConnectionRefusedError, OSError, http.client.HTTPException) as exc:
        return _error("bridge_unreachable", "Could not reach Blender bridge", details=str(exc))
    finally:
        try:
            conn.close()
        except Exception:
            pass

    try:
        data = json.loads(data_bytes.decode("utf-8"))
    except Exception:
        return _error("invalid_bridge_response", "Bridge returned invalid JSON")

    if resp.status != 200:
        return _error("bridge_http_error", f"Bridge HTTP {resp.status}", details=data if isinstance(data, dict) else {})

    if not isinstance(data, dict):
        return _error("invalid_bridge_response", "Bridge response was not an object")

    if data.get("ok"):
        return {"ok": True, "result": data.get("result", {})}

    error = data.get("error") or {}
    message = error.get("message") if isinstance(error, dict) else "Bridge error"
    code = error.get("code") if isinstance(error, dict) else "bridge_error"
    details = error.get("details") if isinstance(error, dict) else {}
    return _error(code or "bridge_error", message or "Bridge error", **(details or {}))
