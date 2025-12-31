# ATHENA Tool Naming Audit & Fixes

**Date:** 2025-12-31
**Status:** RESOLVED

## Executive Summary

An audit of ATHENA's tool naming conventions revealed **4 critical inconsistencies** between the MCP server and Blender bridge. All inconsistencies have been fixed.

## Root Causes

### 1. Transition from Manual to Auto-Discovery
The Blender bridge was refactored from manual tool registration to automatic discovery. Some tools were missed during the migration:
- `scene_query_complete` was not added to `_ATHENA_TOOLS` set
- This caused it to be registered as `blender-scene-query-complete` instead of `athena-blender-scene-query-complete`

### 2. Inconsistent Naming Patterns
Some tools do not follow the standard naming convention:
- `validate_operation_visual` -> MCP calls `athena-validate-operation-visual` (not `athena-blender-validate-operation-visual`)
- This breaks the pattern: non-viewport athena tools should use the `athena-blender-` prefix

### 3. Dual Exposure Pattern
Some diagnostic tools are exposed under both naming schemes:
- `viewport_diagnostics` -> `blender-viewport-diagnostics` and `athena-blender-viewport-diagnostics`
- The function was not in `_ATHENA_TOOLS`, so the athena variant was not auto-registered

## Inconsistencies Found & Fixed

### Fix #1: `scene_query_complete` Missing from `_ATHENA_TOOLS`

**Problem:**
- MCP calls: `athena-blender-scene-query-complete`
- Bridge registered: `blender-scene-query-complete` (auto-discovered)
- Result: tool not found

**Root Cause:** function not in `_ATHENA_TOOLS` set

**Fix:** Added `scene_query_complete` to `_ATHENA_TOOLS` set in `provider_http.py:74`

**File:** `src/athena_mcp/blender_bridge/provider_http.py`

```python
_ATHENA_TOOLS = {
    'scene_query_complete',  # ADDED
    'spatial_analyze', 'topology_validate_complete', 'measure_batch',
    # ...
}
```

---

### Fix #2: `validate_operation_visual` Naming Pattern Inconsistency

**Problem:**
- MCP calls: `athena-validate-operation-visual`
- Bridge would register: `athena-blender-validate-operation-visual` (by convention)
- Result: naming mismatch

**Root Cause:** MCP uses shortened `athena-validate-*` instead of `athena-blender-validate-*`

**Fix:** Added manual alias in `provider_http.py:141`

**File:** `src/athena_mcp/blender_bridge/provider_http.py`

```python
_MANUAL_ALIASES = {
    # ...
    # Athena tools - special cases that do not follow the standard naming pattern
    "athena-validate-operation-visual": "validate_operation_visual",  # ADDED
}
```

---

### Fix #3: `viewport_diagnostics` Dual Naming Support

**Problem:**
- MCP exposes two tools:
  - `blender-viewport-diagnostics` (present)
  - `athena-blender-viewport-diagnostics` (missing)
- Bridge only registered the first one (auto-discovered)

**Root Cause:** function not in `_ATHENA_TOOLS`, so athena variant was not created

**Fix:** Added manual alias in `provider_http.py:143`

**File:** `src/athena_mcp/blender_bridge/provider_http.py`

```python
_MANUAL_ALIASES = {
    # ...
    "athena-blender-viewport-diagnostics": "viewport_diagnostics",  # ADDED
}
```

---

### Fix #4: Backward Compatibility Alias for `scene_query_complete`

**Problem:**
- Some code may call the old name `blender-scene-query-complete`
- After adding to `_ATHENA_TOOLS`, this name is no longer auto-registered

**Fix:** Added backward compatibility alias in `provider_http.py:142`

**File:** `src/athena_mcp/blender_bridge/provider_http.py`

```python
_MANUAL_ALIASES = {
    # ...
    "blender-scene-query-complete": "scene_query_complete",  # ADDED
}
```

---

## Naming Convention Summary

### Auto-Discovery Rules (in `provider_http.py`)

1. **Athena viewport tools** (in `_ATHENA_TOOLS` and starts with `viewport_`):
   - Function: `viewport_diff_comparison`
   - Registered as: `athena-viewport-diff-comparison`

2. **Athena non-viewport tools** (in `_ATHENA_TOOLS` and does not start with `viewport_`):
   - Function: `spatial_analyze`
   - Registered as: `athena-blender-spatial-analyze`

3. **Standard Blender tools** (not in `_ATHENA_TOOLS`):
   - Function: `add_cube`
   - Registered as: `blender-add-cube`

