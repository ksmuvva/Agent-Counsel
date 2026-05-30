"""Phase execution pipeline and the key collaboration mechanisms."""
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from agents import (
    Critic,
    DomainCouncilChair,
    EthicsSafetyAdvisor,
    Executor,
    Orchestrator,
    Planner,
    QualityArbiter,
    Reviewer,
    TaskAnalyst,
    Verifier,
)
from agents.sme_personas import SMEPersonaManager


@dataclass
class PipelineResult:
    task: str
    tier: int
    phases: Dict[str, Any] = field(default_factory=dict)
    selected_personas: List[str] = field(default_factory=list)
    revised: bool = False
    passed: bool = False
    final_output: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "task": self.task,
            "tier": self.tier,
            "selected_personas": self.selected_personas,
            "phases": self.phases,
            "revised": self.revised,
            "passed": self.passed,
            "final_output": self.final_output,
        }


class PhaseExecutionPipeline:
    """Structured workflow with Council consultation for complex tasks."""

    def __init__(
        self,
        orchestrator: Orchestrator,
        council: List[Any],
        sme_manager: Optional[SMEPersonaManager] = None,
        verdict_matrix: Optional["VerdictMatrix"] = None,
        log: Optional[Callable[[str], None]] = None,
    ):
        self.orchestrator = orchestrator
        self.council = council
        self.sme_manager = sme_manager or SMEPersonaManager()
        self.task_analyst = TaskAnalyst()
        self.planner = Planner()
        self.executor = Executor()
        self.critic = Critic()
        self.verifier = Verifier()
        self.reviewer = Reviewer()
        self.verdict_matrix = verdict_matrix or VerdictMatrix(
            self._find(QualityArbiter), self.reviewer
        )
        self._log = log or (lambda msg: None)

    def _find(self, cls):
        for member in self.council:
            if isinstance(member, cls):
                return member
        return cls()

    def run(self, task: str) -> PipelineResult:
        tier = self.orchestrator.classify_tier(task)
        self._log(f"Classified task as Tier {tier}")
        result = PipelineResult(task=task, tier=tier)

        # Phase 1: Analysis
        analysis = self.task_analyst.run(task)
        result.phases["Analysis"] = analysis

        # Phase 2: Council consultation (Tier 3-4 only)
        context: Dict[str, Any] = {"Analysis": analysis}
        if tier >= 3:
            self._log("Consulting Strategic Council")
            chair = self._find(DomainCouncilChair)
            personas = chair.select_personas(task, self.sme_manager.list_available())
            result.selected_personas = personas
            standards = self._find(QualityArbiter).run(
                f"Define quality standards for this task:\n{task}"
            )
            ethics = self._find(EthicsSafetyAdvisor).run(
                f"Review this task for ethics/safety concerns:\n{task}"
            )
            result.phases["Council"] = {
                "selected_personas": personas,
                "standards": standards,
                "ethics_review": ethics,
            }
            context["Quality standards"] = standards

        # Phase 3: Planning
        plan = self.planner.run(task, context=context)
        result.phases["Planning"] = plan
        context["Plan"] = plan

        # Phase 4: Execution
        solution = self.executor.run(task, context=context)
        result.phases["Execution"] = solution

        # Phase 5: Review & verification
        critique = self.critic.attack(solution, context=context)
        verification = self.verifier.run(
            f"Verify this solution for factual accuracy:\n{solution}"
        )
        result.phases["Review"] = {"critique": critique, "verification": verification}

        # Verdict matrix quality gate (one revision cycle on failure)
        passed = self.verdict_matrix.evaluate(solution, context)
        if not passed:
            self._log("Verdict failed - triggering revision")
            solution = self.executor.run(
                task,
                context={**context, "Critique": critique, "Verification": verification},
            )
            result.phases["Revision"] = solution
            result.revised = True
            passed = self.verdict_matrix.evaluate(solution, context)
        result.passed = passed

        # Final verdict
        final = self.reviewer.run(
            f"Provide the final verdict and ship-ready output:\n{solution}"
        )
        result.phases["Final Verdict"] = final
        result.final_output = final
        return result


class SelfPlayDebate:
    """Multi-perspective reasoning resolved by a tiebreaker."""

    def __init__(self, participants: List[Any], tiebreaker: QualityArbiter):
        self.participants = participants
        self.tiebreaker = tiebreaker

    def conduct_debate(self, topic: str) -> Dict[str, Any]:
        arguments = {
            getattr(p, "name", str(p)): p.run(
                f"Argue your perspective on: {topic}"
            )
            for p in self.participants
        }
        joined = "\n\n".join(f"{name}: {arg}" for name, arg in arguments.items())
        verdict = self.tiebreaker.run(
            f"Review these arguments and decide:\n{joined}"
        )
        return {"arguments": arguments, "verdict": verdict}


class VerdictMatrix:
    """Quality gate that scores output against weighted standards."""

    DEFAULT_CRITERIA = {
        "completeness": 0.30,
        "correctness": 0.30,
        "clarity": 0.20,
        "safety": 0.20,
    }

    def __init__(
        self,
        quality_arbiter: QualityArbiter,
        reviewer: Reviewer,
        threshold: float = 0.6,
        criteria: Optional[Dict[str, float]] = None,
    ):
        self.quality_arbiter = quality_arbiter
        self.reviewer = reviewer
        self.threshold = threshold
        self.criteria = criteria or dict(self.DEFAULT_CRITERIA)
        self.last_scores: Dict[str, float] = {}

    def evaluate(self, output: str, standards: Optional[Dict[str, Any]] = None) -> bool:
        """Score the output and return whether it clears the threshold.

        The score blends structural heuristics (length, structure, presence of
        caveats) so the gate is meaningful even offline; online the arbiter's
        judgement can refine these signals.
        """
        text = output or ""
        word_count = len(text.split())
        scores = {
            "completeness": min(1.0, word_count / 80.0),
            "correctness": 0.8 if "error" not in text.lower() else 0.4,
            "clarity": min(1.0, text.count("\n") / 4.0 + 0.4),
            "safety": 0.5 if "[simulated" in text else 0.9,
        }
        weighted = sum(scores[k] * self.criteria.get(k, 0) for k in scores)
        self.last_scores = {**scores, "weighted": round(weighted, 3)}
        return weighted >= self.threshold


class EnsemblePatterns:
    """Pre-configured agent collaborations for common task types."""

    @staticmethod
    def _chain(agents: List[Any], task: str) -> Dict[str, str]:
        results: Dict[str, str] = {}
        context: Dict[str, Any] = {}
        for agent in agents:
            output = agent.run(task, context=context)
            name = getattr(agent, "name", str(agent))
            results[name] = output
            context[name] = output
        return results

    @classmethod
    def creative_writing(cls, researcher, executor, reviewer, task: str) -> Dict[str, str]:
        return cls._chain([researcher, executor, reviewer], task)

    @classmethod
    def code_generation(cls, analyst, planner, executor, reviewer, task: str) -> Dict[str, str]:
        return cls._chain([analyst, planner, executor, reviewer], task)

    @classmethod
    def research_and_analysis(cls, researcher, analyst, verifier, task: str) -> Dict[str, str]:
        return cls._chain([researcher, analyst, verifier], task)

    @classmethod
    def security_audit(cls, critic, code_reviewer, advisor, task: str) -> Dict[str, str]:
        return cls._chain([critic, code_reviewer, advisor], task)

    @classmethod
    def documentation(cls, analyst, writer, reviewer, task: str) -> Dict[str, str]:
        return cls._chain([analyst, writer, reviewer], task)
