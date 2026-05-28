# Azure observability & FinOps

**Last reviewed:** 2026-05-28 · **Confidence:** high ([Monitor cost](https://learn.microsoft.com/azure/azure-monitor/fundamentals/cost-usage), [cost optimization in Monitor](https://learn.microsoft.com/azure/azure-monitor/fundamentals/best-practices-cost), retrieved 2026-05-28).
**Owner:** `azure-ops-engineer`.

## Observability (house opinions #11)
- **Azure Monitor** is the platform; **Log Analytics** is the store; **Application Insights** is the app-telemetry layer — use **workspace-based** App Insights (enables Basic Logs, commitment tiers, retention-by-type).
- **OpenTelemetry** is the instrumentation standard — use the Azure Monitor OpenTelemetry distro; configure only the signals you need.
- **Cost is dominated by Log Analytics ingestion + retention.** Control it: **sampling** (App Insights — biggest lever; minimal metric distortion), **Basic Logs** table plan for high-volume debug/audit tables (cheap ingest, query-time charge), **commitment tiers** (daily-minimum discount), **daily caps** (preventative budget), retention tuning (default 31d; long-term retention to 12y via search jobs).
- Decide whether to **combine operational + security data** in one workspace (Sentinel pricing applies to all data in a Sentinel-enabled workspace).

## FinOps (house opinion #10)
- **Budgets + cost alerts on every subscription** (set thresholds, automated alerts before overruns).
- **Cost analysis**: group by meter/resource; **daily cost-analysis emails** (Subscribe); **CSV exports** for deep analysis; **Azure Advisor** cost recommendations.
- **Capacity reservations / commitment tiers** for steady workloads; pay-as-you-go for spiky.
- **Tag-based chargeback** (owner/cost-center/env/app — see [`azure-landing-zones-and-governance.md`](azure-landing-zones-and-governance.md)).
- The metric is **cost-per-business-outcome**, surfaced as a client deliverable (cost review — `[consultant]` audience).

## Governance enforcement (house opinion #13)
- **Azure Policy** + **Defender for Cloud** on by default across all subscriptions (assigned at MG scope).
- **Diagnostic settings** routed to Log Analytics / Event Hub (SIEM); secure data in transit (TLS 1.2) + at rest (AES-256, default).

> Cost reviews + observability dashboards are consultant deliverables — pair with `ravenclaude-core/documentarian` for the write-up. Security analytics (Sentinel/Defender response) escalates to `ravenclaude-core/security-reviewer`.
