# ATHENA MCP - Refactor Plan: Tool Organization Architecture

**Goal:** Scale from 40 to 1000+ tools with proper organization, discovery, and filtering.

**Timeline:** 4 phases, ~3 hours total execution (using Haiku for heavy lifting)

---

## Phase 1: ToolDefinition v2 + Naming Convention (1h)

### 1.1 Extend ToolDefinition class

**File:** `src/athena_mcp/tools/types.py`

```python
from dataclasses import dataclass, field
from typing import Callable, List

@dataclass
class ToolDefinition:
    name: str
    description: str
    input_schema: JSONDict
    impl: Callable[[JSONDict], JSONDict]

    # NEW: Metadata for organization
    category: str = "general"              # primitives, mesh, object, scene, selection, mode, diag, dev
    tags: List[str] = field(default_factory=list)
    safety_level: str = "safe-first"       # "safe-first" | "view3d-required"
    requires_edit_mode: bool = False

    def to_wire(self) -> JSONDict:
        """Convert to MCP wire format with metadata."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
            # Optional metadata for discovery
            "category": self.category,
            "tags": self.tags,
            "safetyLevel": self.safety_level,
        }
```

### 1.2 Rename ALL tools to follow convention

**Convention:** `blender-<category>-<operation>[-variant]` OR `dev-<operation>` (standalone)

**Mapping table:**

| Old Name | New Name | Category | Tags |
|----------|----------|----------|------|
| `add-cube` | `blender-primitive-cube` | primitives | create, mesh |
| `add-cylinder` | `blender-primitive-cylinder` | primitives | create, mesh |
| `add-sphere` | `blender-primitive-sphere` | primitives | create, mesh |
| `list-objects` | `blender-scene-list-objects` | scene | query |
| `move-object` | `blender-object-move` | object | transform |
| `capabilities` | `blender-diag-capabilities` | diag | info |
| `validate-tool` | `blender-diag-validate-tool` | diag | info |
| `select-all` | `blender-select-all` | selection | select |
| `select-none` | `blender-select-none` | selection | select |
| `select-invert` | `blender-select-invert` | selection | select |
| `set-mode` | `blender-mode-set` | mode | context |
| `set-selection-mode` | `blender-mode-selection-set` | mode | context |
| `submit-tool-spec` | `dev-submit-tool-spec` | dev | standalone |
| `exec-python` | `blender-dev-exec-python` | dev | diagnostic |
| `scene-snapshot` | `blender-diag-scene-snapshot` | diag | safe-first |
| `object-snapshot` | `blender-diag-object-snapshot` | diag | safe-first |
| `mesh-bevel` | `blender-mesh-bevel` | mesh | edit, geometry |
| `mesh-bisect-plane` | `blender-mesh-bisect-plane` | mesh | edit, geometry |
| `mesh-delete` | `blender-mesh-delete` | mesh | edit |
| `mesh-delete-by-index` | `blender-mesh-delete-by-index` | mesh | edit |
| `mesh-duplicate-selection` | `blender-mesh-duplicate-selection` | mesh | edit |
| `mesh-extrude` | `blender-mesh-extrude` | mesh | edit, geometry |
| `mesh-extrude-selection` | `blender-mesh-extrude-selection` | mesh | edit, geometry |
| `mesh-inset` | `blender-mesh-inset` | mesh | edit, geometry |
| `mesh-inset-selection` | `blender-mesh-inset-selection` | mesh | edit, geometry |
| `mesh-loop-cut` | `blender-mesh-loop-cut` | mesh | edit, topology |
| `mesh-merge` | `blender-mesh-merge` | mesh | edit |
| `mesh-scale-selection` | `blender-mesh-scale-selection` | mesh | transform |
| `mesh-select-boundary` | `blender-mesh-select-boundary` | mesh | select |
| `mesh-select-by-index` | `blender-mesh-select-by-index` | mesh | select |
| `mesh-select-by-normal` | `blender-mesh-select-by-normal` | mesh | select |
| `mesh-select-less` | `blender-mesh-select-less` | mesh | select |
| `mesh-select-linked` | `blender-mesh-select-linked` | mesh | select |
| `mesh-select-loop` | `blender-mesh-select-loop` | mesh | select, topology |
| `mesh-select-more` | `blender-mesh-select-more` | mesh | select |
| `mesh-select-non-manifold` | `blender-mesh-select-non-manifold` | mesh | select |
| `mesh-select-ring` | `blender-mesh-select-ring` | mesh | select, topology |
| `mesh-set-selection` | `blender-mesh-set-selection` | mesh | select |
| `mesh-subdivide` | `blender-mesh-subdivide` | mesh | edit, topology |
| `mesh-translate-selection` | `blender-mesh-translate-selection` | mesh | transform |

