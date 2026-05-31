"""Shared runtime context.

Holds the process-wide LLM client, cost tracker and tool registry so that all
agents share a single budget, connection and toolset without threading them
through every constructor.

The :class:`LLMClient` is constructed lazily on first access to ``client``,
so importing or wiring the runtime never requires an API key — only the
moment an agent actually wants to call Claude does.
"""
from typing import Optional

from .cost_tracker import CostTracker
from .llm_client import LLMClient
from .tool_registry import ToolRegistry


class Runtime:
    _instance: Optional["Runtime"] = None

    def __init__(
        self,
        client: Optional[LLMClient] = None,
        cost_tracker: Optional[CostTracker] = None,
        tools: Optional[ToolRegistry] = None,
    ):
        self._client = client
        self.cost_tracker = cost_tracker or CostTracker()
        self.tools = tools if tools is not None else self._build_default_registry()

    @property
    def client(self) -> LLMClient:
        if self._client is None:
            self._client = LLMClient()
        return self._client

    @staticmethod
    def _build_default_registry() -> ToolRegistry:
        # Imported lazily — the tools package depends on this module.
        try:
            from tools import default_registry  # type: ignore
        except Exception:
            return ToolRegistry()
        return default_registry()

    @classmethod
    def get(cls) -> "Runtime":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def configure(
        cls,
        client: Optional[LLMClient] = None,
        cost_tracker: Optional[CostTracker] = None,
        tools: Optional[ToolRegistry] = None,
    ) -> "Runtime":
        """(Re)initialise the shared runtime, e.g. with a specific budget."""
        cls._instance = cls(client=client, cost_tracker=cost_tracker, tools=tools)
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        cls._instance = None
