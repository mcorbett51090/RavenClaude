# Budget + tag + policy every subscription from creation — cost guardrails, not cost reports

**Status:** Pattern — strong default; a subscription with no budget, no enforced tags, and no SKU policy is a cost incident waiting to happen.

**Domain:** FinOps / Governance

**Applies to:** `azure-cloud`

---

## Why this exists

Cost discipline that's purely *reporting* ("the bill was high last month") is always too late. The guardrails go on at **subscription creation**, via **subscription vending**, so spend is bounded and attributable *before* anyone deploys: a **budget with alert thresholds** (actual + forecasted) per subscription so overruns page someone early; **enforced tags** (`owner` / `cost-center` / `environment` / `application`) via an `Append`/`Modify`/`deny`-untagged Azure Policy so every resource is attributable for chargeback; and **Azure Policy guardrails** restricting **allowed SKUs/locations** so a `Standard_M128ms` or an out-of-geography region can't be spun up by accident. House opinions #9 (tag + name to CAF) and #10 (budgets + cost alerts per subscription) combine here. These are *preventative* controls — they shape what can be created — not a monthly retrospective.

## How to apply

Stamp budget + tag-enforcement + allowed-SKU/location policy at subscription creation (subscription vending), so the guardrails predate the workloads.

```bicep
// Subscription-scoped budget with actual + forecasted alert thresholds
targetScope = 'subscription'
resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: 'sub-monthly'
  properties: {
    category: 'Cost'
    amount: 5000
    timeGrain: 'Monthly'
    timePeriod: { startDate: '2026-06-01' }
    notifications: {
      actual80:     { enabled: true, operator: 'GreaterThan', threshold: 80,  thresholdType: 'Actual',     contactEmails: [ 'finops@contoso.com' ] }
      forecast100:  { enabled: true, operator: 'GreaterThan', threshold: 100, thresholdType: 'Forecasted', contactEmails: [ 'finops@contoso.com' ] }
    }
  }
}
```

```text
# Enforce attribution + bound the catalog via Azure Policy (assigned at MG/subscription):
#   - "Require a tag on resources" (owner / cost-center / environment / application) — Modify/Append/deny
#   - "Allowed locations"   -> restrict to compliant geographies (residency + cost)
#   - "Allowed VM SKUs"     -> block oversized/expensive SKUs by default
```

**Do:**
- Create a **budget per subscription** with **Actual** (e.g. 80%) + **Forecasted** (e.g. 100%) notifications wired to an action group / FinOps contact.
- Enforce the **CAF tag set** (`owner`/`cost-center`/`environment`/`application`) with policy so chargeback is possible; pair with CAF naming (`abbr-workload-env-region-instance`).
- Constrain **allowed locations + SKUs** with policy so cost (and residency) can't be blown by a mis-sized deploy.
- Stamp all of this at **subscription creation** via vending — guardrails before workloads.

**Don't:**
- Treat cost as a monthly report — by then the spend already happened; the controls are preventative.
- Put cost tags **only** in policy that elevated users can mutate — subscription-scope tags are mutable by elevated principals, so don't rely on them as a security boundary.
- Skip the budget on "small" subscriptions — those are exactly where a runaway SKU hides.

## Edge cases / when the rule does NOT apply

- **Sandbox** subscriptions under the loose-policy archetype may relax SKU/location policy — but **keep the budget** (sandboxes are where surprise spend lives).
- **Reserved/committed workloads** are deliberately steady — budgets there are a tripwire for anomalies, not a sign of over-spend; size thresholds accordingly.
- **Tag enforcement via `deny`** can block legitimate emergency deploys — prefer `Modify`/`Append` (auto-tag) over hard `deny` for the day-one rollout, then tighten.
- Cost reviews as a **client deliverable** pair with `ravenclaude-core/documentarian`.

## See also

- [`../knowledge/azure-observability-and-finops.md`](../knowledge/azure-observability-and-finops.md) — budgets, cost analysis, tag-based chargeback
- [`../knowledge/azure-landing-zones-and-governance.md`](../knowledge/azure-landing-zones-and-governance.md) — CAF tags + naming + subscription vending
- [`./gov-azure-policy-as-guardrails.md`](./gov-azure-policy-as-guardrails.md) — the policy mechanism these guardrails use
- [`./ops-control-log-analytics-cost.md`](./ops-control-log-analytics-cost.md) — the most common single line item these budgets catch
- [`../agents/azure-ops-engineer.md`](../agents/azure-ops-engineer.md) — owns FinOps

## Provenance

Codifies house opinions #9 + #10 from [`../CLAUDE.md`](../CLAUDE.md) §3. Grounded in Microsoft Learn [`Microsoft.Consumption/budgets`](https://learn.microsoft.com/azure/templates/microsoft.consumption/budgets) (Actual/Forecasted `thresholdType`, `contactEmails`/`contactGroups`, threshold 0–1000), [define your tagging strategy](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/azure-best-practices/resource-tagging) + [Govern tags](https://learn.microsoft.com/azure/governance/policy/tutorials/govern-tags), and the FinOps/landing-zone knowledge files — retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
