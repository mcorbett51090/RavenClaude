---
scenario_id: 2026-06-05-ppo-vs-ffs-payer-mix
contributed_at: 2026-06-05
plugin: dental-practice
product: revenue-cycle
product_version: "n/a"
scope: likely-general
tags: [ppo, write-off, payer-mix, fee-negotiation, ffs, effective-fee]
confidence: medium
reviewed: false
---

## Problem

A busy single-doctor practice was producing strong numbers but taking home less every year. The adjustments line kept growing and the owner discovered it almost by accident — PPO contractual write-offs were quietly eating a large share of gross production. The owner's first reflex was "drop all the PPOs and go fee-for-service tomorrow," which risked shedding the patient volume those plans drove before knowing which plans actually paid.

## Context

- Segment: general-practice, independent, 1 doctor, PPO-heavy, several plans never re-negotiated.
- Constraint: PPO fees had not been re-negotiated in years — the practice was collecting old contracted rates against current costs. Some plans hadn't been touched in 5–10 years [verify-at-use], so the effective fee was set in a prior economy.
- The owner was reasoning from a binary "PPO bad / FFS good" without the per-plan effective-fee data needed to decide which plans to keep, re-negotiate, or drop.

## Attempts

- Tried: measured the **effective fee by plan** (collected ÷ full UCR fee) and the **write-off percentage by payer**, not a blended average. Trade sources put participating-PPO write-offs commonly in the ~30–45% range, with heavily-contracted practices writing off toward 50% of gross production [verify-at-use]. Outcome: revealed a wide spread — a few plans were near break-even or worse while others were tolerable; the blended number had hidden the worst offenders.
- Tried: ranked plans on **effective fee × patient volume × strategic value** rather than write-off alone (a high-write-off plan that fills otherwise-empty chairs can still be worth keeping; a low-volume bad plan is the first to cut). Outcome: a deliberate keep / re-negotiate / drop list instead of an all-or-nothing switch.
- Tried (the move that worked): **re-negotiated the worst-contracted, highest-volume plans first** before dropping anything — trade reports cite 10–30% increases on major codes from a single negotiation round [verify-at-use] — and modeled the volume/collections impact of dropping the lowest-value plans rather than guessing. Outcome: recovered effective fee on the plans worth keeping and planned an orderly exit from the few worth dropping, protecting volume.

## Resolution

PPO write-offs are a **strategy decision, not an accident** (CLAUDE.md §3 #6). The fix was to manage the payer mix deliberately — measure the effective fee per plan, re-negotiate the worst high-volume contracts first, and only then drop the few plans that fail on effective-fee-times-volume — rather than a reflexive all-FFS switch that would have dumped volume blindly. The decision was data-driven and sequenced, not a gut binary.

**Action for the next consultant hitting this pattern:** before "dropping PPOs," **pull the effective fee and write-off percentage per plan** and rank on effective-fee × volume × strategic value. Re-negotiate the worst high-volume contracts first; drop only the plans that fail the ranking. Run [`../skills/manage-the-payer-mix/SKILL.md`](../skills/manage-the-payer-mix/SKILL.md) and route the A/R and claims side to [`dental-rcm-specialist`](../agents/dental-rcm-specialist.md). The PPO write-off arithmetic is in [`../knowledge/dental-ppo-vs-ffs-decision-tree.md`](../knowledge/dental-ppo-vs-ffs-decision-tree.md).

**Sources (retrieved 2026-06-05):**
- Veritas Dental Resources — The True Cost of Dental Insurance Participation (write-off reality): https://veritasdentalresources.com/post/the-true-cost-of-dental-insurance-participation-a-write-off-reality-check
- Veritas Dental Resources — PPO Fee Negotiations in 2025 (10–30% increases possible): https://veritasdentalresources.com/post/ppo-fee-negotiations-2025-0919
- BoomCloud — The Shocking Truth About Your PPO Write-off Percentage: https://boomcloudapps.com/ppo-write-off-percentage-dental/

Write-off and negotiation figures are trade-source ranges, not hard rules — treat as `[verify-at-use]` and validate against the practice's own ledger and contracts (§3 #8).
