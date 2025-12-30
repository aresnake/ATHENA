import pytest

from athena_mcp import tools
from athena_mcp.tools import registry


NEW_VISION_TOOLS = [
    "athena-viewport-diff-comparison",
    "athena-viewport-annotate-markup",
    "athena-validate-operation-visual",
    "athena-viewport-selection-isolate-capture",
    "athena-viewport-measurement-overlay",
    "athena-viewport-compare-matrix",
    "athena-viewport-geometry-heatmap",
    "athena-viewport-context-aware-capture",
    "athena-viewport-xray-section-view",
]


def test_new_vision_tools_registered():
    for name in NEW_VISION_TOOLS:
        tool = registry._TOOL_BANK.get_tool(name)
        assert tool is not None, f"Tool {name} missing"
        assert isinstance(tool.input_schema, dict)


@pytest.mark.parametrize(
    "tool_name,payload",
    [
        ("athena-viewport-diff-comparison", {"before_snapshot": {}, "before_screenshot": "path", "output_path": "/tmp", "highlight_color": None}),
        ("athena-viewport-annotate-markup", {"object_name": "Cube", "output_path": "/tmp", "screenshot_base": None}),
        ("athena-validate-operation-visual", {"operation": {"tool_name": "noop"}, "capture_config": {"views": ["FRONT"]}, "output_path": "/tmp", "generate_report": None}),
    ],
)
def test_new_vision_tools_clean_none(monkeypatch, tool_name, payload):
    captured = {}

    def _mock_bridge(tool, args):
        captured["tool"] = tool
        captured["args"] = args
        return {"ok": True, "result": {"echo": args}}

    monkeypatch.setattr(registry, "_bridge_request", _mock_bridge)

    resp = tools.call_tool(tool_name, payload)
    assert resp["ok"] is True
    assert captured["tool"] == tool_name
    assert all(v is not None for v in captured["args"].values())
