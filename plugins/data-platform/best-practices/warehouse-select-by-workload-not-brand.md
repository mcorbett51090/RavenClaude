# Select the warehouse by workload and engagement economics — not by brand familiarity

**Status:** Pattern — strong default for every engagement-start database decision; deviate only with a written reason tied to a specific client constraint.

**Domain:** Warehouse / database selection

**Applies to:** `data-platform`

---

## Why this exists

The most expensive mistake in a dashboard engagement is reaching for an analytical lakehouse (Snowflake, Databricks, Redshift Serverless) when the workload is a few-GB transactional system-of-record serving a handful of dashboard viewers. The minimum effective spend on those platforms doesn't fit $25-50k engagement economics — and worse, the database choice often gets made *after* the dashboard framework is picked, which gets the layering backwards. The discipline is: name the **workload shape** (OLTP system-of-record vs. embedded read-heavy analytics vs. genuine large-scale OLAP) and the **engagement economics** (ACV, viewer count, ownership at handoff) *first*, then pick the cheapest option that serves that shape. Brand familiarity ("the client knows Snowflake") is a real input — but it belongs in the override-with-rationale column, not the default.

## How to apply

Match workload → default, then apply the override triggers. The full pricing-dated landscape lives in [`../knowledge/cloud-database-landscape-2026.md`](../knowledge/cloud-database-landscape-2026.md).

```
Workload shape                          → Default (SMB consulting)        Override trigger
─────────────────────────────────────────────────────────────────────────────────────────
OLTP system-of-record + dashboard reads → Supabase Pro (Postgres+RLS)     M365 client → Fabric F2
Branch-per-engagement isolation         → Neon (Git-like DB branching)    —
AWS-native shop, IAM auth required      → RDS Postgres                    —
Embedded read-heavy analytics in jobs   → DuckDB (free, OSS)              managed → MotherDuck
Multi-tenant edge-distributed reads     → Turso (DB-per-tenant)           —
Genuine large-scale OLAP, sustained     → Snowflake / BigQuery / Databricks  ONLY if ACV/scale justifies
Client ALREADY on Snowflake/Databricks  → data sharing, NO new pipeline   —
```

```yaml
# stack-decision-record.md fragment — the decision is auditable, not vibes.
workload_shape: oltp-system-of-record-plus-dashboard-reads
viewer_count: 5-50
acv_band: "<$25k"
warehouse_pick: supabase-pro
warehouse_rationale: "Postgres+RLS+auth+storage in one connection string; lowest setup complexity."
override_considered: { snowflake: "ruled out — minimum spend doesn't fit ACV", fabric: "n/a — not M365" }
pricing_claim: "Supabase Pro $25/mo as of 2026-05-21"   # [verify-at-build] re-confirm before quoting
```

**Do:**
- Make the DB choice **before** the ELT and dashboard choices — get the layering right (the engagement-start order).
- Default to **Supabase Pro** for non-Microsoft engagements, **Fabric F2 reserved** for M365-stack — everything else is override-with-rationale.
- Use DuckDB as the **analytics-side** embedded engine, not the system of record where customer writes live.
- When the client is already on Snowflake/Databricks, recommend **data sharing**, not a new pipeline.

**Don't:**
- Default to Snowflake / Databricks / Redshift Serverless for engagements `<$25K` ACV without a specific reason.
- Pick the warehouse to match a brand the stakeholder recognizes, when the workload doesn't need it.
- Quote any tier price without a retrieval date — pricing in this domain moves quarterly (house opinion #9).

## Edge cases / when the rule does NOT apply

- **Client is already on a lakehouse** — don't re-pick; use data sharing (the no-pipeline path).
- **Hard compliance regime** (HIPAA/SOC 2/GDPR) — compliance can override the cost default (e.g. Supabase Team + BAA, Neon Scale) — surface the constraint before recommending a tier.
- **Genuine OLAP scale** (billions of rows, sustained concurrent analytical queries) — the lakehouse default is correct *because* the workload demands it; that's the rule applied, not broken.

## See also

- [`../knowledge/cloud-database-landscape-2026.md`](../knowledge/cloud-database-landscape-2026.md) — retrieval-dated pricing + the decision matrix per Case
- [`../knowledge/data-platform-decision-trees.md`](../knowledge/data-platform-decision-trees.md) — the warehouse-selection decision tree
- [`./warehouse-partition-and-cluster-for-cost.md`](./warehouse-partition-and-cluster-for-cost.md) — once selected, control scan cost
- [`../agents/database-setup-guide.md`](../agents/database-setup-guide.md) — owns the DB-setup recommendation
- [`../skills/stack-selection/SKILL.md`](../skills/stack-selection/SKILL.md) — Case A/B/C/D drives the default

## Provenance

Distilled from `database-setup-guide.md` ("Database choice precedes ELT and dashboard choice"; "Snowflake/Databricks are wrong defaults for SMB consulting <$25K ACV"), `cloud-database-landscape-2026.md` default recommendation + decision matrix, and CLAUDE.md house opinions #10 + anti-pattern "database choice happens after the dashboard framework is picked." `[verify-at-build]` all $/mo figures — quarterly refresh discipline.

---

_Last reviewed: 2026-05-30 by `claude`_
