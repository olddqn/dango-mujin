#!/usr/bin/env python3
"""
protocol_phrase_ledger.py — Protocol Phrase Ledger (Phase 45)
Dan-Go × GITSEA — Globe Foundation Layer

Collects and indexes all protocol phrases from Phase 10–44 into an
append-only advisory ledger. Deduplicates by normalized phrase text,
recording the first phase each phrase appeared and all subsequent phases.

INVARIANTS:
- Protocol phrase ledger is advisory display only.
- Protocol phrase ledger creates no legal authority.
- Protocol phrase ledger is not enforcement.
- Protocol phrase ledger does not override human judgment.
- Human review is required before any real-world action.
- authority: none

Data sources (read-only):
  bridge/RESUME_STATE.md  — Principle Accumulation table (Phase 10–37b)
                            Protocol Phrases code blocks (Phase 38–44)
  globe/reports/*.json    — advisory_phrases arrays (supplement)
  globe/spec/GLOBE_SPEC.md — additional phrases from invariant blocks

CLI:
  python3 globe/runtime/protocol_phrase_ledger.py summary
  python3 globe/runtime/protocol_phrase_ledger.py save
  python3 globe/runtime/protocol_phrase_ledger.py show-phase <phase>
  python3 globe/runtime/protocol_phrase_ledger.py show-type <phrase_type>
  python3 globe/runtime/protocol_phrase_ledger.py search <query>
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Paths ──────────────────────────────────────────────────────────────────

_HERE = Path(__file__).parent
_GLOBE_DIR = _HERE.parent
_REPO_DIR = _GLOBE_DIR.parent
_REPORTS_DIR = _GLOBE_DIR / "reports"
_BRIDGE_DIR = _REPO_DIR / "bridge"
_SPEC_DIR = _GLOBE_DIR / "spec"

# ─── Invariants ─────────────────────────────────────────────────────────────

LEDGER_INVARIANTS: dict[str, object] = {
    "protocol_phrase_ledger_is_advisory_display_only": True,
    "protocol_phrase_ledger_creates_no_legal_authority": True,
    "protocol_phrase_ledger_is_not_enforcement": True,
    "protocol_phrase_ledger_does_not_override_human_judgment": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}

LEDGER_PHRASES: list[str] = [
    "Protocol phrase ledger is advisory display only.",
    "Protocol phrase ledger creates no legal authority.",
    "Protocol phrase ledger is not enforcement.",
    "Protocol phrase ledger does not override human judgment.",
    "Human review is required before any real-world action.",
]

PHRASE_TYPES: list[str] = [
    "advisory",
    "no_authority",
    "no_ranking",
    "no_allocation",
    "no_proof",
    "human_review",
    "no_responsibility_assignment",
    "append_only",
    "other",
]

# ─── Phrase type classifier ──────────────────────────────────────────────────

def classify(text: str) -> str:
    t = text.lower()
    if re.search(r"human (review|approval) is required", t):
        return "human_review"
    if re.search(r"append.only|must never be rewritten|existing entries", t):
        return "append_only"
    if re.search(r"does not assign responsibility|does not allocate responsibility", t):
        return "no_responsibility_assignment"
    if re.search(r"creates? no (legal )?authority|no legal authority", t):
        return "no_authority"
    if re.search(r"(advisory display only|advisory only|is advisory)", t):
        return "advisory"
    if re.search(r"does not rank|is not rank|is not reputation|is not priority score"
                 r"|is not governance score|is not score|does not score", t):
        return "no_ranking"
    if re.search(r"does not allocate|is not allocation|does not distribute", t):
        return "no_allocation"
    if re.search(r"is not proof|is not enforcement|is not judgment|is not coercion"
                 r"|is not certainty|is not command|is not obligation|is not credit"
                 r"|is not debt|is not prediction|is not prescription"
                 r"|is not (a )?(priority|governance|reputation|identity)", t):
        return "no_proof"
    return "other"


def normalize(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    t = text.lower().strip()
    t = re.sub(r"[\"'.!?,;:()]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


# ─── Extraction helpers ──────────────────────────────────────────────────────

def _parse_phase_num(s: str) -> str:
    """Convert a phase string like '10', '27b', '37b' to sortable form."""
    return s.strip()


def _phase_sort_key(p: str) -> tuple:
    """('10', ) → (10, '') ; ('27b', ) → (27, 'b')"""
    m = re.fullmatch(r"(\d+)([a-z]*)", p.lower())
    if m:
        return (int(m.group(1)), m.group(2))
    return (9999, p)


def _extract_resume_state(path: Path) -> list[tuple[str, str, str]]:
    """
    Returns list of (phase_str, phrase_text, source_hint) tuples.
    Parses:
    1. Principle Accumulation table rows: | 10 | "Phrase." |
    2. Protocol Phrases code blocks after: ### Protocol Phrases (Phase NN)
    """
    results: list[tuple[str, str, str]] = []
    if not path.exists():
        return results

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # 1. Principle Accumulation table
    in_table = False
    for i, line in enumerate(lines):
        if "Protocol Principle Accumulation" in line:
            in_table = True
            continue
        if in_table:
            if line.startswith("---") or (line.startswith("##") and "Accumulation" not in line):
                in_table = False
                continue
            m = re.match(r"\|\s*(\w+)\s*\|\s*\"(.+?)\"\s*\|", line)
            if m:
                phase = m.group(1)
                phrase = m.group(2).strip()
                results.append((phase, phrase, f"RESUME_STATE.md:line {i+1}"))

    # 2. Protocol Phrases code blocks
    i = 0
    while i < len(lines):
        m = re.match(r"###\s+Protocol Phrases?\s+\(Phase\s+(\w+)\)", lines[i])
        if m:
            phase = m.group(1)
            # Look for opening ```
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                i += 1
            i += 1  # skip ```
            while i < len(lines) and not lines[i].strip().startswith("```"):
                phrase = lines[i].strip()
                if phrase:
                    results.append((phase, phrase, f"RESUME_STATE.md:line {i+1}"))
                i += 1
        i += 1

    return results


def _extract_report_phrases(reports_dir: Path) -> list[tuple[str, str, str]]:
    """
    Extract advisory_phrases arrays from *.json reports.
    Returns (phase_str, phrase_text, source_hint).
    Phase is derived from the 'phase' field in the JSON.
    """
    results: list[tuple[str, str, str]] = []
    for json_path in sorted(reports_dir.glob("*.json")):
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        phase_raw = data.get("phase", "")
        # e.g. "Phase 41" → "41"
        m = re.search(r"(\d+[a-z]*)", str(phase_raw), re.I)
        phase = m.group(1) if m else "?"
        for phrase in data.get("advisory_phrases", []):
            if isinstance(phrase, str) and phrase.strip():
                results.append((phase, phrase.strip(), f"{json_path.name}"))
    return results


# ─── Builder ────────────────────────────────────────────────────────────────

def build_ledger() -> dict:
    """
    Build Protocol Phrase Ledger from all data sources.
    Deduplicates by normalized_phrase — keeps first occurrence,
    records all_phases list for phrases seen multiple times.
    """
    # Accumulate raw (phase, phrase, source_hint) tuples
    raw: list[tuple[str, str, str]] = []

    resume_path = _BRIDGE_DIR / "RESUME_STATE.md"
    raw.extend(_extract_resume_state(resume_path))

    raw.extend(_extract_report_phrases(_REPORTS_DIR))

    # Sort by phase (numerically) for stable first-seen ordering
    raw.sort(key=lambda x: (_phase_sort_key(x[0]), x[1]))

    # Deduplicate by normalized_phrase; track all phases
    seen: dict[str, dict] = {}  # normalized → entry dict
    entry_order: list[str] = []  # ordered normalized keys for stable output

    for phase, phrase_text, source_hint in raw:
        nrm = normalize(phrase_text)
        if not nrm:
            continue
        if nrm in seen:
            if phase not in seen[nrm]["all_phases"]:
                seen[nrm]["all_phases"].append(phase)
        else:
            seen[nrm] = {
                "normalized_phrase": nrm,
                "phrase_text": phrase_text,
                "phrase_type": classify(phrase_text),
                "phase": phase,
                "all_phases": [phase],
                "source_hint": source_hint,
            }
            entry_order.append(nrm)

    # Build final entries with phrase_ids
    # Assign IDs by phrase_type group then first_phase sort
    entries: list[dict] = []
    counter = 1
    now = datetime.now(timezone.utc).isoformat()

    for nrm in entry_order:
        e = seen[nrm]
        phrase_id = f"phrase-{counter:04d}"
        counter += 1
        entries.append({
            "phrase_id": phrase_id,
            "phase": e["phase"],
            "all_phases": sorted(e["all_phases"], key=_phase_sort_key),
            "source_file": e["source_hint"].split(":")[0],
            "source_line_hint": e["source_hint"],
            "phrase_text": e["phrase_text"],
            "phrase_type": e["phrase_type"],
            "normalized_phrase": e["normalized_phrase"],
            "first_seen_at": now,  # build time — no per-phrase timestamp in sources
            "advisory_only": True,
            "creates_no_legal_authority": True,
        })

    # Counts by type
    by_type: dict[str, int] = {}
    by_phase: dict[str, int] = {}
    for e in entries:
        pt = e["phrase_type"]
        by_type[pt] = by_type.get(pt, 0) + 1
        ph = e["phase"]
        by_phase[ph] = by_phase.get(ph, 0) + 1

    return {
        "ledger_id": "protocol-phrase-ledger-001",
        "generated_at": now,
        "phase": "Phase 45",
        "total_phrases": len(entries),
        "total_unique_normalized": len(entries),
        "total_raw_occurrences": len(raw),
        "by_phrase_type": {k: by_type.get(k, 0) for k in PHRASE_TYPES},
        "by_phase_first_seen": dict(sorted(by_phase.items(), key=lambda x: _phase_sort_key(x[0]))),
        **LEDGER_INVARIANTS,
        "advisory_phrases": LEDGER_PHRASES,
        "entries": entries,
    }


# ─── Output helpers ──────────────────────────────────────────────────────────

def _to_markdown(data: dict) -> str:
    lines = [
        "# Protocol Phrase Ledger (Phase 45)",
        "",
        f"generated_at: {data.get('generated_at', '')}",
        f"total_phrases: {data.get('total_phrases', 0)}",
        f"total_raw_occurrences: {data.get('total_raw_occurrences', 0)}",
        "",
        "## Invariants",
        "",
    ]
    for phrase in data.get("advisory_phrases", []):
        lines.append(f'- "{phrase}"')
    lines.append("")
    lines.append("## By Phrase Type")
    lines.append("")
    for pt, n in data.get("by_phrase_type", {}).items():
        if n > 0:
            lines.append(f"- `{pt}`: {n}")
    lines.append("")
    lines.append("## Entries")
    lines.append("")

    current_type = ""
    for e in data.get("entries", []):
        pt = e["phrase_type"]
        if pt != current_type:
            lines.append(f"### [{pt}]")
            lines.append("")
            current_type = pt
        phases_str = ", ".join(e["all_phases"])
        lines.append(f"**{e['phrase_id']}** `Phase {e['phase']}`  ")
        lines.append(f"> {e['phrase_text']}")
        lines.append(f"")
        lines.append(f"- all_phases: {phases_str}")
        lines.append(f"- source: {e['source_line_hint']}")
        lines.append("")

    return "\n".join(lines)


def save_ledger(data: dict | None = None) -> None:
    if data is None:
        data = build_ledger()
    json_path = _REPORTS_DIR / "protocol_phrase_ledger.json"
    md_path = _REPORTS_DIR / "protocol_phrase_ledger.md"
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_to_markdown(data), encoding="utf-8")
    print(f"  Saved: {json_path.relative_to(_REPO_DIR)}")
    print(f"  Saved: {md_path.relative_to(_REPO_DIR)}")


def load_ledger() -> dict:
    json_path = _REPORTS_DIR / "protocol_phrase_ledger.json"
    if json_path.exists():
        try:
            return json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return build_ledger()


def filter_entries(
    data: dict,
    phase_filter: str | None = None,
    type_filter: str | None = None,
    query: str | None = None,
) -> list[dict]:
    entries = data.get("entries", [])
    if phase_filter:
        entries = [e for e in entries if phase_filter in e.get("all_phases", [])]
    if type_filter:
        entries = [e for e in entries if e.get("phrase_type") == type_filter]
    if query:
        q = query.lower()
        entries = [
            e for e in entries
            if q in e.get("normalized_phrase", "")
            or q in e.get("phrase_type", "")
            or q in " ".join(e.get("all_phases", []))
        ]
    return entries


# ─── CLI ────────────────────────────────────────────────────────────────────

def cmd_summary(data: dict) -> None:
    print("Protocol Phrase Ledger (Phase 45)")
    print("=" * 60)
    print(f"  generated_at:          {data.get('generated_at', '')[:19]}")
    print(f"  total_phrases:         {data.get('total_phrases', 0)}")
    print(f"  total_raw_occurrences: {data.get('total_raw_occurrences', 0)}")
    print()
    print("  By phrase_type:")
    for pt, n in data.get("by_phrase_type", {}).items():
        if n > 0:
            bar = "█" * n
            print(f"    {pt:<30} {n:>3}  {bar}")
    print()
    print("  By first_seen phase:")
    for ph, n in data.get("by_phase_first_seen", {}).items():
        print(f"    Phase {ph:<6} {n:>3} phrase(s)")
    print()
    for phrase in LEDGER_PHRASES:
        print(f'  "{phrase}"')


def _print_entries(entries: list[dict], label: str) -> None:
    print(f"Protocol Phrase Ledger — {label}")
    print("=" * 60)
    print(f"  {len(entries)} phrase(s)")
    print()
    for e in entries:
        phases_str = ", ".join(e.get("all_phases", []))
        print(f"  [{e['phrase_type']}] {e['phrase_id']}  Phase {e['phase']}")
        print(f"    \"{e['phrase_text']}\"")
        print(f"    phases: {phases_str}")
        print(f"    source: {e['source_line_hint']}")
        print()
    for phrase in LEDGER_PHRASES:
        print(f'  "{phrase}"')


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("Usage: protocol_phrase_ledger.py <summary|save|show-phase|show-type|search> [arg]")
        sys.exit(1)

    cmd = args[0]
    data = build_ledger()

    if cmd == "summary":
        cmd_summary(data)

    elif cmd == "save":
        print("Saving Protocol Phrase Ledger (Phase 45)...")
        save_ledger(data)
        print(f"  total_phrases: {data['total_phrases']}")
        print(f"  total_raw_occurrences: {data['total_raw_occurrences']}")
        print()
        for phrase in LEDGER_PHRASES:
            print(f'  "{phrase}"')

    elif cmd == "show-phase":
        ph = args[1] if len(args) > 1 else ""
        _print_entries(filter_entries(data, phase_filter=ph), f"phase={ph}")

    elif cmd == "show-type":
        pt = args[1] if len(args) > 1 else ""
        _print_entries(filter_entries(data, type_filter=pt), f"type={pt}")

    elif cmd == "search":
        q = args[1] if len(args) > 1 else ""
        _print_entries(filter_entries(data, query=q), f"search={q!r}")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
