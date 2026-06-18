"""
observation_builder.py — Phase H-1: Observation Classifier.

Turns Mujin voices into Observation Candidates. An Observation is NOT a Need.
Hermes observes; it does not define what anyone needs. Every observation is
candidate-only, human-confirmation-required, and contestable.

Also acts as Gateway Gap Observer: it may note gap-1 (subject → gateway) and
gap-2 (gateway → Mujin), but it decides no solution.

"Voice is not Need." "Observation is not decision."

CLI:
  python -m bridge.agent_commons.runtime.observation_builder
"""

from __future__ import annotations

from typing import Any

from .store import (
    OBSERVATION_JSONL, append_jsonl, base_invariants, next_id, read_jsonl,
)
from .voice_reader import read_voice_records

# observation vocabulary (the spec's examples)
VOICE_TYPES = ["gateway_voice", "direct_voice", "public_call", "intermediary_voice"]

# keyword → observed bottleneck (advisory observation, never a need definition)
_BOTTLENECK_KEYWORDS = {
    "funding":     ["資金", "寄付", "募金", "funding", "donation", "donate", "緊急資金"],
    "volunteer":   ["ボランティア", "volunteer", "人手", "人材", "担い手"],
    "translation": ["翻訳", "通訳", "translation", "言語", "language"],
    "legal":       ["法的", "法律", "legal", "在留", "難民申請"],
    "housing":     ["住居", "住まい", "housing", "shelter", "避難先"],
    "medical":     ["医療", "medical", "health", "診療"],
    "food":        ["食料", "食事", "food", "炊き出し"],
    "education":   ["教育", "education", "学習", "就学"],
    "employment":  ["就労", "雇用", "employment", "仕事"],
}

_ORG_SIGNAL_SOURCES = {"NGO Report", "Government Report", "ngo_report",
                       "government_report"}
_PUBLIC_SOURCES = {"News Report", "news_report", "public_appeal",
                   "public_interview", "public_statement", "public_video",
                   "public_social_media", "refugee_appeal", "disaster_appeal"}


def _text_of(v: dict[str, Any]) -> str:
    return " ".join(str(v.get(k, "")) for k in
                    ("title", "original_statement", "description")) + \
           " " + " ".join(v.get("tags", []) or [])


def classify(voice: dict[str, Any]) -> dict[str, Any]:
    """Classify a voice into an Observation (advisory, contestable).

    Determines voice_type, whether the need-owner appears present, observed
    bottlenecks, and a gap observation. Defines NO need.
    """
    text = _text_of(voice)
    tags = set(voice.get("tags", []) or [])
    src = voice.get("source_type", "")
    basis: list[str] = []

    is_org = (src in _ORG_SIGNAL_SOURCES) or bool(
        tags & {"organization_level", "public_appeal", "intermediary"})
    is_public = (src in _PUBLIC_SOURCES) or ("public_appeal" in tags)

    if is_org:
        voice_type = "gateway_voice"
        basis.append(f"source/tags indicate an organisation/connector ({src})")
        need_owner_present = False
    elif src in {"refugee_appeal", "disaster_appeal", "public_interview"}:
        voice_type = "direct_voice"
        basis.append(f"source suggests a first-person public appeal ({src})")
        need_owner_present = True
    elif is_public:
        voice_type = "public_call"
        basis.append(f"public source without clear first-person author ({src})")
        need_owner_present = False
    else:
        voice_type = "intermediary_voice"
        basis.append(f"relayed/unclassified source ({src})")
        need_owner_present = False

    bottlenecks = sorted(
        b for b, kws in _BOTTLENECK_KEYWORDS.items()
        if any(k.lower() in text.lower() for k in kws))

    if voice_type in ("gateway_voice", "intermediary_voice", "public_call"):
        gap = {
            "gap_1_subject_to_gateway": "unobserved (occurs outside Mujin)",
            "gap_2_gateway_to_mujin": "bridged by this voice record",
            "note": "Mujin touched the outer layer (gap-2); the individual "
                    "remains behind gap-1, unobserved.",
        }
    else:
        gap = {
            "gap_1_subject_to_gateway": "n/a (apparent first-person voice)",
            "gap_2_gateway_to_mujin": "direct",
            "note": "Apparent direct voice; still requires human review and consent.",
        }

    return {
        "voice_type": voice_type,            # advisory classification, contestable
        "voice_type_basis": basis,
        "need_owner_present": need_owner_present,   # observation, not a fact
        "observed_bottleneck": bottlenecks,         # observed, not a need
        "gap_observation": gap,
    }


def _already_observed() -> set[str]:
    return {o.get("source_voice_id") for o in read_jsonl(OBSERVATION_JSONL)}


def build() -> list[dict[str, Any]]:
    """Build Observation Candidates for voices not yet observed (idempotent)."""
    done = _already_observed()
    created = []
    for v in read_voice_records():
        vid = v.get("voice_id")
        if not vid or vid in done:
            continue
        obs = classify(v)
        record = {
            "record_type": "observation_candidate",
            "observation_id": next_id("obs", OBSERVATION_JSONL),
            "source_voice_id": vid,
            "source_url": v.get("source_url", ""),
            **obs,
            "note": "Observation is not Need. This describes what is observable "
                    "in the voice; it does not define anyone's need.",
            "candidate_only": True,
            "human_confirmation_required": True,
            "voice_is_not_need": True,
            "observation_is_not_decision": True,
            "defines_need": False,
            "selects_gateway": False,
            **base_invariants(),
        }
        created.append(append_jsonl(OBSERVATION_JSONL, record))
        done.add(vid)
    return created


def main() -> None:
    print("=" * 64)
    print("HERMES OBSERVATION BUILDER — voices → observation candidates")
    print('  "Observation is not Need." advisory · contestable · human-confirmed')
    print("=" * 64)
    created = build()
    if not created:
        print("  (no new voices to observe — append-only, idempotent)")
    for o in created:
        print(f"  ✓ {o['observation_id']} ← {o['source_voice_id']} | "
              f"type={o['voice_type']} | need_owner_present={o['need_owner_present']} "
              f"| bottleneck={o['observed_bottleneck']}")
    print("-" * 64)
    print("No Need defined. No Gateway selected. No Mujin/Dan-Go file modified.")


if __name__ == "__main__":
    main()
