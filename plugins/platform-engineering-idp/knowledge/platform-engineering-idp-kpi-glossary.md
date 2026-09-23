# Platform Engineering (IDP) KPI Glossary

> The team's canonical metric definitions. Every metric carries a **definition**, a **window**, and a **baseline** before it ships (CLAUDE.md §3 #1). Benchmark ranges are `[unverified — training knowledge]` unless a dated source is attached — confirm against a current source before using in a deliverable (§3 #8).

## DORA & delivery

> **DORA now publishes 5 metrics, not 4** `[re-verified 2026-09-23]` — deployment frequency, lead time for changes, change fail rate, **failed deployment recovery time** (the renamed "MTTR"/time-to-restore, regrouped as a **throughput** metric rather than stability), and **deployment rework rate** (added 2024/2025). Sources: CD Foundation, ["The DORA 4 key metrics become 5"](https://cd.foundation/blog/2025/10/16/dora-5-metrics/) (2025-10-16); [dora.dev's own metrics history](https://dora.dev/insights/dora-metrics-history/). The table below is updated to the 5-metric set; the elite/high/medium/low tier framing referenced elsewhere in this plugin is this team's own retained **house convention** — DORA's 2025 report itself replaced those four tiers with seven team archetypes (see `platform-engineering-idp-economics.md` §4).

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Deploy frequency** | Deployments to production per unit time | Rolling, per service/team | A throughput key; classify against the bands (§3 #3). |
| **Lead time for change** | Commit → running in production | Median, per service | The flow key; decompose to find the slow stage. |
| **Change-failure rate** | Deployments causing a degradation ÷ total | Rolling | A stability key; pairs with failed deployment recovery time. |
| **Failed deployment recovery time** (formerly "MTTR" / time to restore) | Time to restore service after a failed change | Median | DORA moved this from a stability key to a **throughput** metric in its 2025 metric set `[re-verified 2026-09-23]`; still often a platform-reliability signal, not just a team one (§3 #6). |
| **Deployment rework rate** | Ratio of deployments that are unplanned rework triggered by a prior production issue | Rolling | DORA's 5th metric, added 2024/2025 `[re-verified 2026-09-23]` — a proxy for how much change-failure rate forces a team to redo work. |

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
