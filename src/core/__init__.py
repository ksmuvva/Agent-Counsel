"""Core package.

``Agent``, ``CostTracker`` and the SDK runner are safe to import eagerly. The
pipeline/system modules import the ``agents`` package (which in turn imports
``core.base_agent``), so they are exposed lazily via ``__getattr__`` to avoid a
circular import at package-init time.
"""
from .base_agent import Agent
from .cost_tracker import CostTracker, BudgetExceededError
from .sdk_runner import AgentResult, invoke_agent

__all__ = [
    "Agent",
    "CostTracker",
    "BudgetExceededError",
    "AgentResult",
    "invoke_agent",
    "PhaseExecutionPipeline",
    "PipelineResult",
    "CouncilSystem",
]


def __getattr__(name):
    if name in ("PhaseExecutionPipeline", "PipelineResult"):
        from . import pipeline

        return getattr(pipeline, name)
    if name == "CouncilSystem":
        from .system import CouncilSystem

        return CouncilSystem
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
