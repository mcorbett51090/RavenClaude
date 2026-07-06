# Make schema changes additive and non-breaking

**Status:** Absolute rule
**Domain:** Schema evolution
**Applies to:** `graphql-engineering`

> Engineering rule. GraphQL library/spec/version specifics are `[verify-at-use]`. No PII.

---

## Why this exists

GraphQL has no URL-based versioning: there is one schema, and every client shares it. Removing a field, renaming it, changing its type, or tightening its nullability breaks whatever query still selects it — silently, at the client, in production. The schema evolves the only safe way it can: by **adding**. Deprecate what you want to retire, keep serving it, and remove it only once you can prove no client depends on it.

## How to apply

- Evolve by **adding** new fields, types, and enum values; introduce a replacement alongside the old field rather than mutating it in place.
- Mark retiring fields with `@deprecated(reason: "...")` pointing to the replacement — deprecation is a signal, not a removal.
- Treat removing a field, renaming it, changing its type, or making a nullable field non-null-in-input / non-null→nullable-in-output as a **breaking change** requiring a migration plan.
- **Track field usage** from real traffic before any removal; remove only after usage is zero across the deprecation window.
- Gate merges with schema-diff / breaking-change checks in CI.

**Do:** add-then-deprecate-then-remove-on-evidence; run a breaking-change check on every schema PR.
**Don't:** rename or retype a live field in place, or delete a deprecated field on a hunch that "no one uses it."

## Edge cases / when the rule does NOT apply

A schema still in pre-release with no external consumers can break freely — the rule binds the moment a client you don't control has queried the field.

## See also

- [`../skills/graphql-schema-design-and-evolution/SKILL.md`](../skills/graphql-schema-design-and-evolution/SKILL.md)
- Template: [`../templates/graphql-schema-design-doc.md`](../templates/graphql-schema-design-doc.md)

## Provenance

Codifies `graphql-schema-architect` house opinion on additive evolution and usage-gated removal. Spec/directive specifics: [`../knowledge/graphql-reference-2026.md`](../knowledge/graphql-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-05 by `claude`_
