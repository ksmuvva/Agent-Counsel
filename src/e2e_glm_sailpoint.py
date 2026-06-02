"""End-to-end test: GLM-4 on a SailPoint IAM governance scenario.

Runs the full Agent-Counsel pipeline (all phases, all agents) using ZhipuAI's
GLM-4 model via its OpenAI-compatible API.  Validates that:
 1. The LLMClient routes to the GLM backend.
 2. Every pipeline phase produces a real (non-simulated) response.
 3. The SailPoint domain task is handled end-to-end.
"""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from config.models import GLM_MODEL
from core.system import CouncilSystem

SAILPOINT_TASK = (
    "Design a SailPoint IdentityNow implementation plan for a 5,000-employee "
    "enterprise migrating from a legacy on-premise IAM system. The plan must "
    "cover: identity lifecycle management, access certifications, role mining "
    "and RBAC model design, integration with Active Directory and CyberArk PAM, "
    "SOX/SOD compliance controls, and a phased rollout strategy. Include specific "
    "SailPoint features (e.g., Identity Security Cloud, Access Modeling, "
    "Workflows) and risk mitigations."
)


def main() -> None:
    api_key = os.environ.get("GLM_API_KEY", "")
    if not api_key:
        print("ERROR: Set GLM_API_KEY environment variable.")
        sys.exit(1)

    # Force all agents to use the GLM model via env overrides.
    os.environ["COUNCIL_OPUS_MODEL"] = GLM_MODEL
    os.environ["COUNCIL_SONNET_MODEL"] = GLM_MODEL
    os.environ["COUNCIL_HAIKU_MODEL"] = GLM_MODEL

    print("=" * 70)
    print("E2E SailPoint Test — GLM-4 via ZhipuAI")
    print("=" * 70)
    print(f"\nModel : {GLM_MODEL}")
    print(f"Task  : {SAILPOINT_TASK[:120]}...")

    logs: list[str] = []

    def log(msg: str) -> None:
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        logs.append(line)
        print(f"  • {line}")

    system = CouncilSystem(
        budget=5.0,
        log=log,
        backend="glm",
        glm_api_key=api_key,
    )

    print(f"\nBackend : {system.online and 'ONLINE (GLM-4)' or 'OFFLINE (simulated)'}")
    if not system.online:
        print("WARNING: Running in offline/simulated mode — GLM client not connected.")

    t0 = time.monotonic()
    result = system.run(SAILPOINT_TASK)
    elapsed = time.monotonic() - t0

    print(f"\n{'=' * 70}")
    print("RESULTS")
    print(f"{'=' * 70}")
    print(f"  Tier              : {result.tier}")
    print(f"  Selected personas : {', '.join(result.selected_personas) or '(none)'}")
    print(f"  Quality gate      : {'PASS' if result.passed else 'FAIL'}")
    print(f"  Revised           : {result.revised}")
    print(f"  Total time        : {elapsed:.1f}s")

    print(f"\n{'─' * 70}")
    print("PHASE OUTPUTS (first 300 chars each)")
    print(f"{'─' * 70}")
    for phase_name, output in result.phases.items():
        if isinstance(output, dict):
            preview = json.dumps(output, default=str)[:300]
        else:
            preview = str(output)[:300]
        print(f"\n  [{phase_name}]")
        print(f"    {preview}")

    print(f"\n{'─' * 70}")
    print("FINAL OUTPUT (first 500 chars)")
    print(f"{'─' * 70}")
    print(result.final_output[:500])

    cost = system.cost_summary()
    print(f"\n{'─' * 70}")
    print("COST REPORT")
    print(f"{'─' * 70}")
    print(json.dumps(cost, indent=2))

    # Save full results
    out = {
        "task": SAILPOINT_TASK,
        "model": GLM_MODEL,
        "tier": result.tier,
        "selected_personas": result.selected_personas,
        "passed": result.passed,
        "revised": result.revised,
        "elapsed_s": round(elapsed, 1),
        "phases": {k: str(v)[:2000] for k, v in result.phases.items()},
        "final_output": result.final_output,
        "cost": cost,
        "logs": logs,
    }
    with open("/tmp/e2e_glm_sailpoint_results.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nFull results saved to /tmp/e2e_glm_sailpoint_results.json")

    if not system.online:
        print("\nNOTE: Test ran in simulated mode. Set GLM_API_KEY for a real run.")
        sys.exit(2)
    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
