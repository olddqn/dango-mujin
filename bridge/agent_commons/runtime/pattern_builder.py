"""
pattern_builder.py — Phase H-2.5: Reflection → Learning → Pattern.

Extracts reusable Learnings from Reflections, then tentative Pattern
Candidates from Learnings. A Pattern is NOT a fact — it is a hypothesis that
requires human review. Nothing here defines a Need, selects a Gateway/Agent,
generates a Task, forms a Cooperation, or makes Policy.

Also writes reports/hermes_memory_report.md.

CLI:
  python -m bridge.agent_commons.runtime.pattern_builder
"""

from __future__ import annotations

from typing import Any

from .store import (
    LEARNING_JSONL, MEMORY_REPORT_MD, OBSERVATION_JSONL, PATTERN_JSONL,
    REFLECTION_JSONL, append_jsonl, base_invariants, next_id, read_jsonl,
    utc_now_iso, write_text,
)

# category → reusable learning statement (advisory, not authority)
_LEARNING_STATEMENTS = {
    "gateway_voice":      "Public voices may originate from a gateway/intermediary rather than a direct beneficiary.",
    "intermediary_voice": "Some voices are relayed by intermediaries rather than spoken by the need owner.",
    "public_call":        "Public-call voices may lack a clearly present need owner.",
    "direct_voice":       "Some voices appear to be direct first-person appeals (consent review required).",
    "need_owner_absent":  "Need owner may be absent from a public voice.",
}
# categories that indicate an intermediary origin (need owner not the speaker)
_INTERMEDIARY_CATS = {"gateway_voice", "intermediary_voice", "public_call"}

# fields that would indicate a Need was defined (must never appear)
_NEED_FIELDS = ("need_type", "need_id", "suggested_need_type", "need_approved")


# ── Reflection → Learning ─────────────────────────────────────────────────────

def _existing_learning_categories() -> set[str]:
    return {l.get("category") for l in read_jsonl(LEARNING_JSONL)}


def build_learnings() -> list[dict[str, Any]]:
    """Aggregate reflections into learnings by category (idempotent by category)."""
    reflections = read_jsonl(REFLECTION_JSONL)
    counts: dict[str, int] = {}
    for r in reflections:
        for c in r.get("categories", []):
            counts[c] = counts.get(c, 0) + 1
    existing = _existing_learning_categories()
    created = []
    for cat in sorted(counts):
        if cat in existing:
            continue
        record = {
            "record_type": "learning",
            "learning_id": next_id("learn", LEARNING_JSONL),
            "category": cat,
            "statement": _LEARNING_STATEMENTS.get(cat, f"Observed category: {cat}."),
            "evidence_count": counts[cat],
            "human_review_required": True,
            "learning_is_not_authority": True,
            "learning_is_not_policy": True,
            "learning_is_not_decision": True,
            **base_invariants(),
        }
        created.append(append_jsonl(LEARNING_JSONL, record))
    return created


# ── Learning → Pattern ────────────────────────────────────────────────────────

def _existing_pattern_keys() -> set[str]:
    return {p.get("pattern_key") for p in read_jsonl(PATTERN_JSONL)}


def build_patterns() -> list[dict[str, Any]]:
    """Generate tentative pattern candidates from learnings (idempotent)."""
    learnings = {l["category"]: l for l in read_jsonl(LEARNING_JSONL)}
    existing = _existing_pattern_keys()
    created = []

    intermediary_evidence = sum(
        learnings[c]["evidence_count"] for c in _INTERMEDIARY_CATS if c in learnings)
    if intermediary_evidence >= 3 and "intermediary_origin" not in existing:
        created.append(append_jsonl(PATTERN_JSONL, {
            "record_type": "pattern",
            "pattern_id": next_id("pat", PATTERN_JSONL),
            "pattern_key": "intermediary_origin",
            "statement": "Public voices tend to originate from intermediaries; "
                         "the need owner is often absent from the voice.",
            "evidence_count": intermediary_evidence,
            "status": "tentative",
            "pattern_is_not_fact": True,
            "pattern_requires_human_review": True,
            "pattern_is_not_policy": True,
            **base_invariants(),
        }))
    return created


# ── invariant check + report ──────────────────────────────────────────────────

def check_invariants() -> list[str]:
    violations: list[str] = []
    for rec in read_jsonl(REFLECTION_JSONL):
        for f in _NEED_FIELDS:
            if f in rec:
                violations.append(f"{rec.get('reflection_id')}: defines need ({f})")
        for f in ("reflection_is_not_decision", "reflection_is_not_policy"):
            if rec.get(f) is not True:
                violations.append(f"{rec.get('reflection_id')}: missing/false {f}")
    for rec in read_jsonl(LEARNING_JSONL):
        if rec.get("learning_is_not_authority") is not True:
            violations.append(f"{rec.get('learning_id')}: learning_is_not_authority not true")
    for rec in read_jsonl(PATTERN_JSONL):
        for f in ("pattern_is_not_fact", "pattern_requires_human_review", "pattern_is_not_policy"):
            if rec.get(f) is not True:
                violations.append(f"{rec.get('pattern_id')}: missing/false {f}")
        if rec.get("status") != "tentative":
            violations.append(f"{rec.get('pattern_id')}: status not tentative")
    return violations


