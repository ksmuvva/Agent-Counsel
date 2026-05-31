"""Schema-based tool interface.

Every tool the agents can call inherits from :class:`Tool`. A tool declares
its name, a human description, and a JSON-schema for its inputs. Calling the
tool runs ``execute`` after validating the arguments against the schema.

The schema doubles as the Anthropic tool-use definition, so the same object
is what the registry hands to ``LLMClient`` when an agent needs callable
tools online.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

try:
    from jsonschema import Draft202012Validator
    _SCHEMA_AVAILABLE = True
except Exception:  # pragma: no cover - jsonschema is in requirements
    Draft202012Validator = None  # type: ignore
    _SCHEMA_AVAILABLE = False


class ToolError(RuntimeError):
    """Raised when a tool's inputs are invalid or execution fails."""


class Tool(ABC):
    """Base class for all schema-described tools."""

    #: Unique tool name (snake_case). Used by the registry and by Claude.
    name: str = ""
    #: One-line description shown to the model when picking tools.
    description: str = ""
    #: JSON Schema describing the ``execute`` keyword arguments.
    input_schema: Dict[str, Any] = {"type": "object", "properties": {}}

    def __init__(self) -> None:
        if not self.name:
            raise ToolError(f"{type(self).__name__} must define a non-empty name.")
        if not self.description:
            raise ToolError(f"{type(self).__name__} must define a description.")
        if _SCHEMA_AVAILABLE:
            Draft202012Validator.check_schema(self.input_schema)
            self._validator = Draft202012Validator(self.input_schema)
        else:  # pragma: no cover
            self._validator = None

    # ---- public API ----------------------------------------------------
    def run(self, **kwargs: Any) -> Any:
        """Validate ``kwargs`` against the schema and delegate to ``execute``."""
        self._validate(kwargs)
        return self.execute(**kwargs)

    def as_anthropic_tool(self) -> Dict[str, Any]:
        """Return the tool spec in the format Claude's tool-use API expects."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }

    # ---- subclass contract --------------------------------------------
    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Run the tool. Subclasses implement the actual behaviour."""

    # ---- internals -----------------------------------------------------
    def _validate(self, payload: Dict[str, Any]) -> None:
        if self._validator is None:
            return
        errors = sorted(self._validator.iter_errors(payload), key=lambda e: e.path)
        if errors:
            details = "; ".join(
                f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
                for e in errors
            )
            raise ToolError(f"Invalid input for tool '{self.name}': {details}")

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"Tool(name='{self.name}')"
