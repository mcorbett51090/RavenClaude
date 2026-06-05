---
name: capacity-sizing-and-isolation
description: "Playbook for sizing Fabric capacity SKUs, isolating noisy workloads across capacities, configuring surge protection and smoothing, and diagnosing throttling — the FinOps and operations companion to the capacity-finops knowledge file."
---

# Capacity Sizing and Isolation

## When to Use This Skill

Use when provisioning a new Fabric capacity, when a capacity is throttling and the cause is unclear, or when planning a multi-workload isolation strategy.

## 1. Fabric CU Model Refresher

Fabric capacity is measured in **Capacity Units (CUs)**. Each operation consumes CUs; the system **smooths** consumption over a rolling window (10-second bursts, 24-hour background smoothing). A workload can burst above its SKU's baseline as long as the smoothed average stays under the limit.

| SKU | CUs | Monthly cost (approx, East US) | Typical use |
|---|---|---|---|
| F2 | 2 | ~$262 | Small dev/test |
| F4 | 4 | ~$524 | Single team POC |
| F8 | 8 | ~$1,048 | Small prod workload |
| F16 | 16 | ~$2,097 | Medium team |
| F32 | 32 | ~$4,194 | Multi-team or mixed workloads |
| F64 | 64 | ~$8,389 | Large analytics platform |

[Verify prices at build — Fabric pricing changes frequently.]

## 2. Sizing Decision

**Step 1 — Estimate average concurrent CU demand (not peak):**

```
CU estimate = SUM(workload_avg_CU) across all concurrent workloads
```

Fabric smooths over a 24-hour window for background jobs — size to average + 20% headroom, not to the peak of a single large pipeline run.

**Step 2 — Select the next SKU tier above your estimate.**

**Step 3 — Enable surge protection** (`Overload protection` in the Admin portal) to prevent a single runaway job from exhausting the capacity.

**Step 4 — Monitor for 2 weeks.** Check the Fabric Capacity Metrics app for actual utilization; rightsize if P90 utilization is consistently < 40% (downsize) or > 80% (upsize or isolate).

## 3. Workload Isolation Strategy

| Isolation reason | Pattern |
|---|---|
| Dev vs prod | Separate capacities (different F SKUs; dev can be smaller) |
| Noisy ETL vs interactive queries | Separate capacities or workspace assignment with different capacities |
| Tenant isolation (ISV) | Separate capacity per tenant (billing boundary, security boundary) |
| One heavy batch job starving dashboards | Move the batch job to a dedicated workspace on a separate capacity |

```
Capacity A (F8)  — prod interactive workloads (semantic models, dashboards)
Capacity B (F4)  — prod batch/pipeline workloads (Data Factory pipelines, Spark)
Capacity C (F2)  — dev/test (all teams share)
```

## 4. Diagnosing Throttling

Throttling surfaces as slow queries, pipeline failures, or "Capacity exceeded" errors.

```
Admin portal → Capacity Metrics app → select capacity → "Throttling" tab
```

Key metrics to check:

| Metric | Throttling if |
|---|---|
| Background CU utilization | Smoothed 24h average > 100% |
| Interactive CU utilization | 10s burst > SKU interactive limit |
| Rejected requests | > 0 on interactive tier |

**Common causes:**

1. A single large Spark notebook consuming all background CUs — move to a separate capacity or schedule off-peak
2. Direct Lake semantic model refresh coinciding with pipeline run — stagger schedules
3. Too many concurrent dataflow Gen2 refreshes — reduce parallelism or upgrade SKU
4. V-Order not enabled on gold tables — queries consume more CUs than necessary

## 5. Capacity Metrics App Queries (KQL)

```kql
// Top 5 artifacts by CU consumption — last 24h
FabricCapacityMetrics
| where TimeGenerated > ago(24h)
| summarize TotalCU = sum(CUSeconds) by ArtifactName, ArtifactKind
| top 5 by TotalCU desc
```

[Metric names and schema are Fabric-version dependent — verify at build.]

## 6. Reservation and Cost Optimization

| Strategy | Discount | Commitment |
|---|---|---|
| Pay-as-you-go | 0% | None |
| 1-year reservation | ~37% | 1 year, upfront or monthly |
| 3-year reservation | ~53% | 3 years, upfront |
| Pause capacity (non-prod) | ~40-60% | None — pause nights/weekends |

For dev/test capacities, configure an **auto-pause** schedule (pause at 7pm, resume at 8am) — reduces cost by ~55% on an F2.

## 7. Checklist Before Go-Live

- [ ] Capacity SKU selected from average + 20% headroom (not peak)
- [ ] Surge/overload protection enabled in Admin portal
- [ ] Separate capacity for dev/test vs production
- [ ] Capacity Metrics app deployed and accessible to the ops team
- [ ] Budget alert configured in Azure Cost Management for the Fabric capacity resource
- [ ] Auto-pause schedule set for non-production capacities

## Pitfalls

- Sizing for the peak of a single large Spark job — Fabric smooths over 24 hours; this leads to over-provisioning
- Running all workloads on one capacity — one heavy pipeline starves interactive reports
- Not enabling surge protection — a runaway job can exhaust the capacity and throttle all other workloads
- Forgetting that mirroring is free to replicate but billed to query — a Mirroring-heavy workspace inflates CU consumption on reads

## See Also

- [`../../agents/fabric-admin.md`](../../agents/fabric-admin.md) — capacity management, FinOps, and throttling diagnosis
- [`../../agents/fabric-architect.md`](../../agents/fabric-architect.md) — workspace/domain/capacity topology design
- [`../../CLAUDE.md`](../../CLAUDE.md) — house opinion: capacity is shared and throttleable; size to average + smoothing
