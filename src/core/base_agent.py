"""Base agent: a real, tool-using ReAct agent backed by the Claude Agent SDK."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from claude_agent_sdk import McpSdkServerConfig

from .cost_tracker import CostTracker
from .sdk_runner import AgentResult, invoke_agent


class Agent:
    """A single council agent.

    Calling :meth:`run` executes a genuine agent loop via the SDK: the model
    reasons, optionally calls the tools it has been granted, observes the
    results, and iterates until it produces a final answer.
    """

    def __init__(
        self,
        name: str,
        description: str,
        model: str,
        system_prompt: str,
        allowed_tools: Optional[List[str]] = None,
        max_turns: int = 8,
    ):
        self.name = name
        self.description = description
        self.model = model
        self.system_prompt = system_prompt
        self.allowed_tools = allowed_tools or []
        self.max_turns = max_turns

    def _build_prompt(self, task: str, context: Optional[Dict[str, Any]]) -> str:
        parts: List[str] = []
        if context:
            for key, value in context.items():
                parts.append(f"## {key}\n{value}")
        parts.append(f"## Task\n{task}")
        return "\n\n".join(parts)

    async def run(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        *,
        mcp_servers: Optional[Dict[str, McpSdkServerConfig]] = None,
        cost_tracker: Optional[CostTracker] = None,
    ) -> AgentResult:
        result = await invoke_agent(
            system_prompt=self.system_prompt,
            prompt=self._build_prompt(task, context),
            model=self.model,
            mcp_servers=mcp_servers,
            allowed_tools=self.allowed_tools,
            max_turns=self.max_turns,
        )
        if cost_tracker is not None:
            cost_tracker.record(self.name, result)
        return result

    def __repr__(self) -> str:
        return f"Agent(name={self.name!r}, model={self.model!r})"
