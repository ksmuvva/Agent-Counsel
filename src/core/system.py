"""High-level assembly of the Multi-Agent Council System."""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from .cost_tracker import CostTracker
from .llm_client import LLMClient
from .pipeline import PhaseExecutionPipeline, PipelineResult
from .runtime import Runtime


class CouncilSystem:
    """Wires the runtime, agents and pipeline into one runnable system."""

    def __init__(
        self,
        budget: float = 20.0,
        enforce_budget: bool = False,
        log: Optional[Callable[[str], None]] = None,
        *,
        backend: Optional[str] = None,
        glm_api_key: Optional[str] = None,
        glm_base_url: Optional[str] = None,
    ):
        from agents import (
            DomainCouncilChair,
            EthicsSafetyAdvisor,
            Orchestrator,
            QualityArbiter,
        )
        from agents.sme_personas import SMEPersonaManager

        cost_tracker = CostTracker(budget=budget, enforce=enforce_budget)
        client = LLMClient(
            backend=backend,
            glm_api_key=glm_api_key,
            glm_base_url=glm_base_url,
        )
        Runtime.configure(client=client, cost_tracker=cost_tracker)

        self.orchestrator = Orchestrator()
        self.council: List[Any] = [
            DomainCouncilChair(),
            QualityArbiter(),
            EthicsSafetyAdvisor(),
        ]
        self.sme_manager = SMEPersonaManager()
        self.pipeline = PhaseExecutionPipeline(
            orchestrator=self.orchestrator,
            council=self.council,
            sme_manager=self.sme_manager,
            log=log,
        )

    @property
    def online(self) -> bool:
        return Runtime.get().client.online

    @property
    def cost_tracker(self) -> CostTracker:
        return Runtime.get().cost_tracker

    def run(self, task: str) -> PipelineResult:
        return self.pipeline.run(task)

    def cost_summary(self) -> Dict[str, Any]:
        return self.cost_tracker.summary()
