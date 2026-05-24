#!/usr/bin/env python3
"""
federation_condition_propagation.py — dango-gitsea-bridge / federation branching

Propagate conditions from active plans to dependent claims in the federation.

When an upstream claim reaches an active plan state, the conditions
satisfied by that plan become visible to downstream claims. This module
computes the propagation advisory and can record it as federation events.

Propagation is ADVISORY. It does not execute plans or trigger actions.
It records what conditions are now knowable by dependent claims.

Propagation types:
  condition_met      — upstream condition confirmed by active plan
  condition_blocked  — upstream condition blocked (dignity_violation)
  dignity_propagated — dignity constraints from upstream available downstream

Read-only computation: use --append to record propagation events.

CLI:
  python runtime/federation_condition_propagation.py --source-claim housing-001
  python runtime/federation_condition_propagation.py --source-claim housing-001 --json
  python runtime/federation_condition_propagation.py --source-claim housing-001 --append
  python runtime/federation_condition_propagation.py --source-claim housing-001 --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import read_all, append_event
from claim_federation import load_federation_events, build_federation_map

# ── Condition extraction ───────────────────────────────────────────────────────

def _extract_active_plan_conditions(claim_id: str) -> tuple[set[str], str]:
    """
    Return (conditions, active_plan_id) for the active plan of a claim.
    Returns (set(), "") if no active plan.
    """
    try:
        from reflective_memory import extract_conditions, extract_prior_knowledge
        pk = extract_prior_knowledge(claim_id)
        if not pk:
            return set(), ""
        active_plan_id = pk.get("active_plan_id", "")
        if not active_plan_id:
            return set(), ""

        # Combine learned conditions + structural extraction from plan tree
        learned = set(pk.get("learned_conditions", []))

        plan_events = [
            e for e in read_all("plans")
            if e.get("claim_id") == claim_id
            and e.get("plan_id") == active_plan_id
            and e.get("event_type") in ("plan_tree_created", "plan_tree_amended", "plan_tree_corrected")
        ]
        plan_conditions: set[str] = set()
        for ev in plan_events:
            tree = ev.get("plan_tree", {})
            plan_conditions.update(extract_conditions(tree))

        return (learned | plan_conditions), active_plan_id

    except ImportError:
        return set(), ""


def _has_dignity_violation(claim_id: str) -> bool:
    """Return True if any plan for this claim has a dignity_violation objection."""
    events = [e for e in read_all("plans") if e.get("claim_id") == claim_id]
    return any(
        e.get("event_type") == "plan_objected"
        and e.get("objection_type") == "dignity_violation"
        for e in events
    )


# ── Core propagation computation ──────────────────────────────────────────────

def compute_propagation(
    source_claim_id: str,
    fmap: dict[str, Any],
    fed_events: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Compute what conditions the source claim propagates to dependent claims.

    Returns:
      {
        "source_claim_id": str,
        "active_plan_id":  str,
        "conditions":      [str, ...],   ← all conditions met by active plan
        "dignity_blocked": bool,
        "propagation_targets": [
          {
            "target_claim_id": str,
            "relationship":    str,
            "propagated_conditions": [str, ...],
            "propagation_type": "condition_met" | "condition_blocked" | "dignity_propagated",
          }, ...
        ],
        "already_propagated": [str, ...],  ← conditions already in fed events
      }
    """
    # Find claims that depend on the source
    source_info = fmap.get(source_claim_id, {})
    downstream: list[tuple[str, str]] = []  # (claim_id, relationship)

    for dep_cid in source_info.get("depended_on_by", []):
        downstream.append((dep_cid, "depends_on"))
    for dep_cid in source_info.get("enables", []):
        downstream.append((dep_cid, "enables"))

    # Determine what this source claim can propagate
    dignity_blocked = _has_dignity_violation(source_claim_id)
    conditions, active_plan_id = _extract_active_plan_conditions(source_claim_id)

    # Which conditions are already recorded as propagated?
    already_propagated: set[str] = set()
    for ev in fed_events:
        if (ev.get("event_type") == "federation_condition_met"
                and ev.get("depends_on_claim_id") == source_claim_id):
            cond = ev.get("condition", "")
            if cond:
                already_propagated.add(cond)

    targets: list[dict[str, Any]] = []
    for (target_cid, rel) in downstream:
        if dignity_blocked:
            targets.append({
                "target_claim_id":        target_cid,
                "relationship":           rel,
                "propagated_conditions":  [],
                "propagation_type":       "condition_blocked",
                "reason":                 "dignity_violation on source claim plan",
            })
        elif conditions:
            targets.append({
                "target_claim_id":        target_cid,
                "relationship":           rel,
                "propagated_conditions":  sorted(conditions),
                "propagation_type":       "condition_met",
                "reason":                 f"active plan {active_plan_id!r}",
            })
        else:
            targets.append({
                "target_claim_id":        target_cid,
                "relationship":           rel,
                "propagated_conditions":  [],
                "propagation_type":       "dignity_propagated",
                "reason":                 "no active plan yet; dignity constraints visible",
            })

    return {
        "source_claim_id":      source_claim_id,
        "active_plan_id":       active_plan_id,
        "conditions":           sorted(conditions),
        "dignity_blocked":      dignity_blocked,
        "propagation_targets":  targets,
        "already_propagated":   sorted(already_propagated),
    }


