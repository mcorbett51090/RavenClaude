# Pick the load tool by volume and repeatability — Data Loader vs Bulk API vs ETL

**Status:** Pattern — strong default; deviate only with a written reason naming the row count, cadence, and source-system complexity.

**Domain:** Data / Integration

**Applies to:** `salesforce`

---

## Why this exists

"Load this data into Salesforce" has three structurally different answers, and picking by habit instead of by volume/cadence wastes effort or causes an incident. **Data Loader** (the desktop/CLI tool, which itself rides the Bulk or SOAP API) is right for one-off or occasional admin-driven loads up to moderate volume — it gives a mapping UI, success/error files, and a human in the loop. **Bulk API 2.0** (`skills/bulk-rest-api-client`) is right for large or programmatic loads where you control the job lifecycle from code and need to fit the daily Bulk allocation. A real **ETL / middleware** tier (informatica, Mulesoft, Azure Data Factory via `azure-cloud/*`) is right for **recurring, multi-system, transform-heavy** pipelines — scheduled syncs, joins across sources, retries, and orchestration that a single Bulk job can't express. Using Data Loader for a nightly multi-source sync turns a person into a cron job; using a heavyweight ETL platform for a one-time 2,000-row admin fix is overkill.

## How to apply

Match the load to its volume, cadence, and source complexity. Whatever the tool, wrap it in the data-loader runbook (sandbox-first, backup, dedup, verify) and prefer upsert-on-external-ID for idempotency.

```text
Choose the load tool:
- One-off / occasional, admin-driven, low-moderate volume   -> Data Loader (UI or CLI)
- Large or programmatic, single-object/operation, code-owned -> Bulk API 2.0 (skills/bulk-rest-api-client)
- Recurring + multi-source + transform/orchestration         -> ETL / middleware (azure-cloud/* for Azure-native)
Always:
- upsert on an external id  (idempotent, re-runnable)
- sandbox-first for production-scale loads
- wrap in the data-loader runbook (backup + verify + rollback)
```

```http
# DO — large programmatic load goes through Bulk API 2.0, not row-by-row Data Loader inserts
POST /services/data/vXX.X/jobs/ingest
{ "object":"Contact", "operation":"upsert", "externalIdFieldName":"Source_Id__c", "contentType":"CSV" }
# vs. a recurring multi-source nightly sync -> orchestrate in ETL/middleware, not a person clicking Data Loader
```

**Do:**
- Use **Data Loader** for one-off/occasional admin loads with a human verifying mappings and error files.
- Use **Bulk API 2.0** for large or programmatic loads where code owns the job lifecycle.
- Use **ETL/middleware** for recurring, multi-source, transform-heavy pipelines (coordinate Azure-native with `azure-cloud/*`).
- Prefer **upsert on an external ID** in every case so re-runs are idempotent.

**Don't:**
- Hand-run Data Loader on a schedule a pipeline should own.
- Push a 2,000-row one-off through a standing ETL platform.
- Blind-insert at volume (duplicates on re-run) when an external ID makes upsert safe.

## Edge cases / when the rule does NOT apply

Tiny loads (a few records) belong in the synchronous REST/SOAP path or even a UI edit — no batch tooling needed. Data Loader can run via its CLI (`process-conf`) on a schedule for simple recurring jobs, which can be a pragmatic middle ground before standing up full ETL. The boundary between "large Bulk job" and "needs ETL" is set by **source complexity and orchestration needs**, not row count alone — a 5,000-row load that joins three systems is an ETL job; a 5,000,000-row single-object load is a Bulk job. Daily Bulk allocations and Data Loader batch sizing are version-sensitive — verify `[verify-at-build]`.

## See also

- [`./integration-bulk-api-for-batch-not-row-by-row-rest.md`](./integration-bulk-api-for-batch-not-row-by-row-rest.md) — why Bulk beats row-by-row REST at volume
- [`../skills/bulk-rest-api-client/SKILL.md`](../skills/bulk-rest-api-client/SKILL.md) — the Bulk API 2.0 job sequence
- [`../skills/data-loader-runbook/SKILL.md`](../skills/data-loader-runbook/SKILL.md) — the safe, reversible load procedure for any tool
- [`../knowledge/integration-patterns.md`](../knowledge/integration-patterns.md) — Batch Data Synchronization pattern
- [`../knowledge/integration-data-decision-trees.md`](../knowledge/integration-data-decision-trees.md) — the data-load-tool decision tree

## Provenance

Codifies the Batch Data Synchronization pattern from [`../knowledge/integration-patterns.md`](../knowledge/integration-patterns.md), the Bulk API job mechanics in [`../skills/bulk-rest-api-client/SKILL.md`](../skills/bulk-rest-api-client/SKILL.md), and the reversible-load discipline in [`../skills/data-loader-runbook/SKILL.md`](../skills/data-loader-runbook/SKILL.md). Tool capabilities, Bulk allocations, and Data Loader batch sizing are Salesforce platform features; exact numbers tagged `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
