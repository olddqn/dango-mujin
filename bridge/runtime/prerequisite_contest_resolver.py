#!/usr/bin/env python3
"""
prerequisite_contest_resolver.py — dango-gitsea-bridge / prerequisite promotion

Contest, reaffirm, or deprecate a federation prerequisite.

A promoted prerequisite is not permanent. Any participant can contest it
by proposing a plan tree that does NOT include the condition, and explaining
why the convergence was spurious or the condition is not truly necessary.

Contest resolution:
  - reaffirmed: the prerequisite stands (new convergence evidence, or objection withdrawn)
  - deprecated: the prerequisite is withdrawn (plan tree evidence refutes it)

Design invariants:
  - No arbiter. No authority. Contest events are evidence, not decisions.
  - Append-only. A deprecated prerequisite can be re-promoted with new evidence.
  - The contest history is permanent and auditable.
  - "A learned prerequisite can be contested by producing a better plan tree."

CLI:
  # List all prerequisites with contest status
  python runtime/prerequisite_contest_resolver.py

  # Contest a prerequisite
  python runtime/prerequisite_contest_resolver.py \\
      --contest space_safety_assessed \\
      --reason "..." \\
      --speaker did:key:zContester

  # Reaffirm
  python runtime/prerequisite_contest_resolver.py \\
      --reaffirm space_safety_assessed \\
      --reason "..." \\
      --speaker did:key:zReaffirmer

  # Deprecate
  python runtime/prerequisite_contest_resolver.py \\
      --deprecate space_safety_assessed \\
      --reason "..." \\
      --speaker did:key:zDeprecater

  # JSON output
  python runtime/prerequisite_contest_resolver.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import read_all, append_event
from claim_federation import load_federation_events

# ── Prerequisite event type constants ─────────────────────────────────────────

PROMOTED    = "federation_prerequisite_promoted"
CONTESTED   = "federation_prerequisite_contested"
REAFFIRMED  = "federation_prerequisite_reaffirmed"
DEPRECATED  = "federation_prerequisite_deprecated"
WEAKENED    = "federation_prerequisite_weakened"

_PREREQ_TYPES = {PROMOTED, CONTESTED, REAFFIRMED, DEPRECATED, WEAKENED}


# ── Status computation ────────────────────────────────────────────────────────

def get_prerequisite_events(
    condition: str | None = None,
    fed_events: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Return all prerequisite events, optionally filtered to a single condition."""
    if fed_events is None:
        fed_events = load_federation_events()
    evs = [ev for ev in fed_events if ev.get("event_type") in _PREREQ_TYPES]
    if condition is not None:
        evs = [ev for ev in evs if ev.get("condition") == condition]
    return evs


