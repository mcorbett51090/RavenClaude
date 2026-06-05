---
scenario_id: 2026-06-05-test-coverage-gap-silent-corruption
contributed_at: 2026-06-05
plugin: analytics-engineering
product: dbt-core
product_version: "1.8"
scope: likely-general
tags: [data-quality, test-coverage, relationships, freshness, ci-gate]
confidence: medium
reviewed: false
---

## Problem

A weekly executive revenue report dropped ~6% with no business explanation. Investigation traced it to a `dim_customers` rebuild that had silently lost a slice of rows: an upstream source change renamed a region code, the staging model's hard-coded `accepted_values` mapping let the unmapped rows through as `NULL` region, and a downstream mart `INNER JOIN`ed customers to regions — so the unmapped customers (and their revenue) simply fell out of the join. No test failed because the only tests on the project were `not_null` and `unique` on primary keys. The corruption was *structurally valid* (no nulls where keys were, no dup keys) and therefore invisible.

## Constraints context

- dbt Core project with ~40 models; test coverage was "PK tests only" — `not_null` + `unique` on the surrogate keys, nothing on relationships, accepted values, freshness, or row counts.
- The CI pipeline ran `dbt build` but the only gate was "does it compile and do the PK tests pass" — so a referential drop and a stale source both passed CI green.
- The source-system change (region rename) was upstream of the team's control (ingestion's lane), so the only defensible boundary was a test that *caught* the bad data at the staging boundary, not prevention at source.
- The report consumer trusted "the dashboard is green" as "the number is right" — there was no signal distinguishing "pipeline ran" from "pipeline ran correctly."

## Attempts

- Tried: re-running the full pipeline to "refresh" the number. It reproduced the same wrong number — a re-run of a logically-broken build is still broken. Re-running until it looks right is the anti-pattern (it just hides intermittent drift behind a green run).
- Tried: adding a `relationships` test from `fct_revenue.customer_id` to `dim_customers.customer_id`. It immediately failed — surfacing that customers were being dropped at the join. The failing test *was* the diagnosis: a referential gap that the `INNER JOIN` had been hiding by silently excluding rows.
- Tried: adding an `accepted_values` test on the region code in staging (the boundary where the source lands) so a *new* unmapped region fails the build at staging instead of leaking a `NULL` downstream. Also added the new code to the mapping. This catches the next source rename at the edge.
- Tried: a `dbt_utils`/source-freshness gate plus a trailing row-count anomaly test on `dim_customers` so a sudden row-count drop (the loud symptom of the silent join loss) fails CI. Wired both into the CI gate so a green build now means "ran *and* the data passed its contracts," not just "compiled."

## Resolution

**Test the data like code, at the boundary, and make CI gate on it.** The coverage that would have caught this:

1. **`relationships` tests across every mart join** — an `INNER JOIN` that silently drops unmatched rows is the most common invisible-revenue-loss bug; a relationships test makes the orphan loud instead of silent.
2. **`accepted_values` (and not_null) at the staging boundary** — validate the source's categorical fields where they land, so a renamed/added code fails at the edge rather than leaking a `NULL` into a downstream join.
3. **Source freshness + row-count anomaly gates** — a freshness check catches a stale/paused load; a trailing row-count anomaly check catches a sudden drop that has no schema-level signal.
4. **Gate CI on the tests, and treat "green" as "data passed its contracts."** If the only CI gate is "compiles + PK tests," a structurally-valid corruption ships green. A re-run is never the fix for a failing data test — fix the cause upstream and let the test confirm.

The trap is that PK-only test coverage gives a *false sense of safety*: the build is green, the keys are unique and non-null, and the data is still wrong because the failure mode (a dropped referential slice, a stale load, a renamed category) lives in the gaps PK tests don't cover. Coverage is the defect when a stakeholder, not a test, spots the bad number.

**Action for the next engineer:** when a number moves with no business reason and the build is green, the coverage gap *is* the bug — add the test that would have caught it (usually `relationships` or a row-count anomaly) *before* fixing the value, so the next occurrence fails CI instead of reaching a dashboard.

Cross-reference: the field-note complement to [`../best-practices/test-data-like-code.md`](../best-practices/test-data-like-code.md), [`../best-practices/test-relationships-across-mart-joins.md`](../best-practices/test-relationships-across-mart-joins.md), and [`../best-practices/gate-on-source-freshness.md`](../best-practices/gate-on-source-freshness.md). For triage routing, see the "Data quality failure triage" tree in [`../knowledge/analytics-engineering-decision-trees.md`](../knowledge/analytics-engineering-decision-trees.md).
