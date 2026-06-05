---
scenario_id: 2026-06-05-campaign-feasibility-gift-pyramid
contributed_at: 2026-06-05
plugin: nonprofit-fundraising
product: capital-campaign
product_version: "n/a"
scope: likely-general
tags: [capital-campaign, feasibility, gift-pyramid, gift-range, lead-gift]
confidence: medium
reviewed: false
---

## Problem

A board fell in love with a building and set a **$3M capital campaign goal** by acclamation — a round number anchored on the project cost, not on the donor base's capacity to give it. They wanted to "announce and go public." The risk: a campaign goal set top-down from a budget, with no gift range chart and no confirmed lead gift, that the donor pyramid cannot actually fill — the classic public-failure pattern where a campaign stalls at 40% because the top of the pyramid was never there.

## Context

- Segment: capital-campaign, independent school, strong annual fund but a shallow major-gift history, board-driven, no prior campaign experience.
- Constraint: campaigns are won at the **top of the pyramid** — conventionally the **lead gift is ~10-25% of the goal**, and roughly the **top 10-20% of gifts carry 50-80%+ of the total** (the 80/20 reality of campaign giving). A $3M campaign therefore needs a credible **$300k-$750k lead gift** and a handful of six-figure gifts behind it *before* going public — typically with **~50-70% of the goal quietly committed in the silent phase** first. [verify-at-use]
- The board was reasoning from "the building costs $3M, so the goal is $3M," skipping the feasibility question entirely: *does the prospect pool contain the gifts this pyramid requires?*

## Attempts

- Tried: built the **gift range chart** for the $3M goal first — top gift, the tiers below it, gifts-needed and qualified-prospects-needed per tier — using [`../scripts/fundraising_calc.py`](../scripts/fundraising_calc.py) `gift-pyramid`. Outcome: made the requirement concrete: the campaign needed (illustratively) a ~$450k-$750k lead gift and several $250k+ gifts. The board could now see the *shape* of what they were committing to, not just the headline number.
- Tried: tested the chart against the **actual rated prospect pool** (capacity-screened names), not against optimism. Outcome: surfaced a thin top — enough mid-five-figure capacity, no identified lead-gift prospect at the required level. That gap is a feasibility finding, not a "sell harder" problem.
- Tried: sequenced the honest path — **confirm the case for support** as a real document (see [`../best-practices/the-case-for-support-is-a-document-not-a-tagline.md`](../best-practices/the-case-for-support-is-a-document-not-a-tagline.md)), run a quiet **lead-gift cultivation phase**, and set the public goal *after* the silent phase confirmed the top of the pyramid — rather than announcing $3M and hoping. Outcome: the board adopted a silent-phase-first plan and a working goal range pending the lead gift, instead of a premature public number.

## Resolution

The $3M goal was a **budget number masquerading as a campaign goal**. The fix was to build the gift range chart, test it against the real rated-prospect pool, and refuse to set the public goal until the silent phase confirmed the lead gift and the top tiers. A campaign goal is set from the *pyramid the donors can fill*, not from the project's cost — and the lead gift is the single most load-bearing piece. The board moved from "announce and hope" to "secure the top quietly, then go public at a goal the chart supports."

**Action for the next consultant hitting this pattern:** **never let the project budget set the campaign goal — let the gift range chart and the rated prospect pool set it.** Build the pyramid (lead gift ~10-25% of goal; top 10-20% of gifts carry the majority), test it against capacity-screened prospects, and stay in the silent phase until ~50-70% of the goal — including a confirmed lead gift — is committed before going public. A pyramid the pool can't fill is a feasibility flag, full stop. See [`../knowledge/nonprofit-campaign-readiness-decision-tree.md`](../knowledge/nonprofit-campaign-readiness-decision-tree.md) and the `gift-pyramid` calculator mode.

**Sources (retrieved 2026-06-05):**
- CapitalCampaignPro — gift range chart how-to (lead gift 10-25%; silent-phase share; 80/20): https://capitalcampaignpro.com/capital-campaign-gift-range-chart/
- DonorSearch — gift range chart guide + calculator (prospects-per-gift, pyramid shape): https://www.donorsearch.net/resources/gift-range-chart-guide/
- NonProfit PRO — using your capital campaign gift range chart (top-gift concentration): https://www.nonprofitpro.com/post/4-tips-to-make-the-most-of-your-capital-campaign-gift-range-chart/

Lead-gift percentage, 80/20 concentration, and silent-phase-share figures are trade conventions, not hard rules — treat as `[verify-at-use]` and calibrate to the org's prior campaign history, prospect pool, and segment (§3 #8).
