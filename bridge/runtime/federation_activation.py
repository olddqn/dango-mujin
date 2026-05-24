#!/usr/bin/env python3
"""
federation_activation.py — dango-gitsea-bridge / federation branching

Compute a federation-wide activation snapshot: which claims are active,
paused, or blocked, and what events can be generated to record those states.

An activation snapshot captures the readiness of all claims in a federation
at a point in time. It is derived from:
  - federation dependency graph (federation.jsonl)
  - plan negotiation state (plans.jsonl)
  - existing propagation events (federation.jsonl)

This module can also APPEND activation events:
  - federation_claim_activated — claim is now unblocked and ready
  - federation_claim_paused    — claim is waiting on upstream

These events are advisory records. They do not execute plans.

CLI:
  python runtime/federation_activation.py
  python runtime/federation_activation.py --json
  python runtime/federation_activation.py --append
  python runtime/federation_activation.py --dry-run
  python runtime/federation_activation.py --claim-id housing-002
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import read_all, append_event
from claim_federation import load_federation_events, build_federation_map
from federation_branching import compute_branch_status, compute_all_branch_statuses


# ── Snapshot computation ──────────────────────────────────────────────────────

def compute_activation_snapshot(
    fmap: dict[str, Any],
    fed_events: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Compute the full federation activation snapshot.

    Returns:
      {
        "claim_count":   int,
        "active":        [claim_id, ...],
        "paused":        [claim_id, ...],
        "blocked":       [claim_id, ...],
        "unknown":       [claim_id, ...],
        "federation_readiness": "ready" | "partial" | "blocked",
        "branch_statuses": { claim_id: {...} },
        "summary": str,
      }
    """
    statuses = compute_all_branch_statuses(fmap, fed_events)

    active:  list[str] = []
    paused:  list[str] = []
    blocked: list[str] = []
    unknown: list[str] = []

    for cid, st in sorted(statuses.items()):
        bs = st["branch_status"]
        if bs == "active":
            active.append(cid)
        elif bs == "paused":
            paused.append(cid)
        elif bs == "blocked":
            blocked.append(cid)
        else:
            unknown.append(cid)

    total = len(statuses)
    if blocked:
        readiness = "blocked"
    elif paused:
        readiness = "partial"
    else:
        readiness = "ready"

    parts: list[str] = []
    if active:
        parts.append(f"{len(active)} active")
    if paused:
        parts.append(f"{len(paused)} paused")
    if blocked:
        parts.append(f"{len(blocked)} blocked")
    summary = "; ".join(parts) if parts else "no claims"

    return {
        "claim_count":         total,
        "active":              active,
        "paused":              paused,
        "blocked":             blocked,
        "unknown":             unknown,
        "federation_readiness": readiness,
        "branch_statuses":     statuses,
        "summary":             summary,
    }


# ── Build events from snapshot ────────────────────────────────────────────────

