"""Test MCP protocol compliance."""
import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict


def _read_json_line(proc: subprocess.Popen[str], timeout: float = 2.0) -> Dict[str, object]:
    """Read a JSON line from subprocess stdout."""
    assert proc.stdout is not None
    result: Dict[str, object] = {}

    def _reader() -> None:
        try:
            result["line"] = proc.stdout.readline()
        except Exception as exc:
            result["exc"] = exc

    reader = threading.Thread(target=_reader, daemon=True)
    reader.start()
    reader.join(timeout)
    if reader.is_alive():
        return {}
    if "exc" in result:
        raise result["exc"]  # type: ignore
    line = result.get("line", "")
    if not line:
        return {}
    return json.loads(line)


def _send_request(proc: subprocess.Popen[str], payload: Dict[str, object]) -> Dict[str, object]:
    """Send JSON-RPC request to subprocess."""
    assert proc.stdin is not None
    proc.stdin.write(json.dumps(payload) + "\n")
    proc.stdin.flush()
    return _read_json_line(proc)


def test_initialize_method():
    """Test that initialize method returns correct structure."""
    cmd = [sys.executable, "-m", "athena_mcp.mcp_core.server", "--stdio"]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        response = _send_request(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        assert response.get("jsonrpc") == "2.0"
        assert response.get("id") == 1
        result = response.get("result", {})
        assert isinstance(result, dict)
        assert "protocolVersion" in result
        assert "serverInfo" in result
        assert "capabilities" in result
        capabilities = result["capabilities"]
        assert "tools" in capabilities
        assert "resources" in capabilities
        assert "prompts" in capabilities
    finally:
        proc.terminate()
        proc.wait(timeout=2)


def test_ping_method():
    """Test that ping method returns empty result."""
    cmd = [sys.executable, "-m", "athena_mcp.mcp_core.server", "--stdio"]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        response = _send_request(proc, {"jsonrpc": "2.0", "id": 1, "method": "ping"})
        assert response.get("jsonrpc") == "2.0"
        assert response.get("id") == 1
        result = response.get("result")
        assert result == {}
    finally:
        proc.terminate()
        proc.wait(timeout=2)


def test_tools_list_method():
    """Test that tools/list returns tools array."""
    cmd = [sys.executable, "-m", "athena_mcp.mcp_core.server", "--stdio"]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        response = _send_request(proc, {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
        assert response.get("jsonrpc") == "2.0"
        result = response.get("result", {})
        assert isinstance(result, dict)
        assert "tools" in result
        tools = result["tools"]
        assert isinstance(tools, list)
        assert len(tools) > 0
        # Check first tool has required fields
        first_tool = tools[0]
        assert "name" in first_tool
        assert "inputSchema" in first_tool
    finally:
        proc.terminate()
        proc.wait(timeout=2)


def test_resources_list_method():
    """Test that resources/list returns resources array."""
    cmd = [sys.executable, "-m", "athena_mcp.mcp_core.server", "--stdio"]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        response = _send_request(proc, {"jsonrpc": "2.0", "id": 1, "method": "resources/list", "params": {}})
        assert response.get("jsonrpc") == "2.0"
        result = response.get("result", {})
        assert isinstance(result, dict)
        assert "resources" in result
        assert isinstance(result["resources"], list)
    finally:
        proc.terminate()
        proc.wait(timeout=2)


def test_prompts_list_method():
    """Test that prompts/list returns prompts array."""
    cmd = [sys.executable, "-m", "athena_mcp.mcp_core.server", "--stdio"]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        response = _send_request(proc, {"jsonrpc": "2.0", "id": 1, "method": "prompts/list", "params": {}})
        assert response.get("jsonrpc") == "2.0"
        result = response.get("result", {})
        assert isinstance(result, dict)
        assert "prompts" in result
        assert isinstance(result["prompts"], list)
    finally:
        proc.terminate()
        proc.wait(timeout=2)


def test_notifications_supported():
    """Test that notifications (no id) are accepted without error."""
    cmd = [sys.executable, "-m", "athena_mcp.mcp_core.server", "--stdio"]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        # Send notification (no id)
        assert proc.stdin is not None
        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        proc.stdin.flush()

        # Send regular request to verify server still works
        response = _send_request(proc, {"jsonrpc": "2.0", "id": 1, "method": "ping"})
        assert response.get("id") == 1
    finally:
        proc.terminate()
        proc.wait(timeout=2)
