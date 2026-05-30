from typing import Dict, List

class ModelRouter:
    def __init__(self, model_mapping: Dict[str, str]):
        self.model_mapping = model_mapping

    def get_model(self, agent_role: str) -> str:
        """Returns the appropriate model for a given agent role."""
        return self.model_mapping.get(agent_role, "default_model") # Assuming a default model if not specified

    def update_model_mapping(self, new_mapping: Dict[str, str]):
        """Updates the model mapping."""
        self.model_mapping.update(new_mapping)
