#!/usr/bin/env python3
"""
prerequisite_evidence_bundle.py — dango-gitsea-bridge / prerequisite promotion

Build an evidence bundle for a federation prerequisite candidate.

An evidence bundle makes the case for (or against) a condition becoming
a federation prerequisite. It collects:

  - Which claims learned the condition, and how
  - Which objection triggered the counterplan that introduced the condition
  - Who proposed the plans (authorship lineage)
  - Whether convergence was independent

The evidence bundle is a transparent audit trail.
Anyone can inspect it and verify or contest the conclusion.

This module reads. It does not write.

CLI:
  python runtime/prerequisite_evidence_bundle.py --condition space_safety_assessed
  python runtime/prerequisite_evidence_bundle.py --condition space_safety_assessed --json
  python runtime/prerequisite_evidence_bundle.py --all
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from sutable_log import read_all
from claim_federation import load_federation_events, build_federation_map
from federation_prerequisite_detector import detect_prerequisite_candidates

# ── Plan helpers ──────────────────────────────────────────────────────────────

def _plan_events_for_claim(claim_id: str, plan_events: list[dict]) -> list[dict]:
    return [e for e in plan_events if e.get("claim_id") == claim_id]


def _find_contest_for_condition(
    condition: str,
    claim_id: str,
    plan_events: list[dict],
) -> dict[str, Any] | None:
    """
    Find the plan_contested event whose counterplan introduced `condition`.

    Strategy:
      For each plan_contested event in the claim:
        - Look up the counterplan's plan_tree
        - Walk it for branch conditions
        - Look up the contested plan's tree
        - If condition is in counterplan tree but NOT in contested plan tree → this contest
    """
    from reflective_memory import extract_conditions, _get_plan_tree

    claim_events = _plan_events_for_claim(claim_id, plan_events)
    for ev in claim_events:
        if ev.get("event_type") != "plan_contested":
            continue
        contested_id   = ev.get("contested_plan_id", "")
        counterplan_id = ev.get("counterplan_id", "")
        if not contested_id or not counterplan_id:
            continue

        contested_tree   = _get_plan_tree(claim_events, contested_id)
        counterplan_tree = _get_plan_tree(claim_events, counterplan_id)

        contested_conds   = extract_conditions(contested_tree)
        counterplan_conds = extract_conditions(counterplan_tree)

        if condition in (counterplan_conds - contested_conds):
            return ev
    return None


def _find_triggering_objection(
    contested_plan_id: str,
    claim_id: str,
    plan_events: list[dict],
) -> dict[str, Any] | None:
    """
    Find the plan_objected event that preceded the contest of contested_plan_id.
    We take the last objection on that plan (most proximate trigger).
    """
    claim_events = _plan_events_for_claim(claim_id, plan_events)
    objections = [
        ev for ev in claim_events
        if ev.get("event_type") == "plan_objected"
        and ev.get("plan_id") == contested_plan_id
    ]
    return objections[-1] if objections else None


def _plan_author(plan_id: str, claim_id: str, plan_events: list[dict]) -> str | None:
    """Return speaker of the plan_tree_created/corrected event for plan_id."""
    tree_types = {"plan_tree_created", "plan_tree_corrected", "plan_tree_amended"}
    for ev in plan_events:
        if (
            ev.get("claim_id") == claim_id
            and ev.get("plan_id") == plan_id
            and ev.get("event_type") in tree_types
        ):
            return ev.get("speaker")
    return None


# ── Core bundle builder ───────────────────────────────────────────────────────

def build_evidence_bundle(
    condition: str,
    fmap: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build a full evidence bundle for a prerequisite condition.

    Returns:
        {
          "condition": str,
          "prerequisite_threshold": int,
          "evidence_bundle": {
            "claims": [
              {
                "claim_id": str,
                "objection_type": str | None,
                "objector": str | None,
                "contested_plan_id": str | None,
                "counterplan_id": str | None,
                "counterplan_author": str | None,
                "contested_plan_author": str | None,
                "learned_via": "plan_contest" | "memory_snapshot_only"
              },
              ...
            ],
            "independent_convergence": bool,
            "shared_authorship": bool,
            "shared_objector": bool,
            "dignity_safe": bool,
            "evidence_score": int,
          }
        }
    Returns {"error": "..."} if condition is below threshold.
    """
    if fmap is None:
        fmap = build_federation_map(load_federation_events())

    # Find the candidate
    candidates = detect_prerequisite_candidates(fmap=fmap)
    candidate = next((c for c in candidates if c["condition"] == condition), None)
    if candidate is None:
        return {"error": f"'{condition}' is not a prerequisite candidate (below threshold or no memory snapshots)"}

    plan_events = read_all("plans")
    memory_events = read_all("memory")

    # Latest memory snapshot per claim
    latest_mem: dict[str, dict] = {}
    for ev in memory_events:
        if ev.get("event_type") == "memory_snapshot_created":
            cid = ev.get("claim_id", "")
            if cid:
                latest_mem[cid] = ev

    claim_entries: list[dict[str, Any]] = []

    for cid in candidate["triggered_by"]:
        # Find the contest that introduced this condition
        contest_ev = _find_contest_for_condition(condition, cid, plan_events)

        if contest_ev:
            contested_id   = contest_ev.get("contested_plan_id")
            counterplan_id = contest_ev.get("counterplan_id")
            contested_author   = _plan_author(contested_id, cid, plan_events)
            counterplan_author = _plan_author(counterplan_id, cid, plan_events)
            obj_ev = _find_triggering_objection(contested_id, cid, plan_events)
            learned_via = "plan_contest"
        else:
            # Condition in memory snapshot but no traceable contest in plans.jsonl
            contested_id = counterplan_id = None
            contested_author = counterplan_author = None
            obj_ev = None
            learned_via = "memory_snapshot_only"

        claim_entries.append({
            "claim_id": cid,
            "objection_type": obj_ev.get("objection_type") if obj_ev else None,
            "objector": obj_ev.get("speaker") if obj_ev else None,
            "contested_plan_id": contested_id,
            "counterplan_id": counterplan_id,
            "contested_plan_author": contested_author,
            "counterplan_author": counterplan_author,
            "learned_via": learned_via,
        })

    # ── Independence metrics ──────────────────────────────────────────────────
    # shared_authorship: does the same person appear as a plan author in ≥2 different claims?
    # (not: same person for both plans within one claim)
    claim_author_sets: list[set[str]] = [
        {a for a in [e["contested_plan_author"], e["counterplan_author"]] if a}
        for e in claim_entries
    ]
    cross_author_counts: dict[str, int] = {}
    for author_set in claim_author_sets:
        for a in author_set:
            cross_author_counts[a] = cross_author_counts.get(a, 0) + 1
    shared_authorship = any(v >= 2 for v in cross_author_counts.values())

    objector_counts: dict[str, int] = {}
    for entry in claim_entries:
        if entry["objector"]:
            objector_counts[entry["objector"]] = objector_counts.get(entry["objector"], 0) + 1
    shared_objector = any(v >= 2 for v in objector_counts.values())

    independent_convergence = not shared_authorship

    # ── Dignity safety ────────────────────────────────────────────────────────
    dignity_violation_claims = {
        ev.get("claim_id")
        for ev in plan_events
        if ev.get("event_type") == "plan_objected"
        and ev.get("objection_type") == "dignity_violation"
    }
    dignity_safe = not bool(dignity_violation_claims & set(candidate["triggered_by"]))

    return {
        "condition": condition,
        "prerequisite_threshold": len(candidate["triggered_by"]),
        "evidence_bundle": {
            "claims": claim_entries,
            "independent_convergence": independent_convergence,
            "shared_authorship": shared_authorship,
            "shared_objector": shared_objector,
            "dignity_safe": dignity_safe,
            "evidence_score": candidate["evidence_score"],
        },
    }


