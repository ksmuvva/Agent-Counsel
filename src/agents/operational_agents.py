from typing import Any, Dict, Optional
from core.claude_agent import ClaudeAgent

class OperationalAgent(ClaudeAgent):
    """Base class for Operational Agents."""
    def __init__(self, name: str, description: str, model: str, system_prompt: Optional[str] = None):
        super().__init__(name, description, model, system_prompt)

class Orchestrator(OperationalAgent):
    """Parent agent, tier classification, coordination."""
    def __init__(self, model: str):
        system_prompt = "You are the Orchestrator. Your role is to coordinate all agents and manage the overall workflow."
        super().__init__("Orchestrator", "Parent agent, tier classification, coordination", model, system_prompt)

class TaskAnalyst(OperationalAgent):
    """Task decomposition & requirements analysis."""
    def __init__(self, model: str):
        system_prompt = "You are the Task Analyst. Your role is to decompose tasks and analyze requirements."
        super().__init__("Task Analyst", "Task decomposition & requirements analysis", model, system_prompt)

class Planner(OperationalAgent):
    """Execution planning & sequencing."""
    def __init__(self, model: str):
        system_prompt = "You are the Planner. Your role is to plan the execution sequence of tasks."
        super().__init__("Planner", "Execution planning & sequencing", model, system_prompt)

class Clarifier(OperationalAgent):
    """Question formulation for missing requirements."""
    def __init__(self, model: str):
        system_prompt = "You are the Clarifier. Your role is to identify and ask questions about missing requirements."
        super().__init__("Clarifier", "Question formulation for missing requirements", model, system_prompt)

class Researcher(OperationalAgent):
    """Evidence gathering & web research."""
    def __init__(self, model: str):
        system_prompt = "You are the Researcher. Your role is to gather evidence and conduct web research."
        super().__init__("Researcher", "Evidence gathering & web research", model, system_prompt)

class Executor(OperationalAgent):
    """Solution generation with Tree of Thoughts."""
    def __init__(self, model: str):
        system_prompt = "You are the Executor. Your role is to generate solutions using the Tree of Thoughts method."
        super().__init__("Executor", "Solution generation with Tree of Thoughts", model, system_prompt)

class CodeReviewer(OperationalAgent):
    """Security, performance, style review."""
    def __init__(self, model: str):
        system_prompt = "You are the Code Reviewer. Your role is to review code for security, performance, and style."
        super().__init__("Code Reviewer", "Security, performance, style review", model, system_prompt)

class Formatter(OperationalAgent):
    """Multi-format output generation."""
    def __init__(self, model: str):
        system_prompt = "You are the Formatter. Your role is to generate outputs in multiple formats."
        super().__init__("Formatter", "Multi-format output generation", model, system_prompt)

class Verifier(OperationalAgent):
    """Hallucination detection & fact-checking."""
    def __init__(self, model: str):
        system_prompt = "You are the Verifier. Your role is to detect hallucinations and perform fact-checking."
        super().__init__("Verifier", "Hallucination detection & fact-checking", model, system_prompt)

class Critic(OperationalAgent):
    """Adversarial attack (5 vectors)."""
    def __init__(self, model: str):
        system_prompt = "You are the Critic. Your role is to perform adversarial attacks using 5 vectors."
        super().__init__("Critic", "Adversarial attack (5 vectors)", model, system_prompt)

class Reviewer(OperationalAgent):
    """Final quality gate."""
    def __init__(self, model: str):
        system_prompt = "You are the Reviewer. Your role is to act as the final quality gate."
        super().__init__("Reviewer", "Final quality gate", model, system_prompt)

class MemoryCurator(OperationalAgent):
    """Knowledge extraction & persistence."""
    def __init__(self, model: str):
        system_prompt = "You are the Memory Curator. Your role is to extract and persist knowledge."
        super().__init__("Memory Curator", "Knowledge extraction & persistence", model, system_prompt)
