#!/usr/bin/env python3
"""
plan_negotiation_append.py — dango-gitsea-bridge / plan negotiation layer

Append plan negotiation events to sutable/plans.jsonl.

Negotiation events:
  plan_supported      — a speaker signals support for a plan
  plan_objected       — a speaker signals objection (typed, with reason)
  plan_contested      — a competing plan is proposed to contest an existing one
  plan_rejected       — a plan is formally rejected (with reason)
  plan_superseded     — a plan is marked superseded by another
  active_plan_selected — deterministic selection result recorded

Design principles:
  Support and objection are NOT votes.
  They are structured negotiation signals — evidence and concerns.
  The selection algorithm (active_plan_selector.py) is deterministic and
  fully transparent. No hidden ranking. No opaque weighting.

  A plan_contested event may include an embedded 'counterplan' dict.
  If counterplan_id does not yet exist in plans.jsonl, the embedded
  counterplan is appended as plan_tree_created first — atomically
  before the contest event.

Absolute prohibitions:
  - No automatic execution
  - No AI-driven final decisions
  - No hidden scoring
  - No centralized authority
  - No API keys, wallets, or external network calls
  - No deletion or modification of existing events

CLI:
  python runtime/plan_negotiation_append.py examples/plan-support-event.json
  python runtime/plan_negotiation_append.py examples/plan-objection-event.json
  python runtime/plan_negotiation_append.py examples/plan-contest-event.json
  python runtime/plan_negotiation_append.py examples/plan-contest-event.json --dry-run
  python runtime/plan_negotiation_append.py examples/plan-contest-event.json --verbose
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

# ── Event types handled by this module ───────────────────────────────────────

NEGOTIATION_EVENT_TYPES: frozenset[str] = frozenset({
    "plan_supported",
    "plan_objected",
    "plan_contested",
    "plan_rejected",
    "plan_superseded",
    "active_plan_selected",
})

# Valid objection types (typed objections carry structured meaning)
OBJECTION_TYPES: frozenset[str] = frozenset({
    "missing_condition",
    "dignity_violation",
    "insufficient_risk_coverage",
    "plan_tree_invalid",
    "process_violation",
    "incomplete_reasoning",
    "other",
})

# Required fields per event type
_REQUIRED_FIELDS: dict[str, list[str]] = {
    "plan_supported":       ["event_type", "claim_id", "plan_id", "speaker", "support_reason"],
    "plan_objected":        ["event_type", "claim_id", "plan_id", "speaker",
                             "objection_type", "objection_reason"],
    "plan_contested":       ["event_type", "claim_id", "contested_plan_id",
                             "counterplan_id", "contest_reason"],
    "plan_rejected":        ["event_type", "claim_id", "plan_id", "rejection_reason"],
    "plan_superseded":      ["event_type", "claim_id", "plan_id", "superseded_by"],
    "active_plan_selected": ["event_type", "claim_id", "selected_plan_id", "selection_basis"],
}

# Plan event types that establish a plan_id in plans.jsonl
_PLAN_TREE_TYPES: frozenset[str] = frozenset({
    "plan_tree_created",
    "plan_tree_amended",
    "plan_tree_corrected",
})


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _plan_tree_hash(plan_tree: dict[str, Any]) -> str:
    canonical = json.dumps(plan_tree, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return _sha256(canonical)


def _load_event_file(path: str) -> dict[str, Any]:
    try:
        raw = Path(path).read_text(encoding="utf-8")
        return json.loads(raw)
    except FileNotFoundError:
        print(f"plan_negotiation_append: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as exc:
        print(f"plan_negotiation_append: invalid JSON — {exc}", file=sys.stderr)
        sys.exit(2)


def _load_existing_plans() -> dict[str, dict[str, Any]]:
    """Return mapping plan_id → event for all plan_tree_* events in plans.jsonl."""
    result: dict[str, dict[str, Any]] = {}
    try:
        for ev in read_all("plans"):
            pid = ev.get("plan_id")
            if pid and ev.get("event_type") in _PLAN_TREE_TYPES:
                result[pid] = ev
    except Exception:
        pass
    return result


# ── Validation ────────────────────────────────────────────────────────────────

def validate_negotiation_event(
    event: dict[str, Any],
    existing_plans: dict[str, dict[str, Any]],
) -> list[str]:
    """
    Validate a negotiation event before appending.

    Returns list of error strings. Empty = valid.
    """
    errors: list[str] = []
    et = event.get("event_type", "")

    if et not in NEGOTIATION_EVENT_TYPES:
        errors.append(
            f"event_type must be one of {sorted(NEGOTIATION_EVENT_TYPES)}, got {et!r}"
        )
        return errors

    # Required fields
    for field in _REQUIRED_FIELDS.get(et, []):
        if field not in event:
            errors.append(f"missing required field: {field!r}")
    if errors:
        return errors

    # Type-specific validations
    if et == "plan_supported":
        pid = event.get("plan_id", "")
        if pid not in existing_plans:
            errors.append(f"plan_id {pid!r} not found in plans.jsonl")

    elif et == "plan_objected":
        pid = event.get("plan_id", "")
        if pid not in existing_plans:
            errors.append(f"plan_id {pid!r} not found in plans.jsonl")
        otype = event.get("objection_type", "")
        if otype not in OBJECTION_TYPES:
            errors.append(
                f"objection_type {otype!r} unknown. "
                f"Valid: {sorted(OBJECTION_TYPES)}"
            )

    elif et == "plan_contested":
        contested = event.get("contested_plan_id", "")
        if contested not in existing_plans:
            errors.append(f"contested_plan_id {contested!r} not found in plans.jsonl")
        # counterplan_id must exist OR an embedded counterplan must be provided
        cp_id = event.get("counterplan_id", "")
        if cp_id not in existing_plans and "counterplan" not in event:
            errors.append(
                f"counterplan_id {cp_id!r} not found in plans.jsonl and "
                f"no embedded 'counterplan' provided"
            )
        if "counterplan" in event:
            cp = event["counterplan"]
            if not isinstance(cp, dict):
                errors.append("embedded 'counterplan' must be a JSON object")
            elif "plan_tree" not in cp:
                errors.append("embedded 'counterplan' must have a 'plan_tree' field")
            elif cp.get("plan_id", "") != cp_id:
                errors.append(
                    f"embedded counterplan plan_id {cp.get('plan_id')!r} "
                    f"does not match counterplan_id {cp_id!r}"
                )

    elif et == "plan_rejected":
        pid = event.get("plan_id", "")
        if pid not in existing_plans:
            errors.append(f"plan_id {pid!r} not found in plans.jsonl")

    elif et == "plan_superseded":
        pid = event.get("plan_id", "")
        if pid not in existing_plans:
            errors.append(f"plan_id {pid!r} not found in plans.jsonl")
        by_id = event.get("superseded_by", "")
        if by_id and by_id not in existing_plans:
            errors.append(f"superseded_by {by_id!r} not found in plans.jsonl")

    elif et == "active_plan_selected":
        sel_id = event.get("selected_plan_id", "")
        if sel_id not in existing_plans:
            errors.append(f"selected_plan_id {sel_id!r} not found in plans.jsonl")
        basis = event.get("selection_basis")
        if not isinstance(basis, dict):
            errors.append("selection_basis must be a JSON object")

    return errors


# ── Counterplan auto-creation ─────────────────────────────────────────────────

def _create_counterplan_event(
    cp_data: dict[str, Any],
    contest_event: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a plan_tree_created event from embedded counterplan data.
    """
    plan_tree = cp_data.get("plan_tree", {})
    ev: dict[str, Any] = {
        "event_type": "plan_tree_created",
        "claim_id":   contest_event.get("claim_id", ""),
        "plan_id":    cp_data.get("plan_id", ""),
        "plan_tree":  plan_tree,
        "reasoning_surface": "ogi-compatible",
    }
    if "speaker" in cp_data:
        ev["speaker"] = cp_data["speaker"]
    elif "speaker" in contest_event:
        ev["speaker"] = contest_event["speaker"]
    if isinstance(plan_tree, dict):
        ev["plan_tree_hash"] = _plan_tree_hash(plan_tree)
    return ev


