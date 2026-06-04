# Tier 0.5 acceptance tests — end-to-end smoke test (the DoD)

> **Read this first.** This document is the Definition of Done for Tier 0.5. Until the smoke test below passes end-to-end against a real Snowflake account with at least one real Salesforce partner, Tier 0.5 is not done — regardless of what dbt parse, lint, or CI reports.

## Why this is the DoD (and not the dbt test suite)

The dbt test suite catches schema-shape violations. The data-integrity script catches cross-entity-reference violations. Neither answers the load-bearing question: **does a real Salesforce row flow through the bridge, through the marts, through the export, into a `data.json` that the Tier 1 renderer can read without a single rendering change?**

Only the smoke test answers that. Run it on every Tier 0.5 PR before flipping the draft.

## Pre-flight (skip if already true)

- `snowsql -f snowflake-database-ddl.sql` applied — `SHOW DATABASES LIKE 'PSM_%'` returns both.
- `dbt deps && dbt seed && dbt build --target=dev` exit 0.
- `snowsql -f dynamic-tables-and-tasks.sql` applied — `SHOW DYNAMIC TABLES` shows 11 rows.
- `bridge_account_xref_splink_raw` populated by `load-bridge-account-xref.py --apply` (T2/T3 rows).
- `.env` carries valid `SNOWFLAKE_*` keypair credentials.

## The smoke test — eight steps, each must pass

### Step 1 — A real Salesforce partner exists in the raw landing

```sql
USE WAREHOUSE WH_PSM_DASHBOARD;
SELECT COUNT(*) AS n FROM PSM_RAW.SALESFORCE.ACCOUNT WHERE _fivetran_deleted = FALSE;
-- expect: n >= 1
```

If `n = 0`, the Fivetran connector is not connected — fix that first (build plan §3 Step 2).

### Step 2 — The bridge resolves that partner

```sql
SELECT match_method, COUNT(*) AS n
FROM PSM_CONFORMED.MARTS.BRIDGE_ACCOUNT_XREF
GROUP BY 1
ORDER BY 1;
-- expect: at least one row in (leaid_exact | leaid_compound | external_id)
-- expect: NOT every row is `unresolved`
```

If every row is `unresolved`, the SKILL ladder is misfiring — re-read the loader's `--dry-run` output and check the per-tier counts. Common causes: `NCES_LEAID__c` not populated in SFDC (T0 misses), Planhat `sourceId` not configured (T4 misses), state-FIPS not pre-mapped on the account (T1/T2 misses).

### Step 3 — The partner appears in `dim_partner`

```sql
SELECT account_uid, name, band, score, priority_score, priority_breakdown
FROM PSM_CONFORMED.MARTS.DIM_PARTNER
LIMIT 5;
-- expect: account_uid matches UUIDv4 regex
-- expect: band in ('green', 'yellow', 'red')
-- expect: priority_score IS NULL  (derived_at_render)
-- expect: priority_breakdown IS NULL  (derived_at_render)
```

If `priority_score` or `priority_breakdown` is non-null, the export will fail Gate 53. The reference `dbt-models-marts-priority-score.sql` is for AUDIT only — it does NOT feed `dim_partner`.

### Step 4 — A timeline event for that partner exists

```sql
SELECT type, source, COUNT(*) AS n
FROM PSM_CONFORMED.MARTS.TIMELINE_EVENTS
GROUP BY 1, 2
ORDER BY n DESC
LIMIT 10;
-- expect: at least one row per (source, type) the engagement actually uses
-- expect: NO rows with type='user'  (FERPA filter on)
```

### Step 5 — The export runs and exits 0

```sh
python3 export-psm-dashboard.py \
    --out /tmp/data.json \
    --as-of "$(date +%Y-%m-%d)" \
    --org-uid 11111111-2222-4333-8444-555555555555 \
    --allow-real-ids \
    --validate
# expect: exit 0
# expect: stderr ends with `wrote: /tmp/data.json`
# expect: stderr counts > 0 for partners, contacts, timeline
```

If `--validate` exits non-zero, the assembled JSON does not match `data.export.schema.json`. Run again WITHOUT `--validate`, then `python3 -m jsonschema -i /tmp/data.json plugins/edtech-partner-success/bi-report/data.export.schema.json` to see the field-level error.

### Step 6 — Schema validation against Tier 0's export schema

