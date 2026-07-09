---
title: Snowflake PSM-dashboard cost model
plugin: data-platform
path: plugins/data-platform/knowledge/snowflake-psm-dashboard-cost-model.md
last_reviewed: 2026-06-04
research_source: /tmp/research-snowflake-cost-perf.md
audience: [database-setup-guide, dashboard-builder, dashboard-performance-tuning skill]
refresh_triggers:
  - Snowflake re-prices Standard or Enterprise editions
  - Adaptive (Gen2) warehouses change cold-start behavior or minimum size
  - Dynamic Tables `TARGET_LAG` minimums change
  - Streamlit-in-Snowflake billing model changes (currently two-warehouse meter)
  - PSM portfolio grows past ~100 partners or 90-day window extends past 1 year
---

# Snowflake PSM-dashboard cost model — XS Standard, $350–450/mo Enterprise, attribution via JSON tags

> **Last reviewed:** 2026-06-04. Distilled from `/tmp/research-snowflake-cost-perf.md` (62 numbered + 11 supplementary citations across `docs.snowflake.com`, `select.dev`, Hightouch, Flexera, Keebo, Yuki, Stellans, Chaosgenius, Snowflake builders blog, etc.). Workload context: **single PSM, 25 partners, 90-day rolling window, 8am–6pm business hours, queried sporadically per page load**.

Pair with [`snowflake-warehouse-sizing-recipes.md`](snowflake-warehouse-sizing-recipes.md) for the per-workload sizing recipes.

---

## Default recommendation (opinionated)

For a single-PSM portfolio (25 partners, 90-day rolling, 8am–6pm access):

- **Edition:** Enterprise on-demand (most-likely monthly $350–450).
- **Compute:** **XS Standard for everything.** Streamlit query, Streamlit code, dbt build, ad-hoc — all XS Standard. Auto-suspend = 60s.
- **Materialization:** **Dynamic Tables** with `TARGET_LAG = '15 minutes'` upstream, `TARGET_LAG = DOWNSTREAM` for intermediate layers. Skip Materialized Views (single-base-table constraint kills them for any join-bearing rollup). Skip Streams+Tasks (hand-rolled change tracking).
- **Acceleration features to SKIP at this scale:**
  - Search Optimization Service — wrong access pattern (25 partners is too low-cardinality).
  - Clustering keys — fact tables won't be large enough (re-evaluate past ~50M rows).
  - Snowpark-Optimized warehouses — 1.5× credit rate, M-minimum, wrong tool for BI.
- **Attribution:** JSON `QUERY_TAG` per Streamlit session → `QUERY_ATTRIBUTION_HISTORY` joined to `QUERY_HISTORY`.
- **Guardrails:** per-warehouse Resource Monitor (suspend at 100% of monthly quota) + account-level Budget with daily forecast alert.

---

## Cost model — single PSM, 25 partners (most-likely monthly)

| Component | Configuration | Estimated credits/mo | $ at $3/credit (Enterprise on-demand) |
|---|---|---|---|
| **Streamlit query warehouse** (XS, AUTO_SUSPEND=60s) | PSM opens dashboard ~30× per business day × 3 min avg = 33h active + ~11h cold-start tax = **~44h/mo** | 44 | **$132** |
| **Streamlit code warehouse** (XS, runs Python; WebSocket holds ~15 min after activity) | **~60h/mo** | 60 | **$180** |
| **dbt build warehouse** (XS, hourly incremental, 60s minimum per resume) | 220 runs × ~90s ≈ **5.5h/mo** | 6 | **$18** |
| **Dynamic Table refresh** (serverless) | ~880 small-data refreshes/mo | 5 | **$15** |
| **Storage** (90-day rolling + Time Travel, ~10 GB) | 0.01 TB × $23 | — | **$1** |
| **Cloud-services overhead** (capped 10% of compute) | | 12 | **$36** |
| **TOTAL (on-demand Enterprise)** | | **~127 credits** | **~$382/mo** |

