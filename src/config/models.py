"""Centralised model configuration.

Model IDs are resolved from environment variables so the exact Claude model
strings can be set per-deployment without code changes. The defaults target the
current Claude generation; override them to pin specific dated model IDs.
"""
import os

# Tier aliases -> concrete model IDs (override via env for your account).
OPUS = os.getenv("COUNCIL_OPUS_MODEL", "claude-opus-4-1")
SONNET = os.getenv("COUNCIL_SONNET_MODEL", "claude-sonnet-4-5")
HAIKU = os.getenv("COUNCIL_HAIKU_MODEL", "claude-haiku-4-5")

# OpenAI-compatible model support (e.g. ZhipuAI GLM-4).
GLM_MODEL = os.getenv("COUNCIL_GLM_MODEL", "glm-4")
GLM_BASE_URL = os.getenv("COUNCIL_GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")

# Approximate USD pricing per 1M tokens (input, output). Used by CostTracker.
# Keyed by a substring matched against the model id, longest match wins.
PRICING = {
    "opus": {"input": 15.0, "output": 75.0},
    "sonnet": {"input": 3.0, "output": 15.0},
    "haiku": {"input": 0.80, "output": 4.0},
    "glm-4": {"input": 0.14, "output": 0.14},
}

DEFAULT_PRICING = {"input": 3.0, "output": 15.0}


def price_for(model: str) -> dict:
    """Return the (input, output) per-1M-token pricing for a model id."""
    model_lc = (model or "").lower()
    for key, price in PRICING.items():
        if key in model_lc:
            return price
    return DEFAULT_PRICING
