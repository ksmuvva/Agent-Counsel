from typing import Any, Dict, List

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Any] = {}

    def register_tool(self, name: str, tool: Any):
        """Registers a tool with a given name."""
        if name in self._tools:
            raise ValueError(f"Tool with name '{name}' already registered.")
        self._tools[name] = tool

    def get_tool(self, name: str) -> Any:
        """Retrieves a registered tool by name."""
        tool = self._tools.get(name)
        if tool is None:
            raise ValueError(f"Tool with name '{name}' not found.")
        return tool

    def list_tools(self) -> List[str]:
        """Lists the names of all registered tools."""
        return list(self._tools.keys())
