#!/usr/bin/env python3
"""
federation_trust_propagation.py — dango-gitsea-bridge / federation branching

Compute cross-claim trust propagation within a federation.

When claims are connected (depends_on, enables, derived_from), trust
signals from contributors who have participated in upstream claims can
inform the starting trust baseline for downstream claims.

Trust propagation is:
  - Advisory — does not override local trust computation
  - Diminishing — propagated trust is attenuated across hops
  - Dignity-sensitive — dignity_violation resets propagated trust to 0
  - Deterministic — given same event log, same result always

Trust is NOT a credential. It is a coordination signal.
Propagated trust tells downstream plans: "this contributor has
demonstrated relevant participation in a related claim."

Output per (source_claim, target_claim) pair:
  {
    "source_claim":          str,
    "target_claim":          str,
    "shared_contributors":   [did, ...],
    "propagated_trust_weight": float,
    "attenuation_factor":    float,
    "dignity_gate_passed":   bool,
    "reason":                str,
    "per_contributor":       [{contributor, base_weight, propagated_weight}, ...]
  }

CLI:
  python runtime/federation_trust_propagation.py \
    --source-claim housing-001 --target-claim housing-002
  python runtime/federation_trust_propagation.py --all-pairs
  python runtime/federation_trust_propagation.py --all-pairs --json
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

# ── Trust attenuation ─────────────────────────────────────────────────────────

_DEFAULT_ATTENUATION = 0.8   # per federation hop
_DIGNITY_BLOCK_WEIGHT = 0.0  # dignity violation resets propagated trust to 0
_MAX_PROPAGATED_WEIGHT = 1.0 # cap on any individual propagated weight


# ── Contributor loading ────────────────────────────────────────────────────────

def _load_contributors(claim_id: str) -> dict[str, float]:
    """
    Load contributors and their current trust weights for a claim.

    Returns {contributor_did: trust_weight}.

    Sources:
      1. contributions.jsonl events for the claim (type: contribution_accepted)
      2. plans.jsonl speaker/proposer identifiers (treat as weight 1.0 baseline)
    """
    contributors: dict[str, float] = {}

    # From contributions table
    for ev in read_all("contributions"):
        if ev.get("claim_id") == claim_id and ev.get("event_type") == "contribution_accepted":
            cid  = ev.get("contributor", "")
            wt   = float(ev.get("trust_weight", ev.get("base_weight", 1.0)))
            if cid:
                contributors[cid] = max(contributors.get(cid, 0.0), wt)

    # From plans.jsonl speakers (plan proposers)
    for ev in read_all("plans"):
        if ev.get("claim_id") == claim_id:
            sp = ev.get("speaker", "")
            if sp and sp not in contributors:
                contributors[sp] = 1.0   # baseline — no decay applied

    return contributors


def _dignity_gate_passed(claim_id: str) -> bool:
    """Return True if the claim's plans have no dignity_violation objections."""
    return not any(
        ev.get("event_type") == "plan_objected"
        and ev.get("objection_type") == "dignity_violation"
        for ev in read_all("plans")
        if ev.get("claim_id") == claim_id
    )


# ── Core computation ──────────────────────────────────────────────────────────

