# Normalize every engagement metric to partner size, and state the comparison baseline

**Status:** Pattern

**Domain:** Learning analytics / Metric interpretation

**Applies to:** `edtech-partner-success`

---

## Why this exists

Two metric defects quietly mislead a PSM book. The first is absolute counts: "12,000 logins this month" hides a per-capita collapse in a large district and overstates a small one — a 30-school district and a 2-school district are not comparable on raw totals, so a real decline in a big partner can look like growth. The second is the missing baseline: "engagement is up 18%" is unanswerable until you say *up versus what* — last quarter (am I trending?), the cohort (am I average?), or the onboarding target (am I where the success plan said I'd be?). Those are three different questions with three different answers, and a number without its baseline gets the PSM asked the question they can't answer in the next touchpoint (house opinion §3 #12 — provenance on every claim). The anti-pattern hook flags an unverified numeric claim, and the QBR rule treats the baseline as not optional.

## How to apply

Normalize to partner size before comparing, attach a named baseline to every percentage, and carry the source query and date range with it.

```
Metric-hygiene contract (every engagement number the PSM acts on or presents):
  NORMALIZE  — per-capita / % of active roster, not absolute totals.
               (active-teacher % within a school WoW, not "total logins")
               normalize before any cross-partner or cross-school comparison.
  BASELINE   — state which one, explicitly:
               vs prior quarter   → trending?
               vs cohort (≥10)    → average?  (sub-10 cohort = noise; use segment baseline)
               vs onboarding target → on plan?
  PROVENANCE — source query + date range + the baseline travel WITH the number.
               "up 18%" alone is a §4 anti-pattern; "up 18% vs prior quarter,
               query X, Jan 1-Mar 31" is a claim.
  VANITY GUARD — if a metric can move UP while the partner is failing, it's vanity
               (total logins / sessions / clicks). Keep it off the PSM dashboard.
```

**Do:**
- Make the composite drillable — the PSM clicks "yellow" and sees the 2-3 normalized components that moved.
- Apply the calendar dead-zone overlay before reading a drop as real (a December or testing-window dip is not a per-capita decline).

**Don't:**
- Run a cohort comparison on fewer than 10 partners — variance swamps the signal; use the segment baseline instead.
- Present "up X%" without the baseline, the source query, and the range — the partner (or the CFO) will ask.

## Edge cases / when the rule does NOT apply

- **Single-school or single-seat partners** — per-capita and absolute converge; normalization is a no-op, but the baseline rule still holds.
- **Outcome metrics the buyer mandates in absolute terms** (e.g., "X students must complete Y") — present against the mandate's own denominator, not a per-capita rate.
- **Brand-new instrumentation with no prior quarter and no cohort** — the only honest baseline is the onboarding target; say so rather than inventing a comparison.

## See also

- [`./health-design-leading-not-lagging-signals.md`](./health-design-leading-not-lagging-signals.md) — normalization keeps leading signals from hiding per-capita decline
- [`./qbr-open-with-partner-outcomes-not-product-features.md`](./qbr-open-with-partner-outcomes-not-product-features.md) — the QBR consumer of the baseline rule
- [`../knowledge/psm-metrics-glossary.md`](../knowledge/psm-metrics-glossary.md) — formulas, pitfalls, the vanity-metric overlay, the decision-aid lookup
- [`../agents/learning-analytics-analyst.md`](../agents/learning-analytics-analyst.md) — owns metric definition, normalization, and baselines

## Provenance

Distilled from `agents/learning-analytics-analyst.md` (normalize-to-partner-size, comparison-baselines, vanity-metric guard, cohort ≥10, show-your-work), `knowledge/psm-metrics-glossary.md` (vanity pitfalls, decision-aid), the anti-pattern hook (§7 unverified-numeric-claim check), and house opinion §3 #12 + §4. Authored 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
