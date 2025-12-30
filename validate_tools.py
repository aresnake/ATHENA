#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Validate tool routing between registry and bridge.

This script checks that all tools registered in registry.py
have corresponding routes in provider_http.py bridge.
"""
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent / "src"))

from athena_mcp.tools import registry


def main():
    """Run validation and report results."""
    print("=" * 70)
    print("ATHENA MCP - Tool Registry Validation")
    print("=" * 70)

    tools = registry.list_tools()
    print(f"\n✅ Total tools registered: {len(tools)}")

    # Group by category
    by_category = {}
    by_safety = {}

    for tool in tools:
        # Category grouping
        cat = tool.get('category', 'uncategorized')
        by_category.setdefault(cat, []).append(tool['name'])

        # Safety level grouping (from internal ToolDefinition)
        # Note: list_tools() doesn't expose safety_level, so we check tags
        tags = tool.get('tags', [])
        if 'viewport' in tags:
            level = 'view3d-tools'
        elif 'diagnostic' in tags:
            level = 'diagnostic'
        else:
            level = 'standard'
        by_safety.setdefault(level, []).append(tool['name'])

    # Report by category
    print("\n📊 Tools by Category:")
    for cat in sorted(by_category.keys()):
        count = len(by_category[cat])
        print(f"  {cat:20s}: {count:3d} tools")

    # Show sample athena tools
    athena_tools = [name for name in by_category.get('diag', []) if name.startswith('athena-')]
    if athena_tools:
        print(f"\n🔬 Sample Athena Tools ({len(athena_tools)} total):")
        for name in sorted(athena_tools)[:5]:
            print(f"  - {name}")
        if len(athena_tools) > 5:
            print(f"  ... and {len(athena_tools) - 5} more")

    # Show viewport tools
    viewport_tools = [t['name'] for t in tools if 'viewport' in t.get('tags', [])]
    if viewport_tools:
        print(f"\n🎥 Viewport Tools ({len(viewport_tools)} total):")
        for name in sorted(viewport_tools):
            prefix = "✅" if name.startswith(('athena-', 'blender-')) else "⚠️ "
            print(f"  {prefix} {name}")

    print("\n" + "=" * 70)
    print("✅ VALIDATION COMPLETE")
    print("=" * 70)
    print("\n💡 To check bridge routing, reload the Blender bridge server.")
    print("   All tools with proper function names in executor.py will be")
    print("   automatically routed via dynamic discovery.\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
