"""
Gateway Support Runtime (Route B) for Dan-Go/Mujin.

Implements the observation-only Gateway Support pipeline specified by F-9..F-20:

  Observed Edge → Verified Bottleneck → Support Candidate → Approval →
  Gateway Consent → Support Execution → Reality Feedback → TTFR-G Accounting →
  Withdrawal → Support Memory

It does NOT implement: Person Relief, Need inference, Ranking, Recommendation,
Selection, Auto-execution, Cooperation assignment, Gateway profiling/scoring/
reputation, or Reach Gap estimation.

Invariants (always preserved):
  Person Domain sealed · Gateway Support only · Resource Acceptance layer only ·
  Verified = observable condition (not proof) · Candidate = possibility only ·
  Approval = gatekeeping only · Gateway Consent required · TTFR-G ⟂ TTFR-P ·
  Withdrawal always possible · no ranking/recommendation/auto-execution ·
  human review before action · append-only memory.
"""
