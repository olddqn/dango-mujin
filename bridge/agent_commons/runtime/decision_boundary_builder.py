"""
decision_boundary_builder.py — Phase H-6: Decision Boundary Memory.

N-1.7 found a new boundary: Solution Candidate ┃ Execution Candidate, whose
atomic crossing is SELECTION. H-6 operationalises it. Hermes records WHERE a
candidate turned into a decision (selection / allocation / execution) — it
never makes, approves, or rejects a decision. It records the decision's
origin only.

Parallel to H-4:
  H-4: Observation ┃ Inference   (where inference begins)
  H-6: Candidate   ┃ Decision     (where decision begins)

Detection is NEGATION-AWARE: Hermes's own records are full of anti-decision
disclaimers ("none ranked", "no best gateway", "cannot select"). A naive
marker scan would false-positive on those. So a marker counts only when it is
NOT preceded (within a small window) by a negation. For clean Hermes memory,
every record resolves to `candidate_only` (no decision) — which is the correct
and meaningful result: no decision has entered the memory.

Input (read-only): the 6 memory sources (reflections, learnings, patterns,
evidence, inference boundaries, cooperation patterns).
Output: data/decision_boundaries.jsonl

CLI:
  python -m bridge.agent_commons.runtime.decision_boundary_builder
"""

from __future__ import annotations

import re
from typing import Any

from .store import (
    COOP_PATTERN_JSONL, DECISION_BOUNDARY_JSONL, EVIDENCE_JSONL,
    INFERENCE_BOUNDARY_JSONL, LEARNING_JSONL, PATTERN_JSONL, REFLECTION_JSONL,
    append_jsonl, base_invariants, next_id, read_jsonl,
)

# marker stems (regex). A decision marker means a candidate became a decision.
SELECTION_MARKERS = [r"recommend", r"\bbest\b", r"optimal", r"prefer",
                     r"\bmust\b", r"\bshould\b", r"priorit", r"\brank",
                     r"top choice"]
ALLOCATION_MARKERS = [r"\bdonate", r"\ballocate", r"\bdistribute", r"\bgrant"]
EXECUTION_MARKERS = [r"\bexecute", r"\bperform", r"\bsubmit", r"\bcontact",
                     r"\bdeploy", r"\bimplement"]

NEGATIONS = {"no", "not", "never", "cannot", "cant", "none", "without",
             "avoid", "avoids", "avoided", "forbidden", "forbid", "forbids",
             "prohibit", "prohibits", "prohibited", "refuse", "refuses"}

# Deferral-to-human verbs: "must be confirmed/reviewed by a human" defers TO a
# human — the opposite of Hermes deciding. A marker FOLLOWED (within a small
# window) by one of these is a safety clause, not a decision. Conceptually the
# mirror of NEGATIONS: negation = "do not", deferral = "a human must".
DEFERRALS = {"confirmed", "confirm", "reviewed", "review", "approved", "approve",
             "verified", "verify", "validated", "validate", "checked", "check",
             "decided", "decide", "consent", "consented", "authorised",
             "authorized", "authorise", "authorize", "human", "person", "owner",
             "people"}

# fields whose VALUES carry meaning (not boolean flags). We scan string values.
_SKIP_KEYS = {"event_hash", "appended_at"}


def _text_of(rec: dict[str, Any]) -> str:
    parts = []
    for k, v in rec.items():
        if k in _SKIP_KEYS:
            continue
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            parts.extend(str(x) for x in v if isinstance(x, str))
    return " ".join(parts)


def _nonneg_hits(text: str, patterns: list[str]) -> list[str]:
    """Marker hits that are neither negated (preceding) nor deferred-to-human
    (following). "no best gateway" (negation) and "must be confirmed by a human"
    (deferral) are both anti-decisions and do not count."""
    text = text.lower()
    hits: list[str] = []
    for pat in patterns:
        for m in re.finditer(pat, text):
            prev_words = re.findall(r"[a-z']+", text[:m.start()])[-3:]
            if any(w in NEGATIONS for w in prev_words):
                continue
            next_words = re.findall(r"[a-z']+", text[m.end():])[:4]
            if any(w in DEFERRALS for w in next_words):
                continue
            hits.append(m.group(0).strip())
    return hits


def _candidate_count(rec: dict[str, Any]) -> int:
    for k in ("candidate_dimension_count", "candidate_count"):
        if isinstance(rec.get(k), int):
            return rec[k]
    for k in ("supporting_reflections", "supporting_observations", "candidates"):
        if isinstance(rec.get(k), list):
            return len(rec[k])
    return 0