Source: `/tmp/research-snowflake-cost-perf.md` §10, derived from Costbench / Flexera pricing data retrieved 2026-06.

### Sensitivity bands

| Scenario | Monthly cost |
|---|---|
| **Optimistic** — capacity pricing ($1.80/credit), 50% result-cache hit rate halves query warehouse | **~$170–$220** |
| **Base case** — table above | **~$380** |
| **Pessimistic** — PSM keeps tab open all day (code warehouse runs 220h vs 60h), no cache hits, on-demand | **~$900–$1,100** |
| **Disaster** — someone enables M warehouse, forgets to auto-suspend, runs 24/7 | **~$2,800/mo from one warehouse** at Standard ($1/credit) |

**Most-likely-monthly: $350–$450** for Enterprise on-demand. The single biggest swing factor is whether the PSM tends to leave the tab open — instrument with `QUERY_ATTRIBUTION_HISTORY` before optimizing further.

---

## Dynamic Tables vs Materialized Views — verdict

**Use Dynamic Tables for the PSM rollups. Period.** [verified — `docs.snowflake.com/en/user-guide/dynamic-tables-comparison`, `docs.snowflake.com/en/user-guide/overview-view-mview-dts`]

| Dimension | Materialized Views | Dynamic Tables | Streams + Tasks |
|---|---|---|---|
| Joins | **Single base table only** | Multi-table joins, unions, window functions, CTEs | Anything you can write |
| Refresh trigger | Cloud-services layer, automatic on read | Scheduled by `TARGET_LAG` (min 1 minute) or `DOWNSTREAM` | Manual via task schedule |
| Compute billing | Serverless — opaque, no warehouse needed | **Explicit warehouse**, per-pipeline cost visible | Explicit warehouse |
| Freshness control | Implicit | `TARGET_LAG='15 minutes'` to `'1 hour'` typical | Whatever the task cron says |
| Operational overhead | Lowest | Low (declarative SQL, no orchestration) | Highest |

**Why MVs are the wrong tool:** the partner_daily_agg almost certainly joins `event_facts` with `partner_dim`, which breaks the MV single-base-table constraint. Snowflake's own docs guide to DTs in lieu of MVs for non-trivial aggregations. [verified — Medium / Mike Taveirne / Snowflake]

**Why Streams+Tasks is overkill:** hand-rolling change tracking and scheduling for what DTs do declaratively. The dbt-Snowflake community has converged on DTs as the preferred materialization for incremental aggregations in 2026.

**Recommended chain:**

```
raw.events                       — landed by Fivetran/ingest
  ↓ (dbt staging model, view)
stg.events_clean                 — typed, deduped
  ↓ (DT, TARGET_LAG='15 minutes')
mart.partner_daily_agg           — rollup keyed on (date, partner_id)
  ↓ (DT, TARGET_LAG=DOWNSTREAM)
mart.partner_90d_summary         — what the Streamlit dashboard queries
```

`DOWNSTREAM` means Snowflake only refreshes the intermediate layer when something further down asks — eliminating wasted refreshes for partners no one is currently viewing. [verified — Yuki Dynamic Tables guide]

Monitor `data_lag_seconds` via `SNOWFLAKE.ACCOUNT_USAGE.DYNAMIC_TABLE_REFRESH_HISTORY` and surface it as a "data freshness" tile in the dashboard so the PSM trusts the numbers.

---

## Skip Search Optimization Service at this scale

**Verdict: don't enable.** [synthesized from research §3]

SOS is built for **needle-in-haystack point lookups on large tables** (equality predicates on high-cardinality columns) where standard pruning fails. Cost components:

- **Storage:** ~¼ of the original table size for the search access path.
- **Compute:** background serverless credits, charged to the account (Snowflake cut this 80% in Aug 2024, but the tax is still non-zero).
- **Estimation:** `SYSTEM$ESTIMATE_SEARCH_OPTIMIZATION_COSTS('<table>')` returns build + maintenance estimates before `ALTER TABLE`.

