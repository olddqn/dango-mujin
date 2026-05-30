#!/usr/bin/env python3
"""
deliberation_log.py — Deliberation Data Model (Phase 22)
Dan-Go × GITSEA — Globe Foundation Layer

Append and view deliberation entries for a proposal.

Deliberation is the core of Dan-Go governance:
- Human speakers contribute their views
- AI mediators organize arguments and surface conflicts
- System records capture protocol events
- All entries are append-only — no entry is ever deleted
- Minority opinions and objections are preserved equally

Speaker types:
    human  — a human participant
    ai     — an AI mediator or assistant
    system — a protocol-level event (status change, record note, etc.)

Usage:
    python3 globe/runtime/deliberation_log.py list <proposal_id>
    python3 globe/runtime/deliberation_log.py append <proposal_id>
    python3 globe/runtime/deliberation_log.py view <deliberation_id>
    python3 globe/runtime/deliberation_log.py summary <proposal_id>
    python3 globe/runtime/deliberation_log.py --help
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
_DELIBERATIONS_FILE = _DATA_DIR / "deliberations.json"

SPEAKER_TYPE_LABELS = {
    "human":  "👤",
    "ai":     "🤖",
    "system": "⚙️ ",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _next_id(deliberations: list) -> str:
    existing = [d["deliberation_id"] for d in deliberations if d["deliberation_id"].startswith("delib-")]
    nums = []
    for eid in existing:
        try:
            nums.append(int(eid.split("-")[1]))
        except (IndexError, ValueError):
            pass
    next_num = max(nums, default=0) + 1
    return f"delib-{next_num:03d}"


def load_deliberations() -> list:
    if _DELIBERATIONS_FILE.exists():
        return json.loads(_DELIBERATIONS_FILE.read_text())
    return []


def save_deliberations(deliberations: list) -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    _DELIBERATIONS_FILE.write_text(json.dumps(deliberations, indent=2, ensure_ascii=False))


def cmd_list(args):
    if not args:
        print("Usage: deliberation_log.py list <proposal_id>")
        sys.exit(1)
    proposal_id = args[0]
    deliberations = load_deliberations()
    entries = [d for d in deliberations if d.get("proposal_id") == proposal_id]
    if not entries:
        print(f"No deliberation entries for proposal: {proposal_id}")
        return
    print(f"Deliberation log for: {proposal_id}")
    print(f"{'ID':<15} {'Speaker':<25} {'Type':<8} Timestamp")
    print("-" * 80)
    for e in entries:
        icon = SPEAKER_TYPE_LABELS.get(e.get("speaker_type", ""), "  ")
        print(
            f"{e['deliberation_id']:<15} "
            f"{e.get('speaker_name','?')[:24]:<25} "
            f"{icon} {e.get('speaker_type','?'):<6} "
            f"{e.get('created_at','?')[:19]}"
        )


def cmd_append(args):
    """Append a new deliberation entry for a proposal."""
    if not args:
        print("Usage: deliberation_log.py append <proposal_id>")
        sys.exit(1)
    proposal_id = args[0]
    deliberations = load_deliberations()

    if not sys.stdin.isatty():
        data = json.load(sys.stdin)
    else:
        data = {}
        print(f"=== Append Deliberation for {proposal_id} ===")
        data["speaker_type"] = input("speaker_type [human/ai/system]: ").strip() or "human"
        data["speaker_name"] = input("speaker_name: ").strip()
        print("content (end with a line containing only '---'):")
        lines = []
        while True:
            line = input()
            if line.strip() == "---":
                break
            lines.append(line)
        data["content"] = "\n".join(lines)

    entry = {
        "deliberation_id": _next_id(deliberations),
        "proposal_id":     proposal_id,
        "speaker_type":    data.get("speaker_type", "human"),
        "speaker_name":    data.get("speaker_name", "anonymous"),
        "content":         data.get("content", ""),
        "created_at":      _now(),
    }
    deliberations.append(entry)
    save_deliberations(deliberations)
    print(f"Deliberation entry recorded: {entry['deliberation_id']}")
    print(json.dumps(entry, indent=2, ensure_ascii=False))


def cmd_view(args):
    if not args:
        print("Usage: deliberation_log.py view <deliberation_id>")
        sys.exit(1)
    did = args[0]
    deliberations = load_deliberations()
    for d in deliberations:
        if d["deliberation_id"] == did:
            print(json.dumps(d, indent=2, ensure_ascii=False))
            return
    print(f"Deliberation entry not found: {did}")
    sys.exit(1)


def cmd_summary(args):
    """Print a human-readable deliberation summary for a proposal."""
    if not args:
        print("Usage: deliberation_log.py summary <proposal_id>")
        sys.exit(1)
    proposal_id = args[0]
    deliberations = load_deliberations()
    entries = [d for d in deliberations if d.get("proposal_id") == proposal_id]
    if not entries:
        print(f"No deliberation entries for proposal: {proposal_id}")
        return
    human_count = sum(1 for e in entries if e.get("speaker_type") == "human")
    ai_count = sum(1 for e in entries if e.get("speaker_type") == "ai")
    system_count = sum(1 for e in entries if e.get("speaker_type") == "system")
    print("=" * 70)
    print(f"Deliberation Summary: {proposal_id}")
    print(f"Total entries: {len(entries)} ({human_count} human, {ai_count} AI, {system_count} system)")
    print("=" * 70)
    for e in entries:
        icon = SPEAKER_TYPE_LABELS.get(e.get("speaker_type", ""), "  ")
        speaker = e.get("speaker_name", "?")
        ts = e.get("created_at", "?")[:19]
        print(f"\n[{e['deliberation_id']}] {icon} {speaker} ({ts})")
        print("-" * 60)
        content = e.get("content", "")
        for line in content.split("\n"):
            print(f"  {line}")
    print("\n" + "=" * 70)
    print("Note: All entries are append-only. Minority opinions preserved.")


def cmd_help(args):
    print(__doc__)


COMMANDS = {
    "list":    cmd_list,
    "append":  cmd_append,
    "view":    cmd_view,
    "summary": cmd_summary,
    "--help":  cmd_help,
    "-h":      cmd_help,
}


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: deliberation_log.py <command> [args]")
        cmd_help([])
        return
    cmd = args[0]
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        cmd_help([])
        sys.exit(1)
    COMMANDS[cmd](args[1:])


if __name__ == "__main__":
    main()
