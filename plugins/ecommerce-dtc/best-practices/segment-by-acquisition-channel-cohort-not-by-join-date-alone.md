# Segment by acquisition-channel cohort, not by join-date alone

**Status:** Pattern
**Domain:** DTC retention and analytics
**Applies to:** `ecommerce-dtc`

---

## Why this exists

A join-date cohort mixes customers acquired through organic social, paid Meta, influencer, and email referral — each with radically different LTV trajectories. When retention or LTV looks "fine" in a blended cohort, an expensive paid channel is often hiding behind a strong organic one. Reading channel-sourced cohorts separately reveals which acquisition bets are actually compounding and which are eroding contribution margin over time.

## How to apply

Build cohort retention tables with two dimensions: acquisition month AND acquisition channel (or channel cluster). Identify the channel-sourced cohorts first; only roll up to a blended view after you understand the composition.

```
Cohort: 2025-Q4 | Channel: Meta Paid
  Month 0 revenue: $82k | Repeat rate M3: 18%
  LTV @ 12m: $67 | CAC: $52 → LTV:CAC 1.3:1 ❌

Cohort: 2025-Q4 | Channel: Email Referral
  Month 0 revenue: $31k | Repeat rate M3: 42%
  LTV @ 12m: $138 | CAC: $14 → LTV:CAC 9.9:1 ✅
```

**Do:**
- Always include channel as a cohort dimension when building retention analysis.
- Flag any blended cohort result that masks a channel with LTV:CAC below 2:1.
- Use channel-cohort LTV — not blended CAC — as the input to channel budget allocation decisions.

**Don't:**
- Anchor budget decisions on join-date-only cohorts.
- Call a channel "efficient" without checking its cohort's 6-month+ repeat rate.
- Build a retention scorecard that doesn't allow channel-level drill-down.

## Edge cases / when the rule does NOT apply

For brands with a single dominant channel (e.g., > 80% one source), the blended and channel-sourced cohort converge — still worth instrumenting the split for the day the mix diversifies. Early-stage brands with sample sizes below ~200 per channel per month should acknowledge the small-n caveat rather than over-indexing on noisy cohort splits.

## See also

- [`../agents/retention-analytics-analyst.md`](../agents/retention-analytics-analyst.md) — builds the retention scorecard and cohort analysis.
- [`./cac-is-a-blended-lie-read-it-by-channel-and-by-cohort.md`](./cac-is-a-blended-lie-read-it-by-channel-and-by-cohort.md) — the companion rule on the acquisition side.

## Provenance

Codifies the team's §3 #5 house opinion ("CAC is a blended lie — read it by channel and by cohort") applied to the retention side of the unit-economics model — the LTV half of the ratio that the CAC rule governs on the cost side. Standard DTC analytics practice; formalized here because the join-date-only cohort is the dominant error pattern seen in operator-submitted scorecards.

---

_Last reviewed: 2026-06-05 by `claude`_
