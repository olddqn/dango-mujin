"""
scoped_world_model.py

Integrates scope-aware prerequisites into the world model prior_knowledge.

When a prerequisite is weakened (scoped), the world model hint for a claim
must reflect whether the prerequisite applies in that claim's context.

This module produces the prior_knowledge["federation_prerequisites"] block
with scope fields attached, so plan tree generators can make
context-sensitive decisions.

Structure of each hint in prior_knowledge:
{
  "condition":    str,
  "hint_type":    "federation_prerequisite",
  "authority":    "none",
  "advisory":     True,
  "applicable":   bool,     # True if applies in this claim's context
  "scoped":       bool,     # True if this prerequisite is weakened
  "scope":        str,      # e.g. "non_precertified_spaces"
  "bypass_path":  list[str] | None,  # which bypass conditions are available
  "note":         str,
}

No hard enforcement. No hidden logic. advisory=True always.
stdlib only. Read-only.
"""

import json
import os
import sys

_BRIDGE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _BRIDGE)


def _sutable_path(table: str) -> str:
    base = os.path.dirname(_BRIDGE)
    p = os.path.join(base, "sutable", f"{table}.jsonl")
    if os.path.exists(p):
        return p
    p2 = os.path.normpath(os.path.join(_BRIDGE, "..", "sutable", f"{table}.jsonl"))
    return p2 if os.path.exists(p2) else p


def _read_jsonl(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return events


def _load_fmap(fmap=None) -> dict:
    if fmap is not None:
        return fmap
    return {
        "plans":      _read_jsonl(_sutable_path("plans")),
        "memory":     _read_jsonl(_sutable_path("memory")),
        "federation": _read_jsonl(_sutable_path("federation")),
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_scoped_prior_knowledge(claim_id: str, fmap=None) -> dict:
    """
    Build a world model prior_knowledge block for a specific claim,
    with scope-aware prerequisite hints.

    Returns:
    {
      "claim_id": str,
      "federation_prerequisites": [
        {
          "condition":   str,
          "hint_type":   "federation_prerequisite",
          "authority":   "none",
          "advisory":    True,
          "applicable":  bool,
          "scoped":      bool,
          "scope":       str,
          "bypass_path": list[str] | None,
          "note":        str,
        },
        ...
      ]
    }
    """
    from scoped_condition_propagation import get_scoped_propagation_hints

    fm = _load_fmap(fmap)
    hints = get_scoped_propagation_hints(claim_id, fmap=fm)

    # Reshape hints into the prior_knowledge format
    prereq_hints = []
    for h in hints:
        prereq_hints.append({
            "condition":   h["condition"],
            "hint_type":   h["hint_type"],
            "authority":   h["authority"],
            "advisory":    h["advisory"],
            "applicable":  h["applicable"],
            "scoped":      h["scoped"],
            "scope":       h.get("scope", "all_spaces"),
            "bypass_path": h.get("bypass_reason"),
            "note":        h["note"],
        })

    return {
        "claim_id":                claim_id,
        "federation_prerequisites": prereq_hints,
    }


def integrate_scoped_prerequisites(
    prior_knowledge: dict,
    claim_id: str,
    fmap=None,
) -> dict:
    """
    Merge scoped prerequisite hints into an existing prior_knowledge dict.

    Existing "federation_prerequisites" key is replaced with the
    scope-aware version. All other keys are preserved.

    Returns the updated prior_knowledge dict (copy, not mutated).
    """
    scoped = build_scoped_prior_knowledge(claim_id, fmap=fmap)
    updated = dict(prior_knowledge)
    updated["federation_prerequisites"] = scoped["federation_prerequisites"]
    return updated


def build_all_scoped_prior_knowledge(fmap=None) -> list[dict]:
    """
    Build scoped prior_knowledge for all claims with active plans.
    Returns list ordered by claim_id.
    """
    from prerequisite_scope_resolver import _active_plan_conditions

    fm = _load_fmap(fmap)
    all_plans = _active_plan_conditions(fm["plans"])
    return [
        build_scoped_prior_knowledge(cid, fmap=fm)
        for cid in sorted(all_plans.keys())
    ]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli():
    import argparse
    ap = argparse.ArgumentParser(
        description="Build scoped prerequisite prior_knowledge for claims"
    )
    ap.add_argument("--claim-id", help="specific claim")
    ap.add_argument("--all",      action="store_true", help="all claims")
    ap.add_argument("--json",     action="store_true")
    args = ap.parse_args()

    if args.claim_id:
        result = build_scoped_prior_knowledge(args.claim_id)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            _print_prior(result)
    else:
        results = build_all_scoped_prior_knowledge()
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            if not results:
                print("No claims with active plans.")
            for r in results:
                _print_prior(r)
                print()


def _print_prior(r: dict):
    cid = r["claim_id"]
    prereqs = r["federation_prerequisites"]
    print(f"  {cid}:")
    if not prereqs:
        print("    federation_prerequisites: (none)")
        return
    for p in prereqs:
        mark   = "✓" if p["applicable"] else "⊛"
        scoped = f"  [scope: {p['scope']}]" if p["scoped"] else "  [universal]"
        applic = "applicable" if p["applicable"] else "bypassed"
        print(f"    {mark} {p['condition']}  {applic}{scoped}")
        if p.get("bypass_path"):
            print(f"        bypass_path: {p['bypass_path']}")


if __name__ == "__main__":
    _cli()
