#!/usr/bin/env python3
"""
plan_correction.py — dango-gitsea-bridge / plan append-only layer

Create a plan_tree_corrected event from an existing plan event.

Correction semantics:
  - The original plan is NOT deleted
  - The correction is appended as a new plan_tree_corrected event
  - corrects_plan_id references the plan being superseded
  - The correction chain can be traversed by plan_snapshot.py
  - The corrected plan remains visible in the graph (dashed edge)

Amendment semantics (--amend flag):
  - Use when a subcomponent of the plan is amended, not the whole plan
  - Appends a plan_tree_amended event instead
  - The amended plan remains active (not superseded)

CLI:
  # Correct a plan (new plan supersedes old)
  python runtime/plan_correction.py examples/plan-event.json \
    --reason "missing dignity branch for owner_consent"

  # Correct with a new plan tree file
  python runtime/plan_correction.py examples/plan-event.json \
    --new-plan examples/plan-event-v2.json \
    --reason "dignity branch order corrected"

  # Amendment (partial update, original plan still active)
  python runtime/plan_correction.py examples/plan-event.json \
    --amend \
    --reason "added note to coordination phase"

  # Dry run
  python runtime/plan_correction.py examples/plan-event.json \
    --reason "test" --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import read_all, SutableError
from plan_event_append import (
    append_plan_event,
    _load_existing_plans,
    _plan_tree_hash,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_json(path: str) -> dict[str, Any]:
    try:
        raw = Path(path).read_text(encoding="utf-8")
        return json.loads(raw)
    except FileNotFoundError:
        print(f"plan_correction: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as exc:
        print(f"plan_correction: invalid JSON — {exc}", file=sys.stderr)
        sys.exit(2)


def _next_version(plan_id: str, existing: dict[str, dict]) -> str:
    """
    Given a plan_id like 'plan-housing-001-v1', return the next version
    e.g. 'plan-housing-001-v2'. If the plan_id doesn't follow the vN suffix
    pattern, append '-v2' (or -v3, etc.) until we find an unused ID.
    """
    # Try to parse vN suffix
    parts = plan_id.rsplit("-v", 1)
    if len(parts) == 2:
        try:
            base    = parts[0]
            version = int(parts[1])
            while True:
                version += 1
                candidate = f"{base}-v{version}"
                if candidate not in existing:
                    return candidate
        except ValueError:
            pass
    # Fallback: append -v2, -v3, ...
    version = 2
    while True:
        candidate = f"{plan_id}-v{version}"
        if candidate not in existing:
            return candidate
        version += 1


def _load_original_plan(
    event_file: str,
    existing: dict[str, dict],
) -> tuple[str, str, dict[str, Any]]:
    """
    Load the original plan event and return (plan_id, claim_id, plan_tree).
    Accepts either a plan event file or a raw plan tree file.
    """
    data = _load_json(event_file)

    # Case 1: it's a plan event (has plan_id and event_type)
    if "plan_id" in data and "event_type" in data:
        plan_id   = data["plan_id"]
        claim_id  = data.get("claim_id", "unknown")
        plan_tree = data.get("plan_tree", data)  # fallback to whole dict
        return plan_id, claim_id, plan_tree

    # Case 2: it's a raw plan tree (has node_type: goal)
    if data.get("node_type") == "goal":
        plan_id  = data.get("plan_tree_id", "plan-unknown-v1")
        claim_id = data.get("claim_id", "unknown")
        # Check if this plan_id exists in the su-table
        if plan_id not in existing:
            print(
                f"plan_correction: plan_id {plan_id!r} from plan tree not found in plans.jsonl.\n"
                f"  Tip: run plan_event_append.py first to persist the plan.",
                file=sys.stderr,
            )
            sys.exit(1)
        return plan_id, claim_id, data

    print(
        f"plan_correction: cannot determine plan_id from {event_file}.\n"
        f"  Expected: a plan event JSON (with plan_id + event_type) or a plan tree JSON (node_type=goal).",
        file=sys.stderr,
    )
    sys.exit(1)


# ── Correction builder ────────────────────────────────────────────────────────

def build_correction_event(
    original_plan_id: str,
    claim_id: str,
    original_plan_tree: dict[str, Any],
    new_plan_tree: dict[str, Any] | None,
    reason: str,
    new_plan_id: str | None = None,
    is_amendment: bool = False,
) -> dict[str, Any]:
    """
    Build a plan_tree_corrected (or plan_tree_amended) event dict.

    Args:
        original_plan_id:   plan_id of the plan being corrected/amended.
        claim_id:           claim this plan belongs to.
        original_plan_tree: the original plan tree dict.
        new_plan_tree:      replacement plan tree (None = use original + mark corrected).
        reason:             human-readable reason for the correction.
        new_plan_id:        explicit new plan_id (auto-generated if None).
        is_amendment:       if True, produce plan_tree_amended instead.

    Returns:
        The new event dict (not yet appended).
    """
    # If no new plan tree provided, use the original plan tree as base
    # (caller expected to have modified it before passing it in, or
    #  this creates a structural correction record without a tree change)
    effective_tree = new_plan_tree if new_plan_tree is not None else original_plan_tree

    if is_amendment:
        event: dict[str, Any] = {
            "event_type":       "plan_tree_amended",
            "claim_id":         claim_id,
            "plan_id":          new_plan_id or _next_version_from_existing(original_plan_id),
            "amends_plan_id":   original_plan_id,
            "amendment_reason": reason,
            "plan_tree":        effective_tree,
        }
    else:
        event = {
            "event_type":        "plan_tree_corrected",
            "claim_id":          claim_id,
            "plan_id":           new_plan_id or _next_version_from_existing(original_plan_id),
            "corrects_plan_id":  original_plan_id,
            "correction_reason": reason,
            "plan_tree":         effective_tree,
        }

    return event


def _next_version_from_existing(plan_id: str) -> str:
    existing = _load_existing_plans()
    return _next_version(plan_id, existing)


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="plan_correction",
        description="Create a correction or amendment event for an existing plan.",
    )
    p.add_argument(
        "plan_file",
        metavar="PLAN_FILE",
        help=(
            "Path to the original plan event JSON file "
            "(must have plan_id + event_type, or be a raw plan tree with node_type=goal)."
        ),
    )
    p.add_argument(
        "--reason",
        required=True,
        help="Human-readable reason for the correction or amendment.",
    )
    p.add_argument(
        "--new-plan",
        metavar="FILE",
        default=None,
        help="Path to a new plan tree JSON file (plan_tree or plan event). "
             "If omitted, the original plan tree is reused as the correction base.",
    )
    p.add_argument(
        "--plan-id",
        metavar="PLAN_ID",
        default=None,
        help="Explicit plan_id for the new correction event (auto-generated if omitted).",
    )
    p.add_argument(
        "--amend",
        action="store_true",
        default=False,
        help="Produce a plan_tree_amended event instead of plan_tree_corrected. "
             "The original plan remains active.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print the correction event without writing.",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=False,
        help="Print progress to stderr.",
    )
    return p.parse_args()


def main() -> None:
    args     = _parse_args()
    existing = _load_existing_plans()

    # Load original plan info
    original_plan_id, claim_id, original_tree = _load_original_plan(
        args.plan_file, existing
    )

    if args.verbose:
        print(f"Original plan: {original_plan_id} (claim: {claim_id})", file=sys.stderr)

    # Verify the plan exists in the su-table
    if original_plan_id not in existing:
        print(
            f"plan_correction: plan_id {original_plan_id!r} not found in plans.jsonl.\n"
            f"  Append the original plan first with plan_event_append.py.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Load new plan tree if provided
    new_tree: dict[str, Any] | None = None
    if args.new_plan:
        new_data = _load_json(args.new_plan)
        if new_data.get("node_type") == "goal":
            new_tree = new_data
        elif "plan_tree" in new_data:
            new_tree = new_data["plan_tree"]
        else:
            new_tree = new_data  # assume raw plan tree

    # Build correction/amendment event
    correction_event = build_correction_event(
        original_plan_id  = original_plan_id,
        claim_id          = claim_id,
        original_plan_tree= original_tree,
        new_plan_tree     = new_tree,
        reason            = args.reason,
        new_plan_id       = args.plan_id,
        is_amendment      = args.amend,
    )

    if args.verbose:
        et = correction_event.get("event_type")
        new_id = correction_event.get("plan_id")
        action = "amends" if args.amend else "corrects"
        print(f"Creating {et}: {new_id} ({action} {original_plan_id})", file=sys.stderr)

    # Append
    written = append_plan_event(
        correction_event,
        dry_run=args.dry_run,
        skip_validation=False,
        verbose=args.verbose,
    )

    if not args.dry_run:
        print(json.dumps(written, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
