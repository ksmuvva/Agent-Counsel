"""LLM client wrapper.

Real-only: wraps the Anthropic SDK and fails fast if it can't reach a real
Claude. No offline simulator, no placeholder responses.
"""
import os
from dataclasses import dataclass
from typing import Optional

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
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> LLMResponse:
        message = self._client.messages.create(
            model=model,
            system=system,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(
            block.text for block in message.content if getattr(block, "type", None) == "text"
        )
        usage = getattr(message, "usage", None)
        return LLMResponse(
            text=text,
            model=model,
            input_tokens=getattr(usage, "input_tokens", _estimate_tokens(system + prompt)),
            output_tokens=getattr(usage, "output_tokens", _estimate_tokens(text)),
        )
