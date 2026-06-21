"""
store.py — Mujin Platform MVP v1.1: Phase A Data Layer

Append-only JSON / JSONL storage utilities for Mujin records.

"Registration is not proof."
"Withdrawal is not failure."
"Support is not debt."
"advisory_only is not moral immunity."

Storage rules (ADR-001/002, SPEC §3.2):
  - All Mujin-specific data lives under bridge/mujin/ (data/, examples/, reports/).
  - JSONL files are append-only: existing lines are never rewritten or deleted.
  - JSON snapshot files are written to NEW paths only; overwriting an existing
    record file is refused (state changes are expressed as new appended events,
    not in-place mutation).
  - This module NEVER touches Dan-Go files: no writes to globe/logs/,
    globe/claims/, globe/directives/, or bridge/gitsea/relief/.
  - The canonical Reality Feedback sink (bridge/sutable/reality_feedback.jsonl)
    is owned by the existing Dan-Go appender; the Mujin data layer does not
    write feedback — that is Phase D, and it will go through that canon only.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── paths ─────────────────────────────────────────────────────────────────────
MUJIN_DIR    = Path(__file__).resolve().parent
DATA_DIR     = MUJIN_DIR / "data"
EXAMPLES_DIR = MUJIN_DIR / "examples"
REPORTS_DIR  = MUJIN_DIR / "reports"

CASES_JSONL      = DATA_DIR / "mujin_cases.jsonl"
OBJECTIONS_JSONL = DATA_DIR / "objections.jsonl"
NON_MUJIN_JSONL  = DATA_DIR / "non_mujin_support.jsonl"

# Paths the Mujin data layer must never write to (ADR-001/002/003).
_FORBIDDEN_WRITE_PARTS = (
    ("globe",),                          # all Dan-Go globe records (logs/claims/directives)
    ("bridge", "gitsea"),                # Relief Case Memory and the GITSEA chain
    ("bridge", "sutable"),               # canonical JSONLs owned by existing appenders
)


class MujinStoreError(Exception):
    """Raised when a storage rule would be violated."""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def event_hash(record: dict[str, Any]) -> str:
    """Deterministic sha256 over the record without its own hash field."""
    body = {k: v for k, v in record.items() if k != "event_hash"}
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _guard_path(path: Path) -> Path:
    """Refuse writes outside bridge/mujin/ and writes into Dan-Go territory."""
    resolved = path.resolve()
    parts = resolved.parts
    for forbidden in _FORBIDDEN_WRITE_PARTS:
        for i in range(len(parts) - len(forbidden) + 1):
            if tuple(parts[i:i + len(forbidden)]) == forbidden:
                raise MujinStoreError(
                    f"refusing to write to Dan-Go path: {resolved} "
                    "(Mujin never modifies Execution Logs, Relief Case Memory, "
                    "or canonical sutable files from the data layer)"
                )
    try:
        resolved.relative_to(MUJIN_DIR)
    except ValueError:
        raise MujinStoreError(
            f"refusing to write outside bridge/mujin/: {resolved}"
        ) from None
    return resolved


def append_jsonl(path: Path, record: dict[str, Any]) -> dict[str, Any]:
    """Append one record to a JSONL file. Never rewrites existing lines.

    Adds appended_at and event_hash. Returns the stored record.
    """
    resolved = _guard_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    stored = dict(record)
    stored.setdefault("appended_at", utc_now_iso())
    stored["event_hash"] = event_hash(stored)
    with open(resolved, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(stored, ensure_ascii=False) + "\n")
    return stored


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read all records from a JSONL file (missing file => empty list)."""
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_json_new(path: Path, record: dict[str, Any]) -> Path:
    """Write a JSON snapshot to a NEW file. Refuses to overwrite.

    State changes are appended events (append_jsonl), not file mutations.
    Snapshots are for examples/ and reports/ output.
    """
    resolved = _guard_path(path)
    if resolved.exists():
        raise MujinStoreError(
            f"refusing to overwrite existing file (append-only layer): {resolved}"
        )
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with open(resolved, "w", encoding="utf-8") as fh:
        json.dump(record, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return resolved


def read_json(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def latest_case_state(case_id: str, path: Path = CASES_JSONL) -> dict[str, Any] | None:
    """Reconstruct the latest state of a case from the append-only event stream.

    The stream is the source of truth; the latest event for a case_id wins.
    Earlier events remain in the file untouched (provenance is preserved).
    """
    latest: dict[str, Any] | None = None
    for record in read_jsonl(path):
        if record.get("case_id") == case_id:
            latest = record
    return latest
