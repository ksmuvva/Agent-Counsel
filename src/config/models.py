"""Model aliases for the council agents.

These are the short aliases understood by the Claude CLI / Agent SDK; the SDK
resolves them to the current concrete model for the authenticated account, so
we never hard-code dated model IDs. Override per-deployment via env vars.
"""
import os

OPUS = os.getenv("COUNCIL_OPUS_MODEL", "opus")
SONNET = os.getenv("COUNCIL_SONNET_MODEL", "sonnet")
HAIKU = os.getenv("COUNCIL_HAIKU_MODEL", "haiku")
