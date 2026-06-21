"""
store.py — Route B (Gateway Support) store. Reuses the shared Edge Runtime store
(no duplicated store logic); defines only Route B's data paths and the gateway
invariant set (edge floor + gateway-specific guarantees).

GatewaySupportError is an alias of the shared EdgeRuntimeError for back-compat.
Support memory is NOT stored here — it lives in the shared edge_memory.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# shared single source of truth (de-duplicated) — re-exported for the builders
from bridge.edge_runtime.store import (  # noqa: F401
    EdgeRuntimeError as GatewaySupportError,
    utc_now_iso, event_hash, FORBIDDEN_FIELDS, scan_person_data,
    append_jsonl, read_jsonl, write_text, next_id, edge_base_invariants,
    missing_base_invariants,
)

GW_DIR      = Path(__file__).resolve().parent
DATA_DIR    = GW_DIR / "data"
REPORTS_DIR = GW_DIR / "reports"

VERIFIED_BOTTLENECKS_JSONL = DATA_DIR / "verified_bottlenecks.jsonl"
SUPPORT_CANDIDATES_JSONL   = DATA_DIR / "support_candidates.jsonl"
APPROVAL_RECORDS_JSONL     = DATA_DIR / "approval_records.jsonl"
GATEWAY_CONSENTS_JSONL     = DATA_DIR / "gateway_consents.jsonl"
SUPPORT_EXECUTIONS_JSONL   = DATA_DIR / "support_executions.jsonl"
SUPPORT_FEEDBACK_JSONL     = DATA_DIR / "support_feedback.jsonl"
TTFR_G_RECORDS_JSONL       = DATA_DIR / "ttfr_g_records.jsonl"
WITHDRAWAL_RECORDS_JSONL   = DATA_DIR / "withdrawal_records.jsonl"
REPORT_MD                  = REPORTS_DIR / "gateway_support_report.md"


def base_invariants() -> dict[str, Any]:
    """Edge floor + Route B (gateway support) guarantees."""
    return {
        **edge_base_invariants(),
        "gateway_support_only": True,
        "resource_acceptance_layer_only": True,
        "no_person_relief": True,
        "no_auto_execution": True,
        "no_cooperation_assignment": True,
        "no_gateway_profiling": True,
        "no_gateway_scoring": True,
        "no_gateway_reputation": True,
        "ttfr_g_separate_from_ttfr_p": True,
    }


def carries_base_invariants(rec: dict[str, Any]) -> list[str]:
    """Violations of the full gateway invariant set + forbidden-field scan."""
    bad = [f"{rec.get('record_type','?')}: base invariant {k}"
           for k in missing_base_invariants(rec, base_invariants())]
    for f in FORBIDDEN_FIELDS:
        if f in rec:
            bad.append(f"{rec.get('record_type','?')}: forbidden field {f}")
    return bad
