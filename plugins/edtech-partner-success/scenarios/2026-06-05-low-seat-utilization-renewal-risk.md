---
scenario_id: 2026-06-05-low-seat-utilization-renewal-risk
contributed_at: 2026-06-05
plugin: edtech-partner-success
product: health-scoring
product_version: "n/a"
scope: likely-general
tags: [seat-utilization, license-activation, renewal-risk, k12, evidence, adoption]
confidence: medium
reviewed: false
---

## Problem

A K-12 district partner read **green** in the CRM (the line item was active, the relationship was friendly) but the PSM had no read on whether the district was actually *using* what it bought. The renewal was ~150 days out. The risk: the district was quietly in the "unused-license" pool that gets audited out at budget-build, and the PSM wouldn't find out until the CFO's keep/cut review — too late to do anything but discount.

## Context

- Segment: K-12, mid-sized district, ~4,000 provisioned student seats across multiple schools, single named curriculum-director champion.
- Constraint: "the line item is active" is not "the tool is used." Public research is blunt here — K-12 districts actively use only **~57%** of the EdTech tools they pay for, wasting **~43%** of the spend, and a mid-sized district loses **~$200K-$400K/year** to unused licenses + hidden costs (LearnPlatform / Instructure; Evelyn Learning; EdWeek Market Brief). The narrower "issued licenses never activated" figure is **~27%**. `[verify-at-use — 2026-06-05]`
- The CRM health was a *relationship* read, not a *usage* read — exactly the gap the partner-health score exists to close.

## Attempts

- Tried: pulled the **license-utilization leading indicator** first — "what % of provisioned seats had ≥N meaningful sessions in the last 90 days" — instead of trusting the green CRM band. Outcome: surfaced that activation was concentrated in a handful of schools; whole buildings had near-zero meaningful sessions. The partner was drifting toward the 43%, undetected.
- Tried: ran the **rostering pre-flight before** calling the low-usage buildings a *engagement* problem ("sync ran successfully" ≠ data is correct). Outcome: the dead buildings were partly a rostering-completeness illusion (a roster that synced but never populated some schools) and partly a genuine train-the-trainer cascade that never reached those buildings — a mixed root cause, not a single one.
- Tried: traversed the **play-selection router** (`partner-health-decline-which-play.md`) rather than reflexively opening a renewal conversation. Outcome: the IMPLEMENTATION branch (rostering) fired *above* the renewal branch — fixing the data + re-running the cascade had to precede any commercial motion, or the renewal pitch would land on "the data still isn't right."

## Resolution

The partner was pulled out of the silent-43% trajectory **because the PSM measured utilization months before renewal, not at it** — surfacing the dead buildings while there was still a full semester to re-activate them. The sequence was: utilization read → rostering pre-flight → targeted re-cascade of train-the-trainer to the dead buildings → a year-end impact report built on the *recovered* usage, framed as "57%-side evidence," delivered before the budget-build window closed.

**Action for the next PSM hitting this pattern:** **a green CRM band is a relationship read, not a usage read — pull seat/license utilization as the leading indicator before you trust it.** Then run the rostering pre-flight *before* labeling dead usage an engagement problem, and traverse the play-selection router (IMPLEMENTATION above RENEWAL). The utilization number is what tells you which side of the 57/43 line the partner is on — and you want to know that at T-150, not at the CFO's keep/cut review. The [`../scripts/psm_calc.py`](../scripts/psm_calc.py) `utilization` mode does the activation-rate + dead-seat arithmetic.

**Sources (retrieved 2026-06-05):**
- LearnPlatform / Instructure — EdTech Top 40 (district tool count + ~57% active use): https://www.instructure.com/edtech-top40
- EdWeek Market Brief — >$1B in K-12 ed-tech licensing fees wasted: https://marketbrief.edweek.org/marketplace-k-12/latest-ed-tech-usage-report-shows-improvements-still-1-billion-waste-k-12
- Evelyn Learning — the hidden cost of EdTech sprawl (43% waste, $200K-$400K/district): https://www.evelynlearning.com/blog/the-hidden-cost-of-edtech-sprawl-how-k-12-districts-are-drowning-in-unused-software-and-what-it-leaders-can-do-about-it

Utilization-waste figures are public-benchmark, not partner-attributable — treat as `[verify-at-use]` and recompute against the partner's actual telemetry before any deliverable (CLAUDE.md §3 cite-or-mark rule). Internal cross-refs: [`../knowledge/k12-spend-utilization-43pct.md`](../knowledge/k12-spend-utilization-43pct.md), [`../knowledge/partner-health-decline-which-play.md`](../knowledge/partner-health-decline-which-play.md).
