from typing import Dict, Any, Optional
from .claude_agent import ClaudeAgent
from .model_router import ModelRouter

class AgentFactory:
    def __init__(self, model_router: ModelRouter):
        self.model_router = model_router

    def create_agent(self, role: str, name: str, description: str, system_prompt: Optional[str] = None) -> ClaudeAgent:
        """Creates an agent based on the specified role and configuration."""
        model = self.model_router.get_model(role)
        return ClaudeAgent(name, description, model, system_prompt)
