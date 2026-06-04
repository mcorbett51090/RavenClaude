# Snowflake for PSM Dashboard — Cost + Performance (2026-06-04)

**Workload context:** single Partner Success Manager (PSM) portfolio. 25 partners. 90-day rolling window. Access pattern is 8am–6pm business hours, queried every page load by one user (the PSM), with occasional executive ad-hoc visits. The model below assumes the dashboard is queried sporadically (i.e., not pinned full-time) and that the data backing it lives in Snowflake.

> Methodology note: docs.snowflake.com and select.dev returned HTTP 403 to WebFetch in this session, so primary-doc verification ran through WebSearch result-card excerpts plus cross-corroboration against ≥2 independent secondary sources for every load-bearing claim. Where a number is only single-sourced (e.g., select.dev's "20–45% capacity discount"), it is flagged below.

---

## 1. Warehouse sizing recipes (per workload tier)

| Tier | Workload | Recommended size | Rationale |
|---|---|---|---|
| **A. Dashboard read** (pre-aggregated, sub-second) | Streamlit/Power BI page load, hits a rollup table with WHERE partner_id IN (...) | **XS Standard** | 1 credit/hr; pre-aggregated tables don't benefit from more cores; doubling size doubles credit burn for marginal latency gain on small scans. ([Stellans][1], [Flexera Gen2][2], [Chaosgenius][3]) |
| **B. dbt incremental builds** (the rollups that feed Tier A) | Nightly/hourly model refresh, small data (90-day window, 25 partners) | **XS or S Standard** | Hightouch publicly downsized M→S for dbt Cloud jobs and "greatly reduced credit consumption" with only slight runtime increase. ([Hightouch][4]) |
| **C. Ad-hoc exploration** (PSM occasionally drills past pre-aggs) | Manual SELECTs against raw fact tables | **S Standard**, separate warehouse | Isolation prevents an exploratory full scan from blocking the dashboard XS. Workload isolation is the #1 sizing principle. ([Flexera 8-best-practices][5]) |
| **D. ML/Snowpark/Cortex** | Out of scope for this PSM dashboard | — | Snowpark-optimized warehouses cost **1.5× per credit** and don't exist below M — wrong tool for BI. ([Yuki Snowpark][6], [Snowflake docs Snowpark-optimized][7]) |

**Key constraint:** Snowpark-Optimized warehouses are **only available M and larger** and consume **1.5× credits/hr** vs. Standard at the same size. They are wrong for dashboard workloads — confirmed by both Snowflake docs and Yuki's 2026 guide. ([Yuki Snowpark][6])

**Adaptive (Gen2) warehouses** (2026 feature) intelligently scale up only the slowest portion of a query plan and can deliver 20–40% lower cost than scaling the warehouse manually, per Flexera's Gen2 breakdown. Worth evaluating once the workload stabilizes but not load-bearing for Tier A. ([Flexera Gen2][2])

---

## 2. Result cache best practices

**The cache is free compute when it hits — the goal is to maximize hit rate.**

**What must be identical for a cache hit:** ([npblue][8], [Snowflake community KB][9], [Brontowise][10])

1. Query text must match byte-for-byte (whitespace and case-folding of identifiers are usually OK; **aliases, comments-with-timestamps, lowercased keywords commonly bust the cache** in practice).
2. No non-deterministic functions: `CURRENT_TIMESTAMP`, `RANDOM()`, `UUID_STRING()`, `RANDSTR()`, `CURRENT_DATE` in some forms — all break reuse.
3. No external functions, no hybrid tables, no UDF/UDTF marked VOLATILE.
4. Underlying table micro-partitions must not have changed since the result was cached.
5. The role executing must have privileges that match the cached query's privilege envelope.
6. Session-level parameters affecting result production (timezone, etc.) must match.

**TTL:** results persist **24 hours from the last cache hit**, extending up to a hard ceiling of **31 days from initial execution**. Each new hit re-anchors the 24h window but cannot exceed the 31d wall. ([npblue][8], [Beyondkey][11], [Brontowise][10])

**Toggle:** `USE_CACHED_RESULT` session parameter (default TRUE) controls reuse and can be set at account/user/session level. ([Snowflake community KB][9])

**Practical PSM-dashboard playbook:**
- Render the dashboard's underlying SQL deterministically — **no `CURRENT_TIMESTAMP` in the SELECT**, no comment-stamping per render. Render `WHERE date >= '2026-03-06'` as a literal that only changes once per day, not `WHERE date >= CURRENT_DATE - 90` (which technically can hit cache but is fragile across the date boundary).
- Run the dashboard under a **service role with stable privileges** — privilege diffs between users invalidate the cache.
- Page reloads within ~24h on unchanged data → free. This is the single biggest lever for the 8am–6pm sporadic-access pattern.

---

## 3. Search Optimization — when worth it

**Verdict for this workload: don't enable, the access pattern is wrong for SOS.**

SOS (Search Optimization Service) is built for **needle-in-haystack point lookups on large tables** (equality predicates on high-cardinality columns) where standard pruning fails. Cost components: ([Snowflake docs SOS][12], [Snowflake docs SOS cost estimation][13], [Analytics.today SOS][14], [Medium Snowflake Builders][15])

- **Storage:** roughly **¼ of the original table size** for the search access path (varies with distinct values).
- **Compute (build + maintain):** background serverless credits charged to your account. Snowflake cut this 80% in Aug 2024 by optimizing the background warehouse process. ([Medium Shreya Agrawal][16])
- **Estimation:** `SYSTEM$ESTIMATE_SEARCH_OPTIMIZATION_COSTS('<table>')` returns build + ongoing-maintenance estimates before you ALTER TABLE. ([Snowflake docs estimate function][17])

**Decision rule:** SOS pays back only when (a) the table is **large** (many micro-partitions), (b) queries filter on **high-cardinality** columns that don't appear in the clustering key, (c) latency is **business-critical**, and (d) the same table is queried often enough to amortize the maintenance burn. ([Analytics.today SOS][14])

**For a 25-partner / 90-day PSM dataset:** the fact table is small (low millions of rows max), and `partner_id` is low cardinality (25 values). Pruning via clustering + pre-aggregation will do everything SOS would, free of the maintenance tax. Revisit only if the portfolio grows to 1000+ partners OR a high-cardinality lookup column (e.g., transaction_id) becomes the hot filter.

---

## 4. Clustering keys for partner-keyed access

**Verdict: cluster the rollup tables, not the raw facts. Lead with date, then partner_id.**

**The cardinality rule:** a clustering key needs enough distinct values to prune effectively, but few enough that rows group meaningfully into micro-partitions. Pure `partner_id` (25 values) is **too low cardinality** — every partition would contain every partner. ([Stellans clustering keys][18], [Integrate.io][19], [Medium Ember Crooks data-driven][20])

**Multi-column ordering:** Snowflake checks min/max per micro-partition column-by-column in the order declared. **Put the lower-cardinality column first**, but only if it actually prunes; then add a higher-cardinality column. For date+entity workloads, the well-attested pattern is `CLUSTER BY (DATE_TRUNC('day', event_ts), partner_id)` — date on the leading edge, partner second. ([Medium Ember Crooks][20], [select.dev clustering+MV][21], [Flexera clustering][22])

**The dbt-community proof point:** "billions of e-commerce orders saw query times reduce from 90s → 12s by clustering on (customer_id, order_date)" — but note their lead column is the entity, because in their workload customer_id has high cardinality. For PSM's 25-partner case, **lead with date**. ([Medium Manik Hossain dbt][23])

**Automatic reclustering costs:** serverless background credits, no dedicated warehouse needed; storage costs increase because old micro-partitions are marked deleted but retained for Time Travel / Fail-safe. The standard advice: **cast timestamps to date before clustering** to reduce reclustering churn. ([Snowflake docs auto-reclustering][24], [Snowflake engineering blog][25], [Keebo clustering][26])

**Warning from the field:** "around 80% of customers deploy cluster keys very poorly, which can lead to significant costs with little benefit." Always measure with `SYSTEM$CLUSTERING_INFORMATION` before and after. ([Stellans clustering keys][18])

**For PSM specifically:**
- 90-day rolling window + 25 partners → fact table is probably small enough that **no clustering key is needed** on the rollups (a single XS scan finishes sub-second). Skip clustering unless the rollup grows past ~50M rows or pruning becomes the bottleneck.
- If you do cluster: `CLUSTER BY (DATE_TRUNC('day', event_ts), partner_id)`.

---

## 5. Dynamic Tables vs Materialized Views vs Streams+Tasks (current state)

**Verdict: Dynamic Tables for the PSM rollups. Period.**

| Dimension | Materialized Views | Dynamic Tables | Streams + Tasks |
|---|---|---|---|
| Joins | **Single base table only** | Multi-table joins, unions, window functions, CTEs | Anything you can write |
| Refresh trigger | Snowflake cloud-services layer, automatic on read | Scheduled by `TARGET_LAG` (**min 1 minute**) or `DOWNSTREAM` | Manual via task schedule |
| Compute billing | Serverless — **opaque, no warehouse needed** | **Explicit warehouse**, per-pipeline cost visible | Explicit warehouse |
| Freshness control | Implicit (Snowflake decides) | `TARGET_LAG = '5 minutes'` to `'1 hour'` typical | Whatever the task cron says |
| Operational overhead | Lowest | Low (declarative SQL, no orchestration) | Highest |

Sources: [Snowflake docs DT comparison][27], [RisingWave][28], [Tacnode][29], [Flexera materialized views][30], [Medium Mike Taveirne][31], [Yuki Dynamic Tables][32], [Hexstream][33].

**Why MVs are the wrong tool here:** the single-base-table limit kills them for any rollup that joins partner_facts to a partner_dim. Snowflake's own docs guide is to use DTs in lieu of traditional MVs for any non-trivial aggregation. ([Medium Mike Taveirne][31])

**Why Streams+Tasks is overkill:** you'd be hand-rolling change tracking and scheduling for something DTs do declaratively. The dbt-Snowflake community has converged on **DTs as the preferred materialization for incremental aggregations** in 2026. ([Medium PD Dutta DT+dbt][34])

**Target lag for PSM:** business-hours dashboard with no need for sub-minute freshness → **`TARGET_LAG = '15 minutes'`** during 8am–6pm. Or `DOWNSTREAM` if the rollup is only read by another DT, in which case Snowflake refreshes lazily. ([Snowflake builders DT pipeline guide][35], [Yuki Dynamic Tables][32])

---

## 6. Streamlit-in-Snowflake cost model

**Two warehouses, both meter:** ([Snowflake docs Streamlit billing][36], [Snowflake docs runtime environments][37], [Snowflake discussion forum][38])

1. **Code/runtime warehouse** — runs the Python. Kept alive by a **WebSocket connection that expires ~15 minutes after the viewer's last activity** (mouse movement resets the timer). Custom `streamlitSleepTimeoutMinutes` can be set 5–240 min in `config.toml`.
2. **Query warehouse** — runs SQL the app issues. Honors its own `AUTO_SUSPEND`/`AUTO_RESUME`.

Both warehouses are billed independently. The code warehouse's 60-second-minimum-on-resume is the silent tax: **every time the PSM opens the dashboard cold, you pay 60 seconds on the code warehouse + 60 seconds on the query warehouse** even if both queries finish in 2s.

**Container runtime** alternative bills via Snowpark Container Services compute-pool credits instead — usually more expensive for sporadic BI but cheaper for sustained always-on dashboards. Not worth it for the 8am–6pm PSM pattern.

**Cost levers:**
- Point Streamlit's code warehouse and query warehouse at the **same XS** (cuts the cold-start tax in half).
- Set `AUTO_SUSPEND = 60` on that warehouse.
- Lower `streamlitSleepTimeoutMinutes` from 15 → 5 if the PSM tends to leave the tab open while away. ([Snowflake docs sleep timer][39])
- **Suspend the Streamlit app object** outside business hours (manual or scheduled task). ([Snowflake docs Streamlit billing][36])

---

## 7. Auto-suspend + auto-resume tuning

**Minimum is 60 seconds. The "60-second sweet spot" is the documented sweet spot for sporadic BI, but Keebo argues it's often suboptimal.** ([Stellans auto-suspend][40], [Keebo auto-suspend][41], [Unravel][42])

**The 60-second-minimum-charge trap:** Snowflake bills per-second **after** a 60s minimum charge each time a warehouse resumes. A warehouse that runs for 8s and suspends is billed 60s. So setting `AUTO_SUSPEND = 30` on a workload that fires every ~45s is **strictly worse** than `AUTO_SUSPEND = 60`, because you pay two 60s minimums instead of one continuous billing window. ([Keebo auto-suspend][41])

**Tier recommendations (corroborated across Stellans, Keebo, Unravel, Seemore):**

| Workload | AUTO_SUSPEND | Why |
|---|---|---|
| Dashboard / BI sporadic (PSM page loads) | **60s** | Sweet spot. Aggressive enough to stop idle burn at 6pm, lenient enough to amortize cold starts during a working session. |
| Streamlit code warehouse | **60s** | Match query warehouse so resumes align. |
| dbt incremental builds (scheduled) | **60s** (or even keep separate per-run warehouse) | Job-scoped warehouses can use 60s; never use long suspends for batch. |
| Always-on production warehouses (NOT this workload) | 5–10 minutes | Reuse caches across continuous query streams. |

**The Hightouch lesson** ([Hightouch][4]): they cut Snowflake spend by downsizing first, then optimizing the slow models. Auto-suspend tuning came after — it's a marginal lever vs. right-sizing.

---

## 8. Pre-aggregation table patterns

**The schema pattern** (corroborated across dbt community, Snowflake builders, AtScale): ([Snowflake DT pipeline][35], [AtScale][43], [Princeton IT][44], [Medium Manik dbt materialization][45])

```
raw.events                       — landed by Fivetran/ingest
  ↓ (dbt staging model)
stg.events_clean                 — typed, deduped, view or table
  ↓ (DT, TARGET_LAG='15 minutes')
mart.partner_daily_agg           — rollup keyed on (date, partner_id)
  ↓ (DT, TARGET_LAG=DOWNSTREAM)
mart.partner_90d_summary         — what the Streamlit dashboard queries
```

**Star schema rule:** keep the dashboard pointed at a **single wide rollup** (the third tier above), not a multi-table join. The dashboard query becomes `SELECT * FROM mart.partner_90d_summary WHERE partner_id = :p AND date >= :start` — sub-second on XS, cache-friendly.

**Freshness model:**
- Top of chain: `TARGET_LAG = '15 minutes'` (or align to upstream Fivetran sync cadence).
- Downstream of chain: `TARGET_LAG = DOWNSTREAM` → Snowflake only refreshes when something further down asks, eliminating wasted refreshes for partners no one is currently viewing. ([Yuki Dynamic Tables][32])

**Monitoring:** `DYNAMIC_TABLES` metadata view exposes `data_lag_seconds` per table — surface this on a "data freshness" tile in the Streamlit dashboard so the PSM trusts the numbers. ([Yuki Dynamic Tables][32])

**Why not Materialized Views for the rollup:** the partner_daily_agg almost certainly joins event_facts with partner_dim, breaking the MV single-base-table constraint. (See §5.)

---

## 9. Resource monitors + alerts

**Use both Resource Monitors AND Budgets. They cover different surfaces.**

| Tool | Scope | Enforcement | Notification |
|---|---|---|---|
| **Resource Monitor** | Warehouses only (no serverless, no AI) | **Can SUSPEND warehouses** at threshold | Up to 5 NOTIFY thresholds (percentage of quota), email to ACCOUNTADMIN with notifications on |
| **Budget** | Warehouses + databases + serverless + Cortex AI | Until Feb 2026: no automated action. **Now: User-Defined Actions via stored procs** | Daily forecasted-overage alerts, email + SNS / Event Grid / PubSub / webhook (Slack, Teams, PagerDuty) |

Sources: [Snowflake docs resource monitors][46], [Snowflake docs budgets][47], [Snowflake docs cost monitoring][48], [Flexera resource monitors][49], [Medium Santhosh K L budgets-vs-rm][50], [Medium Alexander budget actions][51].

**Recommended PSM-dashboard setup:**

1. **Per-warehouse Resource Monitor on the Streamlit query warehouse**
   - Monthly quota: 30 credits (≈ $60–$90 depending on edition)
   - NOTIFY at 50%, 75%, 90%
   - SUSPEND_IMMEDIATE at 100% (hard kill — better surprise than a $5k bill)
2. **Account-level Budget**
   - Catches serverless surprises (DT refreshes, auto-clustering, Cortex if anyone enables it).
   - Daily forecast alert to Slack via webhook.
3. **Resource Monitors fire post-hoc** (5–10 min lag in credit accounting) — they are a backstop, not a hard cap. Don't rely on them for runaway-query protection; use statement timeouts for that.

---

## 10. Cost model: single-PSM portfolio (25 partners, 90-day rolling, 8am-6pm access)

### Assumptions

| Variable | Value | Source |
|---|---|---|
| Snowflake credit price (Enterprise, AWS us-east) | **$3/credit** on-demand; ~$1.65–$2.40 with capacity | [Costbench][52], [Flexera pricing][53] |
| XS warehouse rate | **1 credit/hr** | [Snowflake docs warehouses overview][54], [Definite][55] |
| Storage rate (active) | **$23/TB-month** on-demand AWS US East | [Costbench][52] |
| 60-second minimum charge per warehouse resume | Yes | [Stellans][1], [Keebo][41] |
| Business-hours window | 8am–6pm × Mon–Fri = 10h × ~22 days = 220h/mo | derived |

### Per-warehouse breakdown (monthly, on-demand Enterprise)

| Component | Configuration | Estimated credits/mo | $ at $3/credit |
|---|---|---|---|
| **Streamlit query warehouse** (XS, AUTO_SUSPEND=60s) | PSM opens dashboard ~30× per business day, 3 minutes average active per session → 90 min/day × 22 days = **33h active** + cold-start overhead (~22 days × 30 resumes × 60s = 11h tax) ≈ **44h/mo** | 44 | **$132** |
| **Streamlit code warehouse** (XS, same usage profile, runs Python) | Similar resume pattern; WebSocket holds ~15 min after activity so fewer cold starts but longer hold time. Estimate **60h/mo**. | 60 | **$180** |
| **dbt build warehouse** (XS, hourly incremental during business hours) | 10 runs/day × 22 days = 220 runs × ~90s avg (but 60s minimum) = **~5.5h/mo** | 6 | **$18** |
| **Dynamic Table refresh** (serverless, auto-clustering negligible at this scale) | 4 refreshes/hour × 10h × 22 days ≈ 880 refreshes × small data — assume **5 credits/mo** | 5 | **$15** |
| **Storage** (90-day rolling + Time Travel: ~10 GB active, generous) | 0.01 TB × $23 = $0.23 | — | **$1** |
| **Snowflake serverless overhead** (cloud services, etc. — capped at 10% of compute) | ~10% of 115 credits | 12 | **$36** |
| **TOTAL (on-demand Enterprise)** | | **~127 credits** | **~$382/mo** |

### Sensitivity bands

| Scenario | Monthly cost |
|---|---|
| **Optimistic** (capacity pricing at $1.80/credit, result-cache hits on 50% of page loads → query warehouse halves) | **~$170–$220** |
| **Base case** (numbers above) | **~$380** |
| **Pessimistic** (PSM keeps tab open all day → code warehouse runs 220h instead of 60h; no cache hits; on-demand) | **~$900–$1,100** |
| **Disaster** (someone enables a M warehouse, forgets to auto-suspend, runs 24/7) | **$2,800/mo from one warehouse alone** ([1 M warehouse × 4 credits/hr × 720h × $1/credit] ≈ $2,880 at Standard edition) |

**Most-likely-monthly: $350–$450** for Enterprise edition with the recipe above. The single biggest swing factor is whether the PSM tends to leave the tab open (drives code-warehouse hours) — instrument with QUERY_ATTRIBUTION_HISTORY before optimizing further.

### Query attribution: who's racking up the bill

Use `SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY` joined to `QUERY_HISTORY` on `query_id`. The `credits_attributed_compute` column gives **per-query weighted credit cost** including resize/autoscale (but **excludes idle warehouse time** — that's still attributed to the warehouse, not individual queries). ([Snowflake docs QUERY_ATTRIBUTION_HISTORY][56], [Medium Karthik Raman][57], [Snowflake docs cost attribution][58])

Apply a **query tag** in Streamlit's session before each user query:

```sql
ALTER SESSION SET QUERY_TAG = '{"app":"psm-dashboard","user":"matt@ravenpower.net","partner_view":"P-0042"}';
```

Then attribute monthly cost per PSM and per partner-view:

```sql
SELECT
  PARSE_JSON(query_tag):user::STRING       AS dashboard_user,
  PARSE_JSON(query_tag):partner_view::STRING AS partner_id,
  SUM(credits_attributed_compute)          AS credits
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY
WHERE start_time >= DATE_TRUNC('MONTH', CURRENT_DATE)
  AND query_tag ILIKE '%psm-dashboard%'
GROUP BY 1, 2
ORDER BY credits DESC;
```

Sources for the query-tag JSON pattern: [select.dev query tags][59], [Seemore query tags][60], [Medium Jon Osborn QUERY_TAG best practices][61], [Analytics.today query-tag cost attribution][62].

---

## 11. RavenClaude knowledge file content sketches

These are starter outlines for `plugins/ravenclaude-core/knowledge/snowflake-*.md` or a new `plugins/data-platform/` plugin. Each is a paste-ready stub; tighten and version-bump on commit.

### `snowflake-dashboard-warehouse-sizing.md`
```
# Snowflake warehouse sizing for dashboard reads

Default: XS Standard, AUTO_SUSPEND=60s, AUTO_RESUME=TRUE.
Only step up to S if a single dashboard query consistently scans >10 GB of compressed data
OR if concurrency exceeds 8 simultaneous queries (multi-cluster XS is usually cheaper).

Never use Snowpark-Optimized for BI — 1.5× credit rate, M-minimum size, no XS available.

Adaptive (Gen2) warehouses: pilot only after Tier-A workload is steady; can reduce cost 20–40%
on variable plans but cold-start behavior differs from Standard.
```

### `snowflake-result-cache-hygiene.md`
```
# Maximizing Snowflake result-cache hit rate for dashboards

- Render WHERE clauses with literal dates updated once per day, not CURRENT_DATE arithmetic.
- No CURRENT_TIMESTAMP in the SELECT list of dashboard queries.
- Run the dashboard under a stable service role (privilege diffs invalidate cache).
- TTL: 24h from last hit, hard ceiling 31d from initial execution.
- Verify with `SELECT * FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY()) WHERE BYTES_SCANNED=0`
  → those are the cache hits.
```

### `snowflake-dynamic-tables-for-rollups.md`
```
# Dynamic Tables as the default materialization for PSM rollups

Use Dynamic Tables (not Materialized Views) for any rollup that joins two or more tables.

- TARGET_LAG = '15 minutes' for business-hours dashboards.
- TARGET_LAG = DOWNSTREAM for intermediate layers (lazy refresh, no wasted credits).
- Use a dedicated XS Standard warehouse, AUTO_SUSPEND=60s.
- Monitor data_lag_seconds via SNOWFLAKE.ACCOUNT_USAGE.DYNAMIC_TABLE_REFRESH_HISTORY.

Avoid: clustering keys on tables under 50M rows — overhead exceeds benefit.
Avoid: Search Optimization on small low-cardinality tables (PSM at 25 partners qualifies as small).
```

### `snowflake-query-attribution.md`
```
# Per-user / per-dashboard cost attribution

Set a JSON query tag in every dashboard session:
  ALTER SESSION SET QUERY_TAG = '{"app":"<name>","user":"<email>","view":"<id>"}';

Attribute monthly:
  SELECT PARSE_JSON(query_tag):user::STRING AS u,
         SUM(credits_attributed_compute)    AS credits
  FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY
  WHERE start_time >= DATE_TRUNC('MONTH', CURRENT_DATE)
  GROUP BY 1 ORDER BY credits DESC;

Note: idle warehouse time is NOT in credits_attributed_compute — pair with
WAREHOUSE_METERING_HISTORY for full-warehouse accounting.
```

### `snowflake-resource-monitors-and-budgets.md`
```
# Cost guardrails

Per-warehouse Resource Monitor (per Streamlit warehouse):
  - Monthly quota sized to expected + 50% headroom.
  - NOTIFY at 50/75/90%, SUSPEND_IMMEDIATE at 100%.
  - Resource Monitors lag ~5–10 min — they are a backstop, not a hard cap.

Account-level Budget:
  - Catches serverless (DT refresh, auto-clustering, Cortex).
  - Webhook → Slack #data-alerts.
  - User-Defined Actions (since Feb 2026) can call a suspend-everything stored proc.

Statement-level safety: set STATEMENT_TIMEOUT_IN_SECONDS=120 on dashboard role to kill runaways.
```

---

## Sources ledger

Numbered to match inline citations.

1. [Stellans — Snowflake Warehouse Sizing Explained](https://stellans.io/snowflake-warehouse-sizing-2/)
2. [Flexera — Snowflake Gen2 warehouse 101 (2026)](https://www.flexera.com/blog/finops/snowflake-gen2-warehouse/)
3. [Chaosgenius — 8 Tips for Choosing Right Snowflake Warehouse Sizes (2026)](https://www.chaosgenius.io/blog/snowflake-warehouse-sizes/)
4. [Hightouch — How we reduced our Snowflake compute costs](https://hightouch.com/blog/how-we-reduced-our-snowflake-compute-costs)
5. [Flexera — 8 best practices for choosing right Snowflake warehouse sizes (2026)](https://www.flexera.com/blog/finops/snowflake-warehouse-sizes/)
6. [Yuki — Snowpark-Optimized Warehouses: Your Complete 2026 Guide](https://yukidata.com/snowflake-snowpark-optimized-warehouse-guide/)
7. [Snowflake docs — Snowpark-optimized warehouses](https://docs.snowflake.com/en/user-guide/warehouses-snowpark-optimized)
8. [npblue — Snowflake Result Set Reuse Explained](https://www.npblue.com/data/snowflake/snowflake-result-set-reuse)
9. [Snowflake Community KB — Understanding Result Caching](https://community.snowflake.com/s/article/Understanding-Result-Caching)
10. [Brontowise — Caching in Snowflake: Result, Metadata, and Data Cache](https://brontowise.com/2025/11/18/caching-in-snowflake-result-metadata-and-data-cache-whats-real-whats-not/)
11. [Beyondkey — Snowflake Caching](https://www.beyondkey.com/blog/snowflake-caching/)
12. [Snowflake docs — Search optimization service](https://docs.snowflake.com/en/user-guide/search-optimization-service)
13. [Snowflake docs — Search optimization cost estimation](https://docs.snowflake.com/en/user-guide/search-optimization/cost-estimation)
14. [Analytics.today — Optimizing Snowflake Search Optimisation Services](https://articles.analytics.today/best-practices-snowflake-search-optimisation-services)
15. [Medium / Snowflake Builders — Search Optimization Guide](https://medium.com/snowflake/search-optimization-c99b2117cb2e)
16. [Medium / Shreya Agrawal — Faster, cheaper SOS features (Snowflake)](https://medium.com/snowflake/faster-cheaper-and-more-transparent-new-search-optimization-features-a5f9ff51b0ea)
17. [Snowflake docs — SYSTEM$ESTIMATE_SEARCH_OPTIMIZATION_COSTS](https://docs.snowflake.com/en/sql-reference/functions/system_estimate_search_optimization_costs)
18. [Stellans — Snowflake Clustering Keys](https://stellans.io/snowflake-clustering-keys/)
19. [Integrate.io — Comprehensive Guide to Snowflake Data Clustering](https://www.integrate.io/blog/a-comprehensive-guide-to-snowflake-data-clustering/)
20. [Medium / Ember Crooks — Data-Driven Approach to Choosing a Clustering Key](https://medium.com/snowflake/a-data-driven-approach-to-choosing-a-clustering-key-in-snowflake-4b3400704778)
21. [select.dev — Defining multiple cluster keys with materialized views](https://select.dev/posts/clustering-with-materialized-views)
22. [Flexera — Snowflake clustering 101 (2026)](https://www.flexera.com/blog/finops/snowflake-clustering/)
23. [Medium / Manik Hossain — Query Performance Tuning in Snowflake with dbt](https://medium.com/@manik.ruet08/query-performance-tuning-in-snowflake-with-dbt-real-world-examples-05037dfccf28)
24. [Snowflake docs — Automatic Clustering](https://docs.snowflake.com/en/user-guide/tables-auto-reclustering)
25. [Snowflake engineering blog — Automatic Clustering at Snowflake](https://www.snowflake.com/en/engineering-blog/automatic-clustering-at-snowflake/)
26. [Keebo — Why Your Snowflake Clustering Strategy Costs You Money](https://keebo.ai/blog/snowflake-clustering-keys-optimization/)
27. [Snowflake docs — Dynamic tables compared to streams/tasks and MVs](https://docs.snowflake.com/en/user-guide/dynamic-tables-comparison)
28. [RisingWave — Snowflake Dynamic Tables vs Materialized Views](https://risingwave.com/blog/snowflake-dynamic-tables-vs-materialized-views-key-differences/)
29. [Tacnode — DT vs MV: When Each Works, When Neither Does](https://tacnode.io/post/snowflake-dynamic-tables-vs-materialized-views)
30. [Flexera — Views vs Materialized Views (2026)](https://www.flexera.com/blog/finops/snowflake-materialized-views/)
31. [Medium / Mike Taveirne — Using Dynamic Tables in Lieu of Traditional MVs](https://medium.com/snowflake/using-snowflake-dynamic-tables-in-lieu-of-traditional-materialized-views-2bcc29d7a654)
32. [Yuki — Everything to Know About Snowflake Dynamic Tables](https://yukidata.com/snowflake-dynamic-tables-guide/)
33. [Hexstream — MVs vs Dynamic Tables for Engineers Who Have Been Burned](https://www.hexstream.com/tech-corner/materialized-views-vs-dynamic-tables-in-snowflake-for-engineers-who-have-been-burned)
34. [Medium / PD Dutta — Dynamic Tables + dbt](https://medium.com/snowflake/dynamic-tables-dbt-a-powerful-combination-f550ebc23d60)
35. [Snowflake — Build Declarative Data Pipelines with Dynamic Tables](https://www.snowflake.com/en/developers/guides/snowflake-dynamic-tables-data-pipeline/)
36. [Snowflake docs — Managing costs for Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/object-management/billing)
37. [Snowflake docs — Runtime environments for Streamlit apps](https://docs.snowflake.com/en/developer-guide/streamlit/app-development/runtime-environments)
38. [Streamlit Discuss — App Timeout After 15 Minutes](https://discuss.streamlit.io/t/snowflake-streamlit-app-timeout-after-15-minutes-how-to-change-this/82644)
39. [Snowflake docs — Custom sleep timer for a Streamlit app](https://docs.snowflake.com/en/developer-guide/streamlit/features/sleep-timer)
40. [Stellans — Auto-Suspend vs Auto-Resume cost/performance](https://stellans.io/snowflake-auto-suspend-vs-auto-resume-cost-performance-settings-stellans/)
41. [Keebo — How Your "Experts" Have Been Misleading You About Auto-Suspend](https://keebo.ai/2025/03/19/snowflake-auto-suspend/)
42. [Unravel — 3 Proven Ways to Optimize Snowflake Warehouse Sizes](https://www.unraveldata.com/resources/optimize-snowflake-warehouse-sizes)
43. [AtScale — Optimizing Power BI Query Performance in Snowflake](https://www.atscale.com/blog/optimizing-power-bi-query-performance-snowflake/)
44. [Princeton IT — Optimize Snowflake Queries for Faster BI Dashboards](https://princetonits.com/blog/data-engineering/optimize-snowflake-queries-for-faster-bi-dashboards/)
45. [Medium / Manik Hossain — Materializations in dbt for Snowflake](https://medium.com/@manik.ruet08/materializations-in-dbt-which-one-is-right-for-your-snowflake-pipeline-b8b732e9f9f5)
46. [Snowflake docs — Working with resource monitors](https://docs.snowflake.com/en/user-guide/resource-monitors)
47. [Snowflake docs — Monitor credit usage with budgets](https://docs.snowflake.com/en/user-guide/budgets)
48. [Snowflake docs — Controlling cost](https://docs.snowflake.com/en/user-guide/cost-monitoring)
49. [Flexera — Snowflake resource monitors 101 (2026)](https://www.flexera.com/blog/finops/snowflake-resource-monitors/)
50. [Medium / Santhosh K L — Budgets vs Resource Monitors](https://medium.com/@sanusa100/snowflake-budgets-vs-resource-monitors-which-one-to-use-and-when-ac6f6d6bef79)
51. [Medium / Alexander — Automating Cost Control in Snowflake (Budget custom actions)](https://alexandersks.medium.com/automating-cost-control-in-snowflake-a-deep-dive-into-budget-custom-cycle-start-actions-04e3b1897114)
52. [Costbench — Snowflake Pricing 2026](https://costbench.com/software/data-warehousing/snowflake/)
53. [Flexera — Snowflake pricing explained (2026)](https://www.flexera.com/blog/finops/ultimate-snowflake-cost-optimization-guide-reduce-snowflake-costs-pay-as-you-go-pricing-in-snowflake/)
54. [Snowflake docs — Overview of warehouses](https://docs.snowflake.com/en/user-guide/warehouses-overview)
55. [Definite — Snowflake Pricing 2026](https://www.definite.app/blog/understanding-snowflake-pricing)
56. [Snowflake docs — QUERY_ATTRIBUTION_HISTORY view](https://docs.snowflake.com/en/sql-reference/account-usage/query_attribution_history)
57. [Medium / Karthik Raman — Harnessing QUERY_ATTRIBUTION_HISTORY](https://medium.com/@karthiksraman/harnessing-the-power-of-query-attribution-history-a-snowflake-deep-dive-0910cbd2f2eb)
58. [Snowflake docs — Attributing cost](https://docs.snowflake.com/en/user-guide/cost-attributing)
59. [select.dev — Snowflake query tags for enhanced monitoring](https://select.dev/posts/snowflake-query-tags)
60. [Seemore Data — Snowflake Query Tags Implementation Guide](https://seemoredata.io/blog/snowflake-query-tags/)
61. [Medium / Jon Osborn — Best Practices for Using QUERY_TAG](https://medium.com/snowflake/best-practices-for-using-query-tag-in-snowflake-32bfb8d4efba)
62. [Analytics.today — Snowflake Query Cost Attribution via Tags](https://articles.analytics.today/best-practices-for-query-tagging-in-snowflake)

### Additional confirming sources (not directly cited but consulted during corroboration)

- [Snowflake docs — Using Persisted Query Results](https://docs.snowflake.com/en/user-guide/querying-persisted-results)
- [Snowflake docs — Optimizing the warehouse cache](https://docs.snowflake.com/en/user-guide/performance-query-warehouse-cache)
- [Teej.ghost — A Guide To The Snowflake Results Cache](https://teej.ghost.io/a-guide-to-the-snowflake-results-cache/)
- [select.dev — Snowflake Cost Optimization Guide](https://select.dev/posts/snowflake-cost-optimization)
- [select.dev — Snowflake Resource Monitors](https://select.dev/posts/snowflake-resource-monitors)
- [select.dev — Snowflake Query Optimization 16 tips](https://select.dev/posts/snowflake-query-optimization)
- [Snowflake docs — Views, materialized views, and dynamic tables overview](https://docs.snowflake.com/en/user-guide/overview-view-mview-dts)
- [Snowflake — Build a Query Cost Monitoring Tool with Streamlit](https://www.snowflake.com/en/developers/guides/query-cost-monitoring/)
- [Woodmark — Cost monitoring in Snowflake using Streamlit](https://www.woodmark.de/en/blog-detail/cost-monitoring-in-snowflake-using-streamlit)
- [Seemore Data — Snowflake Cost Per Query Attribution Mastery](https://seemoredata.io/blog/mastering-snowflake-cost-per-query-attribution-for-optimal-cloud-spend/)
- [Yuki — Snowflake Cost Per Query](https://yukidata.com/snowflake-cost-per-query/)

Total: **62 numbered citations + 11 supplementary** = 73 sources consulted across docs.snowflake.com, select.dev, Hightouch, Snowflake community, Snowflake builders blog, Medium, Flexera, Keebo, Yuki, Stellans, Chaosgenius, dbt community, AtScale, RisingWave, Tacnode, Hexstream, Brontowise, Analytics.today, Seemore, Integrate.io, Princeton IT, Costbench, Definite, Woodmark, npblue, Beyondkey, and the Streamlit discussion forum.
