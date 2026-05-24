#!/usr/bin/env python3
"""
task_bundle_append.py — dango-gitsea-bridge / plan append-only layer

Append a task bundle event to sutable/plans.jsonl.

Task bundle events are append-only:
  - task_bundle_created   — a new task bundle is derived from a plan tree
  - task_bundle_blocked   — the bundle is fully blocked (all gates unresolved)
  - task_bundle_ready     — all gates resolved; bundle ready for negotiation
  - task_bundle_abandoned — the bundle was abandoned (new plan or claim withdrawn)

The derived_from_plan_id field must reference an existing plan in plans.jsonl.
If the plan does not exist, the append is rejected.

Task bundles do NOT execute tasks. They are negotiation proposals.

CLI:
  python runtime/task_bundle_append.py examples/task-bundle-event.json
  python runtime/task_bundle_append.py examples/task-bundle-event.json --dry-run
  python runtime/task_bundle_append.py examples/task-bundle-event.json --verbose
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import append_event, read_all, SutableError

# ── Valid task bundle event types ─────────────────────────────────────────────

BUNDLE_EVENT_TYPES: frozenset[str] = frozenset({
    "task_bundle_created",
    "task_bundle_blocked",
    "task_bundle_ready",
    "task_bundle_abandoned",
})

_REQUIRED_FIELDS: dict[str, list[str]] = {
    "task_bundle_created":   ["event_type", "claim_id", "bundle_id", "derived_from_plan_id"],
    "task_bundle_blocked":   ["event_type", "claim_id", "bundle_id"],
    "task_bundle_ready":     ["event_type", "claim_id", "bundle_id"],
    "task_bundle_abandoned": ["event_type", "claim_id", "bundle_id", "abandoned_reason"],
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _bundle_hash(bundle: dict[str, Any]) -> str:
    canonical = json.dumps(bundle, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return _sha256(canonical)


def _load_event(path: str) -> dict[str, Any]:
    try:
        raw = Path(path).read_text(encoding="utf-8")
        return json.loads(raw)
    except FileNotFoundError:
        print(f"task_bundle_append: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as exc:
        print(f"task_bundle_append: invalid JSON — {exc}", file=sys.stderr)
        sys.exit(2)


def _load_existing_plan_ids() -> set[str]:
    """Return all plan_ids from plans.jsonl that are plan_tree events."""
    ids: set[str] = set()
    try:
        for ev in read_all("plans"):
            pid = ev.get("plan_id")
            et  = ev.get("event_type", "")
            if pid and et in ("plan_tree_created", "plan_tree_amended", "plan_tree_corrected"):
                ids.add(pid)
    except Exception:
        pass
    return ids


def _load_existing_bundle_ids() -> set[str]:
    """Return all bundle_ids from plans.jsonl."""
    ids: set[str] = set()
    try:
        for ev in read_all("plans"):
            bid = ev.get("bundle_id")
            if bid and ev.get("event_type") in BUNDLE_EVENT_TYPES:
                ids.add(bid)
    except Exception:
        pass
    return ids


# ── Validation ────────────────────────────────────────────────────────────────

def validate_bundle_event(
    event: dict[str, Any],
    existing_plan_ids: set[str],
    existing_bundle_ids: set[str],
) -> list[str]:
    """Validate a task bundle event before appending. Returns error list."""
    errors: list[str] = []
    et = event.get("event_type", "")

    if et not in BUNDLE_EVENT_TYPES:
        errors.append(
            f"event_type must be one of {sorted(BUNDLE_EVENT_TYPES)}, got {et!r}"
        )
        return errors

    for field in _REQUIRED_FIELDS.get(et, []):
        if field not in event:
            errors.append(f"missing required field: {field!r}")

    if errors:
        return errors

    bundle_id           = event.get("bundle_id", "")
    derived_from_plan_id = event.get("derived_from_plan_id", "")

    # bundle_id uniqueness for create events
    if et == "task_bundle_created" and bundle_id in existing_bundle_ids:
        errors.append(
            f"bundle_id {bundle_id!r} already exists — use task_bundle_blocked, "
            f"task_bundle_ready, or task_bundle_abandoned for status updates"
        )

    # derived_from_plan_id must exist for create events
    if et == "task_bundle_created" and derived_from_plan_id:
        if derived_from_plan_id not in existing_plan_ids:
            errors.append(
                f"derived_from_plan_id {derived_from_plan_id!r} not found in plans.jsonl — "
                f"append the plan tree event first"
            )

    # Non-create status events: bundle must exist
    if et in ("task_bundle_blocked", "task_bundle_ready", "task_bundle_abandoned"):
        if bundle_id and bundle_id not in existing_bundle_ids:
            errors.append(
                f"bundle_id {bundle_id!r} not found — append task_bundle_created first"
            )

    return errors


# ── Prepare ───────────────────────────────────────────────────────────────────

def prepare_event(event: dict[str, Any]) -> dict[str, Any]:
    """Enrich event with computed fields."""
    event = dict(event)
    task_bundle = event.get("task_bundle")
    if isinstance(task_bundle, dict):
        event["task_bundle_hash"] = _bundle_hash(task_bundle)
        # Copy summary stats to top level for quick access
        summary = task_bundle.get("summary", {})
        event.setdefault("task_count",    summary.get("task_count", 0))
        event.setdefault("blocked_count", summary.get("blocked_count", 0))
        event.setdefault("gate_count",    summary.get("gate_count", 0))
        event.setdefault("bundle_status", task_bundle.get("bundle_status", "unknown"))
    return event


# ── Append ────────────────────────────────────────────────────────────────────

def append_bundle_event(
    event: dict[str, Any],
    *,
    dry_run: bool = False,
    verbose: bool = False,
) -> dict[str, Any]:
    """
    Validate and append a task bundle event to sutable/plans.jsonl.

    Returns the final event dict as written.
    Raises SystemExit(1) on validation failure.
    """
    existing_plan_ids   = _load_existing_plan_ids()
    existing_bundle_ids = _load_existing_bundle_ids()
    errors = validate_bundle_event(event, existing_plan_ids, existing_bundle_ids)

    if errors:
        print("✗ task_bundle_append: validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    event = prepare_event(event)

    if dry_run:
        print("── DRY RUN — event not written ──")
        print(json.dumps(event, indent=2, ensure_ascii=False))
        return event

    written = append_event("plans", event)

    if verbose:
        print(f"✓ appended to plans.jsonl", file=sys.stderr)
        print(f"  bundle_id:  {written.get('bundle_id')}", file=sys.stderr)
        print(f"  event_type: {written.get('event_type')}", file=sys.stderr)
        print(f"  event_hash: {written.get('event_hash', '')[:16]}…", file=sys.stderr)

    return written


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="task_bundle_append",
        description="Append a task bundle event to sutable/plans.jsonl.",
    )
    p.add_argument(
        "event_file",
        metavar="EVENT_FILE",
        help="Path to task bundle event JSON file.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Validate and print the event without writing.",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=False,
        help="Print progress to stderr.",
    )
    return p.parse_args()


def main() -> None:
    args  = _parse_args()
    event = _load_event(args.event_file)
    written = append_bundle_event(
        event,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )
    if not args.dry_run:
        print(json.dumps(written, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