# ── Append logic ──────────────────────────────────────────────────────────────

def _strip_counterplan(event: dict[str, Any]) -> dict[str, Any]:
    """Return event dict without the embedded counterplan (not stored inline)."""
    return {k: v for k, v in event.items() if k != "counterplan"}


def append_negotiation_event(
    event: dict[str, Any],
    *,
    dry_run: bool = False,
    verbose: bool = False,
) -> list[dict[str, Any]]:
    """
    Validate and append a negotiation event to sutable/plans.jsonl.

    For plan_contested events with an embedded counterplan, the counterplan
    is first appended as plan_tree_created, then the contest event is appended.

    Returns:
        List of written event dicts (usually 1; 2 for auto-created counterplan).

    Raises:
        SystemExit(1) on validation failure.
        SutableError on append failure.
    """
    existing = _load_existing_plans()
    errors   = validate_negotiation_event(event, existing)

    if errors:
        print("✗ plan_negotiation_append: validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    written_events: list[dict[str, Any]] = []
    et = event.get("event_type", "")

    # ── Auto-create counterplan if embedded ──────────────────────────────────
    if et == "plan_contested":
        cp_id = event.get("counterplan_id", "")
        cp_data = event.get("counterplan")
        if cp_data and cp_id not in existing:
            cp_event = _create_counterplan_event(cp_data, event)
            if dry_run:
                print("── DRY RUN — counterplan event (not written) ──")
                print(json.dumps(cp_event, indent=2, ensure_ascii=False))
            else:
                written_cp = append_event("plans", cp_event)
                written_events.append(written_cp)
                if verbose:
                    print(
                        f"✓ auto-created counterplan: {written_cp.get('plan_id')}",
                        file=sys.stderr,
                    )

    # ── Append the negotiation event itself ───────────────────────────────────
    clean_event = _strip_counterplan(event)

    if dry_run:
        print("── DRY RUN — negotiation event (not written) ──")
        print(json.dumps(clean_event, indent=2, ensure_ascii=False))
        return written_events

    written = append_event("plans", clean_event)
    written_events.append(written)

    if verbose:
        print(f"✓ appended to plans.jsonl", file=sys.stderr)
        print(f"  event_type: {written.get('event_type')}", file=sys.stderr)
        pid = written.get("plan_id") or written.get("contested_plan_id") or written.get("selected_plan_id", "")
        if pid:
            print(f"  plan_id:    {pid}", file=sys.stderr)
        print(f"  event_hash: {written.get('event_hash', '')[:16]}…", file=sys.stderr)

    return written_events


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="plan_negotiation_append",
        description="Append a plan negotiation event to sutable/plans.jsonl.",
    )
    p.add_argument(
        "event_file",
        metavar="EVENT_FILE",
        help="Path to negotiation event JSON file.",
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
    event = _load_event_file(args.event_file)
    written_events = append_negotiation_event(
        event,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )
    if not args.dry_run:
        for ev in written_events:
            print(json.dumps(ev, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
