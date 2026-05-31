# Multi-Agent Council System Design

## 1. Introduction
This document describes the architecture of the Multi-Agent Council system: a framework that coordinates Council, Operational and on-demand SME agents through a structured pipeline and a schema-based tool layer, with both CLI and Streamlit front-ends.

## 2. Core Components

### 2.1 Agent SDK
- **Claude Code Agent SDK**: foundation for building and running agents. The runtime wraps the official `anthropic` SDK. There is **no offline simulator** — `LLMClient` requires the `anthropic` package and `ANTHROPIC_API_KEY` and raises `LLMUnavailableError` if either is missing. Pure unit tests (heuristics, cost arithmetic, schema validation, file I/O) run without a key; integration tests that hit the real API are skipped when no key is set.

### 2.2 Agent Types
- **Permanent Agents**: 15 agents (3 Council, 12 Operational) with predefined roles and models (Opus / Sonnet).
- **Dynamic SME Personas**: 10+ on-demand domain experts with specific skills.

### 2.3 Key Features
- **Phase Execution Pipeline**: structured workflow with Council consultation.
- **Self-Play Debate**: multi-perspective reasoning with a tiebreaker.
- **Verdict Matrix**: quality gate with automatic revision triggering.
- **Ensemble Patterns**: pre-configured agent collaborations (chain / parallel-vote).
- **Multi-Modal I/O**: text, documents (Excel, Word, PPT), diagrams (Mermaid, PlantUML).
- **Cost Tracking**: per-call accounting and optional budget enforcement.

### 2.4 User Interfaces
- **CLI (Typer)**: command-line interaction and automation.
- **Streamlit Web UI**: interactive web-based control and visualisation.

## 3. System Architecture Overview

```mermaid
graph TD
    User --> CLI[CLI (Typer)]
    User --> Streamlit[Streamlit Web UI]

    CLI --> Orchestrator[Orchestrator Agent]
    Streamlit --> Orchestrator

    Orchestrator --> StrategicCouncil[Strategic Council]
    Orchestrator --> OperationalAgents[Operational Agents]
    Orchestrator --> SMEPersonas[Dynamic SME Personas]

    Orchestrator -- manages --> PhaseExecutionPipeline
    PhaseExecutionPipeline --> SelfPlayDebate
    PhaseExecutionPipeline --> VerdictMatrix
    PhaseExecutionPipeline --> EnsemblePatterns

    Orchestrator -- uses --> Runtime[Runtime]
    Runtime --> LLMClient
    Runtime --> CostTracker
    Runtime --> ToolRegistry

    ToolRegistry --> ReasoningTools[Reasoning Tools]
    ToolRegistry --> DiagramTools[Diagram Tools (Mermaid / PlantUML)]
    ToolRegistry --> DocumentTools[Document Tools (Excel / Word / PPT)]
    ToolRegistry --> WebSearchTool[Web Search Tool]

    AllAgents[All Agents] -- resolve via --> ToolRegistry
    AllAgents -- report to --> CostTracker
```

## 4. Core Framework

Located in `src/core/`:

- **`base_agent.py`** — `BaseAgent` abstract class; common `run(task, context)` interface and a `tools` list.
- **`claude_agent.py`** — concrete agent backed by `LLMClient`; records token usage against `CostTracker`.
- **`model_router.py`** — maps roles to model IDs (Opus / Sonnet).
- **`agent_factory.py`** — instantiates agents from role configs via `ModelRouter`.
- **`llm_client.py`** — wraps the Anthropic SDK. Real-only: constructor raises `LLMUnavailableError` if the SDK is not installed or `ANTHROPIC_API_KEY` is not set. Retries with exponential backoff via tenacity.
- **`cost_tracker.py`** — per-call price accounting with optional budget enforcement (`BudgetExceededError`).
- **`runtime.py`** — singleton holding the shared `LLMClient`, `CostTracker` and `ToolRegistry`. Agents read from `Runtime.get()` instead of receiving each dependency through their constructor.
- **`tool_registry.py`** — name-keyed registry of schema-based tools; can hand specs to Claude's tool-use API via `anthropic_tool_specs()`.
- **`pipeline.py`** — `PhaseExecutionPipeline`, `SelfPlayDebate`, `VerdictMatrix`, `EnsemblePatterns`.
- **`system.py`** — `CouncilSystem` glues the runtime, agents and pipeline together.

## 5. Agent Implementations

### 5.1 Strategic Council (`src/agents/strategic_council.py`)
- **Domain Council Chair** — SME selection & governance.
- **Quality Arbiter** — quality standard setting & tiebreaker.
- **Ethics & Safety Advisor** — bias, PII, compliance review.

### 5.2 Operational Agents (`src/agents/operational_agents.py`)
Orchestrator, Task Analyst, Planner, Clarifier, Researcher, Executor, Code Reviewer, Formatter, Verifier, Critic, Reviewer, Memory Curator.

### 5.3 Dynamic SME Personas (`src/agents/sme_personas.py`)
`SMEPersonaManager` instantiates SMEs on demand from a predefined catalogue (Cloud Architect, IAM Architect, Security Analyst, Data Engineer, AI/ML Engineer, etc.).

