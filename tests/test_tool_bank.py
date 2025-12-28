from __future__ import annotations


def test_filter_by_category():
    """Test filtering tools by category."""
    from athena_mcp.tools import registry

    mesh_tools = registry.filter_tools(category="mesh")
    assert len(mesh_tools) > 0
    assert all("mesh" in t["name"] for t in mesh_tools)


def test_filter_by_tags():
    """Test filtering tools by tags."""
    from athena_mcp.tools import registry

    select_tools = registry.filter_tools(tags=["select"])
    assert len(select_tools) > 0


def test_search_tools():
    """Test full-text search."""
    from athena_mcp.tools import registry

    results = registry.search_tools("select")
    assert len(results) > 0
    # At least one result should have "select" in name or description
    assert any(
        "select" in r["name"].lower() or "select" in r["description"].lower()
        for r in results
    )


def test_get_categories():
    """Test getting all categories."""
    from athena_mcp.tools import registry

    categories = registry.get_categories()
    assert "mesh" in categories
    assert "primitives" in categories
    assert "diag" in categories


def test_get_tags():
    """Test getting all tags."""
    from athena_mcp.tools import registry

    tags = registry.get_tags()
    assert len(tags) > 0
    assert "select" in tags or "edit" in tags


def test_tool_bank_get_tool():
    """Test direct tool lookup by name."""
    from athena_mcp.tools import registry

    tool = registry._TOOL_BANK.get_tool("blender-mesh-select-loop")
    assert tool is not None
    assert tool.name == "blender-mesh-select-loop"
    assert tool.category == "mesh"


def test_tool_count():
    """Verify we still have 42 tools after refactor."""
    from athena_mcp.tools import registry

    tools = registry.list_tools()
    assert len(tools) == 42
