> Use this template to record a Tableau workbook performance investigation — baseline measurements, bottleneck diagnosis, applied fixes, and before/after results.

# Workbook Performance Report: [Workbook Name]

## Metadata

| Field | Value |
|---|---|
| Workbook name | [Name as published] |
| Tableau Server/Cloud site | [Site / Project path] |
| Data source type | [Published extract / Embedded extract / Live connection] |
| Investigated by | [Name] |
| Investigation date | [YYYY-MM-DD] |
| Status | [In progress / Fixes applied / Closed] |

---

## Problem statement

**Reported symptom:**

[e.g., "Dashboard takes 15–20 seconds to load. Filter actions take 8+ seconds. Reported by Finance team on 2026-05-30."]

**Threshold breached:**

| Metric | Target | Actual |
|---|---|---|
| Initial load | < 5 s | [X s] |
| Filter action | < 2 s | [X s] |
| Extract refresh | < 10 min | [X min] |

---

## Baseline measurements (Performance Recording)

Run Help → Settings and Performance → Start Performance Recording. Interact with the slow views. Stop.

| Sheet name | Query time | Rendering time | Layout time | Total time |
|---|---|---|---|---|
| [Sheet 1] | [X ms] | [X ms] | [X ms] | [X ms] |
| [Sheet 2] | [X ms] | [X ms] | [X ms] | [X ms] |

**Bottleneck identified in:** [ ] Query / [ ] Rendering / [ ] Layout / [ ] Multiple

**Worst offending query (from Performance Recording):**

```sql
-- Paste the generated SQL or VizQL query here
```

---

## Root cause analysis

| Cause | Present? | Evidence |
|---|---|---|
| No extract filter — full table loaded | [ ] | Row count: [X M rows] |
| High-cardinality quick filter with "Show all values" | [ ] | Field: [Name], distinct values: [X] |
| String calculation in hot path | [ ] | Calc: [Name] |
| Nested / cross-source LOD expressions | [ ] | Calc: [Name] |
| Many-to-many join fan-out | [ ] | Tables: [Names] |
| High mark count (> 5 000 marks in view) | [ ] | Sheet: [Name], marks: [X] |
| Live connection with no stated freshness need | [ ] | Source: [Name] |
| Unindexed Hyper field in filter | [ ] | Field: [Name] |

---

## Fixes applied

| Fix | Description | Applied by | Date |
|---|---|---|---|
| Extract filter | [e.g., Added date filter: last 2 years] | [Name] | [YYYY-MM-DD] |
| Quick filter type change | [e.g., Changed Customer Name to typed search] | [Name] | [YYYY-MM-DD] |
| Calc materialisation | [e.g., Materialised [Parsed Region] in extract] | [Name] | [YYYY-MM-DD] |
| Incremental refresh | [e.g., Switched full to incremental on created_date] | [Name] | [YYYY-MM-DD] |
| Mark reduction | [e.g., Replaced 100K scatter with hexbin] | [Name] | [YYYY-MM-DD] |
| [Other] | | | |

---

## After measurements

| Sheet name | Query time | Rendering time | Total time | Improvement |
|---|---|---|---|---|
| [Sheet 1] | [X ms] | [X ms] | [X ms] | [X%] |
| [Sheet 2] | [X ms] | [X ms] | [X ms] | [X%] |

**Target met?** [ ] Yes / [ ] No — further investigation needed (attach follow-up note)

---

## Recommendations for future maintenance

- [e.g., Apply a date-range extract filter before the row count exceeds 20 M rows (estimated: 2027-Q1)]
- [e.g., Review the Customer Name quick filter — it will need conversion to typed search when the customer list exceeds 1 000]
- [e.g., Set a Tableau Server admin alert if extract refresh exceeds 20 min]
