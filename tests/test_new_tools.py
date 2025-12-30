"""Test newly implemented tools."""
from athena_mcp.tools import registry


def test_mesh_query_geometry_exists():
    """Test that mesh_query_geometry tool is registered."""
    tool = registry._TOOL_BANK.get_tool("blender-mesh-query-geometry")
    assert tool is not None
    assert tool.name == "blender-mesh-query-geometry"
    assert "geometry" in tool.description.lower() or "query" in tool.description.lower()


def test_mesh_query_selection_exists():
    """Test that mesh_query_selection tool is registered."""
    tool = registry._TOOL_BANK.get_tool("blender-mesh-query-selection")
    assert tool is not None
    assert tool.name == "blender-mesh-query-selection"


def test_mesh_query_topology_exists():
    """Test that mesh_query_topology tool is registered."""
    tool = registry._TOOL_BANK.get_tool("blender-mesh-query-topology")
    assert tool is not None
    assert tool.name == "blender-mesh-query-topology"


def test_viewport_screenshot_complete_exists():
    """Test that viewport_screenshot_complete tool is registered."""
    tool = registry._TOOL_BANK.get_tool("blender-viewport-screenshot-complete")
    assert tool is not None
    assert tool.name == "blender-viewport-screenshot-complete"


def test_modifier_bevel_exists():
    """Test that modifier_bevel tool is registered."""
    tool = registry._TOOL_BANK.get_tool("blender-modifier-bevel")
    assert tool is not None
    assert tool.name == "blender-modifier-bevel"


def test_mesh_extrude_manifold_exists():
    """Test that mesh_extrude_manifold tool is registered."""
    tool = registry._TOOL_BANK.get_tool("blender-mesh-extrude-manifold")
    assert tool is not None
    assert tool.name == "blender-mesh-extrude-manifold"


def test_material_assign_fixed_exists():
    """Test that material_assign_fixed tool is registered."""
    tool = registry._TOOL_BANK.get_tool("blender-material-assign-fixed")
    assert tool is not None
    assert tool.name == "blender-material-assign-fixed"


def test_all_new_tools_have_schemas():
    """Test that all new tools have proper input schemas."""
    new_tools = [
        "blender-mesh-query-geometry",
        "blender-mesh-query-selection",
        "blender-mesh-query-topology",
        "blender-viewport-screenshot-complete",
        "blender-modifier-bevel",
        "blender-mesh-extrude-manifold",
        "blender-material-assign-fixed",
    ]

    for tool_name in new_tools:
        tool = registry._TOOL_BANK.get_tool(tool_name)
        assert tool is not None, f"Tool {tool_name} not found"
        assert tool.input_schema is not None, f"Tool {tool_name} has no schema"
        assert isinstance(tool.input_schema, dict), f"Tool {tool_name} schema is not a dict"
        assert "type" in tool.input_schema, f"Tool {tool_name} schema missing type"
