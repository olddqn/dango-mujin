"""
commons_registry.py — Phase 16: Cooperation Commons Layer

Dan-Go records advisory commons entries for communities, projects, houses,
and shared initiatives. No authority is claimed. No ownership is implied.

"Community is not authority."
"Commons is not ownership."
"Participation is not control."

Invariants:
  authority: none
  execution_allowed: false
  moves_money: false
  credit_issued: false
  hard_enforcement: false
  advisory: true
  commons_only: true
  append_only: true
  contestable: true
  reopenable: true
  ownership: false
  control: false
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import date

# ── paths ────────────────────────────────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT   = _SCRIPT_DIR.parents[4]
_EXAMPLES    = _SCRIPT_DIR.parent / "examples"

# ── commons types ────────────────────────────────────────────────────────────
COMMONS_TYPES = {
    "community": "A shared community of participants with common interests.",
    "project":   "A cooperative software or creative project.",
    "house":     "A physical or virtual cooperative living/working space.",
    "initiative":"A coordinated collective action or advocacy initiative.",
    "network":   "A loose network of cooperating individuals or groups.",
}

# ── invariants ────────────────────────────────────────────────────────────────
COMMONS_INVARIANTS: dict[str, object] = {
    "authority":          "none",
    "execution_allowed":  False,
    "moves_money":        False,
    "credit_issued":      False,
    "hard_enforcement":   False,
    "advisory":           True,
    "commons_only":       True,
    "append_only":        True,
    "contestable":        True,
    "reopenable":         True,
    "ownership":          False,
    "control":            False,
}

# ── default commons ───────────────────────────────────────────────────────────
DEFAULT_COMMONS: list[dict[str, object]] = [
    {
        "commons_id":    "dango-001",
        "name":          "Dan-Go",
        "description":   "The Dan-Go negotiation protocol — a cooperative, advisory, append-only system.",
        "commons_type":  "project",
        "active":        True,
        "founded":       "2025-01-01",
        "claim_ids":     ["housing-007", "housing-006"],
        "issue_ids":     [1, 2, 3],
    },
    {
        "commons_id":    "jammy-house-001",
        "name":          "Jammy House",
        "description":   "A cooperative housing initiative participating in Dan-Go negotiation.",
        "commons_type":  "house",
        "active":        True,
        "founded":       "2025-03-01",
        "claim_ids":     ["housing-007"],
        "issue_ids":     [3],
    },
    {
        "commons_id":    "yacypherpunks-001",
        "name":          "YacypherPunks",
        "description":   "A cypherpunk community engaged in cooperative digital infrastructure.",
        "commons_type":  "community",
        "active":        True,
        "founded":       "2024-06-01",
        "claim_ids":     [],
        "issue_ids":     [],
    },
    {
        "commons_id":    "dra-001",
        "name":          "D.R.A.",
        "description":   "Decentralised Renter Association — cooperative tenant advocacy initiative.",
        "commons_type":  "initiative",
        "active":        True,
        "founded":       "2025-01-15",
        "claim_ids":     ["housing-006", "housing-007"],
        "issue_ids":     [1, 2, 3],
    },
]


def build_commons_entry(
    commons_id:   str,
    name:         str,
    description:  str,
    commons_type: str,
    active:       bool               = True,
    founded:      str | None         = None,
    claim_ids:    list[str]          | None = None,
    issue_ids:    list[int]          | None = None,
) -> dict[str, object]:
    """Build one advisory commons registry entry."""
    if commons_type not in COMMONS_TYPES:
        commons_type = "community"

    entry: dict[str, object] = {
        "record_type":   "commons_registry_entry",
        "commons_id":    commons_id,
        "name":          name,
        "description":   description,
        "commons_type":  commons_type,
        "type_note":     COMMONS_TYPES[commons_type],
        "active":        active,
        "founded":       founded or str(date.today()),
        "claim_ids":     claim_ids or [],
        "issue_ids":     issue_ids or [],
        # invariants
        "authority":         "none",
        "ownership":         False,
        "control":           False,
        "execution_allowed": False,
        "moves_money":       False,
        "credit_issued":     False,
        "hard_enforcement":  False,
        "advisory":          True,
        "commons_only":      True,
        "append_only":       True,
        "contestable":       True,
        "reopenable":        True,
        # protocol phrases
        "protocol_phrases": [
            "Community is not authority.",
            "Commons is not ownership.",
            "Participation is not control.",
        ],
    }
    return entry


def build_registry(
    commons_list: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """Build the full commons registry."""
    if commons_list is None:
        commons_list = DEFAULT_COMMONS

    entries = [
        build_commons_entry(
            commons_id   = c["commons_id"],       # type: ignore[arg-type]
            name         = c["name"],              # type: ignore[arg-type]
            description  = c["description"],       # type: ignore[arg-type]
            commons_type = c["commons_type"],      # type: ignore[arg-type]
            active       = c.get("active", True),  # type: ignore[arg-type]
            founded      = c.get("founded"),       # type: ignore[arg-type]
            claim_ids    = c.get("claim_ids", []), # type: ignore[arg-type]
            issue_ids    = c.get("issue_ids", []), # type: ignore[arg-type]
        )
        for c in commons_list
    ]

    registry: dict[str, object] = {
        "record_type":   "commons_registry",
        "registry_id":   "commons-registry-001",
        "commons_count": len(entries),
        "commons":       entries,
        **COMMONS_INVARIANTS,
        "protocol_phrases": [
            "Community is not authority.",
            "Commons is not ownership.",
            "Participation is not control.",
            "Dan-Go records cooperation history; it does not govern communities.",
        ],
    }
    return registry


def print_registry(registry: dict[str, object]) -> None:
    print("=== commons_registry.py ===")
    print(f"  registry_id:   {registry['registry_id']}")
    print(f"  commons_count: {registry['commons_count']}")
    for entry in registry["commons"]:                          # type: ignore[union-attr]
        e = entry  # type: ignore[assignment]
        print(f"  [{e['commons_id']}] {e['name']} ({e['commons_type']})")
        print(f"    active={e['active']}, authority={e['authority']}, ownership={e['ownership']}, control={e['control']}")
    print(f"  authority={registry['authority']}, ownership={registry['ownership']}, control={registry['control']}")
    print(f"  moves_money={registry['moves_money']}, credit_issued={registry['credit_issued']}")
    print("  Community is not authority.")
    print("  Commons is not ownership.")


def save_registry(registry: dict[str, object]) -> Path:
    _EXAMPLES.mkdir(parents=True, exist_ok=True)
    out = _EXAMPLES / "commons-registry.json"
    out.write_text(json.dumps(registry, indent=2))
    print(f"  saved → {out.relative_to(_REPO_ROOT)}")
    return out


if __name__ == "__main__":
    reg = build_registry()
    print_registry(reg)
    if "--save" in sys.argv:
        save_registry(reg)
