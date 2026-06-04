---
name: data-quality-testing
description: "Keep the warehouse trustworthy: dbt tests (not_null/unique/accepted_values/relationships) gating the build in CI, source-freshness checks, model contracts at consumer boundaries, singular tests for business invariants, and anomaly detection beyond schema tests."
---

# Data Quality Testing

## Test like code
not_null / unique / accepted_values / relationships on the columns that matter; **build fails** on violation. Untested transforms = silent downstream corruption.

## Freshness
Assert source freshness; **stop** rather than serve stale marts as fresh.

## Contracts
Model contracts (names/types/constraints) on consumer-facing models so upstream changes can't silently break a dashboard.

## Beyond schema
Singular tests for business invariants (line items sum to order total). **Anomaly detection** (row-count drop, distribution shift) catches what schema tests miss -> significance to `applied-statistics`.
