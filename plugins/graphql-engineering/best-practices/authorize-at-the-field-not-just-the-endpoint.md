# Authorize at the field, not just the endpoint

**Status:** Absolute rule
**Domain:** Security
**Applies to:** `graphql-engineering`

> Engineering rule. GraphQL library/spec/version specifics are `[verify-at-use]`. No PII.

---

## Why this exists

One GraphQL endpoint exposes the entire graph, and a single query can traverse from a permitted type into a sensitive one through relationships. Endpoint-level authentication only proves *who is calling* — it says nothing about whether this principal may read *this field on this object*. Authorization therefore has to live where the data is resolved: at the field and type resolvers, evaluated against the request's principal, every time.

## How to apply

- Carry the authenticated **principal** in per-request context and enforce authorization inside field/type resolvers — never assume a passed gate at the endpoint suffices.
- Check authorization against the **specific object** being resolved (ownership / tenancy / role), not just the type, so relationship traversal can't leak data.
- Keep policy centralized (a reusable authorizer / directive) rather than re-implemented ad hoc per resolver, so gaps are visible and auditable.
- Return a consistent not-authorized result; avoid leaking existence through differing error shapes.
- Apply the same enforcement to mutations and to fields reached via nested paths, not only top-level queries.

**Do:** authorize each sensitive field against the request principal and the concrete object.
**Don't:** treat "authenticated at the endpoint" as authorization, or guard only root fields and trust nested traversal.

## Edge cases / when the rule does NOT apply

A fully public, read-only graph with no non-public data needs no per-field checks — but the moment any field is principal-scoped, field-level enforcement is required for the whole traversable neighborhood.

## See also

- [`../skills/graphql-security-and-governance/SKILL.md`](../skills/graphql-security-and-governance/SKILL.md)
- Template: [`../templates/graphql-schema-and-perf-review.md`](../templates/graphql-schema-and-perf-review.md)

## Provenance

Codifies `graphql-security-governance-engineer` house opinion on field-level, principal-aware authorization. Library/directive specifics: [`../knowledge/graphql-reference-2026.md`](../knowledge/graphql-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-05 by `claude`_
