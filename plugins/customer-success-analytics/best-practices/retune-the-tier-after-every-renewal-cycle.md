# Retune the health tier after every full renewal cycle

**Status:** Absolute rule
**Domain:** CS analytics — tier maintenance
**Applies to:** `customer-success-analytics`

---

## Why this exists

A health tier tuned against a specific cohort of renewal outcomes will drift. Product changes shift usage baselines; the customer mix changes as the book grows; a new integration adds a signal source that wasn't available when the original thresholds were set. A tier that is never retuned against new outcomes is a tier that is silently degrading — it still looks like it's working until a VP asks "why did three of our top ten accounts churn from Green?" A post-cycle retune is the mechanism that catches drift before it becomes a leadership conversation.

## How to apply

After each full renewal cycle (quarterly for high-velocity books, semi-annually for enterprise-heavy books with long sales cycles):

```
1. Pull the renewal outcomes for the cycle that just completed:
   - Churned accounts that were Red at T-90: True Positives (good)
   - Churned accounts that were Green or Yellow at T-90: False Negatives (misses — highest-value finding)
   - Renewed accounts that were Red at T-90 for the full 90 days: False Positives (CS capacity wasted)

2. For each False Negative (Green account that churned):
   - What were the signal values at T-90?
   - Is there a signal pattern shared across 3+ false negatives?
   - If yes: that pattern is a missing or under-weighted signal — validate it and add it

3. For each cluster of False Positives:
   - Are they concentrated in a segment? → segment override
   - Are they diffuse? → global threshold loosening
   - Did a product change shift the baseline? → recalibrate threshold to new baseline

4. Document the retune:
   - What changed (threshold, signal, segment override)
   - The back-test result that justified the change
   - The version / date of the updated tier rule
```

**Do:**
- Schedule the retune on the calendar at the start of each cycle — it is a maintenance task, not a reactive investigation.
- Treat false negatives (churned Greens) as the primary finding — they are the costliest error and the most valuable improvement opportunity.
- Version the tier rule: each retune produces a new version with the date and the changes documented.

**Don't:**
- Skip the retune because the tier "seems to be working" — silent drift is invisible until it isn't.
- Make threshold changes without a back-test result to justify them.
- Apply a retune finding from one vertical or segment universally without checking for cross-segment impact.

## Edge cases / when the rule does NOT apply

- The book has fewer than 20 completed renewals in the cycle — the sample is too small for a statistically meaningful retune; document the cycle and defer to a combined next-cycle retune.

## See also

- [`../skills/health-tier-design/SKILL.md`](../skills/health-tier-design/SKILL.md) — Step 6 covers the cycle-end back-test procedure
- [`../skills/churn-signal-backtest/SKILL.md`](../skills/churn-signal-backtest/SKILL.md) — the back-test procedure for new signals found during retune
- [`../knowledge/customer-success-decision-trees.md`](../knowledge/customer-success-decision-trees.md) — the retune-or-rebuild decision tree

## Provenance

Codifies `CLAUDE.md` §4 house opinion #1 (transparent rule-based tiering that the CS leader can explain) — a tier the leader can explain at creation loses that property when it drifts unnoticed. The retune cadence is the maintenance mechanism that keeps the rule grounded.

---

_Last reviewed: 2026-06-05 by `claude`_
