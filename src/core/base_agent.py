from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseAgent(ABC):
    def __init__(self, name: str, description: str, model: str):
        self.name = name
        self.description = description
        self.model = model
        self.tools: List[Any] = []

    def add_tool(self, tool: Any):
        self.tools.append(tool)

    @abstractmethod
    def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> Any:
        pass

    def __str__(self):
        return f"Agent(name='{self.name}', model='{self.model}')"

    def __repr__(self):
        return self.__str__()
