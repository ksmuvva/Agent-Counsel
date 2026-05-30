"""Tier 3-4 strategic council agents: governance, quality, ethics."""
from typing import List

from core.claude_agent import ClaudeAgent
from config.models import OPUS


class StrategicCouncilAgent(ClaudeAgent):
    """Base for Tier 3-4 governance agents."""


class DomainCouncilChair(StrategicCouncilAgent):
    def __init__(self):
        super().__init__(
            name="Domain Council Chair",
            description="SME selection & governance",
            model=OPUS,
            system_prompt=(
                "You are the Domain Council Chair. Given a task, identify the "
                "domains involved and recommend which SME personas should be "
                "engaged. Provide concise governance guidance."
            ),
        )

    def select_personas(self, task: str, available: List[str]) -> List[str]:
        """Heuristically map a task to relevant SME personas.

        When running online the LLM response informs the choice; offline we fall
        back to keyword matching so the selection is still meaningful.
        """
        text = task.lower()
        keywords = {
            "IAM Architect": ["iam", "identity", "access", "sailpoint", "cyberark", "rbac"],
            "Cloud Architect": ["cloud", "azure", "aws", "gcp", "infrastructure"],
            "Security Analyst": ["security", "threat", "owasp", "vulnerab", "compliance"],
            "Data Engineer": ["data", "etl", "pipeline", "sql", "database"],
            "AI/ML Engineer": ["ai", "ml", "machine learning", "rag", "genai", "model", "agent"],
            "Test Engineer": ["test", "qa", "uat", "sit"],
            "Business Analyst": ["requirement", "process", "bpmn", "stakeholder", "gap"],
            "Technical Writer": ["document", "report", "tender", "write", "docs"],
            "DevOps Engineer": ["devops", "ci/cd", "docker", "kubernetes", "terraform", "deploy"],
            "Frontend Developer": ["ui", "frontend", "dashboard", "streamlit", "react"],
        }
        selected = [
            name
            for name, words in keywords.items()
            if name in available and any(w in text for w in words)
        ]
        return selected


class QualityArbiter(StrategicCouncilAgent):
    def __init__(self):
        super().__init__(
            name="Quality Arbiter",
            description="Quality standard setting & tiebreaker",
            model=OPUS,
            system_prompt=(
                "You are the Quality Arbiter. You set quality standards and act "
                "as the decisive tiebreaker in debates, weighing each argument."
            ),
        )


class EthicsSafetyAdvisor(StrategicCouncilAgent):
    def __init__(self):
        super().__init__(
            name="Ethics & Safety Advisor",
            description="Bias, PII, compliance review",
            model=OPUS,
            system_prompt=(
                "You are the Ethics & Safety Advisor. Review content for bias, "
                "PII exposure, and compliance issues, and flag any concerns."
            ),
        )
