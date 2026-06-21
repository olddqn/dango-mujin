"""
discovery_path_evidence_builder.py — Phase F-2.5: Path → Evidence.

Turns observed discovery paths into evidence candidates. Evidence may record:
a real discovery event, the surface/object/event match, or a repeated path. It
may NOT record an inferred path, a recommended path, a growth path, or a funnel.

This module also hosts the shared Path invariant checker used by the Hermes
reviewer: it scans every path record for forbidden growth/marketing/funnel/SEO/
acquisition/conversion/recommendation vocabulary and forbidden field keys, and
confirms required refusal flags.

Input (read-only): data/discovery_path_reflections.jsonl
Output: data/discovery_path_evidence.jsonl

CLI:
  python -m bridge.agent_commons.runtime.discovery_path_evidence_builder
"""

from __future__ import annotations

import re
from typing import Any

from .store import (
    DISCOVERY_PATH_EVIDENCE_JSONL, DISCOVERY_PATH_LEARNINGS_JSONL,
    DISCOVERY_PATH_PATTERNS_JSONL, DISCOVERY_PATH_REFLECTIONS_JSONL,
    append_jsonl, base_invariants, next_id, read_jsonl,
)
from .discovery_path_reflector import DISCOVERY_PATH_INVARIANTS
from .discovery_path_pattern_builder import FORBIDDEN_PATTERN_KEYS

# vocabulary meaning the layer drifted from observation into funnel / growth /
# marketing / acquisition / conversion / recommendation. Scanned over string
# VALUES only (never keys).
FORBIDDEN_TERMS = [
    r"\bgrowth\b", r"\bmarketing\b", r"\bacquisition\b", r"\bacquire\b",
    r"\bconversion\b", r"\bfunnel\b", r"\bseo\b", r"\brecruitment\b", r"\brecruit",
    r"\boutreach\b", r"best path", r"recommended path", r"priority path",
]
# forbidden field keys: ranked/recommended/priority path + funnel/growth/etc.
FORBIDDEN_FIELD_KEYS = ("recommended_path", "ranked_path", "priority_path",
                        "conversion_funnel", "growth_loop", "acquisition_path",
                        "marketing_path", *FORBIDDEN_PATTERN_KEYS)

# evidence-specific required denials
EVIDENCE_DENIALS = {
    "evidence_is_not_funnel": True,
    "evidence_is_not_recommendation": True,
}


def _already() -> set[str]:
    return {r.get("event_id") for r in read_jsonl(DISCOVERY_PATH_EVIDENCE_JSONL)}


def build() -> list[dict[str, Any]]:
    """One evidence record per observed discovery path (idempotent by event_id)."""
    done = _already()
    created = []
    for r in read_jsonl(DISCOVERY_PATH_REFLECTIONS_JSONL):
        eid = r.get("event_id")
        if not eid or eid in done:
            continue
        record = {
            "record_type": "discovery_path_evidence",
            "evidence_id": next_id("dpath-ev", DISCOVERY_PATH_EVIDENCE_JSONL),
            "event_id": eid,
            "path_id": r.get("path_id"),
            "surface_type": r.get("surface_type"),
            "object_type": r.get("object_type"),
            "discoverer_type": r.get("discoverer_type"),
            "claim": "a verified surface→object→event path was observed",
            "surface_match": r.get("surface_match"),
            "object_match": r.get("object_match"),
            "evidence_is_not_fact": True,
            "evidence_is_not_proof": True,
            **EVIDENCE_DENIALS,
            **DISCOVERY_PATH_INVARIANTS,
            **base_invariants(),
        }
        created.append(append_jsonl(DISCOVERY_PATH_EVIDENCE_JSONL, record))
        done.add(eid)
    return created


# ── shared checker (used by hermes_reviewer) ────────────────────────────────

def _all_path_records() -> list[dict[str, Any]]:
    out = []
    for path in (DISCOVERY_PATH_REFLECTIONS_JSONL, DISCOVERY_PATH_LEARNINGS_JSONL,
                 DISCOVERY_PATH_PATTERNS_JSONL, DISCOVERY_PATH_EVIDENCE_JSONL):
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
    """Path records must stay observation; never funnel/growth/marketing/
    acquisition/conversion/recommendation."""
    violations = []
    rid_keys = ("path_id", "learning_id", "pattern_id", "evidence_id")
    for r in _all_path_records():
        rid = next((r[k] for k in rid_keys if r.get(k)), "?")
        for f in DISCOVERY_PATH_INVARIANTS:
            if r.get(f) is not True:
                violations.append(f"{rid}: missing/false {f}")
        for k in FORBIDDEN_FIELD_KEYS:
            if k in r:
                violations.append(f"{rid}: forbidden field key {k}")
        for hit in detect_forbidden_terms(r):
            violations.append(f"{rid}: forbidden term '{hit}'")
        if r.get("record_type") == "discovery_path_evidence":
            for f in EVIDENCE_DENIALS:
                if r.get(f) is not True:
                    violations.append(f"{rid}: missing/false {f}")
    return violations


def main() -> None:
    print("=" * 64)
    print("HERMES DISCOVERY PATH EVIDENCE BUILDER — a path was observed (not funnel)")
    print('  evidence_is_not_funnel / not_recommendation (required).')
    print("=" * 64)
    n = len(read_jsonl(DISCOVERY_PATH_REFLECTIONS_JSONL))
    created = build()
    if n == 0:
        print("  path reflections = 0 → no evidence. 0 is an observation.")
    for r in created:
        print(f"  ✓ {r['evidence_id']} ← {r['event_id']} "
              f"{r['surface_type']} → {r['object_type']}")
    print("-" * 64)
    print(f"  evidence={len(read_jsonl(DISCOVERY_PATH_EVIDENCE_JSONL))} "
          f"violations={len(check_invariants())}")


if __name__ == "__main__":
    main()
