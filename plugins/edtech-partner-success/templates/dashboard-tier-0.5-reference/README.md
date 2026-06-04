# Tier 0.5 reference implementation — real connectors + Snowflake

> **Reference, not production.** A drop-in starting point Codex can copy and adapt for the Tier 0.5 build (real Salesforce + Planhat + Google Calendar + Snowflake, drop-in replacement for the Tier 0 synthetic fixture).
>
> **DoD:** [`tier-0.5-acceptance-tests.md`](./tier-0.5-acceptance-tests.md) — until that file's end-to-end smoke test passes, Tier 0.5 is not done.

## What this directory is

A 14-file reference set authored as the **template** for the Tier 0.5 build. Each file is < 300 lines, Snowflake-flavored, FERPA-annotated, and cites the SKILL / knowledge source for its design choices. Codex copies these into the real paths (under `plugins/data-platform/dbt/psm_dashboard/` etc. — see the build plan) and fills in the engagement-specific particulars (org_uid, partner names, etc.).

## What this directory is NOT

- **Not a runnable dbt project.** The files live here as flat templates; Codex assembles them into the real dbt directory layout per the Tier 0.5 build plan §3.2.
- **Not synthetic data.** Tier 0 owns the synthetic fixture (`bi-report/data.json` + `synthesize.py`). Tier 0.5 reads real warehouse rows. **Do not commit synthetic seed rows into this directory** — Codex's first job is to wire real connectors.
- **Not a rendering layer.** No `report.html`, no `generate-bi-report.py` edits. Tier 0.5 emits `data.json`; Tiers 1–4 render it.
- **Not multi-tenant.** `org_uid` is a single constant from `.env`. Multi-tenant is Tier 5.

## Layout

```
dashboard-tier-0.5-reference/
├── README.md                              this file
├── tier-0.5-acceptance-tests.md           Definition of Done — end-to-end smoke test
├── snowflake-database-ddl.sql             account objects + DBs + schemas + warehouses + roles + seed configs
├── dynamic-tables-and-tasks.sql           Dynamic Table cascade for the marts (TARGET_LAG='15 min')
├── dbt-project.yml                        dbt project config (3-layer materialization, MetricFlow on)
├── dbt-models-sources.yml                 source definitions + freshness expectations
├── dbt-models-staging.sql                 staging models (rename + clean raw)
├── dbt-models-bridge-account-xref.sql     Splink-tier bridge as a Dynamic Table
├── dbt-models-marts-partners.sql          conformed partners mart (Tier 0 schema parity)
├── dbt-models-marts-timeline-events.sql   conformed timeline events (FERPA type=user filter)
├── dbt-models-marts-usage-daily.sql       district-level usage rollups from Snowflake share
├── dbt-models-marts-priority-score.sql    priority score from weights config table (single SoT)
├── dbt-tests.yml                          generic + custom dbt tests
└── export-psm-dashboard.py                stdlib + snowflake-connector-python exporter
```

## How a Codex session uses this

1. Read [`tier-0.5-acceptance-tests.md`](./tier-0.5-acceptance-tests.md) **first** — that is the DoD. Everything else is in service of it.
2. Read the Tier 0.5 build plan at [`docs/plans/2026-06-04-partner-success-command-center/build-plan-tier-0.5-real-connectors.md`](../../../../docs/plans/2026-06-04-partner-success-command-center/build-plan-tier-0.5-real-connectors.md) — that is the contract.
3. Read the Tier 0 brief at [`docs/plans/2026-06-04-partner-success-command-center/build-plan-for-codex.md`](../../../../docs/plans/2026-06-04-partner-success-command-center/build-plan-for-codex.md) for the schema enumeration. **Tier 0 wins all schema disagreements.**
4. Copy each file in this directory to the real path the build plan §3 calls out. Replace the templated `{{org_uid}}`, the demo partner names, and the per-engagement config values.
5. Run `dbt parse`, `dbt build`, then `export-psm-dashboard.py --validate`.
6. Run the smoke test from `tier-0.5-acceptance-tests.md` end to end.

## Invocation

```sh
# Apply Snowflake DDL (account-level — once per account):
snowsql -f snowflake-database-ddl.sql

# Build dbt models (after `dbt deps`):
dbt build --target=dev

# Apply Dynamic Table cascade (after dbt build):
snowsql -f dynamic-tables-and-tasks.sql

# Export to data.json (after dbt build):
python3 export-psm-dashboard.py \
    --out /tmp/data.json \
    --as-of 2026-06-04 \
    --org-uid 11111111-2222-4333-8444-555555555555 \
    --validate
```

## Discipline (mirrors the Tier 0.5 build plan)

- **Snowflake SQL only.** No Postgres-isms. `QUALIFY`, `IFF`, `COUNT_IF`, `DATEDIFF('day', …)`, `DATE_TRUNC('week', …)`.
- **No `priority_score` in dbt or in MetricFlow.** Tier 0 classifies it `derived_at_render`. The mart in this directory (`dbt-models-marts-priority-score.sql`) is a **reference** for an OPTIONAL warehouse-side computation — Codex MUST set `priority_score: null` in the export to honor the classification. The reference file ships so Codex can audit weight provenance vs the renderer.
- **FERPA:** every field that could carry student data is annotated `-- FERPA:` in SQL and `# FERPA:` in Python. Default posture is mask + filter; opt-in surfaces require an explicit `--allow-real-ids` flag.
- **dbt-utils only.** No third-party dbt packages (`dbt_expectations`, etc.) — they accumulate maintenance debt across consumer envs.
- **Export = stdlib + `snowflake-connector-python` only.** Tier 0.5 budget is one extra third-party dep for the snowflake connector + `jsonschema` for validation. No more.
- **Cite the prior on every model.** Every file's header carries the lineage + the SKILL/knowledge source URL.

## When this reference goes stale

Refresh when any of the following changes:

- Tier 0's `data.export.schema.json` evolves (the export shape moves).
- The bridge SKILL adds an 8th tier (the bridge mart shape moves).
- Planhat switches off the native Snowflake bidirectional sync (the staging shape moves).
- Snowflake Dynamic Tables drop below the 15s preview floor (the `target_lag` discussion moves).

## See also

- Build plan: [`docs/plans/2026-06-04-partner-success-command-center/build-plan-tier-0.5-real-connectors.md`](../../../../docs/plans/2026-06-04-partner-success-command-center/build-plan-tier-0.5-real-connectors.md)
- Tier 0 brief (schema source of truth): [`docs/plans/2026-06-04-partner-success-command-center/build-plan-for-codex.md`](../../../../docs/plans/2026-06-04-partner-success-command-center/build-plan-for-codex.md)
- Snowflake substrate: [`plugins/data-platform/knowledge/snowflake-operational-dashboard-patterns.md`](../../../data-platform/knowledge/snowflake-operational-dashboard-patterns.md)
- Cost model: [`plugins/data-platform/knowledge/snowflake-psm-dashboard-cost-model.md`](../../../data-platform/knowledge/snowflake-psm-dashboard-cost-model.md)
- Planhat integration: [`plugins/data-platform/knowledge/planhat-integration.md`](../../../data-platform/knowledge/planhat-integration.md)
- Identity SKILL: [`plugins/data-platform/skills/cross-system-identity-resolution/SKILL.md`](../../../data-platform/skills/cross-system-identity-resolution/SKILL.md)
