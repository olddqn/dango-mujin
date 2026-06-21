#!/usr/bin/env python3
"""Pre-push guard: refuse to expose real, unconsented voice data publicly.

Scans tracked public data files (bridge/mujin/data/*.jsonl) for voice records
that are neither fixtures nor public-safe (gateway_consent / public_safe), and
blocks any tracked file under bridge/mujin/data/private/. Fail-closed.

Run by .githooks/pre-push. Override (deliberate, audited): VOICE_GUARD_OVERRIDE=1
"""
from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

PLACEHOLDER = {"example.org", "example.com", "example.net",
               "ngo.example", "gov.example", ""}
PUBLIC_DATA = sorted(glob.glob("bridge/mujin/data/*.jsonl"))  # private/ is a subdir, excluded


def is_voice(r: dict) -> bool:
    return r.get("record_type") == "voice_record" or bool((r.get("original_statement") or "").strip())


def is_fixture(r: dict) -> bool:
    if r.get("is_fixture") is True:
        return True
    u = r.get("source_url") or ""
    d = urlparse(u).netloc.lower().replace("www.", "") if u else ""
    return d in PLACEHOLDER


def is_public_safe(r: dict) -> bool:
    return is_fixture(r) or r.get("gateway_consent") is True or r.get("public_safe") is True


def main() -> int:
    violations: list[str] = []
    for f in PUBLIC_DATA:
        for i, line in enumerate(Path(f).read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if is_voice(r) and not is_public_safe(r):
                violations.append(
                    f"{f}:{i} voice_id={r.get('voice_id')} (real/unconsented voice in public file)")
    # private/ may exist on disk (sealed, gitignored); it must never be TRACKED.
    try:
        tracked = subprocess.run(
            ["git", "ls-files", "bridge/mujin/data/private/"],
            capture_output=True, text=True, check=False).stdout.split()
    except Exception:
        tracked = []
    for f in tracked:
        violations.append(f"{f} (private voice data is TRACKED — must never be tracked/pushed)")
    if violations:
        sys.stderr.write("VOICE EXPOSURE GUARD: push refused.\n")
        for v in violations:
            sys.stderr.write("  - " + v + "\n")
        sys.stderr.write(
            "Fix: move to fixtures/ (is_fixture) or private/, or set gateway_consent after consent.\n")
        sys.stderr.write("Override (deliberate, audited): VOICE_GUARD_OVERRIDE=1\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(0 if os.environ.get("VOICE_GUARD_OVERRIDE") == "1" else main())
