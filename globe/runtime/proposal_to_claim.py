#!/usr/bin/env python3
"""
proposal_to_claim.py — Proposal → Claim Conversion (Phase 23)
Dan-Go × GITSEA — Globe Claim Conversion Layer

Converts accepted Globe Proposals into Dan-Go Claim format.
Only accepted proposals are eligible for conversion.
Outputs both JSON and Markdown to globe/claims/.

authority: none · advisory only · append-only · stdlib only
claim_creates_obligation: false

Usage:
    python3 globe/runtime/proposal_to_claim.py convert <proposal_id>
    python3 globe/runtime/proposal_to_claim.py convert-globe <globe_id>
    python3 globe/runtime/proposal_to_claim.py list
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_GLOBE_DIR = Path(__file__).resolve().parents[1]
_DATA_DIR = _GLOBE_DIR / "data"
_CLAIMS_DIR = _GLOBE_DIR / "claims"

# Proposal is not execution.
# Claim is not command.
# Conversion is not allocation.

PHASE_INVARIANTS = {
    "source_type": "proposal",
    "authority": "none",
    "execution_allowed": False,
    "moves_money": False,
    "hard_enforcement": False,
    "advisory": True,
    "append_only": True,
    "contestable": True,
    "claim_creates_obligation": False,
    "conversion_is_allocation": False,
    "claim_certifies_execution": False,
}


def _load(filename: str) -> list:
    p = _DATA_DIR / filename
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _load_claims() -> list:
    _CLAIMS_DIR.mkdir(exist_ok=True)
    claims = []
    for f in sorted(_CLAIMS_DIR.glob("*.json")):
        try:
            claims.append(json.loads(f.read_text()))
        except Exception:
            pass
    return claims


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _excerpt(text: str, max_len: int = 120) -> str:
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "…"


def _build_deliberation_summary(proposal_id: str) -> list:
    deliberations = _load("deliberations.json")
    entries = [d for d in deliberations if d.get("proposal_id") == proposal_id]
    summary = []
    for d in entries:
        summary.append({
            "deliberation_id": d.get("deliberation_id", ""),
            "speaker_type": d.get("speaker_type", ""),
            "speaker_name": d.get("speaker_name", ""),
            "content_excerpt": _excerpt(d.get("content", "")),
            "created_at": d.get("created_at", ""),
        })
    return summary


def _build_rationale(proposal: dict, globe_name: str) -> str:
    body = proposal.get("body", "")
    # Try to extract a rationale section from common markers
    for marker in ["理由：\n", "Rationale:\n", "背景：\n", "Background:\n"]:
        idx = body.find(marker)
        if idx != -1:
            section = body[idx + len(marker):]
            end = section.find("\n\n")
            extracted = section[:end].strip() if end != -1 else section.strip()
            if extracted:
                return extracted
    # Fallback: first non-empty paragraph of body
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    if paragraphs:
        return _excerpt(paragraphs[0], 300)
    return (
        f"この提案は {globe_name} において accepted となり、"
        "Dan-Go クレームとして変換されました。詳細は claim_body を参照してください。"
    )


def _build_markdown(claim: dict, globe_name: str) -> str:
    delib_lines = ""
    for d in claim.get("deliberation_summary", []):
        icon = {"human": "👤", "ai": "🤖", "system": "⚙️"}.get(d.get("speaker_type", ""), "")
        delib_lines += (
            f"- {icon} **{d.get('speaker_name', '?')}**"
            f" [{d.get('deliberation_id', '')}]\n"
            f"  > {d.get('content_excerpt', '')}\n\n"
        )

    gitsea = claim.get("gitsea_link") or {}
    gitsea_lines = ""
    for field in ["gitsea_repo_url", "gitsea_issue_url", "gitsea_pr_url", "commit_hash", "linked_rule_path"]:
        val = gitsea.get(field)
        if val:
            gitsea_lines += f"- **{field}**: {val}\n"
    if not gitsea_lines:
        gitsea_lines = "_GITSEA link fields not yet populated._\n"

    delib_section = delib_lines if delib_lines else "_No deliberation entries recorded._\n"
    count = claim.get("deliberation_count", len(claim.get("deliberation_summary", [])))

    return f"""# {claim['title']}

> **claim_id:** `{claim['claim_id']}`
> **status:** `{claim['status']}`
> **source:** Proposal `{claim['source_proposal_id']}` → Dan-Go Claim
> **globe:** {globe_name} (`{claim['globe_id']}`)

---

## Claim Body

{claim.get('claim_body', '')}

---

## Rationale

{claim.get('rationale', '')}

---

## Deliberation Summary ({count} entries)

{delib_section}---

## GITSEA Link

{gitsea_lines}
---

## Next Action

この Claim は `claim_draft` 状態です。
Dan-Go プロトコルに従い、以下のステップを検討してください：

1. 実行計画（Execution Plan）に変換する
2. 必要な貢献（Contribution）を列挙する
3. GITSEA / gitlawb に PR・Issue として提出する
4. 実行履歴（Reality Feedback）を記録する

> authority: none · advisory only · claim_creates_obligation: false
> Proposal is not execution. Claim is not command. Conversion is not allocation.

