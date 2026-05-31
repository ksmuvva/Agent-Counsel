"""Cost tracking and budget enforcement based on real token usage."""
from dataclasses import dataclass, field
from typing import Dict, List

from config.models import price_for


class BudgetExceededError(RuntimeError):
    """Raised when a recorded call would push spend past the budget."""


@dataclass
class UsageRecord:
    agent: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float


@dataclass
class CostTracker:
    """Monitors API usage and enforces a spend budget.

    Costs are computed from token counts and per-model pricing, so the figures
    reflect real usage when running against the live API.
    """

    budget: float = 10.0
    enforce: bool = False
    total_cost: float = 0.0
    records: List[UsageRecord] = field(default_factory=list)
    per_agent: Dict[str, float] = field(default_factory=dict)

    def record_usage(
        self, agent_name: str, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        price = price_for(model)
        cost = (input_tokens / 1_000_000) * price["input"] + (
            output_tokens / 1_000_000
        ) * price["output"]

        if self.enforce and self.total_cost + cost > self.budget:
            raise BudgetExceededError(
                f"Budget ${self.budget:.2f} would be exceeded "
                f"(current ${self.total_cost:.4f} + ${cost:.4f})."
            )

        self.total_cost += cost
        self.per_agent[agent_name] = self.per_agent.get(agent_name, 0.0) + cost
        self.records.append(
            UsageRecord(agent_name, model, input_tokens, output_tokens, cost)
        )
        return cost

    @property
    def remaining(self) -> float:
        return max(0.0, self.budget - self.total_cost)

    def reset(self) -> None:
        self.total_cost = 0.0
        self.records.clear()
        self.per_agent.clear()

    def summary(self) -> Dict[str, object]:
        return {
            "total_cost": round(self.total_cost, 6),
            "budget": self.budget,
            "remaining": round(self.remaining, 6),
            "calls": len(self.records),
            "per_agent": {k: round(v, 6) for k, v in self.per_agent.items()},
        }
