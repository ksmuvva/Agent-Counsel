from core import (
    ModelRouter, AgentFactory, ToolRegistry, CostTracker,
    PhaseExecutionPipeline, SelfPlayDebate, VerdictMatrix
)
from config.agent_config import AGENT_ROLES
from agents import (
    DomainCouncilChair, QualityArbiter, EthicsSafetyAdvisor,
    Orchestrator, TaskAnalyst, Planner, Clarifier, Researcher,
    Executor, CodeReviewer, Formatter, Verifier, Critic, Reviewer, MemoryCurator,
    SMEPersonaManager
)
from tools import DocumentTools, WebSearchTool

def main():
    # Initialize components
    model_mapping = {}
    for category in ["Strategic Council", "Operational Agents"]:
        for role, config in AGENT_ROLES[category].items():
            model_mapping[role] = config["model"]

    router = ModelRouter(model_mapping)
    factory = AgentFactory(router)
    registry = ToolRegistry()
    tracker = CostTracker()

    # Register tools
    registry.register_tool("WebSearch", WebSearchTool.search)
    registry.register_tool("ReadExcel", DocumentTools.read_excel)
    registry.register_tool("WriteWord", DocumentTools.write_word)

    print(f"Tools registered: {registry.list_tools()}")

    # Create a Researcher agent and add the WebSearch tool
    researcher_config = AGENT_ROLES["Operational Agents"]["Researcher"]
    researcher = factory.create_agent(
        "Researcher", 
        "Researcher", 
        researcher_config["description"]
    )
    researcher.add_tool(registry.get_tool("WebSearch"))

    print(f"Created agent: {researcher}")
    print(f"Agent tools: {researcher.tools}")

    # Mock running the agent with a tool
    response = researcher.run("Search for the latest trends in multi-agent systems.")
    print(f"Researcher response: {response}")

if __name__ == "__main__":
    main()
