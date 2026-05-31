"""Dynamic SME persona agents, instantiated on demand."""
from __future__ import annotations

from typing import Dict, List, Optional

from core.base_agent import Agent
from config.agent_config import SME_PERSONAS
from config.models import SONNET
from tools.document_tools import WEB_SEARCH_TOOL_NAME


def make_persona(name: str, domain: str, skills: List[str]) -> Agent:
    return Agent(
        name=name,
        description=f"SME in {domain}",
        model=SONNET,
        system_prompt=(
            f"You are a Subject Matter Expert in {domain} with deep skills in "
            f"{', '.join(skills)}. Provide expert, domain-specific guidance. Use "
            f"web_search if you need current external facts."
        ),
        allowed_tools=[WEB_SEARCH_TOOL_NAME],
    )


class SMEPersonaManager:
    """Creates and caches dynamic SME persona agents."""

    def __init__(self) -> None:
        self._cache: Dict[str, Agent] = {}

    def get_persona(self, name: str) -> Optional[Agent]:
        if name in self._cache:
            return self._cache[name]
        cfg = SME_PERSONAS.get(name)
        if cfg is None:
            return None
        agent = make_persona(name, cfg["domain"], cfg["skills"])
        self._cache[name] = agent
        return agent

    def list_available(self) -> List[str]:
        return list(SME_PERSONAS.keys())
