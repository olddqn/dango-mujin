"""
appeal_packet_builder.py — Appeal Packet Builder (Advisory)

Assembles a complete appeal packet by combining:
  - The recognition appeal record (Phase 14)
  - The unrecognized contribution record (Phase 13)
  - The contribution candidate record (Phase 11)
  - The external credit observation (Phase 12)

An appeal packet is a self-contained advisory document that an external
system may consult when reconsidering a contribution's credit status.

Dan-Go builds the packet. Dan-Go does not submit it.
The external system may or may not consult the packet.
The packet does not compel any response.

This file does NOT:
  - Submit the packet to any external system
  - Force credit issuance
  - Create enforceable claims
  - Move funds
  - Perform wallet operations
  - Call any API

Core principles:
  "Appeal is not enforcement."
  "Recognition remains external."

No secrets. No private keys. No wallet operations. No network. stdlib only.

Usage:
    python bridge/gitsea/appeal/runtime/appeal_packet_builder.py
    python bridge/gitsea/appeal/runtime/appeal_packet_builder.py --save
    python bridge/gitsea/appeal/runtime/appeal_packet_builder.py --json
    python bridge/gitsea/appeal/runtime/appeal_packet_builder.py \\
        --contributor external-001 --claim housing-007 --issue 1
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_FILE_DIR        = Path(__file__).parent
_APPEAL          = _FILE_DIR.parent
_EXAMPLES        = _APPEAL / "examples"
_REPO_ROOT       = _APPEAL.parent.parent.parent
_CREDIT_EXAMPLES = _REPO_ROOT / "bridge" / "gitsea" / "credit" / "examples"
_EXT_EXAMPLES    = _REPO_ROOT / "bridge" / "gitsea" / "external_credit" / "examples"
_REF_EXAMPLES    = _REPO_ROOT / "bridge" / "gitsea" / "reflection" / "examples"


# ── Packet builder ────────────────────────────────────────────────────────────

def build_appeal_packet(
    contributor_id: str,
    claim_id: str,
    issue_id: int,
    contribution_type: str,
    contribution_label: str = "",
    pr_id: int | str | None = None,
    appeal_grounds: str = "general_reconsideration",
    candidate_credit: bool = True,
    external_credit: bool = False,
    external_system: str = "gitsea",
) -> dict[str, Any]:
    """
    Build a self-contained advisory appeal packet.

    Assembles references to Phase 11-13 records into a single document
    that an external system may consult when reconsidering credit status.

    Parameters
    ----------
    contributor_id : str
        Pseudonymous contributor identifier.
    claim_id : str
        Dan-Go claim identifier.
    issue_id : int
        GitHub issue number.
    contribution_type : str
        Type of contribution.
    contribution_label : str
        Human-readable label.
    pr_id : int | str | None
        GitHub PR number.
    appeal_grounds : str
        Stated grounds for the appeal.
    candidate_credit : bool
        Whether candidate_credit was true in Phase 11.
    external_credit : bool
        Whether external credit was detected in Phase 12.
    external_system : str
        External system the packet references.
    """
    packet_id = f"packet-{claim_id}-issue-{issue_id}-{contributor_id}"
    gap_present = candidate_credit and not external_credit

    return {
        "packet_type":       "appeal_packet",
        "generated_at":      datetime.now(timezone.utc).isoformat(),
        "packet_id":         packet_id,

        # Packet header
        "appellant":         contributor_id,
        "appeal_to":         external_system,
        "claim_id":          claim_id,
        "issue_id":          issue_id,
        "pr_id":             pr_id,

        # Phase 11 summary (contribution candidate)
        "phase_11_summary": {
            "phase":             11,
            "record_type":       "contribution_candidate",
            "contributor_id":    contributor_id,
            "contribution_type": contribution_type,
            "contribution_label": contribution_label or contribution_type,
            "candidate_credit":  candidate_credit,
            "credit_issued":     False,
            "source":            "bridge/gitsea/credit/runtime/contribution_candidate.py",
        },

        # Phase 12 summary (external credit observation)
        "phase_12_summary": {
            "phase":                12,
            "record_type":          "external_credit_snapshot",
            "external_system":      external_system,
            "external_credit":      external_credit,
            "observation_status":   (
                "no_credit_detected" if not external_credit else "credit_detected"
            ),
            "source":               "bridge/gitsea/external_credit/runtime/external_credit_snapshot.py",
        },

        # Phase 13 summary (reflection memory)
        "phase_13_summary": {
            "phase":             13,
            "record_type":       "unrecognized_contribution",
            "contributor_id":    contributor_id,
            "recognized":        False,
            "is_failure":        False,
            "is_accusation":     False,
            "contribution_lost": False,
            "source":            "bridge/gitsea/reflection/runtime/unrecognized_contribution.py",
        },

        # Appeal content
        "appeal_grounds":    appeal_grounds,
        "gap_present":       gap_present,

        # What the packet does and doesn't do
        "packet_is_submission":   False,   # invariant — not submitted by Dan-Go
        "packet_compels_response": False,  # invariant — no response required
        "packet_creates_authority": False, # invariant — no authority created
        "packet_note": (
            f"This packet assembles the Phase 11-13 contribution record for "
            f"{contributor_id} (claim {claim_id}, issue #{issue_id}). "
            f"It is advisory only. {external_system} may consult it when "
            "reconsidering credit status. Dan-Go does not submit this packet "
            f"to {external_system}. Recognition remains external."
        ),

        # Permanent invariants
        "credit_issued":      False,
        "moves_money":        False,
        "execution_allowed":  False,
        "hard_enforcement":   False,
        "advisory":           True,
        "appeal_only":        True,
        "authority":          "none",
        "append_only":        True,
        "contestable":        True,
        "reopenable":         True,

        "principle_1": "Appeal is not enforcement.",
        "principle_2": "Recognition remains external.",
    }


# ── Default packets ───────────────────────────────────────────────────────────

DEFAULT_PACKET_SPECS = [
    {
        "contributor_id":    "external-001",
        "claim_id":          "housing-007",
        "issue_id":          1,
        "pr_id":             1,
        "contribution_type": "evidence_reviewed",
        "contribution_label": "Evidence reviewed and approved",
        "appeal_grounds":    "Review was performed and recorded as credit-eligible in Phase 11.",
    },
    {
        "contributor_id":    "external-002",
        "claim_id":          "housing-007",
        "issue_id":          1,
        "pr_id":             1,
        "contribution_type": "evidence_accepted",
        "contribution_label": "Evidence accepted via PR merge",
        "appeal_grounds":    "Evidence submitted was complete and accepted in Dan-Go negotiation.",
    },
]


def build_packets_list(
    raw_specs: list[dict] | None = None,
) -> dict[str, Any]:
    """Build a list of appeal packets."""
    specs = raw_specs if raw_specs is not None else DEFAULT_PACKET_SPECS
    packets = [
        build_appeal_packet(
            contributor_id=s["contributor_id"],
            claim_id=s["claim_id"],
            issue_id=s["issue_id"],
            contribution_type=s["contribution_type"],
            contribution_label=s.get("contribution_label", ""),
            pr_id=s.get("pr_id"),
            appeal_grounds=s.get("appeal_grounds", "general_reconsideration"),
        )
        for s in specs
    ]
    return {
        "list_type":          "appeal_packet_list",
        "generated_at":       datetime.now(timezone.utc).isoformat(),
        "total_packets":      len(packets),
        "packets":            packets,

        "list_note": (
            f"{len(packets)} appeal packet(s) assembled. "
            "No packet is submitted to any external system. "
            "Recognition remains external."
        ),

        # Invariants
        "credit_issued":      False,
        "moves_money":        False,
        "execution_allowed":  False,
        "hard_enforcement":   False,
        "advisory":           True,
        "appeal_only":        True,
        "authority":          "none",
        "append_only":        True,

        "principle_1": "Appeal is not enforcement.",
        "principle_2": "Recognition remains external.",
    }


# ── Save ──────────────────────────────────────────────────────────────────────

def save_packet(doc: dict, out_path: Path | None = None) -> Path:
    if out_path is None:
        out_path = _EXAMPLES / "appeal-packet.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Build advisory appeal packets (not submitted to any system).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Appeal is not enforcement.
Recognition remains external.
Dan-Go builds packets; it does not submit them.

Examples:
  python bridge/gitsea/appeal/runtime/appeal_packet_builder.py
  python bridge/gitsea/appeal/runtime/appeal_packet_builder.py --save
  python bridge/gitsea/appeal/runtime/appeal_packet_builder.py --json
  python bridge/gitsea/appeal/runtime/appeal_packet_builder.py \\
      --contributor external-001 --claim housing-007 --issue 1 \\
      --type evidence_reviewed
        """,
    )
    p.add_argument("--contributor", default=None)
    p.add_argument("--claim", default=None)
    p.add_argument("--issue", type=int, default=None)
    p.add_argument("--type", default=None, dest="ctype")
    p.add_argument("--pr", default=None)
    p.add_argument("--save", action="store_true",
                   help="Save to appeal/examples/appeal-packet.json")
    p.add_argument("--json", action="store_true", dest="json_output")
    args = p.parse_args()

    if args.contributor and args.claim and args.issue and args.ctype:
        doc = build_appeal_packet(
            contributor_id=args.contributor,
            claim_id=args.claim,
            issue_id=args.issue,
            contribution_type=args.ctype,
            pr_id=args.pr,
        )
    else:
        doc = build_packets_list()

    if args.save:
        out = save_packet(doc)
        print(f"Saved: {out}")

    if args.json_output:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return

    # Default: human-readable
    print(f"\n{'='*60}")
    print(f"  Appeal Packets")
    print(f"{'='*60}")

    if "packets" in doc:
        print(f"  Total packets: {doc['total_packets']}")
        print()
        for pk in doc["packets"]:
            print(f"  ↑  [{pk['appellant']}]  "
                  f"{pk['phase_11_summary']['contribution_label']}")
            print(f"       claim: {pk['claim_id']}  issue: #{pk['issue_id']}")
            p11 = pk["phase_11_summary"]
            p12 = pk["phase_12_summary"]
            print(f"       candidate_credit={p11['candidate_credit']}  "
                  f"external_credit={p12['external_credit']}")
            print(f"       is_submission={pk['packet_is_submission']}  "
                  f"compels_response={pk['packet_compels_response']}")
    else:
        print(f"  Packet ID:       {doc['packet_id']}")
        print(f"  Appellant:       {doc['appellant']}")
        print(f"  Is submission:   {doc['packet_is_submission']}")
        print(f"  Compels response:{doc['packet_compels_response']}")

    print(f"\n  credit_issued:    {doc.get('credit_issued', False)}")
    print(f"  appeal_only:      {doc.get('appeal_only', True)}")
    print(f"  hard_enforcement: {doc.get('hard_enforcement', False)}")
    print(f"  moves_money:      {doc.get('moves_money', False)}")
    print(f"  advisory:         {doc.get('advisory', True)}")
    print(f"  authority:        {doc.get('authority', 'none')}")
    print(f"\n  \"{doc.get('principle_1', '')}\"")
    print(f"  \"{doc.get('principle_2', '')}\"")
    print()


if __name__ == "__main__":
    main()