def build_activation_events(
    snapshot: dict[str, Any],
    fed_events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Build federation_claim_activated and federation_claim_paused events
    for claims whose status has changed since the last recorded event.

    Avoids duplicate events: only appends if the last recorded event for
    a claim has a different status.
    """
    # Find the last recorded activation/pause event per claim
    last_status: dict[str, str] = {}
    for ev in fed_events:
        et  = ev.get("event_type", "")
        cid = ev.get("claim_id", "")
        if not cid:
            continue
        if et == "federation_claim_activated":
            last_status[cid] = "active"
        elif et == "federation_claim_paused":
            last_status[cid] = "paused"

    events: list[dict[str, Any]] = []
    statuses = snapshot.get("branch_statuses", {})

    for cid in sorted(statuses):
        current   = statuses[cid]["branch_status"]
        previous  = last_status.get(cid)
        bs_detail = statuses[cid]

        if current == "active" and previous != "active":
            # Determine activation reason
            deps = bs_detail.get("activation_dependencies", [])
            met_by = [d["claim_id"] for d in deps if d["status"] == "met"]
            reason = (
                f"dependent claim(s) reached dignity-safe active state: {met_by}"
                if met_by else "self-standing claim — no upstream dependencies"
            )
            events.append({
                "event_type":        "federation_claim_activated",
                "claim_id":          cid,
                "activation_reason": reason,
                "activated_by_claim": met_by[0] if met_by else "",
            })

        elif current == "paused" and previous != "paused":
            pausing = bs_detail.get("pausing_claims", [])
            reason  = f"waiting on upstream claim(s): {pausing}" if pausing else "upstream unresolved"
            events.append({
                "event_type":   "federation_claim_paused",
                "claim_id":     cid,
                "pause_reason": reason,
                "waiting_on":   pausing,
            })

    return events


# ── Append ────────────────────────────────────────────────────────────────────

def append_activation_events(
    events: list[dict[str, Any]],
    *,
    dry_run: bool = False,
    verbose: bool = False,
) -> list[dict[str, Any]]:
    if not events:
        if verbose:
            print("No new activation events to append.", file=sys.stderr)
        return []

    written: list[dict[str, Any]] = []
    for ev in events:
        if dry_run:
            print(f"[DRY RUN] would append: {ev['event_type']} → {ev.get('claim_id')}")
            written.append(ev)
        else:
            result = append_event("federation", ev)
            written.append(result)
            if verbose:
                print(f"✓ {result['event_type']:35s}  {result['claim_id']}", file=sys.stderr)

    return written


# ── Display ───────────────────────────────────────────────────────────────────

def _print_snapshot(snapshot: dict[str, Any], verbose: bool) -> None:
    print(f"Federation Activation Snapshot")
    print(f"  total claims:          {snapshot['claim_count']}")
    print(f"  federation_readiness:  {snapshot['federation_readiness']}")
    print(f"  summary:               {snapshot['summary']}")

    status_map = snapshot.get("branch_statuses", {})
    icons = {"active": "✓", "paused": "⏸", "blocked": "✗", "unknown": "?"}

    print(f"\n  Claim statuses:")
    for cid in sorted(status_map):
        bs  = status_map[cid]["branch_status"]
        neg = status_map[cid].get("negotiation_status", "")
        neg_str = f"  [{neg}]" if neg and neg != "unknown" else ""
        print(f"    {icons.get(bs,'?')} {cid:20s}  {bs}{neg_str}")

    if verbose:
        print(f"\n  Details:")
        for cid in sorted(status_map):
            deps = status_map[cid].get("activation_dependencies", [])
            if deps:
                print(f"    {cid}:")
                for d in deps:
                    di = icons.get(d["status"], "?")
                    print(f"      {di} {d['claim_id']}  ({d['relationship']})  "
                          f"→ {d['status']}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="federation_activation",
        description=(
            "Compute federation-wide claim activation snapshot. "
            "Optionally append activation events to federation.jsonl."
        ),
    )
    p.add_argument("--claim-id",  metavar="CLAIM_ID",
                   help="Show activation status for one claim only")
    p.add_argument("--append",   action="store_true",
                   help="Append activation/pause events to federation.jsonl")
    p.add_argument("--dry-run",  action="store_true")
    p.add_argument("--json",     action="store_true", dest="json_output")
    p.add_argument("--verbose", "-v", action="store_true")
    return p.parse_args()


def main() -> None:
    args = _parse_args()

    fed_events = load_federation_events()
    fmap       = build_federation_map(fed_events)

    snapshot = compute_activation_snapshot(fmap, fed_events)

    if args.claim_id:
        bs = snapshot["branch_statuses"].get(args.claim_id)
        if not bs:
            print(f"claim_id '{args.claim_id}' not in federation.", file=sys.stderr)
            sys.exit(1)
        out = {"claim_id": args.claim_id, **bs}
        if args.json_output:
            print(json.dumps(out, indent=2, ensure_ascii=False))
        else:
            icons = {"active": "✓", "paused": "⏸", "blocked": "✗"}
            print(f"{icons.get(bs['branch_status'],'?')} {args.claim_id}  "
                  f"[{bs['branch_status']}]")
            for d in bs.get("activation_dependencies", []):
                di = icons.get(d["status"], "?")
                print(f"  {di} {d['claim_id']}  ({d['relationship']})  → {d['status']}")
        return

    if args.append or args.dry_run:
        events = build_activation_events(snapshot, fed_events)
        written = append_activation_events(
            events, dry_run=args.dry_run, verbose=args.verbose
        )
        if args.json_output:
            out = {"snapshot": snapshot, "events_appended": written}
            print(json.dumps(out, indent=2, ensure_ascii=False))
        elif not args.dry_run:
            _print_snapshot(snapshot, verbose=args.verbose)
        return

    if args.json_output:
        print(json.dumps(snapshot, indent=2, ensure_ascii=False))
    else:
        _print_snapshot(snapshot, verbose=args.verbose)


if __name__ == "__main__":
    main()
