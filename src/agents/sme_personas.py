from typing import Any, Dict, List, Optional
from core.claude_agent import ClaudeAgent

class SMEPersona(ClaudeAgent):
    """Dynamic SME Persona (On-demand domain expert)."""
    def __init__(self, persona_name: str, domain: str, skills: List[str], model: str):
        self.domain = domain
        self.skills = skills
        system_prompt = (
            f"You are a {persona_name}, an expert in the {domain} domain. "
            f"Your skills include: {', '.join(skills)}."
        )
        super().__init__(persona_name, f"Expert in {domain}", model, system_prompt)

class SMEPersonaManager:
    """Manages on-demand instantiation of SME Personas."""
    def __init__(self, persona_configs: Dict[str, Dict[str, Any]], default_model: str):
        self.persona_configs = persona_configs
        self.default_model = default_model
        self._active_personas: Dict[str, SMEPersona] = {}

    def get_persona(self, persona_name: str, model: Optional[str] = None) -> SMEPersona:
        """Instantiates and returns an SME persona by name."""
        if persona_name in self._active_personas:
            return self._active_personas[persona_name]

        config = self.persona_configs.get(persona_name)
        if not config:
            raise ValueError(f"Persona '{persona_name}' not found in configuration.")

        persona = SMEPersona(
            persona_name=persona_name,
            domain=config["domain"],
            skills=config["skills"],
            model=model or self.default_model
        )
        self._active_personas[persona_name] = persona
        return persona

    def list_available_personas(self) -> List[str]:
        """Lists all available persona names."""
        return list(self.persona_configs.keys())
