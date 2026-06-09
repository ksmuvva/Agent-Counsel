"""Tests for the Multi-Agent Council System.

These exercise real wiring, not mocks. Pure-logic tests (parsers, cost math,
tool registration, agent construction) run anywhere. The end-to-end test makes
a genuine Claude Agent SDK call and is skipped only when no SDK environment is
available (no authenticated `claude` CLI and no ANTHROPIC_API_KEY).
"""
import os
import shutil
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.cost_tracker import CostTracker, BudgetExceededError  # noqa: E402
from core.sdk_runner import AgentResult  # noqa: E402
from core.pipeline import _parse_tier, _parse_personas, _parse_verdict  # noqa: E402
from agents.sme_personas import SMEPersonaManager  # noqa: E402
from agents.operational_agents import researcher, executor  # noqa: E402
from tools.document_tools import (  # noqa: E402
    ALL_TOOLS,
    DOCUMENT_TOOL_NAMES,
    WEB_SEARCH_TOOL_NAME,
    build_tool_server,
)


def _sdk_available() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY")) or shutil.which("claude") is not None


# ----------------------------- pure logic -------------------------------- #
def test_parse_tier():
    assert _parse_tier("Reasoning here.\nTIER: 4") == 4
    assert _parse_tier("no marker") == 2  # safe default


def test_parse_personas():
    available = SMEPersonaManager().list_available()
    text = "These domains apply.\nSELECTED: Cloud Architect, Security Analyst"
    assert _parse_personas(text, available) == ["Cloud Architect", "Security Analyst"]
    assert _parse_personas("nothing selected", available) == []


def test_parse_verdict():
    assert _parse_verdict("Looks good.\nVERDICT: PASS") is True
    assert _parse_verdict("Needs work.\nVERDICT: FAIL") is False
    assert _parse_verdict("no verdict at all") is False
    # The reviewer often restates the rubric before deciding — only the last
    # verdict marker counts.
    assert _parse_verdict(
        "I must end with 'VERDICT: PASS' or 'VERDICT: FAIL'.\n"
        "The solution has gaps.\nVERDICT: FAIL"
    ) is False


def test_output_dir_confinement(tmp_path, monkeypatch):
    from tools.document_tools import _resolve_path

    base = tmp_path / "outputs"
    base.mkdir()
    monkeypatch.setenv("COUNCIL_OUTPUT_DIR", str(base))
    inside = base / "report.docx"
    assert _resolve_path(str(inside)) == str(inside)
    with pytest.raises(ValueError):
        _resolve_path(str(tmp_path / "escape.docx"))
    with pytest.raises(ValueError):
        _resolve_path(str(base / ".." / "escape.docx"))
    # Unset → unconfined (default behaviour preserved)
    monkeypatch.delenv("COUNCIL_OUTPUT_DIR")
    assert _resolve_path(str(tmp_path / "anywhere.docx"))


def test_cost_tracker_uses_real_sdk_numbers():
    tracker = CostTracker(budget=1.0)
    r = AgentResult(text="hi", cost_usd=0.0123, num_turns=3, duration_ms=500,
                    tools_used=["mcp__council_tools__web_search"])
    tracker.record("Researcher", r)
    assert tracker.total_cost == pytest.approx(0.0123)
    assert tracker.total_turns == 3
    assert "mcp__council_tools__web_search" in tracker.summary()["tools_invoked"]


def test_cost_tracker_budget_enforced():
    tracker = CostTracker(budget=0.01, enforce=True)
    with pytest.raises(BudgetExceededError):
        tracker.record("X", AgentResult(text="", cost_usd=0.5, num_turns=1, duration_ms=1))


def test_tool_server_builds_with_all_tools():
    server = build_tool_server()
    assert server is not None
    assert len(ALL_TOOLS) == 6


def test_agents_are_granted_real_tools():
    # The Researcher must actually be allowed to call the web_search tool.
    assert WEB_SEARCH_TOOL_NAME in researcher().allowed_tools
    # The Executor must be allowed to write real documents.
    assert set(DOCUMENT_TOOL_NAMES).issubset(set(executor().allowed_tools))


def test_persona_manager():
    mgr = SMEPersonaManager()
    assert len(mgr.list_available()) == 10
    persona = mgr.get_persona("Cloud Architect")
    assert persona is not None and "Cloud Infrastructure" in persona.system_prompt
    assert mgr.get_persona("Nonexistent") is None


# ------------------------- real end-to-end ------------------------------- #
@pytest.mark.skipif(not _sdk_available(), reason="No Claude Agent SDK environment available")
@pytest.mark.asyncio
async def test_real_agent_uses_a_tool(tmp_path):
    """A genuine agent run that must actually invoke a document tool."""
    from agents.operational_agents import formatter
    from core.cost_tracker import CostTracker

    out = tmp_path / "out.docx"
    tracker = CostTracker(budget=5.0)
    result = await formatter().run(
        f"Write a Word document to the path '{out}' containing the text 'Hello Council'.",
        mcp_servers={"council_tools": build_tool_server()},
        cost_tracker=tracker,
    )
    assert any("write_word" in t for t in result.tools_used)
    assert out.exists()
    assert tracker.total_cost >= 0.0
