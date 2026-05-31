"""High-level assembly of the Multi-Agent Council System."""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .cost_tracker import CostTracker
from .pipeline import PhaseExecutionPipeline, PipelineResult


class CouncilSystem:
    """Runnable multi-agent council backed by the Claude Agent SDK."""

    def __init__(
        self,
        budget: float = 20.0,
        enforce_budget: bool = False,
        log: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.cost_tracker = CostTracker(budget=budget, enforce=enforce_budget)
        self.pipeline = PhaseExecutionPipeline(self.cost_tracker, log=log)

    async def run(self, task: str) -> PipelineResult:
        return await self.pipeline.run(task)

    def cost_summary(self) -> Dict[str, Any]:
        return self.cost_tracker.summary()
