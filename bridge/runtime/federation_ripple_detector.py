#!/usr/bin/env python3
"""
federation_ripple_detector.py — dango-gitsea-bridge / federation branching

Detect negotiation ripple effects across a claim federation.

A ripple effect occurs when a change in one claim's state cascades
to affect other claims that depend on it. Ripples can be:

  blocking_chain    — claim X blocks Y blocks Z (cascading dependency failure)
  dignity_spread    — dignity violation in X propagates risk to Y, Z
  contest_ripple    — contest in X triggers re-evaluation in Y (shared conditions)
  instability       — X has many counterclaims AND blocks many others

Ripple detection is READ-ONLY. It does not modify state.
Results can be appended as federation_ripple_detected events via --append.

Severity levels:
  low    — advisory; note for future planning
  medium — worth addressing before downstream claims proceed
  high   — blocking or dignity risk; should be resolved first

CLI:
  python runtime/federation_ripple_detector.py
  python runtime/federation_ripple_detector.py --json
  python runtime/federation_ripple_detector.py --append
  python runtime/federation_ripple_detector.py --severity medium
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
from federation_branching import compute_all_branch_statuses


# ── Helpers ───────────────────────────────────────────────────────────────────

def _plan_events_by_claim() -> dict[str, list[dict[str, Any]]]:
    """Return plan events grouped by claim_id."""
    result: dict[str, list] = {}
    for ev in read_all("plans"):
        cid = ev.get("claim_id", "")
        if cid:
            result.setdefault(cid, []).append(ev)
    return result


def _has_dignity_violation(plan_events: list[dict[str, Any]]) -> bool:
    return any(
        e.get("event_type") == "plan_objected"
        and e.get("objection_type") == "dignity_violation"
        for e in plan_events
    )


def _contest_count(plan_events: list[dict[str, Any]]) -> int:
    return sum(1 for e in plan_events if e.get("event_type") == "plan_contested")


def _objection_count(plan_events: list[dict[str, Any]]) -> int:
    return sum(1 for e in plan_events if e.get("event_type") == "plan_objected")


def _counterclaim_count(cid: str, fmap: dict[str, Any]) -> int:
    return len(fmap.get(cid, {}).get("counterclaimed_by", []))


# ── Ripple detectors ──────────────────────────────────────────────────────────

def _detect_blocking_chains(
    fmap: dict[str, Any],
    branch_statuses: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Detect chains where one blocked claim cascades to block its dependents.

    A chain exists when: claim A blocks B, and B blocks C (transitively).
    """
    ripples: list[dict[str, Any]] = []

    # Find all claims that are blocked
    blocked_claims = {
        cid for cid, st in branch_statuses.items()
        if st["branch_status"] == "blocked"
    }

    for blocked_cid in sorted(blocked_claims):
        # Find claims that depend on this blocked claim
        info     = fmap.get(blocked_cid, {})
        affected = sorted(set(
            info.get("depended_on_by", []) + info.get("enables", [])
        ))

        if not affected:
            continue

        # Transitively find further affected claims
        all_affected: list[str] = []
        visited: set[str] = {blocked_cid}
        queue = list(affected)
        while queue:
            next_cid = queue.pop(0)
            if next_cid in visited:
                continue
            visited.add(next_cid)
            all_affected.append(next_cid)
            next_info = fmap.get(next_cid, {})
            queue.extend(next_info.get("depended_on_by", []) + next_info.get("enables", []))

        if all_affected:
            severity = "high" if len(all_affected) >= 3 else "medium"
            ripples.append({
                "ripple_type":      "blocking_chain",
                "source_claim":     blocked_cid,
                "affected_claims":  all_affected,
                "severity":         severity,
                "description":      (
                    f"{blocked_cid} is blocked, cascading to "
                    f"{len(all_affected)} downstream claim(s): {all_affected}"
                ),
            })

    return ripples


