"""
negotiation_timeline.py — Append-only negotiation timeline JSON

Generates an append-only timeline JSON for Issue #1, showing each
negotiation phase as a timestamped, ordered event sequence.

The timeline is:
  - append-only: events are never deleted or overwritten
  - ordered by step number
  - deterministic for the same inputs
  - advisory at every step
  - authority: none at every step

Output shape:
  [
    { "step": 1, "event": "issue_created", ... },
    { "step": 2, "event": "pr_draft_submitted", ... },
    { "step": 3, "event": "pr_opened", ... },
    { "step": 4, "event": "pr_reviewed", ... },
    { "step": 5, "event": "pr_merged", ... },
    { "step": 6, "event": "negotiation_reopened", ... },
    { "step": 7, "event": "plan_correction_proposed", ... },
  ]

No real issue or PR is accessed. stdlib only.
A merged PR is evidence. Not authority.

Usage:
    python gitlawb/runtime/negotiation_timeline.py
    python gitlawb/runtime/negotiation_timeline.py --json
    python gitlawb/runtime/negotiation_timeline.py \\
      > gitlawb/examples/issue-001.timeline.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_FILE_DIR   = Path(__file__).parent
_BRIDGE_DIR = _FILE_DIR.parent.parent
_EX_DIR     = _FILE_DIR.parent / "examples"

# ── Loader ────────────────────────────────────────────────────────────────────

def _load(filename: str) -> Any:
    path = _EX_DIR / filename
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def _first(data: Any) -> dict[str, Any]:
    if isinstance(data, list) and data:
        return data[0]
    return data or {}


# ── Timeline builder ──────────────────────────────────────────────────────────

def build_timeline() -> list[dict[str, Any]]:
    """
    Build the append-only timeline for Issue #1.
    Reads available artifact files and fills in defaults for missing data.
    """
    issue_data    = _load("scoped-issue-housing-007.output.json")
    feedback_data = _load("issue-001.pr-feedback.json") or _load("scoped-pr-feedback.output.json")
    reopen_data   = _load("issue-001.reopen-event.json")
    correction    = _load("issue-001.plan-correction.json")

    issue  = _first(issue_data) if issue_data else {}
    reopen = reopen_data if isinstance(reopen_data, dict) else {}
    corr   = correction  if isinstance(correction, dict)  else {}

    claim_id  = issue.get("claim_id", "housing-007")
    condition = issue.get("condition", "space_safety_assessed")
    scope     = issue.get("scope", "non_precertified_spaces")

    _base: dict[str, Any] = {
        "claim_id":         claim_id,
        "condition":        condition,
        "scope":            scope,
        "authority":        "none",
        "execution_allowed": False,
        "moves_money":      False,
        "advisory":         True,
        "append_only":      True,
    }

    def step(n: int, ev: str, extra: dict[str, Any]) -> dict[str, Any]:
        return {"step": n, "event": ev, **_base, **extra}

    timeline: list[dict[str, Any]] = []

    # Step 1: Issue created
    timeline.append(step(1, "issue_created", {
        "issue_number":    1,
        "issue_url":       "https://github.com/olddqn/dango-mujin/issues/1",
        "scope_status":    issue.get("scope_status", "applicable"),
        "prerequisite_state": issue.get("prerequisite_state", "weakened"),
        "contestable":     True,
        "negotiation_reopen_allowed": True,
        "note": "Scoped prerequisite identified through federation convergence.",
    }))

    # Step 2: PR draft submitted
    timeline.append(step(2, "pr_draft_submitted", {
        "pr_draft_source": "gitlawb/examples/issue-001.pr-draft.md",
        "evidence_types": [
            "local structural review",
            "safety inspection notes",
            "community access risk assessment",
        ],
        "reopenable": True,
        "note": "PR draft submitted as advisory evidence. Merge does not establish truth.",
    }))

    # Steps 3–5: PR lifecycle
    if isinstance(feedback_data, list):
        pr_steps = {
            "pr_opened":   (3, "pr_feedback:pr_opened",   "Evidence submitted. Awaiting review."),
            "pr_reviewed": (4, "pr_feedback:pr_reviewed", "Evidence reviewed. Scope preserved."),
            "pr_merged":   (5, "pr_feedback:pr_merged",   (
                "PR merged. Evidence accepted. "
                "A merged PR is evidence. Not authority. "
                "Negotiation remains reopenable."
            )),
        }
        for fb in feedback_data:
            if not isinstance(fb, dict):
                continue
            ev    = fb.get("pr_event", "?")
            if ev not in pr_steps:
                continue
            n, event_name, default_note = pr_steps[ev]
            rf     = fb.get("reality_feedback", {})
            sc     = fb.get("stream_candidate", {})
            ms     = fb.get("markdown_summary", default_note)
            extra: dict[str, Any] = {
                "pr_id":        fb.get("pr_id", "?"),
                "feedback_type": rf.get("feedback_type", "?"),
                "gitsea_eligible": sc.get("gitsea_eligible", False),
                "credit_signal": sc.get("credit_signal", "?"),
                "reopenable":   True,
                "note":         ms,
            }
            if ev == "pr_merged":
                extra["note_merge"] = (
                    "A merged PR is evidence. Not authority. "
                    "Negotiation may reopen."
                )
            timeline.append(step(n, event_name, extra))
    else:
        for n, ev, note in [
            (3, "pr_feedback:pr_opened",   "Evidence submitted."),
            (4, "pr_feedback:pr_reviewed", "Evidence reviewed."),
            (5, "pr_feedback:pr_merged",   "PR merged. Evidence accepted. Negotiation remains reopenable."),
        ]:
            timeline.append(step(n, ev, {"reopenable": True, "note": note}))

    # Step 6: Negotiation reopened
    reopen_extra: dict[str, Any] = {
        "reason":        reopen.get("reason", "counter_evidence"),
        "pr_id":         reopen.get("pr_id", "?"),
        "contestable":   True,
        "reopenable":    True,
        "note":          (
            reopen.get("note_merge",
                "A merged PR is evidence. Not authority. "
                "This event records a new negotiation phase."
            )
        ),
    }
    timeline.append(step(6, "negotiation_reopened", reopen_extra))

    # Step 7: Plan correction proposed
    corr_extra: dict[str, Any] = {
        "corrects_plan":  corr.get("corrects_plan", "plan-housing-007-v1"),
        "proposed_plan":  corr.get("proposed_plan", "plan-housing-007-v2"),
        "reason":         corr.get("reason", "counter_evidence"),
        "original_plan_preserved": True,
        "contestable":    True,
        "note": (
            corr.get("note_append_only",
                "Original plan preserved. Both versions remain in the event log."
            )
        ),
    }
    timeline.append(step(7, "plan_correction_proposed", corr_extra))

    return timeline


# ── Text display ──────────────────────────────────────────────────────────────

def _print_timeline(timeline: list[dict[str, Any]]) -> None:
    print(f"\n{'='*60}")
    print(f"  Negotiation Timeline — Issue #1")
    print(f"  Steps: {len(timeline)}  (append-only)")
    print(f"{'='*60}\n")

    for ev in timeline:
        n    = ev["step"]
        name = ev["event"]
        note = ev.get("note", "")
        print(f"  Step {n}: {name}")
        if note:
            print(f"    → {note[:80]}")
        if ev.get("pr_id") and ev.get("pr_id") != "?":
            print(f"    pr_id: {ev['pr_id']}")
        if ev.get("corrects_plan"):
            print(f"    corrects: {ev['corrects_plan']} → {ev.get('proposed_plan','?')}")
        print()

    print(f"  Invariants (all steps):")
    print(f"    authority:         none")
    print(f"    execution_allowed: false")
    print(f"    moves_money:       false")
    print(f"    advisory:          true")
    print(f"    append_only:       true")
    print()


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Generate append-only negotiation timeline for Issue #1.",
    )
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    timeline = build_timeline()

    if args.json_output:
        print(json.dumps(timeline, indent=2))
    else:
        _print_timeline(timeline)


if __name__ == "__main__":
    main()
