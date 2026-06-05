---
scenario_id: 2026-06-05-simpsons-paradox-conversion-reversal
contributed_at: 2026-06-05
plugin: applied-statistics
product: causal-inference
product_version: "n/a"
scope: likely-general
tags: [simpsons-paradox, confounding, aggregation, segmentation, causal]
confidence: medium
reviewed: false
---

## Problem

A marketing lead presented a dashboard showing that **Channel A converts at 6.2% and Channel B at 4.9% in aggregate**, and proposed shifting the entire budget to Channel A. The consultant was asked to sanity-check the read before the reallocation, because the team's own intuition (B drove higher-intent traffic) contradicted the dashboard.

## Context

- Two channels, conversion measured over a quarter, aggregated across two device classes (desktop, mobile).
- The aggregate rates were correct numbers (data-platform had reconciled them) — the question was whether the *conclusion* ("A is better, move the budget") was real.
- Traffic mix differed sharply by channel: Channel B sent a far higher share of **mobile** traffic, which converts lower for *everyone*.

## Attempts

- Tried: the aggregate-vs-subgroup check (pitfall: Simpson's paradox; [`../best-practices/simpsons-paradox-check-aggregate-vs-subgroup.md`](../best-practices/simpsons-paradox-check-aggregate-vs-subgroup.md)). Broke each channel's conversion **down by device** before trusting the aggregate. Illustrative subgroup table `[ESTIMATE]`:

  | | Desktop conv. | Mobile conv. | Mix (desktop / mobile) | Aggregate |
  |---|---|---|---|---|
  | Channel A | 7.0% | 3.5% | 80% / 20% | **6.2%** |
  | Channel B | 7.6% | 4.1% | 35% / 65% | **4.9%** |

  Channel B converts **better within both device classes** (7.6 > 7.0 desktop; 4.1 > 3.5 mobile) — yet loses in aggregate because it carries far more low-converting mobile traffic. The aggregate ranking **reverses** the within-subgroup ranking: textbook Simpson's paradox, driven by **device as a confounder of the channel↔conversion comparison.**

- Tried: identified *why* the reversal happens — the comparison wasn't apples-to-apples because channel and device-mix are entangled. The honest comparison is **within device** (or device-mix-standardized), not the raw aggregate.
- Tried (the move that worked): recomputed a **mix-standardized** conversion (apply a common device mix to both channels' within-device rates) so the channels are compared at the same traffic composition. On a standardized basis **B outperformed A** — the opposite of the dashboard's aggregate. Flagged that this is still *observational* (correlation, not a causal lift) per [`../knowledge/causal-inference-primer.md`](../knowledge/causal-inference-primer.md); a clean read would A/B-test the reallocation.

## Resolution

The aggregate comparison was a **Simpson's-paradox reversal** confounded by device mix: Channel B is better within every device class but looks worse aggregated because it skews mobile. Shifting the budget to A on the aggregate number would have been backwards. The defensible read: compare within the confounder (or standardize the mix), and treat even the corrected ranking as association — confirm a reallocation with a randomized test.

**Action for the next consultant hitting this pattern:** before acting on an aggregate comparison, **break it down by the obvious confounder (device, geo, cohort, time)** and check whether the subgroup ranking matches the aggregate. If they disagree, the aggregate is misleading — compare within the subgroup or standardize the mix. And remember the corrected number is still observational; a budget/treatment decision wants a randomized confirmation (see the causal-inference primer and `assess-causal-claim`).

**Sources for the methods cited:** Simpson's paradox + confounder-conditioning — Pearl, *Causality* (2nd ed., 2009), §6 "Simpson's Paradox"; the aggregate-vs-stratified reversal mechanism — Bickel et al. (1975), "Sex Bias in Graduate Admissions: Data from Berkeley," *Science* 187:398-404 (the canonical real case). Figures are illustrative `[ESTIMATE]`; validate against the engagement's actual data before a deliverable.
