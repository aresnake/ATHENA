from __future__ import annotations

from typing import Dict, List, Set

from .types import JSONDict, ToolDefinition


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
            # Name index (O(1) lookup)
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
        result: List[ToolDefinition] = []
        seen: Set[str] = set()
        for tag in tags:
            for tool in self._by_tag.get(tag, []):
                if tool.name in seen:
                    continue
                seen.add(tool.name)
                result.append(tool)
        return result

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
