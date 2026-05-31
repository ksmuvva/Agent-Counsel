"""Cost tracking from real SDK-reported usage.

Costs come straight from the SDK's ``ResultMessage.total_cost_usd`` for each
agent run — they are actual billed amounts, not estimates from a price table.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .sdk_runner import AgentResult


class BudgetExceededError(RuntimeError):
    """Raised when recorded spend passes the configured budget."""


@dataclass
class CostTracker:
    budget: float = 20.0
    enforce: bool = False
    total_cost: float = 0.0
    total_turns: int = 0
    per_agent: Dict[str, float] = field(default_factory=dict)
    tools_used: List[str] = field(default_factory=list)

    def record(self, agent_name: str, result: AgentResult) -> float:
        self.total_cost += result.cost_usd
        self.total_turns += result.num_turns
        self.per_agent[agent_name] = self.per_agent.get(agent_name, 0.0) + result.cost_usd
        self.tools_used.extend(result.tools_used)
        if self.enforce and self.total_cost > self.budget:
            raise BudgetExceededError(
                f"Budget ${self.budget:.2f} exceeded (spent ${self.total_cost:.4f})."
            )
        return result.cost_usd

    @property
    def remaining(self) -> float:
        return max(0.0, self.budget - self.total_cost)

    def summary(self) -> Dict[str, object]:
        return {
            "total_cost_usd": round(self.total_cost, 6),
            "budget": self.budget,
            "remaining": round(self.remaining, 6),
            "total_turns": self.total_turns,
            "tools_invoked": self.tools_used,
            "per_agent": {k: round(v, 6) for k, v in self.per_agent.items()},
        }
