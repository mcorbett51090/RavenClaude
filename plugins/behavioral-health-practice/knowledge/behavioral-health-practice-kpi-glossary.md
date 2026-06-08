# Behavioral Health Practice KPI Glossary

> The team's canonical metric definitions. Every metric carries a **definition**, a **window**, and a **baseline** before it ships (CLAUDE.md §3 #1). Benchmark ranges are `[unverified — training knowledge]` unless a dated source is attached — confirm against a current source before using in a deliverable (§3 #8).

## Access & no-show

| Metric | Definition | Window | Note |
|---|---|---|---|
| **No-show rate** | Visits not attended and not cancelled in time ÷ scheduled visits | Rolling, by clinician | Read with lost slots and revenue, not alone (§3 #1). |
| **Late-cancel rate** | Cancellations inside the policy window ÷ scheduled visits | Rolling | Behaves like a no-show for fill purposes (§3 #1). |
| **Access time** | Days from first contact to first kept appointment | Per referral, by source | The strongest predictor of conversion and retention (§3 #2). |
| **Fill rate** | Kept visits ÷ available slots | Per clinician/period | No-show-adjusted; feeds caseload sizing (§3 #4). |

## Documentation & quality

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Note timeliness** | Notes signed within the policy window ÷ visits | Rolling | Late notes are unbillable and a compliance risk (§3 #3). |
| **Medical-necessity completeness** | Notes with required medical-necessity elements ÷ visits | Per audit | Operational check; the clinical judgment routes out (§3 #8). |
| **MBC capture rate** | Visits with a recorded outcome measure ÷ eligible visits | Rolling | The quality and emerging reimbursement signal (§3 #6). |

## Caseload & payer

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Caseload capacity** | FTEs × target weekly billable hours ÷ avg session length | Per period | Staff to demand, not a fixed ratio (§3 #4). |
| **Utilization** | Billable sessions delivered ÷ capacity | Per clinician/period | Read against the no-show-adjusted fill rate (§3 #4). |
| **Blended reimbursement** | Σ(payer volume × reimbursement) ÷ total volume | Rolling | Read by payer, not blended only (§3 #5). |
| **Margin per visit** | Reimbursement − variable cost | Per payer | The payer-mix margin lever (§3 #5). |

## The rule

A metric without a **window** and a **baseline** is not a finding — it's a number (§3 #1). A benchmark without a **source URL + retrieval date** is `[unverified — training knowledge]` (§3 #8).
