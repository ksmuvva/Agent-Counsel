"""Routes agents to the most appropriate model for their role/tier."""
from typing import Dict

from config.models import HAIKU, OPUS, SONNET


class ModelRouter:
    """Assigns an LLM to each agent, optimising for performance vs. cost."""

    def __init__(self, default_model: str = SONNET):
        self.default_model = default_model
        self.routing_table: Dict[str, str] = {}

    def register(self, agent_name: str, model: str) -> None:
        self.routing_table[agent_name] = model

    def get_model(self, agent_name: str) -> str:
        return self.routing_table.get(agent_name, self.default_model)

    @staticmethod
    def model_for_tier(tier: int) -> str:
        """Pick a model tier from task complexity (1=simple ... 4=complex)."""
        if tier >= 3:
            return OPUS
        if tier == 2:
            return SONNET
        return HAIKU
