# Pharmacy Operations KPI Glossary

> The team's canonical metric definitions. Every metric carries a **definition**, a **window**, and a **baseline** before it ships (CLAUDE.md §3 #1). Benchmark ranges are `[unverified — training knowledge]` unless a dated source is attached — confirm against a current source before using in a deliverable (§3 #8).

## Throughput & safety

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Daily script volume** | Scripts filled per day | Rolling, by pharmacy | The fill-staffing driver (§3 #5). |
| **Verification capacity** | Scripts a pharmacist can verify per hour × pharmacist hours | Per period | Must cover fill volume; a deficit is a safety risk (§3 #1). |
| **Clinical-service time** | Hours on immunizations, MTM, counseling | Per period | Real staffing load beyond fill (§3 #5). |
| **Dispensing-error rate** | Errors caught/reported ÷ scripts | Per period | Operational signal; the clinical judgment routes out (§3 #7 #8). |

## Inventory & margin

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Days-on-hand** | Inventory value ÷ daily COGS | Point-in-time, by class | Tied-up cash and stockout risk; specialty distinct (§3 #2 #6). |
| **Real margin/script** | Reimbursement − acquisition cost − DIR fee | Per script | The sticker overstates margin (§3 #3). |
| **DIR fee** | Direct/indirect remuneration (retroactive clawback) | Per script/period | Can flip a script negative after fill (§3 #3). |
| **Stockout rate** | Scripts that can't be filled from stock ÷ scripts | Per period | A lost script and a service failure (§3 #2). |

## Adherence & stars

| Metric | Definition | Window | Note |
|---|---|---|---|
| **PDC** | Proportion of days covered = days covered ÷ days in period | Measurement period | The standard adherence measure for stars (§3 #4). |
| **MPR** | Medication possession ratio | Measurement period | Related adherence measure; can overstate vs PDC. |
| **Adherence band** | Whether PDC clears the measure threshold | Per measure | Below threshold drags the star measure (§3 #4). |
| **Star measure** | Plan quality rating tied to adherence and services | Annual | Adherence is a direct input and a reimbursement lever (§3 #4). |

## The rule

A metric without a **window** and a **baseline** is not a finding — it's a number (§3 #1). A benchmark without a **source URL + retrieval date** is `[unverified — training knowledge]` (§3 #8).
