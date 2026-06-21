"""
exporter.py — Mujin Platform MVP v1.1: Phase B Export / Import Adapter

Read Dan-Go decision data (read-only) and build Mujin Case DRAFTS for
human review. A draft is not a case. A draft is not an obligation.
A draft is not proof that anyone needs, deserves, or wants support.

"Registration is not proof."
"Withdrawal is not failure."
"Support is not debt."
"advisory_only is not moral immunity."

Boundary rules (ADR-001/002/003, SPEC §3.2):
  - Dan-Go sources are opened READ-ONLY. This module never writes to
    globe/, bridge/gitsea/, or bridge/sutable/ (store.py guards enforce it).
  - Drafts are written ONLY under bridge/mujin/reports/ as
    mujin_export_*.json, write-once.
  - Drafts are NOT appended to the case event stream. Becoming a Mujin Case
    requires human review and, where the subject has not consented yet,
    the deferred-consent path of case_registry.create_mujin_case (D-2/D-3).
  - Every draft carries consent.status="deferred": an export adapter can
    never manufacture consent. Only the subject can consent.

Export source priority (DISCOVERY_REPORT §4):
  P1  globe/directives/*.json          decision intent
  P1  globe/logs/*.jsonl               append-only execution log
  P2  bridge/gitsea/relief/**          relief case memory (reference only)
  P3  bridge/sutable/reality_feedback.jsonl   canonical feedback (read-only)

Missing sources are skipped safely — a partially deployed Dan-Go is normal.

Demo:
  python -m bridge.mujin.exporter        (run from the repository root)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .schemas import base_invariants
from .store import (
    MUJIN_DIR,
    REPORTS_DIR,
    MujinStoreError,
    read_jsonl,
    utc_now_iso,
    write_json_new,
)

# ── Dan-Go source locations (READ-ONLY) ──────────────────────────────────────
_REPO_ROOT = MUJIN_DIR.parents[1]

DIRECTIVES_DIR   = _REPO_ROOT / "globe" / "directives"
EXECUTION_LOGS   = _REPO_ROOT / "globe" / "logs"
RELIEF_DIR       = _REPO_ROOT / "bridge" / "gitsea" / "relief"
REALITY_FEEDBACK = _REPO_ROOT / "bridge" / "sutable" / "reality_feedback.jsonl"


class MujinExportError(Exception):
    """Raised when an export operation cannot proceed."""


# ── discovery ─────────────────────────────────────────────────────────────────

def discover_dango_sources() -> dict[str, Any]:
    """Discover available Dan-Go sources. Missing sources are skipped safely.

    Returns a manifest of what exists; never raises on absence — a partially
    deployed Dan-Go is a normal condition, not an error.
    """
    directives = sorted(DIRECTIVES_DIR.glob("directive-*.json")) if DIRECTIVES_DIR.is_dir() else []
    logs       = sorted(EXECUTION_LOGS.glob("*.jsonl")) if EXECUTION_LOGS.is_dir() else []
    relief     = sorted(RELIEF_DIR.rglob("relief-case-registry*.json")) if RELIEF_DIR.is_dir() else []
    return {
        "discovered_at": utc_now_iso(),
        "directives":        [str(p.relative_to(_REPO_ROOT)) for p in directives],
        "execution_logs":    [str(p.relative_to(_REPO_ROOT)) for p in logs],
        "relief_registries": [str(p.relative_to(_REPO_ROOT)) for p in relief],
        "reality_feedback_present": REALITY_FEEDBACK.is_file(),
        "read_only": True,   # discovery never writes anywhere
    }


# ── loaders (all READ-ONLY) ───────────────────────────────────────────────────

def _read_json(path: Path) -> dict[str, Any] | None:
    """Read one JSON file; unreadable / missing files are skipped (None)."""
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def load_directive(directive_id: str) -> dict[str, Any] | None:
    """Load one directive by id (read-only). None if absent or unreadable."""
    path = DIRECTIVES_DIR / f"{directive_id}.json"
    return _read_json(path) if path.is_file() else None


def load_execution_log(directive_id: str) -> list[dict[str, Any]]:
    """Load the append-only execution log for a directive (read-only).

    Returns [] when the log does not exist. The log is NEVER written to.
    """
    path = EXECUTION_LOGS / f"{directive_id}.jsonl"
    return read_jsonl(path) if path.is_file() else []


def load_relief_case(relief_case_id: str) -> dict[str, Any] | None:
    """Find one relief case by id inside the relief registries (read-only).

    The Relief Case Memory is referenced, never modified (ADR-003).
    """
    if not RELIEF_DIR.is_dir():
        return None
    for registry_path in sorted(RELIEF_DIR.rglob("relief-case-registry*.json")):
        registry = _read_json(registry_path)
        for case in (registry or {}).get("cases", []):
            if case.get("relief_case_id") == relief_case_id:
                return case
    return None


def load_reality_feedback(claim_id: str | None = None) -> list[dict[str, Any]]:
    """Read canonical reality feedback (ADR-001), optionally by claim_id.

    Read-only. The canonical JSONL is never written from the export layer.
    """
    if not REALITY_FEEDBACK.is_file():
        return []
    records = read_jsonl(REALITY_FEEDBACK)
    if claim_id is None:
        return records
    return [r for r in records if r.get("claim_id") == claim_id]


# ── draft builder ─────────────────────────────────────────────────────────────

def _draft_safety_block() -> dict[str, Any]:
    """The non-negotiable flags every export draft carries (SPEC §4, ADR-005)."""
    block = base_invariants()
    block.update({
        "advisory_only": True,
        "human_review_required": True,
        "subject_objection_path_required": True,   # D-1 / SPEC §15
        "outreach_explanation_required": True,     # D-7 / SPEC §8.5
        "reach_gap_unresolved": True,              # D-6 — never claimed solved
        "draft_is_not_a_case": True,
        "draft_creates_no_contact": True,          # exporting never contacts anyone
    })
    return block


def build_mujin_case_draft(
    draft_id: str,
    directive_id: str | None = None,
    relief_case_id: str | None = None,
) -> dict[str, Any]:
    """Build a Mujin Case draft from Dan-Go decision data (read-only).

    At least one source (directive or relief case) must exist. The draft:
      - references its sources (source_refs) and never rewrites them,
      - carries consent.status="deferred" — an adapter cannot manufacture
        consent; only the subject can consent (D-2/D-3),
      - requires human review before anything else happens,
      - proposes needs from the directive's in-scope items / relief case
        description as REVIEW MATERIAL, not as facts about a person.
    """
    directive = load_directive(directive_id) if directive_id else None
    relief    = load_relief_case(relief_case_id) if relief_case_id else None
    if directive is None and relief is None:
        raise MujinExportError(
            "no usable source: neither the directive nor the relief case "
            f"was found (directive_id={directive_id!r}, relief_case_id={relief_case_id!r})"
        )

    log_entries = load_execution_log(directive_id) if directive_id else []
    claim_id = (directive or {}).get("source_claim_id")
    feedback = load_reality_feedback(claim_id) if claim_id else []

    source_refs: dict[str, Any] = {}
    if directive is not None:
        source_refs["directive_id"] = directive_id
        source_refs["claim_id"] = claim_id
        source_refs["globe_id"] = directive.get("globe_id")
    if relief is not None:
        source_refs["relief_case_id"] = relief_case_id
        source_refs["route_id"] = relief.get("route_id")
        source_refs["commons_id"] = relief.get("commons_id")

    # proposed needs — review material only, phrased from decision scope,
    # never from judgments about a person
    proposed_needs: list[dict[str, Any]] = []
    for i, item in enumerate((directive or {}).get("scope", {}).get("in_scope", [])[:3], 1):
        proposed_needs.append({
            "need_id": f"{draft_id}-need-{i:02d}",
            "description": item,
            "addresses_condition": None,
            "status": "open",
            "proposed_only": True,
        })
    if relief is not None and not proposed_needs:
        proposed_needs.append({
            "need_id": f"{draft_id}-need-01",
            "description": f"follow-up cooperation around {relief.get('case_type', 'general_followup')}",
            "addresses_condition": None,
            "status": "open",
            "proposed_only": True,
        })

    draft: dict[str, Any] = {
        "record_type": "mujin_case_draft",
        "draft_id": draft_id,
        "generated_at": utc_now_iso(),
        "created_from": "relief_case" if relief is not None else "direct_application",
        "source_refs": source_refs,
        "consent": {
            "status": "deferred",          # an adapter can never manufacture consent
            "can_consent": False,          # unknown until the subject is actually asked
            "obtained_at": None,
            "confirmation_due": True,      # duty to confirm before anything proceeds (D-2)
            "note": "consent must be obtained from the subject before this draft "
                    "may become a case; a state of being unable to consent is not "
                    "consent (D-3)",
        },
        "discovery_origin": {
            "how": "export adapter over existing Dan-Go decision records",
            "by": "bridge.mujin.exporter",
            "disclosed_to_subject": False,  # must become True at consent confirmation
        },
        "proposed_needs": proposed_needs,
        "context": {
            "directive_title": (directive or {}).get("title"),
            "directive_objective": (directive or {}).get("objective"),
            "execution_log_entries_seen": len(log_entries),
            "reality_feedback_entries_seen": len(feedback),
            "relief_case_status": (relief or {}).get("case_status"),
        },
        "next_step": "human review — then, only with the subject's confirmed consent, "
                     "register via case_registry.create_mujin_case",
        "registration_is_not_proof": True,
    }
    draft.update(_draft_safety_block())
    return draft


# ── export ────────────────────────────────────────────────────────────────────

def export_mujin_case_draft(draft: dict[str, Any]) -> Path | None:
    """Write a draft to bridge/mujin/reports/mujin_export_<draft_id>.json.

    Write-once: an existing export is never overwritten (append-only layer).
    Returns the path, or None when the export already exists.
    """
    for key in ("draft_id", "source_refs", "consent"):
        if key not in draft:
            raise MujinExportError(f"draft is missing required key: {key}")
    if draft["consent"].get("status") != "deferred":
        raise MujinExportError(
            "export drafts must carry consent.status='deferred' — "
            "an export adapter can never manufacture consent (D-2/D-3)"
        )
    path = REPORTS_DIR / f"mujin_export_{draft['draft_id']}.json"
    if path.exists():
        return None
    return write_json_new(path, draft)


# ── demo / CLI verification ───────────────────────────────────────────────────

def run_demo() -> dict[str, Any]:
    """Discover sources and export sample drafts. Read-only on Dan-Go."""
    manifest = discover_dango_sources()
    print(f"  · directives found:        {len(manifest['directives'])}")
    print(f"  · execution logs found:    {len(manifest['execution_logs'])}")
    print(f"  · relief registries found: {len(manifest['relief_registries'])}")
    print(f"  · reality feedback:        {'present' if manifest['reality_feedback_present'] else 'absent (skipped safely)'}")

    summary: dict[str, Any] = {"manifest": manifest, "exports": []}

    # draft 1: from a directive + its execution log (P1 sources)
    if manifest["directives"]:
        directive_id = Path(manifest["directives"][0]).stem
        draft = build_mujin_case_draft(
            draft_id=f"from-{directive_id}",
            directive_id=directive_id,
        )
        written = export_mujin_case_draft(draft)
        summary["exports"].append({
            "draft_id": draft["draft_id"],
            "written": str(written.relative_to(_REPO_ROOT)) if written else "already exists (write-once)",
        })
        print(f"  ✓ draft from directive: {draft['draft_id']}"
              + ("" if written else " (already exported — skipped)"))

    # draft 2: from a relief case (P2 source, reference only)
    relief_case = load_relief_case("relief-case-002")
    if relief_case is not None:
        draft = build_mujin_case_draft(
            draft_id="from-relief-case-002",
            relief_case_id="relief-case-002",
        )
        written = export_mujin_case_draft(draft)
        summary["exports"].append({
            "draft_id": draft["draft_id"],
            "written": str(written.relative_to(_REPO_ROOT)) if written else "already exists (write-once)",
        })
        print(f"  ✓ draft from relief case: {draft['draft_id']}"
              + ("" if written else " (already exported — skipped)"))

    # demonstrate refusal: a draft without deferred consent is rejected
    try:
        bad = build_mujin_case_draft("refusal-demo", relief_case_id="relief-case-002")
        bad["consent"]["status"] = "active"
        export_mujin_case_draft(bad)
        print("  ✗ FAILED TO REFUSE non-deferred draft")
    except MujinExportError as exc:
        summary["refusal_demonstrated"] = str(exc)
        print("  ✓ refusal demonstrated: exports can never carry manufactured consent")

    return summary


def main() -> None:
    print("=" * 72)
    print("MUJIN EXPORT ADAPTER — Phase B (read-only over Dan-Go, advisory only)")
    print('"Registration is not proof." "Withdrawal is not failure."')
    print('"Support is not debt." "advisory_only is not moral immunity."')
    print("=" * 72)
    summary = run_demo()
    print("-" * 72)
    print(json.dumps(
        {k: v for k, v in summary.items() if k != "manifest"},
        ensure_ascii=False, indent=2))
    print("-" * 72)
    print("Dan-Go sources were opened read-only. Drafts are review material,")
    print("not cases, not contacts, not proof. The Reach Gap remains unresolved.")


if __name__ == "__main__":
    main()
