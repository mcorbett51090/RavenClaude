---
scenario_id: 2026-06-05-cac-rising-blended-vs-incremental
contributed_at: 2026-06-05
plugin: ecommerce-dtc
product: acquisition
product_version: "n/a"
scope: likely-general
tags: [cac, blended, incrementality, attribution, channel-mix, mer]
confidence: medium
reviewed: false
---

## Problem

A growth lead saw blended CAC climbing month over month and was about to cut the Meta budget — the platform-reported ROAS on the prospecting campaigns had fallen below the line, so the obvious read was "Meta is broken, move the money." The risk: cutting a channel on its *last-click / platform-attributed* number when that number is the least trustworthy thing on the dashboard. Platform pixels over-claim conversions they merely *witnessed*; a brand that cuts spend on the inflated number often watches *total* orders fall by more than the channel "should" have contributed — proof the channel was driving incremental demand the attribution model hid.

## Context

- Segment: beauty, ~$6M/yr revenue, two paid channels (Meta + Google) plus email/SMS and organic/direct.
- Constraint: iOS signal loss had degraded platform attribution; the brand had **no holdout / incrementality discipline** — it read each channel's in-platform ROAS as truth and summed them, which double-counts overlapping conversions.
- The blended CAC was rising, but nobody had split it: was *acquisition* getting more expensive, or was the *denominator* (new vs. returning, organic vs. paid) shifting under a blended number?

## Attempts

- Tried: **split CAC by channel and cohort first**, instead of trusting the blend (§3 #5). Blended CAC hides which channel is scaling efficiently and which is subsidized; reading new-customer CAC per channel separated a genuinely-degrading channel from one whose *measured* number had simply moved with attribution. Outcome: the per-channel split showed Google new-customer CAC stable; the rise was concentrated in one Meta campaign with a creative-frequency spike.
- Tried: read **MER (marketing efficiency ratio = total revenue ÷ total ad spend)** as the un-gameable top-line check, since blended/last-click ROAS can't be trusted post-iOS. MER can't be inflated by per-platform attribution overlap. Breakeven MER ≈ 1 ÷ contribution-margin% — at ~30% contribution margin, breakeven MER ≈ 3.3 [verify-at-use]. The brand's MER was holding above its breakeven even as platform ROAS "fell," the tell that the platform number, not the business, was the thing moving.
- Tried: a **geo/holdout incrementality test** before touching the budget — hold the channel dark in matched regions and read the lift in *total* orders, not platform-attributed ones. Outcome: the Meta prospecting was meaningfully incremental; cutting it on platform ROAS would have cut real demand.
- Tried: rotated the fatigued creative (frequency > ~3.0 is the first creative-fatigue signal) before any budget change — the cheapest fix first (see [`../knowledge/ecommerce-decision-trees.md`](../knowledge/ecommerce-decision-trees.md) "CAC is climbing — root cause diagnosis").

## Resolution

The budget was **not** cut. The rising blended CAC decomposed into (a) a creative-fatigue spike on one campaign (fixed by rotation) and (b) an attribution artifact (platform ROAS falling while MER and incrementality held). Reading CAC by channel + cohort, cross-checking MER against the contribution-margin breakeven, and running a holdout before reallocating turned a reflex budget cut into a targeted creative refresh — orders held, CAC normalized the next cycle.

**Action for the next consultant hitting this pattern:** **never reallocate on a blended or platform-attributed number.** Split CAC by channel + cohort (§3 #5), read MER against the `1 ÷ contribution-margin%` breakeven as the un-inflatable check, and run a holdout/geo-lift test before cutting a channel that *looks* broken on last-click. The [`../scripts/dtc_calc.py`](../scripts/dtc_calc.py) `breakeven-roas` mode computes the MER/ROAS floor from your margin; `ltv-cac` checks the channel's realized cohort LTV against the 3:1 line.

**Sources (retrieved 2026-06-05):**
- Northbeam — MER vs. ROAS, definition + benchmarks: https://www.northbeam.io/blog/marketing-efficiency-ratio-mer-roas
- Eightx — MER formula + 2026 DTC benchmarks (breakeven MER = 1 ÷ contribution margin%): https://eightx.co/blog/what-is-mer-marketing-efficiency-ratio
- AdLibrary — Blended ROAS as the weekly operator ratio (can't be inflated by per-platform overlap): https://adlibrary.com/posts/blended-roas

Benchmarks (breakeven MER, stage-based MER ranges, the 3.3 figure at 30% margin) are public and segment-dependent — treat as `[verify-at-use]` and recompute against the brand's actual contribution margin and channel mix (§3 #8).
