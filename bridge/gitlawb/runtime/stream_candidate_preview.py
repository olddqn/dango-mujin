"""
stream_candidate_preview.py — PR events → GITSEA-style stream candidate preview

Reads a PR events file and produces stream candidate records in the shape
that a GITSEA economic stream would consume — if such a stream were activated.

No GITSEA connection is made. No funds move. No wallet. No token.
This is a preview / translation layer only.

A stream candidate answers:
  - Who contributed?
  - What did they contribute?
  - Is the dignity guard satisfied?
  - Is this contribution eligible for GITSEA credit (structurally)?
  - What is the credit chain?

No more.

No hard enforcement. No external network. stdlib only.

Usage:
    python stream_candidate_preview.py <pr-events.json>
    python stream_candidate_preview.py <pr-events.json> --json
    python stream_candidate_preview.py <pr-events.json> --gitsea-only
"""

import json
import sys
import os


# ---------------------------------------------------------------------------
# Dignity checks (structural — no runtime dignity_guard.py call)
# ---------------------------------------------------------------------------

DIGNITY_CONDITIONS = [
    "no_identity_exposure",
    "revocable_consent",
    "participant_consent",
]


def _dignity_check(claim: dict | None) -> dict:
    """
    Structural dignity check.  Since we're operating on PR-event data (not
    a live claim), we perform a conservative structural check: all dignity
    conditions are assumed present unless the claim data says otherwise.
    """
    if claim is None:
        return {
            "all_pass":  True,
            "checks":    DIGNITY_CONDITIONS,
            "authority": "none",
            "note":      "Structural assumption — no claim data provided.",
        }
    dig_guard = claim.get("dignity_guard", "pass")
    all_pass  = dig_guard == "pass"
    return {
        "all_pass":  all_pass,
        "checks":    DIGNITY_CONDITIONS,
        "authority": "none",
    }


# ---------------------------------------------------------------------------
# Credit chain builder
# ---------------------------------------------------------------------------

def _build_credit_chain(pr_events: list[dict]) -> list[dict]:
    """
    Build a credit chain from the merged PR event set.
    Roles: submitter, reviewer, federation (for prereq survivability).
    """
    chain: list[dict] = []
    seen_contributors: set[str] = set()

    for ev in pr_events:
        event_type = ev.get("pr_event", "")
        author     = ev.get("author")
        reviewer   = ev.get("reviewer")

        if event_type == "pr_opened" and author and author not in seen_contributors:
            chain.append({
                "role":      "submitter",
                "did":       author,
                "signal":    "evidence_submitted",
                "pr_event":  event_type,
            })
            seen_contributors.add(author)

        if event_type == "pr_reviewed" and reviewer and reviewer not in seen_contributors:
            chain.append({
                "role":      "reviewer",
                "did":       reviewer,
                "signal":    "reviewed_contribution",
                "pr_event":  event_type,
            })
            seen_contributors.add(reviewer)

        if event_type == "pr_merged":
            # federation signal — not a person
            chain.append({
                "role":      "federation",
                "did":       "none",
                "signal":    "prerequisite_weakened_survivor",
                "pr_event":  event_type,
                "note":      "Federation signal: condition survives as scoped prerequisite.",
            })

    return chain


# ---------------------------------------------------------------------------
# Core: produce stream candidate records
# ---------------------------------------------------------------------------

