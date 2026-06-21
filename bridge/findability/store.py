"""
store.py — Route A (Findability) store. Reuses the shared Edge Runtime store
(no duplicated store logic); defines only Route A's data paths and the
findability invariant set (edge floor + findability-specific flags).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# shared primitives (single source of truth) — re-exported for the builders
from bridge.edge_runtime.store import (  # noqa: F401
    EdgeRuntimeError, utc_now_iso, event_hash, FORBIDDEN_FIELDS, scan_person_data,
    append_jsonl, read_jsonl, write_text, next_id, edge_base_invariants,
    missing_base_invariants,
)

FINDABILITY_DIR = Path(__file__).resolve().parent
DATA_DIR    = FINDABILITY_DIR / "data"
REPORTS_DIR = FINDABILITY_DIR / "reports"

SURFACES_JSONL              = DATA_DIR / "findability_surfaces.jsonl"
CONSENT_OPPORTUNITIES_JSONL = DATA_DIR / "consent_opportunities.jsonl"
STATE_RECONCILIATIONS_JSONL = DATA_DIR / "state_reconciliations.jsonl"
REPORT_MD                   = REPORTS_DIR / "findability_report.md"


def findability_base_invariants() -> dict[str, Any]:
    """Edge floor + Route A guarantees."""
    return {
        **edge_base_invariants(),
        "findability_is_observation_only": True,
        "no_outreach": True,
        "no_growth": True,
        "no_marketing": True,
        "direction_owner_to_mujin": True,
        "no_pre_exposure": True,
        "no_person_relief": True,
    }
