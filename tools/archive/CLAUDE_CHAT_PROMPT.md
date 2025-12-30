# CLAUDE CHAT PROMPT - ATHENA MCP

Use this prompt inside Claude Chat to generate and submit MCP tool specs via `dev-submit-tool-spec`. Keep outputs concise, follow the naming conventions, and always include discovery metadata.

## Tool Submission Format (ATHENA v2)

When submitting tools via `dev-submit-tool-spec`, include these metadata fields:

- `tool_name`: `blender-<category>-<operation>` or `dev-<operation>`
- `category`: primitives, mesh, object, scene, selection, mode, diag, dev, material, animation
- `priority`: high/medium/low
- `safe_first`: true/false (can run headless without View3D?)
- `tags`: array of discovery tags

## Tool Submission Format (ATHENA v2) - UPDATED

When submitting tools via `dev-submit-tool-spec`, include these metadata fields:

### Required Metadata
- `category`: One of [primitives, mesh, object, scene, selection, mode, diag, dev, material, animation]
- `priority`: "high" | "medium" | "low"
- `safe_first`: true/false (can run headless without View3D?)
- `tool_name`: Follow naming convention (see below)
- `tags`: Array of relevant tags for discovery

### Naming Convention

**Blender tools:** `blender-<category>-<operation>[-variant]`
- Examples: `blender-primitive-sphere`, `blender-mesh-select-loop`, `blender-material-set-roughness`

**Standalone tools:** `dev-<operation>`
- Examples: `dev-submit-tool-spec`, `dev-exec-python`

### Categories Reference

| Category | Description | Examples |
|----------|-------------|----------|
| primitives | Mesh primitive creation | cube, sphere, cylinder, cone, torus |
| mesh | Mesh editing operations | extrude, inset, bevel, subdivide, select-* |
| object | Object-level operations | move, rotate, scale, duplicate |
| scene | Scene-level queries/operations | list-objects, get-active |
| selection | Selection operations | select-all, select-none, select-invert |
| mode | Mode switching | set-mode, set-selection-mode |
| diag | Diagnostic tools | capabilities, validate-tool, snapshot |
| dev | Developer utilities | exec-python, submit-tool-spec |
| material | Material operations | set-roughness, set-metallic, assign |
| animation | Animation operations | keyframe-insert, armature-create |

### Tags Reference

Common tags for discovery:
- **Actions**: create, edit, select, transform, query, delete
- **Geometry**: mesh, geometry, topology
- **Context**: context, mode, safe-first, view3d-required
- **Diagnostic**: diagnostic, info, testing

### Example Submission (ATHENA v2)

```json
{
  "category": "primitives",
  "priority": "high",
  "tool_name": "blender-primitive-torus",
  "safe_first": true,
  "tags": ["create", "mesh", "geometry"],
  "blender_version": "5.0.0",
  "blender_pseudocode": "bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.25, location=(0,0,0))",
  "api_research": {
    "operator": "bpy.ops.mesh.primitive_torus_add",
    "tested_with_exec_python": true,
    "test_date": "2025-01-XX",
    "blender_version_tested": "5.0.0"
  },
  "validation_tests": {
    "api_tested": true,
    "exec_python_results": {
      "default_test": "✓ Torus created with 576 verts, 576 faces",
      "geometry_verified": "✓ Major/minor radius scaling correct"
    }
  },
  "mcp_spec": {
    "name": "blender:primitive-torus",
    "description": "Add a torus mesh primitive with customizable major/minor radius.",
    "parameters": {
      "type": "object",
      "properties": {
        "name": {"type": "string", "description": "Name for the new torus object"},
        "major_radius": {"type": "number", "default": 1.0, "minimum": 0.001},
        "minor_radius": {"type": "number", "default": 0.25, "minimum": 0.001},
        "location": {
          "type": "array",
          "items": {"type": "number"},
          "minItems": 3,
          "maxItems": 3,
          "default": [0, 0, 0]
        }
      }
    }
  },
  "test_cases": [...],
  "implementation_notes": {...}
}
```
