"""Council agents. Each factory returns a real, SDK-backed :class:`Agent`."""
from .strategic_council import (
    domain_council_chair,
    quality_arbiter,
    ethics_safety_advisor,
)
from .operational_agents import (
    orchestrator,
    task_analyst,
    planner,
    clarifier,
    researcher,
    executor,
    code_reviewer,
    formatter,
    verifier,
    critic,
    reviewer,
    memory_curator,
)
from .sme_personas import SMEPersonaManager, make_persona

__all__ = [
    "domain_council_chair",
    "quality_arbiter",
    "ethics_safety_advisor",
    "orchestrator",
    "task_analyst",
    "planner",
    "clarifier",
    "researcher",
    "executor",
    "code_reviewer",
    "formatter",
    "verifier",
    "critic",
    "reviewer",
    "memory_curator",
    "SMEPersonaManager",
    "make_persona",
]
