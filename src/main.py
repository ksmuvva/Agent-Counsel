"""Demo entry point for the Multi-Agent Council System.

Runs the real pipeline end-to-end via the Claude Agent SDK. Requires a working
SDK environment (an authenticated `claude` CLI or ANTHROPIC_API_KEY).
"""
import asyncio
import json

from core import CouncilSystem


async def _main() -> None:
    print("Initializing Multi-Agent Council System (Claude Agent SDK)...\n")
    system = CouncilSystem(budget=20.0, log=lambda m: print(f"  • {m}"))

    task = "Write a concise one-page market analysis for a new AI note-taking SaaS product."
    print(f"Executing task: {task}\n")

    result = await system.run(task)

    print(f"\nTier: {result.tier}")
    if result.selected_personas:
        print(f"Selected SME personas: {', '.join(result.selected_personas)}")
    print(f"Passed quality gate: {result.passed}")
    if result.failed_agents:
        print(f"Agents that failed (degraded): {', '.join(result.failed_agents)}")
    print()
    print("=== Final Verdict ===")
    print(result.final_output)

    print("\n=== Cost Report (real, from SDK) ===")
    print(json.dumps(system.cost_summary(), indent=2))


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
