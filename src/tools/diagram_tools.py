"""Diagram tools for HLD and LLD.

Two surfaces:

* Generation tools (``mermaid_hld``, ``mermaid_lld``, ``plantuml_lld``) ask
  the LLM to draft diagram source from a natural-language description.
* Validation/persist tools (``mermaid_validate``, ``diagram_save``) accept
  raw diagram source, sanity-check it, and optionally write it to disk.

Output is always the diagram *source* (Mermaid or PlantUML). Rendering to
images is left to whatever toolchain the caller prefers (mermaid-cli,
plantuml.jar, online renderers).
"""
from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional

from .base import Tool, ToolError


_MERMAID_HEADERS = (
    "graph",
    "flowchart",
    "sequencediagram",
    "classdiagram",
    "statediagram",
    "erdiagram",
    "journey",
    "gantt",
    "pie",
    "mindmap",
    "timeline",
    "c4context",
    "c4container",
    "c4component",
    "c4dynamic",
)


def _strip_fence(text: str) -> str:
    """Remove a single ```lang ... ``` fence if present, return the body."""
    body = text.strip()
    match = re.match(r"^```([a-zA-Z0-9_-]*)\s*\n(.*?)\n```\s*$", body, re.DOTALL)
    if match:
        return match.group(2).strip()
    return body


def _validate_mermaid(source: str) -> None:
    body = _strip_fence(source)
    if not body:
        raise ToolError("Mermaid source is empty.")
    first = body.splitlines()[0].strip().lower()
    if not any(first.startswith(h) for h in _MERMAID_HEADERS):
        raise ToolError(
            "Mermaid source must start with a recognised diagram header "
            f"(e.g. {', '.join(_MERMAID_HEADERS[:5])}, ...). Got: {first!r}"
        )


def _validate_plantuml(source: str) -> None:
    body = _strip_fence(source)
    if "@startuml" not in body or "@enduml" not in body:
        raise ToolError("PlantUML source must contain both @startuml and @enduml.")


def _complete(tool_name: str, system: str, prompt: str, *, max_tokens: int = 1200) -> str:
    from core.runtime import Runtime

    runtime = Runtime.get()
    response = runtime.client.complete(
        model="claude-sonnet-4-5",
        system=system,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=0.3,
    )
    runtime.cost_tracker.record_usage(
        f"tool:{tool_name}",
        "claude-sonnet-4-5",
        response.input_tokens,
        response.output_tokens,
    )
    return response.text


# ---------------------------------------------------------------------------
# Generation tools.
# ---------------------------------------------------------------------------
class MermaidHLDTool(Tool):
    name = "mermaid_hld"
    description = (
        "Draft a Mermaid high-level design (HLD) diagram from a natural-language "
        "description. Returns Mermaid source (typically a graph/flowchart or "
        "C4Container view)."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "description": {"type": "string", "minLength": 1},
            "style": {
                "type": "string",
                "enum": ["flowchart", "c4container"],
                "default": "flowchart",
            },
        },
        "required": ["description"],
        "additionalProperties": False,
    }

    def execute(self, *, description: str, style: str = "flowchart") -> str:
        system = (
            "You are a software architect. Produce a Mermaid HLD diagram "
            f"using the {style} syntax. Show major subsystems, external actors "
            "and the data/control flow between them. Reply with the Mermaid "
            "source only — no prose, no code fences."
        )
        source = _strip_fence(_complete(self.name, system, f"## System\n{description}"))
        try:
            _validate_mermaid(source)
        except ToolError:
            header = "flowchart TD" if style == "flowchart" else "C4Container"
            source = f"{header}\n{source}"
            _validate_mermaid(source)
        return source


class MermaidLLDTool(Tool):
    name = "mermaid_lld"
    description = (
        "Draft a Mermaid low-level design (LLD) diagram. Suitable diagram types "
        "include sequenceDiagram, classDiagram and stateDiagram."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "description": {"type": "string", "minLength": 1},
            "diagram_type": {
                "type": "string",
                "enum": ["sequenceDiagram", "classDiagram", "stateDiagram", "erDiagram"],
                "default": "sequenceDiagram",
            },
        },
        "required": ["description"],
        "additionalProperties": False,
    }

    def execute(self, *, description: str, diagram_type: str = "sequenceDiagram") -> str:
        system = (
            "You are a senior engineer producing a low-level design. Output a "
            f"Mermaid {diagram_type}. Be precise about participants, messages, "
            "fields or transitions. Reply with the Mermaid source only — no "
            "prose, no code fences."
        )
        source = _strip_fence(_complete(self.name, system, f"## Detail\n{description}"))
        if not source.lower().startswith(diagram_type.lower()):
            source = f"{diagram_type}\n{source}"
        _validate_mermaid(source)
        return source


class PlantUMLLLDTool(Tool):
    name = "plantuml_lld"
    description = (
        "Draft a PlantUML low-level design diagram (sequence/class/component) "
        "from a description. Returns PlantUML source wrapped in @startuml/@enduml."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "description": {"type": "string", "minLength": 1},
            "diagram_type": {
                "type": "string",
                "enum": ["sequence", "class", "component", "state"],
                "default": "sequence",
            },
        },
        "required": ["description"],
        "additionalProperties": False,
    }

    def execute(self, *, description: str, diagram_type: str = "sequence") -> str:
        system = (
            "You are a senior engineer producing a low-level design as a "
            f"PlantUML {diagram_type} diagram. Reply with PlantUML source only, "
            "wrapped in @startuml/@enduml. No prose, no code fences."
        )
        source = _strip_fence(_complete(self.name, system, f"## Detail\n{description}"))
        if "@startuml" not in source:
            source = f"@startuml\n{source}\n@enduml"
        _validate_plantuml(source)
        return source


# ---------------------------------------------------------------------------
# Validation / persistence tools.
# ---------------------------------------------------------------------------
class MermaidValidateTool(Tool):
    name = "mermaid_validate"
    description = "Sanity-check a Mermaid source string. Returns {valid, header, line_count}."
    input_schema = {
        "type": "object",
        "properties": {"source": {"type": "string", "minLength": 1}},
        "required": ["source"],
        "additionalProperties": False,
    }

    def execute(self, *, source: str) -> Dict[str, Any]:
        body = _strip_fence(source)
        try:
            _validate_mermaid(body)
            return {
                "valid": True,
                "header": body.splitlines()[0].strip(),
                "line_count": len(body.splitlines()),
            }
        except ToolError as exc:
            return {"valid": False, "error": str(exc)}


class DiagramSaveTool(Tool):
    name = "diagram_save"
    description = (
        "Persist diagram source to disk. Suffix is inferred from ``format`` "
        "(mermaid -> .mmd, plantuml -> .puml). Returns the absolute path."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "minLength": 1},
            "source": {"type": "string", "minLength": 1},
            "format": {"type": "string", "enum": ["mermaid", "plantuml"]},
        },
        "required": ["path", "source", "format"],
        "additionalProperties": False,
    }

    def execute(self, *, path: str, source: str, format: str) -> str:
        body = _strip_fence(source)
        if format == "mermaid":
            _validate_mermaid(body)
            suffix = ".mmd"
        else:
            _validate_plantuml(body)
            suffix = ".puml"
        if not path.endswith(suffix):
            path = f"{path}{suffix}"
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body if body.endswith("\n") else body + "\n")
        return os.path.abspath(path)
