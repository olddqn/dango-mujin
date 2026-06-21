"""
discoverable_object_evidence_builder.py — Phase F-1.7: Object → Evidence.

Turns object reflections into evidence candidates. Evidence here records object
visibility, object absence, or object dependency — explicitly NOT marketing,
NOT growth, NOT recruitment (required denials).

This module also hosts the shared Object invariant checker used by the Hermes
reviewer: it scans every object record for forbidden growth/marketing/SEO/
recruitment vocabulary and forbidden field keys, confirms required refusal
flags, and refuses any inferred_* object type.

Input (read-only): data/discoverable_object_reflections.jsonl
Output: data/discoverable_object_evidence.jsonl

CLI:
  python -m bridge.agent_commons.runtime.discoverable_object_evidence_builder
"""

from __future__ import annotations

import re
from typing import Any

from .store import (
    DISCOVERABLE_OBJECT_EVIDENCE_JSONL, DISCOVERABLE_OBJECT_LEARNING_JSONL,
    DISCOVERABLE_OBJECT_PATTERN_JSONL, DISCOVERABLE_OBJECT_REFLECTION_JSONL,
    append_jsonl, base_invariants, next_id, read_jsonl,
)
from .discoverable_object_reflector import (
    DISCOVERABLE_OBJECT_INVARIANTS, ALLOWED_OBJECT_TYPES, FORBIDDEN_OBJECT_TYPES,
)
from .discoverable_object_pattern_builder import FORBIDDEN_PATTERN_KEYS

# vocabulary meaning the layer drifted from observation into growth / marketing /
# recruitment. Scanned over string VALUES only (never keys).
FORBIDDEN_TERMS = [
    r"\bgrowth\b", r"\bmarketing\b", r"\bacquisition\b", r"\bacquire\b",
    r"\brecruit", r"\bconversion\b", r"\bseo\b", r"best object",
    r"recommended object", r"\boutreach\b",
]
# forbidden field keys: ranking/recommendation/priority + the pattern forbidden keys
FORBIDDEN_FIELD_KEYS = ("recommended_object", "priority_object", "ranked_object",
                        *FORBIDDEN_PATTERN_KEYS)

# evidence-specific required denials
EVIDENCE_DENIALS = {
    "object_is_not_marketing": True,
    "object_is_not_growth": True,
    "object_is_not_recruitment": True,
}


def _already() -> set[tuple[str, str]]:
    return {(r.get("surface_type"), r.get("object_type"))
            for r in read_jsonl(DISCOVERABLE_OBJECT_EVIDENCE_JSONL)}


def build() -> list[dict[str, Any]]:
    """One evidence record per object reflection (idempotent). Discoverable
    objects → 'object visibility'; absent objects → 'object absence'."""
    done = _already()
    created = []
    for r in read_jsonl(DISCOVERABLE_OBJECT_REFLECTION_JSONL):
        key = (r.get("surface_type"), r.get("object_type"))
        if key in done:
            continue
        disc = bool(r.get("discoverable"))
        record = {
            "record_type": "discoverable_object_evidence",
            "evidence_id": next_id("obj-ev", DISCOVERABLE_OBJECT_EVIDENCE_JSONL),
            "surface_id": r.get("surface_id"),
            "surface_type": r.get("surface_type"),
            "object_type": r.get("object_type"),
            "evidence_kind": "object_visibility" if disc else "object_absence",
            "discoverable": disc,
            "public": bool(r.get("public")),
            "observed_at": r.get("observed_at"),
            "claim": ("an object is discoverable through this surface" if disc
                      else "an object is not discoverable through this surface"),
            "evidence_is_not_fact": True,
            "evidence_is_not_proof": True,
            **EVIDENCE_DENIALS,
            **DISCOVERABLE_OBJECT_INVARIANTS,
            **base_invariants(),
        }
        created.append(append_jsonl(DISCOVERABLE_OBJECT_EVIDENCE_JSONL, record))
        done.add(key)
    return created


# ── shared checker (used by hermes_reviewer) ────────────────────────────────

def _all_object_records() -> list[dict[str, Any]]:
    out = []
    for path in (DISCOVERABLE_OBJECT_REFLECTION_JSONL, DISCOVERABLE_OBJECT_LEARNING_JSONL,
                 DISCOVERABLE_OBJECT_PATTERN_JSONL, DISCOVERABLE_OBJECT_EVIDENCE_JSONL):
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
    """Object records must stay observation; never marketing/growth/recruitment,
    and never an inferred_* object type."""
    violations = []
    rid_keys = ("reflection_id", "learning_id", "pattern_id", "evidence_id")
    for r in _all_object_records():
        rid = next((r[k] for k in rid_keys if r.get(k)), "?")
        for f in DISCOVERABLE_OBJECT_INVARIANTS:
            if r.get(f) is not True:
                violations.append(f"{rid}: missing/false {f}")
        for k in FORBIDDEN_FIELD_KEYS:
            if k in r:
                violations.append(f"{rid}: forbidden field key {k}")
        for hit in detect_forbidden_terms(r):
            violations.append(f"{rid}: forbidden term '{hit}'")
        ot = r.get("object_type")
        if ot is not None:
            if ot in FORBIDDEN_OBJECT_TYPES:
                violations.append(f"{rid}: forbidden object_type {ot}")
            elif ot not in ALLOWED_OBJECT_TYPES:
                violations.append(f"{rid}: unknown object_type {ot}")
        if r.get("record_type") == "discoverable_object_evidence":
            for f in EVIDENCE_DENIALS:
                if r.get(f) is not True:
                    violations.append(f"{rid}: missing/false {f}")
    return violations


def main() -> None:
    print("=" * 64)
    print("HERMES DISCOVERABLE OBJECT EVIDENCE BUILDER — object visibility/absence")
    print('  object_is_not_marketing/growth/recruitment (required).')
    print("=" * 64)
    created = build()
    if not created:
        print("  (no new evidence — no object reflections, or already built)")
    for r in created:
        print(f"  ✓ {r['evidence_id']} {r['surface_type']:<18}→ {r['object_type']:<18} "
              f"[{r['evidence_kind']}]")
    print("-" * 64)
    print(f"  evidence={len(read_jsonl(DISCOVERABLE_OBJECT_EVIDENCE_JSONL))} "
          f"violations={len(check_invariants())}")


if __name__ == "__main__":
    main()
