# Loss Triangle Development Reveals Reserve Direction — Read It Before Opining on Reserves

**Status:** Primary diagnostic
**Domain:** Actuarial / reserving
**Applies to:** `insurance-pc`

---

## Why this exists

A reserve adequacy opinion stated without reviewing the historical loss development triangle is an opinion stated without evidence. The triangle shows whether losses on prior accident years are developing favorably (closing below reserve) or adversely (emerging above reserve) — and whether that trend is accelerating. Adverse development that is consistent across multiple accident years and development periods is a signal of systematic reserve inadequacy, not random noise. An analyst who concludes "reserves look adequate" based on current-period incurred loss ratios, without reading what prior-year triangles are doing, has committed the most common reserving error in portfolio analysis.

## How to apply

Before opining on reserve adequacy, read the paid and incurred development triangles for at least 5 accident years.

```
Loss Triangle Diagnostic — What to Look For
──────────────────────────────────────────────────────
Step 1 — BUILD OR OBTAIN THE TRIANGLE
  Rows = accident years (most recent 5–10 at minimum)
  Columns = development periods (12, 24, 36, 48... months)
  Show both paid and incurred (case reserve + IBNR) triangles separately.

Step 2 — COMPUTE LINK RATIOS (LDFs)
  LDF_n = Column n+1 total ÷ Column n total
  Volume-weighted LDF is the default; document if using a different selection.

Step 3 — LOOK FOR PATTERNS (red flags)
  □ Diagonal effects — a recent diagonal (the most-recent evaluation)
    that is materially higher than the prior 3-diagonal average signals
    a reserve strengthening or a new loss emergence.
  □ Increasing LDFs at older periods — unusual; signals re-opening of
    settled claims (social inflation, litigation) or case-reserve adequacy issue.
  □ Paid-vs-incurred divergence — if paid is developing slower than incurred,
    claims are not closing; open-count growth is the explanation to test.
  □ Consistent favorability — if the most recent 3 accident years all show
    favorable development at 24 months, the IBNR may be conservative (over-reserved).

Step 4 — SUMMARIZE DIRECTION
  For each accident year: favorable / on-trend / adverse / insufficient data
  Overall direction: reserve appears adequate / needs strengthening / uncertain
```

**Do:**
- Compare LDFs to the carrier's own historical selected factors — the triangle shows where actual vs. expected diverges.
- Note the most recent accident year separately; it has the least development and highest uncertainty, and its LDF is the most volatile.
- If the triangle shows adverse development in the most recent 2+ accident years, raise a reserve-strengthening discussion before the analysis proceeds to the combined ratio.

**Don't:**
- Accept a management assertion of "reserves are adequate" without looking at the triangle; the triangle is the evidence.
- Extrapolate from a single development period; look for pattern consistency across at least 3 periods and 3 accident years before drawing a directional conclusion.
- Ignore the paid triangle in favor of only the incurred triangle — the gap between the two reveals case-reserve adequacy and settlement behavior.

## Edge cases / when the rule does NOT apply

- **Short-tail lines** (property, inland marine with rapid settlement) — development beyond 24 months is minimal; a shorter triangle (3 accident years, 2–3 development periods) may be sufficient, but the rule still requires reading it.
- **New programs with fewer than 3 accident years** — a triangle cannot be constructed; document the limitation and rely on industry benchmarks and the underwriting guidelines to assess adequacy, flagging the inherent uncertainty.

## See also

- [`../agents/actuarial-pricing-analyst.md`](../agents/actuarial-pricing-analyst.md) — owns loss development, triangle diagnostics, and reserve direction analysis.
- [`./reserve-adequacy-is-the-truth-teller.md`](./reserve-adequacy-is-the-truth-teller.md) — the upstream house opinion that establishes why reserve adequacy is the foundational diagnostic; this doc operationalizes the triangle-reading discipline.

## Provenance

Codifies the actuarial-pricing-analyst's triangle-diagnostic discipline from the insurance-pc plugin's CLAUDE.md §3 #5 (reserve adequacy is the truth-teller) and the `knowledge/pc-underwriting-economics.md` file. The paid/incurred triangle structure, LDF computation, and red-flag patterns reflect standard CAS reserving practice.

---

_Last reviewed: 2026-06-05 by `claude`_
