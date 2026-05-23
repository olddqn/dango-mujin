#!/usr/bin/env python3
"""
temporal_trust_decay.py — dango-gitsea-bridge / trust layer

Compute time-decaying trust weights for su-table contribution events.

Core insight:
  memory is permanent — trust is dynamic.

Trust weight formula:
  trust_weight =
      base_weight
    × decay_factor
    × verification_multiplier
    × dignity_multiplier
    × continuity_multiplier

  decay_factor = max(MIN_WEIGHT, 0.5 ^ (days_since / half_life_days))

Default half-life: 90 days.
Minimum weight:    0.05  (contribution never fully disappears from memory)

Dignity block is the only hard zero:
  dignity_review = "block"  →  trust_weight = 0.0 (exact zero, no minimum)

All calculations are deterministic. No external I/O. No randomness.

Public API:
  compute_days_since(timestamp_str, reference_date=None) → float
  compute_decay_factor(days_since, half_life_days=90)    → float
  compute_continuity_multiplier(contribution_count)       → float
  compute_trust_weight(event, reference_date=None, half_life_days=90, contribution_count=1)
    → dict
  trust_level(trust_weight)   → "high" | "medium" | "low" | "blocked"
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Optional

# ── Constants ─────────────────────────────────────────────────
HALF_LIFE_DAYS  = 90.0   # default half-life for trust decay
MIN_WEIGHT      = 0.05   # floor; contributions never completely vanish
MAX_CONTINUITY  = 1.5    # anti-cartel cap on continuity bonus
CONTINUITY_STEP = 0.1    # bonus per additional accepted contribution

# Thresholds for human-readable trust level
THRESHOLD_HIGH   = 0.7
THRESHOLD_MEDIUM = 0.3

VERIFICATION_MULTIPLIERS: dict[str, float] = {
    "verified":      1.2,
    "self_reported": 1.0,
    "disputed":      0.6,
}

DIGNITY_MULTIPLIERS: dict[str, float] = {
    "pass":     1.0,
    "escalate": 0.8,
    "block":    0.0,
}

# Contribution event types whose trust weight is meaningful
CONTRIBUTION_EVENT_TYPES = frozenset({
    "contribution_accepted",
    "contribution_completed",
    "contribution_offer",
})


# ── Timestamp parsing ──────────────────────────────────────────

def _parse_ts(ts: str) -> datetime:
    """Parse ISO 8601 timestamp (with or without Z) to UTC datetime."""
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)


# ── Core computation functions ─────────────────────────────────

def compute_days_since(
    timestamp_str: str,
    reference_date: Optional[datetime] = None,
) -> float:
    """
    Return fractional days elapsed between timestamp_str and reference_date.
    reference_date defaults to now (UTC).
    Returns 0.0 if timestamp is in the future.
    """
    if reference_date is None:
        reference_date = datetime.now(timezone.utc)
    if not timestamp_str:
        return 0.0
    event_dt = _parse_ts(timestamp_str)
    delta_seconds = (reference_date - event_dt).total_seconds()
    return max(0.0, delta_seconds / 86400.0)


def compute_decay_factor(
    days_since: float,
    half_life_days: float = HALF_LIFE_DAYS,
) -> float:
    """
    Time-decay factor.

    Formula: max(MIN_WEIGHT, 0.5 ^ (days_since / half_life_days))

    The minimum floor (0.05) ensures ancient contributions are still
    visible in coordination memory — just with a very weak signal.
    """
    if half_life_days <= 0:
        raise ValueError(f"half_life_days must be > 0, got {half_life_days}")
    raw = 0.5 ** (days_since / half_life_days)
    return max(MIN_WEIGHT, raw)


def compute_continuity_multiplier(contribution_count: int) -> float:
    """
    Continuity bonus for contributors who return multiple times.

    Formula: min(MAX_CONTINUITY, 1.0 + CONTINUITY_STEP × (count − 1))

    The cap (1.5) prevents reputation cartel formation:
    frequent contributors are recognised, but not infinitely privileged.

    count=1 → 1.0   (no bonus)
    count=2 → 1.1
    count=3 → 1.2
    ...
    count=6 → 1.5   (capped)
    """
    count = max(1, int(contribution_count))
    raw = 1.0 + CONTINUITY_STEP * (count - 1)
    return round(min(MAX_CONTINUITY, raw), 4)


def compute_trust_weight(
    event: dict,
    reference_date: Optional[datetime] = None,
    half_life_days: float = HALF_LIFE_DAYS,
    contribution_count: int = 1,
) -> dict:
    """
    Compute the full trust weight for a single contribution event.

    Returns a dict with all component values plus a summary trust_weight.

    The dignity multiplier is the only true zero:
      dignity_review = "block" → trust_weight = 0.0 exactly.
      All other situations: trust_weight >= MIN_WEIGHT.

    Args:
      event              — su-table event dict
      reference_date     — UTC datetime to compute decay against (default: now)
      half_life_days     — decay half-life in days (default: 90)
      contribution_count — total accepted contributions from this contributor
                           to this claim (for continuity multiplier)
    """
    timestamp          = event.get("timestamp", "")
    verification_status = event.get("verification_status", "self_reported")
    dignity_review      = event.get("dignity_review", "")

    # Resolve dignity_review from dignity_cleared if explicit field absent
    if dignity_review not in DIGNITY_MULTIPLIERS:
        dignity_cleared = event.get("dignity_cleared")
        if dignity_cleared is True:
            dignity_review = "pass"
        elif dignity_cleared is False:
            dignity_review = "block"
        else:
            dignity_review = "pass"

    days_since   = compute_days_since(timestamp, reference_date)
    decay_factor = compute_decay_factor(days_since, half_life_days)

    v_mult   = VERIFICATION_MULTIPLIERS.get(verification_status, 1.0)
    d_mult   = DIGNITY_MULTIPLIERS.get(dignity_review, 1.0)
    c_mult   = compute_continuity_multiplier(contribution_count)
    base_w   = 1.0

    raw_trust = base_w * decay_factor * v_mult * d_mult * c_mult

    # Dignity block is an absolute zero — minimum floor does NOT apply
    if d_mult == 0.0:
        trust_weight = 0.0
    else:
        trust_weight = max(MIN_WEIGHT, raw_trust)

    return {
        "trust_weight":            round(trust_weight, 4),
        "base_weight":             round(base_w, 4),
        "decay_factor":            round(decay_factor, 4),
        "verification_multiplier": round(v_mult, 4),
        "dignity_multiplier":      round(d_mult, 4),
        "continuity_multiplier":   round(c_mult, 4),
        "days_since_event":        round(days_since, 1),
        "half_life_days":          half_life_days,
        "verification_status":     verification_status,
        "dignity_review":          dignity_review,
        "contribution_count":      contribution_count,
    }


def trust_level(weight: float) -> str:
    """
    Return a human-readable tier string for a trust weight.

      ≥ 0.7  → "high"
      ≥ 0.3  → "medium"
      > 0.0  → "low"
        0.0  → "blocked"   (dignity violation)
    """
    if weight == 0.0:
        return "blocked"
    if weight >= THRESHOLD_HIGH:
        return "high"
    if weight >= THRESHOLD_MEDIUM:
        return "medium"
    return "low"
