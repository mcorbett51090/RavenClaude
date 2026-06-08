# FinOps & Cloud Cost KPI Glossary

> The team's canonical metric definitions. Every metric carries a **definition**, a **window**, and a **baseline** before it ships (CLAUDE.md §3 #1). Benchmark ranges are `[unverified — training knowledge]` unless a dated source is attached — confirm against a current source before using in a deliverable (§3 #8).

## Allocation & accountability

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Allocation coverage** | Tagged/attributed spend ÷ total spend | Rolling | Below a usable threshold, optimization is guessing (§3 #1). |
| **Showback** | Visibility of spend to the owning team | Per team/period | Drives most behavior change (§3 #6). |
| **Chargeback** | Spend booked to a team's real budget | Per team/period | Drives the rest; harder, comes after showback (§3 #6). |
| **Shared cost** | Spend not cleanly attributable to one team | Rolling | Allocate usage-based or even-split; name the method. |

## Optimization & commitments

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Waste** | Idle/orphaned/oversized/zombie resources | Point-in-time | Pure savings, no trade-off — first win (§3 #5). |
| **Rightsizing savings** | Current cost − utilization-implied cost | Monthly | Do BEFORE committing (§3 #4). |
| **Commitment coverage** | Committed usage ÷ total eligible usage | Rolling | A portfolio dial, not a max (§3 #3). |
| **Commitment utilization** | Committed capacity actually used ÷ committed | Rolling | Low utilization = locked-in waste (§3 #3). |

## Unit economics & forecast

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Cost per unit** | Allocated cost ÷ units (customer/txn/feature) | Per period | Read the trend, not the level (§3 #2). |
| **Forecast accuracy** | |forecast − actual| ÷ actual | Per period | Budget against the forecast (§3 #7). |
| **Anomaly** | Spend deviation beyond the alert threshold | Real-time | Catch in hours, not on the invoice (§3 #7). |

## The rule

A metric without a **window** and a **baseline** is not a finding — it's a number (§3 #1). A benchmark without a **source URL + retrieval date** is `[unverified — training knowledge]` (§3 #8).
