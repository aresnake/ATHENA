from athena_mcp.tools import registry


def test_select_loop_schema_defaults():
    tools = {t.name: t for t in registry.TOOLS}
    schema = tools["blender-mesh-select-loop"].input_schema
    props = schema.get("properties", {})
    assert props["extend"].get("default") is False


def test_bevel_schema_defaults():
    tools = {t.name: t for t in registry.TOOLS}
    schema = tools["blender-mesh-bevel"].input_schema
    props = schema.get("properties", {})
    assert props["offset"].get("default") == 0.02
    assert props["segments"].get("default") == 1
    assert props["profile"].get("default") == 0.5


def test_safe_bisect_defaults():
    tools = {t.name: t for t in registry.TOOLS}
    schema = tools["blender-mesh-bisect-plane"].input_schema
    props = schema.get("properties", {})
    assert props["clear_inner"].get("default") is False
    assert props["clear_outer"].get("default") is False
