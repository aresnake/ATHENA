"""Registry validation: detect missing bridge routing for tools."""
from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for imports
if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from athena_mcp.tools import registry
from athena_mcp.blender_bridge import provider_http


def validate_tool_routing() -> tuple[list[str], list[str]]:
    """Validate that all registered tools have bridge routing.

    Returns:
        Tuple of (missing_tools, extra_routes)
        - missing_tools: Tools in registry.py but not in bridge
        - extra_routes: Routes in bridge but not in registry
    """
    # Get all tool names from registry
    registered_tools = {tool['name'] for tool in registry.list_tools()}

    # Get all routed tools from bridge
    bridge_registry = provider_http._build_dynamic_registry()
    routed_tools = set(bridge_registry.keys())

    # Find discrepancies
    missing_in_bridge = registered_tools - routed_tools
    extra_in_bridge = routed_tools - registered_tools

    return sorted(missing_in_bridge), sorted(extra_in_bridge)


def report_validation() -> bool:
    """Print validation report and return True if valid."""
    missing, extra = validate_tool_routing()

    print("=" * 60)
    print("ATHENA MCP - Tool Routing Validation")
    print("=" * 60)

    if not missing and not extra:
        print("✅ ALL TOOLS PROPERLY ROUTED")
        print(f"\nTotal tools registered: {len(registry.list_tools())}")
        print(f"Total routes in bridge: {len(provider_http._build_dynamic_registry())}")
        return True

    success = True

    if missing:
        print(f"\n❌ MISSING BRIDGE ROUTING ({len(missing)} tools):")
        print("These tools are registered but not accessible via HTTP bridge:\n")
        for tool_name in missing[:10]:
            print(f"  - {tool_name}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")
        success = False

    if extra:
        print(f"\n⚠️  EXTRA ROUTES ({len(extra)} routes):")
        print("These routes exist but have no registry entry:\n")
        for route_name in extra[:10]:
            print(f"  - {route_name}")
        if len(extra) > 10:
            print(f"  ... and {len(extra) - 10} more")
        # Extra routes are OK - they're aliases

    return success


if __name__ == "__main__":
    success = report_validation()
    sys.exit(0 if success else 1)
