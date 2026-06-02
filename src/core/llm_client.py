"""LLM client wrapper.

Supports three backends:
1. Anthropic SDK (Claude models) — when ``ANTHROPIC_API_KEY`` is set.
2. OpenAI-compatible API (GLM-4, etc.) — when ``GLM_API_KEY`` is set.
3. Deterministic offline simulation — when neither key is available.
"""
import os
import hashlib
from dataclasses import dataclass
from typing import Optional

try:  # pragma: no cover - exercised only when the SDK is installed
    from anthropic import Anthropic
    _ANTHROPIC_AVAILABLE = True
except Exception:  # pragma: no cover
    Anthropic = None  # type: ignore
    _ANTHROPIC_AVAILABLE = False

try:  # pragma: no cover
    from openai import OpenAI as _OpenAI
    _OPENAI_AVAILABLE = True
except Exception:  # pragma: no cover
    _OpenAI = None  # type: ignore
    _OPENAI_AVAILABLE = False

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
    """Single entry point for completions — Anthropic, OpenAI-compatible, or offline."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        backend: Optional[str] = None,
        glm_api_key: Optional[str] = None,
        glm_base_url: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self._glm_key = glm_api_key or os.getenv("GLM_API_KEY")
        self._glm_base = glm_base_url or os.getenv(
            "COUNCIL_GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/"
        )
        self._backend = backend or os.getenv("COUNCIL_BACKEND", "auto")

        self._anthropic = None
        self._openai = None

        if self._backend == "offline":
            return

        if self._backend in ("auto", "anthropic") and _ANTHROPIC_AVAILABLE and self.api_key:
            try:
                self._anthropic = Anthropic(api_key=self.api_key)
            except Exception:
                self._anthropic = None

        if self._backend in ("auto", "openai", "glm") and _OPENAI_AVAILABLE and self._glm_key:
            try:
                self._openai = _OpenAI(api_key=self._glm_key, base_url=self._glm_base)
            except Exception:
                self._openai = None

    @property
    def online(self) -> bool:
        """True when real API calls will be made."""
        return self._anthropic is not None or self._openai is not None

    @property
    def backend_name(self) -> str:
        if self._backend in ("openai", "glm") and self._openai:
            return "openai"
        if self._backend == "anthropic" and self._anthropic:
            return "anthropic"
        if self._anthropic:
            return "anthropic"
        if self._openai:
            return "openai"
        return "offline"

    def complete(
        self,
        model: str,
        system: str,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> LLMResponse:
        active = self.backend_name
        if active == "openai":
            return self._complete_openai(model, system, prompt, max_tokens, temperature)
        if active == "anthropic":
            return self._complete_anthropic(model, system, prompt, max_tokens, temperature)
        return self._complete_offline(model, system, prompt)

    @_retry
    def _complete_anthropic(self, model, system, prompt, max_tokens, temperature) -> LLMResponse:
        message = self._anthropic.messages.create(
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

    @_retry
    def _complete_openai(self, model, system, prompt, max_tokens, temperature) -> LLMResponse:
        try:
            resp = self._openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
        except Exception as exc:
            return LLMResponse(
                text=f"[openai error: {exc}]",
                model=model,
                input_tokens=_estimate_tokens(system + prompt),
                output_tokens=0,
                simulated=True,
            )
        choice = resp.choices[0] if resp.choices else None
        text = choice.message.content if choice else ""
        usage = resp.usage
        return LLMResponse(
            text=text or "",
            model=model,
            input_tokens=getattr(usage, "prompt_tokens", _estimate_tokens(system + prompt)),
            output_tokens=getattr(usage, "completion_tokens", _estimate_tokens(text or "")),
            simulated=False,
        )

    def _complete_offline(self, model, system, prompt) -> LLMResponse:
        """Deterministic local stand-in for an LLM completion."""
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
