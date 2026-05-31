"""Reasoning tools.

Structured-thinking helpers that delegate to the shared :class:`LLMClient`.
Agents call these to get reusable reasoning artefacts — chain-of-thought,
branched alternatives, claim checks, task decompositions — without each
agent re-inventing the prompt.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .base import Tool


def _complete(system: str, prompt: str, *, max_tokens: int = 1024, temperature: float = 0.4) -> str:
    """Run a completion via the shared runtime client."""
    # Imported lazily to keep the tools package free of core dependencies at import time.
    from core.runtime import Runtime

    runtime = Runtime.get()
    response = runtime.client.complete(
        model="claude-sonnet-4-5",
        system=system,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    runtime.cost_tracker.record_usage(
        f"tool:{system[:24]}", "claude-sonnet-4-5", response.input_tokens, response.output_tokens
    )
    return response.text


class ChainOfThoughtTool(Tool):
    name = "chain_of_thought"
    description = (
        "Produce a numbered chain-of-thought walkthrough for a problem, ending "
        "with an explicit Answer line."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "problem": {"type": "string", "minLength": 1},
            "context": {"type": "string"},
        },
        "required": ["problem"],
        "additionalProperties": False,
    }

    def execute(self, *, problem: str, context: str = "") -> str:
        system = (
            "You are a careful reasoner. Think in numbered steps and finish "
            "with a single line that starts with 'Answer:'."
        )
        prompt = f"## Problem\n{problem}"
        if context:
            prompt += f"\n\n## Context\n{context}"
        return _complete(system, prompt)


class TreeOfThoughtsTool(Tool):
    name = "tree_of_thoughts"
    description = (
        "Explore multiple candidate approaches to a problem in parallel, score "
        "each one, and recommend the best."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "problem": {"type": "string", "minLength": 1},
            "branches": {"type": "integer", "minimum": 2, "maximum": 6, "default": 3},
        },
        "required": ["problem"],
        "additionalProperties": False,
    }

    def execute(self, *, problem: str, branches: int = 3) -> Dict[str, Any]:
        system = (
            "You are an expert problem-solver. For the given problem propose "
            f"{branches} distinct approaches. For each approach produce a short "
            "rationale, a numeric score from 0-10, and a one-line outcome. End "
            "with a line 'Recommended: <approach number>'."
        )
        text = _complete(system, f"## Problem\n{problem}", max_tokens=1500, temperature=0.6)
        return {"branches": branches, "analysis": text}


class ClaimVerifierTool(Tool):
    name = "verify_claim"
    description = (
        "Adversarially evaluate a claim against supplied evidence. Returns the "
        "verdict (supported / contradicted / inconclusive) and a justification."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "claim": {"type": "string", "minLength": 1},
            "evidence": {"type": "string", "minLength": 1},
        },
        "required": ["claim", "evidence"],
        "additionalProperties": False,
    }

    def execute(self, *, claim: str, evidence: str) -> Dict[str, str]:
        system = (
            "You are a skeptical fact-checker. Compare the claim to the evidence "
            "and respond in three lines exactly:\n"
            "Verdict: <supported|contradicted|inconclusive>\n"
            "Confidence: <0-1>\n"
            "Reason: <one sentence>"
        )
        text = _complete(
            system,
            f"## Claim\n{claim}\n\n## Evidence\n{evidence}",
            max_tokens=400,
            temperature=0.2,
        )
        result: Dict[str, str] = {"raw": text}
        for line in text.splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                result[key.strip().lower()] = value.strip()
        return result


class TaskDecomposerTool(Tool):
    name = "decompose_task"
    description = (
        "Break a task into an ordered list of concrete subtasks with "
        "dependencies, suitable for planning."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "task": {"type": "string", "minLength": 1},
            "max_steps": {"type": "integer", "minimum": 2, "maximum": 20, "default": 8},
        },
        "required": ["task"],
        "additionalProperties": False,
    }

    def execute(self, *, task: str, max_steps: int = 8) -> List[Dict[str, str]]:
        system = (
            f"You are a senior planner. Decompose the task into up to {max_steps} "
            "atomic subtasks. Respond with one subtask per line in the form:\n"
            "<index>. <title> | depends_on=<comma-separated indices or none> | "
            "outcome=<one short sentence>"
        )
        text = _complete(system, f"## Task\n{task}", max_tokens=900, temperature=0.3)
        steps: List[Dict[str, str]] = []
        for line in text.splitlines():
            line = line.strip()
            if not line or "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            head = parts[0]
            idx, _, title = head.partition(".")
            entry: Dict[str, str] = {"index": idx.strip(), "title": title.strip()}
            for p in parts[1:]:
                if "=" in p:
                    k, _, v = p.partition("=")
                    entry[k.strip()] = v.strip()
            steps.append(entry)
        if not steps:
            # Fall back to a single unstructured entry so the caller always
            # receives the model's response rather than a silent empty list.
            steps.append({"index": "1", "title": text.strip(), "depends_on": "none"})
        return steps
