# Skill: cloud-database-comparison

> **Invoked by:** `database-setup-guide` (primary). Also consulted by `ravenclaude-core/architect` when running the `stack-selection` skill.
>
> **When to invoke:** any database selection for a new engagement; pricing-tier reasoning; HIPAA / SOC 2 / GDPR posture checks; "managed vs self-hosted" decisions.
>
> **Output:** an opinionated database choice with rationale + pricing claim (with retrieval date) + setup-complexity expectation + alt-stack overrides.

## The recommendation tiers (ranked, opinionated)

### Default — Supabase Pro
- **Tier price:** $25/mo + usage (per [supabase.com/pricing](https://supabase.com/pricing), retrieved 2026-05-21)
- **What you get:** 8 GB DB, 100k MAU, 100 GB file storage, auth, edge functions, realtime, REST + GraphQL auto-API
- **Why default:** lowest setup complexity of any option; Postgres + RLS native; one connection string handles the whole stack
- **When NOT to default:** Microsoft-stack engagement → Fabric F2; client already on Snowflake/Databricks → data sharing; HIPAA → upgrade to Supabase Team ($599/mo + HIPAA add-on)

### Microsoft alt — Fabric F2 reserved
- **Tier price:** ~$263/mo PAYG, ~$156/mo with 1-year reservation (Synapx 2026; verify against [azure.microsoft.com/pricing](https://azure.microsoft.com/en-us/pricing/details/microsoft-fabric/) before quoting)
- **What you get:** Lakehouse + Data Warehouse + Power BI + Data Factory + Notebooks in one capacity
- **Why pick:** Microsoft-stack client; Power BI embedding integration is unbeatable
- **When NOT to pick:** non-Microsoft client; portfolio dashboards (overkill)

### Postgres-branching alt — Neon
- **Tier prices:** Free (100 CU-hrs/mo, ~0.5 GB), Launch ($5/mo + usage), Scale ($0.222/CU-hour + SOC 2 Type 2 + HIPAA eligibility post-2025 Databricks acquisition) (per [neon.com/pricing](https://neon.com/pricing), retrieved 2026-05-21 via secondary)
- **Why pick:** Git-like database branching is the killer feature — branch-per-engagement-per-environment
- **When NOT to pick:** if you want auth/storage/realtime bundled — Supabase wins

### Analytics embedded — DuckDB / MotherDuck
- **DuckDB:** free, open-source, embeddable in Python/Node/browser-WASM. Use for in-process analytics in pipeline jobs, not for system-of-record.
- **MotherDuck (managed):** Free tier (3 users, 10 GB, 10 compute hours/mo); paid floor jumped from $25/mo to $250/mo (Dec 2025 – Feb 2026 restructure, secondary sources). Used to be the "cheap cloud DuckDB" — less so now.
- **When to pick:** small data (≤100 GB), DuckDB-friendly workflow, single-tenant analytics

### AWS path — RDS / Aurora
- **RDS:** free tier (first 12 mo new accounts, 750hr/mo, 20 GB; post-2025-07-15 sign-ups get $100 credit model instead — secondary source). $30-100/mo `db.t3.micro` post-free-tier.
- **Aurora Serverless v2:** $0.12/ACU-hr; 0.5 ACU minimum = $43.80/mo always-on floor.
- **When to pick:** existing AWS shop; IAM auth needed; predictable workload
- **2026 gotcha:** MySQL 5.7 / Postgres 11 extended-support rates doubled March 1, 2026 — push legacy clients to newer versions before onboarding

### Snowflake / Databricks / Redshift Serverless
- **Don't default** for engagements <$25K ACV.
- **Snowflake:** $2.00/credit Standard on AWS US, $23/TB/mo storage; practical SMB monthly $250-$2,000. Annual capacity contract reportedly $25k/year minimum.
- **Databricks SQL Serverless:** ~$0.70-$0.91/DBU US/EU; no published SMB minimum; practitioner reports ~$50k/yr Year 1.
- **Redshift Serverless:** $0.375/RPU-hr, 4 RPU base, 60s minimum. ~$1,080/mo always-on floor (auto-pause cuts this).
- **When to pick:** client engagement specifically requires it; their data is already there

### Edge / multi-tenant lightweight — Turso
- **Tiers:** Free (5 GB, 100 DBs, 500M reads/mo); Developer $4.99/mo; Scaler $24.92/mo; Pro $416.58/mo (per [turso.tech/pricing](https://turso.tech/pricing) secondary, 2026-05-21)
- **Why pick:** per-client database isolation cheaply; edge-distributed reads
- **When NOT to pick:** complex transactional workloads (LibSQL has scope limits)

## Decision matrix

| Engagement type | Default | Microsoft client | HIPAA | Cost-tightest |
|---|---|---|---|---|
| Case A (portfolio) | (no DB; static deploy) | (no DB; static deploy) | n/a | (no DB) |
| Case B (client deliverable) — single tenant | Supabase Pro | Fabric F2 reserved | Supabase Team + BAA | Postgres on Railway/Render ($7/mo) |
| Case B — multi-tenant | Supabase Pro + RLS | Fabric F2 reserved | Supabase Team + BAA, or Neon Scale | Turso (DB-per-tenant) |
| Case C (productized SaaS) | Supabase Pro + RLS | Fabric F2 reserved | Supabase Team / Neon Scale | Self-hosted Postgres on Hetzner |
| Case D (pipes only) | Postgres on client's cloud | Client's Fabric / Synapse | Client-mandated | n/a |

## Compliance posture (HIPAA / SOC 2 / GDPR)

- **Supabase Team ($599/mo + HIPAA add-on):** SOC 2, HIPAA-eligible with BAA
- **Neon Scale (post-2025 Databricks acquisition):** SOC 2 Type 2 + HIPAA eligibility verified
- **Fabric / Azure SQL:** Microsoft signs BAA on Azure; HIPAA-eligible services list applies
- **AWS RDS / Aurora:** HIPAA-eligible per AWS HIPAA services list; BAA required

**When the engagement is regulated, the client (not the consultant) pays the upgrade.** Surface this in the cost quote.

## Pricing-volatility discipline

Every pricing claim in this skill or in the output it produces:
- Carries a retrieval date (`per [vendor.com/pricing], retrieved YYYY-MM-DD`)
- Has a refresh trigger (typically quarterly)
- Surfaces "secondary source" or "primary verified" annotation

The hook ([`../hooks/flag-data-platform-smells.sh`](../hooks/flag-data-platform-smells.sh)) does not enforce retrieval dates programmatically (would be hard to pattern-match); the skill's review checklist does.

## Setup-complexity matrix (subjective; informs effort estimates)

| Option | First-hour setup | First-week production |
|---|---|---|
| Supabase | One click | Connection-string + RLS policies + denial test |
| Neon | One click | Connection-string + branching strategy |
| Railway / Render Postgres | One click | Connection-string |
| MotherDuck | 10 min | Auth + Parquet workflow |
| RDS / Aurora | 30 min + VPC | IaC + parameter group + security group |
| Fabric F2 | Tenant admin + ~1 hour | Workspace + capacity + Power BI |
| Snowflake | Trial signup + ~1 hour | Account + warehouse + role + capacity contract |

## Anti-patterns this skill flags

- Recommending Snowflake / Databricks for an engagement <$25K ACV
- Recommending RDS / Aurora when Supabase Pro covers the case at one-tenth the setup complexity
- Pricing claim without a retrieval date
- HIPAA engagement recommended on a tier that doesn't sign a BAA
- Recommending a new database when the client is already on Snowflake / Databricks (data sharing is the answer)
- MotherDuck recommended as a SMB-cheap option (the paid floor moved up materially in early 2026)
- "We'll add RLS later" — RLS retrofit on a populated multi-tenant table is harder than it looks

## References

- Knowledge: [`../knowledge/cloud-database-landscape-2026.md`](../knowledge/cloud-database-landscape-2026.md) — full pricing tables and decision criteria
- Skill: [`./stack-selection.md`](stack-selection.md) — Case A/B/C/D names the engagement shape first
- Skill: [`./rls-policy-authoring.md`](rls-policy-authoring.md) — what to ship alongside the schema
