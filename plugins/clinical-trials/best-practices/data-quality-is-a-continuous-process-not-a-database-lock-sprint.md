# Data Quality Is a Continuous Process, Not a Database-Lock Sprint

**Status:** Absolute rule
**Domain:** Clinical data management / submissions
**Applies to:** `clinical-trials`

---

## Why this exists

Database lock is the gate between data collection and the statistical analysis plan execution. When data quality is treated as a final sprint — rushing queries, outstanding protocol deviations, and missing data points in the weeks before lock — query resolution rates drop, protocol deviations are under-reported, and analysis datasets are delivered with residual errors. An FDA or EMA inspection during the submission review that surfaces data integrity gaps can result in a Complete Response Letter or a clinical hold. The cost of a late, error-laden lock routinely exceeds the cost of the entire in-trial data-management program.

## How to apply

Instrument data quality as a rolling KPI throughout the trial, not a pre-lock check.

```
Rolling data quality metrics (check at every data review):
- Outstanding query rate: target <2% of total data points
- Query resolution cycle time: target ≤14 days (median)
- Protocol deviation rate: tracked by category and site
- Missing data % by field and visit: flagged at >5% per field
- AE/SAE reconciliation: 100% before each interim analysis lock
- SDV completion by site tier: tracked against the risk-based monitoring plan
```

**Do:**
- Set a data-management cleaning milestone at the end of each study period/quarter, not only at the end of the trial.
- Reconcile safety data (AE/SAE) with the pharmacovigilance database at each interim analysis, not only at final lock.
- Report the outstanding query rate by site in the same dashboard as enrollment and retention metrics.

**Don't:**
- Allow >60-day-old open queries to accumulate — they are almost always unresolvable at lock.
- Defer protocol deviation categorization to the post-lock period; deviations shape the per-protocol population definition.
- Use "database lock" as a synonym for "data quality complete" — they are different milestones.

## Edge cases / when the rule does NOT apply

For early feasibility or pilot studies with minimal data collection (e.g., a 5-patient phase-I dose-escalation with a single endpoint), a lighter rolling check is acceptable — but the principle that queries should be aging-capped still applies.

## See also

- [`../agents/regulatory-submissions-specialist.md`](../agents/regulatory-submissions-specialist.md) — data quality underpins submission readiness and inspection response.
- [`../agents/clinical-operations-manager.md`](../agents/clinical-operations-manager.md) — site-level query rate and SDV compliance feed into this metric.
- [`./the-submission-is-built-throughout-not-at-the-end.md`](./the-submission-is-built-throughout-not-at-the-end.md) — the overarching principle.

## Provenance

Codifies the submission-built-throughout principle (CLAUDE.md §3 #7) applied to data management; grounded in ICH E6(R3) Good Clinical Practice guideline and standard FDA/EMA data integrity inspection expectations.

---

_Last reviewed: 2026-06-05 by `claude`_
