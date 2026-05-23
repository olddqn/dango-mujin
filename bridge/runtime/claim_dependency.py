#!/usr/bin/env python3
"""
claim_dependency.py — dango-gitsea-bridge / claim federation

Validate and append claim federation events to sutable/federation.jsonl.

Federation event types:
  claim_dependency  — explicit directional dependency between claims
  counterclaim      — disagreement with an existing claim
  federation_link   — general associative link
  federation_correction — corrects an earlier federation event

Dependency types (in claim_dependency events):
  depends_on      — A cannot proceed without B being active/resolved
  enables         — A's progress enables B to proceed
  blocks          — A explicitly blocks B from proceeding
  counterclaim    — A disputes the validity of B (use counterclaim event_type instead)
  amendment_of    — A proposes a modification to B
  derived_from    — A was created from B (conceptual inheritance)
  federation_link — general associative link (symmetric)
  dignity_override— A's dignity constraints override B's (propagate upward)
  correction_of   — A corrects an earlier federation relationship

Circular dependency rules:
  - Self-reference (A depends_on A) → always rejected
  - Directional cycle (A depends_on B, B depends_on A) → rejected
  - ONLY for: depends_on, blocks, dignity_override
  - counterclaim, derived_from, amendment_of, federation_link → ALLOWED bidirectional

Usage:
  python runtime/claim_dependency.py examples/claim-dependency.json
  python runtime/claim_dependency.py examples/claim-dependency.json --append
  python runtime/claim_dependency.py examples/claim-dependency.json --check-only
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import read_all, append_event, SutableError

# ── Relationship taxonomy ──────────────────────────────────────

DEPENDENCY_TYPES = frozenset({
    "depends_on",
    "enables",
    "blocks",
    "counterclaim",
    "amendment_of",
    "derived_from",
    "federation_link",
    "dignity_override",
    "correction_of",
})

# Only these directional types are checked for circular dependency
# (A→B and B→A simultaneously is forbidden for these)
CIRCULAR_CHECKED_TYPES = frozenset({
    "depends_on",
    "blocks",
    "dignity_override",
})

FEDERATION_EVENT_TYPES = frozenset({
    "claim_dependency",
    "counterclaim",
    "federation_link",
    "federation_correction",
})


# ── Graph helpers ──────────────────────────────────────────────

def load_existing_graph() -> dict[str, set[tuple[str, str]]]:
    """
    Load all federation events and return a graph of directional edges.

    Returns:
      {(from_claim, dep_type): {to_claim, ...}, ...}
      simplified as: {"from_claim": {("dep_type", "to_claim"), ...}}
    """
    graph: dict[str, set[tuple[str, str]]] = {}

    try:
        events = read_all("federation")
    except Exception:
        events = []

    for e in events:
        et = e.get("event_type", "")
        if et == "claim_dependency":
            src = e.get("claim_id", "")
            dst = e.get("depends_on_claim_id", "")
            dep = e.get("dependency_type", "")
            if src and dst and dep in CIRCULAR_CHECKED_TYPES:
                graph.setdefault(src, set()).add((dep, dst))
        elif et == "counterclaim":
            # counterclaims are NOT checked for circularity
            pass

    return graph


def _is_reachable(
    start: str,
    target: str,
    graph: dict[str, set[tuple[str, str]]],
    dep_type: str,
    visited: Optional[set[str]] = None,
) -> bool:
    """
    Return True if `target` is reachable from `start` via `dep_type` edges.
    Used for circular dependency detection.
    """
    if visited is None:
        visited = set()
    if start in visited:
        return False
    visited.add(start)

    for (dt, dst) in graph.get(start, set()):
        if dt == dep_type:
            if dst == target:
                return True
            if _is_reachable(dst, target, graph, dep_type, visited):
                return True
    return False


# ── Validation ────────────────────────────────────────────────

def validate_federation_event(
    event: dict,
    existing_graph: Optional[dict[str, set[tuple[str, str]]]] = None,
) -> tuple[bool, str]:
    """
    Validate a federation event.

    Returns:
      (True, "ok")            — valid
      (False, reason_string)  — invalid with reason
    """
    et = event.get("event_type", "")

    if et not in FEDERATION_EVENT_TYPES:
        return False, (
            f"Unknown event_type: '{et}'. "
            f"Expected one of: {sorted(FEDERATION_EVENT_TYPES)}"
        )

    claim_id = event.get("claim_id", "")
    if not claim_id:
        return False, "claim_id is required."

    # ── claim_dependency validation ────────────────────────────
    if et == "claim_dependency":
        depends_on = event.get("depends_on_claim_id", "")
        dep_type   = event.get("dependency_type", "")

        if not depends_on:
            return False, "depends_on_claim_id is required for claim_dependency events."

        if dep_type not in DEPENDENCY_TYPES:
            return False, (
                f"Invalid dependency_type: '{dep_type}'. "
                f"Expected one of: {sorted(DEPENDENCY_TYPES)}"
            )

        # Self-reference check (always forbidden regardless of type)
        if claim_id == depends_on:
            return False, (
                f"Self-reference forbidden: claim_id == depends_on_claim_id "
                f"('{claim_id}'). A claim cannot depend on itself."
            )

        # Circular dependency check (only for CIRCULAR_CHECKED_TYPES)
        if dep_type in CIRCULAR_CHECKED_TYPES:
            graph = existing_graph if existing_graph is not None else load_existing_graph()
            # Would adding claim_id -dep_type-> depends_on create a cycle?
            # A cycle exists if depends_on can already reach claim_id via dep_type
            if _is_reachable(depends_on, claim_id, graph, dep_type):
                return False, (
                    f"Circular dependency detected: adding "
                    f"'{claim_id}' --{dep_type}--> '{depends_on}' "
                    f"would create a cycle. Dependency rejected."
                )

    # ── counterclaim validation ────────────────────────────────
    elif et == "counterclaim":
        target = event.get("counterclaim_to", "")
        if not target:
            return False, "counterclaim_to is required for counterclaim events."
        # Note: bidirectional counterclaims ARE allowed in Dan-Go.
        # Disagreement is part of the protocol.
        if claim_id == target:
            return False, (
                f"Self-counterclaim forbidden: a claim cannot counterclaim itself "
                f"('{claim_id}')."
            )

    # ── federation_link validation ─────────────────────────────
    elif et == "federation_link":
        linked = event.get("linked_claim_id", "")
        if not linked:
            return False, "linked_claim_id is required for federation_link events."
        if claim_id == linked:
            return False, "Self-link forbidden: claim_id == linked_claim_id."

    # ── federation_correction validation ──────────────────────
    elif et == "federation_correction":
        corrects = event.get("corrects_event_hash", "")
        if not corrects:
            return False, "corrects_event_hash is required for federation_correction events."

    return True, "ok"


def normalize_federation_event(event: dict) -> dict:
    """
    Return a normalized copy of the event.
    Adds default fields where appropriate.
    Does not mutate the input.
    """
    out = dict(event)
    # Ensure reason is present as empty string if absent
    if "reason" not in out:
        out["reason"] = ""
    return out


# ── CLI ───────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Validate (and optionally append) a claim federation event.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate only
  python runtime/claim_dependency.py examples/claim-dependency.json

  # Validate and append to federation.jsonl
  python runtime/claim_dependency.py examples/claim-dependency.json --append

  # Check without loading existing graph (faster, no circular detection)
  python runtime/claim_dependency.py examples/claim-dependency.json --check-only
        """,
    )
    p.add_argument("event_file", metavar="EVENT_FILE",
                   help="Path to a JSON federation event file")
    p.add_argument("--append", action="store_true",
                   help="Append to sutable/federation.jsonl if valid")
    p.add_argument("--check-only", action="store_true",
                   help="Validate structure only (skip circular detection against live graph)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    path = Path(args.event_file)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(path, encoding="utf-8") as f:
            event = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(event, dict):
        print("Error: event must be a JSON object.", file=sys.stderr)
        sys.exit(1)

    existing_graph = {} if args.check_only else None
    valid, reason = validate_federation_event(event, existing_graph)

    if not valid:
        print(f"✗ Validation FAILED: {reason}", file=sys.stderr)
        print(json.dumps({"valid": False, "reason": reason}, indent=2, ensure_ascii=False))
        sys.exit(1)

    event = normalize_federation_event(event)
    print(json.dumps({"valid": True, "reason": reason, "event": event}, indent=2, ensure_ascii=False))

    if args.append:
        try:
            written = append_event("federation", event, chain=True)
            print(f"\n✓ Appended to sutable/federation.jsonl", file=sys.stderr)
            print(f"  event_type: {written['event_type']}", file=sys.stderr)
            print(f"  event_hash: {written['event_hash'][:16]}…", file=sys.stderr)
        except SutableError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
