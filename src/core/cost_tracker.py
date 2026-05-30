from typing import Dict

class CostTracker:
    def __init__(self):
        self.costs: Dict[str, float] = {}
        self.total_cost: float = 0.0

    def record_cost(self, agent_name: str, cost: float):
        """Records the cost incurred by a specific agent."""
        self.costs[agent_name] = self.costs.get(agent_name, 0.0) + cost
        self.total_cost += cost

    def get_agent_cost(self, agent_name: str) -> float:
        """Returns the total cost for a specific agent."""
        return self.costs.get(agent_name, 0.0)

    def get_total_cost(self) -> float:
        """Returns the total cost across all agents."""
        return self.total_cost

    def reset(self):
        """Resets all recorded costs."""
        self.costs = {}
        self.total_cost = 0.0

    def __str__(self):
        return f"Total Cost: ${self.total_cost:.4f}, Agent Costs: {self.costs}"
