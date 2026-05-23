#!/usr/bin/env python3
"""
sutable_log.py — dango-gitsea-bridge / su-table

Common JSONL append helper for the su-table (素テーブル).

Responsibilities:
  - Atomic append to a JSONL file (one JSON object per line)
  - sha256 content hash for each event
  - Optional chain integrity: previous_event_hash links events
  - Never overwrites. Never deletes. Only appends.

Design principle:
  History is part of the protocol.
  An event that was appended is part of the record — forever.
  Corrections are new events. Deletions do not exist.
"""

import json
import hashlib
import fcntl
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

SUTABLE_DIR = Path(__file__).parent.parent / "sutable"

VALID_TABLES = {
    "claims",
    "negotiations",
    "contributions",
    "executions",
    "reality_feedback",
}


class SutableError(Exception):
    pass


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _table_path(table: str) -> Path:
    if table not in VALID_TABLES:
        raise SutableError(
            f"Unknown table: '{table}'. Valid: {sorted(VALID_TABLES)}"
        )
    path = SUTABLE_DIR / f"{table}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _last_event_hash(path: Path) -> str | None:
    """Read the last line of a JSONL file and return its event_hash, or None."""
    if not path.exists() or path.stat().st_size == 0:
        return None
    try:
        with open(path, "rb") as f:
            # Read last non-empty line efficiently
            f.seek(0, 2)
            size = f.tell()
            buf = b""
            pos = size - 1
            while pos >= 0:
                f.seek(pos)
                char = f.read(1)
                if char == b"\n" and buf.strip():
                    break
                buf = char + buf
                pos -= 1
            line = buf.decode("utf-8").strip()
            if line:
                obj = json.loads(line)
                return obj.get("event_hash")
    except Exception:
        return None
    return None


def append_event(
    table: str,
    event: dict[str, Any],
    *,
    chain: bool = True,
) -> dict[str, Any]:
    """
    Append a single event to the given su-table JSONL file.

    Automatically adds:
      - timestamp (if not present)
      - event_hash  (sha256 of the serialized event body)
      - previous_event_hash (if chain=True and a previous event exists)

    Returns the final event dict as written.

    Raises SutableError if event_type is missing or table is invalid.
    """
    if "event_type" not in event:
        raise SutableError("event_type is required for every su-table event.")

    event = dict(event)  # shallow copy — never mutate caller's dict

    # Auto-timestamp
    if "timestamp" not in event:
        event["timestamp"] = _now_iso()

    path = _table_path(table)

    # Chain: link to previous event
    if chain:
        prev_hash = _last_event_hash(path)
        if prev_hash:
            event["previous_event_hash"] = prev_hash

    # Stable serialization for hashing (sorted keys, no whitespace)
    body_str = json.dumps(event, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    event["event_hash"] = _sha256(body_str)

    # Final line (pretty-minimized: compact but readable)
    line = json.dumps(event, ensure_ascii=False) + "\n"

    # Atomic append with file lock
    with open(path, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.write(line)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)

    return event


def read_all(table: str) -> list[dict[str, Any]]:
    """Read all events from a table. Returns list of dicts."""
    path = _table_path(table)
    if not path.exists() or path.stat().st_size == 0:
        return []
    events = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"[sutable_log] Warning: malformed JSON on line {i} of {table}.jsonl: {e}",
                      file=sys.stderr)
    return events


def verify_chain(table: str) -> list[str]:
    """
    Verify the hash chain integrity of a table.
    Returns list of error strings. Empty list = chain is intact.
    """
    events = read_all(table)
    errors = []
    prev_hash = None

    for i, event in enumerate(events):
        stored_hash = event.get("event_hash")
        stored_prev = event.get("previous_event_hash")

        # Check previous_event_hash linkage
        if i > 0 and prev_hash is not None:
            if stored_prev != prev_hash:
                errors.append(
                    f"Line {i+1}: previous_event_hash mismatch. "
                    f"Expected {prev_hash[:12]}… got {str(stored_prev)[:12]}…"
                )

        # Verify event_hash
        if stored_hash:
            # Reconstruct body without event_hash
            body = {k: v for k, v in event.items() if k != "event_hash"}
            body_str = json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
            expected = _sha256(body_str)
            if expected != stored_hash:
                errors.append(
                    f"Line {i+1}: event_hash invalid for event_type={event.get('event_type')}"
                )

        prev_hash = stored_hash

    return errors


def count_events(table: str) -> int:
    path = _table_path(table)
    if not path.exists():
        return 0
    return sum(1 for line in open(path, encoding="utf-8") if line.strip())
