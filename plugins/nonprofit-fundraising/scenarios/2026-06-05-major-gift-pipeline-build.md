---
scenario_id: 2026-06-05-major-gift-pipeline-build
contributed_at: 2026-06-05
plugin: nonprofit-fundraising
product: major-gifts
product_version: "n/a"
scope: likely-general
tags: [major-gifts, moves-management, portfolio, pipeline, qualification]
confidence: medium
reviewed: false
---

## Problem

A development office had a stack of "major-gift prospects" — a board-supplied list of ~120 names — and a major-gifts officer (MGO) who was "working the list" with no portfolio structure, no qualification gate, and no documented moves. The result: lots of activity (coffees, event invites), almost no asks, and a leadership team asking "where are the gifts?" The real problem was a **pipeline with no stages**: every name sat in an undifferentiated pool, so the MGO spent equal effort on a $250 donor and a genuine six-figure prospect, and nobody could say which prospects were actually close to an ask.

## Context

- Segment: major-gifts, mid-size arts org, one MGO, ED-involved, board with some wealth but reluctant to ask (door-openers, not askers — see [`../best-practices/board-members-are-door-openers-not-askers-by-default.md`](../best-practices/board-members-are-door-openers-not-askers-by-default.md)).
- Constraint: an MGO can actively manage only a bounded portfolio — the trade rule of thumb is roughly **100-150 qualified prospects** per full-time officer, far fewer if each is deeply cultivated. 120 *unqualified* names is not a portfolio; it's a research backlog. [verify-at-use]
- The office conflated "has a list" with "has a pipeline." A list is names; a pipeline is names *with a stage and a next move*.

## Attempts

- Tried: ran a **qualification pass** before any cultivation — scored each name on **capacity** (can they give at the target level? wealth/giving signals) and **affinity/relationship** (warm connection? documented mission alignment?), using the major-gift go/cultivate tree in [`../knowledge/fundraising-decision-trees.md`](../knowledge/fundraising-decision-trees.md). Outcome: ~120 names collapsed to ~40 genuinely qualified — the rest were annual-fund/mid-level donors over-labeled as "major," or had no capacity evidence at all.
- Tried: assigned every qualified prospect a **moves-management stage** (identification → qualification → cultivation → solicitation → stewardship) and a **dated next move** with an owner, logged in the CRM rather than the MGO's head (see [`../best-practices/moves-management-is-a-documented-record-not-a-mental-model.md`](../best-practices/moves-management-is-a-documented-record-not-a-mental-model.md)). Outcome: the office could finally see how many prospects were near solicitation (the leading indicator of near-term gifts) vs stuck in early cultivation.
- Tried: built the ask-side feasibility check — a **gift range chart** for the year's major-gift goal — to confirm the qualified pool could actually carry the number, not just the activity (see [`../scripts/fundraising_calc.py`](../scripts/fundraising_calc.py) `gift-pyramid`). Outcome: surfaced that the pool was thin at the top — enough mid-five-figure prospects, too few six-figure ones to hit the lead-gift tier — a recruiting flag, not a "work harder" flag.

## Resolution

"No gifts" was a **pipeline-structure** problem, not an effort problem. The fix was qualification before cultivation (collapsing 120 names to ~40 real prospects), an explicit moves-management stage + dated next move per prospect, and a gift-range-chart feasibility check that exposed the thin top of the pool. The MGO's effort was the same; it was now *directed*, and leadership could read pipeline velocity instead of activity.

**Action for the next consultant hitting this pattern:** **a list is not a pipeline.** Qualify on capacity AND affinity before spending cultivation hours, cap the portfolio at what one officer can genuinely move (~100-150 qualified, fewer if deep), assign every prospect a stage + a dated next move in the CRM (not the officer's memory), and run a gift-range chart to confirm the qualified pool can carry the goal. Velocity through the stages — especially how many are near solicitation — is the leading indicator, not meeting count.

**Sources (retrieved 2026-06-05):**
- CapitalCampaignPro — gift range charts (top gift 10-25% of goal; 80/20 of campaign giving): https://capitalcampaignpro.com/capital-campaign-gift-range-chart/
- DonorSearch — gift range chart guide + calculator (prospects-per-gift, pyramid structure): https://www.donorsearch.net/resources/gift-range-chart-guide/

Portfolio-size and pyramid figures are trade rules-of-thumb, not hard rules — treat as `[verify-at-use]` and calibrate to the org's case mix, officer experience, and segment (§3 #8).