def get_prerequisite_status(
    condition: str,
    fed_events: list[dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    """
    Return the current status record for a condition.

    Status is computed from the event log — last event wins per phase:
      promoted → contested → reaffirmed / deprecated

    Returns None if the condition has never been promoted.
    """
    if fed_events is None:
        fed_events = load_federation_events()

    evs = get_prerequisite_events(condition, fed_events)
    if not evs:
        return None

    promoted_ev  = None
    contest_evs  = []
    reaffirm_evs = []
    deprecate_ev = None
    weaken_evs   = []

    for ev in evs:
        et = ev.get("event_type")
        if et == PROMOTED:
            promoted_ev = ev
        elif et == CONTESTED:
            contest_evs.append(ev)
        elif et == REAFFIRMED:
            reaffirm_evs.append(ev)
        elif et == DEPRECATED:
            deprecate_ev = ev   # last deprecation wins
        elif et == WEAKENED:
            weaken_evs.append(ev)

    if promoted_ev is None:
        return None

    # Determine current status
    # Priority: deprecated > weakened > reaffirmed > contested > promoted
    if deprecate_ev:
        current_status = "deprecated"
    elif weaken_evs:
        current_status = "weakened"
    elif reaffirm_evs:
        current_status = "reaffirmed"
    elif contest_evs:
        current_status = "contested"
    else:
        current_status = "promoted"

    # new_scope from the most recent weakened event
    new_scope = weaken_evs[-1].get("new_scope") if weaken_evs else None

    return {
        "condition": condition,
        "status": current_status,
        "authority": promoted_ev.get("authority", "none"),
        "evidence_claims": promoted_ev.get("evidence_claims", []),
        "evidence_claims_count": len(promoted_ev.get("evidence_claims", [])),
        "independent_convergence": promoted_ev.get("independent_convergence"),
        "evidence_score": promoted_ev.get("evidence_score", 0),
        "contest_count": len(contest_evs),
        "reaffirm_count": len(reaffirm_evs),
        "weaken_count": len(weaken_evs),
        "new_scope": new_scope,
        "deprecated": deprecate_ev is not None,
        "contestable": True,
        "promotion_basis": promoted_ev.get("promotion_basis", ""),
    }


def all_prerequisite_statuses(
    fed_events: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Return status for every distinct condition that has been promoted."""
    if fed_events is None:
        fed_events = load_federation_events()
    conditions = sorted({
        ev["condition"]
        for ev in fed_events
        if ev.get("event_type") == PROMOTED and ev.get("condition")
    })
    return [get_prerequisite_status(c, fed_events) for c in conditions]


# ── Event builders ────────────────────────────────────────────────────────────

def build_contest_event(
    condition: str,
    reason: str,
    speaker: str,
) -> dict[str, Any]:
    return {
        "event_type": CONTESTED,
        "condition": condition,
        "contest_reason": reason,
        "speaker": speaker,
        "note": "Contest this prerequisite by producing a plan tree that does not include the condition and achieves the claim's goals.",
    }


def build_reaffirm_event(
    condition: str,
    reason: str,
    speaker: str,
) -> dict[str, Any]:
    return {
        "event_type": REAFFIRMED,
        "condition": condition,
        "reaffirm_reason": reason,
        "speaker": speaker,
    }


def build_deprecate_event(
    condition: str,
    reason: str,
    speaker: str,
) -> dict[str, Any]:
    return {
        "event_type": DEPRECATED,
        "condition": condition,
        "deprecation_reason": reason,
        "speaker": speaker,
        "note": "A deprecated prerequisite can be re-promoted if new convergence evidence emerges.",
    }


def append_prerequisite_event(
    event: dict[str, Any],
    *,
    dry_run: bool = False,
    verbose: bool = False,
) -> dict[str, Any]:
    """Append a prerequisite event to federation.jsonl (or preview if dry_run)."""
    if dry_run:
        if verbose:
            print(f"[dry-run] {event['event_type']}: {event.get('condition')}")
        return event
    result = append_event("federation", event)
    if verbose:
        et = result["event_type"]
        cond = result["condition"]
        h = result["event_hash"][:12]
        print(f"✓ {et}: {cond}  {h}…")
    return result


# ── CLI ───────────────────────────────────────────────────────────────────────

def _main() -> None:
    parser = argparse.ArgumentParser(
        description="Contest, reaffirm, or deprecate a federation prerequisite."
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")

    # Mutually exclusive actions
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--contest",   metavar="COND", help="Contest a prerequisite")
    group.add_argument("--reaffirm",  metavar="COND", help="Reaffirm a prerequisite")
    group.add_argument("--deprecate", metavar="COND", help="Deprecate a prerequisite")

    parser.add_argument("--reason",  metavar="TEXT", help="Reason (required for actions)")
    parser.add_argument("--speaker", metavar="DID",  help="Speaker DID (required for actions)")

    args = parser.parse_args()

    action_cond = args.contest or args.reaffirm or args.deprecate

    if action_cond:
        # Action mode
        if not args.reason:
            parser.error("--reason is required for contest/reaffirm/deprecate")
        if not args.speaker:
            parser.error("--speaker is required for contest/reaffirm/deprecate")

        fed_events = load_federation_events()
        status = get_prerequisite_status(action_cond, fed_events)
        if status is None:
            print(f"✗ '{action_cond}' has not been promoted. No action taken.", file=sys.stderr)
            sys.exit(1)

        if args.contest:
            event = build_contest_event(action_cond, args.reason, args.speaker)
        elif args.reaffirm:
            event = build_reaffirm_event(action_cond, args.reason, args.speaker)
        else:
            event = build_deprecate_event(action_cond, args.reason, args.speaker)

        result = append_prerequisite_event(event, dry_run=args.dry_run, verbose=True)
        if args.json:
            print(json.dumps(result, indent=2))
        return

    # List mode — show all prerequisite statuses
    fed_events = load_federation_events()
    statuses = all_prerequisite_statuses(fed_events)

    if args.json:
        print(json.dumps(statuses, indent=2))
        return

    if not statuses:
        print("No promoted prerequisites found.")
        print("Run: python runtime/prerequisite_promotion.py --append")
        return

    print("Federation Prerequisite Status")
    print()
    for s in statuses:
        status_sym = {
            "promoted":   "✓",
            "reaffirmed": "✓✓",
            "contested":  "⚠",
            "deprecated": "✗",
        }.get(s["status"], "?")
        ind = "independent" if s.get("independent_convergence") else "shared authors"
        print(f"  {status_sym} {s['condition']}  [{s['status']}]")
        print(f"      authority:   {s['authority']}")
        print(f"      convergence: {s['evidence_claims_count']} claim(s)  [{ind}]")
        print(f"      evidence:    {', '.join(s['evidence_claims'])}")
        print(f"      score:       {s['evidence_score']}")
        print(f"      contests:    {s['contest_count']}  reaffirmed: {s['reaffirm_count']}")
        print(f"      contestable: True")
        print()


if __name__ == "__main__":
    _main()
