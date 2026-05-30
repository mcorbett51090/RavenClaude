# Wire diagnostic settings to Log Analytics from day one — not after the first incident

**Status:** Pattern — strong default; a prod resource with no diagnostic settings is a resource you can't debug or audit after the fact.

**Domain:** Observability / Governance

**Applies to:** `azure-cloud`

---

## Why this exists

Azure resource logs are **not collected by default** — until you create a **diagnostic setting** pointing the resource's logs/metrics at a destination, they're discarded, and you **cannot retroactively get logs for an incident that already happened**. Teams discover this during the first prod incident, when the data they need never existed. The discipline is to wire **diagnostic settings → a workspace-based Log Analytics workspace** at *provisioning time*, for every resource that matters, as part of the IaC — not as a post-incident scramble. At fleet scale this is enforced with a **`DeployIfNotExists` Azure Policy** so any new resource auto-gets a diagnostic setting (the ALZ pattern). Sending logs to one workspace also unlocks cross-resource KQL, alerting, and (with the security data) Sentinel — house opinion #11 (observability = OTel + workspace-based App Insights) sits on top of this foundation.

## How to apply

Attach a diagnostic setting (use the `allLogs` category group + `AllMetrics`) to each resource at deploy time; enforce it estate-wide with a `DeployIfNotExists` policy.

```bicep
// Per-resource: ship all logs + metrics to the central workspace at provisioning time
resource diag 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'to-law'
  scope: keyVault                                  // any resource that emits logs
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs:    [ { categoryGroup: 'allLogs', enabled: true } ]   // not hand-picked categories
    metrics: [ { category: 'AllMetrics', enabled: true } ]
  }
}
```

```text
# Fleet enforcement: assign the built-in DeployIfNotExists policy/initiative
#   "Deploy Diagnostic Settings to Log Analytics workspace" at the MG/subscription scope
#   so every NEW resource auto-gets a diagnostic setting (ALZ pattern; needs a managed identity).
```

**Do:**
- Provision the **diagnostic setting with the resource** in IaC; use the **`allLogs` category group** so new log categories are picked up automatically, plus `AllMetrics`.
- Send to a **workspace-based** Log Analytics workspace (the same one App Insights uses — house opinion #11).
- Enforce estate-wide with a **`DeployIfNotExists`** policy at MG scope so coverage doesn't depend on each author remembering.
- Pick **one destination type per setting**; add a separate Event Hub setting if a SIEM needs a stream.

**Don't:**
- Ship a prod resource with **no** diagnostic setting and expect logs to be there after an incident — they won't exist.
- Hand-pick individual log categories when `allLogs` is available — you'll miss categories added later.
- Rely on per-author discipline at fleet scale — use the policy.

## Edge cases / when the rule does NOT apply

- **Cost-sensitive high-volume log tables** belong on the **Basic Logs** plan or get sampled — collect them, but tune the plan (see the cost rule); don't drop them to save money blindly.
- **Some resources require a target selection** before the setting can be added (e.g. Storage sub-resources) — that's a UX wrinkle, not an exemption.
- **The `audit` category group** is enough for compliance-only resources where full `allLogs` is noise — a deliberate, narrower choice, not "no logging."
- **Enabling the `audit` diagnostic category does not, by itself, turn on Azure SQL database auditing** — that's a separate SQL setting.

## See also

- [`../knowledge/azure-observability-and-finops.md`](../knowledge/azure-observability-and-finops.md) — Monitor / Log Analytics / workspace-based App Insights / OTel
- [`./ops-control-log-analytics-cost.md`](./ops-control-log-analytics-cost.md) — keeping the ingestion this rule turns on affordable
- [`./gov-azure-policy-as-guardrails.md`](./gov-azure-policy-as-guardrails.md) — the `DeployIfNotExists` policy that enforces coverage
- [`../agents/azure-ops-engineer.md`](../agents/azure-ops-engineer.md) — owns observability + governance

## Provenance

Codifies house opinion #11/#13 from [`../CLAUDE.md`](../CLAUDE.md) §3. Grounded in Microsoft Learn [Diagnostic settings](https://learn.microsoft.com/azure/azure-monitor/platform/diagnostic-settings) (`allLogs`/`audit` category groups; logs not collected until a setting exists; one destination per type; SQL-audit caveat) and [ALZ policy-driven governance](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/enterprise-scale/dine-guidance) (`DeployIfNotExists` deploys diagnostic settings) — retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
