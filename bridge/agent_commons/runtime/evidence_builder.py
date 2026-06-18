"""
evidence_builder.py — Phase H-3.5: Pattern → Evidence Candidate.

Completes the chain:
  Voice → Observation → Reflection → Learning → Pattern → Evidence Candidate

An Evidence Candidate is NOT a fact and NOT a proof. It is the set of
observations / reflections / learnings that SUPPORT a pattern, gathered so a
human can trace WHY a pattern was generated. Hermes is an Observer — it
organises supporting observations; it does not define needs, select cases,
assign tasks, allocate resources, or decide anything.

Note on file names: this reads the ACTUAL memory files created in H-2.5
(memory/reflection_records.jsonl, learning_records.jsonl, pattern_records.jsonl;
data/observation_candidates.jsonl). The H-3.5 spec used different illustrative
names; reality is followed here.

CLI:
  python -m bridge.agent_commons.runtime.evidence_builder
"""

from __future__ import annotations

from typing import Any

from .store import (
    EVIDENCE_JSONL, LEARNING_JSONL, PATTERN_JSONL, REFLECTION_JSONL,
    append_jsonl, base_invariants, next_id, read_jsonl,
)

# pattern_key → the reflection/learning categories that contributed to it.
# (Mirrors pattern_builder's _INTERMEDIARY_CATS for the intermediary_origin pattern.)
_PATTERN_SOURCE_CATEGORIES = {
    "intermediary_origin": {"gateway_voice", "intermediary_voice", "public_call"},
}

# fields that would indicate a Need was defined (must never appear)
_NEED_FIELDS = ("need_type", "need_id", "suggested_need_type", "need_approved")


def _evidence_flags() -> dict[str, Any]:
    return {
        "candidate_only": True,
        "evidence_is_not_fact": True,
        "pattern_is_not_proven": True,
        "evidence_is_not_policy": True,
        "evidence_is_not_decision": True,
        "cannot_define_need": True,
        "cannot_select_case": True,
        "cannot_assign_task": True,
        "cannot_allocate_resources": True,
        "human_review_required": True,
        "human_reviewed": False,   # honest: AI-gathered, not yet human-reviewed
    }


def _already_built() -> set[str]:
    return {e.get("pattern_id") for e in read_jsonl(EVIDENCE_JSONL)}


def build() -> list[dict[str, Any]]:
    """Build an Evidence Candidate for each pattern (idempotent by pattern_id)."""
    reflections = read_jsonl(REFLECTION_JSONL)
    learnings = read_jsonl(LEARNING_JSONL)
    patterns = read_jsonl(PATTERN_JSONL)
    done = _already_built()
    created = []

    for pat in patterns:
        pid = pat.get("pattern_id")
        if not pid or pid in done:
            continue
        cats = _PATTERN_SOURCE_CATEGORIES.get(pat.get("pattern_key"), set())

        supporting_reflections, supporting_observations = [], []
        for r in reflections:
            if set(r.get("categories", [])) & cats:
                supporting_reflections.append(r.get("reflection_id"))
                if r.get("source_observation"):
                    supporting_observations.append(r.get("source_observation"))
        supporting_learning = [l.get("learning_id") for l in learnings
                               if l.get("category") in cats]

        record = {
            "record_type": "evidence_candidate",
            "evidence_id": next_id("evcand", EVIDENCE_JSONL),
            "pattern_id": pid,
            "pattern_statement": pat.get("statement", ""),
            "supporting_observations": sorted(set(supporting_observations)),
            "supporting_reflections": sorted(set(supporting_reflections)),
            "supporting_learning": sorted(set(supporting_learning)),
            "support_count": len(set(supporting_observations)),
            **_evidence_flags(),
            **base_invariants(),
        }
        created.append(append_jsonl(EVIDENCE_JSONL, record))
        done.add(pid)
    return created


def coverage() -> dict[str, Any]:
    """Pattern coverage by evidence (for the report)."""
    patterns = read_jsonl(PATTERN_JSONL)
    evidence = read_jsonl(EVIDENCE_JSONL)
    with_ev = {e.get("pattern_id") for e in evidence}
    pats_with = [p for p in patterns if p.get("pattern_id") in with_ev]
    pats_without = [p for p in patterns if p.get("pattern_id") not in with_ev]
    human_reviewed = [e for e in evidence if e.get("human_reviewed") is True]
    return {
        "evidence_count": len(evidence),
        "pattern_count": len(patterns),
        "patterns_with_evidence": len(pats_with),
        "patterns_without_evidence": len(pats_without),
        "evidence_coverage": (f"{len(pats_with)}/{len(patterns)}"
                              if patterns else "0/0"),
        "human_reviewed_evidence_count": len(human_reviewed),
    }


def check_invariants() -> list[str]:
    violations: list[str] = []
    required = ("candidate_only", "evidence_is_not_fact", "pattern_is_not_proven",
                "evidence_is_not_policy", "evidence_is_not_decision",
                "cannot_define_need", "cannot_select_case", "cannot_assign_task",
                "cannot_allocate_resources", "human_review_required")
    for e in read_jsonl(EVIDENCE_JSONL):
        for f in _NEED_FIELDS:
            if f in e:
                violations.append(f"{e.get('evidence_id')}: defines need ({f})")
        for f in required:
            if e.get(f) is not True:
                violations.append(f"{e.get('evidence_id')}: missing/false {f}")
        if e.get("authority") != "none":
            violations.append(f"{e.get('evidence_id')}: authority not none")
    return violations


def main() -> None:
    print("=" * 64)
    print("HERMES EVIDENCE BUILDER — pattern → evidence candidate")
    print('  "Evidence is not fact." "Pattern is not proven." advisory · human-reviewed')
    print("=" * 64)
    created = build()
    if not created:
        print("  (no new patterns to support — append-only, idempotent)")
    for e in created:
        print(f"  ✓ {e['evidence_id']} → {e['pattern_id']} | "
              f"obs={e['supporting_observations']} | "
              f"refl={e['supporting_reflections']} | learn={e['supporting_learning']}")
    cov = coverage()
    print("-" * 64)
    print(f"  evidence={cov['evidence_count']} coverage={cov['evidence_coverage']} "
          f"violations={len(check_invariants())}")
    print("  Evidence organises support for a hypothesis. It proves nothing. Humans decide.")


if __name__ == "__main__":
    main()
