"""End-to-end and unit tests that run fully offline (no API key needed)."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core import CouncilSystem, Runtime  # noqa: E402
from core.cost_tracker import CostTracker, BudgetExceededError  # noqa: E402
from core.llm_client import LLMClient  # noqa: E402
from core.pipeline import VerdictMatrix, SelfPlayDebate  # noqa: E402
from agents import Critic, Orchestrator, QualityArbiter, Reviewer, Verifier  # noqa: E402
from agents.sme_personas import SMEPersonaManager  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_runtime():
    Runtime.reset()
    yield
    Runtime.reset()


def test_offline_client_is_deterministic():
    client = LLMClient(api_key=None)
    assert client.online is False
    a = client.complete("claude-sonnet-4-5", "You are X.", "Do the thing.")
    b = client.complete("claude-sonnet-4-5", "You are X.", "Do the thing.")
    assert a.text == b.text
    assert a.simulated is True
    assert a.output_tokens > 0


def test_pipeline_runs_end_to_end():
    system = CouncilSystem(budget=50.0)
    result = system.run("Design a comprehensive, secure enterprise cloud architecture.")
    assert 1 <= result.tier <= 4
    assert result.final_output
    assert "Analysis" in result.phases
    assert "Final Verdict" in result.phases
    assert system.cost_summary()["calls"] > 0


def test_complex_task_triggers_council():
    system = CouncilSystem(budget=50.0)
    result = system.run(
        "Design a comprehensive enterprise security and IAM architecture for "
        "a multi-cloud production migration with full compliance auditing."
    )
    assert result.tier >= 3
    assert "Council" in result.phases
    assert result.selected_personas  # keyword routing should pick experts


def test_tier_classification_monotonic():
    orch = Orchestrator()
    simple = orch.classify_tier("Add two numbers.")
    complex_ = orch.classify_tier(
        "Design a comprehensive, production-grade, enterprise security "
        "architecture with multi-cloud migration and compliance audit."
    )
    assert simple < complex_


def test_cost_tracker_pricing_and_budget():
    tracker = CostTracker(budget=0.0, enforce=True)
    with pytest.raises(BudgetExceededError):
        tracker.record_usage("X", "claude-opus-4-1", 1000, 1000)

    tracker2 = CostTracker(budget=100.0)
    cost = tracker2.record_usage("X", "claude-opus-4-1", 1_000_000, 1_000_000)
    assert cost == pytest.approx(15.0 + 75.0)


def test_verdict_matrix_threshold():
    vm = VerdictMatrix(QualityArbiter(), Reviewer())
    assert vm.evaluate("error " * 2) is False
    long_text = "A solid, complete answer.\n" * 20
    assert vm.evaluate(long_text) is True


def test_self_play_debate():
    Runtime.reset()
    debate = SelfPlayDebate([Critic(), Verifier()], QualityArbiter())
    out = debate.conduct_debate("Is X better than Y?")
    assert "arguments" in out and "verdict" in out
    assert len(out["arguments"]) == 2


def test_sme_persona_manager():
    mgr = SMEPersonaManager()
    assert len(mgr.list_available()) == 10
    persona = mgr.get_persona("Cloud Architect")
    assert persona is not None
    assert persona.domain == "Cloud Infrastructure"
    assert mgr.get_persona("Nonexistent") is None
