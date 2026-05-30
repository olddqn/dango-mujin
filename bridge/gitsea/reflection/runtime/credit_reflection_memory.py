"""
credit_reflection_memory.py — Credit Reflection Memory (Advisory, Append-Only)

Records the full lifecycle of a contribution candidate as reflection memory:
  - The candidate was created (Phase 11)
  - External credit was checked (Phase 12)
  - No external credit was observed
  - The gap was recorded
  - Reflection is now stored

Dan-Go remembers. It does not punish, rank, or decide.
A contribution that was not credited is still a contribution that happened.
A gap that was recorded is still an observable fact.

This file does NOT:
  - Issue credit
  - Appeal to external systems
  - Judge contributors
  - Rank contributions
  - Move funds
  - Perform wallet operations
  - Call any API

Core principles:
  "Unrecognized contribution is still observable."
  "Reflection is not judgment."

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/reflection/runtime/credit_reflection_memory.py
    python bridge/gitsea/reflection/runtime/credit_reflection_memory.py --save
    python bridge/gitsea/reflection/runtime/credit_reflection_memory.py --json
    python bridge/gitsea/reflection/runtime/credit_reflection_memory.py \\
        --claim housing-007 --issue 1 --contributor external-001
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_FILE_DIR   = Path(__file__).parent
_REFLECTION = _FILE_DIR.parent
_EXAMPLES   = _REFLECTION / "examples"


# ── Lifecycle stages recorded in memory ──────────────────────────────────────

REFLECTION_STAGES = [
    "candidate_created",
    "external_credit_checked",
    "credit_not_observed",
    "gap_recorded",
    "reflection_stored",
]

STAGE_LABELS = {
    "candidate_created":      "Contribution candidate recorded in Dan-Go (Phase 11)",
    "external_credit_checked": "External credit system observed (Phase 12)",
    "credit_not_observed":    "No external credit detected in observed system",
    "gap_recorded":           "Gap between candidate and external credit documented",
    "reflection_stored":      "Reflection memory stored (Phase 13)",
}


# ── Memory builder ────────────────────────────────────────────────────────────

def build_credit_reflection_memory(
    claim_id: str,
    issue_id: int,
    contributor_id: str,
    contribution_type: str,
    candidate_credit: bool,
    external_system: str = "gitsea",
    external_credit: bool = False,
    stages: list[str] | None = None,
    contribution_label: str = "",
) -> dict[str, Any]:
    """
    Build a credit reflection memory record.

    Records the full lifecycle of a contribution candidate from creation
    through external credit observation. The memory persists regardless
    of whether external credit was ever issued.

    Parameters
    ----------
    claim_id : str
        Dan-Go claim identifier.
    issue_id : int
        GitHub issue number.
    contributor_id : str
        Pseudonymous contributor identifier.
    contribution_type : str
        Type of contribution (from Phase 11 CONTRIBUTION_TYPES).
    candidate_credit : bool
        Whether this contribution had candidate_credit=true in Phase 11.
    external_system : str
        External system that was observed.
    external_credit : bool
        Whether external credit was detected (default False).
    stages : list[str] | None
        Lifecycle stages completed. Defaults to all five stages.
    contribution_label : str
        Human-readable label for the contribution type.
    """
    completed_stages = stages if stages is not None else list(REFLECTION_STAGES)
    stage_records = [
        {
            "stage":        s,
            "label":        STAGE_LABELS[s],
            "completed":    s in completed_stages,
        }
        for s in REFLECTION_STAGES
    ]

    return {
        "memory_type":       "credit_reflection_memory",
        "generated_at":      datetime.now(timezone.utc).isoformat(),
        "memory_id":         f"mem-{claim_id}-issue-{issue_id}-{contributor_id}",

        # Contribution identity
        "claim_id":          claim_id,
        "issue_id":          issue_id,
        "contributor_id":    contributor_id,
        "contribution_type": contribution_type,
        "contribution_label": contribution_label or contribution_type,

        # Candidate state (from Phase 11)
        "candidate_credit":  candidate_credit,

        # External observation state (from Phase 12)
        "external_system":   external_system,
        "external_credit":   external_credit,

        # Reflection lifecycle
        "stages":            stage_records,
        "stages_completed":  len(completed_stages),
        "stages_total":      len(REFLECTION_STAGES),
        "reflection_complete": len(completed_stages) == len(REFLECTION_STAGES),

        # What the memory records
        "gap_present":       candidate_credit and not external_credit,
        "gap_is_failure":    False,   # invariant — a gap is never a failure
        "contribution_lost": False,   # invariant — contribution is always observable

        # Permanent invariants
        "credit_issued":      False,
        "moves_money":        False,
        "execution_allowed":  False,
        "hard_enforcement":   False,
        "advisory":           True,
        "reflection_only":    True,
        "authority":          "none",
        "append_only":        True,
        "contestable":        True,
        "reopenable":         True,

        "principle_1": "Unrecognized contribution is still observable.",
        "principle_2": "Reflection is not judgment.",
        "memory_note": (
            "Dan-Go records contribution reflection memory. "
            "Gaps are observable facts, not accusations. "
            "External systems remain sovereign over credit decisions."
        ),
    }


# ── Default memory records ────────────────────────────────────────────────────

DEFAULT_MEMORIES = [
    {
        "claim_id":          "housing-007",
        "issue_id":          1,
        "contributor_id":    "external-001",
        "contribution_type": "evidence_reviewed",
        "contribution_label": "Evidence reviewed and approved",
        "candidate_credit":  True,
        "external_credit":   False,
    },
    {
        "claim_id":          "housing-007",
        "issue_id":          1,
        "contributor_id":    "external-002",
        "contribution_type": "evidence_accepted",
        "contribution_label": "Evidence accepted via PR merge",
        "candidate_credit":  True,
        "external_credit":   False,
    },
    {
        "claim_id":          "housing-007",
        "issue_id":          1,
        "contributor_id":    "external-003",
        "contribution_type": "contest_raised",
        "contribution_label": "Legitimate contest raised",
        "candidate_credit":  False,
        "external_credit":   False,
    },
]


def build_reflection_memory_list(
    raw_memories: list[dict] | None = None,
) -> dict[str, Any]:
    """Build an aggregated list of credit reflection memory records."""
    raws = raw_memories if raw_memories is not None else DEFAULT_MEMORIES
    memories = [
        build_credit_reflection_memory(
            claim_id=r["claim_id"],
            issue_id=r["issue_id"],
            contributor_id=r["contributor_id"],
            contribution_type=r["contribution_type"],
            candidate_credit=r.get("candidate_credit", False),
            external_credit=r.get("external_credit", False),
            contribution_label=r.get("contribution_label", ""),
        )
        for r in raws
    ]
    gap_count = sum(1 for m in memories if m["gap_present"])
    return {
        "list_type":        "credit_reflection_memory_list",
        "generated_at":     datetime.now(timezone.utc).isoformat(),
        "total_memories":   len(memories),
        "gap_count":        gap_count,
        "memories":         memories,

        # Invariants
        "credit_issued":    False,
        "moves_money":      False,
        "execution_allowed": False,
        "hard_enforcement": False,
        "advisory":         True,
        "reflection_only":  True,
        "authority":        "none",
        "append_only":      True,

        "principle_1": "Unrecognized contribution is still observable.",
        "principle_2": "Reflection is not judgment.",
    }


# ── Save ──────────────────────────────────────────────────────────────────────

def save_memory(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "credit-reflection-memory.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Record credit reflection memory (advisory, no credit issued).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Unrecognized contribution is still observable.
Reflection is not judgment.
Dan-Go remembers; it does not punish, rank, or decide.

Examples:
  python bridge/gitsea/reflection/runtime/credit_reflection_memory.py
  python bridge/gitsea/reflection/runtime/credit_reflection_memory.py --save
  python bridge/gitsea/reflection/runtime/credit_reflection_memory.py --json
  python bridge/gitsea/reflection/runtime/credit_reflection_memory.py \\
      --claim housing-007 --issue 1 --contributor external-001 \\
      --type evidence_reviewed
        """,
    )
    p.add_argument("--claim", default=None)
    p.add_argument("--issue", type=int, default=None)
    p.add_argument("--contributor", default=None)
    p.add_argument("--type", default=None, dest="ctype",
                   help="Contribution type")
    p.add_argument("--external-credit", action="store_true",
                   help="Mark external credit as detected (default: false)")
    p.add_argument("--save", action="store_true",
                   help="Save to reflection/examples/credit-reflection-memory.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    if args.claim and args.issue and args.contributor and args.ctype:
        doc = build_credit_reflection_memory(
            claim_id=args.claim,
            issue_id=args.issue,
            contributor_id=args.contributor,
            contribution_type=args.ctype,
            candidate_credit=True,
            external_credit=args.external_credit,
        )
    else:
        doc = build_reflection_memory_list()

    if args.save:
        out = save_memory(doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*60}")
    print(f"  Credit Reflection Memory")
    print(f"{'='*60}")

    if "memories" in doc:
        print(f"  Total memories: {doc['total_memories']}")
        print(f"  Gaps present:   {doc['gap_count']}  (none are failures)")
        print()
        for m in doc["memories"]:
            mark = "△" if m["gap_present"] else "✓"
            print(f"  {mark}  [{m['contributor_id']}]  {m['contribution_label']}")
            print(f"       candidate_credit={m['candidate_credit']}  "
                  f"external_credit={m['external_credit']}  "
                  f"gap={m['gap_present']}")
    else:
        print(f"  Memory ID:      {doc['memory_id']}")
        print(f"  Contributor:    {doc['contributor_id']}")
        print(f"  Type:           {doc['contribution_label']}")
        print(f"  Stages:         {doc['stages_completed']}/{doc['stages_total']}")
        print(f"  Gap present:    {doc['gap_present']}")
        print(f"  Gap is failure: {doc['gap_is_failure']}")

    print(f"\n  credit_issued:      {doc.get('credit_issued', False)}")
    print(f"  reflection_only:    {doc.get('reflection_only', True)}")
    print(f"  moves_money:        {doc.get('moves_money', False)}")
    print(f"  execution_allowed:  {doc.get('execution_allowed', False)}")
    print(f"  advisory:           {doc.get('advisory', True)}")
    print(f"  authority:          {doc.get('authority', 'none')}")
    print(f"\n  \"{doc.get('principle_1', '')}\"")
    print(f"  \"{doc.get('principle_2', '')}\"")
    print()


if __name__ == "__main__":
    main()
