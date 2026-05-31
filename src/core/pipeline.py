"""Phase execution pipeline — real, async, multi-agent orchestration.

Every phase is an actual agent run via the Claude Agent SDK. Agents may call
the in-process tool server during their reasoning. Control signals (tier,
selected personas, pass/fail verdict) are parsed from the agents' own output.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List

from agents.operational_agents import (
    critic,
    executor,
    orchestrator,
    planner,
    reviewer,
    task_analyst,
    verifier,
)
from agents.strategic_council import (
    domain_council_chair,
    ethics_safety_advisor,
    quality_arbiter,
)
from agents.sme_personas import SMEPersonaManager
from core.base_agent import Agent
from core.cost_tracker import CostTracker
from tools.document_tools import build_tool_server


@dataclass
class PipelineResult:
    task: str
    tier: int
    phases: Dict[str, Any] = field(default_factory=dict)
    selected_personas: List[str] = field(default_factory=list)
    passed: bool = False
    final_output: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "task": self.task,
            "tier": self.tier,
            "selected_personas": self.selected_personas,
            "phases": self.phases,
            "passed": self.passed,
            "final_output": self.final_output,
        }


def _parse_tier(text: str) -> int:
    match = re.search(r"TIER:\s*([1-4])", text or "", re.IGNORECASE)
    return int(match.group(1)) if match else 2


def _parse_personas(text: str, available: List[str]) -> List[str]:
    match = re.search(r"SELECTED:\s*(.+)", text or "", re.IGNORECASE)
    if not match:
        return []
    named = match.group(1)
    return [p for p in available if p.lower() in named.lower()]


def _parse_verdict(text: str) -> bool:
    return bool(re.search(r"VERDICT:\s*PASS", text or "", re.IGNORECASE))


class PhaseExecutionPipeline:
    """Structured workflow with Council consultation for complex tasks."""

    def __init__(self, cost_tracker: CostTracker, log=None) -> None:
        self.cost_tracker = cost_tracker
        self.sme_manager = SMEPersonaManager()
        self.tool_server = build_tool_server()
        self._servers = {"council_tools": self.tool_server}
        self._log = log or (lambda msg: None)

    async def _run(self, agent: Agent, task: str, context=None) -> str:
        result = await agent.run(
            task,
            context=context,
            mcp_servers=self._servers,
            cost_tracker=self.cost_tracker,
        )
        if result.tools_used:
            self._log(f"{agent.name} used tools: {', '.join(result.tools_used)}")
        return result.text

    async def run(self, task: str) -> PipelineResult:
        # Phase 0: tier classification (a real agent decision)
        tier_text = await self._run(orchestrator(), task)
        tier = _parse_tier(tier_text)
        self._log(f"Orchestrator classified task as Tier {tier}")
        result = PipelineResult(task=task, tier=tier)

        # Phase 1: Analysis
        analysis = await self._run(task_analyst(), task)
        result.phases["Analysis"] = analysis
        context: Dict[str, Any] = {"Analysis": analysis}

        # Phase 2: Council consultation (Tier 3-4 only)
        if tier >= 3:
            self._log("Consulting Strategic Council")
            chair_text = await self._run(
                domain_council_chair(), task, {"Analysis": analysis}
            )
            personas = _parse_personas(chair_text, self.sme_manager.list_available())
            result.selected_personas = personas
            standards = await self._run(
                quality_arbiter(), f"Define quality standards for this task:\n{task}"
            )
            ethics = await self._run(
                ethics_safety_advisor(),
                f"Review this task for ethics/safety concerns:\n{task}",
            )
            result.phases["Council"] = {
                "selected_personas": personas,
                "standards": standards,
                "ethics_review": ethics,
            }
            context["Quality standards"] = standards

            # Engage the selected SME experts for real
            sme_inputs = {}
            for persona_name in personas:
                persona = self.sme_manager.get_persona(persona_name)
                if persona:
                    sme_inputs[persona_name] = await self._run(persona, task, context)
            if sme_inputs:
                result.phases["SME Input"] = sme_inputs
                context["Expert input"] = "\n\n".join(
                    f"{k}: {v}" for k, v in sme_inputs.items()
                )

        # Phase 3: Planning
        plan = await self._run(planner(), task, context)
        result.phases["Planning"] = plan
        context["Plan"] = plan

        # Phase 4: Execution (may call document tools)
        solution = await self._run(executor(), task, context)
        result.phases["Execution"] = solution

        # Phase 5: Adversarial critique + verification
        critique = await self._run(
            critic(), f"Attack this solution:\n{solution}", context
        )
        verification = await self._run(
            verifier(), f"Verify this solution for factual accuracy:\n{solution}", context
        )
        result.phases["Review"] = {"critique": critique, "verification": verification}

        # Phase 6: Final verdict (reviewer decides PASS/FAIL)
        final = await self._run(
            reviewer(),
            f"Produce the final ship-ready output and verdict.\n\n"
            f"Solution:\n{solution}\n\nCritique:\n{critique}\n\n"
            f"Verification:\n{verification}",
        )
        result.passed = _parse_verdict(final)
        result.phases["Final Verdict"] = final
        result.final_output = final
        return result
