# Kill the N+1 with batching

**Status:** Absolute rule
**Domain:** Performance
**Applies to:** `graphql-engineering`

> Engineering rule. GraphQL library/spec/version specifics are `[verify-at-use]`. No PII.

---

## Why this exists

GraphQL's per-field resolver model makes the N+1 query the default failure mode: a list of N parents whose child field resolves independently issues one downstream call per parent — N+1 round-trips for what should be one or two. It is invisible in a single-item test and catastrophic under a real query. Batching per request is not an optimization you add later; it is how a correct resolver layer is built.

## How to apply

- Put a **DataLoader** (or equivalent batch-and-cache) in front of every by-key fetch; collect keys within a tick and resolve them in one batched call.
- Scope loaders **per request** so caching and deduplication are correct and never leak data across users.
- Measure resolver fan-out — count downstream calls per query, not just wall-clock — and treat a call count that scales with result size as a bug.
- Prefer batched data-source methods (`getUsersByIds`) over per-item fetches the resolver calls in a loop.

**Do:** instantiate loaders in per-request context; assert downstream call counts in tests.
**Don't:** call the database or a service directly inside a field resolver that runs per list item.

## Edge cases / when the rule does NOT apply

A root field that fetches a single object, or a field backed by already-loaded in-memory data, needs no loader — batching matters wherever a field resolves once *per parent* in a list.

## See also

- [`../skills/resolver-performance-and-n-plus-one/SKILL.md`](../skills/resolver-performance-and-n-plus-one/SKILL.md)
- Template: [`../templates/graphql-schema-and-perf-review.md`](../templates/graphql-schema-and-perf-review.md)

## Provenance

Codifies `graphql-server-engineer` house opinion on per-request batching and fan-out measurement. Library specifics: [`../knowledge/graphql-reference-2026.md`](../knowledge/graphql-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-05 by `claude`_
