#!/usr/bin/env python3
"""
Validate tool naming consistency between MCP server and Blender bridge.

This script checks that:
1. All tools exposed by the MCP server have corresponding functions in the bridge
2. The naming conventions are consistent
3. No tools are missing from either side
"""
import sys
from pathlib import Path

# Add ATHENA to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from athena_mcp.tools import registry as mcp_registry
from athena_mcp.blender_bridge.provider_http import _build_dynamic_registry

def main():
    print("=" * 80)
    print("ATHENA Tool Naming Validation")
    print("=" * 80)

    # Get all MCP tools
    mcp_tools = mcp_registry.list_tools()
    print(f"\n[*] Found {len(mcp_tools)} tools in MCP registry\n")

    # Get all bridge tools
    bridge_registry = _build_dynamic_registry()
    print(f"[*] Found {len(bridge_registry)} tools in Blender bridge registry\n")

    # Extract tool names that call the bridge
    mcp_bridge_calls = set()
    for tool in mcp_tools:
        name = tool.get("name", "")
        # Check if this is a bridge tool (not a dev tool)
        if name.startswith("blender-") or name.startswith("athena-"):
            mcp_bridge_calls.add(name)

    print(f"[*] Found {len(mcp_bridge_calls)} MCP tools that call the bridge\n")

    # Check for missing tools
    print("[*] Checking for naming inconsistencies...\n")

    missing_in_bridge = []
    for mcp_tool in sorted(mcp_bridge_calls):
        if mcp_tool not in bridge_registry:
            missing_in_bridge.append(mcp_tool)

    if missing_in_bridge:
        print(f"[X] {len(missing_in_bridge)} tools missing in bridge registry:")
        for tool in missing_in_bridge:
            print(f"   - {tool}")
        print()
    else:
        print("[OK] All MCP tools are registered in the bridge\n")

    # Check for extra tools in bridge that aren't exposed by MCP
    extra_in_bridge = []
    for bridge_tool in sorted(bridge_registry.keys()):
        if bridge_tool.startswith("blender-") or bridge_tool.startswith("athena-"):
            if bridge_tool not in mcp_bridge_calls:
                extra_in_bridge.append(bridge_tool)

    if extra_in_bridge:
        print(f"[INFO] {len(extra_in_bridge)} tools in bridge not exposed by MCP:")
        for tool in extra_in_bridge[:20]:  # Limit output
            print(f"   - {tool}")
        if len(extra_in_bridge) > 20:
            print(f"   ... and {len(extra_in_bridge) - 20} more")
        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    if missing_in_bridge:
        print(f"[X] FAILED: {len(missing_in_bridge)} tools missing in bridge")
        return 1
    else:
        print("[OK] PASSED: All MCP tools are properly mapped to bridge functions")
        return 0

if __name__ == "__main__":
    sys.exit(main())
