# Multi-Agent Council System Design

## 1. Introduction
This document outlines the architectural design for the Multi-Agent Council system, which will leverage the Claude Code Agent SDK. The system aims to provide a robust and flexible framework for complex task execution through collaborative AI agents, featuring a dual user interface (CLI and Streamlit).

## 2. Core Components

### 2.1 Agent SDK
- **Claude Code Agent SDK**: The foundational SDK for building and managing agents. We will integrate with the `claude-agent-sdk-python` library.

### 2.2 Agent Types
- **Permanent Agents**: 15 agents (3 Council, 12 Operational) with predefined roles and models (Opus/Sonnet).
- **Dynamic SME Personas**: 10+ on-demand domain experts with specific skills.

### 2.3 Key Features
- **Phase Execution Pipeline**: Structured workflow with Council consultation.
- **Self-Play Debate**: Multi-perspective reasoning with tiebreaker.
- **Verdict Matrix**: Quality gate with automatic revision triggering.
- **5 Ensemble Patterns**: Pre-configured agent collaborations.
- **Multi-Modal I/O**: Support for text, images, documents (Excel, Word, PPT), and code files.
- **Cost Tracking**: Budget enforcement with real-time monitoring.

### 2.4 User Interfaces
- **CLI (Typer)**: For command-line interaction and automation.
- **Streamlit Web Interface**: For interactive web-based control and visualization.

## 3. System Architecture Overview

```mermaid
graph TD
    User --> CLI[CLI (Typer)]
    User --> Streamlit[Streamlit Web UI]

    CLI --> Orchestrator[Orchestrator Agent]
    Streamlit --> Orchestrator

    Orchestrator --> StrategicCouncil[Strategic Council Agents]
    Orchestrator --> OperationalAgents[Operational Agents]
    Orchestrator --> SMEPersonas[Dynamic SME Personas]

    StrategicCouncil --> DomainCouncilChair
    StrategicCouncil --> QualityArbiter
    StrategicCouncil --> EthicsSafetyAdvisor

    OperationalAgents --> TaskAnalyst
    OperationalAgents --> Planner
    OperationalAgents --> Clarifier
    OperationalAgents --> Researcher
    OperationalAgents --> Executor
    OperationalAgents --> CodeReviewer
    OperationalAgents --> Formatter
    OperationalAgents --> Verifier
    OperationalAgents --> Critic
    OperationalAgents --> Reviewer
    OperationalAgents --> MemoryCurator

    SMEPersonas --> IAMArchitect
    SMEPersonas --> CloudArchitect
    SMEPersonas --> SecurityAnalyst
    SMEPersonas --> DataEngineer
    SMEPersonas --> AIMLEngineer
    SMEPersonas --> TestEngineer
    SMEPersonas --> BusinessAnalyst
    SMEPersonas --> TechnicalWriter
    SMEPersonas --> DevOpsEngineer
    SMEPersonas --> FrontendDeveloper

    Orchestrator -- Manages --> PhaseExecutionPipeline
    PhaseExecutionPipeline --> SelfPlayDebate
    PhaseExecutionPipeline --> VerdictMatrix
    PhaseExecutionPipeline --> EnsemblePatterns

    Orchestrator -- Utilizes --> ToolRegistry[Tool Registry]
    Orchestrator -- Tracks --> CostTracker[Cost Tracker]

    ToolRegistry --> WebSearch[Web Search Tool]
    ToolRegistry --> DocumentTools[Document Tools (Excel, Word, PPT)]
    ToolRegistry --> CodeFiles[Code File Tools]
    ToolRegistry --> ImageTools[Image Tools]

    AllAgents[All Agents] -- Access --> ToolRegistry
    AllAgents -- Report to --> CostTracker
    AllAgents -- Interact via --> MultiModalIO[Multi-Modal I/O]
```

## 4. Core Framework Implementation

The foundational components for the agent system have been laid out in the `src/core` directory:

- **`base_agent.py`**: Defines the `BaseAgent` abstract class, providing a common interface for all agents, including methods for adding tools and running tasks. All specific agents will inherit from this class.
- **`model_router.py`**: Manages the mapping of agent roles to specific LLM models (e.g., Opus, Sonnet). This allows for flexible model assignment and easy updates.
- **`tool_registry.py`**: A central repository for registering and retrieving tools that agents can utilize. This ensures discoverability and standardized access to external functionalities like web search or document processing.
- **`cost_tracker.py`**: Implements functionality to monitor and record the costs associated with agent operations, providing real-time budget enforcement and reporting.
- **`claude_agent.py`**: Provides a wrapper for integrating with the Claude Code Agent SDK, allowing agents to leverage Claude's capabilities.
- **`agent_factory.py`**: A factory class for creating agent instances based on their roles and configurations, using the `ModelRouter` to assign appropriate LLM models.

