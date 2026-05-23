#!/usr/bin/env python3
"""
claim_to_agent_task.py — dango-ogi-bridge

Transform a Dan-Go Claim JSON into an OGI-style agent task.

Runs post_scarcity_guard first. Blocks if guard fails.

Usage:
  python runtime/claim_to_agent_task.py examples/post-scarcity.claim.json
  python runtime/claim_to_agent_task.py examples/post-scarcity.claim.json --json
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))
from post_scarcity_guard import run_guard, final_decision

# ── Contribution → Capability mapping ─────────────────────────
CONTRIBUTION_TO_CAPABILITY = {
    "coordination":   "negotiation",
    "translation":    "translation",
    "compute":        "compute",
    "legal_review":   "risk_review",
    "safety_review":  "risk_review",
    "risk_review":    "risk_review",
    "distribution":   "distribution",
    "funding":        "monetary_contribution",
    "story_editing":  "content_review",
    "verification":   "verification",
    "local_knowledge":"local_knowledge",
    "care":           "care",
    "code":           "code",
}

# ── Decision → Task status ─────────────────────────────────────
DECISION_TO_STATUS = {
    "negotiate": "open",
    "execute":   "active",
    "escalate":  "under_review",
    "reject":    "closed",
}

# ── Task type inference ────────────────────────────────────────
def _infer_task_type(contributions: list[str]) -> str:
    if "coordination" in contributions:
        return "coordination_analysis"
    if "legal_review" in contributions or "safety_review" in contributions or "risk_review" in contributions:
        return "risk_assessment"
    if "translation" in contributions:
        return "translation_task"
    if "compute" in contributions:
        return "compute_task"
    if "distribution" in contributions:
        return "distribution_task"
    if "funding" in contributions:
        return "resource_allocation"
    return "general_coordination"


def transform(claim: dict, guard_decision: str, guard_reason: str) -> dict:
    claim_id      = claim.get("claim_id", "unknown")
    contributions = claim.get("possible_contributions", [])
    constraints   = claim.get("dignity_constraints", [])
    decision      = claim.get("decision", "negotiate")

    # Map contributions → capabilities (deduplicate while preserving order)
    seen: set[str] = set()
    capabilities: list[str] = []
    for c in contributions:
        cap = CONTRIBUTION_TO_CAPABILITY.get(c, c)
        if cap not in seen:
            seen.add(cap)
            capabilities.append(cap)

    task_status   = "blocked" if guard_decision == "block" else DECISION_TO_STATUS.get(decision, "open")
    dignity_req   = bool(constraints)

    task: dict = {
        "task_id":                   f"task-{claim_id}",
        "origin_claim_id":           claim_id,
        "task_type":                 _infer_task_type(contributions),
        "task_description":          claim.get("statement", ""),
        "task_status":               task_status,
        "required_capabilities":     capabilities,
        "open_conditions":           claim.get("missing_conditions", []),
        "required_conditions":       claim.get("required_state", []),
        "dignity_required":          dignity_req,
        "dignity_constraints":       constraints,
        "post_scarcity_guard":       guard_decision,
        "post_scarcity_guard_reason":guard_reason,
        "post_scarcity_guard_required": dignity_req,
        "created_from":              "dango_claim",
        "created_at":                claim.get("created_at", datetime.now(timezone.utc).isoformat()),
    }

    if guard_decision == "block":
        task["blocked_reason"] = guard_reason

    return task


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python claim_to_agent_task.py <claim.json> [--json]")
        sys.exit(1)

    path    = sys.argv[1]
    as_json = "--json" in sys.argv

    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        claim = json.load(f)

    checks            = run_guard(claim)
    guard_decision, guard_reason = final_decision(checks)

    task = transform(claim, guard_decision, guard_reason)

    if as_json:
        print(json.dumps(task, indent=2, ensure_ascii=False))
        return

    # Human-readable output
    ICON = {"pass": "✓", "block": "✗", "escalate": "⚠"}
    guard_icon = ICON.get(guard_decision, "?")

    print("=" * 60)
    print("CLAIM → AGENT TASK TRANSFORMATION — dango-ogi-bridge")
    print("=" * 60)
    print(f"\nSource claim:     {claim.get('claim_id')}")
    print(f"Task ID:          {task['task_id']}")
    print(f"Task type:        {task['task_type']}")
    print(f"Task status:      {task['task_status']}")
    print(f"\nPost-scarcity guard: {guard_icon} {guard_decision.upper()}")
    print(f"Reason:              {guard_reason}")

    print(f"\nRequired capabilities ({len(task['required_capabilities'])}):")
    for cap in task["required_capabilities"]:
        print(f"  → {cap}")

    print(f"\nOpen conditions ({len(task['open_conditions'])}):")
    for cond in task["open_conditions"]:
        print(f"  ✗ {cond}")

    print(f"\nDignity required:  {'YES' if task['dignity_required'] else 'NO'}")
    if task["dignity_constraints"]:
        for c in task["dignity_constraints"]:
            print(f"  · {c}")

    print()
    print("=" * 60)
    if guard_decision == "block":
        print("BLOCKED: Agent task cannot be created from this Claim.")
        print("Resolve the post-scarcity guard issue and rerun.")
    elif guard_decision == "escalate":
        print("ESCALATE: Human review required before agent task is activated.")
        print("Task is created in under_review status.")
    else:
        print("PASSED: Agent task created.")
        print("Eligible for OGI-compatible agent assignment.")
    print("=" * 60)


if __name__ == "__main__":
    main()
