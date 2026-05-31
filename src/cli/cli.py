"""Command-line interface for the Multi-Agent Council System."""
import asyncio
import json

import typer

from agents.sme_personas import SMEPersonaManager
from config.agent_config import AGENT_ROLES
from core import CouncilSystem

app = typer.Typer(help="Agent-Counsel: Multi-Agent Council System CLI")


@app.command()
def run(
    task: str = typer.Argument(..., help="The task for the council to execute."),
    budget: float = typer.Option(20.0, help="Spend budget in USD."),
    enforce: bool = typer.Option(False, help="Abort if the budget is exceeded."),
    json_output: bool = typer.Option(False, "--json", help="Emit the full result as JSON."),
):
    """Run a task through the full phase execution pipeline (real agents)."""

    async def _go():
        system = CouncilSystem(
            budget=budget, enforce_budget=enforce, log=lambda m: typer.echo(f"  • {m}")
        )
        result = await system.run(task)
        if json_output:
            typer.echo(json.dumps(result.as_dict(), indent=2))
        else:
            typer.echo(f"\nTier: {result.tier} | Passed: {result.passed}")
            if result.selected_personas:
                typer.echo(f"SME personas: {', '.join(result.selected_personas)}")
            if result.failed_agents:
                typer.echo(f"Degraded (failed) agents: {', '.join(result.failed_agents)}")
            typer.echo("\n=== Final Verdict ===")
            typer.echo(result.final_output)
        typer.echo("\n=== Cost (real, from SDK) ===")
        typer.echo(json.dumps(system.cost_summary(), indent=2))

    asyncio.run(_go())


@app.command("list-agents")
def list_agents():
    """List all permanent agents and their assigned models."""
    for group, members in AGENT_ROLES.items():
        typer.echo(f"\n{group}:")
        for name, cfg in members.items():
            typer.echo(f"  - {name} [{cfg['model']}] — {cfg['description']}")


@app.command("list-personas")
def list_personas():
    """List the available dynamic SME personas."""
    for name in SMEPersonaManager().list_available():
        typer.echo(f"  - {name}")


@app.command()
def version():
    """Show the version."""
    typer.echo("Agent-Counsel 0.2.0")


if __name__ == "__main__":
    app()
