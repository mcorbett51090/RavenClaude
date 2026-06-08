# Sales & Revenue Operations KPI Glossary

> The team's canonical metric definitions. Every metric carries a **definition**, a **window**, and a **baseline** before it ships (CLAUDE.md §3 #1). Benchmark ranges are `[unverified — training knowledge]` unless a dated source is attached — confirm against a current source before using in a deliverable (§3 #8).

## Pipeline & coverage

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Coverage ratio** | Open pipeline ÷ remaining quota | Point-in-time, by close-period | Read by segment; target ratio ≈ 1 ÷ stage-weighted win-rate. |
| **Pipeline created** | New qualified pipeline added | Rolling period | A leading indicator vs the coverage target (§3 #5). |
| **Pipeline aging** | Days a deal has dwelt in its current stage | Per deal | Beyond stage-normal dwell = slip risk (§3 #6). |
| **Weighted pipeline** | Σ(deal value × stage win-rate) | Point-in-time | The forecast base before slip haircut (§3 #2). |

## Funnel & velocity

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Stage conversion** | Deals advancing stage N→N+1 ÷ entering N | Cohort | The leaking stage localizes the bottleneck (§3 #3). |
| **Win-rate** | Closed-won ÷ (closed-won + closed-lost) | Rolling, by segment | Always segment by ACV/motion; a blended rate misleads. |
| **Sales-cycle** | Days from create (or qual) to close-won | Median, by segment | Use median; a few whales skew the mean. |
| **Sales velocity** | (open deals × win-rate × ACV) ÷ cycle-length | Rolling | Four levers; moving one moves another (§3 #3). |

## Quota & attainment

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Ramped capacity** | Ramped reps × productivity/rep × ramp factor | Period | Quota must fit under it (§3 #4). |
| **Attainment** | Bookings ÷ quota | Per rep / period | Read the distribution (P25/P50/P75), not the average (§3 #4). |
| **Forecast accuracy** | |forecast − actual| ÷ actual | Per period | The lagging scorecard the leading indicators predict (§3 #5). |

## The rule

A metric without a **window** and a **baseline** is not a finding — it's a number (§3 #1). A benchmark without a **source URL + retrieval date** is `[unverified — training knowledge]` (§3 #8).
