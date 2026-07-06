# Design the schema for clients, not your database

**Status:** Absolute rule
**Domain:** Schema design
**Applies to:** `graphql-engineering`

> Engineering rule. GraphQL library/spec/version specifics are `[verify-at-use]`. No PII.

---

## Why this exists

A GraphQL schema is the public contract clients program against for years, not a projection of today's tables. When the graph mirrors your database — foreign-key IDs, join tables, column-shaped fields — every future storage change becomes a breaking API change, and clients inherit accidental complexity that has nothing to do with their use-cases. Model the domain and the questions clients actually ask; let resolvers bridge to whatever storage sits behind.

## How to apply

- Start from client use-cases and domain concepts; name types and fields for the domain, not for tables or columns.
- Expose relationships as typed edges (`author: User`), not raw foreign keys the client must re-join.
- Make **nullability deliberate**: non-null is a permanent promise, so default to nullable and mark non-null only where the value is truly always present.
- Standardize pagination across the graph — use Relay-style connections (`edges`/`node`/`pageInfo`, cursors) rather than ad-hoc `limit`/`offset` per field.
- Keep DB shape behind the resolver layer; leaking it couples the contract to storage.

**Do:** design the type for how clients consume it; choose non-null only when the guarantee is permanent.
**Don't:** auto-generate the schema from your ORM/tables and ship that as the contract.

## Edge cases / when the rule does NOT apply

An internal, single-consumer, short-lived BFF graph can pragmatically track its backing store — but the moment a second client or a longer lifetime appears, the client-first contract wins.

## See also

- [`../skills/graphql-schema-design-and-evolution/SKILL.md`](../skills/graphql-schema-design-and-evolution/SKILL.md)
- Template: [`../templates/graphql-schema-design-doc.md`](../templates/graphql-schema-design-doc.md)

## Provenance

Codifies `graphql-schema-architect` house opinion on client-first modeling and deliberate nullability. Spec/library specifics: [`../knowledge/graphql-reference-2026.md`](../knowledge/graphql-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-05 by `claude`_
