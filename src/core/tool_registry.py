"""Central registry of callable tools.

Stores :class:`tools.base.Tool` instances keyed by name and exposes helpers
for invoking them or handing their specs to the Claude tool-use API. Legacy
plain-object tools (no schema) are still accepted for backwards compatibility
but are not surfaced to Claude.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, Any] = {}

    # ---- registration --------------------------------------------------
    def register_tool(self, name_or_tool, tool: Optional[Any] = None) -> None:
        """Register a tool.

        Two call styles are supported:
        - ``register_tool(tool_instance)`` — name is read from ``tool.name``.
        - ``register_tool("explicit_name", tool_instance)`` — legacy form.
        """
        if tool is None:
            tool = name_or_tool
            name = getattr(tool, "name", None)
            if not name:
                raise ValueError("Tool instance must define a non-empty 'name'.")
        else:
            name = name_or_tool
        if name in self._tools:
            raise ValueError(f"Tool with name '{name}' already registered.")
        self._tools[name] = tool

    def register_many(self, tools) -> None:
        for t in tools:
            self.register_tool(t)

    # ---- lookup --------------------------------------------------------
    def get_tool(self, name: str) -> Any:
        tool = self._tools.get(name)
        if tool is None:
            raise ValueError(f"Tool with name '{name}' not found.")
        return tool

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())

    # ---- invocation ----------------------------------------------------
    def invoke(self, name: str, **kwargs: Any) -> Any:
        """Run the tool with validated kwargs."""
        tool = self.get_tool(name)
        runner = getattr(tool, "run", None)
        if callable(runner):
            return runner(**kwargs)
        raise TypeError(f"Tool '{name}' is not callable via run(**kwargs).")

    # ---- Claude tool-use integration -----------------------------------
    def anthropic_tool_specs(self) -> List[Dict[str, Any]]:
        """Return the subset of registered tools as Anthropic tool specs."""
        specs: List[Dict[str, Any]] = []
        for tool in self._tools.values():
            as_spec = getattr(tool, "as_anthropic_tool", None)
            if callable(as_spec):
                specs.append(as_spec())
        return specs
