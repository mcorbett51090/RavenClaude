# Customer Support & CX Operations KPI Glossary

> The team's canonical metric definitions. Every metric carries a **definition**, a **window**, and a **baseline** before it ships (CLAUDE.md §3 #1). Benchmark ranges are `[unverified — training knowledge]` unless a dated source is attached — confirm against a current source before using in a deliverable (§3 #8).

## Deflection & cost

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Deflection rate** | Self-service resolutions ÷ self-service attempts | Rolling | Measure against attempts, not assume (§3 #1). |
| **Cost-per-contact** | Fully-loaded support cost ÷ handled contacts | Rolling | Include people + tooling, by channel (§3 #1). |
| **Cost avoided** | Deflection-rate × volume × cost-per-contact | Per period | The deflection ROI vs a hire (§3 #1). |

## Staffing & flow

| Metric | Definition | Window | Note |
|---|---|---|---|
| **AHT** | Average handle time per contact | By channel | Voice ≠ chat ≠ email; never blend (§3 #2). |
| **Workload hours** | Contacts × AHT | Per interval | The input to staffing, not a ratio (§3 #2). |
| **Occupancy** | Time on contacts ÷ time available | Per interval | A band; too high burns out, too low wastes (§3 #2). |
| **Backlog change** | Arrivals − resolution capacity | Per day | Positive = growing backlog (§3 #5). |
| **SLA attainment** | Contacts within target time ÷ total | Per period | A queueing outcome of the flow (§3 #5). |

## Quality & satisfaction

| Metric | Definition | Window | Note |
|---|---|---|---|
| **FCR** | Resolved on first interaction ÷ total | Rolling, segmented | The master metric (§3 #4). |
| **Reopen rate** | Reopened ÷ resolved | Rolling | The inverse signal of FCR (§3 #4). |
| **CSAT** | Satisfied responses ÷ responses | Segmented | Never blend channel/tier/issue (§3 #3). |
| **QA score** | Rubric score on sampled contacts | Sampled | Sample must be statistically meaningful (§3 #6). |

## The rule

A metric without a **window** and a **baseline** is not a finding — it's a number (§3 #1). A benchmark without a **source URL + retrieval date** is `[unverified — training knowledge]` (§3 #8).
