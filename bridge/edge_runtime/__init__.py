"""
Edge Runtime — shared foundation for the two Edge routes (F-9..F-25).

    Voice → Observed Edge → Edge Runtime ├── Route A (Findability)
                                          └── Route B (Gateway Support)

The Edge Runtime owns the concepts both routes share — edge records, edge memory,
edge audit, and edge reporting — so neither route duplicates them. It enforces
the universal edge floor: authority none · advisory only · human review required ·
Person Domain sealed · no need inference · no ranking · no recommendation ·
no selection · no reach-gap estimation · no Saiyan Scouter behaviour · append-only.

Route-specific guarantees (Resource Acceptance / TTFR-G separation for Route B;
observation-only / no-outreach for Route A) extend this floor in each route.
"""
