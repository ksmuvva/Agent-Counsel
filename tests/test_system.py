"""End-to-end and unit tests that run fully offline (no API key needed)."""
import importlib
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


# ---------------------- Installation validation ----------------------------- #
class TestInstallation:
    """Verify that all required packages import and key modules load."""

    @pytest.mark.parametrize("pkg", [
        "streamlit", "openai", "tenacity", "pydantic",
        "openpyxl", "docx", "pptx", "requests",
    ])
    def test_dependency_importable(self, pkg):
        mod = importlib.import_module(pkg)
        assert mod is not None

    def test_core_modules_import(self):
        from core.llm_client import LLMClient, LLMResponse
        from core.cost_tracker import CostTracker, BudgetExceededError
        from core.pipeline import PhaseExecutionPipeline, PipelineResult, VerdictMatrix
        from core.system import CouncilSystem
        from core.runtime import Runtime
        from core.base_agent import BaseAgent
        from core.claude_agent import ClaudeAgent
        from core.model_router import ModelRouter
        from core.agent_factory import AgentFactory
        from core.tool_registry import ToolRegistry
        assert all([
            LLMClient, LLMResponse, CostTracker, BudgetExceededError,
            PhaseExecutionPipeline, PipelineResult, VerdictMatrix,
            CouncilSystem, Runtime, BaseAgent, ClaudeAgent, ModelRouter,
            AgentFactory, ToolRegistry,
        ])

    def test_agent_modules_import(self):
        from agents import (
            Orchestrator, TaskAnalyst, Planner, Clarifier, Researcher,
            Executor, CodeReviewer, Formatter, Verifier, Critic, Reviewer,
            MemoryCurator, DomainCouncilChair, QualityArbiter,
            EthicsSafetyAdvisor, SMEPersonaManager,
        )
        assert all([
            Orchestrator, TaskAnalyst, Planner, Clarifier, Researcher,
            Executor, CodeReviewer, Formatter, Verifier, Critic, Reviewer,
            MemoryCurator, DomainCouncilChair, QualityArbiter,
            EthicsSafetyAdvisor, SMEPersonaManager,
        ])

    def test_config_models_pricing(self):
        from config.models import price_for, PRICING
        assert "glm-4" in PRICING
        assert price_for("glm-4")["input"] > 0
        assert price_for("claude-opus-4-1")["input"] == 15.0
        assert price_for("unknown-model") == {"input": 3.0, "output": 15.0}


# ---------------------- GLM backend integration ----------------------------- #
class TestGLMBackend:
    """Verify GLM/OpenAI-compatible backend wiring (no network needed)."""

    def test_llm_client_offline_backend(self):
        client = LLMClient(backend="offline")
        assert client.online is False
        assert client.backend_name == "offline"

    def test_llm_client_glm_backend_initialises(self):
        client = LLMClient(backend="glm", glm_api_key="test-key")
        assert client.backend_name == "openai"
        assert client.online is True

    def test_glm_error_returns_response_not_exception(self):
        client = LLMClient(backend="glm", glm_api_key="invalid-key",
                           glm_base_url="http://127.0.0.1:1/v1/")
        resp = client.complete("glm-4", "system", "prompt", max_tokens=10)
        assert "error" in resp.text.lower() or resp.simulated

    def test_council_system_with_glm_backend(self):
        os.environ["COUNCIL_OPUS_MODEL"] = "glm-4"
        os.environ["COUNCIL_SONNET_MODEL"] = "glm-4"
        os.environ["COUNCIL_HAIKU_MODEL"] = "glm-4"
        try:
            system = CouncilSystem(budget=5.0, backend="offline")
            assert not system.online
            result = system.run(
                "Design a SailPoint IdentityNow implementation for a 5000-employee enterprise."
            )
            assert result.tier >= 3
            assert "IAM Architect" in result.selected_personas
            assert result.final_output
        finally:
            for k in ("COUNCIL_OPUS_MODEL", "COUNCIL_SONNET_MODEL", "COUNCIL_HAIKU_MODEL"):
                os.environ.pop(k, None)

    def test_sailpoint_tier_classification(self):
        orch = Orchestrator()
        tier = orch.classify_tier(
            "Design a SailPoint IdentityNow implementation plan for a "
            "5,000-employee enterprise migrating from a legacy on-premise IAM system. "
            "The plan must cover: identity lifecycle management, access certifications, "
            "role mining and RBAC model design, integration with Active Directory and "
            "CyberArk PAM, SOX/SOD compliance controls, and a phased rollout strategy."
        )
        assert tier == 4

    def test_sailpoint_sme_selection(self):
        from agents.strategic_council import DomainCouncilChair
        chair = DomainCouncilChair()
        available = SMEPersonaManager().list_available()
        selected = chair.select_personas(
            "SailPoint IdentityNow implementation with CyberArk PAM integration, "
            "cloud migration, security compliance, and AI-driven access modelling.",
            available,
        )
        assert "IAM Architect" in selected
        assert "Cloud Architect" in selected
        assert "Security Analyst" in selected
