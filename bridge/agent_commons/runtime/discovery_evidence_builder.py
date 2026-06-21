"""
discovery_evidence_builder.py — Phase F-2: Discovery Event → Evidence.

Turns real discovery reflections into evidence candidates. Evidence records the
existence of a discovery event — never a ranking of discoverers, a ranking of
channels, or a recommendation.

This module also hosts the shared Discovery invariant checker used by the Hermes
reviewer: it scans every discovery record for forbidden growth/marketing/
recruitment/recommendation vocabulary and forbidden field keys, confirms
required refusal flags, and refuses any inferred/predicted/recommended/target
discoverer type.

Input (read-only): data/discovery_reflections.jsonl
Output: data/discovery_evidence.jsonl

CLI:
  python -m bridge.agent_commons.runtime.discovery_evidence_builder
"""

from __future__ import annotations

import re
from typing import Any

from .store import (
    DISCOVERY_EVIDENCE_JSONL, DISCOVERY_LEARNINGS_JSONL, DISCOVERY_PATTERNS_JSONL,
    DISCOVERY_REFLECTIONS_JSONL, append_jsonl, base_invariants, next_id, read_jsonl,
)
from .discovery_reflector import (
    DISCOVERY_INVARIANTS, ALLOWED_DISCOVERER_TYPES, FORBIDDEN_DISCOVERER_TYPES,
)
from .discovery_pattern_builder import FORBIDDEN_PATTERN_KEYS

# vocabulary meaning the layer drifted from observation into growth / marketing /
# recruitment / recommendation. Scanned over string VALUES only (never keys).
FORBIDDEN_TERMS = [
    r"\bgrowth\b", r"\bmarketing\b", r"\brecruitment\b", r"\brecruit",
    r"\bacquisition\b", r"\bacquire\b", r"\boutreach\b", r"\brecommended\b",
    r"\bpriority\b", r"\bbest\b", r"\bconversion\b", r"growth funnel",
]
# forbidden field keys: ranking/recommendation of surface or actor
FORBIDDEN_FIELD_KEYS = ("recommended_surface", "ranked_surface", "priority_surface",
                        "recommended_actor", "ranked_actor", *FORBIDDEN_PATTERN_KEYS)

# evidence-specific required denials
EVIDENCE_DENIALS = {
    "evidence_is_not_ranking": True,
    "evidence_is_not_recommendation": True,
}


def _already() -> set[str]:
    return {r.get("source_event") for r in read_jsonl(DISCOVERY_EVIDENCE_JSONL)}


def build() -> list[dict[str, Any]]:
    """One evidence record per real discovery reflection (idempotent)."""
    done = _already()
    created = []
    for r in read_jsonl(DISCOVERY_REFLECTIONS_JSONL):
        eid = r.get("source_event")
        if not eid or eid in done:
            continue
        record = {
            "record_type": "discovery_evidence",
            "evidence_id": next_id("disc-ev", DISCOVERY_EVIDENCE_JSONL),
            "source_event": eid,
            "claim": "a verified discovery event occurred",
            "discoverer_type": r.get("discoverer_type"),
            "surface": r.get("surface"),
            "object": r.get("object"),
            "observed_at": r.get("observed_at"),
            "evidence_is_not_fact": True,
            "evidence_is_not_proof": True,
            **EVIDENCE_DENIALS,
            **DISCOVERY_INVARIANTS,
            **base_invariants(),
        }
        created.append(append_jsonl(DISCOVERY_EVIDENCE_JSONL, record))
        done.add(eid)
    return created


# ── shared checker (used by hermes_reviewer) ────────────────────────────────

def _all_discovery_records() -> list[dict[str, Any]]:
    out = []
    for path in (DISCOVERY_REFLECTIONS_JSONL, DISCOVERY_LEARNINGS_JSONL,
                 DISCOVERY_PATTERNS_JSONL, DISCOVERY_EVIDENCE_JSONL):
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
    return [pat.strip("\\b") for pat in FORBIDDEN_TERMS if re.search(pat, text)]


def check_invariants() -> list[str]:
    """Discovery records must stay observation; never growth/marketing/
    recruitment/recommendation, and never an invented discoverer type."""
    violations = []
    rid_keys = ("reflection_id", "learning_id", "pattern_id", "evidence_id")
    for r in _all_discovery_records():
        rid = next((r[k] for k in rid_keys if r.get(k)), "?")
        for f in DISCOVERY_INVARIANTS:
            if r.get(f) is not True:
                violations.append(f"{rid}: missing/false {f}")
        for k in FORBIDDEN_FIELD_KEYS:
            if k in r:
                violations.append(f"{rid}: forbidden field key {k}")
        for hit in detect_forbidden_terms(r):
            violations.append(f"{rid}: forbidden term '{hit}'")
        dt = r.get("discoverer_type")
        if dt is not None:
            if dt in FORBIDDEN_DISCOVERER_TYPES:
                violations.append(f"{rid}: forbidden discoverer_type {dt}")
            elif dt not in ALLOWED_DISCOVERER_TYPES:
                violations.append(f"{rid}: unknown discoverer_type {dt}")
        if r.get("record_type") == "discovery_evidence":
            for f in EVIDENCE_DENIALS:
                if r.get(f) is not True:
                    violations.append(f"{rid}: missing/false {f}")
    return violations


def main() -> None:
    print("=" * 64)
    print("HERMES DISCOVERY EVIDENCE BUILDER — a discovery happened (not ranking)")
    print('  evidence_is_not_ranking / not_recommendation (required).')
    print("=" * 64)
    n = len(read_jsonl(DISCOVERY_REFLECTIONS_JSONL))
    created = build()
    if n == 0:
        print("  discovery reflections = 0 → no evidence. 0 is an observation.")
    for r in created:
        print(f"  ✓ {r['evidence_id']} ← {r['source_event']} "
              f"[{r['discoverer_type']}] {r['surface']} → {r['object']}")
    print("-" * 64)
    print(f"  evidence={len(read_jsonl(DISCOVERY_EVIDENCE_JSONL))} "
          f"violations={len(check_invariants())}")


if __name__ == "__main__":
    main()