# ── Build events from propagation result ─────────────────────────────────────

def build_propagation_events(prop: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Build a list of federation events representing the computed propagation.
    Does not write — caller decides whether to append.
    """
    events: list[dict[str, Any]] = []
    source = prop["source_claim_id"]
    active_plan = prop.get("active_plan_id", "")

    for target in prop["propagation_targets"]:
        ptype  = target["propagation_type"]
        target_cid = target["target_claim_id"]

        if ptype == "condition_blocked":
            events.append({
                "event_type":             "federation_condition_blocked",
                "claim_id":               target_cid,
                "depends_on_claim_id":    source,
                "reason":                 target["reason"],
            })

        elif ptype == "condition_met":
            already = set(prop.get("already_propagated", []))
            for cond in target["propagated_conditions"]:
                if cond not in already:
                    events.append({
                        "event_type":             "federation_condition_met",
                        "claim_id":               target_cid,
                        "depends_on_claim_id":    source,
                        "condition":              cond,
                        "source_plan_id":         active_plan,
                    })

    return events


# ── Append ────────────────────────────────────────────────────────────────────

def append_propagation_events(
    events: list[dict[str, Any]],
    *,
    dry_run: bool = False,
    verbose: bool = False,
) -> list[dict[str, Any]]:
    """Append propagation events to sutable/federation.jsonl."""
    if not events:
        if verbose:
            print("No new propagation events to append.", file=sys.stderr)
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
                et  = result.get("event_type", "")
                cid = result.get("claim_id", "")
                cond = result.get("condition", "")
                print(f"✓ appended {et}  {cid}  {cond}", file=sys.stderr)

    return written


# ── Display ───────────────────────────────────────────────────────────────────

def _print_propagation(prop: dict[str, Any]) -> None:
    src = prop["source_claim_id"]
    print(f"\nCondition Propagation — {src}")
    print(f"  active_plan_id:    {prop.get('active_plan_id') or '(none)'}")
    print(f"  dignity_blocked:   {prop['dignity_blocked']}")
    conds = prop.get("conditions", [])
    print(f"  conditions ({len(conds)}):  {conds or '(none)'}")

    already = prop.get("already_propagated", [])
    if already:
        print(f"  already propagated ({len(already)}): {already}")

    targets = prop.get("propagation_targets", [])
    if targets:
        print(f"\n  Propagation targets ({len(targets)}):")
        for t in targets:
            icon = {"condition_met": "✓", "condition_blocked": "✗",
                    "dignity_propagated": "~"}.get(t["propagation_type"], "?")
            print(f"    {icon} {t['target_claim_id']:20s}  [{t['propagation_type']}]")
            if t["propagated_conditions"]:
                for c in t["propagated_conditions"]:
                    print(f"      • {c}")
    else:
        print("\n  No downstream targets.")


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="federation_condition_propagation",
        description=(
            "Compute and optionally record condition propagation "
            "from a source claim to its federation dependents."
        ),
    )
    p.add_argument("--source-claim", required=True, metavar="CLAIM_ID")
    p.add_argument("--append",   action="store_true",
                   help="Append computed propagation events to federation.jsonl")
    p.add_argument("--dry-run",  action="store_true",
                   help="Compute and print events without writing")
    p.add_argument("--json",     action="store_true", dest="json_output")
    p.add_argument("--verbose", "-v", action="store_true")
    return p.parse_args()


def main() -> None:
    args = _parse_args()

    fed_events = load_federation_events()
    fmap       = build_federation_map(fed_events)

    prop = compute_propagation(args.source_claim, fmap, fed_events)

    if args.json_output and not args.append and not args.dry_run:
        print(json.dumps(prop, indent=2, ensure_ascii=False))
        return

    if args.append or args.dry_run:
        events = build_propagation_events(prop)
        written = append_propagation_events(
            events,
            dry_run=args.dry_run,
            verbose=args.verbose or not args.json_output,
        )
        if args.json_output:
            print(json.dumps({"propagation": prop, "events_written": written},
                             indent=2, ensure_ascii=False))
    else:
        if args.json_output:
            print(json.dumps(prop, indent=2, ensure_ascii=False))
        else:
            _print_propagation(prop)


if __name__ == "__main__":
    main()
