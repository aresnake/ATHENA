import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, Tuple


class _StubBridgeHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # pragma: no cover - silence test noise
        return

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler naming
        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length)
        data = json.loads(payload.decode("utf-8"))
        response = {"ok": True, "result": {"tool": data.get("tool"), "args": data.get("args")}}
        body = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _start_stub_bridge() -> Tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _StubBridgeHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _read_json_line(proc: subprocess.Popen[str], timeout: float = 5.0) -> Dict[str, object]:
    assert proc.stdout is not None
    result: Dict[str, object] = {}

    def _reader() -> None:
        try:
            result["line"] = proc.stdout.readline()
        except Exception as exc:  # pragma: no cover - defensive
            result["exc"] = exc

    reader = threading.Thread(target=_reader, daemon=True)
    reader.start()
    reader.join(timeout)
    assert not reader.is_alive(), "Timed out waiting for stdio response"
    if "exc" in result:
        raise result["exc"]  # type: ignore[misc]
    line = result.get("line")
    assert line is not None and line != "", "No response from stdio server"
    return json.loads(line)


def _send_request(proc: subprocess.Popen[str], payload: Dict[str, object]) -> Dict[str, object]:
    assert proc.stdin is not None
    proc.stdin.write(json.dumps(payload) + "\n")
    proc.stdin.flush()
    return _read_json_line(proc)


def test_stdio_jsonrpc_flow(tmp_path):
    bridge_server, bridge_thread = _start_stub_bridge()
    host, port = bridge_server.server_address
    cmd = [
        sys.executable,
        "-m",
        "athena_mcp.mcp_core.server",
        "--stdio",
        "--bridge-host",
        host,
        "--bridge-port",
        str(port),
    ]
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )

    try:
        init_resp = _send_request(
            proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "0.1.0"}}
        )
        assert init_resp["jsonrpc"] == "2.0"
        assert init_resp["id"] == 1
        assert init_resp["result"]["protocolVersion"] == "0.1.0"

        list_resp = _send_request(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        assert list_resp["id"] == 2
        tools = list_resp["result"]["tools"]
        assert isinstance(tools, list)
        assert any(t["name"] == "blender-list-objects" for t in tools)
        assert all("inputSchema" in t for t in tools)

        call_resp = _send_request(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "blender-list-objects", "arguments": {"sample": True}},
            },
        )
        assert call_resp["id"] == 3
        content = call_resp["result"]["content"]
        assert isinstance(content, list)
        first = content[0]
        assert first["type"] == "text"
        tool_echo = json.loads(first["text"])
        assert tool_echo["tool"] == "blender-list-objects"
        assert tool_echo["args"] == {"sample": True}
    finally:
        if proc.stdin:
            proc.stdin.close()
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        bridge_server.shutdown()
        bridge_thread.join(timeout=2)