def _source_id(rec: dict[str, Any]) -> str | None:
    for k in ("boundary_id", "pattern_id", "evidence_id", "learning_id",
              "reflection_id"):
        if rec.get(k):
            return rec[k]
    return None


def _sources() -> list[dict[str, Any]]:
    out = []
    for path in (REFLECTION_JSONL, LEARNING_JSONL, PATTERN_JSONL, EVIDENCE_JSONL,
                 INFERENCE_BOUNDARY_JSONL, COOP_PATTERN_JSONL):
        out += read_jsonl(path)
    return out


def classify(rec: dict[str, Any]) -> dict[str, Any]:
    """Classify a source record's decision-boundary status (negation-aware)."""
    text = _text_of(rec)
    sel = _nonneg_hits(text, SELECTION_MARKERS)
    alloc = _nonneg_hits(text, ALLOCATION_MARKERS)
    exe = _nonneg_hits(text, EXECUTION_MARKERS)
    # execution > allocation > selection > candidate_only (escalation order)
    if exe:
        btype, marker = "execution", exe[0]
    elif alloc:
        btype, marker = "allocation", alloc[0]
    elif sel:
        btype, marker = "selection", sel[0]
    else:
        btype, marker = "candidate_only", None
    return {
        "boundary_type": btype,
        "decision_marker": marker,
        "decision_detected": btype != "candidate_only",
        "selection_present": bool(sel),
        "allocation_present": bool(alloc),
        "execution_present": bool(exe),
    }


def _already() -> set[str]:
    return {r.get("source_record") for r in read_jsonl(DECISION_BOUNDARY_JSONL)}


def build() -> list[dict[str, Any]]:
    """Record a decision boundary status for each source record (idempotent)."""
    done = _already()
    created = []
    for rec in _sources():
        sid = _source_id(rec)
        if not sid or sid in done:
            continue
        c = classify(rec)
        record = {
            "record_type": "decision_boundary",
            "decision_boundary_id": next_id("db", DECISION_BOUNDARY_JSONL),
            "source_record": sid,
            "candidate_count": _candidate_count(rec),
            **c,
            "human_review_required": True,
            "authority": "none",
            "cannot_define_need": True,
            "cannot_select": True,
            "cannot_allocate_resources": True,
            "cannot_execute": True,
            "decision_is_not_execution": True,
            "decision_is_not_policy": True,
            "status": "observed",
            **base_invariants(),
        }
        created.append(append_jsonl(DECISION_BOUNDARY_JSONL, record))
        done.add(sid)
    return created


def check_invariants() -> list[str]:
    """A decision_boundary record must never itself decide."""
    violations = []
    required = ("cannot_define_need", "cannot_select", "cannot_allocate_resources",
                "cannot_execute", "decision_is_not_execution", "decision_is_not_policy",
                "human_review_required")
    forbidden_self = ("selected_candidate", "recommendation", "chosen", "allocation_made")
    for r in read_jsonl(DECISION_BOUNDARY_JSONL):
        for f in required:
            if r.get(f) is not True:
                violations.append(f"{r.get('decision_boundary_id')}: missing/false {f}")
        for f in forbidden_self:
            if f in r:
                violations.append(f"{r.get('decision_boundary_id')}: self-decides ({f})")
        if r.get("authority") != "none":
            violations.append(f"{r.get('decision_boundary_id')}: authority not none")
    return violations


def main() -> None:
    print("=" * 64)
    print("HERMES DECISION BOUNDARY BUILDER — where candidate became decision")
    print('  "Decision is not execution." Hermes records the origin, never decides.')
    print("=" * 64)
    created = build()
    if not created:
        print("  (no new source records — append-only, idempotent)")
    fired = [r for r in created if r["decision_detected"]]
    for r in created:
        print(f"  ✓ {r['decision_boundary_id']} ← {r['source_record']} "
              f"[{r['boundary_type']}] decision_detected={r['decision_detected']}")
    print("-" * 64)
    print(f"  boundaries={len(read_jsonl(DECISION_BOUNDARY_JSONL))} "
          f"fired(decision_detected)={sum(1 for r in read_jsonl(DECISION_BOUNDARY_JSONL) if r['decision_detected'])} "
          f"violations={len(check_invariants())}")
    print("  Hermes can say WHERE a decision began. It never says WHAT to decide.")


if __name__ == "__main__":
    main()
