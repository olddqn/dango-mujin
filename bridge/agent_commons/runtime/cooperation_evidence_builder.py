"""
cooperation_evidence_builder.py — Phase H-5: Cooperation Evidence + report.

For each tentative cooperation pattern, gathers the cooperation reflections
(and the inference boundaries beneath them) that support it, so a human can
trace WHY the pattern was raised. Evidence is not fact and not proof. No actor
is named, ranked, recommended, or prioritised. Also writes the cooperation
memory report.

Input (read-only): memory/cooperation_patterns.jsonl,
cooperation_reflections.jsonl, inference_boundary_records.jsonl
Output: memory/cooperation_evidence_candidates.jsonl,
reports/cooperation_memory_report.md

CLI:
  python -m bridge.agent_commons.runtime.cooperation_evidence_builder
"""

from __future__ import annotations

from typing import Any

from .store import (
    COOP_EVIDENCE_JSONL, COOP_LEARNING_JSONL, COOP_MEMORY_REPORT_MD,
    COOP_PATTERN_JSONL, COOP_REFLECTION_JSONL, append_jsonl, base_invariants,
    next_id, read_jsonl, utc_now_iso, write_text,
)
from .cooperation_reflector import COOPERATION_INVARIANTS

# terms that would mean Hermes crossed from observation into governance.
FORBIDDEN_TERMS = [
    "best gateway", "best_gateway", "recommended gateway", "recommended_gateway",
    "connect gateway", "assign participant", "should cooperate", "must cooperate",
    "priority gateway", "priority_gateway", "optimal cooperation",
    "optimal_gateway",
]
_NEED_FIELDS = ("need_type", "need_id", "suggested_need_type", "need_approved")


def _already() -> set[str]:
    return {e.get("supports_pattern") for e in read_jsonl(COOP_EVIDENCE_JSONL)}


def build() -> list[dict[str, Any]]:
    """One evidence candidate per cooperation pattern (idempotent)."""
    reflections = read_jsonl(COOP_REFLECTION_JSONL)
    patterns = read_jsonl(COOP_PATTERN_JSONL)
    done = _already()
    created = []
    for pat in patterns:
        pid = pat.get("pattern_id")
        if not pid or pid in done:
            continue
        supporting_reflections = [r.get("reflection_id") for r
                                  in reflections
                                  if r.get("reflection_type") == "cooperation_observation"]
        supporting_boundaries = sorted({b for r in reflections
                                        for b in r.get("source_boundaries", [])})
        created.append(append_jsonl(COOP_EVIDENCE_JSONL, {
            "record_type": "cooperation_evidence_candidate",
            "evidence_id": next_id("coop-ev", COOP_EVIDENCE_JSONL),
            "supports_pattern": pid,
            "supporting_reflections": sorted(set(supporting_reflections)),
            "supporting_boundaries": supporting_boundaries,
            "evidence_is_not_fact": True,
            "candidate_only": True,
            **COOPERATION_INVARIANTS,
            **base_invariants(),
        }))
        done.add(pid)
    return created


def _all_cooperation_records() -> list[dict[str, Any]]:
    return (read_jsonl(COOP_REFLECTION_JSONL) + read_jsonl(COOP_LEARNING_JSONL)
            + read_jsonl(COOP_PATTERN_JSONL) + read_jsonl(COOP_EVIDENCE_JSONL))


def check_invariants() -> list[str]:
    """Cooperation invariant + forbidden-term check (used by Hermes review)."""
    violations: list[str] = []
    required = list(COOPERATION_INVARIANTS.keys())
    for rec in _all_cooperation_records():
        rid = rec.get("reflection_id") or rec.get("learning_id") \
            or rec.get("pattern_id") or rec.get("evidence_id")
        for f in _NEED_FIELDS:
            if f in rec:
                violations.append(f"{rid}: defines need ({f})")
        for f in required:
            if rec.get(f) is not True:
                violations.append(f"{rid}: missing/false {f}")
        blob = " ".join(str(v) for v in rec.values()).lower()
        for term in FORBIDDEN_TERMS:
            if term in blob:
                violations.append(f"{rid}: forbidden term '{term}'")
    return violations


def build_report() -> Any:
    refl = read_jsonl(COOP_REFLECTION_JSONL)
    learn = read_jsonl(COOP_LEARNING_JSONL)
    pat = read_jsonl(COOP_PATTERN_JSONL)
    ev = read_jsonl(COOP_EVIDENCE_JSONL)
    violations = check_invariants()
    human_reviewed = [r for r in _all_cooperation_records()
                      if r.get("human_reviewed") is True]

    md = f"""# Cooperation Memory Report

- Generated: {utc_now_iso()}
- Layer: `bridge/agent_commons/memory/` (advisory only · authority none · AI proposes, human decides)
- Hermes records that cooperation MAY exist. It does not create, propose,
  execute, or assign cooperation, and names / ranks / recommends no actor.

## Counts
| metric | value |
|---|---|
| Reflection Count | {len(refl)} |
| Learning Count | {len(learn)} |
| Pattern Count | {len(pat)} |
| Evidence Count | {len(ev)} |
| Violation Count | {len(violations)} |
| Human Reviewed Count | {len(human_reviewed)} (AI-generated; human review pending by design) |
| Cooperation Generated Count | 0 (Hermes never creates a cooperation) |

## Violations
{chr(10).join(f"- {v}" for v in violations) if violations else "- (none)"}

## Cooperation Reflections
{chr(10).join(f"- `{r['reflection_id']}` ← {r['source_voice']} · dims={r.get('candidate_dimension_count')} · {r['summary']}" for r in refl) or "- (none)"}

## Cooperation Learnings
{chr(10).join(f"- `{l['learning_id']}` [{l['learning_type']}] evidence={l['evidence_count']} · {l['statement']}" for l in learn) or "- (none)"}

## Cooperation Patterns (tentative hypotheses — not facts, not policy)
{chr(10).join(f"- `{p['pattern_id']}` ({p['status']}) {p['pattern_type']} evidence={p['evidence_count']} · {p['statement']}" for p in pat) or "- (none)"}

## Cooperation Evidence Candidates
{chr(10).join(f"- `{e['evidence_id']}` → {e['supports_pattern']} · reflections={e['supporting_reflections']} · boundaries={e['supporting_boundaries']}" for e in ev) or "- (none)"}

---

*A cooperation pattern is a hypothesis that cooperation MAY be relevant. No
actor is named, ranked, recommended, or prioritised. Hermes is a Memory Layer,
not a Governance Layer. Reach Gap is unresolved; this layer does not resolve it.*
"""
    return write_text(COOP_MEMORY_REPORT_MD, md)


def main() -> None:
    print("=" * 64)
    print("HERMES COOPERATION EVIDENCE BUILDER — pattern → evidence + report")
    print('  "Evidence is not fact." No actor named. No cooperation generated.')
    print("=" * 64)
    created = build()
    for e in created:
        print(f"  ✓ {e['evidence_id']} → {e['supports_pattern']} "
              f"reflections={e['supporting_reflections']}")
    if not created:
        print("  (no new patterns to support — append-only, idempotent)")
    path = build_report()
    print(f"  ✓ report: {path.name}")
    print(f"  violations={len(check_invariants())} · cooperation_generated=0")


if __name__ == "__main__":
    main()
