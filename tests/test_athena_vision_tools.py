import pytest

from athena_mcp import tools
from athena_mcp.tools import registry


ATHENA_VISION_TOOLS = [
    "athena-blender-scene-query-complete",
    "athena-blender-spatial-analyze",
    "athena-blender-topology-validate-complete",
    "athena-blender-measure-batch",
    "athena-blender-validate-operation",
]


def test_athena_tools_registered():
    for name in ATHENA_VISION_TOOLS:
        tool = registry._TOOL_BANK.get_tool(name)
        assert tool is not None, f"Tool {name} missing"
        assert isinstance(tool.input_schema, dict)
        assert tool.input_schema.get("type") == "object"


def test_scene_query_complete_strips_none(monkeypatch):
    calls = {}

    def _mock_bridge(tool, args):
        calls["tool"] = tool
        calls["args"] = args
        return {"ok": True, "result": {"echo": args}}

    monkeypatch.setattr(registry, "_bridge_request", _mock_bridge)

    resp = tools.call_tool("athena-blender-scene-query-complete", {"include_topology": None})
    assert resp["ok"] is True
    assert calls["tool"] == "athena-blender-scene-query-complete"
    assert "include_topology" not in calls["args"]


@pytest.mark.parametrize(
    "tool_name,payload",
    [
        ("athena-blender-spatial-analyze", {"object_names": None, "queries": None}),
        ("athena-blender-topology-validate-complete", {"object_name": "Cube", "checks": None}),
        ("athena-blender-measure-batch", {"measurements": [{"type": "DISTANCE", "from": {"object": "A"}, "to": {"object": "B"}}]}),
        ("athena-blender-validate-operation", {"object_name": "Cube", "expectations": {"manifold": True}}),
    ],
)
def test_athena_tools_forward_to_bridge(monkeypatch, tool_name, payload):
    calls = {}

    def _mock_bridge(tool, args):
        calls["tool"] = tool
        calls["args"] = args
        return {"ok": True, "result": {"received": args}}

    monkeypatch.setattr(registry, "_bridge_request", _mock_bridge)

    resp = tools.call_tool(tool_name, payload)
    assert resp["ok"] is True
    assert calls["tool"] == tool_name
    for key, value in payload.items():
        if value is None:
            assert key not in calls["args"]
        else:
            assert calls["args"][key] == value
