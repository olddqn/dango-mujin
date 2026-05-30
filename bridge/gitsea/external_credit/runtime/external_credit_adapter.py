"""
external_credit_adapter.py — External Credit System Adapter (Observation Only)

Represents known external credit systems and their observed state relative
to Dan-Go contribution candidates.

An external credit adapter record:
  - Names the external system (e.g. GITSEA)
  - Records whether credit is currently visible from that system
  - Records whether credit has been issued (always: not by Dan-Go)
  - Records the observation timestamp and status

This file does NOT:
  - Issue credit
  - Activate GITSEA streams
  - Modify external credit state
  - Call any external API
  - Move funds
  - Perform wallet operations

Dan-Go observes external credit systems. It does not operate them.

Core principles:
  "Observation is not issuance."
  "Candidate credit is not external credit."

All records are advisory. All records are append-only.
credit_issued is always False.

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/external_credit/runtime/external_credit_adapter.py
    python bridge/gitsea/external_credit/runtime/external_credit_adapter.py --save
    python bridge/gitsea/external_credit/runtime/external_credit_adapter.py --json
    python bridge/gitsea/external_credit/runtime/external_credit_adapter.py \\
        --system gitsea --claim housing-007 --issue 1
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_FILE_DIR       = Path(__file__).parent
_EXTERNAL_CREDIT = _FILE_DIR.parent
_EXAMPLES       = _EXTERNAL_CREDIT / "examples"


# ── Known external systems ────────────────────────────────────────────────────

EXTERNAL_SYSTEMS = {
    "gitsea": {
        "name":        "GITSEA",
        "description": "Git-native economic system for on-chain repository credit",
        "chain":       "Base",
        "repovault":   "0x3F9c96A429697B458Fe0a16502A050E5AB50bB00",
        "sovereign":   True,
        "note": (
            "GITSEA is sovereign over its own credit decisions. "
            "Dan-Go does not push candidates to GITSEA. "
            "Dan-Go does not activate or confirm GITSEA credit."
        ),
    },
}


# ── Adapter builder ───────────────────────────────────────────────────────────

def build_external_credit_adapter(
    system_id: str = "gitsea",
    claim_id: str = "housing-007",
    issue_id: int = 1,
    observed: bool = True,
    credit_visible: bool = False,
) -> dict[str, Any]:
    """
    Build an advisory external credit adapter record.

    Represents the current observed state of an external credit system
    relative to a Dan-Go claim. Does not modify any external state.

    Parameters
    ----------
    system_id : str
        External system identifier (e.g. "gitsea").
    claim_id : str
        Dan-Go claim identifier.
    issue_id : int
        GitHub issue number.
    observed : bool
        Whether the external system has been observed (always True in practice).
    credit_visible : bool
        Whether credit is currently visible in the external system.
        Default False — no external credit detected.
    """
    if system_id not in EXTERNAL_SYSTEMS:
        raise ValueError(
            f"Unknown system {system_id!r}. Valid: {list(EXTERNAL_SYSTEMS)}"
        )
    sys_info = EXTERNAL_SYSTEMS[system_id]

    return {
        "adapter_type":       "external_credit_adapter",
        "generated_at":       datetime.now(timezone.utc).isoformat(),

        # System identity
        "system":             system_id,
        "system_name":        sys_info["name"],
        "system_description": sys_info["description"],
        "system_sovereign":   sys_info["sovereign"],
        "system_note":        sys_info["note"],

        # Claim context
        "claim_id":           claim_id,
        "issue_id":           issue_id,

        # Observed state
        "observed":           observed,
        "credit_visible":     credit_visible,
        "credit_issued":      False,   # permanent invariant — never issued by Dan-Go
        "observation_status": (
            "credit_detected" if credit_visible else "no_credit_detected"
        ),

        # What this adapter does NOT do
        "dango_issues_credit":    False,
        "dango_activates_stream": False,
        "dango_modifies_external": False,

        # Invariants
        "moves_money":        False,
        "execution_allowed":  False,
        "hard_enforcement":   False,
        "advisory":           True,
        "authority":          "none",
        "append_only":        True,
        "contestable":        True,
        "reopenable":         True,

        "observation_note": (
            "Dan-Go observes external credit systems. It does not operate them. "
            "Observation is not issuance. "
            "Candidate credit is not external credit."
        ),
        "principle_1": "Observation is not issuance.",
        "principle_2": "Candidate credit is not external credit.",
    }


# ── Default adapters ──────────────────────────────────────────────────────────

DEFAULT_ADAPTERS = [
    {
        "system_id":     "gitsea",
        "claim_id":      "housing-007",
        "issue_id":      1,
        "observed":      True,
        "credit_visible": False,   # No external credit detected yet
    },
]


def build_adapters_list(
    raw_adapters: list[dict] | None = None,
) -> dict[str, Any]:
    """Build a list of external credit adapter records."""
    raws = raw_adapters if raw_adapters is not None else DEFAULT_ADAPTERS
    adapters = [
        build_external_credit_adapter(
            system_id=r["system_id"],
            claim_id=r.get("claim_id", "housing-007"),
            issue_id=r.get("issue_id", 1),
            observed=r.get("observed", True),
            credit_visible=r.get("credit_visible", False),
        )
        for r in raws
    ]
    credit_detected = [a for a in adapters if a["credit_visible"]]
    return {
        "list_type":             "external_credit_adapter_list",
        "generated_at":          datetime.now(timezone.utc).isoformat(),
        "total_adapters":        len(adapters),
        "credit_detected_count": len(credit_detected),
        "adapters":              adapters,

        # Invariants
        "credit_issued":         False,
        "moves_money":           False,
        "execution_allowed":     False,
        "hard_enforcement":      False,
        "advisory":              True,
        "authority":             "none",
        "append_only":           True,

        "principle_1": "Observation is not issuance.",
        "principle_2": "Candidate credit is not external credit.",
    }


# ── Save ──────────────────────────────────────────────────────────────────────

def save_adapter(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "credit-adapter.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Observe external credit systems (no credit issued).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Observation is not issuance.
Candidate credit is not external credit.
Dan-Go observes external credit systems; it does not operate them.

Examples:
  python bridge/gitsea/external_credit/runtime/external_credit_adapter.py
  python bridge/gitsea/external_credit/runtime/external_credit_adapter.py --save
  python bridge/gitsea/external_credit/runtime/external_credit_adapter.py --json
  python bridge/gitsea/external_credit/runtime/external_credit_adapter.py \\
      --system gitsea --claim housing-007 --issue 1
        """,
    )
    p.add_argument("--system", default=None,
                   choices=list(EXTERNAL_SYSTEMS),
                   help="External system to observe")
    p.add_argument("--claim", default="housing-007")
    p.add_argument("--issue", type=int, default=1)
    p.add_argument("--credit-visible", action="store_true",
                   help="Mark external credit as currently visible (default: false)")
    p.add_argument("--save", action="store_true",
                   help="Save to external_credit/examples/credit-adapter.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    if args.system:
        # Single adapter mode
        try:
            doc = build_external_credit_adapter(
                system_id=args.system,
                claim_id=args.claim,
                issue_id=args.issue,
                credit_visible=args.credit_visible,
            )
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        doc = build_adapters_list()

    if args.save:
        out = save_adapter(doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*60}")
    print(f"  External Credit Adapter")
    print(f"{'='*60}")

    if "adapters" in doc:
        print(f"  Total adapters:       {doc['total_adapters']}")
        print(f"  Credit detected:      {doc['credit_detected_count']}")
        print()
        for a in doc["adapters"]:
            mark = "✓" if a["credit_visible"] else "○"
            print(f"  {mark}  [{a['system']}]  claim: {a['claim_id']}  "
                  f"issue: #{a['issue_id']}")
            print(f"       status: {a['observation_status']}")
    else:
        print(f"  System:               {doc.get('system_name')}")
        print(f"  Claim:                {doc.get('claim_id')}  "
              f"(issue #{doc.get('issue_id')})")
        print(f"  Observed:             {doc.get('observed')}")
        print(f"  Credit visible:       {doc.get('credit_visible')}")
        print(f"  Status:               {doc.get('observation_status')}")

    print(f"\n  credit_issued:        False  (permanent: never by Dan-Go)")
    print(f"  moves_money:          {doc.get('moves_money', False)}")
    print(f"  execution_allowed:    {doc.get('execution_allowed', False)}")
    print(f"  advisory:             {doc.get('advisory', True)}")
    print(f"  authority:            {doc.get('authority', 'none')}")
    print(f"\n  \"{doc.get('principle_1', 'Observation is not issuance.')}\"")
    print(f"  \"{doc.get('principle_2', 'Candidate credit is not external credit.')}\"")
    print()


if __name__ == "__main__":
    main()
