#!/usr/bin/env python3
"""
trust_score.py — Dan-Go Mujin Protocol

Calculate trust scores from a contribution history JSON file.
Uses the formula defined in TRUST_MODEL.md.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

WEIGHTS = {
    "verified": 2.0,
    "committed": 1.5,
    "delivered": 1.0,
    "offered": 0.5,
    "disputed": -1.0,
    "withdrawn_after_commit": -2.0,
}

PSEUDONYM_MULTIPLIER = 0.8

SAMPLE_HISTORY = {
    "contributors": [
        {
            "contributor_id": "did:key:z6Mkexample1",
            "pseudonymous": False,
            "contributions": [
                {"status": "verified", "timestamp": "2026-05-01T00:00:00Z"},
                {"status": "delivered", "timestamp": "2026-05-10T00:00:00Z"},
                {"status": "offered",   "timestamp": "2026-05-20T00:00:00Z"},
            ]
        },
        {
            "contributor_id": "anon-participant-42",
            "pseudonymous": True,
            "contributions": [
                {"status": "offered",   "timestamp": "2026-05-15T00:00:00Z"},
                {"status": "committed", "timestamp": "2026-05-18T00:00:00Z"},
            ]
        }
    ]
}


def time_factor(timestamps: list[str]) -> float:
    """More recent contributions count slightly more. Returns 0.8–1.2."""
    if not timestamps:
        return 1.0
    now = datetime.now(timezone.utc)
    ages_days = []
    for ts in timestamps:
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            ages_days.append((now - dt).days)
        except Exception:
            pass
    if not ages_days:
        return 1.0
    avg_age = sum(ages_days) / len(ages_days)
    # Contributions with avg age < 30 days get 1.2, > 365 days get 0.8
    factor = 1.2 - (avg_age / 365) * 0.4
    return max(0.8, min(1.2, factor))


def calculate_score(contributor: dict) -> float:
    contributions = contributor.get("contributions", [])
    pseudonymous = contributor.get("pseudonymous", False)

    if not contributions:
        return 0.0

    raw_score = sum(WEIGHTS.get(c.get("status", ""), 0.0) for c in contributions)
    total = len(contributions)
    timestamps = [c.get("timestamp", "") for c in contributions]

    score = (raw_score / max(1, total)) * time_factor(timestamps)
    if pseudonymous:
        score *= PSEUDONYM_MULTIPLIER

    return max(0.0, min(1.0, score))


def score_label(score: float) -> str:
    if score < 0.2:
        return "New participant"
    if score < 0.5:
        return "Early contributor"
    if score < 0.8:
        return "Established contributor"
    return "High trust"


def main():
    if len(sys.argv) >= 2:
        path = sys.argv[1]
        if not Path(path).exists():
            print(f"Error: file not found: {path}")
            sys.exit(1)
        with open(path) as f:
            history = json.load(f)
    else:
        print("No history file provided. Running with sample data.\n")
        history = SAMPLE_HISTORY

    print("=" * 60)
    print("TRUST SCORE REPORT — Dan-Go Mujin Protocol")
    print("=" * 60)

    contributors = history.get("contributors", [])
    if not contributors:
        print("No contributors found.")
        return

    scores = []
    for c in contributors:
        cid = c.get("contributor_id", "unknown")
        score = calculate_score(c)
        label = score_label(score)
        pseudo = " (pseudonymous)" if c.get("pseudonymous") else ""
        n = len(c.get("contributions", []))
        scores.append((score, cid, label, pseudo, n))

    scores.sort(reverse=True)

    print(f"\n{'Rank':<5} {'Score':<7} {'Label':<26} {'ID'}")
    print("-" * 60)
    for i, (score, cid, label, pseudo, n) in enumerate(scores, 1):
        print(f"#{i:<4} {score:.3f}  {label + pseudo:<26}  {cid}  ({n} contributions)")

    print("\n" + "=" * 60)
    print("Note: Trust score is information, not a gate.")
    print("See TRUST_MODEL.md for the full model.")
    print("=" * 60)


if __name__ == "__main__":
    main()
