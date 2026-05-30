"""Concrete agent that talks to Claude (or the offline simulator)."""
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent
from .runtime import Runtime


class ClaudeAgent(BaseAgent):
    """An agent backed by the Claude API via the shared runtime.

    Each call routes through :class:`~core.llm_client.LLMClient` and records
    token usage against the shared :class:`~core.cost_tracker.CostTracker`.
    """

    def __init__(
        self,
        name: str,
        description: str,
        model: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ):
        super().__init__(name, description, model)
        self.system_prompt = system_prompt or f"You are {name}. {description}"
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.last_simulated: Optional[bool] = None

    def _build_prompt(self, task: str, context: Optional[Dict[str, Any]]) -> str:
        parts: List[str] = []
        if context:
            for key, value in context.items():
                parts.append(f"## {key}\n{value}")
        parts.append(f"## Task\n{task}")
        if self.tools:
            tool_names = ", ".join(getattr(t, "name", str(t)) for t in self.tools)
            parts.append(f"## Available tools\n{tool_names}")
        return "\n\n".join(parts)

    def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        runtime = Runtime.get()
        prompt = self._build_prompt(task, context)
        response = runtime.client.complete(
            model=self.model,
            system=self.system_prompt,
            prompt=prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        runtime.cost_tracker.record_usage(
            self.name, self.model, response.input_tokens, response.output_tokens
        )
        self.last_simulated = response.simulated
        return response.text
