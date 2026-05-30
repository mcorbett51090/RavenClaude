---
name: bulk-rest-api-client
description: Build Bulk API 2.0 ingest and query jobs for high-volume data movement. Use when loading or extracting large datasets over the REST Bulk API rather than row-by-row.
---

# Bulk REST API Client

Construct a Bulk API 2.0 job (ingest or query) for high-volume data movement that respects API limits.

## When to use

Moving more data than a synchronous REST/SOAP call should carry — large imports, exports, or syncs. This is the **Batch Data Synchronization** integration pattern (`knowledge/integration-patterns.md`).

## Steps

1. **Pick job type.** Ingest job (insert/update/upsert/delete) or query job.
2. **Create the job.** `POST /jobs/ingest` (or `/jobs/query`) with object, operation, and (for upsert) `externalIdFieldName`; line ending and column delimiter for CSV.
3. **Upload data** in CSV batches to the job's `/batches` endpoint; respect the per-job size guidance.
4. **Close / run the job** to start processing (`state: UploadComplete`).
5. **Poll status** until `JobComplete`; then fetch `successfulResults`, `failedResults`, `unprocessedRecords`.
6. **Budget the limits.** Bulk API 2.0 consumes the daily Bulk API allocation and the org's daily API request limit — verify current numbers `[verify-at-build]`. Always sandbox-first for large loads.

## Output

The job-creation payload, the upload/close/poll sequence, and the result-handling step, with the API limits the job consumes.
