"""LLM client wrapper.

Real-only: wraps the Anthropic SDK and fails fast if it can't reach a real
Claude. No offline simulator, no placeholder responses.

``complete()`` supports both a single-prompt convenience form and a full
multi-turn ``messages=`` form, and accepts ``tools=`` to enable Anthropic
tool-use. The :class:`LLMResponse` carries the ``stop_reason``, any
``tool_uses`` extracted from the response, and the raw content blocks so
callers can drive a tool-use loop (see :class:`core.claude_agent.ClaudeAgent`).
"""
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

try:
    from anthropic import Anthropic
    _SDK_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised when the SDK is missing
    Anthropic = None  # type: ignore
    _SDK_AVAILABLE = False

try:
    from tenacity import retry, stop_after_attempt, wait_exponential

    _retry = retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
except ImportError:  # pragma: no cover - tenacity not installed

    def _retry(func):
        return func


class LLMUnavailableError(RuntimeError):
    """Raised when the Anthropic SDK or API key is missing."""


@dataclass
class LLMResponse:
    """Normalised response returned by :class:`LLMClient.complete`."""

    text: str
    model: str
    input_tokens: int
    output_tokens: int
    stop_reason: str = ""
    tool_uses: List[Dict[str, Any]] = field(default_factory=list)
    raw_content: List[Any] = field(default_factory=list)


def _estimate_tokens(text: str) -> int:
    """Rough token estimate (~1.3 tokens per whitespace word).

    Used as a fallback only when the API response omits usage data — Anthropic
    normally returns exact counts.
    """
    if not text:
        return 0
    return max(1, int(len(text.split()) * 1.3))


class LLMClient:
    """Real Claude client. Raises if the SDK or ``ANTHROPIC_API_KEY`` is missing."""

    def __init__(self, api_key: Optional[str] = None):
        if not _SDK_AVAILABLE:
            raise LLMUnavailableError(
                "The 'anthropic' package is not installed. Run "
                "`pip install anthropic` to enable real Claude calls."
            )
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise LLMUnavailableError(
                "ANTHROPIC_API_KEY is not set. Export it before running the "
                "system (or pass api_key= when constructing LLMClient)."
            )
        self._client = Anthropic(api_key=self.api_key)

    @_retry
    def complete(
        self,
        model: str,
        system: str,
        prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        messages: Optional[List[Dict[str, Any]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        """Run one Claude completion.

        Provide either ``prompt`` (single user turn) or ``messages``
        (full multi-turn history). Pass ``tools=registry.anthropic_tool_specs()``
        to enable tool-use.
        """
        if messages is None:
            if prompt is None:
                raise ValueError("complete() requires either 'prompt' or 'messages'.")
            messages = [{"role": "user", "content": prompt}]

        kwargs: Dict[str, Any] = {
            "model": model,
            "system": system,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        message = self._client.messages.create(**kwargs)

        raw_content: List[Any] = list(message.content)
        text = "".join(
            block.text for block in raw_content if getattr(block, "type", None) == "text"
        )
        tool_uses = [
            {
                "id": block.id,
                "name": block.name,
                "input": block.input,
            }
            for block in raw_content
            if getattr(block, "type", None) == "tool_use"
        ]

        usage = getattr(message, "usage", None)
        prompt_chars = system + (prompt or "")
        return LLMResponse(
            text=text,
            model=model,
            input_tokens=getattr(usage, "input_tokens", _estimate_tokens(prompt_chars)),
            output_tokens=getattr(usage, "output_tokens", _estimate_tokens(text)),
            stop_reason=getattr(message, "stop_reason", "") or "",
            tool_uses=tool_uses,
            raw_content=raw_content,
        )