### 1.3 Update all ToolDefinitions in registry.py

Example:
```python
ToolDefinition(
    name="blender-primitive-cube",
    description="Add a cube mesh primitive with customizable size and location.",
    input_schema=primitives.ADD_CUBE_SCHEMA,
    impl=_tool_blender_add_cube,
    category="primitives",
    tags=["create", "mesh"],
    safety_level="safe-first",
),
```

---

## Phase 2: ToolBank with Indices (30min)

### 2.1 Create ToolBank class

**File:** `src/athena_mcp/tools/tool_bank.py` (NEW)

```python
from typing import Dict, List, Set
from .types import ToolDefinition, JSONDict

class ToolBank:
    """Indexed registry for fast tool lookup and filtering."""

    def __init__(self, tools: List[ToolDefinition]):
        self._tools = tools
        self._by_name: Dict[str, ToolDefinition] = {}
        self._by_category: Dict[str, List[ToolDefinition]] = {}
        self._by_tag: Dict[str, List[ToolDefinition]] = {}
        self._by_safety: Dict[str, List[ToolDefinition]] = {}
        self._build_indices()

    def _build_indices(self) -> None:
        """Build all lookup indices."""
        for tool in self._tools:
            # Name index
            self._by_name[tool.name] = tool

            # Category index
            if tool.category not in self._by_category:
                self._by_category[tool.category] = []
            self._by_category[tool.category].append(tool)

            # Tags index
            for tag in tool.tags:
                if tag not in self._by_tag:
                    self._by_tag[tag] = []
                self._by_tag[tag].append(tool)

            # Safety level index
            if tool.safety_level not in self._by_safety:
                self._by_safety[tool.safety_level] = []
            self._by_safety[tool.safety_level].append(tool)

    def get_tool(self, name: str) -> ToolDefinition | None:
        """Get tool by name (O(1))."""
        return self._by_name.get(name)

    def list_all(self) -> List[ToolDefinition]:
        """List all tools."""
        return self._tools

    def filter_by_category(self, category: str) -> List[ToolDefinition]:
        """Get all tools in a category (O(1))."""
        return self._by_category.get(category, [])

    def filter_by_tags(self, *tags: str) -> List[ToolDefinition]:
        """Get tools matching any of the provided tags."""
        result_set: Set[ToolDefinition] = set()
        for tag in tags:
            result_set.update(self._by_tag.get(tag, []))
        return list(result_set)

    def filter_by_safety(self, level: str) -> List[ToolDefinition]:
        """Get tools by safety level."""
        return self._by_safety.get(level, [])

    def get_categories(self) -> List[str]:
        """List all available categories."""
        return sorted(self._by_category.keys())

    def get_tags(self) -> List[str]:
        """List all available tags."""
        return sorted(self._by_tag.keys())

    def search(self, query: str) -> List[ToolDefinition]:
        """Full-text search in name and description."""
        query_lower = query.lower()
        results = []

        for tool in self._tools:
            score = 0

            # Exact name match
            if tool.name == query_lower:
                score = 100
            # Name starts with query
            elif tool.name.startswith(query_lower):
                score = 50
            # Name contains query
            elif query_lower in tool.name:
                score = 25
            # Description contains query
            elif query_lower in tool.description.lower():
                score = 10

            if score > 0:
                results.append((tool, score))

        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return [tool for tool, score in results]
```

### 2.2 Integrate ToolBank in registry.py

