# Submittal-to-Fill Ratio Is the Funnel Quality Metric

**Status:** Pattern
**Domain:** Staffing operations
**Applies to:** `staffing-operations`

---

## Why this exists

Fill rate measures the outcome; submittal-to-fill ratio measures the efficiency of the path to that outcome. A desk that submits 12 candidates per placement is doing three times the work of a desk that submits 4 — and is probably providing worse service to the client (quality of submittals is low) while consuming more recruiter capacity than necessary. Submittal-to-fill ratio is the KPI that exposes funnel quality: too high means submittals are untargeted; too low may signal the firm isn't submitting enough to compete.

## How to apply

Track and report submittal-to-fill ratio alongside fill rate in every funnel analysis:

```
Submittal-to-Fill Ratio KPI
──────────────────────────────
Definition:  Total submittals ÷ placements made in the period
             (submittals = clinician profiles sent to the client facility for a specific order)

Period:  ________________
Segment:  ________________
Division / desk:  ________________

Submittals in period:   ___
Placements in period:   ___
Submittal-to-fill ratio: ___:1

Benchmark range:
  Travel nursing:   4:1–6:1 is healthy; >8:1 suggests quality issues or order difficulty
  Allied health:    5:1–8:1 (longer credentialing time inflates denominator)
  Per-diem:         3:1–5:1 (faster decisions)
  School-based:     6:1–10:1 (longer district decision cycles)
  [ESTIMATE — calibrate to firm's own historical baseline]

Segmentation:
  Ratio by order type (new vs. renewal):  ___  /  ___
  Ratio by facility tier (MSP vs. direct): ___  /  ___
  Ratio by recruiter (for performance benchmarking):  per recruiter table

Diagnostic:
  Ratio trending up:  submittal quality may be declining; or client selection criteria tightening
  Ratio trending down:  submittals becoming more targeted; or placements concentrating in easy fills
```

**Do:**
- Calculate the ratio at the recruiter level as well as the desk level — a recruiter with a 12:1 ratio vs. a desk average of 5:1 is either working harder orders or submitting untargeted candidates.
- Separate new-order submittals from renewal/extension submittals — renewals typically convert at a much higher rate and should not be blended into the quality read.
- Combine with time-to-fill to get a complete funnel picture: high submittal-to-fill + slow time-to-fill = both quality and speed problems.

**Don't:**
- Use submittal-to-fill ratio as a standalone performance metric without context — order difficulty (rural, hard-to-fill specialty, low bill rate) legitimately inflates the ratio.
- Target a ratio of 1:1 — some redundancy in submittals is the normal buffer against candidate drop-off; the goal is appropriate efficiency, not zero waste.
- Compare ratios across segments without acknowledging their structurally different ranges.

## Edge cases / when the rule does NOT apply

VMS/MSP-managed programs with automated submittal scoring may have different numerator definitions (only compliant submittals count); confirm the VMS definition before calculating the ratio against the standard definition.

## See also

- [`../agents/recruiting-funnel-strategist.md`](../agents/recruiting-funnel-strategist.md) — owns the funnel metrics including submittal-to-fill and conversion-stage analysis.
- [`./pair-fill-rate-with-time-to-fill.md`](./pair-fill-rate-with-time-to-fill.md) — submittal-to-fill is the third metric that completes the fill-rate / TTF pair.

## Provenance

Codifies CLAUDE.md §3 #2 (time-to-fill and fill rate are a pair) extended to the submittal-to-fill funnel quality metric. Submittal-to-fill ratio is a recognized staffing funnel metric in operations consulting and is tracked in most enterprise ATS platforms [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