def build_all_evidence_bundles(
    fmap: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Build evidence bundles for all prerequisite candidates."""
    if fmap is None:
        fmap = build_federation_map(load_federation_events())
    candidates = detect_prerequisite_candidates(fmap=fmap)
    return [build_evidence_bundle(c["condition"], fmap=fmap) for c in candidates]


# ── CLI ───────────────────────────────────────────────────────────────────────

def _main() -> None:
    parser = argparse.ArgumentParser(
        description="Build evidence bundle for a federation prerequisite condition."
    )
    parser.add_argument("--condition", metavar="COND", help="Specific condition")
    parser.add_argument("--all", action="store_true", help="All candidates")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if args.all:
        bundles = build_all_evidence_bundles()
        if args.json:
            print(json.dumps(bundles, indent=2))
        else:
            for b in bundles:
                _print_bundle(b)
        return

    if not args.condition:
        parser.error("--condition COND or --all is required")

    bundle = build_evidence_bundle(args.condition)
    if "error" in bundle:
        print(f"✗ {bundle['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(bundle, indent=2))
    else:
        _print_bundle(bundle)


def _print_bundle(b: dict[str, Any]) -> None:
    if "error" in b:
        print(f"✗ {b['error']}")
        return

    eb = b["evidence_bundle"]
    ind = "✓ independent" if eb["independent_convergence"] else "~ shared authors"
    saf = "dignity-safe" if eb["dignity_safe"] else "⚠ DIGNITY RISK"
    print(f"Evidence Bundle: {b['condition']}")
    print(f"  convergence: {b['prerequisite_threshold']} claim(s)  {ind}  [{saf}]")
    print(f"  evidence score: {eb['evidence_score']}")
    print(f"  shared_authorship: {eb['shared_authorship']}")
    print(f"  shared_objector:   {eb['shared_objector']}")
    print(f"  claims:")
    for cl in eb["claims"]:
        ot = cl.get("objection_type") or "(none)"
        lv = cl.get("learned_via", "?")
        print(f"    {cl['claim_id']}")
        print(f"      learned via: {lv}")
        print(f"      objection:   {ot}  (objector: {cl.get('objector') or '—'})")
        print(f"      contested:   {cl.get('contested_plan_id') or '—'}")
        print(f"      counterplan: {cl.get('counterplan_id') or '—'}")
    print()


if __name__ == "__main__":
    _main()
