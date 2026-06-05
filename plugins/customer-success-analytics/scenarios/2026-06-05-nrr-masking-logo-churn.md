---
scenario_id: 2026-06-05-nrr-masking-logo-churn
contributed_at: 2026-06-05
plugin: customer-success-analytics
product: retention-metrics
product_version: "n/a"
scope: likely-general
tags: [nrr, grr, logo-churn, expansion-concentration, board-metric]
confidence: medium
reviewed: false
---

## Problem

A board deck led with "NRR is 112% — retention is healthy." Three quarters later the team had lost roughly a fifth of its logos and the leadership was blindsided. The headline NRR had been *true* the whole time — and had been **masking a serious logo-churn problem** behind a handful of expanding accounts.

## Context

- Segment: B2B SaaS, ~250 accounts, meaningful land-and-expand motion on the enterprise tier, a long SMB tail.
- Constraint: only **NRR** was reported. GRR was never on the slide. Expansion was **concentrated** — a small number of large accounts were growing fast enough to lift the net figure above 100% while the SMB tail bled.
- The conflation was the classic one: "the book is net-growing" (NRR's question) was being read as "we're keeping customers" (GRR's question). Those are different metrics answering different questions.

## Attempts

- Tried: computed GRR alongside NRR for the same period (`cs_calc.py retention`). GRR came out in the low-80s% `[ESTIMATE]` against the 112% NRR — a ~30-point gap that was *entirely expansion*. Because GRR caps at 100% and excludes expansion, it exposed the leak the net figure hid. Outcome: the real retention floor became visible for the first time.
- Tried: decomposed the expansion to test concentration. A few large accounts drove most of it; strip them and NRR fell below 100%. Outcome: reframed "healthy retention" as "a churn problem subsidized by a few whales" — a fragility, not a strength (if one whale leaves, the masking evaporates).
- Tried: changed the board metric to **always show NRR and GRR together**, plus an expansion-concentration note, and added a logo-retention line so dollar-NRR couldn't hide unit churn. Outcome: the next deck surfaced the SMB-tail churn as a named problem with a CS motion attached, instead of a surprise.

## Resolution

NRR ≥ 100% is not proof of healthy retention — it can sit on top of significant churn whenever expansion (especially **concentrated** expansion) outweighs the loss. **GRR caps at 100% and is the honest retention floor**; the NRR-minus-GRR gap *is* the expansion contribution, and a wide gap driven by a few accounts is a risk, not a win. The fix was reporting discipline: surface both, every time, with concentration context — never NRR alone.

**Action for the next consultant hitting this pattern:** when someone celebrates NRR, **ask for GRR in the same breath.** If GRR is materially below NRR, expansion is carrying the number — check whether it's broad-based (real growth) or whale-concentrated (masked churn). Add a logo-retention line so dollar expansion can't hide unit loss. Use the NRR-vs-GRR decision tree (`cs-retention-metrics.md`) to pick the lead metric by audience.

**Sources (retrieved 2026-06-05):** NRR vs GRR (GRR excludes expansion, caps at 100%, the honest floor) — https://churnzero.com/blog/net-revenue-retention-vs-gross-revenue-retention-explained/ ; GRR formula + why it reveals true retention health — https://blog.customerscore.io/gross-revenue-retention-the-saas-metric-that-reveals-your-true-retention-health/ ; NRR benchmark context (~106% median, segment-dependent, "almost meaningless" without ACV/stage) — https://www.fiscallion.io/blog/net-revenue-retention-benchmark-saas-what-the-numbers-actually-mean-for-your-stage . All revenue figures here are illustrative `[ESTIMATE]` — validate against the client's own movement data.
