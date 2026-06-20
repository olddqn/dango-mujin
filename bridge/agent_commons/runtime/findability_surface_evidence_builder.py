"""
findability_surface_evidence_builder.py — Phase F-1.5: Surface → Evidence.

Turns existing surfaces into evidence candidates. Evidence here records a
surface's existence, its public state, and its discoverability — explicitly NOT
recruitment, NOT outreach, NOT growth, NOT marketing (required denials).

Only surfaces with exists=true are turned into evidence ("Evidence 化できるもの:
surface の存在"). Absent surfaces remain as reflections.

This module also hosts the shared Surface invariant checker used by the Hermes
reviewer: it scans every surface record for forbidden growth/outreach/marketing
vocabulary and forbidden field keys, and confirms required refusal flags.

Input (read-only): data/findability_surface_reflections.jsonl
Output: data/findability_surface_evidence.jsonl

CLI:
  python -m bridge.agent_commons.runtime.findability_surface_evidence_builder
"""

from __future__ import annotations

import re
from typing import Any

from .store import (
    FINDABILITY_SURFACE_EVIDENCE_JSONL, FINDABILITY_SURFACE_LEARNING_JSONL,
    FINDABILITY_SURFACE_PATTERN_JSONL, FINDABILITY_SURFACE_REFLECTION_JSONL,
    append_jsonl, base_invariants, next_id, read_jsonl,
)
from .findability_surface_reflector import FINDABILITY_SURFACE_INVARIANTS
from .findability_surface_pattern_builder import FORBIDDEN_PATTERN_KEYS

# vocabulary meaning the layer drifted from observation into growth / outreach /
# marketing. Scanned over string VALUES only (never keys).
FORBIDDEN_TERMS = [
    r"\boutreach\b", r"\brecruit", r"\bgrowth\b", r"\bmarketing\b",
    r"\bacquisition\b", r"\bacquire\b", r"\bconversion\b", r"seo optimi",
    r"best channel", r"recommended channel", r"best surface",
    r"recommended surface", r"\bviral\b", r"\bfunnel\b",
]
# forbidden field keys: ranking/recommendation/priority + the pattern forbidden keys
FORBIDDEN_FIELD_KEYS = ("ranked_surface", "recommended_surface", "priority_surface",
                        *FORBIDDEN_PATTERN_KEYS)

# evidence-specific required denials
EVIDENCE_DENIALS = {
    "surface_is_not_recruitment": True,
    "surface_is_not_outreach": True,
    "surface_is_not_growth": True,
    "surface_is_not_marketing": True,
}


def _already() -> set[str]:
    return {r.get("surface_type") for r in read_jsonl(FINDABILITY_SURFACE_EVIDENCE_JSONL)}


def build() -> list[dict[str, Any]]:
    """One evidence record per EXISTING surface (idempotent by surface_type)."""
    done = _already()
    created = []
    for r in read_jsonl(FINDABILITY_SURFACE_REFLECTION_JSONL):
        st = r.get("surface_type")
        if not r.get("exists") or st in done:
            continue
        record = {
            "record_type": "findability_surface_evidence",
            "evidence_id": next_id("surface-ev", FINDABILITY_SURFACE_EVIDENCE_JSONL),
            "surface_type": st,
            "claim": "a surface exists with the observed public/discoverable state",
            "exists": True,
            "publicly_accessible": r.get("publicly_accessible"),
            "discoverable": r.get("discoverable"),
            "observed_at": r.get("observed_at"),
            "evidence_is_not_fact": True,
            "evidence_is_not_proof": True,
            **EVIDENCE_DENIALS,
            **FINDABILITY_SURFACE_INVARIANTS,
            **base_invariants(),
        }
        created.append(append_jsonl(FINDABILITY_SURFACE_EVIDENCE_JSONL, record))
        done.add(st)
    return created


# ── shared checker (used by hermes_reviewer) ────────────────────────────────

def _all_surface_records() -> list[dict[str, Any]]:
    out = []
    for path in (FINDABILITY_SURFACE_REFLECTION_JSONL, FINDABILITY_SURFACE_LEARNING_JSONL,
                 FINDABILITY_SURFACE_PATTERN_JSONL, FINDABILITY_SURFACE_EVIDENCE_JSONL):
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
    """Surface records must stay observation; never outreach/growth/marketing."""
    violations = []
    rid_keys = ("reflection_id", "learning_id", "pattern_id", "evidence_id")
    for r in _all_surface_records():
        rid = next((r[k] for k in rid_keys if r.get(k)), "?")
        for f in FINDABILITY_SURFACE_INVARIANTS:
            if r.get(f) is not True:
                violations.append(f"{rid}: missing/false {f}")
        for k in FORBIDDEN_FIELD_KEYS:
            if k in r:
                violations.append(f"{rid}: forbidden field key {k}")
        for hit in detect_forbidden_terms(r):
            violations.append(f"{rid}: forbidden term '{hit}'")
        if r.get("requires_outreach") is True:
            violations.append(f"{rid}: requires_outreach is True")
        if r.get("record_type") == "findability_surface_evidence":
            for f in EVIDENCE_DENIALS:
                if r.get(f) is not True:
                    violations.append(f"{rid}: missing/false {f}")
    return violations


def main() -> None:
    print("=" * 64)
    print("HERMES FINDABILITY SURFACE EVIDENCE BUILDER — surface exists (not marketing)")
    print('  surface_is_not_recruitment/outreach/growth/marketing (required).')
    print("=" * 64)
    created = build()
    if not created:
        print("  (no new evidence — no existing surfaces, or already built)")
    for r in created:
        print(f"  ✓ {r['evidence_id']} {r['surface_type']:<22} "
              f"public={r['publicly_accessible']} discoverable={r['discoverable']}")
    print("-" * 64)
    print(f"  evidence={len(read_jsonl(FINDABILITY_SURFACE_EVIDENCE_JSONL))} "
          f"violations={len(check_invariants())}")


if __name__ == "__main__":
    main()
