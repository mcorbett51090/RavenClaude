# Fabric 2026 capability map (GA vs preview)

**Last reviewed:** 2026-06-19 · **Confidence:** medium-high — Fabric ships **monthly**, so this is the freshness anchor the Researcher staleness sweep re-dates. Every row carries a retrieval date; verify GA/preview status before quoting to a client.
**Owner:** all agents (the "cite the status with a retrieval date" discipline, house opinion #9).
**Source:** [What's new in Fabric](https://learn.microsoft.com/fabric/fundamentals/whats-new) + per-feature docs, retrieved 2026-05-28. **Spark Runtime 2.0 (→ Spark/Delta 4.1) and OneLake security (→ GA + default-on) re-verified 2026-06-11 via the Microsoft-Learn MCP.** **Runtime 1.3 corrected Delta 3.1 → 3.2 (Spark 3.5.5 / Python 3.11) and its end-of-support (2026-09-30 → LTS through March 2027) added — re-verified 2026-06-18 via the Microsoft-Learn MCP ([runtime](https://learn.microsoft.com/fabric/data-engineering/runtime), [runtime-1-3](https://learn.microsoft.com/fabric/data-engineering/runtime-1-3), [lifecycle](https://learn.microsoft.com/fabric/data-engineering/lifecycle)).** **June-2026 sweep (re-verified 2026-06-19, Microsoft-Learn MCP):** Fabric Graph → **GA**; Eventstream Kafka/Service Bus connectors → **GA-announced, source page still "(preview)"** `[verify-at-use]` — **UPDATE (re-verified 2026-07-08, Microsoft-Learn MCP): the Apache Kafka + Azure Service Bus source pages are no longer titled "(preview)"**, and the eventstream source table lists both without a "(preview)" tag (only Azure Data Explorer + Anomaly Detection carry it) — the docs have caught up to the June-2026 GA, so treat the connectors as GA (drop the "page-still-preview" caveat); Fabric Data Agents in M365 Copilot → **GA-announced, consume page still "(preview)"** `[verify-at-use]`.

## Spark runtimes (get this right — affects perf defaults)

| Runtime | Spark / Delta | Status (2026-05-28) |
|---|---|---|
| 1.2 | Spark 3.4 / Delta 2.4 | **EOSA** — end of support 2026-03-31 (already past); migrate off |
| **1.3** | Spark 3.5.5 / Delta 3.2 | **current GA** (LTS) — production default; **end-of-support 2026-09-30, then LTS Oct 2026 → March 2027** `[verify-at-use]` ([runtime](https://learn.microsoft.com/fabric/data-engineering/runtime), [lifecycle](https://learn.microsoft.com/fabric/data-engineering/lifecycle), Microsoft-Learn 2026-06-18) — its support clock is ~3 mo out, so plan the Runtime 2.0 migration as 2.0 reaches GA |
| 2.0 | Spark 4.1 / Delta 4.1 (Python 3.13) | **public preview** — not the production default yet. **Updated Spark 4.0→4.1 / Delta 4.0→4.1 / Python 3.12→3.13**; the Python bump is a **breaking change** — re-publish every Environment that has libraries or Spark jobs fail "No module found" (re-verified 2026-06-11, [Runtime 2.0](https://learn.microsoft.com/fabric/data-engineering/runtime-2-0)) |

- **Native Execution Engine (NEE)** — Velox/Gluten vectorized engine, **GA on Runtime 1.3 and 2.0**; the biggest free Spark perf/cost lever. Recommend it by default.
- **Autotune** (`spark.ms.autotune.enabled`) — **Runtime-1.2-only**, incompatible with high-concurrency mode; **deprecated path**. Do **not** recommend it; NEE is the modern lever.
- **Starter pools** (Medium nodes, 5-10 s session start) vs **custom pools/environments** (node size, libraries, Spark props, ~3 min or ~5 s with a custom live pool in Full mode). **Python notebooks** (2-core, instant) vs **PySpark notebooks** (distributed). ([spark-compute](https://learn.microsoft.com/fabric/data-engineering/spark-compute))

## Stores & engineering

| Capability | Status |
|---|---|
| Lakehouse, Warehouse, SQL analytics endpoint | GA |
| **SQL database in Fabric** (OLTP, auto-mirrors to OneLake) | GA |
| **Cosmos DB in Fabric** (NoSQL/vector, auto-mirrors, CU-billed, Entra-only) | GA-track (verify) |
| **Materialized lake views** | GA-track — verify; declarative medallion |
| Schema-enabled lakehouses | GA (prerequisite for the OneLake-security **data-preview** pane; not required for Spark RLS/CLS enforcement) |
| OneLake shortcuts, external data sharing (cross-tenant) | GA |
| **Fabric Graph** (labeled-property-graph over OneLake; GQL/NL2GQL, CU-billed, no separate SKU, min 100 GB storage) | **GA (June 2026)** — was preview since Oct 2025; *graph-as-AI-data-source in Fabric Data Agent stays preview* `[verify-at-use]` ([Graph overview](https://learn.microsoft.com/fabric/graph/overview)) |

## Power BI / semantic models
- **Direct Lake on SQL** (fallback to DirectQuery) — GA. **Direct Lake on OneLake** (no fallback, composite models) — GA, the modern recommendation. PBIP/TMDL, live editing — GA. ([Direct Lake](https://learn.microsoft.com/fabric/fundamentals/direct-lake-overview))

## Real-Time Intelligence
- Eventstream, Eventhouse, KQL DB/queryset, Real-Time dashboard, **Activator**, anomaly detection — GA. **Eventhouse endpoint for Lakehouse** (Oct 2025), entity diagram in KQL DB (Nov 2025, preview), Azure Monitor Logs into Fabric via Eventstream (Sep 2025). Digital twin builder — preview. **Eventstream Apache Kafka + Azure Service Bus source connectors — GA (June 2026, docs caught up 2026-07-08)** (what's-new RTI table: hardened reliability, SASL_SSL/SASL_PLAINTEXT/Entra auth, production throughput). **Re-verified 2026-07-08 (Microsoft-Learn MCP): the [Add Apache Kafka source](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-source-apache-kafka) and [Add Azure Service Bus source](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-source-azure-service-bus) pages are no longer titled "(preview)", and the eventstream source table lists both with no "(preview)" tag** — the earlier "GA-announced/page-still-preview" caveat is now resolved; treat as GA (`[verify-at-use]` GA SLAs per your contract). **Real-Time Dashboards Live Refresh — GA (June 2026)**. ([RTI overview](https://learn.microsoft.com/fabric/real-time-intelligence/overview))

## AI / Data Science (v0.2.0 agent territory)
- **Fabric Data Agents** — conversational read-only NL Q&A over Lakehouse/Warehouse/semantic-model/KQL/ontology via Azure OpenAI Assistant APIs; Foundry / Copilot Studio / M365 Copilot integration. Source control for data agents — preview.
- **Operations Agents** — ontology-driven, act on live streams via Activator/Power Automate.
- **Copilot in Fabric** — notebooks (`/fix`, chat pane), DAX, KQL, Data Factory. AI functions, MLflow autologging, AutoML, Data Wrangler, model endpoints, GraphQL API — GA/various. ([analyze-train-data](https://learn.microsoft.com/fabric/fundamentals/analyze-train-data))

## Platform / ALM / governance
- Git integration + deployment pipelines — GA (some items preview). **Fabric CLI v1.5 — GA (March 2026)**. **Bulk import/export item-definition APIs — preview (March 2026)**. OneLake catalog (Explore/Govern/Secure), domains, Purview, sensitivity labels — GA. **OneLake security + OneLake data access roles — GA (May 2026)**, and **being enabled by default on all supported items by end of May 2026** (re-verified 2026-06-11, [Fabric what's-new](https://learn.microsoft.com/fabric/fundamentals/whats-new)). Data-access roles (Read / **ReadWrite**, folder/RLS/CLS) apply to **Lakehouse, Azure Databricks Mirrored Catalog, Mirrored Databases**; third-party/external engine enforcement is the **authorized-engine model** (engines retrieve policy + effective access via OneLake APIs; OneLake stays the single source of truth) — [data access control model](https://learn.microsoft.com/fabric/onelake/security/data-access-control-model). **Eventhouse RLS** remains preview `[verify-at-use]`.

## How to keep this current
Re-run the Microsoft Learn `what's-new` search on each Researcher sweep; re-date this file; correct any row whose status changed; bump the plugin patch version if a default (e.g. the production runtime, NEE availability) changes.
