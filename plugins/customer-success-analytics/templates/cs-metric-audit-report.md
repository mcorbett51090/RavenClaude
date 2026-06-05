# CS Metric Audit Report

> **Use for:** documenting the findings from a CS analytics metric audit. One report per audit run. Produced by the `cs-metric-audit` skill; handed to the `cs-analytics-architect` for mart fixes and to `data-platform` for pipeline work.

---

**Audit date:** [YYYY-MM-DD]
**Dashboard / surface audited:** [dashboard name or URL]
**Mart version / last refresh:** [date]
**Audited by:** [agent or analyst]
**Triggered by:** [scheduled quarterly / CS leader reported discrepancy / pre-rebuild / QBR prep]

---

## Metric inventory

| Metric name | Where computed | Source | Window | NULL handling | Status |
|---|---|---|---|---|---|
| [metric 1] | [mart / BI-tool / live API] | [table.column] | [window] | [NULL / zero] | [PASS / FLAG] |
| [metric 2] | | | | | |
| [metric 3] | | | | | |

---

## Flags found

### Mart-bypass violations (metric computed outside the mart)

| Metric | Location | Impact | Recommended fix |
|---|---|---|---|
| [metric name] | [BI-tool SQL / live API call] | [divergence risk / query latency] | [move to mart model] |

### NULL handling violations (NULL silently converted to 0 or omitted)

| Metric | Location | Impact | Recommended fix |
|---|---|---|---|
| [metric name] | [mart model / BI layer] | [inflated score for absent signal] | [return explicit NULL] |

### Trend-column violations (trend computed at query time, not materialized)

| Metric | Location | Impact | Recommended fix |
|---|---|---|---|
| [metric name] | [BI-tool window function / mart] | [inconsistent values; slow queries] | [materialize in mart model] |

### Explainability gaps (Red accounts with no named tier drivers)

- Red accounts missing `tier_driver_1`: [count / %]
- Red accounts missing `tier_driver_2`: [count / %]
- Recommended fix: [update tier rule or driver-population logic in mart]

---

## Health snapshot check

| Check | Result | Detail |
|---|---|---|
| Append-only (no deletes / upserts) | [PASS / FAIL] | |
| Row count stable per date | [PASS / FAIL] | [date range] |
| Trend columns materialized | [PASS / FAIL] | |
| NULL is NULL (not zero) | [PASS / FAIL] | |

---

## Identity-resolution check

| Check | Result | Detail |
|---|---|---|
| Unresolved account_ids in health snapshot | [N] | [0 = PASS] |
| Name-match joins found in mart | [yes / no] | [tables if yes] |
| `bridge_account_xref` used as join spine | [yes / no] | |

---

## Summary

- Total metrics audited: [N]
- Passed: [N]
- Flagged: [N] ([N] critical / [N] medium / [N] low)

---

## Handoff to data-platform

| Work item | Priority | Owner | Notes |
|---|---|---|---|
| [mart fix description] | [P0 / P1 / P2] | data-platform | |

---

## Next audit

- Recommended re-audit date: [YYYY-MM-DD]
- Trigger: [quarterly / after mart fixes deployed / after new source added]
