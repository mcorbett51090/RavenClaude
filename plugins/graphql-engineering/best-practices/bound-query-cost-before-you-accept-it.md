# Bound query cost before you accept it

**Status:** Absolute rule
**Domain:** Security / performance
**Applies to:** `graphql-engineering`

> Engineering rule. GraphQL library/spec/version specifics are `[verify-at-use]`. No PII.

---

## Why this exists

A single GraphQL query can be arbitrarily expensive: deep nesting, wide selection sets, aliased duplication, and cyclic relationships let one request ask for work that no REST endpoint could express. Without a bound, that is a denial-of-service primitive handed to every caller. Cost must be measured and rejected **before execution begins** — once resolvers start fanning out, the damage is already done.

## How to apply

- Enforce a **maximum query depth** to stop pathological nesting and relationship cycles.
- Apply a **cost / complexity budget**: assign field weights, sum the query's static cost, and reject over-budget queries before they run.
- Bound breadth and aliasing — cap selection width and alias count so a caller can't multiply cost with repeated aliases.
- Prefer **persisted (allow-listed) queries** for first-party clients so only known, pre-costed operations execute in production.
- Layer rate limiting / timeouts as backstops, not as the primary control.

**Do:** reject on a static cost estimate at validation time; pre-register client operations where you can.
**Don't:** rely on execution timeouts or downstream rate limits to catch an expensive query after it's already running.

## Edge cases / when the rule does NOT apply

A fully persisted-query-only internal graph, where every operation is pre-registered and pre-costed, has already bounded cost — dynamic depth/complexity limits then matter most at the arbitrary-query edge.

## See also

- [`../skills/graphql-security-and-governance/SKILL.md`](../skills/graphql-security-and-governance/SKILL.md)
- Template: [`../templates/graphql-schema-and-perf-review.md`](../templates/graphql-schema-and-perf-review.md)

## Provenance

Codifies `graphql-security-governance-engineer` house opinion on pre-execution cost bounding and persisted queries. Limit/library specifics: [`../knowledge/graphql-reference-2026.md`](../knowledge/graphql-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-05 by `claude`_
