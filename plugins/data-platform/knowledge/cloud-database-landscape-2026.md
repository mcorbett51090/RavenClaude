# Cloud database landscape 2026

> **Last reviewed:** 2026-05-21. Research-distilled reference for SMB-consulting use cases (4-6 engagements/year, $25-50k each). Sources: AWS / Azure / GCP pricing pages, Supabase / Neon / Planhat / Turso pricing pages, Snowflake / Databricks / MotherDuck pricing and product pages, secondary aggregators (Oliv.ai, CloudZero, Synapx, SaaSletter). Refresh when: (a) any major cloud provider restructures pricing, (b) a M&A event changes vendor status (Databricks/Neon precedent), (c) a new option enters the SMB-friendly tier, or (d) any pricing claim ages past 90 days without re-verification.

## Default recommendation (opinionated)

For a 4-6 engagement/year solo consulting practice, the **minimum viable database stack** is:

- **System of record:** **Supabase Pro** ($25/mo + usage as of 2026-05-21, per [supabase.com/pricing](https://supabase.com/pricing))
- **Analytics layer:** **DuckDB** (free, OSS, embedded in pipeline jobs)
- **HIPAA / SOC 2 work:** upgrade client to **Supabase Team** ($599/mo + HIPAA add-on) or push to **Neon Scale** (post-Databricks-acquisition HIPAA eligibility)
- **Microsoft-stack clients:** **Microsoft Fabric F2 reserved** (~$156/mo per Synapx 2026 reservation math)
- **Client already on Snowflake / Databricks:** use **data sharing**, not a new pipeline

**Explicitly avoid as defaults** (reach only when a specific client engagement justifies): Snowflake, Databricks, Redshift Serverless, Cosmos DB, Spanner, AlloyDB. Their minimum effective spend doesn't fit $25-50k engagement economics unless the client is already on it.

---

## AWS — RDS / Aurora / DynamoDB

### RDS (Postgres / MySQL / MariaDB / SQL Server / Oracle)
- **Free tier (pre-2025-07-15 accounts):** 750 hrs Single-AZ, 20 GB gp2 storage, 20 GB backup for 12 months [per AWS RDS Free Tier](https://aws.amazon.com/rds/free/)
- **Post-2025-07-15 accounts:** redesigned Free Plan with $100 credits instead of the legacy free tier (secondary source — verify on the live page)
- **Storage:** $0.115/GB-month for gp2 (per [AWS RDS Pricing](https://aws.amazon.com/rds/pricing/), retrieved 2026-05-21 via secondary aggregator)
- **Outbound transfer:** $0.09/GB
- **Typical SMB monthly:** $30-100/mo for `db.t3.micro` / `db.t4g.small` single-AZ; multi-AZ roughly doubles it
- **2026 gotcha:** **MySQL 5.7 / Postgres 11 extended-support Year-3 rates doubled March 1, 2026.** Push legacy clients to current versions before onboarding. (CloudBurn / CloudZero writeups; AWS announcement exists.)
- **When to pick:** existing AWS shop; IAM auth needed; predictable workload; multi-AZ HA required

### Aurora Serverless v2
- **Compute:** $0.12/ACU-hour; min 0.5 ACU; ~2 GiB RAM per ACU [per AWS Aurora Pricing](https://aws.amazon.com/rds/aurora/pricing/)
- **Idle floor:** ~$43.80/month at 0.5 ACU continuous
- **When to pick:** spiky workload on AWS; want autoscaling without managing instance classes
- **Avoid:** for steady high-utilization (provisioned + 1-yr RI cheaper above ~60-70% utilization per AWS guidance)

### DynamoDB
- **On-demand:** $1.25/M writes, $0.25/M reads
- **Always-free tier:** 25 GB storage, 25 WCU/25 RCU (provisioned only)
- **When to pick:** key-value lookups at scale; serverless apps
- **Avoid:** dashboard ad-hoc queries — punishes scans, no SQL

### Redshift Serverless
- **Compute:** $0.375/RPU-hour; 4 RPU base capacity minimum; 60-second minimum charge
- **Storage:** $0.024/GB/month managed
- **Always-on floor:** 4 × $0.375 = $1.50/hr ≈ $1,080/mo (auto-pause cuts this; real SMB analytics bills $100-300/mo for intermittent use)
- **3-year Serverless Reservations** launched Feb 2026 — up to 45% savings (per [AWS Whats New Feb 2026](https://aws.amazon.com/about-aws/whats-new/2026/02/amazon-redshift-serverless-three-year-reservations/))
- **When to pick:** AWS-native shop with sustained analytical queries
- **When NOT to default:** SMB consulting (the minimum doesn't fit)

---

## Azure — SQL DB / Postgres / Cosmos / Fabric

### Azure SQL Database
- **Free offer (lifetime per subscription):** 100k vCore-seconds + 32 GB data + 32 GB backup per database, up to 10 databases [per Microsoft Learn](https://learn.microsoft.com/en-us/azure/azure-sql/database/free-offer)
- **Serverless compute:** ~$0.5218/vCore-hour, 0.5 vCore minimum, auto-pause (Flexera blog citing Azure pricing)
- **When to pick:** Microsoft-stack client; MSDN/EA credits available

### Azure Database for PostgreSQL — Flexible Server
- **Burstable B1ms:** ~$12.41/mo PAYG (1 vCore, 2 GiB RAM); storage separate [per Azure Postgres Flexible Server pricing](https://azure.microsoft.com/en-us/pricing/details/postgresql/flexible-server/)
- **Cheapest "real Postgres" entry in Azure.** Good for Power Platform integrations.

### Azure Cosmos DB
- **Lifetime free tier:** 1000 RU/s + 25 GB on first account [per Microsoft Learn](https://learn.microsoft.com/en-us/azure/cosmos-db/free-tier)
- **Real foot-gun:** free tier does NOT apply to Serverless accounts
- **When to pick:** rare for SMB consulting; client must already use it

### Microsoft Fabric
- **F2 PAYG:** ~$263/mo
- **F2 with 1-year reservation:** ~$156/mo (~41% savings) (per Synapx 2026 / DataTako secondary sources — verify against [azure.microsoft.com/pricing](https://azure.microsoft.com/en-us/pricing/details/microsoft-fabric/) before quoting)
- **What you get at F2:** Lakehouse + Data Warehouse + Power BI + Data Factory + Notebooks in one bill
- **When to pick:** Microsoft-stack client. **This is the default alt-stack to Supabase for M365-aligned engagements** and dovetails with the `power-platform` plugin.

---

## GCP — Cloud SQL / AlloyDB / BigQuery / Spanner

### Cloud SQL
- Managed Postgres / MySQL / SQL Server. Cheaper than AlloyDB; comparable to RDS.
- **When to pick:** existing GCP shop or BigQuery integration

### AlloyDB
- **~39% markup over Cloud SQL Enterprise Plus.** Data storage ~$0.339/GB vs Cloud SQL SSD ~$0.17/GB (Bytebase + Google Cloud blog).
- **Avoid:** overkill for SMB consulting

### BigQuery
- **On-demand:** $6.25/TiB scanned (some sources quote $5/TB — verify on the live page). First 1 TB/month free. 10 GB active storage free.
- **Storage:** $0.02/GB active, $0.01/GB long-term (>90 days unmodified)
- **When to pick:** ad-hoc analytics with predictable scan volumes; the free tier is genuinely useful for solo work
- **Default destination for GA4** — native export, free, daily + intraday

### Spanner
- Global, distributed; minimum 100 PU
- **Avoid:** overkill for SMB

---

## Modern serverless Postgres

### Supabase
- **Free:** 2 projects, 500 MB DB, 50k MAU, projects pause after 7 days inactivity
- **Pro:** **$25/mo + usage; 8 GB DB, 100k MAU, 100 GB file storage** — verified [supabase.com/pricing](https://supabase.com/pricing) 2026-05-21
- **Team:** $599/mo with SOC 2
- **HIPAA:** requires Team plan + BAA + HIPAA add-on [per Supabase HIPAA Compliance docs](https://supabase.com/docs/guides/security/hipaa-compliance)
- **Setup complexity:** lowest of all options — `supabase init`, get URL + anon key. Includes auth, storage, edge functions, realtime, REST + GraphQL auto-API.
- **The default.** Especially for embedded-in-website use case.

### Neon
- **Free:** 100 CU-hrs/month/project, ~0.5 GB storage
- **Launch:** $5/mo minimum, $0.106/CU-hour, $0.35/GB-month storage
- **Scale:** $0.222/CU-hour; includes SOC 2 Type 2 and **HIPAA eligibility** gained after Databricks acquisition May 2025 [per Databricks press release](https://www.databricks.com/company/newsroom/press-releases/databricks-agrees-acquire-neon-help-developers-deliver-ai-systems)
- **Killer feature:** instant database branching (Git-like) — a real differentiator for a consultant running 4-6 simultaneous engagements

### PlanetScale
- **Postgres single-node:** $5/mo
- **MySQL HA (Metal):** $50/mo
- **No free plan.**
- **When to pick:** specifically need Vitess sharding (rare for SMB) or migrating from existing MySQL

### Railway / Render
- **Railway Hobby:** $5/mo with $5 included usage
- **Render Postgres small:** ~$7/mo baseline
- **When to pick:** budget-tightest single-tenant Postgres for Case B engagements

---

## Modern analytical / lakehouse

### Snowflake
- **Standard credits $2.00 on AWS US** on-demand; storage $23/TB/mo compressed
- **AI/Cortex billing split out (effective 2026-04-01; retrieved 2026-07-09):** Snowflake now meters Cortex/AI features in a **separate AI Credit currency** at a **flat $2.00/credit (global) / $2.20 (regional), independent of edition**. Only **Platform Credits** (warehouse compute + storage, non-AI) remain edition-priced. Billing-breakout release note dated 2026-04-06: `docs.snowflake.com/en/release-notes/2026/other/2026-04-06-ai-services-billing-breakout`. `[verify-at-use — pricing, subject to change; primary docs.snowflake.com/.../pricing 403'd automated fetch, cross-referenced via secondaries]`
- **Practical SMB monthly:** $250-$2,000 with auto-suspend (CloudZero / Definite analyses)
- **Annual capacity contract reportedly $25k/year** minimum for committed pricing (secondary)
- **Avoid as a default** for 4-6 engagement/year practice. Reach when client is already there.

### Databricks SQL Serverless
- **~$0.70-$0.91/DBU US/EU** (Databricks SQL Pricing, secondary)
- **No published SMB minimum.** Practitioner reports ~$50k/yr Year 1.
- **Avoid as a default.**

### MotherDuck
- **2026 pricing reset:** Free tier ($0, 3 users, 10 GB, 10 compute hours/mo). **Paid floor jumped from $25/mo (Lite) to $250/mo (Business)** in Dec 2025 – Feb 2026 (Layerbase, Tasrie IT writeups corroborate).
- **GA achieved June 2024** [per MotherDuck blog](https://motherduck.com/blog/announcing-motherduck-general-availability-data-warehousing-with-duckdb/)
- **When to pick:** small data (≤100 GB), DuckDB-friendly workflow. The free tier is still attractive for prototyping; the paid floor is no longer SMB-cheap.

### ClickHouse Cloud
- **Development tier:** $1-$193/mo. Compute $0.22-$0.75/CU-hour; storage $25.30-$50/TB-month [per ClickHouse Pricing](https://clickhouse.com/pricing)
- **When to pick:** event/log analytics at scale. Overkill for client engagement data; right tool if a client has telemetry-style needs.

---

## Embedded / file-based

### DuckDB
- **Free, open-source.** Embeddable in Python/Node/browser (WASM).
- **Production-ready for embedded read-heavy analytics** (Kestra, MotherDuck, Tinybird writeups; the Talkdatatomelol "Is DuckDB Production-Ready?" post counsels caution for write-heavy or multi-writer)
- **When to pick:** dashboard reads pre-aggregated client data; bulk transform/compute step in a pipeline

### SQLite
- Battle-tested, single-writer constraint matters. Fine for embedded read paths.

### Turso (LibSQL)
- **Free:** 5 GB storage, 100 DBs, 500M row reads/mo
- **Developer:** $4.99/mo
- **Scaler:** $24.92/mo
- **Pro:** $416.58/mo (per [turso.tech/pricing](https://turso.tech/pricing) secondary, 2026-05-21)
- **Production-ready in 2026.** Cloudflare D1 GA April 2024; LiteFS stabilized; Turso embedded replicas widely deployed.
- **When to pick:** multi-tenant per-client database isolation; edge-distributed reads; very-low-cost-per-tenant

---

## Decision matrix (the quick lookup)

| Engagement profile | First pick | M365 client | HIPAA | Cost-tightest |
|---|---|---|---|---|
| Case A (portfolio) | (no DB; static deploy) | n/a | n/a | n/a |
| Case B single-tenant | Supabase Pro | Fabric F2 reserved | Supabase Team + BAA | Railway/Render Postgres |
| Case B multi-tenant | Supabase Pro + RLS | Fabric F2 reserved | Supabase Team + BAA OR Neon Scale | Turso DB-per-tenant |
| Case C (productized SaaS) | Supabase Pro + Cube semantic layer | Fabric F2 reserved | Supabase Team / Neon Scale | Self-hosted Postgres on Hetzner |
| Case D (pipes only) | Postgres on client's cloud | Client's Fabric | Client-mandated | n/a |

## 2024-2026 macro shifts worth remembering

1. **Databricks acquired Neon May 2025** — brought HIPAA eligibility to Scale plan. Verified.
2. **MotherDuck price floor jumped $25 → $250/mo** in Dec 2025 – Feb 2026. Still has a free tier; the "cheap cloud DuckDB" story is weaker.
3. **AWS RDS extended-support rates doubled March 1, 2026** for MySQL 5.7 / Postgres 11. Push legacy clients off before onboarding.
4. **AWS Free Tier redesigned for accounts created after July 15, 2025** — $100 credit model instead of always-on micro instances. (Secondary sources; verify on AWS Free Tier page.)
5. **Redshift Serverless 3-year Reservations** launched Feb 2026. Verified.
6. **Microsoft Fabric** matured into the primary Microsoft analytics product; Synapse positioning weakened.
7. **DuckDB / Turso / SQLite-on-the-edge** crossed the production-readiness threshold for read paths in 2026.

## Refresh triggers for this document

- Any cloud provider restructures pricing (Snowflake, Databricks restructures are most likely)
- Major M&A event (vendor acquisition, public listing)
- New SMB-friendly tier from any vendor
- Any pricing claim ages past 90 days without re-verification
- Government regulation that changes compliance posture for any tier (HIPAA, GDPR, state privacy)
