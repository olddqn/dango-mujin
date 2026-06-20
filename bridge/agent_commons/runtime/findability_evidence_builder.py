"""
findability_evidence_builder.py — Phase F-1: Findability Event → Evidence.

Turns Findability Events into evidence candidates. Evidence here is a record
that a discovery *happened*; it is explicitly NOT marketing, NOT growth, NOT
recruitment. Those denials are required flags on every evidence record.

This module also hosts the shared Findability invariant checker used by the
Hermes reviewer: it scans every findability record (reflections, learnings,
patterns, evidence) for forbidden growth/outreach vocabulary and forbidden
field keys, and confirms the required refusal flags and passivity.

Input (read-only): data/findability_events.jsonl
Output: data/findability_evidence.jsonl

CLI:
  python -m bridge.agent_commons.runtime.findability_evidence_builder
"""

from __future__ import annotations

import re
from typing import Any

from .store import (
    FINDABILITY_EVENT_JSONL, FINDABILITY_EVIDENCE_JSONL,
    FINDABILITY_LEARNING_JSONL, FINDABILITY_PATTERN_JSONL,
    FINDABILITY_REFLECTION_JSONL, append_jsonl, base_invariants, next_id,
    read_jsonl,
)
from .findability_reflector import FINDABILITY_INVARIANTS
from .findability_pattern_builder import FORBIDDEN_PATTERN_KEYS

# vocabulary that would mean the layer drifted from observation into outreach /
# growth / recruitment. Scanned over string VALUES only (never keys), so the
# boolean invariant flags like findability_is_not_outreach do not self-trip.
FORBIDDEN_TERMS = [
    r"\boutreach\b", r"\brecruit", r"\bacquisition\b", r"\bacquire\b",
    r"lead generation", r"\blead gen\b", r"growth funnel", r"growth strategy",
    r"conversion optimization", r"conversion optimisation", r"recommended channel",
    r"best channel", r"marketing campaign", r"\bcold (call|email|contact)",
]
FORBIDDEN_FIELD_KEYS = FORBIDDEN_PATTERN_KEYS  # best_channel, ...strategy, etc.

# evidence-specific required denials
EVIDENCE_DENIALS = {
    "evidence_is_not_marketing": True,
    "evidence_is_not_growth": True,
    "evidence_is_not_recruitment": True,
}


def _already() -> set[str]:
    return {r.get("source_event") for r in read_jsonl(FINDABILITY_EVIDENCE_JSONL)}


def build() -> list[dict[str, Any]]:
    """One evidence record per Findability Event (idempotent by source_event)."""
    done = _already()
    created = []
    for ev in read_jsonl(FINDABILITY_EVENT_JSONL):
        eid = ev.get("event_id")
        if not eid or eid in done:
            continue
        record = {
            "record_type": "findability_evidence",
            "evidence_id": next_id("find-ev", FINDABILITY_EVIDENCE_JSONL),
            "source_event": eid,
            "claim": "a discovery event occurred",
            "discoverer_type": ev.get("discoverer_type"),
            "source_channel": ev.get("source_channel"),
            "passive_discovery": not (ev.get("contact_initiated_by_mujin")
                                      or ev.get("outreach_used")),
            "evidence_is_not_fact": True,
            "evidence_is_not_proof": True,
            **EVIDENCE_DENIALS,
            **FINDABILITY_INVARIANTS,
            **base_invariants(),
        }
        created.append(append_jsonl(FINDABILITY_EVIDENCE_JSONL, record))
        done.add(eid)
    return created


# ── shared checker (used by hermes_reviewer) ────────────────────────────────

def _all_findability_records() -> list[dict[str, Any]]:
    out = []
    for path in (FINDABILITY_REFLECTION_JSONL, FINDABILITY_LEARNING_JSONL,
                 FINDABILITY_PATTERN_JSONL, FINDABILITY_EVIDENCE_JSONL):
        out += read_jsonl(path)
    return out


def _string_values(rec: dict[str, Any]) -> str:
    parts = []
    for k, v in rec.items():
        if k in ("event_hash", "appended_at"):
            continue
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            parts.extend(str(x) for x in v if isinstance(x, str))
    return " ".join(parts).lower()


def detect_forbidden_terms(rec: dict[str, Any]) -> list[str]:
    text = _string_values(rec)
    hits = []
    for pat in FORBIDDEN_TERMS:
        if re.search(pat, text):
            hits.append(pat.strip("\\b"))
    return hits


def check_invariants() -> list[str]:
    """Findability records must stay observation; never outreach/growth/recruit."""
    violations = []
    rid_keys = ("reflection_id", "learning_id", "pattern_id", "evidence_id")
    for r in _all_findability_records():
        rid = next((r[k] for k in rid_keys if r.get(k)), "?")
        # required refusal flags
        for f in FINDABILITY_INVARIANTS:
            if r.get(f) is not True:
                violations.append(f"{rid}: missing/false {f}")
        # no forbidden growth/strategy field keys
        for k in FORBIDDEN_FIELD_KEYS:
            if k in r:
                violations.append(f"{rid}: forbidden field key {k}")
        # no forbidden vocabulary in string content
        for hit in detect_forbidden_terms(r):
            violations.append(f"{rid}: forbidden term '{hit}'")
        # discovery must be passive (Mujin never initiated)
        if r.get("passive_discovery") is False:
            violations.append(f"{rid}: passive_discovery is False (Mujin initiated)")
        if r.get("source_contact_initiated_by_mujin") is True:
            violations.append(f"{rid}: Mujin initiated contact")
        if r.get("source_outreach_used") is True:
            violations.append(f"{rid}: outreach was used")
        # evidence-specific denials
        if r.get("record_type") == "findability_evidence":
            for f in EVIDENCE_DENIALS:
                if r.get(f) is not True:
                    violations.append(f"{rid}: missing/false {f}")
    return violations


def main() -> None:
    print("=" * 64)
    print("HERMES FINDABILITY EVIDENCE BUILDER — discovery happened (not marketing)")
    print('  evidence_is_not_marketing / not_growth / not_recruitment (required).')
    print("=" * 64)
    n_events = len(read_jsonl(FINDABILITY_EVENT_JSONL))
    created = build()
    if n_events == 0:
        print("  findability events = 0 → no evidence. 0 is an observation.")
    for r in created:
        print(f"  ✓ {r['evidence_id']} ← {r['source_event']} [{r['source_channel']}]")
    print("-" * 64)
    print(f"  evidence={len(read_jsonl(FINDABILITY_EVIDENCE_JSONL))} "
          f"violations={len(check_invariants())}")
    print("Evidence that a discovery happened — not marketing, growth, or recruitment.")


if __name__ == "__main__":
    main()
