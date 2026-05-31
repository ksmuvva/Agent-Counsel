"""Dynamic SME persona agents, instantiated on demand."""
from typing import Dict, List, Optional

from core.claude_agent import ClaudeAgent
from config.agent_config import SME_PERSONAS
from config.models import SONNET


class SMEPersona(ClaudeAgent):
    """A dynamically created domain expert."""

    def __init__(self, name: str, domain: str, skills: List[str]):
        super().__init__(
            name=name,
            description=f"SME in {domain}",
            model=SONNET,
            system_prompt=(
                f"You are a Subject Matter Expert in {domain} with deep skills "
                f"in {', '.join(skills)}. Provide expert, domain-specific guidance."
            ),
        )
        self.domain = domain
        self.skills = skills


class SMEPersonaManager:
    """Manages dynamic SME persona creation and caching."""

    def __init__(self):
        self.personas: Dict[str, SMEPersona] = {}

    def get_persona(self, name: str) -> Optional[SMEPersona]:
        if name in self.personas:
            return self.personas[name]
        if name in SME_PERSONAS:
            config = SME_PERSONAS[name]
            persona = SMEPersona(name=name, domain=config["domain"], skills=config["skills"])
            self.personas[name] = persona
            return persona
        return None

    def list_available(self) -> List[str]:
        return list(SME_PERSONAS.keys())
