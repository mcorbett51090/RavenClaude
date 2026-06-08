# Platform Engineering (IDP) KPI Glossary

> The team's canonical metric definitions. Every metric carries a **definition**, a **window**, and a **baseline** before it ships (CLAUDE.md §3 #1). Benchmark ranges are `[unverified — training knowledge]` unless a dated source is attached — confirm against a current source before using in a deliverable (§3 #8).

## DORA & delivery

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Deploy frequency** | Deployments to production per unit time | Rolling, per service/team | A throughput key; classify against the bands (§3 #3). |
| **Lead time for change** | Commit → running in production | Median, per service | The flow key; decompose to find the slow stage. |
| **Change-failure rate** | Deployments causing a degradation ÷ total | Rolling | A stability key; pairs with MTTR. |
| **MTTR** | Time to restore service after a failed change | Median | Often a platform-reliability signal, not just a team one (§3 #6). |

## Adoption & cognitive load

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Golden-path adoption** | Teams on the golden path ÷ total teams | Point-in-time | The success metric — features shipped is not (§3 #7). |
| **Time-to-first-deploy** | New service init → first prod deploy | Per new service | The paved-road friction test (§3 #2). |
| **Self-service ratio** | Self-service actions ÷ (self-service + tickets) | Rolling | Every ticket is platform debt (§3 #4). |
| **Cognitive load** | Surfaces a developer must reason about to ship | Qualitative + survey | Abstract heavy lifting, not service behavior (§3 #5). |

## Platform reliability

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Paved-path success rate** | Successful paved-path runs ÷ total | Rolling | A platform SLI (§3 #6). |
| **Provisioning latency** | Request → resource ready (p95) | Rolling | A platform SLI; gates the self-service promise (§3 #4 #6). |
| **Error budget** | (1 − SLO target) × window | Per window | Gates how much platform change ships (§3 #6). |

## The rule

A metric without a **window** and a **baseline** is not a finding — it's a number (§3 #1). A benchmark without a **source URL + retrieval date** is `[unverified — training knowledge]` (§3 #8).
