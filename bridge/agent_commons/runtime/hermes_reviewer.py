"""
hermes_reviewer.py — Hermes as Safety Reviewer.

Hermes confirms that the Agent Commons has not crossed any line:
  - no auto-approval, no auto-execution
  - no Need was defined / approved / rejected
  - no Task was auto-assigned to an agent
  - no invariant violations in observations / tasks / agent registry

Hermes is NOT the Reviewer of Record (a human is). Hermes only flags. It
proposes; humans decide.

CLI:
  python -m bridge.agent_commons.runtime.hermes_reviewer
"""

from __future__ import annotations

from typing import Any

from .store import (
    AGENT_REGISTRY_JSONL, OBSERVATION_JSONL, TASK_JSONL, read_jsonl,
)
from .agent_registry import AGENT_REFUSALS

# fields that would indicate a Need was defined (must never appear)
_NEED_DEFINITION_FIELDS = ("need_type", "need_id", "suggested_need_type",
                           "need_owner_decided", "need_approved")


def run_review() -> dict[str, Any]:
    """Return a review result with any invariant violations (should be empty)."""
    violations: list[str] = []
    obs = read_jsonl(OBSERVATION_JSONL)
    tasks = read_jsonl(TASK_JSONL)
    agents = read_jsonl(AGENT_REGISTRY_JSONL)

    # 1. observations: no need definition; required flags true
    for o in obs:
        for f in _NEED_DEFINITION_FIELDS:
            if f in o:
                violations.append(f"{o.get('observation_id')}: defines a need ({f})")
        for f in ("voice_is_not_need", "observation_is_not_decision",
                  "candidate_only", "human_confirmation_required"):
            if o.get(f) is not True:
                violations.append(f"{o.get('observation_id')}: missing/false {f}")
        if o.get("defines_need") is not False or o.get("selects_gateway") is not False:
            violations.append(f"{o.get('observation_id')}: defines_need/selects_gateway not false")

    # 2. tasks: never assigned; required flags true
    for t in tasks:
        if t.get("assigned_agent") not in (None, ""):
            violations.append(f"{t.get('task_id')}: has an assigned_agent (assignment)")
        for f in ("task_is_not_assignment", "task_is_not_order",
                  "agent_participation_is_voluntary", "human_review_required"):
            if t.get(f) is not True:
                violations.append(f"{t.get('task_id')}: missing/false {f}")

    # 3. agents: required refusals true; no real connection / execution this phase
    for a in agents:
        for f in AGENT_REFUSALS:
            if a.get(f) is not True:
                violations.append(f"{a.get('agent_id')}: missing/false {f}")
        if a.get("real_connection") is not False:
            violations.append(f"{a.get('agent_id')}: real_connection not false")
        if a.get("execution_enabled") is not False:
            violations.append(f"{a.get('agent_id')}: execution_enabled not false")

    # 4. evidence candidates (H-3.5): no need def; required refusal flags
    from .evidence_builder import check_invariants as _ev_check
    from .store import (read_jsonl as _rj, EVIDENCE_JSONL as _EV,
                        INFERENCE_BOUNDARY_JSONL as _IB)
    evidence = _rj(_EV)
    violations += _ev_check()

    # 4b. inference boundaries (H-4): records where inference began; no need def
    from .inference_boundary_builder import check_invariants as _ib_check
    boundaries = _rj(_IB)
    violations += _ib_check()

    # 5. global auto-action guard (no record enables auto anything)
    for rec in obs + tasks + agents + evidence + boundaries:
        for f in ("auto_approval", "auto_execution", "auto_needification",
                  "auto_task_assignment", "execution_allowed"):
            if rec.get(f) is True:
                violations.append(f"{rec.get('record_type')}: {f} is True")

    return {
        "observation_count": len(obs),
        "task_candidate_count": len(tasks),
        "agent_count": len(agents),
        "evidence_count": len(evidence),
        "inference_boundary_count": len(boundaries),
        "checks": [
            "no Need defined / approved / rejected",
            "no Task auto-assigned to an agent",
            "all agents carry refusal flags; no real connection / execution",
            "evidence candidates: not fact, not proof, no need definition",
            "inference boundaries: record where inference begins, define no need",
            "no auto-approval / auto-execution / auto-needification",
        ],
        "violations": violations,
        "passed": not violations,
        "reviewer_of_record": "human (Hermes only flags; it does not decide)",
    }


def main() -> None:
    print("=" * 64)
    print("HERMES SAFETY REVIEWER — flags only; human is the Reviewer of Record")
    print("=" * 64)
    r = run_review()
    print(f"  observations: {r['observation_count']} | tasks: {r['task_candidate_count']} "
          f"| agents: {r['agent_count']}")
    for c in r["checks"]:
        print(f"  · check: {c}")
    if r["passed"]:
        print("  ✓ no invariant violations detected")
    else:
        print("  ✗ VIOLATIONS:")
        for v in r["violations"]:
            print(f"    - {v}")
    print("-" * 64)
    print("Hermes proposes. Humans decide.")


if __name__ == "__main__":
    main()
