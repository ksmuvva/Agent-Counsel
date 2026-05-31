"""Concrete agent that talks to Claude via the shared runtime.

If the agent has tools attached via :meth:`BaseAgent.add_tool`, ``run()``
drives a real Anthropic tool-use loop: the model can request a tool call,
the agent dispatches it through :class:`core.tool_registry.ToolRegistry`,
the result is fed back, and the conversation continues until the model
stops requesting tools (or the iteration cap is hit).
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent
from .runtime import Runtime

MAX_TOOL_ITERATIONS = 6


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

    def _build_prompt(self, task: str, context: Optional[Dict[str, Any]]) -> str:
        parts: List[str] = []
        if context:
            for key, value in context.items():
                parts.append(f"## {key}\n{value}")
        parts.append(f"## Task\n{task}")
        return "\n\n".join(parts)

    def _tool_specs(self) -> List[Dict[str, Any]]:
        specs: List[Dict[str, Any]] = []
        for tool in self.tools:
            spec_fn = getattr(tool, "as_anthropic_tool", None)
            if callable(spec_fn):
                specs.append(spec_fn())
        return specs

    @staticmethod
    def _format_tool_result(result: Any) -> str:
        if isinstance(result, str):
            return result
        try:
            return json.dumps(result, default=str)
        except TypeError:
            return str(result)

    def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        runtime = Runtime.get()
        prompt = self._build_prompt(task, context)
        messages: List[Dict[str, Any]] = [{"role": "user", "content": prompt}]
        tool_specs = self._tool_specs()

        last_text = ""
        for _ in range(MAX_TOOL_ITERATIONS):
            response = runtime.client.complete(
                model=self.model,
                system=self.system_prompt,
                messages=messages,
                tools=tool_specs or None,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            runtime.cost_tracker.record_usage(
                self.name, self.model, response.input_tokens, response.output_tokens
            )
            last_text = response.text

            if response.stop_reason != "tool_use" or not response.tool_uses:
                return last_text

            # Echo the assistant's tool-use turn into the conversation.
            messages.append({"role": "assistant", "content": response.raw_content})

            # Dispatch each requested tool through the registry and send the
            # results back as a single user turn.
            tool_results: List[Dict[str, Any]] = []
            for call in response.tool_uses:
                try:
                    result = runtime.tools.invoke(call["name"], **(call["input"] or {}))
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": call["id"],
                            "content": self._format_tool_result(result),
                        }
                    )
                except Exception as exc:
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": call["id"],
                            "content": f"Tool error: {exc}",
                            "is_error": True,
                        }
                    )
            messages.append({"role": "user", "content": tool_results})

        return last_text
