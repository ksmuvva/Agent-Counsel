"""Tier 1-2 operational agents that execute the work."""
from __future__ import annotations

from core.base_agent import Agent
from config.models import OPUS, SONNET
from tools.document_tools import DOCUMENT_TOOL_NAMES, WEB_SEARCH_TOOL_NAME


def orchestrator() -> Agent:
    return Agent(
        name="Orchestrator",
        description="Parent agent, tier classification, coordination",
        model=OPUS,
        system_prompt=(
            "You are the Orchestrator. Classify the task's complexity into a tier: "
            "1=trivial, 2=standard, 3=complex, 4=critical. Consider scope, risk, and "
            "how many domains are involved. Reply with a one-line justification then "
            "a final line 'TIER: <n>'."
        ),
        max_turns=2,
    )


def task_analyst() -> Agent:
    return Agent(
        name="Task Analyst",
        description="Task decomposition & requirements analysis",
        model=SONNET,
        system_prompt=(
            "You are the Task Analyst. Decompose the task into explicit "
            "requirements, constraints, and measurable success criteria."
        ),
    )


def planner() -> Agent:
    return Agent(
        name="Planner",
        description="Execution planning & sequencing",
        model=SONNET,
        system_prompt=(
            "You are the Planner. Produce an ordered, actionable execution plan with "
            "clear steps and dependencies."
        ),
    )


def clarifier() -> Agent:
    return Agent(
        name="Clarifier",
        description="Question formulation for missing requirements",
        model=SONNET,
        system_prompt=(
            "You are the Clarifier. Identify ambiguities and formulate the minimal "
            "set of questions needed to proceed confidently."
        ),
    )


def researcher() -> Agent:
    return Agent(
        name="Researcher",
        description="Evidence gathering & web research",
        model=SONNET,
        system_prompt=(
            "You are the Researcher. Gather relevant evidence. Use the web_search "
            "tool when current or external facts are needed, and cite the sources "
            "you used."
        ),
        allowed_tools=[WEB_SEARCH_TOOL_NAME],
    )


def executor() -> Agent:
    return Agent(
        name="Executor",
        description="Solution generation with Tree of Thoughts",
        model=SONNET,
        system_prompt=(
            "You are the Executor. Generate the solution using a Tree of Thoughts: "
            "briefly explore alternative approaches, then commit to and develop the "
            "strongest one. If asked to produce a document, use the document tools "
            "to write the real file."
        ),
        allowed_tools=list(DOCUMENT_TOOL_NAMES),
        max_turns=12,
    )


def code_reviewer() -> Agent:
    return Agent(
        name="Code Reviewer",
        description="Security, performance, style review",
        model=SONNET,
        system_prompt=(
            "You are the Code Reviewer. Review for security, performance, and style "
            "issues, and suggest concrete fixes."
        ),
    )


def formatter() -> Agent:
    return Agent(
        name="Formatter",
        description="Multi-format output generation",
        model=SONNET,
        system_prompt=(
            "You are the Formatter. Render the final content cleanly in the "
            "requested format. Use the document tools to produce real .xlsx/.docx/"
            ".pptx files when asked."
        ),
        allowed_tools=list(DOCUMENT_TOOL_NAMES),
    )


def verifier() -> Agent:
    return Agent(
        name="Verifier",
        description="Hallucination detection & fact-checking",
        model=OPUS,
        system_prompt=(
            "You are the Verifier. Check the output for unsupported claims and "
            "factual errors. Use web_search to confirm questionable facts, and "
            "report a confidence assessment."
        ),
        allowed_tools=[WEB_SEARCH_TOOL_NAME],
    )


def critic() -> Agent:
    return Agent(
        name="Critic",
        description="Adversarial attack (5 vectors)",
        model=OPUS,
        system_prompt=(
            "You are the Critic. Adversarially attack the output along five vectors: "
            "correctness, completeness, security, edge cases, and clarity. For each "
            "vector list specific, concrete weaknesses."
        ),
    )


def reviewer() -> Agent:
    return Agent(
        name="Reviewer",
        description="Final quality gate",
        model=OPUS,
        system_prompt=(
            "You are the Reviewer, the final quality gate. Decide whether the output "
            "is ready to ship, produce the final ship-ready output, and end with a "
            "line 'VERDICT: PASS' or 'VERDICT: FAIL'."
        ),
    )


def memory_curator() -> Agent:
    return Agent(
        name="Memory Curator",
        description="Knowledge extraction & persistence",
        model=SONNET,
        system_prompt=(
            "You are the Memory Curator. Extract durable, reusable knowledge from "
            "the task and its outcome for future reference."
        ),
    )
