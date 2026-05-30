#!/usr/bin/env python3
"""
globe_registry.py — Globe Data Model (Phase 22)
Dan-Go × GITSEA — Globe Foundation Layer

Create, list, and view Globe records.

A Globe is a free-participation voluntary community unit that can encompass
nation-states, municipalities, DAOs, local communities, and projects.
Membership is open. Participation is voluntary. Exit is free.

Usage:
    python3 globe/runtime/globe_registry.py list
    python3 globe/runtime/globe_registry.py view <globe_id>
    python3 globe/runtime/globe_registry.py create  (interactive, or via JSON stdin)
    python3 globe/runtime/globe_registry.py --help
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
_GLOBES_FILE = _DATA_DIR / "globes.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_globes() -> list:
    if _GLOBES_FILE.exists():
        return json.loads(_GLOBES_FILE.read_text())
    return []


def save_globes(globes: list) -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    _GLOBES_FILE.write_text(json.dumps(globes, indent=2, ensure_ascii=False))


def find_globe(globes: list, globe_id: str) -> dict | None:
    for g in globes:
        if g["globe_id"] == globe_id:
            return g
    return None


def cmd_list(args):
    globes = load_globes()
    if not globes:
        print("(no Globes registered yet)")
        return
    print(f"{'Globe ID':<20} {'Name':<30} {'Governance':<25} {'Policy':<10} Created")
    print("-" * 100)
    for g in globes:
        print(
            f"{g['globe_id']:<20} "
            f"{g['name'][:29]:<30} "
            f"{g.get('governance_model','?')[:24]:<25} "
            f"{g.get('membership_policy','?'):<10} "
            f"{g.get('created_at','?')[:10]}"
        )


def cmd_view(args):
    if len(args) < 1:
        print("Usage: globe_registry.py view <globe_id>")
        sys.exit(1)
    globe_id = args[0]
    globes = load_globes()
    g = find_globe(globes, globe_id)
    if not g:
        print(f"Globe not found: {globe_id}")
        sys.exit(1)
    print(json.dumps(g, indent=2, ensure_ascii=False))


def cmd_create(args):
    """Create a new Globe from stdin JSON or interactive prompts."""
    if not sys.stdin.isatty():
        # Pipe mode: read JSON from stdin
        data = json.load(sys.stdin)
    else:
        # Interactive mode
        data = {}
        print("=== Create New Globe ===")
        data["globe_id"] = input("globe_id (e.g. globe-004): ").strip()
        data["name"] = input("name: ").strip()
        data["description"] = input("description: ").strip()
        data["founding_statement"] = input("founding_statement: ").strip()
        data["membership_policy"] = input("membership_policy [open/invite/closed]: ").strip() or "open"
        data["governance_model"] = input("governance_model [deliberative_consensus/voting/council]: ").strip() or "deliberative_consensus"

    globes = load_globes()
    if find_globe(globes, data.get("globe_id", "")):
        print(f"Globe already exists: {data['globe_id']}")
        sys.exit(1)

    now = _now()
    entry = {
        "globe_id":           data.get("globe_id"),
        "name":               data.get("name", ""),
        "description":        data.get("description", ""),
        "founding_statement": data.get("founding_statement", ""),
        "membership_policy":  data.get("membership_policy", "open"),
        "governance_model":   data.get("governance_model", "deliberative_consensus"),
        "gitsea_link": data.get("gitsea_link", {
            "gitsea_repo_url":   None,
            "gitsea_issue_url":  None,
            "gitsea_pr_url":     None,
            "commit_hash":       None,
            "linked_rule_path":  None,
        }),
        "created_at": now,
        "updated_at": now,
    }
    globes.append(entry)
    save_globes(globes)
    print(f"Globe created: {entry['globe_id']}")
    print(json.dumps(entry, indent=2, ensure_ascii=False))


def cmd_help(args):
    print(__doc__)


COMMANDS = {
    "list":   cmd_list,
    "view":   cmd_view,
    "create": cmd_create,
    "--help": cmd_help,
    "-h":     cmd_help,
}


def main():
    args = sys.argv[1:]
    if not args:
        cmd_list([])
        return
    cmd = args[0]
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        cmd_help([])
        sys.exit(1)
    COMMANDS[cmd](args[1:])


if __name__ == "__main__":
    main()
