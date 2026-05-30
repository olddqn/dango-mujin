"""
contributor_registry.py — Contributor Registry (Advisory, Append-Only)

Records contributors and their roles in the Dan-Go negotiation protocol.

A contributor registry entry records:
  - A pseudonymous contributor identifier
  - Their observed role in the negotiation (reviewer, author, contester, etc.)
  - Whether they are currently active in the negotiation

This file does NOT:
  - Issue credit
  - Assign rewards
  - Score contributors for economic outcomes
  - Link contributor identities to real-world persons
  - Connect to external systems

Contribution history is not credit.
Dan-Go records contribution candidates; external systems may issue credit.

All entries are advisory. All entries are append-only.
No contributor is penalized. No contributor is ranked.

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/credit/runtime/contributor_registry.py
    python bridge/gitsea/credit/runtime/contributor_registry.py --save
    python bridge/gitsea/credit/runtime/contributor_registry.py --json
    python bridge/gitsea/credit/runtime/contributor_registry.py --add external-001 reviewer
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_FILE_DIR = Path(__file__).parent
_CREDIT   = _FILE_DIR.parent
_EXAMPLES = _CREDIT / "examples"

# ── Role definitions ──────────────────────────────────────────────────────────

KNOWN_ROLES = {
    "author":     "Submitted original evidence or PR",
    "reviewer":   "Reviewed submitted evidence or PR",
    "contester":  "Contested a claim or plan (healthy dissent)",
    "reaffirmer": "Reaffirmed a position with new context",
    "observer":   "Observed the negotiation without direct contribution",
    "corrector":  "Proposed a plan correction",
}

# ── Default registry (housing-007 / Issue #1 participants) ───────────────────
# Pseudonymous. No real-world identity. No personal data.

DEFAULT_REGISTRY: list[dict[str, Any]] = [
    {
        "contributor_id": "external-001",
        "name":           "example_contributor",
        "role":           "reviewer",
        "claim_id":       "housing-007",
        "issue_id":       1,
        "active":         True,
        "registered_at":  "2026-05-30T00:00:00+00:00",
        "pseudonymous":   True,
    },
    {
        "contributor_id": "external-002",
        "name":           "evidence_author",
        "role":           "author",
        "claim_id":       "housing-007",
        "issue_id":       1,
        "active":         True,
        "registered_at":  "2026-05-30T00:00:00+00:00",
        "pseudonymous":   True,
    },
    {
        "contributor_id": "external-003",
        "name":           "dissent_contributor",
        "role":           "contester",
        "claim_id":       "housing-007",
        "issue_id":       1,
        "active":         True,
        "registered_at":  "2026-05-30T00:00:00+00:00",
        "pseudonymous":   True,
    },
]


# ── Registry builder ──────────────────────────────────────────────────────────

def build_registry(
    contributors: list[dict] | None = None,
) -> dict[str, Any]:
    """Build an advisory contributor registry."""
    entries = contributors if contributors is not None else DEFAULT_REGISTRY
    return {
        "registry_type":    "contributor_registry",
        "generated_at":     datetime.now(timezone.utc).isoformat(),
        "contributor_count": len(entries),
        "contributors":     entries,
        "known_roles":      KNOWN_ROLES,

        # Invariants
        "credit_issued":    False,
        "moves_money":      False,
        "execution_allowed": False,
        "hard_enforcement": False,
        "advisory":         True,
        "authority":        "none",
        "append_only":      True,
        "contestable":      True,
        "reopenable":       True,

        "contribution_note": "Contribution history is not credit.",
        "credit_note": (
            "Dan-Go records contribution candidates; "
            "external systems may issue credit."
        ),
        "identity_note": (
            "All contributor identifiers are pseudonymous. "
            "No real-world identity linkage. No personal data stored."
        ),
    }


def make_entry(
    contributor_id: str,
    role: str,
    name: str | None = None,
    claim_id: str = "housing-007",
    issue_id: int = 1,
) -> dict[str, Any]:
    if role not in KNOWN_ROLES:
        raise ValueError(f"Unknown role {role!r}. Valid: {list(KNOWN_ROLES)}")
    return {
        "contributor_id": contributor_id,
        "name":           name or contributor_id,
        "role":           role,
        "claim_id":       claim_id,
        "issue_id":       issue_id,
        "active":         True,
        "registered_at":  datetime.now(timezone.utc).isoformat(),
        "pseudonymous":   True,
    }


# ── Save (append-only) ────────────────────────────────────────────────────────

def save_registry(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "contributor-registry.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Record contributors in the Dan-Go negotiation protocol.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contribution history is not credit.
Dan-Go records contribution candidates; external systems may issue credit.

Roles: author, reviewer, contester, reaffirmer, observer, corrector

Examples:
  python bridge/gitsea/credit/runtime/contributor_registry.py
  python bridge/gitsea/credit/runtime/contributor_registry.py --save
  python bridge/gitsea/credit/runtime/contributor_registry.py --json
  python bridge/gitsea/credit/runtime/contributor_registry.py \\
      --add external-004 contester
        """,
    )
    p.add_argument("--add", nargs=2, metavar=("ID", "ROLE"),
                   help="Add a contributor: --add CONTRIBUTOR_ID ROLE")
    p.add_argument("--claim", default="housing-007")
    p.add_argument("--issue", type=int, default=1)
    p.add_argument("--save", action="store_true",
                   help="Save to credit/examples/contributor-registry.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    contributors = list(DEFAULT_REGISTRY)

    if args.add:
        cid, role = args.add
        try:
            entry = make_entry(cid, role, claim_id=args.claim, issue_id=args.issue)
            contributors.append(entry)
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)

    doc = build_registry(contributors)

    if args.save:
        out = save_registry(doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*58}")
    print(f"  Contributor Registry")
    print(f"{'='*58}")
    print(f"  Total contributors: {doc['contributor_count']}")
    print()
    for c in doc["contributors"]:
        print(f"  [{c['contributor_id']}]  {c['name']:<25}  role: {c['role']}")
        print(f"    claim: {c['claim_id']}  issue: #{c['issue_id']}")
    print(f"\n  credit_issued:      {doc['credit_issued']}")
    print(f"  moves_money:        {doc['moves_money']}")
    print(f"  execution_allowed:  {doc['execution_allowed']}")
    print(f"  advisory:           {doc['advisory']}")
    print(f"  authority:          {doc['authority']}")
    print(f"\n  \"{doc['contribution_note']}\"")
    print(f"  \"{doc['credit_note']}\"")
    print()


if __name__ == "__main__":
    main()
