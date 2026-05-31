"""globe_search.py — Phase 31: Globe Search / Filter

Builds a flat search index across all Globe-layer artifacts and provides
CLI search/filter commands and a JSON index for globe_server.py.

INVARIANTS (permanent, not negotiable):
  Search is advisory display only.
  Search result is not proof of relevance.
  Search result does not rank participants.
  Search result does not allocate resources.
  Human review is required before any real-world action.
  authority: none

CLI:
  python3 globe/runtime/globe_search.py save-index
  python3 globe/runtime/globe_search.py search <query>
  python3 globe/runtime/globe_search.py filter --globe <globe_id>
  python3 globe/runtime/globe_search.py filter --entry-type <entry_type>
  python3 globe/runtime/globe_search.py filter --resolution-status <status>
  python3 globe/runtime/globe_search.py filter --bridge-target <target>
  python3 globe/runtime/globe_search.py filter --type globe|proposal|directive|log|feedback|link|claim
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────

_GLOBE_DIR   = Path(__file__).resolve().parents[1]      # globe/
_REPORTS_DIR = _GLOBE_DIR / "reports"
_DATA_DIR    = _GLOBE_DIR / "data"
_CLAIMS_DIR  = _GLOBE_DIR / "claims"
_DIRECTIVES_DIR = _GLOBE_DIR / "directives"
_LOGS_DIR    = _GLOBE_DIR / "logs"

_INDEX_PATH  = _REPORTS_DIR / "globe_search_index.json"

# ─── Invariants ───────────────────────────────────────────────────────────────

SEARCH_INVARIANTS = {
    "search_is_advisory_display_only": True,
    "search_result_is_not_proof_of_relevance": True,
    "search_result_does_not_rank_participants": True,
    "search_result_does_not_allocate_resources": True,
    "human_review_is_required_before_any_real_world_action": True,
    "authority": "none",
}

SEARCH_PHRASES = [
    "Search is advisory display only.",
    "Search result is not proof of relevance.",
    "Search result does not rank participants.",
    "Search result does not allocate resources.",
    "Human review is required before any real-world action.",
]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _load_jsonl(path: Path) -> list:
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except Exception:
                pass
    return entries


def _excerpt(text: str, max_len: int = 160) -> str:
    text = " ".join(str(text).split())
    return text[:max_len] + ("…" if len(text) > max_len else "")


def _searchable(*parts: str | None) -> str:
    return " ".join(str(p) for p in parts if p).lower()


def _make_item(
    item_id: str,
    item_type: str,
    globe_id: str,
    source_path: str,
    title: str,
    content_excerpt: str,
    searchable_text: str,
    tags: list[str],
    created_at: str = "",
    entry_type: str = "",
    resolution_status: str = "",
    bridge_target: str = "",
    confidence: str = "",
    url_path: str = "",
) -> dict:
    return {
        "item_id": item_id,
        "item_type": item_type,
        "globe_id": globe_id,
        "source_path": source_path,
        "title": title,
        "content_excerpt": content_excerpt,
        "searchable_text": searchable_text,
        "tags": tags,
        "created_at": created_at,
        # Optional filter fields — empty string when not applicable
        "entry_type": entry_type,
        "resolution_status": resolution_status,
        "bridge_target": bridge_target,
        "confidence": confidence,
        "url_path": url_path,
        "advisory_only": True,
    }


# ─── Index builders ───────────────────────────────────────────────────────────

def _index_globes() -> list[dict]:
    items = []
    data = _load_json(_DATA_DIR / "globes.json")
    if not isinstance(data, list):
        return items
    for g in data:
        gid = g.get("globe_id", "")
        title = g.get("name", gid)
        body = " ".join(filter(None, [
            g.get("description", ""),
            g.get("founding_statement", ""),
            g.get("governance_model", ""),
            g.get("membership_policy", ""),
        ]))
        tags = list(filter(None, [
            g.get("governance_model", ""),
            g.get("membership_policy", ""),
        ]))
        items.append(_make_item(
            item_id=gid,
            item_type="globe",
            globe_id=gid,
            source_path=str(_DATA_DIR / "globes.json"),
            title=title,
            content_excerpt=_excerpt(body),
            searchable_text=_searchable(gid, title, body, *tags),
            tags=tags,
            created_at=g.get("created_at", ""),
            url_path=f"/globe/{gid}",
        ))
    return items


def _index_proposals() -> list[dict]:
    items = []
    data = _load_json(_DATA_DIR / "proposals.json")
    if not isinstance(data, list):
        return items
    for p in data:
        pid = p.get("proposal_id", "")
        gid = p.get("globe_id", "")
        title = p.get("title", pid)
        body = " ".join(filter(None, [
            p.get("body", ""),
            p.get("proposer", ""),
            p.get("status", ""),
        ]))
        tags = list(filter(None, [p.get("status", ""), gid]))
        items.append(_make_item(
            item_id=pid,
            item_type="proposal",
            globe_id=gid,
            source_path=str(_DATA_DIR / "proposals.json"),
            title=title,
            content_excerpt=_excerpt(p.get("body", "")),
            searchable_text=_searchable(pid, gid, title, body, *tags),
            tags=tags,
            created_at=p.get("created_at", ""),
            url_path=f"/globe/{gid}/proposals/{pid}",
        ))
    return items


def _index_deliberations() -> list[dict]:
    items = []
    data = _load_json(_DATA_DIR / "deliberations.json")
    if not isinstance(data, list):
        return items
    # Build proposal→globe map
    proposals = _load_json(_DATA_DIR / "proposals.json") or []
    prop_map = {p.get("proposal_id", ""): p.get("globe_id", "") for p in proposals}

    for d in data:
        did = d.get("deliberation_id", "")
        pid = d.get("proposal_id", "")
        gid = prop_map.get(pid, "")
        speaker = d.get("speaker_name", d.get("speaker_type", ""))
        content = d.get("content", "")
        title = f"Deliberation by {speaker} on {pid}"
        tags = list(filter(None, [d.get("speaker_type", ""), gid, pid]))
        items.append(_make_item(
            item_id=did,
            item_type="deliberation",
            globe_id=gid,
            source_path=str(_DATA_DIR / "deliberations.json"),
            title=title,
            content_excerpt=_excerpt(content),
            searchable_text=_searchable(did, pid, gid, speaker, content),
            tags=tags,
            created_at=d.get("created_at", ""),
            url_path=f"/globe/{gid}/proposals/{pid}",
        ))
    return items


def _index_claims() -> list[dict]:
    items = []
    for p in sorted(_CLAIMS_DIR.glob("*.json")):
        c = _load_json(p)
        if not isinstance(c, dict):
            continue
        cid = c.get("claim_id", p.stem)
        gid = c.get("globe_id", "")
        title = c.get("title", cid)
        # deliberation_summary may be a list of dicts
        delib_sum = c.get("deliberation_summary", "")
        if isinstance(delib_sum, list):
            delib_sum = " ".join(
                d.get("content_excerpt", "") for d in delib_sum if isinstance(d, dict)
            )
        body = " ".join(filter(None, [
            c.get("claim_body", ""),
            c.get("rationale", ""),
            str(delib_sum),
        ]))
        tags = list(filter(None, [c.get("status", ""), gid]))
        items.append(_make_item(
            item_id=cid,
            item_type="claim",
            globe_id=gid,
            source_path=str(p),
            title=title,
            content_excerpt=_excerpt(body),
            searchable_text=_searchable(cid, gid, title, body, *tags),
            tags=tags,
            created_at=c.get("created_at", ""),
        ))
    return items


def _index_directives() -> list[dict]:
    items = []
    for p in sorted(_DIRECTIVES_DIR.glob("*.json")):
        d = _load_json(p)
        if not isinstance(d, dict):
            continue
        did = d.get("directive_id", p.stem)
        gid = d.get("globe_id", "")
        title = d.get("title", did)
        # scope / execution_steps may be dicts or lists
        scope = d.get("scope", "")
        if isinstance(scope, dict):
            scope = " ".join(
                " ".join(v) if isinstance(v, list) else str(v)
                for v in scope.values()
            )
        elif isinstance(scope, list):
            scope = " ".join(str(s) for s in scope)
        body = " ".join(filter(None, [
            d.get("objective", ""),
            str(scope),
            d.get("non_authority_clause", ""),
        ]))
        tags = list(filter(None, [d.get("status", ""), gid]))
        items.append(_make_item(
            item_id=did,
            item_type="directive",
            globe_id=gid,
            source_path=str(p),
            title=title,
            content_excerpt=_excerpt(body),
            searchable_text=_searchable(did, gid, title, body, *tags),
            tags=tags,
            created_at=d.get("created_at", ""),
            url_path=f"/globe/{gid}/directives/{did}",
        ))
    return items


def _index_logs() -> list[dict]:
    items = []
    for p in sorted(_LOGS_DIR.glob("*.jsonl")):
        for entry in _load_jsonl(p):
            lid = entry.get("log_id", "")
            did = entry.get("directive_id", "")
            gid = entry.get("globe_id", "")
            et = entry.get("entry_type", "")
            rs = entry.get("resolution_status", "")
            actor = entry.get("actor_name", entry.get("actor_type", ""))
            content = entry.get("content", "")
            title = f"{et} by {actor} [{lid}]"
            tags = list(filter(None, [et, gid, rs, did]))
            items.append(_make_item(
                item_id=lid,
                item_type="log",
                globe_id=gid,
                source_path=str(p),
                title=title,
                content_excerpt=_excerpt(content),
                searchable_text=_searchable(lid, did, gid, et, rs, actor, content),
                tags=tags,
                created_at=entry.get("created_at", ""),
                entry_type=et,
                resolution_status=rs,
                url_path=f"/globe/{gid}/logs/{did}",
            ))
    return items


def _index_bridge() -> list[dict]:
    items = []
    data = _load_json(_REPORTS_DIR / "reality_feedback_bridge.json")
    if not isinstance(data, dict):
        return items
    for r in data.get("records", []):
        fid = r.get("feedback_id", "")
        did = r.get("source_directive_id", "")
        gid = r.get("globe_id", "")
        et = r.get("entry_type", "")
        target = r.get("suggested_bridge_target", "")
        actor = r.get("actor_name", r.get("actor_type", ""))
        content = r.get("content", "")
        reason = r.get("suggested_reason", "")
        title = f"Bridge feedback {fid}: {et} → {target}"
        tags = list(filter(None, [et, target, gid, did]))
        items.append(_make_item(
            item_id=fid,
            item_type="feedback",
            globe_id=gid,
            source_path=str(_REPORTS_DIR / "reality_feedback_bridge.json"),
            title=title,
            content_excerpt=_excerpt(content + " " + reason),
            searchable_text=_searchable(fid, did, gid, et, target, actor, content, reason),
            tags=tags,
            created_at=r.get("source_entry_created_at", ""),
            entry_type=et,
            bridge_target=target,
            url_path=f"/globe/{gid}/logs/{did}",
        ))
    return items


def _index_links() -> list[dict]:
    items = []
    data = _load_json(_REPORTS_DIR / "bridge_target_links.json")
    if not isinstance(data, dict):
        return items
    for c in data.get("candidates", []):
        lid = c.get("link_id", "")
        did = c.get("source_directive_id", "")
        gid = c.get("globe_id", "")
        target = c.get("suggested_bridge_target", "")
        conf = c.get("confidence", "")
        ctype = c.get("candidate_target_type", "")
        cpath = c.get("candidate_path", "")
        desc = c.get("candidate_description", "")
        reason = c.get("match_reason", "")
        title = f"Link {lid}: {ctype} ({conf})"
        tags = list(filter(None, [conf, ctype, target, gid]))
        items.append(_make_item(
            item_id=lid,
            item_type="link",
            globe_id=gid,
            source_path=str(_REPORTS_DIR / "bridge_target_links.json"),
            title=title,
            content_excerpt=_excerpt(desc + " " + reason),
            searchable_text=_searchable(lid, did, gid, conf, ctype, cpath, desc, reason, target),
            tags=tags,
            created_at=c.get("created_at", ""),
            bridge_target=target,
            confidence=conf,
        ))
    return items


# ─── Index assembly ───────────────────────────────────────────────────────────

def build_index() -> dict:
    """Build and return the full search index.

    Advisory only. Not proof of relevance. No ranking. No allocation.
    """
    items: list[dict] = []
    items.extend(_index_globes())
    items.extend(_index_proposals())
    items.extend(_index_deliberations())
    items.extend(_index_claims())
    items.extend(_index_directives())
    items.extend(_index_logs())
    items.extend(_index_bridge())
    items.extend(_index_links())

    # Stable sort: source_path then created_at (no relevance ranking)
    items.sort(key=lambda x: (x["source_path"], x["created_at"]))

    counts: dict[str, int] = {}
    for it in items:
        counts[it["item_type"]] = counts.get(it["item_type"], 0) + 1

    return {
        "index_id": "globe-search-index",
        "generated_at": _now(),
        "total_items": len(items),
        "item_type_counts": counts,
        **SEARCH_INVARIANTS,
        "phase": "31",
        "phase_phrases": SEARCH_PHRASES,
        "items": items,
    }


# ─── Search / Filter ──────────────────────────────────────────────────────────

def _match_reason(item: dict, query_lower: str) -> str:
    """Describe why this item matched — no score, no ranking."""
    reasons = []
    q = query_lower
    if q in item["title"].lower():
        reasons.append("matched title")
    if q in item["content_excerpt"].lower():
        reasons.append("matched content")
    if any(q in t.lower() for t in item["tags"]):
        reasons.append("matched tag")
    if q in item.get("entry_type", "").lower():
        reasons.append("matched entry_type")
    if q in item.get("resolution_status", "").lower():
        reasons.append("matched resolution_status")
    if q in item.get("bridge_target", "").lower():
        reasons.append("matched bridge_target")
    if not reasons and q in item["searchable_text"]:
        reasons.append("matched searchable text")
    return " · ".join(reasons) if reasons else "matched"


def search(
    index_items: list[dict],
    query: str | None = None,
    globe_id: str | None = None,
    entry_type: str | None = None,
    resolution_status: str | None = None,
    bridge_target: str | None = None,
    item_type: str | None = None,
) -> list[dict]:
    """Return matching items from the index.

    Advisory display only. Results are not ranked by relevance.
    Results are ordered by source_path + created_at (stable, not by score).
    """
    results = []
    q = query.lower().strip() if query else None

    for item in index_items:
        # Apply filters first (exact / substring, case-insensitive)
        if globe_id and item["globe_id"].lower() != globe_id.lower():
            continue
        if entry_type and item.get("entry_type", "").lower() != entry_type.lower():
            continue
        if resolution_status and item.get("resolution_status", "").lower() != resolution_status.lower():
            continue
        if bridge_target and item.get("bridge_target", "").lower() != bridge_target.lower():
            continue
        if item_type and item["item_type"].lower() != item_type.lower():
            continue

        # Text query — simple substring, no scoring
        if q and q not in item["searchable_text"]:
            continue

        reason = _match_reason(item, q) if q else "filter match"
        results.append({
            "item_type": item["item_type"],
            "item_id": item["item_id"],
            "title": item["title"],
            "globe_id": item["globe_id"],
            "match_reason": reason,
            "content_excerpt": item["content_excerpt"],
            "source_path": item["source_path"],
            "url_path": item.get("url_path", ""),
            "entry_type": item.get("entry_type", ""),
            "resolution_status": item.get("resolution_status", ""),
            "bridge_target": item.get("bridge_target", ""),
            "confidence": item.get("confidence", ""),
            "created_at": item["created_at"],
            "advisory_only": True,
        })

    return results  # already stable-sorted from index build


# ─── Persistence ──────────────────────────────────────────────────────────────

def save_index() -> Path:
    """Save the search index as JSON. Advisory only."""
    idx = build_index()
    _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    _INDEX_PATH.write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding="utf-8")
    return _INDEX_PATH


def load_index() -> list[dict]:
    """Load index items from saved JSON, or build on-the-fly."""
    if _INDEX_PATH.exists():
        try:
            raw = json.loads(_INDEX_PATH.read_text(encoding="utf-8"))
            if isinstance(raw, dict) and "items" in raw:
                return raw["items"]
        except Exception:
            pass
    return build_index()["items"]


# ─── CLI Print helpers ────────────────────────────────────────────────────────

_TYPE_ICON = {
    "globe":       "🌐",
    "proposal":    "📋",
    "deliberation":"💬",
    "claim":       "📌",
    "directive":   "🗂️",
    "log":         "📝",
    "feedback":    "🔗",
    "link":        "🔗",
}


def _print_result(r: dict, idx: int) -> None:
    icon = _TYPE_ICON.get(r["item_type"], "•")
    print(f"  [{idx}] {icon} {r['item_type'].upper():12s} {r['item_id']}")
    print(f"       title:   {r['title']}")
    if r["globe_id"]:
        print(f"       globe:   {r['globe_id']}")
    if r.get("entry_type"):
        print(f"       entry_type: {r['entry_type']}")
    if r.get("resolution_status"):
        print(f"       resolution_status: {r['resolution_status']}")
    if r.get("bridge_target"):
        print(f"       bridge_target: {r['bridge_target']}")
    if r.get("confidence"):
        print(f"       confidence: {r['confidence']}")
    print(f"       reason:  {r['match_reason']}")
    if r["content_excerpt"]:
        print(f"       excerpt: {r['content_excerpt'][:100]}")
    if r.get("url_path"):
        print(f"       url:     http://localhost:7422{r['url_path']}")
    print()


def print_results(results: list[dict], label: str) -> None:
    print(f"\nSearch / Filter Results — {label}")
    print("=" * 60)
    print(f"  {len(results)} result(s)  [advisory display only · not proof of relevance · no ranking]")
    print()
    if not results:
        print("  No items matched.")
    else:
        for i, r in enumerate(results, 1):
            _print_result(r, i)
    print('  "Search result is not proof of relevance."')
    print('  "Search result does not rank participants."')
    print('  "Human review is required before any real-world action."')


# ─── CLI entry point ──────────────────────────────────────────────────────────

def main(argv: list[str]) -> None:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return

    cmd = argv[0]

    # ── save-index ──────────────────────────────────────────────────────
    if cmd == "save-index":
        idx = build_index()
        path = save_index()
        print(f"Search index saved: {path}")
        print(f"  total_items:      {idx['total_items']}")
        for k, v in sorted(idx["item_type_counts"].items()):
            print(f"  {k:16s}: {v}")
        print()
        for phrase in SEARCH_PHRASES:
            print(f'  "{phrase}"')
        return

    # ── search <query> ──────────────────────────────────────────────────
    if cmd == "search":
        if len(argv) < 2:
            print("Usage: globe_search.py search <query>", file=sys.stderr)
            sys.exit(1)
        query = " ".join(argv[1:])
        items = load_index()
        results = search(items, query=query)
        print_results(results, f'query="{query}"')
        return

    # ── filter ──────────────────────────────────────────────────────────
    if cmd == "filter":
        globe_id = entry_type = resolution_status = bridge_target = item_type = None
        args = argv[1:]
        i = 0
        while i < len(args):
            flag = args[i]
            val = args[i + 1] if i + 1 < len(args) else ""
            if flag == "--globe":
                globe_id = val; i += 2
            elif flag == "--entry-type":
                entry_type = val; i += 2
            elif flag == "--resolution-status":
                resolution_status = val; i += 2
            elif flag == "--bridge-target":
                bridge_target = val; i += 2
            elif flag == "--type":
                item_type = val; i += 2
            else:
                print(f"Unknown flag: {flag}", file=sys.stderr)
                sys.exit(1)

        if not any([globe_id, entry_type, resolution_status, bridge_target, item_type]):
            print("Usage: globe_search.py filter [--globe G] [--entry-type E] "
                  "[--resolution-status S] [--bridge-target T] [--type TYPE]",
                  file=sys.stderr)
            sys.exit(1)

        parts = []
        if globe_id:           parts.append(f"globe={globe_id}")
        if entry_type:         parts.append(f"entry_type={entry_type}")
        if resolution_status:  parts.append(f"resolution_status={resolution_status}")
        if bridge_target:      parts.append(f"bridge_target={bridge_target}")
        if item_type:          parts.append(f"type={item_type}")
        label = " · ".join(parts)

        items = load_index()
        results = search(
            items,
            globe_id=globe_id,
            entry_type=entry_type,
            resolution_status=resolution_status,
            bridge_target=bridge_target,
            item_type=item_type,
        )
        print_results(results, label)
        return

    print(f"Unknown command: {cmd}", file=sys.stderr)
    print("Commands: save-index | search <query> | filter [flags]", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
