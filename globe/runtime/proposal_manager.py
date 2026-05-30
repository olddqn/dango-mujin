#!/usr/bin/env python3
"""
proposal_manager.py — Proposal Data Model (Phase 22)
Dan-Go × GITSEA — Globe Foundation Layer

Create, list, view, and advance Proposals within a Globe.

A Proposal moves through the following lifecycle:
    draft → discussion → voting → accepted | rejected | archived

Minority opinions and objections are always preserved.
No proposal is deleted from history. Append-only.

Usage:
    python3 globe/runtime/proposal_manager.py list [globe_id]
    python3 globe/runtime/proposal_manager.py view <proposal_id>
    python3 globe/runtime/proposal_manager.py advance <proposal_id> <new_status>
    python3 globe/runtime/proposal_manager.py create
    python3 globe/runtime/proposal_manager.py --help
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
_PROPOSALS_FILE = _DATA_DIR / "proposals.json"

VALID_STATUSES = ["draft", "discussion", "voting", "accepted", "rejected", "archived"]

STATUS_TRANSITIONS = {
    "draft":      ["discussion", "archived"],
    "discussion": ["voting", "archived"],
    "voting":     ["accepted", "rejected", "archived"],
    "accepted":   ["archived"],
    "rejected":   ["archived"],
    "archived":   [],
}

STATUS_LABELS = {
    "draft":      "📝 draft",
    "discussion": "💬 discussion",
    "voting":     "🗳  voting",
    "accepted":   "✅ accepted",
    "rejected":   "❌ rejected",
    "archived":   "📦 archived",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_proposals() -> list:
    if _PROPOSALS_FILE.exists():
        return json.loads(_PROPOSALS_FILE.read_text())
    return []


def save_proposals(proposals: list) -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    _PROPOSALS_FILE.write_text(json.dumps(proposals, indent=2, ensure_ascii=False))


def find_proposal(proposals: list, proposal_id: str) -> dict | None:
    for p in proposals:
        if p["proposal_id"] == proposal_id:
            return p
    return None


def cmd_list(args):
    proposals = load_proposals()
    globe_filter = args[0] if args else None
    if globe_filter:
        proposals = [p for p in proposals if p.get("globe_id") == globe_filter]
    if not proposals:
        print("(no proposals found)")
        return
    print(f"{'Proposal ID':<20} {'Globe':<15} {'Status':<15} {'Title'}")
    print("-" * 90)
    for p in proposals:
        status_label = STATUS_LABELS.get(p.get("status", "?"), p.get("status", "?"))
        print(
            f"{p['proposal_id']:<20} "
            f"{p.get('globe_id','?')[:14]:<15} "
            f"{status_label:<15} "
            f"{p.get('title','?')[:50]}"
        )


def cmd_view(args):
    if not args:
        print("Usage: proposal_manager.py view <proposal_id>")
        sys.exit(1)
    proposal_id = args[0]
    proposals = load_proposals()
    p = find_proposal(proposals, proposal_id)
    if not p:
        print(f"Proposal not found: {proposal_id}")
        sys.exit(1)
    print(json.dumps(p, indent=2, ensure_ascii=False))


def cmd_advance(args):
    """Advance a proposal to the next status."""
    if len(args) < 2:
        print("Usage: proposal_manager.py advance <proposal_id> <new_status>")
        print(f"Valid statuses: {', '.join(VALID_STATUSES)}")
        sys.exit(1)
    proposal_id, new_status = args[0], args[1]
    if new_status not in VALID_STATUSES:
        print(f"Invalid status: {new_status}. Valid: {', '.join(VALID_STATUSES)}")
        sys.exit(1)
    proposals = load_proposals()
    p = find_proposal(proposals, proposal_id)
    if not p:
        print(f"Proposal not found: {proposal_id}")
        sys.exit(1)
    current = p.get("status", "draft")
    allowed = STATUS_TRANSITIONS.get(current, [])
    if new_status not in allowed:
        print(f"Cannot transition {proposal_id} from '{current}' to '{new_status}'.")
        print(f"Allowed transitions from '{current}': {allowed or '(terminal state)'}")
        sys.exit(1)
    p["status"] = new_status
    p["updated_at"] = _now()
    save_proposals(proposals)
    print(f"Proposal {proposal_id}: {current} → {new_status}")


def cmd_create(args):
    """Create a new Proposal from stdin JSON or interactively."""
    if not sys.stdin.isatty():
        data = json.load(sys.stdin)
    else:
        data = {}
        print("=== Create New Proposal ===")
        data["proposal_id"] = input("proposal_id (e.g. proposal-005): ").strip()
        data["globe_id"] = input("globe_id: ").strip()
        data["title"] = input("title: ").strip()
        print("body (end with a line containing only '---'):")
        lines = []
        while True:
            line = input()
            if line.strip() == "---":
                break
            lines.append(line)
        data["body"] = "\n".join(lines)
        data["proposer"] = input("proposer (pseudonym or ID): ").strip()
        data["status"] = "draft"

    proposals = load_proposals()
    if find_proposal(proposals, data.get("proposal_id", "")):
        print(f"Proposal already exists: {data['proposal_id']}")
        sys.exit(1)

    now = _now()
    entry = {
        "proposal_id": data.get("proposal_id"),
        "globe_id":    data.get("globe_id"),
        "title":       data.get("title", ""),
        "body":        data.get("body", ""),
        "proposer":    data.get("proposer", "anonymous"),
        "status":      data.get("status", "draft"),
        "gitsea_link": data.get("gitsea_link", {
            "gitsea_repo_url":  None,
            "gitsea_issue_url": None,
            "gitsea_pr_url":    None,
            "commit_hash":      None,
            "linked_rule_path": None,
        }),
        "created_at": now,
        "updated_at": now,
    }
    proposals.append(entry)
    save_proposals(proposals)
    print(f"Proposal created: {entry['proposal_id']}")
    print(json.dumps(entry, indent=2, ensure_ascii=False))


def cmd_help(args):
    print(__doc__)


COMMANDS = {
    "list":    cmd_list,
    "view":    cmd_view,
    "advance": cmd_advance,
    "create":  cmd_create,
    "--help":  cmd_help,
    "-h":      cmd_help,
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
