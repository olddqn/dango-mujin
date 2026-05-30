"""
contribution_evaluator.py — Advisory Cooperation Metrics

Generates advisory cooperation metrics from a Dan-Go negotiation event log.

Cooperation is measured because:
  - It reveals who participated and how
  - It makes contribution patterns legible
  - It is evidence, not a verdict

Cooperation is NOT:
  - A reputation score
  - A reward signal
  - A ranking mechanism
  - Enforced by any authority
  - Permanent or irrevocable

All output is advisory. No participant is penalized. No participant is
automatically rewarded. Cooperation signals are contestable.

Core principle:
  "Contribution becomes legible before it becomes valuable."

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/lifecycle/runtime/contribution_evaluator.py
    python bridge/gitsea/lifecycle/runtime/contribution_evaluator.py --save
    python bridge/gitsea/lifecycle/runtime/contribution_evaluator.py --json
    python bridge/gitsea/lifecycle/runtime/contribution_evaluator.py \\
        --input PATH_TO_EVENTS_JSON
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_FILE_DIR  = Path(__file__).parent
_LIFECYCLE = _FILE_DIR.parent
_EXAMPLES  = _LIFECYCLE / "examples"
_REPO_ROOT = _LIFECYCLE.parent.parent.parent


# ── Event weight table ────────────────────────────────────────────────────────
# Each event type contributes a weight toward the cooperation signal.
# Weights are advisory: they represent participation diversity, not quality.

EVENT_WEIGHTS: dict[str, float] = {
    "evidence":             0.30,   # Evidence contribution
    "contest":              0.20,   # Contesting a claim or plan — healthy dissent
    "reaffirm":             0.20,   # Reaffirming a prior position with new context
    "pr_submitted":         0.15,   # PR submitted as evidence
    "pr_merged":            0.10,   # PR merged (evidence accepted)
    "plan_correction":      0.05,   # Plan correction proposed
}

# Maximum raw score before normalization (sum of all weights)
_MAX_RAW = sum(EVENT_WEIGHTS.values())


# ── Evaluator ─────────────────────────────────────────────────────────────────

def evaluate_cooperation(
    participants: list[str],
    events: dict[str, int],
    claim_id: str = "housing-007",
    issue_id: int | None = 1,
) -> dict[str, Any]:
    """
    Generate an advisory cooperation evaluation.

    Parameters
    ----------
    participants : list[str]
        Pseudonymous participant identifiers.
    events : dict[str, int]
        Count of each event type observed.
    claim_id : str
        The Dan-Go claim identifier.
    issue_id : int | None
        Associated issue number.

    Returns
    -------
    dict
        Advisory cooperation evaluation. Never enforced. Never final.
    """
    # Compute raw weighted participation score
    raw_score: float = 0.0
    for event_type, count in events.items():
        weight = EVENT_WEIGHTS.get(event_type, 0.0)
        # Count contribution, but cap at 3 per type (diminishing returns)
        effective = min(count, 3)
        raw_score += weight * effective

    # Participation diversity bonus: more participants → higher signal
    # Cap at 5 participants for the diversity multiplier
    diversity_multiplier = min(len(participants), 5) / 5.0
    # Blend: 70% event coverage, 30% diversity
    blended = (0.70 * min(raw_score / _MAX_RAW, 1.0)) + (0.30 * diversity_multiplier)
    # Round to 2 decimal places
    cooperation_signal = round(blended, 2)

    # Contest and reaffirm count — healthy negotiation indicators
    n_contest  = events.get("contest",  0)
    n_reaffirm = events.get("reaffirm", 0)
    n_evidence = events.get("evidence", 0)

    return {
        "evaluation_type":   "cooperation_evaluation",
        "generated_at":      datetime.now(timezone.utc).isoformat(),
        "claim_id":          claim_id,
        "issue_id":          issue_id,

        # Participants — pseudonymous, no personal data
        "participants":      participants,
        "participant_count": len(participants),

        # Events observed
        "events":            events,
        "total_events":      sum(events.values()),

        # Cooperation signal (advisory only — not a score, not enforced)
        "cooperation_signal": cooperation_signal,
        "signal_components": {
            "event_coverage":       round(min(raw_score / _MAX_RAW, 1.0), 3),
            "diversity_multiplier": round(diversity_multiplier, 3),
        },

        # Healthy negotiation indicators
        "healthy_negotiation": {
            "evidence_count":  n_evidence,
            "contest_count":   n_contest,
            "reaffirm_count":  n_reaffirm,
            "dissent_present": n_contest > 0,
            "note": (
                "Contest events are a sign of healthy negotiation, not failure. "
                "Dissent is part of the protocol."
            ),
        },

        # Invariants
        "authority":         "none",
        "execution_allowed": False,
        "moves_money":       False,
        "hard_enforcement":  False,
        "advisory":          True,
        "append_only":       True,
        "contestable":       True,
        "reopenable":        True,
        "economic_value":    False,

        "cooperation_note": (
            "This cooperation signal is advisory. "
            "It is not a reputation score. It is not a reward. "
            "It is not enforced by any authority. "
            "Participants are not penalized for low signals. "
            "Contribution becomes legible before it becomes valuable."
        ),
    }


# ── Save ──────────────────────────────────────────────────────────────────────

def save_evaluation(eval_doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "contribution-signal.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(eval_doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Generate advisory cooperation metrics for a Dan-Go claim.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Cooperation is NOT reputation. Cooperation is NOT reward.
Cooperation is NOT enforced. Cooperation is advisory participation legibility.

Event types (with advisory weights):
  evidence        0.30  — evidence contribution
  contest         0.20  — contesting a claim or plan
  reaffirm        0.20  — reaffirming with new context
  pr_submitted    0.15  — PR submitted as evidence
  pr_merged       0.10  — PR merged (evidence accepted)
  plan_correction 0.05  — plan correction proposed

Examples:
  python bridge/gitsea/lifecycle/runtime/contribution_evaluator.py
  python bridge/gitsea/lifecycle/runtime/contribution_evaluator.py --save
  python bridge/gitsea/lifecycle/runtime/contribution_evaluator.py --json
        """,
    )
    p.add_argument("--claim", metavar="CLAIM_ID", default="housing-007")
    p.add_argument("--issue", metavar="ISSUE_NUM", type=int, default=1)
    p.add_argument("--participants", nargs="*",
                   default=["alice", "bob", "carol"])
    p.add_argument("--events", metavar="JSON",
                   default='{"evidence": 2, "contest": 1, "reaffirm": 1, "pr_submitted": 1, "pr_merged": 1}',
                   help="JSON dict of event_type → count")
    p.add_argument("--input", metavar="PATH",
                   help="Load events from JSON file (overrides --events)")
    p.add_argument("--save", action="store_true",
                   help="Save to lifecycle/examples/contribution-signal.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    # Resolve events
    if args.input:
        with open(args.input, encoding="utf-8") as f:
            events_raw = json.load(f)
            if isinstance(events_raw, dict) and "events" in events_raw:
                events = events_raw["events"]
            else:
                events = events_raw
    else:
        try:
            events = json.loads(args.events)
        except json.JSONDecodeError as e:
            print(f"ERROR: --events is not valid JSON: {e}", file=sys.stderr)
            sys.exit(1)

    eval_doc = evaluate_cooperation(
        participants=args.participants,
        events=events,
        claim_id=args.claim,
        issue_id=args.issue,
    )

    if args.save:
        out = save_evaluation(eval_doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(eval_doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*58}")
    print(f"  Cooperation Evaluation: {eval_doc['claim_id']}")
    print(f"{'='*58}")
    print(f"  Issue:             #{eval_doc['issue_id']}")
    print(f"  Participants:      {', '.join(eval_doc['participants'])}")
    print(f"  Total events:      {eval_doc['total_events']}")
    print(f"\n  Events observed:")
    for etype, count in eval_doc["events"].items():
        w = EVENT_WEIGHTS.get(etype, 0.0)
        print(f"    {etype:<20} {count:>2}  (weight {w:.2f})")
    print(f"\n  Cooperation signal: {eval_doc['cooperation_signal']}  (advisory)")
    print(f"    Event coverage:    {eval_doc['signal_components']['event_coverage']}")
    print(f"    Diversity mult.:   {eval_doc['signal_components']['diversity_multiplier']}")
    h = eval_doc["healthy_negotiation"]
    print(f"\n  Dissent present:   {'✓ (healthy)' if h['dissent_present'] else '○ (none)'}")
    print(f"  Contest events:    {h['contest_count']}")
    print(f"  Reaffirm events:   {h['reaffirm_count']}")
    print(f"\n  execution_allowed: {eval_doc['execution_allowed']}")
    print(f"  moves_money:       {eval_doc['moves_money']}")
    print(f"  advisory:          {eval_doc['advisory']}")
    print(f"  economic_value:    {eval_doc['economic_value']}")
    print()


if __name__ == "__main__":
    main()
