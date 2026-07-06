---
description: "Audit an existing GraphQL schema and server for breaking changes, N+1 / resolver fan-out, query-cost exposure, field-level authz gaps, and unbounded pagination (specifics verify-at-use)."
argument-hint: "[schema/SDL or endpoint + what changed]"
---

You are running `/graphql-engineering:review-schema-and-perf`. Use `graphql-server-engineer` + `graphql-security-governance-engineer` with the `resolver-performance-and-n-plus-one` and `graphql-security-and-governance` skills.

> Engineering judgment, not a certification. Every library version, GraphQL-spec detail, and cost/limit default is `[verify-at-use]`. Diff against the DEPLOYED schema, not intent. No PII in examples.

## Steps
1. Capture the schema/SDL or endpoint under review, the deployed-schema baseline to diff against, and what changed.
2. Run the breaking-change scan: removed, re-typed, or nullability-narrowed fields (and newly-required args) vs the deployed schema — each a live-client break.
3. Trace N+1 / resolver fan-out (resolver -> downstream calls -> batched? -> fix) and assess query-cost exposure (depth limit, cost budget, persisted queries, introspection in prod) — flag each library/limit specific `[verify-at-use]`.
4. Check field-level authorization at the resolver (not just the route) and pagination correctness (unbounded lists, unenforced max page size).
5. Emit using `templates/graphql-schema-and-perf-review.md` + the Structured Output block, with prioritized P0/P1/P2 findings and a remediation order that closes the surface (authz/cost guards) before reshaping the schema.
