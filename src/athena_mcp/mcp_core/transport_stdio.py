from __future__ import annotations

import json
import logging
import sys
import traceback
from typing import Any, Dict, TextIO

from ..tools import call_tool, list_tools
from .types import jsonrpc_error, jsonrpc_result

LOGGER = logging.getLogger("athena_mcp.stdio")
PROTOCOL_VERSION = "2024-11-05"


def _read_line(stream: TextIO) -> str | None:
    line = stream.readline()
    return line if line else None


def _setup_logging() -> None:
    if LOGGER.handlers:
        return
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.INFO)
    LOGGER.propagate = False


def _write_json_line(stream: TextIO, payload: Dict[str, Any]) -> None:
    stream.write(json.dumps(payload, separators=(",", ":")) + "\n")
    stream.flush()


def _validate_request(payload: Any) -> tuple[Any, Any, Dict[str, Any], Dict[str, Any] | None]:
    if not isinstance(payload, dict):
        return None, None, {}, jsonrpc_error(None, -32600, "Invalid Request")
    if payload.get("jsonrpc") != "2.0":
        return payload.get("id"), None, {}, jsonrpc_error(payload.get("id"), -32600, "Invalid Request")

    request_id = payload.get("id")
    method = payload.get("method")
    params = payload.get("params", {})

    if not isinstance(method, str):
        return request_id, None, {}, jsonrpc_error(request_id, -32600, "Method must be a string")
    if params is None:
        params = {}
    if not isinstance(params, dict):
        return request_id, None, {}, jsonrpc_error(request_id, -32602, "Params must be an object")

    return request_id, method, params, None


def _tool_to_mcp(defn: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": defn.get("name"),
        "description": defn.get("description", ""),
        "inputSchema": defn.get("input_schema", {}),
    }


def _handle_initialize() -> Dict[str, Any]:
    return {
        "protocolVersion": PROTOCOL_VERSION,
        "serverInfo": {"name": "athena-mcp", "version": "0.1.0"},
        "capabilities": {"tools": {}},
    }


def _handle_tools_list() -> Dict[str, Any]:
    return {"tools": [_tool_to_mcp(tool) for tool in list_tools()]}


def _format_content(result: Any) -> list[Dict[str, str]]:
    if isinstance(result, str):
        text = result
    else:
        try:
            text = json.dumps(result)
        except TypeError:
            text = str(result)
    return [{"type": "text", "text": text}]


def _handle_tools_call(request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
    name = params.get("name") or params.get("tool")
    args = params.get("arguments", params.get("args", {}))
    if not isinstance(name, str):
        return jsonrpc_error(request_id, -32602, "Tool name must be provided as a string")
    if not isinstance(args, dict):
        return jsonrpc_error(request_id, -32602, "Tool arguments must be an object")

    result = call_tool(name, args)
    if not isinstance(result, dict):
        return jsonrpc_error(request_id, -32000, "Invalid tool response")

    if not result.get("ok"):
        error_obj = result.get("error") or {}
        message = error_obj.get("message") if isinstance(error_obj, dict) else "Tool error"
        code = error_obj.get("code") if isinstance(error_obj, dict) else "tool_error"
        details = error_obj.get("details") if isinstance(error_obj, dict) else {}
        return jsonrpc_error(request_id, -32000, message or "Tool error", data={"code": code, "details": details})

    payload = result.get("result", {})
    return jsonrpc_result(request_id, {"content": _format_content(payload)})


def serve_stdio(stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> None:
    """
    JSON-RPC 2.0 stdio transport for Claude Desktop MCP.
    """
    _setup_logging()
    for raw in iter(lambda: _read_line(stdin), None):
        raw = raw.strip()
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            _write_json_line(stdout, jsonrpc_error(None, -32700, "Parse error"))
            continue
        request_id, method, params, error = _validate_request(payload)
        if error:
            _write_json_line(stdout, error)
            continue

        # Notifications (no id) are valid but don't require a response
        if request_id is None:
            LOGGER.debug(f"Received notification: {method}")
            continue

        try:
            assert method is not None  # for mypy
            if method == "initialize":
                response = jsonrpc_result(request_id, _handle_initialize())
            elif method == "tools/list":
                response = jsonrpc_result(request_id, _handle_tools_list())
            elif method == "tools/call":
                response = _handle_tools_call(request_id, params)
            else:
                response = jsonrpc_error(request_id, -32601, "Method not found")
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.exception("Unhandled error processing request")
            response = jsonrpc_error(
                request_id,
                -32603,
                "Internal error",
                data={"exception": str(exc), "traceback": traceback.format_exc()},
            )

        _write_json_line(stdout, response)
