---
scenario_id: 2026-06-08-offline-win-didnt-transfer
contributed_at: 2026-06-08
plugin: search-relevance-engineering
product: relevance
product_version: "n/a"
scope: likely-general
tags: [ab-testing, ndcg, ctr, offline-online]
confidence: medium
reviewed: false
---

## Problem

A tuning change lifted offline NDCG and the team shipped it, but online CTR didn't move. The risk: offline gains don't always transfer — a judgment list that diverges from real user intent, or position bias, can make offline NDCG improve while users see no benefit (§3 #6).

## Context

- Search: e-commerce, interactive.
- Constraint: validate offline wins with an online A/B; offline metric divergence is real (§3 #6).
- The team treated the offline NDCG gain as victory.

## Attempts

- Tried: **ran an online A/B on CTR/conversion** instead of shipping on the offline number (§3 #6). Outcome: the variant showed no lift — the offline win didn't transfer.
- Tried: **inspected the judgment list for intent divergence and position bias.** Outcome: click-derived judgments were position-biased, rewarding an ordering users didn't actually prefer (§3 #3 #6).
- Tried: **rebuilt graded judgments with bias correction**, re-tuned, and re-A/B'd. Outcome: the corrected offline metric now predicted an online lift that the A/B confirmed.

## Resolution

The fix was to **debias the judgment list, re-tune, and confirm with an A/B before shipping** — **not** to trust the original offline NDCG. The output was the A/B result, the judgment-list bias diagnosis, and the confirmed online lift.

**Action for the next consultant hitting this pattern:** **confirm every offline win with an online A/B, and distrust position-biased judgments.** Offline NDCG can rise while CTR doesn't if the judgment list diverges from intent. Debias click-derived judgments before tuning. See Tree 1 and the `validate-online` skill.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
