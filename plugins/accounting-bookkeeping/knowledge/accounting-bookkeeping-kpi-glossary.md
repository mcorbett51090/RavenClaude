# Accounting & Bookkeeping Practice KPI Glossary

> The team's canonical metric definitions. Every metric carries a **definition**, a **window**, and a **baseline** before it ships (CLAUDE.md §3 #1). Benchmark ranges are `[unverified — training knowledge]` unless a dated source is attached — confirm against a current source before using in a deliverable (§3 #8).

## Close & reconciliation

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Days-to-close** | Business days from period-end to final statements | Per period | The close metric; target it (§3 #1). |
| **Critical path** | Longest dependent task chain in the close | Per period | The bottleneck, not task count, sets duration (§3 #1). |
| **Reconciliation status** | Accounts tied to source ÷ accounts requiring it | Per period | A close can't finish on un-reconciled accounts (§3 #2). |
| **Control exception** | An SoD or approval-control breach found | Rolling | Approve ≠ enter ≠ reconcile (§3 #5). |

## Working capital & cash

| Metric | Definition | Window | Note |
|---|---|---|---|
| **DSO** | AR ÷ revenue × days | Period | Cash already earned but not collected (§3 #3). |
| **DPO** | AP ÷ COGS × days | Period | A deliberate working-capital lever (§3 #4). |
| **DIO** | Inventory ÷ COGS × days | Period | Cash tied up in stock. |
| **Cash conversion cycle** | DSO + DIO − DPO | Period | Lower frees cash (§3 #3 #4). |
| **Weighted bad-debt** | Σ(aging bucket × loss rate) | Per period | Older buckets carry higher loss rates (§3 #3). |

## Basis & coding

| Concept | Definition | Note |
|---|---|---|
| **Accrual basis** | Revenue/expense recognized when earned/incurred | Matches effort to result; state it (§3 #6). |
| **Cash basis** | Recognized when cash moves | Same business can look very different (§3 #6). |
| **COA hygiene** | Consistent coding, no catch-alls/duplicates | Precedes any analysis (§3 #7). |

## The rule

A metric without a **window** and a **baseline** is not a finding — it's a number (§3 #1). A benchmark without a **source URL + retrieval date** is `[unverified — training knowledge]` (§3 #8).