## 5. Agent Implementations

### 5.1 Strategic Council Agents

Implemented in `src/agents/strategic_council.py`, these agents are responsible for high-level governance and decision-making:
- **Domain Council Chair**: SME selection & governance.
- **Quality Arbiter**: Quality standard setting & tiebreaker.
- **Ethics & Safety Advisor**: Bias, PII, compliance review.

### 5.2 Operational Agents

Implemented in `src/agents/operational_agents.py`, these agents handle the execution of tasks:
- **Orchestrator**: Parent agent, tier classification, coordination.
- **Task Analyst**: Task decomposition & requirements analysis.
- **Planner**: Execution planning & sequencing.
- **Clarifier**: Question formulation for missing requirements.
- **Researcher**: Evidence gathering & web research.
- **Executor**: Solution generation with Tree of Thoughts.
- **Code Reviewer**: Security, performance, style review.
- **Formatter**: Multi-format output generation.
- **Verifier**: Hallucination detection & fact-checking.
- **Critic**: Adversarial attack (5 vectors).
- **Reviewer**: Final quality gate.
- **Memory Curator**: Knowledge extraction & persistence.

### 5.3 Dynamic SME Personas

Implemented in `src/agents/sme_personas.py`, this system allows for on-demand instantiation of specialized domain experts:
- **SMEPersona**: Base class for dynamic SME agents.
- **SMEPersonaManager**: Manages the creation and retrieval of SME personas based on predefined configurations.

## 6. Advanced Features Implementation

Implemented in `src/core/pipeline.py`, these components provide sophisticated control over agent collaboration and task execution:
- **Phase Execution Pipeline**: Defines a structured workflow for task execution, incorporating various phases and agent consultations.
- **Self-Play Debate**: Facilitates multi-perspective reasoning among agents, with a `QualityArbiter` acting as a tiebreaker.
- **Verdict Matrix**: Acts as a quality gate, evaluating agent outputs against predefined standards and triggering revisions if necessary.
- **Phase pipeline**: real async orchestration in `src/core/pipeline.py`, where
  each phase is an actual agent run and control signals (tier, selected
  personas, PASS/FAIL verdict) are parsed from the agents' own output.

## 7. User Interfaces

### 7.1 CLI (Typer)

Implemented in `src/cli/cli.py`, providing command-line access to the system:
- Commands for running tasks, listing agents and personas, and managing costs.

### 7.2 Streamlit Web Interface

Implemented in `src/ui/streamlit_app.py`, offering an interactive web-based control panel:
- Dashboard for system overview.
- Interface for running tasks and selecting agents.
- Agent management and cost tracking views.

## 8. Tool Integration

Implemented in `src/tools/document_tools.py` as real in-process `@tool`
functions, exposed to the agents through an SDK MCP server
(`build_tool_server`). When an agent decides to call one, the SDK executes the
Python code and feeds the result back into the model's reasoning loop:
- **Document tools**: real Excel (`openpyxl`), Word (`python-docx`), and
  PowerPoint (`python-pptx`) read/write.
- **web_search**: real web search via the Tavily API (errors clearly if
  `TAVILY_API_KEY` is unset, rather than returning fabricated results).

Each agent is sandboxed via `ClaudeAgentOptions(tools=...)` so it can only call
the tools it has been granted — not the host CLI's built-ins.

## 9. Execution Engine

`src/core/sdk_runner.py` is the real engine. `invoke_agent` runs one agent to
completion via `claude_agent_sdk.query`, returning an `AgentResult` with the
final text, the tools actually invoked, the real `total_cost_usd`, and the
turn count — all sourced directly from the SDK's `ResultMessage`. There is no
mock or offline simulation path.

## 10. Development Environment Setup

- **Python 3.10+**
- **claude-agent-sdk** (drives the agent loop and tool calling)
- An authenticated `claude` CLI **or** `ANTHROPIC_API_KEY`
- **Streamlit**, **Typer**
- Optional: `TAVILY_API_KEY` for the web_search tool
