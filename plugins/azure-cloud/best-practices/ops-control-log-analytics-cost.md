# Control Log Analytics cost deliberately — sampling, Basic Logs, commitment tiers, daily caps

**Status:** Primary diagnostic — when an Azure bill is unexpectedly high, check Log Analytics ingestion + retention first.

**Domain:** FinOps / Observability

**Applies to:** `azure-cloud`

---

## Why this exists

The single most common "why is my Azure bill so high?" surprise is **Log Analytics ingestion + retention** — telemetry is easy to turn on (`ops-diagnostic-settings-to-log-analytics-from-day-one` tells you to) and easy to leave on full-volume, full-retention, full-price. The mistake people make in response is the *opposite* over-correction: ripping out diagnostic settings to save money, blinding themselves before the next incident. The right move is to keep the data but **tune the cost levers**: **App Insights sampling** (the biggest lever, minimal metric distortion), the **Basic Logs** table plan for high-volume debug/audit tables (cheap ingest, pay-per-query), **commitment tiers** (a daily-minimum discount once steady volume is known), **daily caps** (a preventative ceiling), and **retention-by-type** (default 31d; archive to long-term only what compliance needs). House opinion #10 names workspace-cost control explicitly.

## How to apply

Diagnose with cost analysis (group by meter), then apply the lever that fits the table's role: sample chatty app telemetry, Basic-Logs the high-volume audit/debug tables, commit once volume is steady, cap to prevent runaway.

```text
Chatty app telemetry, volume-driven cost   -> App Insights sampling (biggest lever, low distortion)
High-volume debug/audit table, rarely queried -> Basic Logs table plan (cheap ingest, query-time charge)
Steady, predictable daily ingest           -> Commitment tier (daily-minimum discount)
Need a hard budget ceiling                  -> Daily cap (preventative; may drop late-day data)
Data needed for compliance, not daily query -> short interactive retention + long-term archive
```

```bicep
// Workspace daily cap + a Basic Logs table plan for a high-volume table
resource law 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: lawName
  location: location
  properties: { workspaceCapping: { dailyQuotaGb: 50 } }   // preventative ceiling
}
// (App Insights sampling is configured in the OTel/App Insights distro, not here:
//   set the sampling ratio in the Azure Monitor OpenTelemetry exporter.)
```

**Do:**
- Diagnose first: **cost analysis grouped by meter/table**; the worst offenders are usually a couple of high-volume tables.
- Apply **sampling** to app telemetry (biggest lever); **Basic Logs** to high-volume rarely-queried tables; **commitment tiers** once steady; **daily caps** as a ceiling.
- Tune **retention by data type** — short interactive retention, long-term archive only for compliance-mandated tables.
- Set **subscription budgets + alerts** so the workspace cost shows up before the invoice (see the cost-guardrails rule).

**Don't:**
- Delete diagnostic settings to cut cost — you re-blind the estate; tune the plan instead.
- Set a **daily cap so low it drops incident-time data** — caps are a ceiling, not a target; size them above normal peak.
- Combine operational + security data in a workspace without realizing **Sentinel pricing then applies to all of it**.

## Edge cases / when the rule does NOT apply

- **Security/Sentinel tables** often can't use Basic Logs and need full retention for hunting — don't sample them away; that's a deliberate analytics-vs-cost tradeoff with the security owner.
- **Low-volume estates** may sit below the cost-tuning threshold entirely — don't add commitment-tier complexity to a workspace ingesting a few GB/day.
- **Compliance retention** (multi-year) is a requirement, not waste — archive it cheaply; don't drop it to save ingest cost.
- Security-analytics retention/Sentinel decisions → `ravenclaude-core/security-reviewer`.

## See also

- [`../knowledge/azure-observability-and-finops.md`](../knowledge/azure-observability-and-finops.md) — the cost levers (sampling, Basic Logs, commitment tiers, daily caps, retention)
- [`./ops-diagnostic-settings-to-log-analytics-from-day-one.md`](./ops-diagnostic-settings-to-log-analytics-from-day-one.md) — the ingestion this rule keeps affordable (don't undo it)
- [`./cost-budgets-tags-and-policy-guardrails.md`](./cost-budgets-tags-and-policy-guardrails.md) — budgets that surface the workspace cost early
- [`../agents/azure-ops-engineer.md`](../agents/azure-ops-engineer.md) — owns FinOps + observability

## Provenance

Codifies house opinion #10 from [`../CLAUDE.md`](../CLAUDE.md) §3. Grounded in Microsoft Learn [cost optimization in Azure Monitor](https://learn.microsoft.com/azure/azure-monitor/fundamentals/best-practices-cost) + [Monitor cost/usage](https://learn.microsoft.com/azure/azure-monitor/fundamentals/cost-usage) (sampling, Basic Logs table plan, commitment tiers, daily caps, retention-by-type, Sentinel-pricing caveat) as captured in the observability/FinOps knowledge file (retrieved 2026-05-28; re-confirmed 2026-05-30).

---

_Last reviewed: 2026-05-30 by `claude`_
