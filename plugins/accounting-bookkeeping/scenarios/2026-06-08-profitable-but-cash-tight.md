---
scenario_id: 2026-06-08-profitable-but-cash-tight
contributed_at: 2026-06-08
plugin: accounting-bookkeeping
product: working-capital
product_version: "n/a"
scope: likely-general
tags: [cash-conversion, dso, dpo, accrual-vs-cash]
confidence: medium
reviewed: false
---

## Problem

A client showed healthy accrual profit but kept running short of cash, and the instinct was to cut expenses. The risk: profit on accrual and cash are different things; cash can be trapped in receivables (high DSO) or surrendered by paying AP too early, and cutting expenses doesn't free the trapped cash (§3 #3 #6).

## Context

- Client: a project-based B2B services firm, accrual basis.
- Constraint: cash conversion cycle = DSO + DIO − DPO, and accrual profit ≠ cash (§3 #3 #4 #6).
- The client reasoned from the P&L, not the cash cycle.

## Attempts

- Tried: **stated the basis and computed the cash conversion cycle** (`acctgops_calc.py working-capital`). Outcome: DSO had drifted well above terms — large cash earned but uncollected.
- Tried: **read the AR aging and weighted bad-debt** (`acctgops_calc.py aging`). Outcome: a concentration in older buckets flagged collection risk, not just slow pay (§3 #3).
- Tried: **checked DPO** (§3 #4). Outcome: the client was also paying vendors early, surrendering free financing on both sides of the cycle.

## Resolution

The fix was a **collections push on aged AR plus deliberate AP timing to terms** — not expense cuts. The output was the cash-conversion-cycle read (basis stated), the aging/bad-debt estimate, and the AP-timing lever.

**Action for the next consultant hitting this pattern:** **state the basis and read the cash conversion cycle before cutting costs.** Accrual profit can hide cash trapped in AR or surrendered in early AP; DSO + DIO − DPO locates it. See Tree 2 and the `acctgops_calc.py` `working-capital` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
