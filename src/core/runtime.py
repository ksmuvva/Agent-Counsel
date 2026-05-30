"""Shared runtime context.

Holds the process-wide LLM client and cost tracker so that all agents share a
single budget and connection without threading them through every constructor.
"""
from typing import Optional

from .cost_tracker import CostTracker
from .llm_client import LLMClient


class Runtime:
    _instance: Optional["Runtime"] = None

    def __init__(self, client: Optional[LLMClient] = None, cost_tracker: Optional[CostTracker] = None):
        self.client = client or LLMClient()
        self.cost_tracker = cost_tracker or CostTracker()

    @classmethod
    def get(cls) -> "Runtime":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def configure(cls, client: Optional[LLMClient] = None, cost_tracker: Optional[CostTracker] = None) -> "Runtime":
        """(Re)initialise the shared runtime, e.g. with a specific budget."""
        cls._instance = cls(client=client, cost_tracker=cost_tracker)
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        cls._instance = None
