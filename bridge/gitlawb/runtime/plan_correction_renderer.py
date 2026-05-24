"""
plan_correction_renderer.py — Reopen event → plan_correction_proposed

After a negotiation_reopened event, the plan author may propose a
plan correction. This module generates the plan_correction_proposed
event — an append-only record that a new plan version is proposed.

The correction:
  - does NOT delete the previous plan
  - is append-only (both plans remain visible)
  - requires a plan_author action (not auto-generated)
  - proposes a new plan version (plan-{claim_id}-v{N+1})
  - does not execute any action

Input:
    negotiation_reopened event JSON (issue-001.reopen-event.json)

Output:
    plan_correction_proposed event JSON:
    {
      event_type: "plan_correction_proposed",
      claim_id: "housing-007",
      corrects_plan: "plan-housing-007-v1",
      proposed_plan: "plan-housing-007-v2",
      reason: "counter_evidence_submitted",
      ...
    }

No real plan is modified. Append-only generation only. stdlib only.

A merged PR is evidence. Not authority.

Usage:
    python gitlawb/runtime/plan_correction_renderer.py \\
      gitlawb/examples/issue-001.reopen-event.json
    python gitlawb/runtime/plan_correction_renderer.py \\
      gitlawb/examples/issue-001.reopen-event.json --json \\
      > gitlawb/examples/issue-001.plan-correction.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_FILE_DIR = Path(__file__).parent

# ── Version bump helper ───────────────────────────────────────────────────────

def _next_plan_version(plan_id: str) -> str:
    """
    Given 'plan-housing-007-v1', return 'plan-housing-007-v2'.
    Fallback: append '-v2'.
    """
    if "-v" in plan_id:
        prefix, ver_part = plan_id.rsplit("-v", 1)
        try:
            return f"{prefix}-v{int(ver_part) + 1}"
        except ValueError:
            pass
    return f"{plan_id}-v2"


def _guess_current_plan(claim_id: str) -> str:
    return f"plan-{claim_id}-v1"


# ── Core ──────────────────────────────────────────────────────────────────────

def generate_plan_correction(
    reopen_event: dict[str, Any],
    current_plan_id: str | None = None,
    correction_note: str = "",
) -> dict[str, Any]:
    """
    Generate a plan_correction_proposed event from a negotiation_reopened event.

    The correction:
      - references the plan being superseded (corrects_plan)
      - proposes a new plan version (proposed_plan)
      - is append-only — the original plan remains visible
      - requires human/agent review before acceptance
    """
    claim_id  = reopen_event.get("claim_id", "unknown")
    condition = reopen_event.get("condition", "unknown")
    reason    = reopen_event.get("reason", "unspecified")
    pr_id     = reopen_event.get("pr_id", "unknown")
    issue_num = reopen_event.get("reopens_issue", None)

    if current_plan_id is None:
        current_plan_id = _guess_current_plan(claim_id)

    proposed_plan = _next_plan_version(current_plan_id)
    timestamp     = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Describe what the correction addresses
    correction_description = _correction_description(reason, condition, claim_id)

    return {
        "event_type":           "plan_correction_proposed",
        "timestamp":            timestamp,
        "claim_id":             claim_id,
        "condition":            condition,
        "corrects_plan":        current_plan_id,
        "proposed_plan":        proposed_plan,
        "reason":               reason,
        "reopens_issue":        issue_num,
        "triggered_by_pr":      pr_id,
        "correction_description": correction_description,
        "note":                 correction_note or correction_description,
        "authority":            "none",
        "execution_allowed":    False,
        "moves_money":          False,
        "advisory":             True,
        "contestable":          True,
        "hard_enforcement":     False,
        "append_only":          True,
        "original_plan_preserved": True,
        "note_append_only": (
            f"The original plan `{current_plan_id}` is NOT deleted. "
            "Both versions remain in the append-only event log. "
            "The plan tree can be regenerated from either version."
        ),
        "note_merge": (
            "A merged PR is evidence. Not authority. "
            f"This correction addresses the condition `{condition}` "
            "based on the negotiation_reopened event."
        ),
        "proposed_plan_changes": _proposed_changes(reason, condition, proposed_plan),
    }


def _correction_description(reason: str, condition: str, claim_id: str) -> str:
    descs = {
        "counter_evidence": (
            f"New evidence for `{condition}` requires re-evaluation of "
            f"the plan tree for `{claim_id}`. The updated plan incorporates "
            "the counter-evidence into the reasoning surface."
        ),
        "bypass_equivalence": (
            f"`{claim_id}` has demonstrated an equivalent bypass path for "
            f"`{condition}`. The updated plan records the bypass as an "
            "audit assertion rather than an active subgoal."
        ),
        "dignity_violation": (
            "A dignity guard violation was identified in the accepted evidence. "
            f"The updated plan for `{claim_id}` removes the violating evidence "
            "and proposes an anonymised alternative."
        ),
        "prerequisite_deprecation": (
            f"The prerequisite `{condition}` has been deprecated. "
            f"The updated plan for `{claim_id}` removes the active subgoal "
            "and records a deprecation assertion instead."
        ),
        "scope_contest": (
            f"The scope applicability of `{condition}` for `{claim_id}` "
            "is being contested. The updated plan proposes a narrowed scope "
            "or an alternative evidence path."
        ),
    }
    return descs.get(reason, f"Plan correction for `{condition}` on `{claim_id}` — reason: {reason}.")


def _proposed_changes(reason: str, condition: str, proposed_plan: str) -> list[str]:
    changes: dict[str, list[str]] = {
        "counter_evidence": [
            f"Re-evaluate `{condition}` evidence node",
            "Attach counter-evidence as a sibling assertion",
            "Branch: if counter-evidence invalidates original → abstain",
        ],
        "bypass_equivalence": [
            f"Move `{condition}` from subgoal to bypassed audit assertion",
            "Record bypass conditions in plan tree",
            "Remove gate branch that blocked plan advancement",
        ],
        "dignity_violation": [
            "Remove violating evidence reference",
            "Replace with anonymised or aggregate evidence node",
            "Add dignity_check assertion confirming fix",
        ],
        "prerequisite_deprecation": [
            f"Remove `{condition}` active subgoal",
            f"Add deprecation assertion for `{condition}`",
            "Record deprecation lifecycle event in plan metadata",
        ],
        "scope_contest": [
            f"Narrow scope annotation on `{condition}` subgoal",
            "Add contestation evidence as sibling assertion",
            "Branch: if scope not applicable → bypass assertion",
        ],
    }
    return changes.get(reason, [f"Update `{condition}` handling in `{proposed_plan}`"])


# ── CLI ───────────────────────────────────────────────────────────────────────

def _print_correction(c: dict[str, Any]) -> None:
    print(f"\n{'='*60}")
    print(f"  Plan Correction Proposed")
    print(f"{'='*60}")
    print(f"  claim_id:       {c['claim_id']}")
    print(f"  corrects_plan:  {c['corrects_plan']}")
    print(f"  proposed_plan:  {c['proposed_plan']}")
    print(f"  reason:         {c['reason']}")
    print(f"  append_only:    {c['append_only']}")
    print(f"  original_preserved: {c['original_plan_preserved']}")
    print(f"\n  Proposed changes:")
    for ch in c.get("proposed_plan_changes", []):
        print(f"    - {ch}")
    print()


def main() -> None:
    p = argparse.ArgumentParser(
        description="Generate a plan_correction_proposed event from a reopen event.",
    )
    p.add_argument("reopen_file", metavar="REOPEN_FILE")
    p.add_argument("--json",         action="store_true", dest="json_output")
    p.add_argument("--current-plan", default=None,
                   help="Current plan ID (default: inferred from claim_id)")
    p.add_argument("--note",         default="")
    args = p.parse_args()

    if not os.path.exists(args.reopen_file):
        print(f"ERROR: file not found: {args.reopen_file}", file=sys.stderr)
        sys.exit(1)

    with open(args.reopen_file) as f:
        data = json.load(f)

    ev = generate_plan_correction(data, current_plan_id=args.current_plan, correction_note=args.note)

    if args.json_output:
        print(json.dumps(ev, indent=2))
    else:
        print("\nPlan Correction Renderer")
        print(f"Input: {args.reopen_file}")
        print(f"(No plan modified — append-only proposal only)")
        _print_correction(ev)


if __name__ == "__main__":
    main()
