"""Dynamic agent creation driven by configuration."""
from typing import Optional

from .claude_agent import ClaudeAgent
from .model_router import ModelRouter


class AgentFactory:
    """Creates agents with the model assigned by the router."""

    def __init__(self, model_router: Optional[ModelRouter] = None):
        self.model_router = model_router or ModelRouter()

    def create_agent(
        self,
        name: str,
        description: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> ClaudeAgent:
        resolved_model = model or self.model_router.get_model(name)
        return ClaudeAgent(
            name=name,
            description=description,
            model=resolved_model,
            system_prompt=system_prompt,
        )
