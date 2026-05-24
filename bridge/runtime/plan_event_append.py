#!/usr/bin/env python3
"""
plan_event_append.py — dango-gitsea-bridge / plan append-only layer

Append a plan_tree event to sutable/plans.jsonl.

Plan events are append-only:
  - plan_tree_created   — a new plan tree is proposed
  - plan_tree_amended   — a subcomponent is amended (plan still active)
  - plan_tree_corrected — a full correction (new plan replaces old structurally)

Validation is required before append. A plan tree that fails structural
validation is rejected — it is not appended to the su-table.

The plan tree itself is stored inline in the event so the su-table is
self-contained. The plan_tree_hash is a sha256 of the serialised plan tree.

Correction policy:
  - corrects_plan_id references the plan being superseded
  - The original plan is NOT deleted — it remains in plans.jsonl
  - The correction is appended as a new event
  - plan_snapshot.py resolves which plan is "active"

CLI:
  python runtime/plan_event_append.py examples/plan-event.json
  python runtime/plan_event_append.py examples/plan-event.json --dry-run
  python runtime/plan_event_append.py examples/plan-event.json --no-validate
  python runtime/plan_event_append.py examples/plan-event.json --verbose
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
# Also add ogi/runtime so plan_tree_validator is importable from here
_OGI_RUNTIME = Path(__file__).parent.parent / "ogi" / "runtime"
if _OGI_RUNTIME.exists():
    sys.path.insert(0, str(_OGI_RUNTIME))

from sutable_log import append_event, read_all, SutableError

# Import validator (graceful fallback)
try:
    from plan_tree_validator import validate_plan_tree, ValidationResult
    _VALIDATOR_AVAILABLE = True
except ImportError:
    _VALIDATOR_AVAILABLE = False

# ── Valid plan event types ────────────────────────────────────────────────────

PLAN_EVENT_TYPES: frozenset[str] = frozenset({
    "plan_tree_created",
    "plan_tree_amended",
    "plan_tree_corrected",
})

# Required fields per event type
_REQUIRED_FIELDS: dict[str, list[str]] = {
    "plan_tree_created":   ["event_type", "claim_id", "plan_id", "plan_tree"],
    "plan_tree_amended":   ["event_type", "claim_id", "plan_id", "amends_plan_id", "plan_tree", "amendment_reason"],
    "plan_tree_corrected": ["event_type", "claim_id", "plan_id", "corrects_plan_id", "plan_tree", "correction_reason"],
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _plan_tree_hash(plan_tree: dict[str, Any]) -> str:
    """Stable SHA256 hash of a plan tree (sorted keys, compact JSON)."""
    canonical = json.dumps(plan_tree, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return _sha256(canonical)


def _load_event(path: str) -> dict[str, Any]:
    try:
        raw = Path(path).read_text(encoding="utf-8")
        return json.loads(raw)
    except FileNotFoundError:
        print(f"plan_event_append: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as exc:
        print(f"plan_event_append: invalid JSON — {exc}", file=sys.stderr)
        sys.exit(2)


def _load_existing_plans() -> dict[str, dict[str, Any]]:
    """Return mapping plan_id → event for all plan_tree_* events in plans.jsonl."""
    result: dict[str, dict[str, Any]] = {}
    try:
        for ev in read_all("plans"):
            pid = ev.get("plan_id")
            if pid and ev.get("event_type") in PLAN_EVENT_TYPES:
                result[pid] = ev
    except Exception:
        pass
    return result


# ── Validation ────────────────────────────────────────────────────────────────

def validate_plan_event(
    event: dict[str, Any],
    existing_plans: dict[str, dict[str, Any]],
    skip_tree_validation: bool = False,
) -> list[str]:
    """
    Validate a plan event before appending.

    Returns a list of error strings. Empty = valid.
    """
    errors: list[str] = []
    et = event.get("event_type", "")

    # ── Check event_type ──────────────────────────────────────
    if et not in PLAN_EVENT_TYPES:
        errors.append(
            f"event_type must be one of {sorted(PLAN_EVENT_TYPES)}, got {et!r}"
        )
        return errors  # can't proceed without a valid type

    # ── Check required fields ─────────────────────────────────
    for field in _REQUIRED_FIELDS.get(et, []):
        if field not in event:
            errors.append(f"missing required field: {field!r}")

    if errors:
        return errors

    plan_id = event.get("plan_id", "")
    plan_tree = event.get("plan_tree")

    # ── plan_id uniqueness (for create events) ────────────────
    if et == "plan_tree_created":
        if plan_id in existing_plans:
            errors.append(
                f"plan_id {plan_id!r} already exists — use plan_tree_corrected "
                f"or plan_tree_amended for updates"
            )

    # ── corrects_plan_id must exist ───────────────────────────
    if et == "plan_tree_corrected":
        corrects = event.get("corrects_plan_id", "")
        if corrects and corrects not in existing_plans:
            errors.append(
                f"corrects_plan_id {corrects!r} not found in plans.jsonl"
            )

    # ── amends_plan_id must exist ─────────────────────────────
    if et == "plan_tree_amended":
        amends = event.get("amends_plan_id", "")
        if amends and amends not in existing_plans:
            errors.append(
                f"amends_plan_id {amends!r} not found in plans.jsonl"
            )

    # ── Plan tree structural validation ───────────────────────
    if not skip_tree_validation and plan_tree is not None:
        if not isinstance(plan_tree, dict):
            errors.append("plan_tree must be a JSON object (dict)")
        elif not _VALIDATOR_AVAILABLE:
            errors.append(
                "plan_tree_validator not available — use --no-validate to skip"
            )
        else:
            result: ValidationResult = validate_plan_tree(plan_tree)
            if not result.valid:
                for e in result.errors:
                    errors.append(f"plan_tree invalid: {e}")

    return errors


# ── Append ────────────────────────────────────────────────────────────────────

def prepare_event(event: dict[str, Any]) -> dict[str, Any]:
    """
    Enrich a plan event with computed fields before appending:
      - plan_tree_hash (sha256 of the plan_tree contents)
      - reasoning_surface (always "ogi-compatible")
    """
    event = dict(event)
    plan_tree = event.get("plan_tree")
    if isinstance(plan_tree, dict):
        event["plan_tree_hash"] = _plan_tree_hash(plan_tree)
    event.setdefault("reasoning_surface", "ogi-compatible")
    return event


def append_plan_event(
    event: dict[str, Any],
    *,
    dry_run: bool = False,
    skip_validation: bool = False,
    verbose: bool = False,
) -> dict[str, Any]:
    """
    Validate and append a plan event to sutable/plans.jsonl.

    Args:
        event:           Plan event dict.
        dry_run:         If True, validate and print but do not write.
        skip_validation: If True, skip plan tree structural validation.
        verbose:         If True, print progress to stderr.

    Returns:
        The final event dict as written (with event_hash added).

    Raises:
        SystemExit(1) on validation failure.
        SutableError on append failure.
    """
    existing = _load_existing_plans()
    errors   = validate_plan_event(event, existing, skip_tree_validation=skip_validation)

    if errors:
        print("✗ plan_event_append: validation failed:", file=sys.stderr)
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
        print(f"  plan_id:    {written.get('plan_id')}", file=sys.stderr)
        print(f"  event_type: {written.get('event_type')}", file=sys.stderr)
        print(f"  event_hash: {written.get('event_hash', '')[:16]}…", file=sys.stderr)

    return written


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="plan_event_append",
        description="Append a plan tree event to sutable/plans.jsonl.",
    )
    p.add_argument(
        "event_file",
        metavar="EVENT_FILE",
        help="Path to plan event JSON file.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Validate and print the event without writing.",
    )
    p.add_argument(
        "--no-validate",
        action="store_true",
        default=False,
        help="Skip plan tree structural validation.",
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
    written = append_plan_event(
        event,
        dry_run=args.dry_run,
        skip_validation=args.no_validate,
        verbose=args.verbose,
    )
    if not args.dry_run:
        print(json.dumps(written, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
