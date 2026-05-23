#!/usr/bin/env python3
"""
claim_federation.py — dango-gitsea-bridge / claim federation

Build and query the federation map from su-table federation events.

A federation map is a dict keyed by claim_id, storing all relationships
that claim participates in — as source and as target.

Public API:
  load_federation_events()         → list[dict]
  build_federation_map(events)     → dict
  get_claim_summary(claim_id, map) → dict
  list_claim_ids(map)              → list[str]
  compute_federation_depth(claim_id, map, max_depth) → int

CLI:
  python runtime/claim_federation.py                         (read from su-table)
  python runtime/claim_federation.py examples/claim-federation.json
  python runtime/claim_federation.py --claim-id housing-001
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import read_all

# ── Federation event field extraction ─────────────────────────

def _extract_relationships(event: dict) -> list[tuple[str, str, str, str]]:
    """
    Return (src_claim, rel_type, dst_claim, reason) tuples from an event.
    May return multiple tuples if an event implies both directions.
    """
    et     = event.get("event_type", "")
    reason = event.get("reason", "")

    if et == "claim_dependency":
        src  = event.get("claim_id", "")
        dst  = event.get("depends_on_claim_id", "")
        dep  = event.get("dependency_type", "depends_on")
        if src and dst:
            return [(src, dep, dst, reason)]

    elif et == "counterclaim":
        src = event.get("claim_id", "")
        dst = event.get("counterclaim_to", "")
        if src and dst:
            return [(src, "counterclaim", dst, reason)]

    elif et == "federation_link":
        src = event.get("claim_id", "")
        dst = event.get("linked_claim_id", "")
        if src and dst:
            # Symmetric: store both directions
            return [
                (src, "federation_link", dst, reason),
                (dst, "federation_link", src, reason),
            ]

    elif et == "federation_correction":
        src = event.get("claim_id", "")
        if src:
            return [(src, "correction_of", src, reason)]  # self-referential correction

    return []


# ── Build federation map ───────────────────────────────────────

def build_federation_map(events: list[dict]) -> dict[str, dict]:
    """
    Build a complete federation map from a list of federation events.

    Returns:
      {
        claim_id: {
          "depends_on":      [claim_id, ...],  # outgoing: A depends on B
          "enables":         [claim_id, ...],  # outgoing: A enables B
          "blocks":          [claim_id, ...],  # outgoing: A blocks B
          "counterclaims":   [claim_id, ...],  # outgoing: A counterclaims B
          "amendment_of":    [claim_id, ...],  # outgoing: A amends B
          "derived_from":    [claim_id, ...],  # outgoing: A derived from B
          "federation_link": [claim_id, ...],  # symmetric
          "dignity_override":[claim_id, ...],  # outgoing
          "correction_of":   [claim_id, ...],  # outgoing
          "enabled_by":      [claim_id, ...],  # incoming: B enables A
          "blocked_by":      [claim_id, ...],  # incoming: B blocks A
          "counterclaimed_by":[claim_id, ...], # incoming: B counterclaims A
          "depended_on_by":  [claim_id, ...],  # incoming: B depends on A
        }
      }
    """
    # All claim IDs appearing anywhere
    all_claims: set[str] = set()

    # Collect all (src, rel, dst) relationships
    rels: list[tuple[str, str, str]] = []
    for event in events:
        for src, rel, dst, _ in _extract_relationships(event):
            all_claims.add(src)
            all_claims.add(dst)
            rels.append((src, rel, dst))

    # Initialize empty map for all claims
    def _empty() -> dict:
        return {
            "depends_on":       [],
            "enables":          [],
            "blocks":           [],
            "counterclaims":    [],
            "amendment_of":     [],
            "derived_from":     [],
            "federation_link":  [],
            "dignity_override": [],
            "correction_of":    [],
            # Incoming (reverse)
            "enabled_by":       [],
            "blocked_by":       [],
            "counterclaimed_by":[],
            "depended_on_by":   [],
        }

    fmap: dict[str, dict] = {cid: _empty() for cid in all_claims}

    # Semantic convention for claim_dependency events:
    #   src (claim_id)          = the DOWNSTREAM claim making the statement
    #   dst (depends_on_claim_id) = the UPSTREAM claim
    #
    #   "depends_on"     → src depends on dst      → src.depends_on=[dst], dst.depended_on_by=[src]
    #   "enables"        → dst ENABLES src          → dst.enables=[src], src.enabled_by=[dst]
    #   "blocks"         → dst BLOCKS src           → dst.blocks=[src], src.blocked_by=[dst]
    #   "dignity_override"→ dst overrides src's dignity → dst.dignity_override=[src]
    #   others (amendment_of, derived_from, correction_of) → src.{type}=[dst]
    #   "counterclaim"   → handled by separate event type
    #   "federation_link" → symmetric: both src and dst link each other

    for (src, rel, dst) in rels:
        def _add(claim: str, key: str, target: str) -> None:
            if target not in fmap[claim][key]:
                fmap[claim][key].append(target)

        if rel == "depends_on":
            _add(src, "depends_on", dst)
            _add(dst, "depended_on_by", src)
        elif rel == "enables":
            # dst (upstream) enables src (downstream)
            _add(dst, "enables", src)
            _add(src, "enabled_by", dst)
        elif rel == "blocks":
            # dst (upstream) blocks src (downstream)
            _add(dst, "blocks", src)
            _add(src, "blocked_by", dst)
        elif rel == "counterclaim":
            _add(src, "counterclaims", dst)
            _add(dst, "counterclaimed_by", src)
        elif rel == "federation_link":
            _add(src, "federation_link", dst)
            _add(dst, "federation_link", src)
        elif rel == "dignity_override":
            # dst overrides dignity constraints for src
            _add(dst, "dignity_override", src)
        elif rel in ("amendment_of", "derived_from", "correction_of"):
            _add(src, rel, dst)
        else:
            # unknown rel type — store as outgoing from src
            if rel in fmap[src]:
                _add(src, rel, dst)

    return fmap


def load_federation_events() -> list[dict]:
    """Load all events from sutable/federation.jsonl."""
    try:
        return list(read_all("federation"))
    except Exception:
        return []


# ── Summary + depth computation ────────────────────────────────

def compute_federation_depth(
    claim_id: str,
    fmap: dict[str, dict],
    max_depth: int = 20,
    _visited: Optional[set[str]] = None,
) -> int:
    """
    Compute the maximum federation depth reachable from claim_id.
    Follows: enables, depends_on, derived_from, amendment_of edges (outgoing).
    Stops at max_depth to prevent runaway on large networks.
    """
    if _visited is None:
        _visited = set()
    if claim_id in _visited or max_depth <= 0:
        return 0
    _visited.add(claim_id)

    info = fmap.get(claim_id, {})
    reachable = set(
        info.get("enables", []) +
        info.get("depends_on", []) +
        info.get("derived_from", []) +
        info.get("amendment_of", [])
    )

    if not reachable:
        return 1

    max_sub = max(
        compute_federation_depth(c, fmap, max_depth - 1, _visited)
        for c in reachable
    )
    return 1 + max_sub


def get_claim_summary(claim_id: str, fmap: dict[str, dict]) -> dict:
    """
    Return a compact summary dict for a claim_id within the federation.
    """
    info = fmap.get(claim_id, {})
    depth = compute_federation_depth(claim_id, fmap)

    return {
        "claim_id":          claim_id,
        "depends_on":        info.get("depends_on", []),
        "enables":           info.get("enables", []),
        "blocks":            info.get("blocks", []),
        "blocked_by":        info.get("blocked_by", []),
        "counterclaims":     info.get("counterclaims", []),
        "counterclaimed_by": info.get("counterclaimed_by", []),
        "amendment_of":      info.get("amendment_of", []),
        "derived_from":      info.get("derived_from", []),
        "enabled_by":        info.get("enabled_by", []),
        "depended_on_by":    info.get("depended_on_by", []),
        "federation_link":   info.get("federation_link", []),
        "dignity_override":  info.get("dignity_override", []),
        "federation_depth":  depth,
    }


def list_claim_ids(fmap: dict[str, dict]) -> list[str]:
    return sorted(fmap.keys())


# ── CLI ───────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Build and query the claim federation map.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Read from su-table
  python runtime/claim_federation.py

  # Read from a JSON events file (list of federation events)
  python runtime/claim_federation.py examples/claim-federation.json

  # Show summary for specific claim
  python runtime/claim_federation.py --claim-id housing-001
  python runtime/claim_federation.py examples/claim-federation.json --claim-id housing-001
        """,
    )
    p.add_argument("events_file", metavar="EVENTS_FILE", nargs="?",
                   help="JSON file containing a list of federation events (default: read su-table)")
    p.add_argument("--claim-id", metavar="ID",
                   help="Show summary for this specific claim_id")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.events_file:
        path = Path(args.events_file)
        if not path.exists():
            print(f"Error: file not found: {path}", file=sys.stderr)
            sys.exit(1)
        with open(path, encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error: invalid JSON: {e}", file=sys.stderr)
                sys.exit(1)
        events = data if isinstance(data, list) else [data]
    else:
        events = load_federation_events()

    if not events:
        print("No federation events found.", file=sys.stderr)
        print(json.dumps({"federation_map": {}, "claim_ids": []}, indent=2))
        return

    fmap = build_federation_map(events)

    if args.claim_id:
        if args.claim_id not in fmap:
            print(f"claim_id '{args.claim_id}' not found in federation events.", file=sys.stderr)
            all_ids = list_claim_ids(fmap)
            print(f"Known claim IDs: {all_ids}", file=sys.stderr)
            sys.exit(1)
        result = get_claim_summary(args.claim_id, fmap)
    else:
        result = {
            "claim_ids": list_claim_ids(fmap),
            "summaries": {cid: get_claim_summary(cid, fmap) for cid in fmap},
        }

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