def _detect_dignity_spread(
    fmap: dict[str, Any],
    plan_events_by_claim: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """
    Detect dignity risk spreading from upstream to downstream claims.

    When a claim has dignity_violation objections, any dependent claim
    inherits dignity risk — it cannot safely proceed until the upstream
    dignity concern is resolved.
    """
    ripples: list[dict[str, Any]] = []

    for cid, plan_events in sorted(plan_events_by_claim.items()):
        if not _has_dignity_violation(plan_events):
            continue

        info     = fmap.get(cid, {})
        affected = sorted(set(
            info.get("depended_on_by", []) + info.get("enables", [])
        ))

        if not affected:
            continue

        ripples.append({
            "ripple_type":     "dignity_spread",
            "source_claim":    cid,
            "affected_claims": affected,
            "severity":        "high",
            "description":     (
                f"{cid} has dignity_violation objection; "
                f"dignity risk propagates to: {affected}"
            ),
        })

    return ripples


def _detect_contest_ripple(
    fmap: dict[str, Any],
    plan_events_by_claim: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """
    Detect when a contested upstream plan requires re-evaluation
    of conditions in downstream claims.

    A contest ripple occurs when the active plan for an upstream claim
    is contested (and might change), and downstream claims have already
    assumed those conditions are met.
    """
    ripples: list[dict[str, Any]] = []

    for cid, plan_events in sorted(plan_events_by_claim.items()):
        n_contests = _contest_count(plan_events)
        if n_contests == 0:
            continue

        info     = fmap.get(cid, {})
        affected = sorted(set(
            info.get("depended_on_by", []) + info.get("enables", [])
        ))

        if not affected:
            continue

        severity = "medium" if n_contests == 1 else "high"
        ripples.append({
            "ripple_type":     "contest_ripple",
            "source_claim":    cid,
            "affected_claims": affected,
            "severity":        severity,
            "description":     (
                f"{cid} has {n_contests} active contest(s); "
                f"dependent claim(s) {affected} may need condition re-evaluation "
                f"if the active plan changes"
            ),
            "contest_count":   n_contests,
        })

    return ripples


def _detect_instability(
    fmap: dict[str, Any],
    plan_events_by_claim: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """
    Detect federation instability: claims that are heavily contested,
    objected to, AND block many other claims.

    High instability = potential coordination bottleneck.
    """
    ripples: list[dict[str, Any]] = []

    for cid, plan_events in sorted(plan_events_by_claim.items()):
        n_contests   = _contest_count(plan_events)
        n_objections = _objection_count(plan_events)
        n_cc         = _counterclaim_count(cid, fmap)

        info       = fmap.get(cid, {})
        blocks     = len(info.get("depended_on_by", [])) + len(info.get("enables", []))

        # Instability score: (contests + objections + counterclaims) × blocks_count
        score = (n_contests + n_objections + n_cc) * max(blocks, 1)
        if score < 3:
            continue

        affected = sorted(set(
            info.get("depended_on_by", []) + info.get("enables", [])
        ))

        severity = "high" if score >= 6 else "medium"
        ripples.append({
            "ripple_type":     "instability",
            "source_claim":    cid,
            "affected_claims": affected,
            "severity":        severity,
            "instability_score": score,
            "description": (
                f"{cid} has {n_contests} contest(s), {n_objections} objection(s), "
                f"{n_cc} counterclaim(s), and blocks {blocks} downstream claim(s) "
                f"(instability score: {score})"
            ),
        })

    return ripples


# ── Core: detect all ripples ──────────────────────────────────────────────────

def detect_ripples(
    fmap: dict[str, Any],
    fed_events: list[dict[str, Any]],
    *,
    min_severity: str = "low",
) -> list[dict[str, Any]]:
    """
    Detect all ripple effects in the federation.

    Args:
        fmap:         Federation map from build_federation_map()
        fed_events:   All federation events
        min_severity: Filter; only return ripples at or above this level

    Returns:
        List of ripple dicts, sorted by severity (high first).
    """
    branch_statuses      = compute_all_branch_statuses(fmap, fed_events)
    plan_events_by_claim = _plan_events_by_claim()

    all_ripples: list[dict[str, Any]] = []
    all_ripples.extend(_detect_blocking_chains(fmap, branch_statuses))
    all_ripples.extend(_detect_dignity_spread(fmap, plan_events_by_claim))
    all_ripples.extend(_detect_contest_ripple(fmap, plan_events_by_claim))
    all_ripples.extend(_detect_instability(fmap, plan_events_by_claim))

    # Severity ordering
    _order = {"high": 0, "medium": 1, "low": 2}
    severity_filter = _order.get(min_severity, 2)

    filtered = [r for r in all_ripples if _order.get(r["severity"], 2) <= severity_filter]
    return sorted(filtered, key=lambda r: (_order.get(r["severity"], 2), r["source_claim"]))


# ── Build events ──────────────────────────────────────────────────────────────

def build_ripple_events(ripples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build federation_ripple_detected events (one per ripple)."""
    return [
        {
            "event_type":      "federation_ripple_detected",
            "ripple_type":     r["ripple_type"],
            "source_claim":    r["source_claim"],
            "affected_claims": r["affected_claims"],
            "severity":        r["severity"],
            "description":     r["description"],
        }
        for r in ripples
    ]


def append_ripple_events(
    events: list[dict[str, Any]],
    *,
    dry_run: bool = False,
    verbose: bool = False,
) -> list[dict[str, Any]]:
    if not events:
        if verbose:
            print("No ripple events to append.", file=sys.stderr)
        return []

    written = []
    for ev in events:
        if dry_run:
            print(f"[DRY RUN] {ev['event_type']:35s}  {ev['source_claim']:15s}  "
                  f"sev={ev['severity']}")
            written.append(ev)
        else:
            result = append_event("federation", ev)
            written.append(result)
            if verbose:
                print(f"✓ {result['event_type']:35s}  {result['source_claim']:15s}  "
                      f"sev={result['severity']}", file=sys.stderr)

    return written


# ── Display ───────────────────────────────────────────────────────────────────

def _print_ripples(ripples: list[dict[str, Any]]) -> None:
    if not ripples:
        print("No ripple effects detected.")
        return

    icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    print(f"Ripple Effects ({len(ripples)} detected):")
    for r in ripples:
        icon = icons.get(r["severity"], "·")
        print(f"\n  {icon} [{r['severity']:6s}] {r['ripple_type']}")
        print(f"    source:    {r['source_claim']}")
        print(f"    affects:   {r['affected_claims']}")
        print(f"    note:      {r.get('description','')}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="federation_ripple_detector",
        description="Detect negotiation ripple effects across the claim federation.",
    )
    p.add_argument("--severity",  default="low",
                   choices=["low", "medium", "high"],
                   help="Minimum severity to report (default: low)")
    p.add_argument("--append",   action="store_true",
                   help="Append federation_ripple_detected events to federation.jsonl")
    p.add_argument("--dry-run",  action="store_true")
    p.add_argument("--json",     action="store_true", dest="json_output")
    p.add_argument("--verbose", "-v", action="store_true")
    return p.parse_args()


def main() -> None:
    args = _parse_args()

    fed_events = load_federation_events()
    fmap       = build_federation_map(fed_events)

    ripples = detect_ripples(fmap, fed_events, min_severity=args.severity)

    if args.append or args.dry_run:
        events = build_ripple_events(ripples)
        written = append_ripple_events(
            events, dry_run=args.dry_run, verbose=args.verbose
        )
        if args.json_output:
            print(json.dumps({"ripples": ripples, "events": written},
                             indent=2, ensure_ascii=False))
        else:
            _print_ripples(ripples)
        return

    if args.json_output:
        print(json.dumps(ripples, indent=2, ensure_ascii=False))
    else:
        _print_ripples(ripples)


if __name__ == "__main__":
    main()
