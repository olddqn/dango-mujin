"""
voice_reader.py — Phase H-1: read Mujin voice records (READ-ONLY).

The Voice Reader observes voices. It does not decide their meaning and does
not define a Need. Input: bridge/mujin/data/voice_records.jsonl (read-only).
The Observation Builder turns these into Observation Candidates.

"Voice is not Need." "Observation is not decision."

CLI:
  python -m bridge.agent_commons.runtime.voice_reader
"""

from __future__ import annotations

from typing import Any

from .store import MUJIN_VOICE_RECORDS, read_jsonl


def read_voice_records() -> list[dict[str, Any]]:
    """Read Mujin voice records. Read-only — this layer never writes them."""
    return read_jsonl(MUJIN_VOICE_RECORDS)


def main() -> None:
    voices = read_voice_records()
    print("=" * 64)
    print("HERMES VOICE READER — read-only over Mujin voice records")
    print('  "Voice is not Need." "Observation is not decision."')
    print("=" * 64)
    print(f"  source: {MUJIN_VOICE_RECORDS}")
    print(f"  voices read: {len(voices)}")
    for v in voices:
        print(f"    {v.get('voice_id','?')} | {v.get('source_type','?')} | "
              f"{v.get('title', v.get('original_statement',''))[:48]}")
    print("-" * 64)
    print("Read-only. No Need defined. No Mujin file modified.")


if __name__ == "__main__":
    main()
