# Agent-Counsel: Multi-Agent Council System

## Overview

Agent-Counsel is a sophisticated multi-agent system designed to tackle complex tasks through collaborative AI agents. It leverages the Claude Code Agent SDK and features a council of permanent agents, dynamic SME personas, a structured phase execution pipeline, and dual user interfaces (CLI and Streamlit).

## Features

- **15 Permanent Agents**: Comprising 3 Strategic Council agents and 12 Operational agents, each with predefined roles and assigned LLM models (Claude Opus or Sonnet).
- **10+ Dynamic SME Personas**: On-demand domain experts that can be instantiated as needed for specialized tasks.
- **Phase Execution Pipeline**: A structured workflow that guides task execution, incorporating Council consultation at critical junctures.
- **Self-Play Debate**: A mechanism for multi-perspective reasoning, including a tiebreaker function to resolve disagreements.
- **Verdict Matrix**: A quality gate that evaluates outputs and can trigger automatic revisions.
- **5 Ensemble Patterns**: Pre-configured collaboration strategies for agents to work together effectively.
- **Multi-Modal I/O**: Support for processing and generating text, images, documents (Excel, Word, PowerPoint), and code files.
- **Cost Tracking**: Real-time monitoring and enforcement of budget constraints for LLM API usage.
- **Dual UI**: A command-line interface (CLI) built with Typer for automation and a rich web interface built with Streamlit for interactive control and visualization.

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
- `ANTHROPIC_API_KEY` exported in your environment (the system is real-only — see DESIGN.md §2.1)

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
    *(Note: `requirements.txt` will be generated in the next step)*

4.  **Set up your API key:**
    Create a `.env` file in the root directory and add:
    ```
    ANTHROPIC_API_KEY="your_anthropic_api_key"
    # Optional, for the web_search tool:
    # TAVILY_API_KEY="your_tavily_api_key"
    ```

### Running the CLI

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python src/cli/cli.py --help
```

### Running the Streamlit App

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
streamlit run src/ui/streamlit_app.py
```

## Project Structure

```
Agent-Counsel/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── operational_agents.py
│   │   ├── sme_personas.py
│   │   └── strategic_council.py
│   ├── cli/
│   │   └── cli.py
│   ├── config/
│   │   ├── agent_config.py
│   │   └── models.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── agent_factory.py
│   │   ├── base_agent.py
│   │   ├── claude_agent.py
│   │   ├── cost_tracker.py
│   │   ├── llm_client.py
│   │   ├── model_router.py
│   │   ├── pipeline.py
│   │   ├── runtime.py
│   │   ├── system.py
│   │   └── tool_registry.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── diagram_tools.py
│   │   ├── document_tools.py
│   │   └── reasoning_tools.py
│   ├── ui/
│   │   └── streamlit_app.py
│   └── main.py
├── tests/
│   ├── test_system.py
│   └── test_tools.py
├── DESIGN.md
├── README.md
└── requirements.txt
```

## Development

### Adding New Agents

1.  Create a new agent class inheriting from `BaseAgent` (or `StrategicCouncilAgent`/`OperationalAgent`/`SMEPersona`).
2.  Add the agent's configuration to `src/config/agent_config.py`.
3.  Update `src/agents/__init__.py` to export the new agent.

### Adding New Tools

1.  Subclass `tools.Tool` in `src/tools/`, set `name`, `description`, and a JSON `input_schema`, then implement `execute(**kwargs)`.
2.  Register an instance in `tools.default_registry()` (or call `runtime.tools.register_tool(MyTool())` at runtime). The same `Tool` declaration drives schema validation, local dispatch, and the Anthropic tool-use spec.
3.  To let an agent actually call the tool, attach it: `agent.add_tool(runtime.tools.get_tool("my_tool"))`. `ClaudeAgent.run()` will drive the tool-use loop automatically.

## License

[Specify your license here, e.g., MIT License]
