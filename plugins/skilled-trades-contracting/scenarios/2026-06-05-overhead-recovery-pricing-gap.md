---
scenario_id: 2026-06-05-overhead-recovery-pricing-gap
contributed_at: 2026-06-05
plugin: skilled-trades-contracting
product: estimating
product_version: "n/a"
scope: likely-general
tags: [overhead, recovery, loaded-rate, pricing, net-margin]
confidence: medium
reviewed: false
---

## Problem

A general contractor doing residential remodels showed "healthy" job-level gross margins on every estimate, yet net profit hovered near break-even. The estimates priced labor at a wage-plus-burden rate and added a profit markup, but the rate **never carried overhead** — so every job looked profitable at the job level while the company quietly under-recovered its fixed cost across the year.

## Context

- Trade: general contracting / remodeling, ~$1.2M revenue, owner + office manager + field crews, overhead (rent, office, vehicles not on a job, insurance, owner's admin time) not allocated into any rate.
- Constraint: the loaded labor rate stopped at wage + burden; overhead was treated as "whatever's left after the jobs" — which is exactly backwards. Net margin in residential/GC work is thin (industry net often **~5–6%**, with a healthy target **~8–10%**) [verify-at-use], so an unrecovered overhead markup is the difference between profit and break-even.
- The owner read healthy job gross margins as healthy business — the classic gross-vs-net blind spot.

## Attempts

- Tried: computed the **overhead recovery markup** before touching prices — annual overhead ÷ annual direct job cost — with [`../scripts/trades_calc.py`](../scripts/trades_calc.py) `overhead-rate`. Outcome: overhead was running ~16% of direct cost (and ~12% of revenue), none of which the estimates were adding — the exact net-margin gap.
- Tried: rebuilt the **fully-loaded labor rate** to include the per-billable-hour share of overhead (`loaded-rate` mode: wage + burden + overhead ÷ sellable hours), so every estimated hour carries its overhead before profit (§3 #1). Outcome: the loaded rate rose; estimates now break even on overhead *before* the profit markup is added.
- Tried: separated the **overhead markup** from the **profit markup** in the estimate template so the two are visible and tunable independently (the "10-and-10" framing — ~10% overhead + ~10% profit as a baseline) [verify-at-use]. Outcome: the owner could see, per job, what covered overhead vs what was actual profit.

## Resolution

The business was **under-recovering overhead** because the labor rate didn't carry it — healthy job gross margins masked a near-zero net because fixed cost was never priced in. Building the overhead recovery markup into the loaded rate (and separating overhead from profit in the estimate) closed the gap. Job gross margin ≠ business net margin; the rate has to carry overhead before profit.

**Action for the next consultant hitting this pattern:** when job-level margins look fine but net profit doesn't, **build the overhead recovery rate before pricing** (§3 #1). Compute overhead ÷ direct cost, fold it into the loaded labor rate, and keep the overhead markup and profit markup as separate, visible line items. See [`../knowledge/trades-markup-vs-margin-decision-tree.md`](../knowledge/trades-markup-vs-margin-decision-tree.md), the [`overhead-allocation-rate`](../best-practices/overhead-allocation-rate-must-be-built-before-pricing-any-job.md) / [`estimate-to-a-fully-loaded-labor-rate`](../best-practices/estimate-to-a-fully-loaded-labor-rate-not-a-wage.md) rules, and [`../skills/build-the-loaded-rate/SKILL.md`](../skills/build-the-loaded-rate/SKILL.md).

**Sources (retrieved 2026-06-05):**
- NEXT Insurance — *Typical Contractor Overhead and Profit Margin* (overhead + profit markup, the 10-and-10 baseline): https://www.nextinsurance.com/blog/typical-contractor-overhead-profit-margin/
- Aladdin Bookkeeping — *What Is the Average Construction Industry Profit Margin in 2025?* (net margin ~5–6%, healthy ~8–10%): https://aladdinbookkeeping.com/average-construction-industry-profit-margin/
- Procore — *Construction Markup and Profit Margin* (overhead recovery, separating overhead from profit): https://www.procore.com/library/construction-markup-and-profit-margin

Overhead ratios and net-margin targets are segment-dependent; treat any specific number as `[verify-at-use]` and validate against the contractor's actual P&L (§3 #8).
