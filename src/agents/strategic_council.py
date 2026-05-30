from typing import Any, Dict, Optional
from core.claude_agent import ClaudeAgent

class StrategicCouncilAgent(ClaudeAgent):
    """Base class for Strategic Council Agents (Tier 3-4 only)."""
    def __init__(self, name: str, description: str, model: str, system_prompt: Optional[str] = None):
        super().__init__(name, description, model, system_prompt)

class DomainCouncilChair(StrategicCouncilAgent):
    """SME selection & governance."""
    def __init__(self, model: str):
        system_prompt = (
            "You are the Domain Council Chair. Your role is to govern the multi-agent system, "
            "select appropriate SME personas for specific tasks, and ensure overall alignment "
            "with strategic goals."
        )
        super().__init__("Domain Council Chair", "SME selection & governance", model, system_prompt)

class QualityArbiter(StrategicCouncilAgent):
    """Quality standard setting & tiebreaker."""
    def __init__(self, model: str):
        system_prompt = (
            "You are the Quality Arbiter. Your role is to set quality standards for all outputs, "
            "act as a tiebreaker in debates, and ensure that the final verdict meets the highest "
            "quality bars."
        )
        super().__init__("Quality Arbiter", "Quality standard setting & tiebreaker", model, system_prompt)

class EthicsSafetyAdvisor(StrategicCouncilAgent):
    """Bias, PII, compliance review."""
    def __init__(self, model: str):
        system_prompt = (
            "You are the Ethics & Safety Advisor. Your role is to review all agent interactions "
            "and outputs for bias, PII leaks, and compliance with safety standards."
        )
        super().__init__("Ethics & Safety Advisor", "Bias, PII, compliance review", model, system_prompt)
