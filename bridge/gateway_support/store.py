"""
store.py — Gateway Support Runtime: shared append-only storage with hard guards.

This layer WRITES only under bridge/gateway_support/. The write guard refuses any
path outside it and explicitly refuses Dan-Go (globe/, bridge/gitsea/,
bridge/sutable/), Mujin (bridge/mujin/), and the Agent Commons (bridge/agent_commons/).

Every record carries the Gateway Support base invariants (authority none,
advisory only, human review required, person domain sealed, gateway support
only, Resource Acceptance layer only, no ranking/recommendation/selection/
auto-execution/cooperation-assignment/gateway-profiling/scoring/reputation/
reach-gap-estimation, TTFR-G separated from TTFR-P, append-only).
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── paths ─────────────────────────────────────────────────────────────────────
GW_DIR      = Path(__file__).resolve().parent              # bridge/gateway_support
REPO_ROOT   = GW_DIR.parents[1]                            # repo root
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
SUPPORT_MEMORY_JSONL       = DATA_DIR / "support_memory.jsonl"

REPORT_MD = REPORTS_DIR / "gateway_support_report.md"

# paths this layer must never write to
_FORBIDDEN_WRITE_PARTS = (
    ("globe",),
    ("bridge", "gitsea"),
    ("bridge", "sutable"),
    ("bridge", "mujin"),
    ("bridge", "agent_commons"),
)


class GatewaySupportError(Exception):
    pass


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def event_hash(record: dict[str, Any]) -> str:
    body = {k: v for k, v in record.items() if k != "event_hash"}
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def base_invariants() -> dict[str, Any]:
    """Carried by every Gateway Support record. Never weakened.

    Encodes the 14 architectural requirements plus the explicit non-goals."""
    return {
        "authority": "none",
        "advisory_only": True,
        "human_review_required": True,
        # domain / layer
        "person_domain_sealed": True,
        "gateway_support_only": True,
        "resource_acceptance_layer_only": True,
        # non-goals (must always be true = never done)
        "no_person_relief": True,
        "no_need_inference": True,
        "no_ranking": True,
        "no_recommendation": True,
        "no_selection": True,
        "no_auto_execution": True,
        "no_cooperation_assignment": True,
        "no_gateway_profiling": True,
        "no_gateway_scoring": True,
        "no_gateway_reputation": True,
        "no_reach_gap_estimation": True,
        # accounting / storage
        "ttfr_g_separate_from_ttfr_p": True,
        "append_only": True,
    }


# Fields that must NEVER appear on any record (structural prohibition).
FORBIDDEN_FIELDS = (
    "rank", "ranking", "score", "gateway_score", "reputation", "gateway_reputation",
    "recommendation", "recommended", "priority", "best", "selected_candidate",
    "gateway_profile", "reach_gap_estimate", "owner_id", "owner_need",
    "person_relief", "ttfr_p",            # never store TTFR-P here
    "combined_metric", "relief_count_kpi",
)

# Person-data leakage guard (B-6): the gateway-only boundary means raw personal
# identifiers (of an absent owner or anyone) must never be pasted into free-text
# fields. Operators describe ("email confirmation from the gateway"), they do not
# paste addresses/numbers. Email is detected reliably; phone is detected only as a
# 10+ digit run or an international +NN… pattern, which avoids amounts/dates.
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE_RE = re.compile(r"(?<!\d)(?:\+\d[\d \-]{8,}\d|\d{10,})(?!\d)")
_SCAN_SKIP_KEYS = {"event_hash", "appended_at"}


def scan_person_data(record: dict[str, Any]) -> list[str]:
    """Return free-text fields that look like they contain personal identifiers."""
    hits: list[str] = []
    for k, v in record.items():
        if k in _SCAN_SKIP_KEYS:
            continue
        if isinstance(v, str):
            vals = [v]
        elif isinstance(v, list):
            vals = [x for x in v if isinstance(x, str)]
        else:
            continue
        for s in vals:
            if _EMAIL_RE.search(s):
                hits.append(f"{k}: email-like pattern")
            if "url" not in k.lower() and _PHONE_RE.search(s):
                hits.append(f"{k}: phone-like pattern")
    return hits


def missing_base_invariants(record: dict[str, Any]) -> list[str]:
    """Base invariants a domain record must carry, with the expected value."""
    return [k for k, v in base_invariants().items() if record.get(k) != v]


def _guard_path(path: Path) -> Path:
    resolved = path.resolve()
    parts = resolved.parts
    for forbidden in _FORBIDDEN_WRITE_PARTS:
        for i in range(len(parts) - len(forbidden) + 1):
            if tuple(parts[i:i + len(forbidden)]) == forbidden:
                raise GatewaySupportError(
                    f"refusing to write to protected path: {resolved} "
                    "(Gateway Support writes only under bridge/gateway_support/)")
    try:
        resolved.relative_to(GW_DIR)
    except ValueError:
        raise GatewaySupportError(
            f"refusing to write outside bridge/gateway_support/: {resolved}") from None
    return resolved


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def append_jsonl(path: Path, record: dict[str, Any]) -> dict[str, Any]:
    """Append one record under bridge/gateway_support/ only. Adds hash + ts.

    Persistence-boundary enforcement (B-4): every persisted record must (a) carry
    no structurally forbidden field, (b) carry the full base invariants if it is a
    domain record (has record_type), and (c) contain no person-data in free text
    (B-6). This makes a direct append_jsonl bypass unable to write an unflagged,
    invariant-weakened, or person-data-bearing record. Append-only is preserved."""
    for f in FORBIDDEN_FIELDS:
        if f in record:
            raise GatewaySupportError(
                f"refusing to persist record with forbidden field {f!r} "
                "(no ranking/score/recommendation/reputation/owner/ttfr_p/reach-gap)")
    if "record_type" in record:
        missing = missing_base_invariants(record)
        if missing:
            raise GatewaySupportError(
                f"refusing to persist domain record missing/weakened base invariants: {missing}")
    pd = scan_person_data(record)
    if pd:
        raise GatewaySupportError(
            f"refusing to persist record with possible person data: {pd} "
            "(gateway-only boundary; describe, do not paste personal identifiers)")
    resolved = _guard_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    stored = dict(record)
    stored.setdefault("appended_at", utc_now_iso())
    stored["event_hash"] = event_hash(stored)
    with open(resolved, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(stored, ensure_ascii=False) + "\n")
    return stored


def write_text(path: Path, text: str) -> Path:
    resolved = _guard_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with open(resolved, "w", encoding="utf-8") as fh:
        fh.write(text)
    return resolved


def next_id(prefix: str, path: Path) -> str:
    return f"{prefix}-{len(read_jsonl(path)) + 1:03d}"


def carries_base_invariants(rec: dict[str, Any]) -> list[str]:
    """Return list of violated base invariants (empty = ok)."""
    bad = []
    for k, v in base_invariants().items():
        if rec.get(k) != v:
            bad.append(f"{rec.get('record_type','?')}:{rec.get('event_hash','?')[:8]} "
                       f"base invariant {k} expected {v!r}, got {rec.get(k)!r}")
    for f in FORBIDDEN_FIELDS:
        if f in rec:
            bad.append(f"{rec.get('record_type','?')}: forbidden field {f}")
    return bad
