"""
inference_boundary_report.py — Phase H-4 report.

Writes reports/inference_boundary_report.md summarising where inference begins
across the candidates of a voice. Hermes is an Inference Boundary Observer; it
records "from here on this is a guess" and never crosses the boundary.

CLI:
  python -m bridge.agent_commons.runtime.inference_boundary_report
"""

from __future__ import annotations

from typing import Any

from .store import (
    INFERENCE_BOUNDARY_JSONL, INFERENCE_BOUNDARY_REPORT_MD, read_jsonl,
    utc_now_iso, write_text,
)
from .inference_boundary_builder import check_invariants


def _counts(records: list[dict[str, Any]]) -> dict[str, Any]:
    risk: dict[str, int] = {}
    for r in records:
        risk[r.get("scouter_risk", "?")] = risk.get(r.get("scouter_risk", "?"), 0) + 1
    return {
        "boundary_count": len(records),
        "direct_observation": sum(1 for r in records if r.get("boundary_type") == "direct_observation"),
        "inference": sum(1 for r in records if r.get("boundary_type") == "inference"),
        "speculation": sum(1 for r in records if r.get("boundary_type") == "speculation"),
        "need_owner_absent": sum(1 for r in records if r.get("need_owner_present") is False),
        "gateway_need": sum(1 for r in records if r.get("gateway_need") is True),
        "individual_need": sum(1 for r in records if r.get("individual_need") is True),
        "scouter_risk_breakdown": dict(sorted(risk.items())),
        "requiring_human_review": sum(1 for r in records if r.get("boundary_requires_human_review") is True),
    }


def build_report() -> tuple[Any, dict[str, Any]]:
    records = read_jsonl(INFERENCE_BOUNDARY_JSONL)
    c = _counts(records)
    violations = check_invariants()
    v6 = [r for r in records if r.get("voice_id") == "voice-006"]

    rows = "\n".join(
        f"| `{r['boundary_id']}` | {r['candidate']} | {r['boundary_type']} | "
        f"{r['need_owner_present']} | {r.get('gateway_need')} | {r.get('individual_need')} | "
        f"{r['distance_from_voice']} | {r['scouter_risk']} | {r['boundary_requires_human_review']} |"
        for r in records) or "| (none) | | | | | | | | |"

    v6_lines = "\n".join(
        f"- `{r['candidate']}` [{r['boundary_type']}] — last direct obs: "
        f"\"{r['last_direct_observation']}\" → first inference: "
        f"\"{r['first_inference'] or '— (none; direct)'}\" (risk={r['scouter_risk']})"
        for r in v6) or "- (none)"

    md = f"""# Inference Boundary Report

- Generated: {utc_now_iso()}
- Layer: `bridge/agent_commons/memory/` (advisory only · authority none · AI proposes, human decides)
- Hermes is an **Inference Boundary Observer**: it records where inference began
  ("from here on, this is a guess"). It does not define / approve / reject a Need.
- Source of the inference: the human review (`docs/NEED_DEFINITION_REVIEW.md`).
  Hermes records the boundary; it invents no inference.

## Counts
| metric | value |
|---|---|
| Boundary Count | {c['boundary_count']} |
| Direct Observation Count | {c['direct_observation']} |
| Inference Count | {c['inference']} |
| Speculation Count | {c['speculation']} |
| Need Owner Absent Count | {c['need_owner_absent']} |
| Gateway Need Count | {c['gateway_need']} |
| Individual Need Count | {c['individual_need']} |
| Boundary Requiring Human Review | {c['requiring_human_review']} |

## Scouter Risk Breakdown
{chr(10).join(f"- {k}: {v}" for k, v in c['scouter_risk_breakdown'].items()) or "- (none)"}

## Invariant Violations
{chr(10).join(f"- {v}" for v in violations) if violations else "- (none)"}

## All Boundaries
| boundary | candidate | type | owner_present | gateway | individual | distance | risk | needs_review |
|---|---|---|---|---|---|---|---|---|
{rows}

## voice-006 Boundary Analysis
{v6_lines}

> The inference boundary for voice-006 falls between B (volunteer, direct) and
> C (translation, inference): direct observation ends at JAR's stated resource
> needs; inference begins when JAR's activity areas are read as individual
> needs. Scouter risk appears exactly at that line.

---

*Hermes records "from here on, this is a guess." It defines no Need, selects no
Gateway, generates no Task, allocates no resources. Reach Gap is unresolved;
this layer does not claim to resolve it.*
"""
    path = write_text(INFERENCE_BOUNDARY_REPORT_MD, md)
    return path, {**c, "violations": violations}


def main() -> None:
    print("=" * 64)
    print("INFERENCE BOUNDARY REPORT BUILDER")
    print("=" * 64)
    path, summary = build_report()
    print(f"  ✓ wrote {path.name}")
    print(f"  boundaries={summary['boundary_count']} "
          f"(direct={summary['direct_observation']} "
          f"inference={summary['inference']} speculation={summary['speculation']}) "
          f"risk={summary['scouter_risk_breakdown']} "
          f"violations={len(summary['violations'])}")


if __name__ == "__main__":
    main()
