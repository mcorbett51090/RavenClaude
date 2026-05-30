# Move bulk datasets with Bulk API 2.0 — not row-by-row synchronous REST/SOAP

**Status:** Pattern — strong default; deviate only with a written reason naming the row count and why synchronous calls win at that volume.

**Domain:** Integration / Data

**Applies to:** `salesforce`

---

## Why this exists

A synchronous REST or SOAP call carries one record (or a small batch) and consumes one **daily API request** and a long-running concurrent-request slot per call. Loop that pattern over tens of thousands of rows and you exhaust the daily API allocation, saturate the org's tiny concurrent-request budget, and tie the wall-clock time to network round-trips. **Bulk API 2.0** is the platform's answer for the **Batch Data Synchronization** pattern: you create one ingest (or query) job, upload the dataset as CSV, and Salesforce processes it asynchronously in server-side batches — collapsing thousands of REST calls into a handful of job-management calls against the daily limit. Using row-by-row REST where Bulk belonged is the classic way a nightly sync that worked at 500 rows takes the org's whole API budget at 500,000.

## How to apply

Pick Bulk API 2.0 the moment the dataset is "more than a synchronous call should carry." Create the job, upload CSV, close to run, poll to completion, then reconcile results — prefer **upsert on an external ID** so the load is idempotent and re-runnable.

```http
# DO — one Bulk API 2.0 ingest job for the whole dataset (idempotent upsert on an external id)
POST /services/data/vXX.X/jobs/ingest
Content-Type: application/json
{
  "object": "Account",
  "operation": "upsert",
  "externalIdFieldName": "ERP_Id__c",
  "contentType": "CSV",
  "lineEnding": "LF"
}
# -> returns job Id; then:
PUT  /services/data/vXX.X/jobs/ingest/<jobId>/batches   (CSV body)
PATCH /services/data/vXX.X/jobs/ingest/<jobId>          {"state":"UploadComplete"}
# poll GET .../jobs/ingest/<jobId> until state == JobComplete, then fetch
# successfulResults / failedResults / unprocessedRecords
```

```text
DON'T — loop a synchronous single-record POST over a large dataset
for each of 200,000 rows:  POST /sobjects/Account  (one record)
# burns 200,000 daily API requests, saturates concurrent-request slots, no resumability
```

**Do:**
- Reach for Bulk API 2.0 for large import/export/sync — it is the Batch Data Synchronization pattern (`knowledge/integration-patterns.md`).
- Prefer **upsert on an external ID** so a partial run can be safely re-run.
- Always fetch and reconcile `successfulResults` / `failedResults` / `unprocessedRecords` before declaring the job done.
- Sandbox-first for any large production load.

**Don't:**
- Loop a synchronous single-record REST/SOAP call over a bulk dataset.
- Blind-insert at volume (creates duplicates on re-run) when an external ID makes upsert idempotent.
- Ignore the daily Bulk API allocation and daily API request limit — both are consumed.

## Edge cases / when the rule does NOT apply

A handful of records, or a genuine request-reply where the caller needs each record's response immediately, is correctly synchronous REST. Very large or continuous streams may belong in Platform Events / CDC (push) or an ETL/middleware tier (`azure-cloud/*`) rather than scheduled Bulk jobs. Bulk API has per-job size and field guidance, and complex post-load automation (triggers, Flows, sharing recalc) fires on Bulk-loaded rows just as on UI edits — budget for it. Exact Bulk allocations and per-job limits are version-sensitive — verify against the current limits cheat sheet `[verify-at-build]`.

## See also

- [`../skills/bulk-rest-api-client/SKILL.md`](../skills/bulk-rest-api-client/SKILL.md) — the job-create / upload / poll / reconcile sequence
- [`../skills/data-loader-runbook/SKILL.md`](../skills/data-loader-runbook/SKILL.md) — the safe, reversible load procedure that wraps the job
- [`./data-loader-vs-bulk-api-selection.md`](./data-loader-vs-bulk-api-selection.md) — picking the load tool
- [`../knowledge/integration-patterns.md`](../knowledge/integration-patterns.md) — Batch Data Synchronization pattern and the limit budget
- [`../knowledge/integration-data-decision-trees.md`](../knowledge/integration-data-decision-trees.md) — the data-load-tool decision tree

## Provenance

Codifies the Batch Data Synchronization pattern from [`../knowledge/integration-patterns.md`](../knowledge/integration-patterns.md) and the Bulk API 2.0 job mechanics in [`../skills/bulk-rest-api-client/SKILL.md`](../skills/bulk-rest-api-client/SKILL.md). Bulk API 2.0 endpoints, job lifecycle, and allocations are Salesforce platform features; exact numbers tagged `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
