---
scenario_id: 2026-06-05-annual-fund-renewal-lift
contributed_at: 2026-06-05
plugin: nonprofit-fundraising
product: analytics
product_version: "n/a"
scope: likely-general
tags: [annual-fund, renewal, upgrade, segmentation, lybunt-sybunt]
confidence: medium
reviewed: false
---

## Problem

An annual fund was "flat to down" and the team's default plan was a bigger acquisition appeal. But the actual leak was in **renewal**: a large block of prior-year donors (LYBUNTs — gave **L**ast **Y**ear **B**ut **U**nfortunately **N**ot **T**his year) were quietly not renewing, and a deeper block of multi-year-but-now-lapsed donors (SYBUNTs — gave **S**ome **Y**ear But Unfortunately Not This year) had aged past the easy-reactivation window. The office had never run a LYBUNT/SYBUNT report, so the renewal hole was invisible — they were measuring gross dollars, not the renewal cohort.

## Context

- Segment: annual-fund, faith-based human-services org, broad small-donor base, no mid-level program, no documented renewal series.
- Constraint: a **LYBUNT** is the highest-probability reactivation target (gave 12 months ago — still warm), a **SYBUNT** is lower-probability (longer lapse) but a larger pool; the reactivation window narrows sharply with time since last gift. Renewing a donor is far cheaper than acquiring one (renewal channels run ~$0.20/dollar or less vs ~$1.00-1.25 for direct-mail acquisition), so a renewal lift is the cheapest growth available. [verify-at-use]
- The office was conflating "raise more" (acquisition reflex) with "stop losing the donors we have" (the actual driver) — the same single-cause trap the retention tree warns against, one tier down from the retention-turnaround scenario.

## Attempts

- Tried: pulled the **LYBUNT and SYBUNT segments** first and sized each. Outcome: the LYBUNT block was large and recent — a concentrated, addressable renewal opportunity that no appeal was specifically targeting.
- Tried: built a **segmented renewal series** instead of one generic appeal — a LYBUNT-specific "we missed you / here's what your last gift did" track timed to the giving anniversary, and a separate SYBUNT win-back track acknowledging the longer absence. Personalized the prior gift amount and its impact (the acknowledgment/personalization levers from the retention tree). Outcome: renewal response on the LYBUNT segment materially outran the prior generic appeal's response on the same names.
- Tried: layered a **right-sized upgrade ask** onto renewing donors — a percent-increase suggested amount anchored on their prior gift, not an arbitrary round number (see [`../best-practices/upgrade-asks-are-percent-increases-not-arbitrary-round-numbers.md`](../best-practices/upgrade-asks-are-percent-increases-not-arbitrary-round-numbers.md)). Outcome: lifted average gift on the renewing cohort without depressing the renewal rate.

## Resolution

Flat annual-fund revenue was a **renewal** problem, and the fix was segment-then-sequence, not spend-more-on-acquisition. Run the LYBUNT/SYBUNT report to make the renewal hole visible, target LYBUNTs first (highest reactivation probability, cheapest dollar), give SYBUNTs a distinct win-back track before the window closes, and add a percent-based upgrade ask to renewing donors. The team shifted from a single gross-dollars number to **renewal rate by cohort** as the metric that actually moved.

**Action for the next consultant hitting this pattern:** when the annual fund is flat, **run a LYBUNT/SYBUNT report before recommending acquisition.** LYBUNTs (lapsed one year, still warm) are the highest-ROI reactivation target; SYBUNTs need a distinct win-back track before the lapse window closes. Renewal is far cheaper than acquisition — segment the renewal cohorts, sequence to each, and layer a percent-increase upgrade ask on renewing donors. See [`../knowledge/fundraising-decision-trees.md`](../knowledge/fundraising-decision-trees.md) "Donor retention problem — where to start" and the [`../scripts/fundraising_calc.py`](../scripts/fundraising_calc.py) `donor-ltv` mode for the retain-vs-acquire math.

**Sources (retrieved 2026-06-05):**
- Neon One — LYBUNTs and SYBUNTs explained (definitions, reactivation use): https://neonone.com/resources/blog/lybunts-and-sybunts-explained/
- Donorbox — regaining lapsed donors (win-back sequencing, lapse window): https://donorbox.org/nonprofit-blog/regaining-your-lapsed-donors
- RallyUp — cost-per-dollar by channel (renewal vs acquisition ratios): https://rallyup.com/blog/fundraising-metrics-cost-per-dollar-raised/

Reactivation-probability and cost-ratio figures move yearly and are segment-dependent; treat any specific number as `[verify-at-use]` and validate against the org's own data (§3 #8).
