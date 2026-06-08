---
scenario_id: 2026-06-08-aum-up-but-organically-flat
contributed_at: 2026-06-08
plugin: wealth-management-ria
product: aum-revenue
product_version: "n/a"
scope: likely-general
tags: [organic-growth, net-new-flows, market-vs-organic, aum-bridge]
confidence: medium
reviewed: false
---

## Problem

An RIA principal celebrated a record-AUM year and planned to hire on the strength of it. The risk: market appreciation can inflate AUM and revenue while the practice is organically flat or shrinking, so a hiring decision built on a bull-market AUM number rests on growth the firm didn't earn (§3 #1 #7).

## Context

- Model: AUM-fee RIA, mass-affluent + HNW.
- Constraint: AUM growth = net new flows + market; only net new flows ÷ beginning AUM is organic (§3 #1 #7).
- The principal reasoned from the ending AUM headline.

## Attempts

- Tried: **built the AUM bridge separating flows from market** (`riaops_calc.py aum-revenue`). Outcome: nearly all the AUM rise was market; net new flows were roughly flat (§3 #1).
- Tried: **computed the organic growth rate** (§3 #7). Outcome: organic growth was near zero — the practice rode the market.
- Tried: **checked net new flows for hidden attrition** (§3 #5). Outcome: inflows barely offset outflows, so the new-client engine and retention both needed attention before hiring.

## Resolution

The response was to **fix the organic-growth engine (new-client flow and retention) before hiring on market-inflated AUM** — and to plan for a drawdown where only organic growth survives. The output was the AUM bridge, the organic rate, and a flows-focused plan.

**Action for the next consultant hitting this pattern:** **separate net new flows from market before reading growth.** A record-AUM year in a bull market can be organically flat; organic growth ÷ beginning AUM is the only rate that survives a drawdown. See Tree 1 and the `riaops_calc.py` `aum-revenue` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