**For a 25-partner / 90-day dataset:** the fact table is small (low millions of rows max), and `partner_id` is low cardinality (25 values). Pruning via clustering + pre-aggregation will do everything SOS would, free of the maintenance tax. **Revisit only if** (a) the portfolio grows to 1000+ partners OR (b) a high-cardinality lookup column (e.g., `transaction_id`) becomes the hot filter pattern. [verified — Analytics.today SOS guide, Snowflake docs SOS cost-estimation]

---

## Result-cache hygiene (free compute when it hits)

[verified — `community.snowflake.com/s/article/Understanding-Result-Caching`, npblue + Brontowise + Beyondkey corroboration]

**What must be identical for a cache hit:**

1. Query text matches byte-for-byte (case-folding of keywords is usually OK; comments-with-timestamps, lowercased keywords, alias changes commonly bust the cache in practice).
2. No non-deterministic functions: `CURRENT_TIMESTAMP`, `RANDOM()`, `UUID_STRING()`, `CURRENT_DATE` in some forms.
3. No external functions, no hybrid tables, no VOLATILE UDF/UDTF.
4. Underlying micro-partitions unchanged since the result was cached.
5. Role privileges match the cached query's privilege envelope.
6. Session parameters affecting result production (timezone, etc.) match.

**TTL:** 24 hours from last cache hit, hard ceiling 31 days from initial execution.

**Practical PSM-dashboard playbook:**

- Render the dashboard's underlying SQL deterministically — **no `CURRENT_TIMESTAMP` in the SELECT**, no comment-stamping per render. Render `WHERE date >= '2026-03-06'` as a literal that only changes once per day, not `WHERE date >= CURRENT_DATE - 90`.
- Run the dashboard under a **service role with stable privileges** — privilege diffs between users invalidate the cache.
- Page reloads within ~24h on unchanged data → free. This is the single biggest lever for the 8am–6pm sporadic-access pattern.

Verify hits with: `SELECT * FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY()) WHERE BYTES_SCANNED = 0` — those are the cache hits.

---

## Attribution: JSON query tags

[verified — `docs.snowflake.com/en/sql-reference/account-usage/query_attribution_history`, `docs.snowflake.com/en/user-guide/cost-attributing`, corroborated by select.dev, Seemore, Medium/Jon Osborn, Analytics.today]

Set a JSON `QUERY_TAG` in every Streamlit session before each user query:

```sql
ALTER SESSION SET QUERY_TAG = '{"app":"psm-dashboard","user":"matt@ravenpower.net","partner_view":"P-0042"}';
```

Then attribute monthly cost per dashboard user and per partner view:

```sql
SELECT
  PARSE_JSON(query_tag):user::STRING         AS dashboard_user,
  PARSE_JSON(query_tag):partner_view::STRING AS partner_id,
  SUM(credits_attributed_compute)            AS credits
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY
WHERE start_time >= DATE_TRUNC('MONTH', CURRENT_DATE)
  AND query_tag ILIKE '%psm-dashboard%'
GROUP BY 1, 2
ORDER BY credits DESC;
```

**Important nuance:** `credits_attributed_compute` includes resize/autoscale weight but **excludes idle warehouse time** — idle time still attributes to the warehouse, not individual queries. Pair with `WAREHOUSE_METERING_HISTORY` for full-warehouse accounting.

---

## Resource Monitors + Budgets — use both

[verified — `docs.snowflake.com/en/user-guide/resource-monitors`, `docs.snowflake.com/en/user-guide/budgets`, Flexera, Medium analyses]

| Tool | Scope | Enforcement | Notification |
|---|---|---|---|
| **Resource Monitor** | Warehouses only (no serverless, no AI) | **Can SUSPEND warehouses** at threshold | Up to 5 NOTIFY thresholds, email to ACCOUNTADMIN |
| **Budget** | Warehouses + databases + serverless + Cortex AI | Until Feb 2026: notify only. **Now: User-Defined Actions via stored procs.** | Daily forecasted-overage alerts; email + SNS / Event Grid / PubSub / webhook (Slack, Teams, PagerDuty) |