### Special Cases (Manual Aliases)

Tools that do not follow the standard pattern are added to `_MANUAL_ALIASES`:

```python
_MANUAL_ALIASES = {
    # Legacy names (backward compatibility)
    "blender-add-cube": "add_cube",  # Legacy, now blender-primitive-cube

    # Athena tools with non-standard naming
    "athena-validate-operation-visual": "validate_operation_visual",  # athena-validate instead of athena-blender-validate

    # Dual exposure (both blender- and athena-blender- variants)
    "athena-blender-viewport-diagnostics": "viewport_diagnostics",

    # Backward compatibility for migrated tools
    "blender-scene-query-complete": "scene_query_complete",
}
```

---

## Validation

Created `validate_tool_naming.py` script to detect naming inconsistencies:

```bash
python validate_tool_naming.py
```

### Current Status (After Fixes)

```
[*] Found 142 tools in MCP registry
[*] Found 130 tools in Blender bridge registry
[*] Found 142 MCP tools that call the bridge

[OK] All implemented MCP tools are properly mapped to bridge functions
```

**Note:** 29 tools are defined in MCP specs but not yet implemented in the executor. This is expected for a project in development.

---

## Tools Currently Defined But Not Implemented

These tools have specs in the MCP server but no executor implementation yet:

1. **Primitives:** `blender-primitive-cone`, `blender-primitive-torus`
2. **Mesh operations:** `blender-mesh-decimate`, `blender-mesh-remesh`, `blender-mesh-cleanup-complete`, etc.
3. **Modifiers:** `blender-modifier-array-complete`, `blender-modifier-boolean`, etc.
4. **Advanced features:** `blender-batch-operation`, `blender-curve-from-vertices`, etc.

**Total:** 29 tools pending implementation

---

## Prevention Strategy

### 1. Use Auto-Discovery First
- Add new executor functions as public functions (no leading `_`)
- Add function name to `_ATHENA_TOOLS` if it should have `athena-` prefix
- The registry will automatically discover it

### 2. Manual Aliases Only When Needed
Use `_MANUAL_ALIASES` only for:
- Backward compatibility (legacy names)
- Non-standard naming patterns (e.g., `athena-validate-` instead of `athena-blender-validate-`)
- Dual exposure (both `blender-` and `athena-blender-` variants)

### 3. Run Validation Before Commits
```bash
python validate_tool_naming.py
```
This will catch naming mismatches before they reach production.

### 4. Document Naming Decisions
If a tool uses a non-standard name, add a comment in `_MANUAL_ALIASES` explaining why.

---

## Files Modified

1. `src/athena_mcp/blender_bridge/provider_http.py`
   - Added `scene_query_complete` to `_ATHENA_TOOLS` (line 74)
   - Added 3 manual aliases for special cases (lines 141-143)

2. `validate_tool_naming.py` (NEW)
   - Validation script to detect naming inconsistencies

3. `docs/tool-naming-audit.md` (NEW)
   - This document

---

## Testing Instructions

1. **Restart Blender with HTTP bridge:**
   ```powershell
   & "C:\\Program Files\\Blender Foundation\\Blender 5.0\\blender.exe" `
     --factory-startup `
     --python-use-system-env `
     --python "D:\\ATHENA\\src\\athena_mcp\\blender_bridge\\provider_http.py"
   ```

2. **Start MCP server:**
   ```bash
   python -m athena_mcp.mcp_core.server --http --port 9000
   ```

3. **Test the fixed tools:**
   ```bash
   # Test athena-blender-scene-query-complete
   curl -X POST http://127.0.0.1:9000/tools/call \
     -H "Content-Type: application/json" \
     -d '{"name":"athena-blender-scene-query-complete","args":{"max_objects":10}}'

   # Test athena-validate-operation-visual
   curl -X POST http://127.0.0.1:9000/tools/call \
     -H "Content-Type: application/json" \
     -d '{"name":"athena-validate-operation-visual","args":{}}'

   # Test athena-blender-viewport-diagnostics
   curl -X POST http://127.0.0.1:9000/tools/call \
     -H "Content-Type: application/json" \
     -d '{"name":"athena-blender-viewport-diagnostics","args":{}}'
   ```

---

## Conclusion

All critical naming inconsistencies have been resolved. The tool naming system now follows a clear convention with documented exceptions. A validation script is available to prevent future regressions.

**Next Steps:**
1. Implement the 29 pending tools as needed
2. Run `validate_tool_naming.py` before major releases
3. Consider CI integration for automatic validation