def compute_trust_propagation(
    source_claim_id: str,
    target_claim_id: str,
    *,
    attenuation: float = _DEFAULT_ATTENUATION,
) -> dict[str, Any]:
    """
    Compute trust propagation from source_claim to target_claim.

    The propagated trust weight represents the aggregate trust signal
    that can be attributed to contributors active in the source claim,
    attenuated by the federation hop.

    Returns:
      {
        "source_claim":            str,
        "target_claim":            str,
        "shared_contributors":     [str, ...],
        "propagated_trust_weight": float,   ← aggregate, attenuated
        "attenuation_factor":      float,
        "dignity_gate_passed":     bool,
        "reason":                  str,
        "per_contributor":         [...]
      }
    """
    src_contributors = _load_contributors(source_claim_id)
    tgt_contributors = _load_contributors(target_claim_id)

    dignity_ok = _dignity_gate_passed(source_claim_id)

    # Shared contributors: present in both claims
    shared = sorted(set(src_contributors) & set(tgt_contributors))

    # Also include source-only contributors — they *could* contribute to target
    source_only = sorted(set(src_contributors) - set(tgt_contributors))

    per_contributor: list[dict[str, Any]] = []

    if not dignity_ok:
        # Dignity violation: propagated weight = 0 for all
        for cid_did in shared + source_only:
            per_contributor.append({
                "contributor":        cid_did,
                "base_weight":        src_contributors.get(cid_did, 0.0),
                "propagated_weight":  0.0,
                "reason":             "dignity_violation on source claim",
            })
        aggregate = 0.0
        reason = "dignity_violation on source claim — trust propagation blocked"
    else:
        for cid_did in shared:
            base = src_contributors.get(cid_did, 1.0)
            prop = min(base * attenuation, _MAX_PROPAGATED_WEIGHT)
            per_contributor.append({
                "contributor":        cid_did,
                "base_weight":        round(base, 4),
                "propagated_weight":  round(prop, 4),
                "reason":             "shared contributor — active in both claims",
            })
        for cid_did in source_only:
            base = src_contributors.get(cid_did, 1.0)
            prop = min(base * attenuation * 0.5, _MAX_PROPAGATED_WEIGHT)  # extra 0.5 for non-shared
            per_contributor.append({
                "contributor":        cid_did,
                "base_weight":        round(base, 4),
                "propagated_weight":  round(prop, 4),
                "reason":             "source-only contributor — potential signal for target",
            })

        if per_contributor:
            aggregate = round(
                sum(c["propagated_weight"] for c in per_contributor) / len(per_contributor), 4
            )
        else:
            aggregate = 0.0

        if shared:
            reason = f"shared contributor(s) + dignity gate passed"
        elif src_contributors:
            reason = f"source contributors available; no shared contributors yet"
        else:
            reason = "no contributors in source claim"

    return {
        "source_claim":            source_claim_id,
        "target_claim":            target_claim_id,
        "shared_contributors":     shared,
        "source_only_contributors": source_only,
        "propagated_trust_weight": aggregate,
        "attenuation_factor":      attenuation,
        "dignity_gate_passed":     dignity_ok,
        "reason":                  reason,
        "per_contributor":         per_contributor,
    }


def compute_all_pairs(
    fmap: dict[str, Any],
    *,
    attenuation: float = _DEFAULT_ATTENUATION,
) -> list[dict[str, Any]]:
    """
    Compute trust propagation for all connected (source, target) pairs
    in the federation map.
    """
    pairs: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for src_cid, info in fmap.items():
        for tgt_cid in info.get("depended_on_by", []) + info.get("enables", []):
            pair = (src_cid, tgt_cid)
            if pair not in seen:
                seen.add(pair)
                pairs.append(pair)

    return [
        compute_trust_propagation(src, tgt, attenuation=attenuation)
        for (src, tgt) in sorted(pairs)
    ]


# ── Display ───────────────────────────────────────────────────────────────────

def _print_propagation(result: dict[str, Any]) -> None:
    src = result["source_claim"]
    tgt = result["target_claim"]
    wt  = result["propagated_trust_weight"]
    ok  = "✓" if result["dignity_gate_passed"] else "✗"
    print(f"\nTrust Propagation: {src} → {tgt}")
    print(f"  dignity gate:              {ok}")
    print(f"  propagated_trust_weight:   {wt:.4f}")
    print(f"  attenuation_factor:        {result['attenuation_factor']}")
    print(f"  shared_contributors ({len(result['shared_contributors'])}):  "
          f"{result['shared_contributors'] or '(none)'}")
    print(f"  reason:                    {result['reason']}")
    pcs = result.get("per_contributor", [])
    if pcs:
        print(f"  per contributor ({len(pcs)}):")
        for pc in pcs:
            print(f"    {pc['contributor'][:50]:50s}  "
                  f"base={pc['base_weight']:.3f}  prop={pc['propagated_weight']:.3f}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="federation_trust_propagation",
        description=(
            "Compute cross-claim trust propagation within a federation. "
            "Read-only — does not write events."
        ),
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--source-claim", metavar="CLAIM_ID",
                   help="Source claim (upstream)")
    g.add_argument("--all-pairs", action="store_true",
                   help="Compute all connected (source, target) pairs")
    p.add_argument("--target-claim", metavar="CLAIM_ID",
                   help="Target claim (required with --source-claim)")
    p.add_argument("--attenuation", type=float, default=_DEFAULT_ATTENUATION,
                   help=f"Attenuation factor per hop (default: {_DEFAULT_ATTENUATION})")
    p.add_argument("--json",          action="store_true", dest="json_output")
    p.add_argument("--verbose", "-v", action="store_true")
    return p.parse_args()


def main() -> None:
    args = _parse_args()

    fed_events = load_federation_events()
    fmap       = build_federation_map(fed_events)

    if args.all_pairs:
        results = compute_all_pairs(fmap, attenuation=args.attenuation)
        if args.json_output:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            for r in results:
                _print_propagation(r)
        return

    if not args.target_claim:
        print("Error: --target-claim is required with --source-claim", file=sys.stderr)
        sys.exit(1)

    result = compute_trust_propagation(
        args.source_claim, args.target_claim, attenuation=args.attenuation
    )

    if args.json_output:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        _print_propagation(result)


if __name__ == "__main__":
    main()
