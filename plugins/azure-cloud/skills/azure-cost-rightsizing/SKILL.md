---
name: azure-cost-rightsizing
description: "FinOps playbook for diagnosing Azure overspend and rightsizing resources — covers Cost Management query patterns, compute/storage/Log Analytics levers, reservation vs savings plan decisions, and the budget-alert setup checklist."
---

# Azure Cost Rightsizing

## When to Use This Skill

Use when a subscription bill is unexpectedly high, when preparing a periodic FinOps review, or when provisioning new workloads and you need to size them correctly from the start.

## 1. Diagnosis: Where Is the Cost Coming From?

```bash
# Top 10 resource types by cost — last 30 days
az costmanagement query \
  --scope /subscriptions/$SUBSCRIPTION_ID \
  --type Usage \
  --timeframe MonthToDate \
  --dataset-granularity None \
  --dataset-grouping '[{"type":"Dimension","name":"ResourceType"}]' \
  --dataset-aggregation '{"totalCost":{"name":"Cost","function":"Sum"}}' \
  --query "properties.rows | sort_by(@, &[1]) | reverse(@) | [0:10]"
```

Top cost drivers in typical workloads:

| Driver | First lever |
|---|---|
| Compute (VMs, App Service) | Rightsize SKU; enable autoscale; Reserved Instances |
| Log Analytics / Sentinel | Sampling, Basic Logs tier, daily cap, commitment tier |
| Storage (LRS/GRS) | Lifecycle policies; access tier (Hot/Cool/Archive) |
| Bandwidth (egress) | Move workloads to same region; CDN for static content |
| Azure SQL / Cosmos | DTU/vCore rightsize; serverless for dev; Reservations |

## 2. Compute Rightsizing Decision

| Utilization (CPU + memory P95) | Action |
|---|---|
| < 20% | Downsize 1-2 SKU tiers; consider Burstable (B-series) for dev |
| 20-60% | Good fit; evaluate Reserved Instance for prod |
| 60-80% | Current SKU appropriate; enable autoscale to handle bursts |
| > 80% sustained | Upsize or add instances; check for code-level optimization first |

```bash
# Get average CPU for an App Service Plan (last 7 days)
az monitor metrics list \
  --resource /subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.Web/serverFarms/$PLAN \
  --metric "CpuPercentage" \
  --interval P1D \
  --aggregation Average \
  --start-time $(date -d '7 days ago' -u +%Y-%m-%dT%H:%MZ)
```

## 3. Log Analytics Cost Levers

Log Analytics is often the surprise line item. Apply in order:

1. **Identify noisy tables:** `Usage | summarize DataGB = sum(Quantity) by DataType | order by DataGB desc`
2. **Switch verbose tables to Basic Logs** (8x cheaper, query-on-demand only): `SecurityEvent`, `DeviceProcessEvents`
3. **Sampling** for App Insights telemetry (adaptive sampling on by default — verify it's not disabled)
4. **Daily cap** as a safety net (set to 110% of expected daily ingestion)
5. **Commitment tier** at 100+ GB/day (10-65% discount vs pay-as-you-go)

## 4. Reservation vs Savings Plan

| Scenario | Recommendation |
|---|---|
| Stable, predictable compute (same VM family, same region, 1-3 yr) | **Reserved Instance** — up to 72% discount |
| Mixed/flexible compute (different VM families or regions) | **Azure Savings Plan** — up to 65% discount, flexible |
| Dev/test workloads | **Dev/Test pricing** (requires MSDN/Visual Studio subscription) |
| Short-lived or bursty | Pay-as-you-go or Spot (non-prod only) |

Reservations are a commitment, not a reservation of capacity. Always model the break-even:
`Break-even utilization = Reserved cost / (On-demand cost × hours)`

## 5. Budget and Alert Setup

```bash
# Create a budget with 80% and 100% forecast alerts
az consumption budget create \
  --budget-name "myapp-prod-monthly" \
  --amount 500 \
  --category Cost \
  --time-grain Monthly \
  --start-date "2026-06-01" \
  --end-date "2027-06-01" \
  --resource-group rg-myapp-prod-eastus \
  --notifications '{
    "Actual_80": {
      "enabled": true, "operator": "GreaterThan", "threshold": 80,
      "thresholdType": "Actual", "contactEmails": ["finops@example.com"]
    },
    "Forecast_100": {
      "enabled": true, "operator": "GreaterThan", "threshold": 100,
      "thresholdType": "Forecasted", "contactEmails": ["finops@example.com"]
    }
  }'
```

## 6. Monthly FinOps Review Checklist

- [ ] Cost Management: top 5 resource types this month vs last month
- [ ] Orphaned resources: disks, public IPs, NICs with no attached resource
- [ ] Underutilized compute: Advisor recommendations reviewed and acted on
- [ ] Log Analytics: ingestion breakdown reviewed; Basic Logs candidates identified
- [ ] Reservations: utilization > 80%? Any expired or under-utilized reservations?
- [ ] Budgets: no alerts fired without a known cause

## Pitfalls

- Setting a daily cap on Log Analytics at current ingestion — leaves no headroom; the cap should be 110-120% of expected
- Buying reservations for dev/test instances that are frequently deleted and re-created
- Ignoring bandwidth costs — cross-region data transfers are billed; same-region is free
- Not tagging resources with `cost-center` and `application` — makes cost allocation impossible in Cost Management

## See Also

- [`../../agents/azure-ops-engineer.md`](../../agents/azure-ops-engineer.md) — observability, FinOps, and governance enforcement
- [`../../agents/azure-architect.md`](../../agents/azure-architect.md) — landing zone subscription topology and cost isolation
- [`../../CLAUDE.md`](../../CLAUDE.md) — house opinion: budgets and cost alerts per subscription
