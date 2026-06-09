# Engineering Management KPI Glossary

> The team's canonical signal definitions. Every signal carries a **definition**, a **window**, and a **baseline** before it ships (CLAUDE.md §3 #3 #4). Benchmark ranges are `[unverified — training knowledge]` unless a dated source is attached — confirm against a current source before using in a deliverable (§3 #8). **None of these are individual stack-rank inputs** — they are system-health signals to improve the system (§3 #3).

## Delivery / flow (DORA + flow)

| Signal | Definition | Window | Note |
|---|---|---|---|
| **Deploy frequency** | How often the team ships to production | Rolling (wk/day) | Throughput of the delivery system, not of a person (§3 #3). |
| **Lead time for change** | Commit → running in production | Rolling | Shrinks with smaller batches + limited WIP. |
| **Change-fail rate** | Deploys causing a failure ÷ deploys | Rolling | Quality of flow; pairs with deploy frequency. |
| **MTTR** | Time to restore service after a failure | Per incident | Resilience signal; improve with rollback + observability. |
| **WIP** | Items in progress at once | Instant | The lever: lower WIP → lower lead time (Little's Law). |
| **Flow efficiency** | Active time ÷ total lead time | Per item | Exposes hidden wait/rework, not effort. |

## People / team health

| Signal | Definition | Window | Note |
|---|---|---|---|
| **Regretted attrition** | Departures the org wanted to keep ÷ headcount | Rolling 12mo | The attrition that costs; size it with `attrition-cost`. |
| **1:1 cadence held** | Scheduled 1:1s actually held (not cancelled) | Rolling | A leading trust signal; cancelling is the expensive cheap call (§3 #2). |
| **eNPS / team sentiment** | Survey-based team sentiment | Per survey | A signal, not a verdict; pair with conversation (§3 #4). |
| **Span of control** | Direct reports per manager | Instant | Too-wide starves 1:1s; too-narrow over-manages (§3 #8 — varies by context). |

## On-call / operational load

| Signal | Definition | Window | Note |
|---|---|---|---|
| **Pages per shift** | Actionable pages per on-call night/shift | Per rotation | Sustained > a few/night signals toil; size with `oncall-load`. |
| **Off-hours page rate** | Pages outside working hours | Rolling | The burnout driver; reduce before adding people. |
| **Rotation depth** | Engineers in the rotation | Instant | Drives how often each person is on the hook. |
| **Toil %** | Time on repetitive ops vs engineering | Rolling | The automation budget signal. |

## Quality / codebase health

| Signal | Definition | Window | Note |
|---|---|---|---|
| **Lead-time drift** | Lead time rising over time | Trend | Felt "the codebase is slowing us" → measured (§3 #7). |
| **Rework rate** | Changes reverted/re-fixed soon after | Rolling | A debt symptom; localize to hotspots. |
| **Change hotspots** | Files with high churn × high complexity | Snapshot | Where paydown has the most leverage. |

## The rule

A signal without a **window** and a **baseline** is not a finding — it's a number (§3 #3 #4). A benchmark without a **source URL + retrieval date** is `[unverified — training knowledge]` (§3 #8). **No signal here ranks a person** — it improves a system (§3 #3).
