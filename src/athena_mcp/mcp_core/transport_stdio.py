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

# Minimum schema that Claude Desktop/Zod accepts reliably
_DEFAULT_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {},
    "additionalProperties": False,
}


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
        # NOTE: Claude Desktop is picky about id=null in error objects.
        # We still return a JSON-RPC error, but caller may choose to ignore for id=None.
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


def _normalize_input_schema(schema: Any) -> Dict[str, Any]:
    # Accept only dict schemas; otherwise fall back
    if isinstance(schema, dict) and schema:
        # If it's a JSON schema but missing type, it still often fails Zod unions.
        # Make sure we always have a type.
        if "type" not in schema:
            schema = {**schema, "type": "object"}
        if "properties" not in schema:
            schema = {**schema, "properties": {}}
        return schema
    return dict(_DEFAULT_INPUT_SCHEMA)


def _tool_to_mcp(defn: Dict[str, Any]) -> Dict[str, Any]:
    schema = defn.get("input_schema")
    if schema is None:
        schema = defn.get("inputSchema")
    if schema is None:
        schema = {}
    return {
        "name": defn.get("name"),
        "description": defn.get("description", ""),
        "inputSchema": schema,
    }



def _handle_initialize() -> Dict[str, Any]:
    return {
        "protocolVersion": PROTOCOL_VERSION,
        "serverInfo": {"name": "athena-mcp", "version": "0.1.0"},
        "capabilities": {
            "tools": {},
            "resources": {},
            "prompts": {},
        },
    }


def _handle_ping() -> Dict[str, Any]:
    """Handle ping request as per MCP spec."""
    return {}


def _handle_tools_list() -> Dict[str, Any]:
    tools = list_tools()
    # list_tools() should return list[dict]; be defensive
    if not isinstance(tools, list):
        tools = []
    return {"tools": [_tool_to_mcp(t) for t in tools if isinstance(t, dict)]}


def _format_content(result: Any) -> list[Dict[str, str]]:
    if isinstance(result, str):
        text = result
    else:
        try:
            text = json.dumps(result, ensure_ascii=False)
        except TypeError:
            text = str(result)
    return [{"type": "text", "text": text}]


def _tool_call_result(request_id: Any, *, ok: bool, payload: Any, err: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    MCP-friendly: tool errors are returned in result with isError=true, not as JSON-RPC top-level error.
    This avoids Claude Desktop Zod schema rejections.
    """
    if ok:
        return jsonrpc_result(request_id, {"content": _format_content(payload)})

    # Error path
    msg = "Tool error"
    details = {}
    if isinstance(err, dict):
        msg = err.get("message") or msg
        details = err.get("details") if isinstance(err.get("details"), dict) else {"details": err.get("details")}
    # Pack structured info in text so the client always sees it
    return jsonrpc_result(
        request_id,
        {
            "isError": True,
            "content": _format_content({"message": msg, "details": details}),
        },
    )


def _handle_tools_call(request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
    name = params.get("name") or params.get("tool")
    raw_args = params.get("arguments")
    if raw_args is None:
        raw_args = params.get("args")
    if raw_args is None:
        raw_args = params.get("params") or params.get("parameters")
    if raw_args is None:
        raw_args = {}

    if not isinstance(name, str) or not name:
        return _tool_call_result(request_id, ok=False, payload=None, err={"message": "Tool name must be a non-empty string"})
    if not isinstance(raw_args, dict):
        return _tool_call_result(request_id, ok=False, payload=None, err={"message": "Tool arguments must be an object"})

    args = raw_args
    result = call_tool(name, args)
    if not isinstance(result, dict):
        return _tool_call_result(request_id, ok=False, payload=None, err={"message": "Invalid tool response"})

    if not result.get("ok"):
        error_obj = result.get("error") if isinstance(result.get("error"), dict) else {"message": "Tool error"}
        return _tool_call_result(request_id, ok=False, payload=None, err=error_obj)

    payload = result.get("result", {})
    return _tool_call_result(request_id, ok=True, payload=payload)


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
            # Avoid responding with id=null (some Claude Desktop builds reject it).
            # Just ignore garbage lines.
            LOGGER.warning("Parse error on incoming line (ignored)")
            continue

        request_id, method, params, error = _validate_request(payload)
        if error:
            # If id is None, do NOT reply (Claude Desktop can reject id=null).
            if request_id is None:
                LOGGER.warning("Invalid request without id (ignored)")
                continue
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
            elif method == "ping":
                response = jsonrpc_result(request_id, _handle_ping())
            elif method == "tools/list":
                response = jsonrpc_result(request_id, _handle_tools_list())
            elif method == "tools/call":
                response = _handle_tools_call(request_id, params)
            elif method == "resources/list":
                response = jsonrpc_result(request_id, {"resources": []})
            elif method == "prompts/list":
                response = jsonrpc_result(request_id, {"prompts": []})
            else:
                # Prefer MCP-friendly result error rather than JSON-RPC error top-level
                response = jsonrpc_result(
                    request_id,
                    {"isError": True, "content": _format_content({"message": "Method not found", "method": method})},
                )
        except Exception as exc:  # pragma: no cover
            LOGGER.exception("Unhandled error processing request")
            response = jsonrpc_result(
                request_id,
                {
                    "isError": True,
                    "content": _format_content(
                        {"message": "Internal error", "exception": str(exc), "traceback": traceback.format_exc()}
                    ),
                },
            )

        _write_json_line(stdout, response)
