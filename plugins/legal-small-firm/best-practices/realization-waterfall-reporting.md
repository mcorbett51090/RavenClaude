# Report Realization as a Waterfall, Not a Single Number

**Status:** Absolute rule
**Domain:** Small-firm legal practice
**Applies to:** `legal-small-firm`

---

## Why this exists

A single "realization rate" figure is almost always ambiguous: it may mean billed-hours ÷ standard-value, collected ÷ billed, or collected ÷ standard-value. The distinction matters enormously for diagnosis — a 70% collected realization that comes from 95% billed / 74% collected points to a collection problem; one that comes from 74% billed / 95% collected points to a billing-judgment problem. Without the waterfall, the attorney picks the wrong lever.

## How to apply

Structure every realization report as a waterfall with explicit stage labels:

```
Stage                           Amount       Rate
─────────────────────────────────────────────────
Standard-rate value (billable)   $  X        100%
  Less: write-downs at billing   $ (D)
Billed A/R                       $  B         B/X  ← Billed realization
  Less: A/R write-offs            $ (O)
  Less: A/R discount / settlement $ (S)
Collected revenue                 $  C         C/X  ← Collected realization
                                               C/B  ← Collection rate on billed
```

Report each stage with a trailing 12-month window and a same-period prior-year baseline.

**Do:**
- Label each rate explicitly (billed realization, collection rate, collected realization).
- Include the dollar amounts, not just percentages — a 90% rate on a $40 k matter is a $4 k gap, which is material for a solo practice.
- Flag when the window crosses a seasonal change (e.g., a year when a major matter closed distorts the trailing 12).

**Don't:**
- Report a single percentage and call it "realization."
- Average across matter types without noting the mix — a litigation practice and a transactional practice in the same waterfall hide each segment's true rate.
- Present the waterfall without the prior-period baseline. A number without a comparison is not a finding.

## Edge cases / when the rule does NOT apply

For a purely contingency practice, there are no billable hours; the analog is fee-earned ÷ standard-value-of-time-invested, tracked post-settlement. The waterfall concept still applies but the inputs differ.

## See also

- [`../agents/legal-operations-analyst.md`](../agents/legal-operations-analyst.md) — owns realization reporting and the scorecard.
- [`./write-down-write-off-discipline.md`](./write-down-write-off-discipline.md) — companion rule distinguishing the two adjustment types that feed the waterfall.

## Provenance

Codifies CLAUDE.md §3 #1 (realization, not billed hours, is the practice's truth) and §3 #7 (collections are part of the matter). Thomson Reuters / Clio Benchmarking surveys use this waterfall structure; it is the standard small-firm practice management framing.

---

_Last reviewed: 2026-06-05 by `claude`_