```python
from .tool_bank import ToolBank

# ... existing TOOLS list ...

# Build tool bank on module load
_TOOL_BANK = ToolBank(TOOLS)

def list_tools() -> List[JSONDict]:
    """List all tools in MCP wire format."""
    return [tool.to_wire() for tool in _TOOL_BANK.list_all()]

def call_tool(name: str, args: JSONDict) -> JSONDict:
    """Call a tool by name."""
    tool = _TOOL_BANK.get_tool(name)
    if not tool:
        return error_response(f"Unknown tool '{name}'", code="unknown_tool")
    # ... rest of implementation ...

# NEW: Discovery functions
def get_categories() -> List[str]:
    return _TOOL_BANK.get_categories()

def get_tags() -> List[str]:
    return _TOOL_BANK.get_tags()

def search_tools(query: str) -> List[JSONDict]:
    return [tool.to_wire() for tool in _TOOL_BANK.search(query)]

def filter_tools(category: str = None, tags: List[str] = None) -> List[JSONDict]:
    if category:
        tools = _TOOL_BANK.filter_by_category(category)
    elif tags:
        tools = _TOOL_BANK.filter_by_tags(*tags)
    else:
        tools = _TOOL_BANK.list_all()
    return [tool.to_wire() for tool in tools]
```

---

## Phase 3: Update Tests (30min)

### 3.1 Update test files

Files to update:
- `tests/test_primitives.py` → update tool names
- `tests/test_mesh_edit.py` → update tool names
- `tests/test_registry.py` → update tool names, add ToolBank tests
- All other test files referencing tool names

### 3.2 Add new ToolBank tests

**File:** `tests/test_tool_bank.py` (NEW)

```python
def test_filter_by_category():
    from athena_mcp.tools import registry

    mesh_tools = registry.filter_tools(category="mesh")
    assert len(mesh_tools) > 0
    assert all("mesh" in t["name"] for t in mesh_tools)

def test_filter_by_tags():
    from athena_mcp.tools import registry

    select_tools = registry.filter_tools(tags=["select"])
    assert len(select_tools) > 0

def test_search_tools():
    from athena_mcp.tools import registry

    results = registry.search_tools("select")
    assert len(results) > 0
    assert "select" in results[0]["name"].lower() or "select" in results[0]["description"].lower()

def test_get_categories():
    from athena_mcp.tools import registry

    categories = registry.get_categories()
    assert "mesh" in categories
    assert "primitives" in categories
    assert "diag" in categories
```

---

## Phase 4: Update Documentation (30min)

### 4.1 Update CLAUDE_CHAT_PROMPT.md

Add section about required metadata:

```markdown
## Tool Submission Format (ATHENA v2)

When submitting tools via `dev-submit-tool-spec`, include these metadata fields:

### Required Metadata
- `category`: One of [primitives, mesh, object, scene, selection, mode, diag, dev, material, animation]
- `priority`: "high" | "medium" | "low"
- `safe_first`: true/false (can run headless without View3D?)
- `tool_name`: Follow naming convention `blender-<category>-<operation>`

### Naming Convention
- **Blender tools:** `blender-<category>-<operation>[-variant]`
  - Examples: `blender-primitive-sphere`, `blender-mesh-select-loop`
- **Standalone tools:** `dev-<operation>`
  - Examples: `dev-submit-tool-spec`

### Example Submission
```json
{
  "category": "primitives",
  "priority": "high",
  "tool_name": "blender-primitive-torus",
  "safe_first": true,
  "tags": ["create", "mesh", "geometry"],
  "blender_version": "5.0.0",
  ...
}
```
```

### 4.2 Update README.md

Add discovery section:

```markdown
## Tool Discovery & Organization

ATHENA MCP organizes tools using:
- **Categories**: primitives, mesh, object, scene, selection, mode, diag, dev
- **Tags**: create, edit, select, transform, query, etc.
- **Safety levels**: safe-first (headless), view3d-required

### Filtering Tools
```python
# By category
mesh_tools = filter_tools(category="mesh")

# By tags
select_tools = filter_tools(tags=["select"])

# Search
results = search_tools("extrude")
```
```

---

## Execution Order

1. ✅ Create `types.py` with ToolDefinition v2
2. ✅ Create `tool_bank.py` with ToolBank class
3. ✅ Update all tool names in registry.py TOOLS list
4. ✅ Add category/tags to all 40 tools
5. ✅ Integrate ToolBank in registry.py
6. ✅ Update all test files
7. ✅ Run pytest to verify (must pass 100%)
8. ✅ Update documentation

---

## Success Criteria

- [ ] All 40 tools renamed following convention
- [ ] All tools have category + tags metadata
- [ ] ToolBank indices working (O(1) lookups)
- [ ] All tests passing (pytest)
- [ ] Tool count still 40 (no tools lost)
- [ ] Discovery functions working (get_categories, search_tools, filter_tools)

---

## Rollback Plan

If anything breaks:
1. Git stash changes
2. Revert to previous commit
3. Debug issue in isolated branch