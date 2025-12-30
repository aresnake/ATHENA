# ATHENA MCP - Architecture & Organization

This document describes the organization and architecture of the ATHENA MCP server.

## Tool Organization

### ToolDefinition v2

All tools are defined using the `ToolDefinition` dataclass with metadata:

```python
@dataclass
class ToolDefinition:
    name: str                    # Tool name (e.g., "blender-mesh-select-loop")
    description: str             # Human-readable description
    input_schema: JSONDict       # JSON Schema for parameters
    impl: Callable               # Implementation function

    # Metadata for organization
    category: str                # Category (mesh, primitives, etc.)
    tags: List[str]              # Tags for discovery
    safety_level: str            # "safe-first" or "view3d-required"
    requires_edit_mode: bool     # Requires EDIT mode?
```

### ToolBank - Indexed Registry

The ToolBank class provides O(1) lookup and efficient filtering:
- By name: `_TOOL_BANK.get_tool("blender-mesh-select-loop")`
- By category: `_TOOL_BANK.filter_by_category("mesh")`
- By tags: `_TOOL_BANK.filter_by_tags("select", "topology")`
- Full-text search: `_TOOL_BANK.search("extrude")`

### Naming Convention

Format: `<namespace>-<category>-<operation>[-variant]`
Examples:
- `blender-primitive-cube` - Blender primitive tool
- `blender-mesh-select-loop` - Blender mesh selection
- `blender-dev-exec-python` - Developer/diagnostic tool

### Categories

| Category  | Purpose                   | Tool Count |
|-----------|---------------------------|------------|
| primitives| Mesh primitive creation   | 5          |
| mesh      | Mesh editing & selection  | 24         |
| object    | Object-level operations   | 1          |
| scene     | Scene queries             | 1          |
| selection | Selection operations      | 3          |
| mode      | Mode switching            | 2          |
| diag      | Diagnostics & inspection  | 4          |
| dev       | Developer utilities       | 1          |

### Tags

Tags enable cross-category discovery:
- Actions: create, edit, select, transform, query, delete
- Geometry: mesh, geometry, topology
- Context: safe-first, view3d-required, diagnostic

## File Structure

```
src/athena_mcp/tools/
├── types.py              # ToolDefinition dataclass
├── tool_bank.py          # Indexed registry
├── registry.py           # Central tool registry + discovery API
├── primitives.py         # Primitive tool schemas
├── mesh_edit.py          # Mesh editing schemas
└── devtools.py           # Developer tool schemas

tests/
├── test_tool_bank.py     # ToolBank tests
├── test_registry.py      # Registry tests
└── test_*.py             # Tool-specific tests
```

## Scaling to 1000+ Tools

The architecture is designed to scale:
- Lazy loading: Tool definitions can be loaded on-demand
- Indexed lookup: O(1) lookups via ToolBank indices
- Category-based organization: Logical grouping
- Tag-based discovery: Cross-category search
- Full-text search: Find tools by name/description

## Adding New Tools

1. Define schema in appropriate module (e.g., `primitives.py`).
2. Add implementation function in `registry.py`.
3. Add `ToolDefinition` to `TOOLS` list with metadata.
4. Tool automatically indexed by ToolBank on load.

Example:

```python
ToolDefinition(
    name="blender-primitive-torus",
    description="Add a torus mesh primitive.",
    input_schema=primitives.ADD_TORUS_SCHEMA,
    impl=_tool_blender_add_torus,
    category="primitives",
    tags=["create", "mesh", "geometry"],
    safety_level="safe-first",
)
```

The tool is immediately available via:
- Direct call: `registry.call_tool("blender-primitive-torus", args)`
- Category filter: `registry.filter_tools(category="primitives")`
- Tag search: `registry.filter_tools(tags=["create"])`
- Text search: `registry.search_tools("torus")`
