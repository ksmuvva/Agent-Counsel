"""Tests for the schema-based tool framework."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core import Runtime  # noqa: E402
from core.tool_registry import ToolRegistry  # noqa: E402
from tools import (  # noqa: E402
    ChainOfThoughtTool,
    ClaimVerifierTool,
    DiagramSaveTool,
    MermaidHLDTool,
    MermaidLLDTool,
    MermaidValidateTool,
    PlantUMLLLDTool,
    TaskDecomposerTool,
    Tool,
    ToolError,
    TreeOfThoughtsTool,
    WebSearchTool,
    default_registry,
)


@pytest.fixture(autouse=True)
def fresh_runtime():
    Runtime.reset()
    yield
    Runtime.reset()


def test_default_registry_has_expected_tools():
    registry = default_registry()
    names = set(registry.list_tools())
    expected = {
        "chain_of_thought",
        "tree_of_thoughts",
        "verify_claim",
        "decompose_task",
        "excel_read",
        "excel_write",
        "word_read",
        "word_write",
        "powerpoint_read",
        "powerpoint_write",
        "mermaid_hld",
        "mermaid_lld",
        "plantuml_lld",
        "mermaid_validate",
        "diagram_save",
        "web_search",
    }
    assert expected.issubset(names)


def test_anthropic_specs_match_schema_shape():
    registry = default_registry()
    specs = registry.anthropic_tool_specs()
    assert len(specs) == len(registry.list_tools())
    for spec in specs:
        assert {"name", "description", "input_schema"} <= set(spec)
        assert spec["input_schema"]["type"] == "object"


def test_tool_validates_input():
    tool = ChainOfThoughtTool()
    with pytest.raises(ToolError):
        tool.run()  # missing 'problem'
    with pytest.raises(ToolError):
        tool.run(problem="x", unknown_field=1)


def test_registry_rejects_duplicates():
    registry = ToolRegistry()
    registry.register_tool(ChainOfThoughtTool())
    with pytest.raises(ValueError):
        registry.register_tool(ChainOfThoughtTool())


def test_registry_invoke_dispatches_to_tool():
    registry = default_registry()
    out = registry.invoke("chain_of_thought", problem="What is 2 + 2?")
    assert "[simulated" in out  # offline runtime → deterministic simulated output


def test_web_search_requires_api_key(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    with pytest.raises(ToolError):
        WebSearchTool().run(query="anything")


def test_mermaid_hld_returns_valid_source():
    tool = MermaidHLDTool()
    src = tool.run(description="A web app with a Postgres database and a Redis cache.")
    header = src.splitlines()[0].strip().lower()
    assert header.startswith(("flowchart", "graph", "c4container"))


def test_mermaid_lld_prefixes_diagram_type_when_missing():
    src = MermaidLLDTool().run(
        description="User logs in via OAuth.",
        diagram_type="sequenceDiagram",
    )
    assert src.lower().startswith("sequencediagram")


def test_plantuml_lld_wraps_in_startuml():
    src = PlantUMLLLDTool().run(description="A class with two methods.")
    assert "@startuml" in src and "@enduml" in src


def test_mermaid_validate_detects_invalid():
    result = MermaidValidateTool().run(source="this is not a diagram")
    assert result["valid"] is False


def test_mermaid_validate_accepts_fenced():
    fenced = "```mermaid\nflowchart LR\n  A --> B\n```"
    result = MermaidValidateTool().run(source=fenced)
    assert result["valid"] is True
    assert result["line_count"] == 2


def test_diagram_save_writes_file(tmp_path):
    target = tmp_path / "design"
    path = DiagramSaveTool().run(
        path=str(target),
        source="flowchart TD\n  A --> B",
        format="mermaid",
    )
    assert path.endswith(".mmd")
    with open(path) as fh:
        assert "flowchart TD" in fh.read()


def test_runtime_exposes_tool_registry():
    runtime = Runtime.get()
    assert "chain_of_thought" in runtime.tools.list_tools()


def test_reasoning_tools_run_offline():
    """Every reasoning tool must produce *some* output via the offline fallback."""
    for tool_cls, kwargs in [
        (ChainOfThoughtTool, {"problem": "Add 1 + 1"}),
        (TreeOfThoughtsTool, {"problem": "Choose a database", "branches": 2}),
        (ClaimVerifierTool, {"claim": "The sky is blue.", "evidence": "Daytime photo of a clear sky."}),
        (TaskDecomposerTool, {"task": "Launch a new product"}),
    ]:
        out = tool_cls().run(**kwargs)
        assert out  # truthy: non-empty string / dict / list


class _NoName(Tool):
    description = "x"

    def execute(self):
        return None


def test_tool_requires_name():
    with pytest.raises(ToolError):
        _NoName()