**Recommended PSM-dashboard setup:**

1. **Per-warehouse Resource Monitor on the Streamlit query warehouse**
   - Monthly quota: 30 credits (≈ $60–$90 depending on edition)
   - NOTIFY at 50/75/90%
   - **SUSPEND_IMMEDIATE at 100%** — better surprise than a $5k bill
2. **Account-level Budget**
   - Catches serverless surprises (DT refreshes, auto-clustering, Cortex if anyone enables it)
     - **Cortex/AI billing correction (effective 2026-04-01):** Cortex/AI now bills in a **separate AI Credit currency that is edition-independent (flat rate)** — see the dated figure in [`cloud-database-landscape-2026.md`](cloud-database-landscape-2026.md) (do not hardcode the rate here; it is quarterly-volatile). Any old edition-dependent Cortex-credit estimate (e.g. "~30 credits ≈ $60–90 depending on edition") **no longer applies**. Only warehouse-compute/storage Platform Credits stay edition-priced (so the per-warehouse quota above is unaffected). `[verify-at-use]`
   - Daily forecast alert to Slack via webhook
3. **Resource Monitors fire post-hoc** (5–10 min lag in credit accounting) — backstop, not a hard cap. Set `STATEMENT_TIMEOUT_IN_SECONDS = 120` on the dashboard role for runaway-query protection.

---

## Things to NOT do at this scale

- **Don't enable Snowpark-Optimized warehouses for BI.** 1.5× credit rate, M-minimum size (no XS available). Wrong tool for dashboard workloads. [verified — Yuki Snowpark guide + `docs.snowflake.com/en/user-guide/warehouses-snowpark-optimized`]
- **Don't enable Search Optimization.** Wrong access pattern; the maintenance tax exceeds the latency benefit at 25 partners / few-million rows.
- **Don't cluster the fact tables yet.** Below ~50M rows, the auto-reclustering serverless cost exceeds the pruning benefit. Re-evaluate at scale; when you do, lead with `CLUSTER BY (DATE_TRUNC('day', event_ts), partner_id)` — date on the leading edge for low-cardinality entities.
- **Don't set `AUTO_SUSPEND` below 60.** The 60-second minimum-charge rule means a warehouse firing every ~45s on `AUTO_SUSPEND = 30` pays two 60s minimums instead of one continuous billing window — strictly worse. [verified — Keebo auto-suspend post]
- **Don't pilot Adaptive (Gen2) warehouses on day one.** They can save 20–40% on variable workloads but cold-start behavior differs from Standard. Pilot only after Tier-A workload is steady. [vendor — Flexera Gen2 breakdown]

---

## Vendor-flagged claims NOT to cite as fact

- "Hightouch cut their bill by downsizing M→S for dbt Cloud jobs" — Hightouch self-published case study; the *structural* lesson (right-size first, optimize-slow-models second, auto-suspend last) is widely corroborated, the specific savings figure is not independently verified.
- "20–40% Gen2 savings" — Flexera figure; vendor-attributed.
- "Search Optimization 80% cheaper post-Aug-2024" — Snowflake announcement, corroborated by Medium/Shreya Agrawal; the magnitude has not been independently benchmarked.

---

## See also

- [`snowflake-warehouse-sizing-recipes.md`](snowflake-warehouse-sizing-recipes.md) — per-workload sizing recipes, auto-suspend tuning, the 60s sweet spot
- [`../skills/dashboard-performance-tuning/SKILL.md`](../skills/dashboard-performance-tuning/SKILL.md) — per-widget budgets + pre-aggregation tiers
- [`cloud-database-landscape-2026.md`](cloud-database-landscape-2026.md) — Snowflake's place in the broader database landscape (not the SMB default)
- Research source: `/tmp/research-snowflake-cost-perf.md`
