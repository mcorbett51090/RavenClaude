# Mortgage Lending Operations KPI Glossary

> The team's canonical metric definitions. Every metric carries a **definition**, a **window**, and a **baseline** before it ships (CLAUDE.md §3 #1). Benchmark ranges are `[unverified — training knowledge]` unless a dated source is attached — confirm against a current source before using in a deliverable (§3 #8).

## Funnel & pull-through

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Pull-through** | Funded loans ÷ applications | Cohort, by channel | The master funnel metric (§3 #1). |
| **Stage fallout** | Loans lost between consecutive stages ÷ entering | Per stage | Localizes the leak; fix the worst (§3 #1). |
| **App→approved** | Approved ÷ applications | Cohort | First major fallout gate. |
| **CTC→funded** | Funded ÷ clear-to-close | Cohort | Late-stage fallout = lock/rate or condition issues (§3 #3). |

## Cycle & capacity

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Cycle time** | App-to-close days | Median, by product | Drives capacity and satisfaction (§3 #2). |
| **Bottleneck dwell** | Days in the slowest stage | Per stage | The stage to fix first (§3 #2). |
| **Loans per processor** | Open loans a processor carries at the current cycle | Point-in-time | Falls as cycle lengthens (§3 #4). |
| **Monthly capacity** | Processors × loans-per-processor-at-cycle | Per month | Staff to cycle and the rate swing (§3 #4 #7). |

## Risk, cost & quality

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Locked pipeline exposure** | Locked loan volume at risk to rate moves, net of fallout | Point-in-time | Un-hedged exposure is a P&L risk; hedge routes out (§3 #3). |
| **Cost-to-originate** | (fixed + variable × loans) ÷ funded loans | Per period | The unit economic that survives the rate cycle (§3 #5). |
| **Breakeven volume** | Fixed cost ÷ margin per loan | Per period | The volume the downturn must clear (§3 #5 #7). |
| **QC defect rate** | Defective loans ÷ sampled loans | Per audit | Operational signal; the regulatory judgment routes to counsel (§3 #6). |

## The rule

A metric without a **window** and a **baseline** is not a finding — it's a number (§3 #1). A benchmark without a **source URL + retrieval date** is `[unverified — training knowledge]` (§3 #8).
