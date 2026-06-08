---
scenario_id: 2026-06-08-biggest-client-was-unprofitable
contributed_at: 2026-06-08
plugin: wealth-management-ria
product: client-profitability
product_version: "n/a"
scope: likely-general
tags: [segmentation, cost-to-serve, breakeven-aum, profitability]
confidence: medium
reviewed: false
---

## Problem

A firm prioritized its largest-AUM households for the best service and discounts. The risk: AUM rank is not profitability rank — a large, high-touch, fee-discounted client can sit below breakeven, so ranking by AUM misdirects the firm's scarce service capacity (§3 #2).

## Context

- Model: hybrid fee RIA with negotiated breakpoints.
- Constraint: client margin = revenue − cost-to-serve; breakeven AUM = cost-to-serve ÷ effective fee (§3 #2).
- The firm reasoned from AUM rank alone.

## Attempts

- Tried: **segmented by margin, not AUM** (`riaops_calc.py client-profitability`). Outcome: the top-AUM household, deeply discounted and high-touch, fell below breakeven.
- Tried: **computed breakeven AUM per client** (§3 #2). Outcome: several large clients needed a higher fee or lower service intensity to clear breakeven.
- Tried: **checked advisor capacity the discounting consumed** (§3 #4). Outcome: the unprofitable whales were absorbing capacity that profitable clients needed — a retention risk on the good book.

## Resolution

The response was to **re-price or right-size service on the sub-breakeven accounts and re-allocate capacity to profitable households** — not lavish more on the biggest AUM. Any fee/disclosure change routes through compliance (§3 #3 #6). The output was the margin segmentation, breakeven AUM, and a capacity re-allocation.

**Action for the next consultant hitting this pattern:** **rank clients by margin net of cost-to-serve, not AUM.** The biggest account can be the least profitable; compute breakeven AUM and protect capacity for clients who clear it. See Tree 2 and the `riaops_calc.py` `client-profitability` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
