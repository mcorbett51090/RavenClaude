# Segment Before You Analyze Retention

**Status:** Primary diagnostic
**Domain:** Product metrics / retention
**Applies to:** `product-management`

---

## Why this exists

An aggregate retention curve is a weighted average of multiple underlying retention patterns, and the average is almost always misleading. A cohort that retains at 55% on Day 30 may contain a segment retaining at 80% and a segment retaining at 20% — and these two segments have entirely different root causes, fixes, and strategic implications. The 80% segment may be the signal that points toward the product's true customer; the 20% segment may be the result of mis-acquired users who never should have been onboarded. An un-segmented retention analysis produces a single number that justifies both "it's not that bad" and "it's really bad" interpretations simultaneously — and neither interpretation leads to a useful decision.

## How to apply

Before drawing any retention conclusion, segment the cohort by at least two dimensions.

```
Retention Segmentation — Minimum Dimensions
──────────────────────────────────────────────────────
Segment by acquisition source first:
  Organic / direct vs. paid / referral vs. sales-assisted
  (Acquired users have different activation profiles; mixing them obscures both)

Then by behavior in the first session:
  Users who reached the activation moment vs. those who didn't
  (This is the most predictive segmentation for retention — validate empirically)

Then by plan tier / use case / persona (if available):
  Solo vs. team; free vs. paid; use case A vs. use case B

For each segment, report:
  Day-7, Day-30, Day-90 retention curve
  Sample size (note if < 100 — statistically thin)
  Activation rate for this segment

Retention segmentation table structure:
  Segment | N (cohort) | Day-7 ret | Day-30 ret | Day-90 ret | Activation rate
  ──────────────────────────────────────────────────────────────────────────────
  Source: organic        | 450 | 62% | 48% | 35% | 74%
  Source: paid           | 280 | 44% | 31% | 20% | 51%
  Activated              | 520 | 71% | 58% | 43% | 100%
  Not activated          | 210 |  9% |  6% |  3% | 0%
```

**Do:**
- Start the segmentation with the activation split — it is almost always the highest-signal segmentation for retention.
- Note sample sizes explicitly; a retention curve on 30 users is noise, not signal.
- Report the segmented curves to the team before the aggregate — the segment that retains well is the product insight; the aggregate is the average.

**Don't:**
- Run retention optimization experiments on unsegmented cohorts; the treatment effect is averaged across segments and may be positive for one and negative for another.
- Use retention percentages without cohort sizes in a stakeholder report — "Day-30 retention is 55%" without a denominator invites projection and misleads.
- Conclude from a rising aggregate retention curve that all segments are improving; one improving segment can mask a declining one.

## Edge cases / when the rule does NOT apply

- **Very early stage** (fewer than 100 users total) — segmentation produces samples too small to interpret; run aggregate analysis and note the limitation explicitly.
- **Single-use or transactional products** (e.g., a tax-filing product used once a year) — the retention metric is annual return-to-file, not a weekly curve; segment by return vs. churn, not by time-to-retention.

## See also

- [`../agents/product-metrics-analyst.md`](../agents/product-metrics-analyst.md) — owns retention analysis, cohort segmentation, and the funnel diagnostic.
- [`./activation-is-the-first-metric-to-fix.md`](./activation-is-the-first-metric-to-fix.md) — the activation split is the most important segmentation for retention; this rule is the analysis method, that rule is the prioritization principle.

## Provenance

Codifies the product-metrics-analyst's retention segmentation discipline from the product-management plugin's CLAUDE.md §2 #5 (North Star with input metrics; not vanity metrics) and §1 (product-metrics-analyst: "funnel/retention/activation analysis framing"). The activation-split-first segmentation approach reflects standard growth analytics practice (Reforge, Amplitude, Mixpanel best practices).

---

_Last reviewed: 2026-06-05 by `claude`_
