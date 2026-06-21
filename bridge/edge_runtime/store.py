"""
store.py — Edge Runtime shared store (single source of truth for both routes).

Append-only storage with hard guards, shared by edge_runtime, findability (Route
A) and gateway_support (Route B). Writes are allowed only under those three
bridges and are refused for Dan-Go (globe/, bridge/gitsea/, bridge/sutable/),
Mujin (bridge/mujin/) and the Agent Commons (bridge/agent_commons/).

Every persisted domain record must carry the universal edge invariants
(edge_base_invariants), must contain no structurally forbidden field, and must
contain no person-data in free text. Route-specific invariants extend the edge
floor in each route and are checked by each route's audit.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── paths ─────────────────────────────────────────────────────────────────────
EDGE_DIR    = Path(__file__).resolve().parent              # bridge/edge_runtime
REPO_ROOT   = EDGE_DIR.parents[1]                           # repo root
DATA_DIR    = EDGE_DIR / "data"
REPORTS_DIR = EDGE_DIR / "reports"

EDGE_RECORDS_JSONL = DATA_DIR / "edge_records.jsonl"
EDGE_MEMORY_JSONL  = DATA_DIR / "edge_memory.jsonl"
EDGE_REPORT_MD     = REPORTS_DIR / "edge_runtime_report.md"

# the three route subtrees this shared store may write to
_ALLOWED_ROOTS = (
    REPO_ROOT / "bridge" / "edge_runtime",
    REPO_ROOT / "bridge" / "findability",
    REPO_ROOT / "bridge" / "gateway_support",
)
# protected territories never written to from here
_FORBIDDEN_WRITE_PARTS = (
    ("globe",),
    ("bridge", "gitsea"),
    ("bridge", "sutable"),
    ("bridge", "mujin"),
    ("bridge", "agent_commons"),
)


class EdgeRuntimeError(Exception):
    pass


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def event_hash(record: dict[str, Any]) -> str:
    body = {k: v for k, v in record.items() if k != "event_hash"}
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def edge_base_invariants() -> dict[str, Any]:
    """Universal floor carried by EVERY edge-route record (both A and B)."""
    return {
        "authority": "none",
        "advisory_only": True,
        "human_review_required": True,
        "person_domain_sealed": True,
        "no_need_inference": True,
        "no_ranking": True,
        "no_recommendation": True,
        "no_selection": True,
        "no_reach_gap_estimation": True,
        "no_saiyan_scouter": True,
        "append_only": True,
    }


# Fields that must NEVER appear on any record (structural prohibition).
FORBIDDEN_FIELDS = (
    "rank", "ranking", "score", "gateway_score", "reputation", "gateway_reputation",
    "recommendation", "recommended", "priority", "best", "selected_candidate",
    "gateway_profile", "reach_gap_estimate", "owner_id", "owner_need",
    "person_relief", "ttfr_p", "combined_metric", "relief_count_kpi",
    "discoverer_target", "outreach_target",
)

# Person-data leakage guard (gateway/findability are not person stores).
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE_RE = re.compile(r"(?<!\d)(?:\+\d[\d \-]{8,}\d|\d{10,})(?!\d)")
_SCAN_SKIP_KEYS = {"event_hash", "appended_at"}


def scan_person_data(record: dict[str, Any]) -> list[str]:
    hits: list[str] = []
    for k, v in record.items():
        if k in _SCAN_SKIP_KEYS:
            continue
        vals = [v] if isinstance(v, str) else ([x for x in v if isinstance(x, str)]
                                               if isinstance(v, list) else [])
        for s in vals:
            if _EMAIL_RE.search(s):
                hits.append(f"{k}: email-like pattern")
            if "url" not in k.lower() and _PHONE_RE.search(s):
                hits.append(f"{k}: phone-like pattern")
    return hits


def missing_base_invariants(record: dict[str, Any],
                            expected: dict[str, Any] | None = None) -> list[str]:
    expected = expected if expected is not None else edge_base_invariants()
    return [k for k, v in expected.items() if record.get(k) != v]


def _guard_path(path: Path) -> Path:
    resolved = path.resolve()
    parts = resolved.parts
    for forbidden in _FORBIDDEN_WRITE_PARTS:
        for i in range(len(parts) - len(forbidden) + 1):
            if tuple(parts[i:i + len(forbidden)]) == forbidden:
                raise EdgeRuntimeError(
                    f"refusing to write to protected path: {resolved}")
    for root in _ALLOWED_ROOTS:
        try:
            resolved.relative_to(root)
            return resolved
        except ValueError:
            continue
    raise EdgeRuntimeError(
        f"refusing to write outside edge_runtime/findability/gateway_support: {resolved}")


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
    """Append one record under an allowed route subtree only. Enforces forbidden
    fields, edge base invariants (for domain records), and the person-data guard,
    so a direct-append bypass cannot write an unflagged/leaky record. Append-only."""
    for f in FORBIDDEN_FIELDS:
        if f in record:
            raise EdgeRuntimeError(
                f"refusing to persist record with forbidden field {f!r}")
    if "record_type" in record:
        missing = missing_base_invariants(record)
        if missing:
            raise EdgeRuntimeError(
                f"refusing to persist domain record missing edge base invariants: {missing}")
    pd = scan_person_data(record)
    if pd:
        raise EdgeRuntimeError(
            f"refusing to persist record with possible person data: {pd} "
            "(edge routes are not person stores; describe, do not paste identifiers)")
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
