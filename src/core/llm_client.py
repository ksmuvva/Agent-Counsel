"""LLM client wrapper.

Wraps the Anthropic SDK when an API key is available and the package is
installed. Otherwise it degrades gracefully to a deterministic offline
simulation so the full pipeline remains runnable (and testable) without
credentials or network access.
"""
import os
import hashlib
from dataclasses import dataclass
from typing import Optional

try:  # pragma: no cover - exercised only when the SDK is installed
    from anthropic import Anthropic
    _SDK_AVAILABLE = True
except Exception:  # pragma: no cover
    Anthropic = None  # type: ignore
    _SDK_AVAILABLE = False

try:  # optional retry support
    from tenacity import retry, stop_after_attempt, wait_exponential

    _retry = retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
except Exception:  # pragma: no cover - tenacity not installed

    def _retry(func):
        return func


@dataclass
class LLMResponse:
    """Normalised response returned by :class:`LLMClient.complete`."""

    text: str
    model: str
    input_tokens: int
    output_tokens: int
    simulated: bool


def _estimate_tokens(text: str) -> int:
    """Rough token estimate (~1.3 tokens per whitespace word)."""
    if not text:
        return 0
    return max(1, int(len(text.split()) * 1.3))


class LLMClient:
    """Single entry point for completions, online or offline."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self._client = None
        if _SDK_AVAILABLE and self.api_key:
            try:
                self._client = Anthropic(api_key=self.api_key)
            except Exception:
                self._client = None

    @property
    def online(self) -> bool:
        """True when real API calls will be made."""
        return self._client is not None

    def complete(
        self,
        model: str,
        system: str,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> LLMResponse:
        if self.online:
            return self._complete_online(model, system, prompt, max_tokens, temperature)
        return self._complete_offline(model, system, prompt)

    @_retry
    def _complete_online(self, model, system, prompt, max_tokens, temperature) -> LLMResponse:
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
            simulated=False,
        )

    def _complete_offline(self, model, system, prompt) -> LLMResponse:
        """Deterministic local stand-in for an LLM completion.

        The output is reproducible for a given (system, prompt) pair so tests
        and demos behave consistently. It is clearly labelled as simulated.
        """
        digest = hashlib.sha256((system + "\x00" + prompt).encode()).hexdigest()[:8]
        role = system.strip().splitlines()[0] if system.strip() else "Agent"
        snippet = prompt.strip().replace("\n", " ")
        if len(snippet) > 240:
            snippet = snippet[:237] + "..."
        text = (
            f"[simulated:{digest}] {role}\n"
            f"Addressing: {snippet}\n"
            f"Conclusion: produced a structured response consistent with the "
            f"agent's role using model '{model}'."
        )
        return LLMResponse(
            text=text,
            model=model,
            input_tokens=_estimate_tokens(system + prompt),
            output_tokens=_estimate_tokens(text),
            simulated=True,
        )