```sh
python3 -m jsonschema \
    -i /tmp/data.json \
    plugins/edtech-partner-success/bi-report/data.export.schema.json
# expect: exit 0
```

Common failures and their root cause:

| jsonschema error | Root cause |
|---|---|
| `account_uid` regex mismatch | The MD5→UUIDv4 derivation in `dim_partner` did not force the `4` and `8` at the right positions. |
| `priority_weights` sum to wrong total | Someone edited `PRIORITY_WEIGHTS` config table without re-asserting sum=100. |
| `source_ref` regex mismatch | A new event type emitted a non-opaque URI. v3-tightened regex bans `://` past scheme and `.` in body. |
| `additionalProperties: false` violation | A new column was added to a mart without updating the schema. |

### Step 7 — Tier 0 integrity script passes in export mode

```sh
python3 scripts/check-psm-data-integrity.py \
    --data /tmp/data.json \
    --export-mode
# expect: exit 0
# expect: all 16 checks pass except the synthetic-only ones (Demo: prefix,
#         synthetic- ID prefix) — `--export-mode` skips those.
```

### Step 8 — Drop-in test against Tier 1 renderer

```sh
# Backup the synthetic fixture and substitute the real export.
cp plugins/edtech-partner-success/bi-report/data.json \
   /tmp/data.json.synthetic-backup
cp /tmp/data.json plugins/edtech-partner-success/bi-report/data.json

# Open the renderer (report.html) in a browser.
# Tier 1's renderer reads data.json and assembles the dashboard.
# Visually verify:
#   - The partner names from SFDC appear (no synthetic 'Wendelhart' names).
#   - The priority score renders (it's computed by the renderer from raw signals).
#   - The Live/Stale/Paused badge shows per-source state from connector_health.
#   - No console errors. No empty panels.

# Restore the synthetic fixture before commit:
cp /tmp/data.json.synthetic-backup \
   plugins/edtech-partner-success/bi-report/data.json
```

If any panel renders incorrectly with the real data but rendered correctly with the synthetic fixture, the bug is in the EXPORT shape, not in the renderer. Tier 0.5 owns it.

## Acceptance scoring

| # | Step | Pass criterion |
|---|---|---|
| 1 | Raw SFDC | ≥1 partner row in raw landing |
| 2 | Bridge resolves | ≥1 non-`unresolved` row per source |
| 3 | dim_partner | UUIDv4 account_uid + null priority_score |
| 4 | Timeline events | ≥1 cross-source event; no type='user' |
| 5 | Export exit 0 | `wrote:` line emitted; counts > 0 |
| 6 | jsonschema validate | exit 0 against data.export.schema.json |
| 7 | Integrity script | exit 0 in `--export-mode` |
| 8 | Renderer drop-in | All panels render; no console errors |

**Tier 0.5 is DONE when all 8 pass.** PR can flip from draft.

## Wall-handling at this layer

If step N fails, do NOT skip ahead to step N+1. Each step's pass is a precondition for the next.

- **Step 1 fails** → connector. Re-read `salesforce-integration.md` § field allow-list.
- **Step 2 fails** → bridge ladder. Re-read SKILL § "Step 1 — Inventory candidate keys".
- **Step 3 fails** → dim_partner SQL. Audit the MD5→UUIDv4 formula; check FERPA classification.
- **Step 4 fails** → timeline join. Check the bridge's `match_method != 'unresolved'` filter — orphan events drop here.
- **Step 5 fails** → export shape. Read stderr; degraded sources emit empty blocks (NOT crash).
- **Step 6 fails** → schema drift. Use the table above.
- **Step 7 fails** → cross-entity ref. Check `--check N` output to pinpoint.
- **Step 8 fails** → render shape. Diff `/tmp/data.json` against synthetic fixture; look for missing keys.

## What this test does NOT cover (intentionally — those tiers ship later)

- **Live freshness / sub-15-min latency.** Tier 0.5's target_lag is 15 min; sub-minute is Tier 2+.
- **Multi-tenant row-access policies.** Single-tenant in Tier 0.5; multi-tenant is Tier 5.
- **Renderer changes / new panels.** Tier 1 owns rendering. Tier 0.5 changes nothing in `report.html`.
- **Outlook calendar / Zendesk fallback.** Q3 = Google Calendar, Q1 = SFDC Service Cloud — settled.
- **Stewardship UI for T3 bridge rows.** The bridge accepts T3-with-reviewer; the UI is a separate concern.