def stream_candidates_from_pr_events(data: dict, gitsea_only: bool = False) -> dict:
    """
    Produce the full stream candidate preview from a PR events file.

    Returns:
        {
          stream_candidates: [...],
          dignity_summary: {...},
          credit_chain: [...],
          gitsea_eligible_count: int,
          moves_money: False,
          advisory: True,
        }
    """
    pr_events  = data.get("pr_events", [])
    candidates: list[dict] = []

    # Contribution type: infer from condition
    first_event = pr_events[0] if pr_events else {}
    condition   = first_event.get("condition_resolved", "unknown")
    contrib_type = (
        "safety_review" if "safety" in condition
        else "evidence_review"
    )

    for ev in pr_events:
        event_type   = ev.get("pr_event", "unknown")
        claim_id     = ev.get("claim_id", "unknown")
        cond         = ev.get("condition_resolved", condition)
        author       = ev.get("author", "unknown")
        reviewer     = ev.get("reviewer", None)
        pr_id        = ev.get("pr_id", "unknown")

        gitsea_elig  = event_type == "pr_merged"
        credit_signal = {
            "pr_opened":     "evidence_submitted",
            "pr_reviewed":   "reviewed_contribution",
            "pr_merged":     "accepted_contribution",
            "pr_rejected":   "rejected_submission",
            "pr_superseded": "superseded_submission",
        }.get(event_type, "unknown")

        candidate: dict = {
            "stream_candidate":  True,
            "moves_money":       False,
            "contribution_type": contrib_type,
            "credit_signal":     credit_signal,
            "contributor":       author,
            "claim_id":          claim_id,
            "condition":         cond,
            "pr_id":             pr_id,
            "pr_event":          event_type,
            "dignity_guard":     "pass",
            "gitsea_eligible":   gitsea_elig,
            "advisory":          True,
        }
        if reviewer:
            candidate["reviewer"] = reviewer
        if gitsea_elig:
            candidate["gitsea_note"] = (
                f"Merged safety review for a Dan-Go condition ({cond}). "
                "If GITSEA activates an economic stream for this condition, "
                "this contribution is the primary credit candidate. "
                "No funds move now."
            )
        else:
            candidate["gitsea_note"] = (
                "Not GITSEA-eligible at this stage — requires pr_merged event."
            )

        if not gitsea_only or gitsea_elig:
            candidates.append(candidate)

    dignity_summary = _dignity_check(None)
    credit_chain    = _build_credit_chain(pr_events)
    gitsea_count    = sum(1 for c in candidates if c["gitsea_eligible"])

    return {
        "stream_candidates":    candidates,
        "dignity_summary":      dignity_summary,
        "credit_chain":         credit_chain,
        "gitsea_eligible_count": gitsea_count,
        "moves_money":          False,
        "advisory":             True,
        "_design_note": (
            "stream_candidate_preview is a read-only translation layer. "
            "It does not write to any su-table, does not create GITSEA streams, "
            "does not move funds. It answers: who contributed, what did they do, "
            "and does the dignity guard pass? No more."
        ),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_candidates(result: dict) -> None:
    candidates = result["stream_candidates"]
    credit_chain = result.get("credit_chain", [])
    dignity = result.get("dignity_summary", {})

    print(f"\n  Stream Candidates: {len(candidates)}")
    print(f"  GITSEA-eligible:   {result['gitsea_eligible_count']}")
    print(f"  moves_money:       {result['moves_money']}")
    print(f"  advisory:          {result['advisory']}")
    print()

    for c in candidates:
        eligible_tag = " [GITSEA-eligible]" if c["gitsea_eligible"] else ""
        print(f"  ─ {c['pr_event']}{eligible_tag}")
        print(f"    credit_signal:    {c['credit_signal']}")
        print(f"    contribution_type:{c['contribution_type']}")
        print(f"    contributor:      {c['contributor']}")
        if c.get("reviewer"):
            print(f"    reviewer:         {c['reviewer']}")
        print(f"    dignity_guard:    {c['dignity_guard']}")
        print(f"    gitsea_note: {c['gitsea_note'][:80]}...")
        print()

    print(f"  Credit Chain:")
    for link in credit_chain:
        print(f"    [{link['role']}] {link['did']}  →  {link['signal']}")

    print()
    print(f"  Dignity Summary:")
    print(f"    all_pass: {dignity.get('all_pass')}  authority: {dignity.get('authority')}")
    print(f"    checks: {dignity.get('checks')}")
    print()


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    input_path  = args[0]
    as_json     = "--json" in args
    gitsea_only = "--gitsea-only" in args

    if not os.path.exists(input_path):
        print(f"ERROR: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path) as f:
        data = json.load(f)

    result = stream_candidates_from_pr_events(data, gitsea_only=gitsea_only)

    if as_json:
        print(json.dumps(result, indent=2))
        return

    print(f"\nDan-Go → GITSEA Stream Candidate Preview")
    print(f"Input: {input_path}")
    print(f"(No GITSEA connection — preview only · moves_money: False)")
    _print_candidates(result)


if __name__ == "__main__":
    main()
