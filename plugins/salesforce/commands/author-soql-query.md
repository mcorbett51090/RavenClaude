---
description: Author a selective, indexed, bulk-safe SOQL query for a goal you describe — choosing indexed filters, avoiding non-selective full scans and skew, and recommending Batch Apple / skinny tables / custom indexes when the data volume demands it.
argument-hint: "[what to query, e.g. 'open opportunities for accounts in EMEA']"
---

# Author a SOQL query

You are running `/salesforce:author-soql-query`. Write a correct, **selective** SOQL query for what the user asked (`$ARGUMENTS`), using this plugin's `soql-authoring` skill and data best-practices. The goal is a query that stays fast at high data volume, not just one that returns the right rows in a dev org.

## When to use this

You need a query for Apex, a report, a Data Loader extract, or an integration — and the object is (or will become) large.

## Steps

1. **Make it selective** (`data-selective-soql-on-indexed-fields`, `apex-query-selectively-with-indexes`): filter on **indexed** fields (Id, Name, external IDs, audit fields, lookups, or custom-indexed fields). Avoid leading `%` `LIKE`, negative filters (`!=`, `NOT`), and nulls on unindexed fields — they force full scans.
2. **Select only the fields you need** — never `SELECT *`-style field dumps; each field is heap + transfer cost.
3. **Watch for skew** (`data-avoid-ownership-and-lookup-skew`): a parent with >10k children, or one owner with huge volume, causes record-lock contention — note it if the filter implies it.
4. **Volume strategy** when the result set is large:
   - >50k rows in Apex → **Batch Apex** (`data-batch-apex-for-large-result-sets`), not a single query.
   - Reporting on a huge object → **skinny table / custom index** (`data-skinny-tables-and-custom-indexes`).
   - Extract → **Bulk API**, not row-by-row REST (`data-loader-vs-bulk-api-selection`, `integration-bulk-api-for-batch-not-row-by-row-rest`).
5. **In Apex**: bind variables (`apex-bind-variables-in-dynamic-soql`), never string-concatenate user input.
6. Show the query + a one-line note on *why it's selective* and the Query Plan tool check to confirm.

## Guardrails

- A query that's fast on 1k rows can table-scan on 1M — always reason about the indexed leading column.
- Never concatenate untrusted input into dynamic SOQL.
- If the right answer is "don't query this in real time" (archive cold rows — `data-archive-cold-rows-to-keep-hot-object-small`), say so.
