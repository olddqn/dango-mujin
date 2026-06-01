"""
phrase_genealogy.py — Protocol Phrase Genealogy View (Phase 46)

Reads protocol_phrase_ledger.json and produces a genealogy view showing:
- which phase each phrase first appeared in
- which phases it was carried forward to
- its continuity classification (foundational / repeated / recent / single_phase)
- an advisory continuity_note

INVARIANTS (permanent, all sessions):
    Phrase genealogy is advisory display only.
    Phrase genealogy creates no legal authority.
    Phrase genealogy is not enforcement.
    Phrase genealogy does not override human judgment.
    Human review is required before any real-world action.
    authority: none
    execution_allowed: false
    moves_money: false
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────

_RUNTIME_DIR = Path(__file__).parent
_GLOBE_DIR   = _RUNTIME_DIR.parent
_REPORTS_DIR = _GLOBE_DIR / "reports"
_LEDGER_JSON = _REPORTS_DIR / "protocol_phrase_ledger.json"

# ─── Invariants ───────────────────────────────────────────────────────────────

GENEALOGY_INVARIANTS: dict[str, object] = {
    "phrase_genealogy_is_advisory_display_only":       True,
    "phrase_genealogy_creates_no_legal_authority":     True,
    "phrase_genealogy_is_not_enforcement":             True,
    "phrase_genealogy_does_not_override_human_judgment": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority":          "none",
    "execution_allowed":  False,
    "moves_money":        False,
    "hard_enforcement":   False,
    "credit_issued":      False,
}

GENEALOGY_PHRASES: list[str] = [
    "Phrase genealogy is advisory display only.",
    "Phrase genealogy creates no legal authority.",
    "Phrase genealogy is not enforcement.",
    "Phrase genealogy does not override human judgment.",
    "Human review is required before any real-world action.",
]

# ─── Continuity classes ───────────────────────────────────────────────────────

CONTINUITY_CLASSES: list[str] = [
    "foundational",   # phase_count >= 10
    "repeated",       # 3 <= phase_count < 10
    "recent",         # phase_count < 3 and first_phase_num >= 40
    "single_phase",   # phase_count == 1 (and not recent)
]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _phase_num(phase_str: str) -> int:
    """Return numeric part of phase string (e.g. '27b' → 27, '45' → 45)."""
    if not phase_str:
        return 0
    m = re.match(r"(\d+)", str(phase_str).strip())
    return int(m.group(1)) if m else 0


def _phase_sort_key(p: str) -> tuple:
    m = re.fullmatch(r"(\d+)([a-z]*)", str(p).lower().strip())
    if m:
        return (int(m.group(1)), m.group(2))
    return (9999, p)


def _classify(phase_count: int, first_phase_num: int) -> str:
    if phase_count >= 10:
        return "foundational"
    if phase_count >= 3:
        return "repeated"
    if first_phase_num >= 40:
        return "recent"
    return "single_phase"


def _continuity_note(
    phrase_text: str,
    phrase_type: str,
    continuity_class: str,
    phase_count: int,
    first_phase: str,
    phases_seen: list[str],
) -> str:
    first_num = _phase_num(first_phase)
    last = phases_seen[-1] if phases_seen else first_phase
    if continuity_class == "foundational":
        return (
            f"Foundational principle — present across {phase_count} phases "
            f"(Phase {first_phase}–{last}). "
            f"Establishes a persistent {phrase_type.replace('_', ' ')} constraint."
        )
    if continuity_class == "repeated":
        phase_list = ", ".join(f"Phase {p}" for p in phases_seen[:6])
        if len(phases_seen) > 6:
            phase_list += f", +{len(phases_seen)-6} more"
        return (
            f"Recurring principle across {phase_count} phases "
            f"({phase_list}). "
            f"Signals a {phrase_type.replace('_', ' ')} commitment carried forward."
        )
    if continuity_class == "recent":
        return (
            f"Recent addition — introduced in Phase {first_phase}. "
            f"Reflects latest {phrase_type.replace('_', ' ')} framing as of Phase {last}."
        )
    # single_phase
    return (
        f"Introduced in Phase {first_phase}. "
        f"Advisory {phrase_type.replace('_', ' ')} statement scoped to this phase."
    )


# ─── Build ────────────────────────────────────────────────────────────────────

def _load_ledger() -> dict:
    if not _LEDGER_JSON.exists():
        # build on-the-fly via importlib
        try:
            import importlib.util as _ilu
            _spec = _ilu.spec_from_file_location(
                "protocol_phrase_ledger",
                _RUNTIME_DIR / "protocol_phrase_ledger.py",
            )
            _mod = _ilu.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            return _mod.build_ledger()
        except Exception as exc:
            raise RuntimeError(f"protocol_phrase_ledger.json not found and build failed: {exc}")
    return json.loads(_LEDGER_JSON.read_text(encoding="utf-8"))


def build_genealogy() -> dict:
    """Build phrase genealogy from protocol_phrase_ledger.json."""
    ledger = _load_ledger()
    entries = ledger.get("entries", [])

    nodes: list[dict] = []

    # counters for by-class summary
    by_class:      dict[str, int] = {c: 0 for c in CONTINUITY_CLASSES}
    by_type:       dict[str, int] = {}
    by_first_phase: dict[str, int] = {}

    for entry in entries:
        phrase_id   = entry.get("phrase_id", "")
        phrase_text = entry.get("phrase_text", "")
        phrase_type = entry.get("phrase_type", "other")
        norm        = entry.get("normalized_phrase", "")
        first_phase = entry.get("phase", "") or entry.get("first_seen_phase", "")
        all_phases  = sorted(entry.get("all_phases", []) or [first_phase],
                             key=_phase_sort_key)
        src_file    = entry.get("source_file", "")
        src_hint    = entry.get("source_line_hint", "")

        phase_count    = len(all_phases)
        first_phase_num = _phase_num(first_phase)
        continuity_class = _classify(phase_count, first_phase_num)

        note = _continuity_note(
            phrase_text, phrase_type, continuity_class,
            phase_count, first_phase, all_phases,
        )

        genealogy_id = f"gen-{phrase_id}"

        node: dict = {
            "genealogy_id":          genealogy_id,
            "phrase_id":             phrase_id,
            "normalized_phrase":     norm,
            "phrase_text":           phrase_text,
            "phrase_type":           phrase_type,
            "first_phase":           first_phase,
            "phases_seen":           all_phases,
            "phase_count":           phase_count,
            "source_files":          [src_file] if src_file else [],
            "source_line_hints":     [src_hint] if src_hint else [],
            "continuity_class":      continuity_class,
            "continuity_note":       note,
            "advisory_only":         True,
            "creates_no_legal_authority": True,
            "not_enforcement":       True,
        }
        nodes.append(node)

        by_class[continuity_class] = by_class.get(continuity_class, 0) + 1
        by_type[phrase_type]       = by_type.get(phrase_type, 0) + 1
        by_first_phase[first_phase] = by_first_phase.get(first_phase, 0) + 1

    # sort by (first_phase_num, phrase_id)
    nodes.sort(key=lambda n: (_phase_sort_key(n["first_phase"]), n["phrase_id"]))

    return {
        "genealogy_id":        "phrase-genealogy-phase-46",
        "generated_at":        datetime.now(timezone.utc).isoformat(),
        "phase":               "46",
        "total_nodes":         len(nodes),
        "by_continuity_class": by_class,
        "by_phrase_type":      dict(sorted(by_type.items(), key=lambda x: -x[1])),
        "by_first_phase":      {
            k: v for k, v in sorted(by_first_phase.items(), key=lambda x: _phase_sort_key(x[0]))
        },
        **GENEALOGY_INVARIANTS,
        "advisory_phrases":    GENEALOGY_PHRASES,
        "nodes":               nodes,
    }


# ─── Filter ───────────────────────────────────────────────────────────────────

def filter_nodes(
    data:         dict,
    phase_filter: str | None = None,
    type_filter:  str | None = None,
    query:        str | None = None,
) -> list[dict]:
    nodes = data.get("nodes", [])
    if phase_filter:
        nodes = [n for n in nodes if phase_filter in n.get("phases_seen", [])]
    if type_filter:
        nodes = [n for n in nodes if n.get("phrase_type") == type_filter]
    if query:
        q = query.lower()
        nodes = [
            n for n in nodes
            if q in n.get("normalized_phrase", "")
            or q in n.get("phrase_type", "")
            or q in " ".join(n.get("phases_seen", []))
            or q in n.get("continuity_class", "")
        ]
    return nodes


# ─── Markdown ─────────────────────────────────────────────────────────────────

def _to_markdown(data: dict) -> str:
    lines: list[str] = []
    lines.append("# Phrase Genealogy (Phase 46)\n")
    lines.append(f"Generated: {data.get('generated_at', '')}\n")
    lines.append(f"Total nodes: {data.get('total_nodes', 0)}\n")
    lines.append("")

    lines.append("## By Continuity Class\n")
    for cls, cnt in data.get("by_continuity_class", {}).items():
        lines.append(f"- `{cls}`: {cnt}")
    lines.append("")

    lines.append("## By Phrase Type\n")
    for pt, cnt in data.get("by_phrase_type", {}).items():
        lines.append(f"- `{pt}`: {cnt}")
    lines.append("")

    # group by continuity_class
    by_cls: dict[str, list[dict]] = {}
    for n in data.get("nodes", []):
        cls = n.get("continuity_class", "single_phase")
        by_cls.setdefault(cls, []).append(n)

    for cls in CONTINUITY_CLASSES:
        nodes_in_cls = by_cls.get(cls, [])
        if not nodes_in_cls:
            continue
        lines.append(f"\n## {cls.replace('_', ' ').title()} ({len(nodes_in_cls)})\n")
        for n in nodes_in_cls:
            lines.append(f"### {n['genealogy_id']} — Phase {n['first_phase']}")
            lines.append(f"**Phrase:** \"{n['phrase_text']}\"")
            lines.append(f"**Type:** `{n['phrase_type']}`")
            lines.append(f"**Phase count:** {n['phase_count']}")
            lines.append(f"**Phases seen:** {', '.join(n['phases_seen'])}")
            lines.append(f"**Note:** {n['continuity_note']}")
            lines.append("")

    lines.append("---\n")
    for p in GENEALOGY_PHRASES:
        lines.append(f"*{p}*")
    lines.append("")
    return "\n".join(lines)


# ─── Save / Load ──────────────────────────────────────────────────────────────

_GENEALOGY_JSON = _REPORTS_DIR / "phrase_genealogy.json"
_GENEALOGY_MD   = _REPORTS_DIR / "phrase_genealogy.md"


def save_genealogy() -> dict:
    data = build_genealogy()
    _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    _GENEALOGY_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _GENEALOGY_MD.write_text(_to_markdown(data), encoding="utf-8")
    return data


def load_genealogy() -> dict:
    if _GENEALOGY_JSON.exists():
        return json.loads(_GENEALOGY_JSON.read_text(encoding="utf-8"))
    return build_genealogy()


# ─── CLI helpers ──────────────────────────────────────────────────────────────

def _bar(n: int, total: int, width: int = 30) -> str:
    filled = int(width * n / max(total, 1))
    return "█" * filled


def _print_nodes(nodes: list[dict], label: str) -> None:
    width = 60
    print(f"Protocol Phrase Genealogy — {label}")
    print("=" * width)
    print(f"  {len(nodes)} node(s)\n")
    for n in nodes:
        cls   = n.get("continuity_class", "")
        pt    = n.get("phrase_type", "")
        gid   = n.get("genealogy_id", "")
        fp    = n.get("first_phase", "")
        pc    = n.get("phase_count", 0)
        text  = n.get("phrase_text", "")
        note  = n.get("continuity_note", "")
        phases = n.get("phases_seen", [])
        shown_phases = phases[:8]
        phase_str = ", ".join(f"Phase {p}" for p in shown_phases)
        if len(phases) > 8:
            phase_str += f", +{len(phases)-8} more"
        print(f"  [{cls}] {gid}  Phase {fp}  ×{pc}")
        print(f"    [{pt}] \"{text}\"")
        print(f"    phases: {phase_str}")
        print(f"    note:   {note[:100]}")
        print()
    for p in GENEALOGY_PHRASES:
        print(f"  \"{p}\"")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main() -> None:  # noqa: C901
    args = sys.argv[1:]
    if not args:
        args = ["summary"]
    cmd = args[0]

    if cmd == "summary":
        data = build_genealogy()
        total = data.get("total_nodes", 0)
        width = 60
        print(f"Protocol Phrase Genealogy (Phase 46)")
        print("=" * width)
        print(f"  generated_at:    {data.get('generated_at', '')}")
        print(f"  total_nodes:     {total}")
        print()
        print("  By continuity_class:")
        for cls, cnt in data.get("by_continuity_class", {}).items():
            bar = _bar(cnt, total)
            print(f"    {cls:<30} {cnt:>4}  {bar}")
        print()
        print("  By phrase_type:")
        by_type = data.get("by_phrase_type", {})
        for pt, cnt in by_type.items():
            bar = _bar(cnt, total)
            print(f"    {pt:<35} {cnt:>4}  {bar}")
        print()
        print("  By first_seen phase:")
        for phase, cnt in data.get("by_first_phase", {}).items():
            print(f"    Phase {phase:<8} {cnt} node(s)")
        print()
        for p in GENEALOGY_PHRASES:
            print(f"  \"{p}\"")

    elif cmd == "save":
        print("Saving Protocol Phrase Genealogy (Phase 46)...")
        data = save_genealogy()
        print(f"  Saved: {_GENEALOGY_JSON.relative_to(Path.cwd())}")
        print(f"  Saved: {_GENEALOGY_MD.relative_to(Path.cwd())}")
        print(f"  total_nodes: {data.get('total_nodes', 0)}")
        print()
        for p in GENEALOGY_PHRASES:
            print(f"  \"{p}\"")

    elif cmd == "show-phrase":
        if len(args) < 2:
            print("Usage: phrase_genealogy.py show-phrase <phrase_id_or_partial>")
            sys.exit(1)
        arg = args[1].lower()
        data = load_genealogy()
        nodes = [
            n for n in data.get("nodes", [])
            if arg in n.get("genealogy_id", "").lower()
            or arg in n.get("phrase_id", "").lower()
            or arg in n.get("normalized_phrase", "")
        ]
        _print_nodes(nodes, f"phrase={args[1]}")

    elif cmd == "show-type":
        if len(args) < 2:
            print("Usage: phrase_genealogy.py show-type <phrase_type>")
            sys.exit(1)
        data = load_genealogy()
        nodes = filter_nodes(data, type_filter=args[1])
        _print_nodes(nodes, f"type={args[1]}")

    elif cmd == "show-phase":
        if len(args) < 2:
            print("Usage: phrase_genealogy.py show-phase <phase>")
            sys.exit(1)
        data = load_genealogy()
        nodes = filter_nodes(data, phase_filter=args[1])
        _print_nodes(nodes, f"phase={args[1]}")

    elif cmd == "search":
        if len(args) < 2:
            print("Usage: phrase_genealogy.py search <query>")
            sys.exit(1)
        data = load_genealogy()
        nodes = filter_nodes(data, query=args[1])
        _print_nodes(nodes, f"search='{args[1]}'")

    else:
        print("Usage: phrase_genealogy.py <summary|save|show-phrase|show-type|show-phase|search> [arg]")
        sys.exit(1)


if __name__ == "__main__":
    main()
