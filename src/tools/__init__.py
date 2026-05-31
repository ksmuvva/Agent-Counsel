"""Tool package — schema-described capabilities the agents can invoke."""
from .base import Tool, ToolError
from .diagram_tools import (
    DiagramSaveTool,
    MermaidHLDTool,
    MermaidLLDTool,
    MermaidValidateTool,
    PlantUMLLLDTool,
)
from .document_tools import (
    DocumentTools,
    ExcelReadTool,
    ExcelWriteTool,
    MissingDependencyError,
    PowerPointReadTool,
    PowerPointWriteTool,
    WebSearchTool,
    WordReadTool,
    WordWriteTool,
)
from .reasoning_tools import (
    ChainOfThoughtTool,
    ClaimVerifierTool,
    TaskDecomposerTool,
    TreeOfThoughtsTool,
)


def default_registry():
    """Return a ``ToolRegistry`` pre-populated with every built-in tool."""
    # Imported here to avoid a hard dependency between the tools package and
    # the core package at import time.
    from core.tool_registry import ToolRegistry

    registry = ToolRegistry()
    registry.register_many(
        [
            # Reasoning
            ChainOfThoughtTool(),
            TreeOfThoughtsTool(),
            ClaimVerifierTool(),
            TaskDecomposerTool(),
            # Documents
            ExcelReadTool(),
            ExcelWriteTool(),
            WordReadTool(),
            WordWriteTool(),
            PowerPointReadTool(),
            PowerPointWriteTool(),
            # Diagrams
            MermaidHLDTool(),
            MermaidLLDTool(),
            PlantUMLLLDTool(),
            MermaidValidateTool(),
            DiagramSaveTool(),
            # Web
            WebSearchTool(),
        ]
    )
    return registry


__all__ = [
    "Tool",
    "ToolError",
    "DocumentTools",
    "MissingDependencyError",
    "ExcelReadTool",
    "ExcelWriteTool",
    "WordReadTool",
    "WordWriteTool",
    "PowerPointReadTool",
    "PowerPointWriteTool",
    "WebSearchTool",
    "ChainOfThoughtTool",
    "TreeOfThoughtsTool",
    "ClaimVerifierTool",
    "TaskDecomposerTool",
    "MermaidHLDTool",
    "MermaidLLDTool",
    "PlantUMLLLDTool",
    "MermaidValidateTool",
    "DiagramSaveTool",
    "default_registry",
]
