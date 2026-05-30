"""Tier 1-2 operational agents that execute the work."""
import re
from typing import Any, Dict, List, Optional

from core.claude_agent import ClaudeAgent
from config.models import OPUS, SONNET


class Orchestrator(ClaudeAgent):
    def __init__(self):
        super().__init__(
            name="Orchestrator",
            description="Parent agent, tier classification, coordination",
            model=OPUS,
            system_prompt=(
                "You are the Orchestrator. Classify task complexity into a tier "
                "(1=trivial, 2=standard, 3=complex, 4=critical) and coordinate "
                "the operational agents."
            ),
        )

    def classify_tier(self, task: str) -> int:
        """Estimate task complexity tier from signal words and length.

        Online this can be delegated to the LLM; the heuristic below guarantees
        a sensible tier offline and as a fast-path default.
        """
        text = task.lower()
        score = 1
        complex_signals = [
            "architecture", "design", "security", "compliance", "migrate",
            "end-to-end", "production", "scal", "multi", "strategy", "audit",
            "comprehensive", "enterprise", "critical",
        ]
        score += sum(1 for s in complex_signals if s in text)
        if len(task) > 400:
            score += 1
        if len(re.findall(r"[.!?]", task)) > 4:
            score += 1
        return max(1, min(4, score))


class TaskAnalyst(ClaudeAgent):
    def __init__(self):
        super().__init__(
            name="Task Analyst",
            description="Task decomposition & requirements analysis",
            model=SONNET,
            system_prompt=(
                "You are the Task Analyst. Decompose the task into explicit "
                "requirements, constraints, and success criteria."
            ),
        )


class Planner(ClaudeAgent):
    def __init__(self):
        super().__init__(
            name="Planner",
            description="Execution planning & sequencing",
            model=SONNET,
            system_prompt=(
                "You are the Planner. Produce an ordered, actionable execution "
                "plan with clear steps and dependencies."
            ),
        )


class Clarifier(ClaudeAgent):
    def __init__(self):
        super().__init__(
            name="Clarifier",
            description="Question formulation for missing requirements",
            model=SONNET,
            system_prompt=(
                "You are the Clarifier. Identify ambiguities and formulate the "
                "minimal set of questions needed to proceed confidently."
            ),
        )


class Researcher(ClaudeAgent):
    def __init__(self):
        super().__init__(
            name="Researcher",
            description="Evidence gathering & web research",
            model=SONNET,
            system_prompt=(
                "You are the Researcher. Gather relevant evidence and cite "
                "sources where possible."
            ),
        )


class Executor(ClaudeAgent):
    def __init__(self):
        super().__init__(
            name="Executor",
            description="Solution generation with Tree of Thoughts",
            model=SONNET,
            max_tokens=2048,
            system_prompt=(
                "You are the Executor. Generate the solution using a Tree of "
                "Thoughts: briefly explore alternative approaches, then commit "
                "to and develop the strongest one."
            ),
        )


class CodeReviewer(ClaudeAgent):
    def __init__(self):
        super().__init__(
            name="Code Reviewer",
            description="Security, performance, style review",
            model=SONNET,
            system_prompt=(
                "You are the Code Reviewer. Review for security, performance, "
                "and style issues, and suggest concrete fixes."
            ),
        )


class Formatter(ClaudeAgent):
    def __init__(self):
        super().__init__(
            name="Formatter",
            description="Multi-format output generation",
            model=SONNET,
            system_prompt=(
                "You are the Formatter. Render the final content cleanly in the "
                "requested output format."
            ),
        )


class Verifier(ClaudeAgent):
    def __init__(self):
        super().__init__(
            name="Verifier",
            description="Hallucination detection & fact-checking",
            model=OPUS,
            system_prompt=(
                "You are the Verifier. Check the output for unsupported claims "
                "and factual errors, and report a confidence assessment."
            ),
        )


class Critic(ClaudeAgent):
    """Adversarial reviewer attacking along five vectors."""

    ATTACK_VECTORS = [
        "Correctness",
        "Completeness",
        "Security",
        "Edge cases",
        "Clarity",
    ]

    def __init__(self):
        super().__init__(
            name="Critic",
            description="Adversarial attack (5 vectors)",
            model=OPUS,
            system_prompt=(
                "You are the Critic. Adversarially attack the output along five "
                "vectors: correctness, completeness, security, edge cases, and "
                "clarity. Be specific and ruthless."
            ),
        )

    def attack(self, output: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Run the critique across each attack vector and return findings."""
        findings: Dict[str, str] = {}
        for vector in self.ATTACK_VECTORS:
            findings[vector] = self.run(
                f"Attack this output on the '{vector}' vector and list weaknesses:\n{output}",
                context=context,
            )
        return findings


class Reviewer(ClaudeAgent):
    def __init__(self):
        super().__init__(
            name="Reviewer",
            description="Final quality gate",
            model=OPUS,
            system_prompt=(
                "You are the Reviewer, the final quality gate. Decide whether "
                "the output is ready to ship and summarise the verdict."
            ),
        )


class MemoryCurator(ClaudeAgent):
    def __init__(self):
        super().__init__(
            name="Memory Curator",
            description="Knowledge extraction & persistence",
            model=SONNET,
            system_prompt=(
                "You are the Memory Curator. Extract durable, reusable knowledge "
                "from the task and its outcome for future reference."
            ),
        )