def build_memory_report() -> tuple[Any, dict[str, Any]]:
    obs = read_jsonl(OBSERVATION_JSONL)
    refl = read_jsonl(REFLECTION_JSONL)
    learn = read_jsonl(LEARNING_JSONL)
    pat = read_jsonl(PATTERN_JSONL)
    tentative = [p for p in pat if p.get("status") == "tentative"]
    human_reviewed = [r for r in refl if r.get("human_reviewed") is True]
    violations = check_invariants()

    md = f"""# Hermes Memory Report

- Generated: {utc_now_iso()}
- Layer: `bridge/agent_commons/memory/` (advisory only · authority none · AI proposes, human decides)
- Hermes records *what was learned*, not *what to do*. Pattern is hypothesis, not fact.

## Counts
| metric | value |
|---|---|
| Observation Count | {len(obs)} |
| Reflection Count | {len(refl)} |
| Learning Count | {len(learn)} |
| Pattern Count | {len(pat)} |
| Tentative Pattern Count | {len(tentative)} |
| Human Reviewed Count | {len(human_reviewed)} (reflections are AI-generated; human review pending by design) |

## Invariant Violations
{chr(10).join(f"- {v}" for v in violations) if violations else "- (none)"}

## Reflections
{chr(10).join(f"- `{r['reflection_id']}` ← {r['source_observation']} ({r['source_voice']}) · confidence={r.get('confidence')} · {r['reflection']}" for r in refl) or "- (none)"}

## Learnings (reusable, advisory — not authority)
{chr(10).join(f"- `{l['learning_id']}` [{l['category']}] evidence={l['evidence_count']} · {l['statement']}" for l in learn) or "- (none)"}

## Pattern Candidates (tentative hypotheses — not facts)
{chr(10).join(f"- `{p['pattern_id']}` ({p['status']}) evidence={p['evidence_count']} · {p['statement']}" for p in pat) or "- (none)"}

## voice-006 chain
{_chain_line()}

---

*A Pattern is not a fact and not a policy; it requires human review. Hermes is
an Observer, not a Planner / Coordinator / Policy Maker. Reach Gap is
unresolved; this layer does not claim to resolve it.*
"""
    path = write_text(MEMORY_REPORT_MD, md)
    return path, {
        "observation": len(obs), "reflection": len(refl), "learning": len(learn),
        "pattern": len(pat), "tentative": len(tentative),
        "human_reviewed": len(human_reviewed), "violations": violations,
    }


def _chain_line() -> str:
    """Trace voice-006 → obs-006 → refl → learn → pat for verification."""
    refl = next((r for r in read_jsonl(REFLECTION_JSONL)
                 if r.get("source_voice") == "voice-006"), None)
    learn = next((l for l in read_jsonl(LEARNING_JSONL)
                  if l.get("category") == "gateway_voice"), None)
    pat = next((p for p in read_jsonl(PATTERN_JSONL)
                if p.get("pattern_key") == "intermediary_origin"), None)
    return (f"`voice-006` → `obs-006` → "
            f"`{refl['reflection_id'] if refl else '—'}` → "
            f"`{learn['learning_id'] if learn else '—'}` → "
            f"`{pat['pattern_id'] if pat else '—'}`")


def main() -> None:
    print("=" * 64)
    print("HERMES PATTERN BUILDER — reflection → learning → pattern")
    print('  "Pattern is not a fact." "Pattern requires human review."')
    print("=" * 64)
    learnings = build_learnings()
    patterns = build_patterns()
    for l in learnings:
        print(f"  ✓ {l['learning_id']} [{l['category']}] evidence={l['evidence_count']}")
    for p in patterns:
        print(f"  ✓ {p['pattern_id']} ({p['status']}) evidence={p['evidence_count']} · {p['statement']}")
    if not learnings and not patterns:
        print("  (no new learnings/patterns — append-only, idempotent)")
    path, summary = build_memory_report()
    print(f"  ✓ report: {path.name}")
    print("-" * 64)
    print(f"  reflections={summary['reflection']} learnings={summary['learning']} "
          f"patterns={summary['pattern']} (tentative={summary['tentative']}) "
          f"violations={len(summary['violations'])}")
    print("  Pattern is hypothesis, not fact. Humans decide.")


if __name__ == "__main__":
    main()
