"""Central registry of callable tools.

Stores :class:`tools.base.Tool` instances keyed by ``tool.name`` and exposes
helpers for invoking them or handing their specs to the Claude tool-use API.
"""
from __future__ import annotations

from typing import Any, Dict, List


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, Any] = {}

    # ---- registration --------------------------------------------------
    def register_tool(self, tool: Any) -> None:
        """Register a :class:`~tools.base.Tool` instance under ``tool.name``."""
        name = getattr(tool, "name", None)
        if not name:
            raise ValueError("Tool instance must define a non-empty 'name'.")
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
        """Return the registered tools as Anthropic tool specs."""
        specs: List[Dict[str, Any]] = []
        for tool in self._tools.values():
            as_spec = getattr(tool, "as_anthropic_tool", None)
            if callable(as_spec):
                specs.append(as_spec())
        return specs
