import typer
from typing import Optional
from core import CostTracker
from agents import SMEPersonaManager
from config.agent_config import AGENT_ROLES

app = typer.Typer()

# Global instances
cost_tracker = CostTracker()
sme_manager = SMEPersonaManager(AGENT_ROLES["Dynamic SME Personas"], "claude-3-5-sonnet-20240620")

@app.command()
def run_task(task: str, agent: Optional[str] = None):
    """Run a task with a specific agent or the orchestrator."""
    typer.echo(f"Running task: {task}")
    if agent:
        typer.echo(f"Using agent: {agent}")
    else:
        typer.echo("Using default Orchestrator agent")

@app.command()
def list_agents():
    """List all available agents."""
    typer.echo("Strategic Council Agents:")
    for agent_name in AGENT_ROLES["Strategic Council"].keys():
        typer.echo(f"  - {agent_name}")
    
    typer.echo("\nOperational Agents:")
    for agent_name in AGENT_ROLES["Operational Agents"].keys():
        typer.echo(f"  - {agent_name}")

@app.command()
def list_personas():
    """List all available SME personas."""
    typer.echo("Available SME Personas:")
    for persona_name in sme_manager.list_available_personas():
        typer.echo(f"  - {persona_name}")

@app.command()
def get_costs():
    """Display total costs."""
    typer.echo(f"Total Cost: ${cost_tracker.get_total_cost():.4f}")
    for agent_name, cost in cost_tracker.costs.items():
        typer.echo(f"  - {agent_name}: ${cost:.4f}")

@app.command()
def reset_costs():
    """Reset all recorded costs."""
    cost_tracker.reset()
    typer.echo("Costs reset successfully.")

if __name__ == "__main__":
    app()
