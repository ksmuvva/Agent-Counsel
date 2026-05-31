"""Demo entry point for the Multi-Agent Council System."""
import json

from core import CouncilSystem


def main():
    print("Initializing Multi-Agent Council System...")
    system = CouncilSystem(budget=20.0)

    task = "Develop a comprehensive market analysis report for a new SaaS product."
    print(f"Executing task: {task}\n")

    result = system.run(task)

    print(f"Tier: {result.tier}")
    if result.selected_personas:
        print(f"Selected SME personas: {', '.join(result.selected_personas)}")
    print(f"Revised: {result.revised} | Passed quality gate: {result.passed}\n")
    print("=== Final Verdict ===")
    print(result.final_output)

    print("\n=== Cost Report ===")
    print(json.dumps(system.cost_summary(), indent=2))


if __name__ == "__main__":
    main()