---

_Generated by Dan-Go Mujin · Phase 23 · {claim.get('created_at', '')[:10]}_
"""


def convert_proposal(proposal_id: str, verbose: bool = True) -> dict | None:
    """Convert a single accepted proposal to a Dan-Go Claim."""
    proposals = _load("proposals.json")
    globes = _load("globes.json")

    p = next((x for x in proposals if x.get("proposal_id") == proposal_id), None)
    if not p:
        if verbose:
            print(f"ERROR: proposal '{proposal_id}' not found.")
        return None

    if p.get("status") != "accepted":
        if verbose:
            print(
                f"ERROR: proposal '{proposal_id}' has status "
                f"'{p.get('status')}'. Only accepted proposals can be converted."
            )
        return None

    globe = next((g for g in globes if g.get("globe_id") == p.get("globe_id")), {})
    globe_name = globe.get("name", p.get("globe_id", ""))

    now = _now()
    claim_id = f"claim-{proposal_id}"

    # Check if already exists — update updated_at but preserve created_at
    existing_path = _CLAIMS_DIR / f"{claim_id}.json"
    original_created_at = now
    if existing_path.exists():
        try:
            existing = json.loads(existing_path.read_text())
            original_created_at = existing.get("created_at", now)
        except Exception:
            pass

    deliberation_summary = _build_deliberation_summary(proposal_id)
    rationale = _build_rationale(p, globe_name)

    claim = {
        "claim_id": claim_id,
        **PHASE_INVARIANTS,
        "source_proposal_id": proposal_id,
        "globe_id": p.get("globe_id", ""),
        "title": p.get("title", ""),
        "claim_body": p.get("body", ""),
        "rationale": rationale,
        "deliberation_summary": deliberation_summary,
        "deliberation_count": len(deliberation_summary),
        "gitsea_link": p.get("gitsea_link"),
        "status": "claim_draft",
        "created_at": original_created_at,
        "updated_at": now,
    }

    # Write JSON
    _CLAIMS_DIR.mkdir(exist_ok=True)
    json_path = _CLAIMS_DIR / f"{claim_id}.json"
    json_path.write_text(json.dumps(claim, ensure_ascii=False, indent=2))

    # Write Markdown
    md_path = _CLAIMS_DIR / f"{claim_id}.md"
    md_path.write_text(_build_markdown(claim, globe_name))

    if verbose:
        print(f"claim_id:      {claim_id}")
        print(f"source:        proposal/{proposal_id}")
        print(f"globe:         {globe_name} ({p.get('globe_id', '')})")
        print(f"title:         {p.get('title', '')}")
        print(f"deliberations: {len(deliberation_summary)} entries")
        print(f"status:        claim_draft")
        print(f"output (json): globe/claims/{claim_id}.json")
        print(f"output (md):   globe/claims/{claim_id}.md")
        print()
        print("authority: none · advisory only · claim_creates_obligation: false")

    return claim


def convert_globe(globe_id: str) -> None:
    """Batch-convert all accepted proposals in a globe."""
    proposals = _load("proposals.json")
    accepted = [
        p for p in proposals
        if p.get("globe_id") == globe_id and p.get("status") == "accepted"
    ]

    if not accepted:
        print(f"No accepted proposals found for globe '{globe_id}'.")
        return

    print(f"Converting {len(accepted)} accepted proposal(s) in globe '{globe_id}'...\n")
    converted = 0
    for p in accepted:
        pid = p["proposal_id"]
        print(f"--- {pid} ---")
        result = convert_proposal(pid, verbose=True)
        if result:
            converted += 1
        print()

    print(f"Done. {converted}/{len(accepted)} proposals converted.")
    print()
    print("Proposal is not execution. Claim is not command. Conversion is not allocation.")


def list_claims() -> None:
    """List all generated claims in globe/claims/."""
    claims = _load_claims()
    if not claims:
        print("No claims found in globe/claims/.")
        print()
        print("Run: python3 globe/runtime/proposal_to_claim.py convert <proposal_id>")
        return

    print(f"globe/claims/ — {len(claims)} claim(s)\n")
    for c in claims:
        count = c.get("deliberation_count", len(c.get("deliberation_summary", [])))
        print(f"  {c.get('claim_id', '?')}")
        print(f"    source:        proposal/{c.get('source_proposal_id', '?')}")
        print(f"    globe:         {c.get('globe_id', '?')}")
        print(f"    title:         {c.get('title', '?')}")
        print(f"    status:        {c.get('status', '?')}")
        print(f"    deliberations: {count}")
        print(f"    created_at:    {str(c.get('created_at', '?'))[:19]}")
        print()


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]

    if cmd == "convert":
        if len(args) < 2:
            print("Usage: proposal_to_claim.py convert <proposal_id>")
            sys.exit(1)
        convert_proposal(args[1])

    elif cmd == "convert-globe":
        if len(args) < 2:
            print("Usage: proposal_to_claim.py convert-globe <globe_id>")
            sys.exit(1)
        convert_globe(args[1])

    elif cmd == "list":
        list_claims()

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: convert, convert-globe, list")
        sys.exit(1)


if __name__ == "__main__":
    main()
