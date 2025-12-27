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


def test_duplicate_selection_defaults():
    tools = {t.name: t for t in registry.TOOLS}
    schema = tools["blender-mesh-duplicate-selection"].input_schema
    props = schema.get("properties", {})
    assert props["dx"]["default"] == 0.0
    assert props["dy"]["default"] == 0.0
    assert props["dz"]["default"] == 0.0


def test_scene_snapshot_defaults():
    tools = {t.name: t for t in registry.TOOLS}
    schema = tools["blender-scene-snapshot"].input_schema
    props = schema.get("properties", {})
    assert props["include_mesh_stats"]["default"] is True
    assert props["max_objects"]["default"] == 200
    assert props["max_materials_per_object"]["default"] == 32
    assert props["max_items_per_list"]["default"] == 5000


def test_object_snapshot_defaults():
    tools = {t.name: t for t in registry.TOOLS}
    schema = tools["blender-object-snapshot"].input_schema
    props = schema.get("properties", {})
    assert props["include_materials"]["default"] is True
    assert props["include_modifiers"]["default"] is True
    assert props["max_items_per_list"]["default"] == 5000
