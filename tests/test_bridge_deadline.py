import time

from athena_mcp.blender_bridge import provider_http


def test_execute_tool_skips_when_deadline_expired(monkeypatch):
    ran = {"flag": False}

    def _fake_tool(_args):
        ran["flag"] = True
        return {"ok": True, "result": {"noop": True}}

    monkeypatch.setitem(provider_http._TOOL_REGISTRY, "fake-tool", _fake_tool)
    job_id = "job-deadline"
    deadline = time.monotonic() - 1.0

    try:
        result = provider_http._execute_tool("fake-tool", {}, job_id, deadline)
    finally:
        provider_http._TOOL_REGISTRY.pop("fake-tool", None)

    assert ran["flag"] is False
    assert result["ok"] is False
    assert result["error"]["code"] == "timeout"
    assert result["error"]["job_id"] == job_id
    assert result["error"]["timeout_source"] == "deadline"
