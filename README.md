# Agent-Counsel: Multi-Agent Council System

## Overview

Agent-Counsel is a multi-agent system that tackles complex tasks through collaborative AI agents. It is built on the **Claude Agent SDK**: every agent is a real, tool-using ReAct agent, not a scripted mock. It features a council of permanent agents, dynamic SME personas, a structured phase execution pipeline, and dual user interfaces (CLI and Streamlit).

## Features

- **Real tool-using agents**: Each agent runs a genuine ReAct loop via the Claude Agent SDK — it reasons, calls the tools it has been granted, observes the results, and iterates. Each agent is sandboxed to only its own tools.
- **15 Permanent Agents**: 3 Strategic Council agents and 12 Operational agents, each with a defined role and model (Opus or Sonnet).
- **10 Dynamic SME Personas**: On-demand domain experts, engaged automatically when the Council selects them for a task.
- **Phase Execution Pipeline**: A real async workflow — tier classification → analysis → Council consultation (Tier 3-4) → SME input → planning → execution → adversarial critique + verification → final verdict — where each phase is an actual agent run.
- **Adversarial review & verdict gate**: A Critic attacks the output along five vectors, a Verifier fact-checks it, and a Reviewer issues a PASS/FAIL verdict parsed from its own output. On FAIL, the Executor automatically revises the solution and the gate re-runs (bounded by `--max-revisions`, default 1).
- **Real document & web tools**: Genuine Excel/Word/PowerPoint read/write (`openpyxl`, `python-docx`, `python-pptx`) and web search (Tavily), executed in-process and fed back into the agent's reasoning.
- **Real cost tracking**: Per-agent USD cost and turn counts taken directly from the SDK's reported usage — actual billed amounts, with optional budget enforcement.
- **Dual UI**: A Typer CLI for automation and a Streamlit web app for interactive use.

## Agent Roster

### Strategic Council (Tier 3-4 only)

| Agent                   | Role                                    | Model |
|-------------------------|-----------------------------------------|-------|
| Domain Council Chair    | SME selection & governance              | Opus  |
| Quality Arbiter         | Quality standard setting & tiebreaker   | Opus  |
| Ethics & Safety Advisor | Bias, PII, compliance review            | Opus  |

### Operational Agents

| Agent            | Role                                          | Model   |
|------------------|-----------------------------------------------|---------|
| Orchestrator     | Parent agent, tier classification, coordination | Opus    |
| Task Analyst     | Task decomposition & requirements analysis    | Sonnet  |
| Planner          | Execution planning & sequencing               | Sonnet  |
| Clarifier        | Question formulation for missing requirements | Sonnet  |
| Researcher       | Evidence gathering & web research             | Sonnet  |
| Executor         | Solution generation with Tree of Thoughts     | Sonnet  |
| Code Reviewer    | Security, performance, style review           | Sonnet  |
| Formatter        | Multi-format output generation                | Sonnet  |
| Verifier         | Hallucination detection & fact-checking       | Opus    |
| Critic           | Adversarial attack (5 vectors)                | Opus    |
| Reviewer         | Final quality gate                            | Opus    |
| Memory Curator   | Knowledge extraction & persistence            | Sonnet  |

### Dynamic SME Personas (10 available)

| Persona             | Domain                      | Skills                                    |
|---------------------|-----------------------------|-------------------------------------------|
| IAM Architect       | Identity & Access Management| SailPoint, CyberArk, RBAC                 |
| Cloud Architect     | Cloud Infrastructure        | Azure, AWS, GCP                           |
| Security Analyst    | Security & Compliance       | Threat modelling, OWASP                   |
| Data Engineer       | Data Pipelines              | ETL, databases, SQL                       |
| AI/ML Engineer      | AI/ML Systems               | GenAI, RAG, agents                        |
| Test Engineer       | Testing Strategies          | Test cases, SIT, UAT                      |
| Business Analyst    | Requirements & Processes    | BPMN, gap analysis                        |
| Technical Writer    | Documentation               | Docs, tenders, reports                    |
| DevOps Engineer     | CI/CD & Infrastructure      | Docker, Kubernetes, Terraform             |
| Frontend Developer  | UI Development              | Streamlit, React, dashboards              |

