---
scenario_id: 2026-06-05-cost-spike-log-analytics-and-orphans
contributed_at: 2026-06-05
plugin: azure-cloud
product: cost-management
product_version: "n/a"
scope: likely-general
tags: [finops, cost-management, log-analytics, rightsizing, orphaned, reservation]
confidence: high
reviewed: false
---

## Problem

A monthly Azure bill jumped ~35% with no new workload shipped, and a budget alert fired on the production subscription. The team's first instinct was to buy a reservation on the biggest VM "to lock in a discount." That would have committed spend against a resource that turned out to be over-sized — locking in the waste.

## Constraints context

- Segment: SaaS product, ~2 production subscriptions, no tagging discipline (`cost-center`/`application` mostly blank), so the portal's cost-by-resource view was hard to allocate.
- The bill surprise was a *mix* of causes wearing one number, which is the usual shape: a verbose new diagnostic setting, several orphaned resources from a deleted environment, and one genuinely over-provisioned PaaS tier.
- This is a FinOps engagement for `azure-ops-engineer`; nothing here is a security action.

## Attempts

- Tried: buying a Reserved Instance on the largest VM first. Stopped — the team hadn't confirmed the VM was right-sized, and **a reservation on an over-sized resource locks in the over-size**. Rightsize *then* commit. Outcome: aborted, correctly.
- Tried: finding the dominant cost driver from data instead of intuition — a Cost Management query grouped by `ResourceType` over the month. The top line was **Log Analytics ingestion**, not compute. A recently-added diagnostic setting was streaming verbose platform logs into the default-tier workspace. Outcome: the real #1 driver, which was not where anyone was looking.
- Tried (the moves that worked, in cost-lever order):
  1. **Log Analytics** — `Usage | summarize GB=sum(Quantity) by DataType | order by GB desc` found two noisy tables; switched the high-volume/low-query ones to the **Basic/Auxiliary Logs** tier, turned off the verbose-but-unused diagnostic categories, confirmed App Insights adaptive sampling wasn't disabled, and set a **daily cap at ~115%** of expected ingestion as a safety net (not at current, which leaves no headroom). Immediate, low-risk.
  2. **Orphans** — `az disk list --query "[?managedBy==null]"`, unattached public IPs and NICs, and snapshots from a torn-down environment. Free to delete, immediate.
  3. **Right-size then commit** — pulled Advisor + P95 CPU/memory metrics; the over-provisioned SQL tier was at ~10% DTU/RU utilization, so moved it to an autoscale/serverless tier. **Only after** 30 days of a stable right-sized baseline did a savings plan / reservation make sense.
  Outcome: the bill came back below the pre-spike baseline, and the reservation decision was deferred until the baseline was real.

## Resolution

The trap is that **the loud symptom (a big compute line, or "buy a reservation") is rarely the cheapest correct first lever.** Diagnose the actual dominant `ResourceType` from a Cost Management query, then pull levers in order of *time-to-savings × reversibility*: Log Analytics ingestion + orphaned resources (immediate, free, low-risk) before right-sizing (1–2 weeks, test after) before commitment purchases (only on a confirmed stable baseline). This is the team's FinOps tree — see [`../knowledge/azure-observability-and-finops.md`](../knowledge/azure-observability-and-finops.md) and the FinOps decision tree in [`../knowledge/azure-compute-decision-tree.md`](../knowledge/azure-compute-decision-tree.md).

**Action for the next consultant hitting this pattern:** query cost-by-`ResourceType` first — never assume it's compute. Check Log Analytics ingestion (the #1 surprise line item) and orphaned disks/IPs/snapshots before touching SKUs, and **never buy a reservation/savings plan to fix an over-sized resource — right-size first, commit on a 30-day baseline.** Push for `cost-center` + `application` tags so the next review is allocatable. Per-SKU pricing, tier discounts, and the Basic/Auxiliary-Logs table eligibility are version-volatile — `[verify-at-use]`; the plugin ships no baked-in prices.

**Sources (retrieved 2026-06-05):**
- Azure Cost Management + Billing docs — https://learn.microsoft.com/azure/cost-management-billing/
- Log Analytics / Azure Monitor cost optimization + table plans (Analytics / Basic / Auxiliary) — https://learn.microsoft.com/azure/azure-monitor/logs/cost-logs and https://learn.microsoft.com/azure/azure-monitor/logs/basic-logs-configure
- Azure savings plan vs reservations — https://learn.microsoft.com/azure/cost-management-billing/savings-plan/savings-plan-compute-overview

Pricing, discount percentages, and table-tier eligibility move — `[verify-at-use]` against current Microsoft pricing before quoting any number.
