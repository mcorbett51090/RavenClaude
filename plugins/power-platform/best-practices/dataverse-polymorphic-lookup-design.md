# Use polymorphic lookups only where the fan-out is unavoidable

**Status:** Pattern
**Domain:** Dataverse data modeling
**Applies to:** `power-platform`

---

## Why this exists

A Dataverse polymorphic lookup (the `Customer` column type, or a multi-table `Regarding` field) lets one column point to rows in more than one entity — for example, a case can relate to either an Account or a Contact. The flexibility is real, but the cost is significant: polymorphic lookups do not support server-side `$filter` the same way a standard lookup does, they complicate Power Fx `Patch` calls (the record type must be specified explicitly), they break FetchXML `link-entity` aggregations, and they require the UI to show a two-step picker. Reaching for the `Customer` column as a general "flexible reference" pattern is a design smell.

## How to apply

Apply the narrowest relationship type that satisfies the requirement:

| Requirement | Correct column type |
|---|---|
| Always points to one specific entity | Standard lookup |
| Must point to one of exactly two well-known entities (and they are the canonical Salesforce/CRM "party" types) | Customer (polymorphic) |
| Must point to any entity (activity-party style) | `Regarding` on Activity entities only |
| Multiple entity types, but you control the schema | Consider a base/abstract entity pattern with child entities instead |

**Do:**
- Document on every Customer/polymorphic column which entity types it may reference and whether that set is open or closed.
- Write Power Fx `Patch` with the explicit `{Id: ..., '@odata.type': 'Microsoft.Dynamics.CRM.account'}` shape when writing to a polymorphic column.
- Test FetchXML queries against polymorphic columns in the target environment — aggregate behavior varies by Dataverse build.

**Don't:**
- Create polymorphic lookups for convenience when a standard lookup to a common parent entity would work.
- Mix polymorphic-column reads with `Lookup()` in canvas apps without handling the multi-type result — it returns a record whose type depends on which entity is referenced, and the behavior differs from a typed lookup.
- Add a third entity to an existing `Customer` column mid-project — this is a schema change and requires testing every form, view, and flow that reads the column.

## Edge cases / when the rule does NOT apply

The standard Dataverse `Regarding` column on Activity entities (email, phone call, task) is intentionally polymorphic by design — leave it as-is and do not try to replace it with a typed lookup.

## See also

- [`../agents/dataverse-architect.md`](../agents/dataverse-architect.md) — owns column-type selection
- [`./dataverse-choice-vs-lookup-vs-customer-column.md`](./dataverse-choice-vs-lookup-vs-customer-column.md) — the full choice/lookup/customer selection tree

## Provenance

Codifies `dataverse-architect`'s opinion informed by known limitations of polymorphic lookups in Power Fx, FetchXML, and the Dataverse Web API; standard Dataverse data-modeling practice.

---

_Last reviewed: 2026-06-05 by `claude`_
