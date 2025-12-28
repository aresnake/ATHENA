from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List

from ..mcp_core.types import error_response, ok_response

JSONDict = Dict[str, Any]


@dataclass
class ToolDefinition:
    """MCP tool definition with metadata for organization and discovery."""

    name: str
    description: str
    input_schema: JSONDict
    impl: Callable[[JSONDict], JSONDict]

    # Metadata for organization
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    safety_level: str = "safe-first"
    requires_edit_mode: bool = False

    def to_wire(self) -> JSONDict:
        """Convert to MCP wire format with optional metadata."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
            # Optional metadata for discovery (not part of core MCP spec)
            "category": self.category,
            "tags": self.tags,
            "safetyLevel": self.safety_level,
        }