## Quick Start

### Prerequisites

- Python 3.10 or higher
- A working **Claude Agent SDK** environment — either an authenticated `claude`
  CLI on your `PATH`, or an `ANTHROPIC_API_KEY`. The agents are real: each run
  drives the model through the SDK and the model decides when to call tools.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ksmuvva/Agent-Counsel.git
    cd Agent-Counsel
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Authenticate** (one of):
    ```bash
    # Option A — use the Claude CLI (the SDK spawns it):
    npm install -g @anthropic-ai/claude-code && claude login

    # Option B — use an API key:
    export ANTHROPIC_API_KEY="sk-ant-..."

    # Optional — enable the Researcher's real web_search tool:
    export TAVILY_API_KEY="tvly-..."

    # Optional — confine all document-tool reads/writes to one directory
    # (recommended outside local dev; unset means unrestricted):
    export COUNCIL_OUTPUT_DIR="./outputs"
    ```

### How it works (real agents, real tools)

Every agent is a genuine ReAct loop run via the Claude Agent SDK: the model
reasons, may call the in-process Python tools it has been granted (real
Excel/Word/PowerPoint I/O and web search), observes the results, and iterates
to a final answer. Each agent is sandboxed to **only** its own tools, and
costs/turns reported in the cost summary come straight from the SDK — they are
actual billed amounts, not estimates. There is no mock or simulation path.

### Running the CLI

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python src/cli/cli.py run "Write a one-page market analysis for an AI SaaS product"
python src/cli/cli.py list-agents
python src/cli/cli.py list-personas
```

### Running the Streamlit App

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
streamlit run src/ui/streamlit_app.py
```

### Running the Tests

```bash
pytest
```

Pure-logic tests (parsers, cost math, tool wiring) run anywhere. The end-to-end
test makes a real SDK call and is skipped automatically if no SDK environment
is detected.

## Project Structure

```
Agent-Counsel/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── operational_agents.py   # 12 operational agent factories
│   │   ├── sme_personas.py         # dynamic SME persona manager
│   │   └── strategic_council.py    # 3 council agent factories
│   ├── cli/
│   │   └── cli.py                  # Typer CLI (async run / list-agents / list-personas)
│   ├── config/
│   │   ├── agent_config.py         # agent + persona roster
│   │   └── models.py               # model aliases (env-overridable)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── base_agent.py           # Agent: a real SDK-backed ReAct agent
│   │   ├── sdk_runner.py           # invoke_agent: the real execution engine
│   │   ├── cost_tracker.py         # cost/turns from real SDK ResultMessage
│   │   ├── pipeline.py             # real async multi-agent orchestration
│   │   └── system.py               # CouncilSystem assembly
│   ├── tools/
│   │   ├── __init__.py
│   │   └── document_tools.py       # real @tool functions + SDK MCP server
│   ├── ui/
│   │   └── streamlit_app.py
│   └── main.py
├── tests/
│   └── test_system.py              # logic tests + a real end-to-end SDK test
├── DESIGN.md
├── README.md
└── requirements.txt
```

## Development

### Adding New Agents

1.  Add a factory function in the relevant module under `src/agents/` that
    returns an `Agent` (see `core/base_agent.py`), giving it a `system_prompt`
    and the `allowed_tools` it may call.
2.  Export it from `src/agents/__init__.py` and wire it into the pipeline.

### Adding New Tools

1.  Define a real `@tool` function in `src/tools/document_tools.py` and add it
    to `ALL_TOOLS` (it is then served by `build_tool_server`).
2.  Add its fully-qualified name (`mcp__council_tools__<name>`) to the
    `allowed_tools` of any agent that should be able to call it.

## License

[Specify your license here, e.g., MIT License]
