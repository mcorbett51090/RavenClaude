---
scenario_id: 2026-06-05-renewal-forecast-miss-single-thread
contributed_at: 2026-06-05
plugin: customer-success-analytics
product: renewal-workflow
product_version: "n/a"
scope: likely-general
tags: [renewal-forecast, single-thread, decision-maker, champion-silence, commit]
confidence: medium
reviewed: false
---

## Problem

A CS org committed a quarterly renewal number to the leadership team and missed it by a wide margin — and the misses clustered in accounts the health tier had marked **Green**. The forecast wasn't wrong because the math was wrong; it was wrong because it ignored the **late-stage relationship signals** that decide renewals.

## Context

- Segment: B2B SaaS, ~180 renewals in the quarter, mix of enterprise and mid-market.
- Constraint: the forecast was built **per-account from the health tier** (good) but committed the *full* renewal $ for every Green account at face value — including expansion upside blended into the same number. It never checked whether the decision-maker was confirmed in role or whether the relationship was **single-threaded** to one champion.
- Several of the missed accounts were "Green" on usage and product signals but **single-threaded** — the one champion had quietly gone silent or left, and there was no one else in the account. Champion silence is a leading churn signal the usage-only tier didn't carry.

## Attempts

- Tried: re-ran the forecast through the renewal-forecast-confidence tree (`cs-retention-metrics.md`). The accounts that missed all failed the same node: **decision-maker not confirmed AND relationship single-threaded.** Outcome: identified the structural gap — the tier scored *product* health but not *relationship* health.
- Tried: added a multi-threading + DM-confirmation check to the renewal workflow's Confirm/Multi-thread stages (`renewal-and-account-lifecycle.md` §2) and **haircut the at-risk dollars explicitly** rather than committing them at face value. Outcome: the committed number got smaller but credible, with a stated confidence band.
- Tried: **separated expansion upside from the renewal base** — committed the base (GRR-shaped) and tracked expansion as a separate stretch line, so a blended number stopped inflating the commit. Outcome: the next quarter's forecast landed within its band.

## Resolution

A renewal forecast built off a usage-only health tier misses the **relationship** failures — a single-threaded account with a silent champion renews "Green" right up to the day it doesn't. The fix was to gate the committable number on the late-stage workflow signals (DM confirmed, multi-threaded), haircut the unconfirmed at-risk dollars, and split expansion upside out of the renewal base.

**Action for the next consultant hitting this pattern:** **a renewal forecast is only as good as its late-stage relationship signals.** Before committing a number, run the renewal-forecast-confidence tree: per-account (not top-down), validated tier, decision-maker confirmed, relationship multi-threaded, and expansion separated from base. Single-threaded + unconfirmed-DM is the top miss — haircut those dollars explicitly instead of assuming they close. Feed champion-silence back into the tier so "Green" can't hide a dead relationship.

**Sources (retrieved 2026-06-05):** customer-health-scoring (leading indicators, depth-of-relationship outweighs raw usage for enterprise) — https://www.everafter.ai/glossary/customer-health-score ; segment-specific scoring improves accuracy — https://www.successifier.com/blog/customer-health-scores-that-actually-predict-churn-a-practical-guide-for-cs-team . The single-thread/DM-confirmation discipline is grounded in this plugin's own `renewal-and-account-lifecycle.md` §2; all figures are illustrative `[ESTIMATE]`.