## 6. Advanced Pipeline Features (`src/core/pipeline.py`)
- **PhaseExecutionPipeline** — orchestrates phases (Analysis, Planning, Execution, Review, Final Verdict) with Council consultation gated by task tier.
- **SelfPlayDebate** — agents argue opposing positions; `QualityArbiter` arbitrates.
- **VerdictMatrix** — weighted quality gate (completeness / correctness / clarity / safety) computed from structural signals. `arbiter_score()` additionally delegates to the real Quality Arbiter agent for deep semantic scoring.
- **EnsemblePatterns** — built-in collaboration shapes (chain, parallel-vote) for reuse across tasks.

## 7. User Interfaces

### 7.1 CLI (`src/cli/cli.py`)
Typer commands for running tasks, listing agents/personas, and inspecting cost.

### 7.2 Streamlit Web UI (`src/ui/streamlit_app.py`)
Dashboard, task runner with agent selection, agent management view, cost tracker view.

## 8. Tool Layer

All tools implement the same contract and are wired into the runtime via `default_registry()` (`src/tools/__init__.py`).

### 8.1 `Tool` contract (`src/tools/base.py`)
Every tool declares:

- `name` — unique snake_case identifier used by the registry and Claude.
- `description` — one-line summary the model sees when picking tools.
- `input_schema` — JSON Schema describing the keyword arguments of `execute`.
- `execute(**kwargs)` — the actual implementation.

`Tool.run(**kwargs)` validates inputs against the schema via `jsonschema` and raises `ToolError` on mismatch. `Tool.as_anthropic_tool()` returns the same metadata in the shape Claude's tool-use API expects, so a single declaration drives both local dispatch and remote tool-use.

### 8.2 `ToolRegistry` (`src/core/tool_registry.py`)
- `register_tool(tool)` / `register_many([...])` — name is read from `tool.name`.
- `get_tool(name)` / `invoke(name, **kwargs)` — name-keyed lookup and dispatch.
- `anthropic_tool_specs()` — list of specs to hand to Claude when an agent should be allowed to call tools.

The registry is built lazily by `Runtime` and is reachable from any agent via `Runtime.get().tools`.

### 8.3 Built-in tools

**Reasoning** (`src/tools/reasoning_tools.py`)
| Tool | Purpose |
| --- | --- |
| `chain_of_thought` | Numbered CoT walkthrough ending with an `Answer:` line. |
| `tree_of_thoughts` | Generates N branches, scores each, recommends the best. |
| `verify_claim` | Skeptical fact-check of a claim against supplied evidence; returns `verdict / confidence / reason`. |
| `decompose_task` | Breaks a task into ordered subtasks with dependencies and outcomes. |

**Documents** (`src/tools/document_tools.py`)
| Tool | Backed by |
| --- | --- |
| `excel_read` / `excel_write` | `openpyxl` |
| `word_read` / `word_write` | `python-docx` |
| `powerpoint_read` / `powerpoint_write` | `python-pptx` |

Missing optional dependencies raise `MissingDependencyError` with an install hint — no silent fakes.

**Diagrams (HLD / LLD)** (`src/tools/diagram_tools.py`)
| Tool | Purpose |
| --- | --- |
| `mermaid_hld` | Draft a Mermaid HLD (`flowchart` or `C4Container`) from a description. |
| `mermaid_lld` | Draft a Mermaid LLD (`sequenceDiagram` / `classDiagram` / `stateDiagram` / `erDiagram`). |
| `plantuml_lld` | Draft a PlantUML LLD (sequence / class / component / state). |
| `mermaid_validate` | Header / structure check on arbitrary Mermaid source. |
| `diagram_save` | Validate then persist Mermaid (`.mmd`) or PlantUML (`.puml`) source to disk. |

Generation tools produce *source* only; rendering to images is delegated to whichever toolchain the caller prefers (`mermaid-cli`, `plantuml.jar`, etc.).

**Web research** (`src/tools/document_tools.py`)
| Tool | Backed by |
| --- | --- |
| `web_search` | Tavily API (requires `TAVILY_API_KEY`); raises `ToolError` if absent. |

### 8.4 Adding a new tool
1. Subclass `Tool` and set `name`, `description`, `input_schema`.
2. Implement `execute(**kwargs)`.
3. Register it in `tools.default_registry()` (or call `runtime.tools.register_tool(...)` at runtime).
That's it — the registry, schema validation and Claude tool-use spec come for free.

## 9. Development Environment
- Python 3.10+
- **Required**: `anthropic` + `ANTHROPIC_API_KEY` — the system is real-only.
- Optional: `openpyxl` / `python-docx` / `python-pptx` (document tools), `requests` + `TAVILY_API_KEY` (web search), `mermaid-cli` / `plantuml.jar` (diagram rendering).
- Streamlit, Typer.

## 10. Roadmap
1. Image tools (vision + OCR) for the multi-modal pipeline.
2. Code-file tools (read / patch / lint) for the Code Reviewer agent.
3. Optional renderers for `diagram_save` (`mermaid-cli`, `plantuml.jar`) to emit SVG/PNG alongside source.
4. Tool-use loop in `ClaudeAgent` that exposes `runtime.tools.anthropic_tool_specs()` to the model and dispatches tool calls automatically.
5. Persistent memory store fed by the Memory Curator.
