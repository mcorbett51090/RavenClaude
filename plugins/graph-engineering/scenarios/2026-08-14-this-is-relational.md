# This is relational

**Date:** 2026-08-14
**Tags:** graph-vs-relational
**Unverified** — teaching scenario.

A team asked to “model orders and customers as a graph” because they wanted “customer → orders → line items.” Every hop was a known foreign key; every write was a multi-row transaction with a rollback story; ad-hoc SQL was the reporting language.

**Fix:** stay in `database-engineering`. A foreign-key join is not a variable-depth traversal. Revisit a graph only if a *path* question appears (fraud rings, recommendation, BOM explosion) that SQL cannot bound.

See [`../knowledge/graph-vs-relational-decision-tree.md`](../knowledge/graph-vs-relational-decision-tree.md).
