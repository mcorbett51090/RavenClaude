# Select only what you need — never read a Graph collection bare

**Status:** Absolute rule — a collection `GET` with no `$select` is an over-fetch bug, not a style choice.

**Domain:** Web API / OData query shaping

**Applies to:** `microsoft-graph`

---

## Why this exists

Every property you don't `$select` is network, serialization, and memory you pay for and throw away — and for `user`, `group`, and other resources deriving from `directoryObject`, the opposite failure also bites: the **default property set on a list/read is only a subset**, so the field you actually need (e.g. `streetAddress`, `signInActivity`) is *silently absent* until you `$select` it. Graph cares enough about this that an un-`$select`ed `GET` comes back with a `@microsoft.graph.tips` property literally nagging you to add one. The sibling failure is filtering client-side: paging an entire collection into memory to keep three rows wastes calls, burns throttling budget, and doesn't scale past the first tenant that grows.

## How to apply

Name the properties. Filter and search on the **server**, not in your loop.

```http
GET https://graph.microsoft.com/v1.0/users?$select=id,displayName,mail,accountEnabled&$filter=accountEnabled eq false&$top=999
```

```csharp
// Microsoft.Graph (.NET v5+) — projection + server-side filter
var page = await graphClient.Users.GetAsync(rc =>
{
    rc.QueryParameters.Select = new[] { "id", "displayName", "mail", "accountEnabled" };
    rc.QueryParameters.Filter = "accountEnabled eq false";
    rc.QueryParameters.Top    = 999;
});
```

**Do:**
- `$select` the explicit, minimal property list on every collection read — and on `$expand`ed children too: `$expand=members($select=id,displayName)`.
- Push predicates server-side with `$filter` (and `$search` for free-text); let Graph do the narrowing.
- Treat the `@microsoft.graph.tips` projection hint in a response as a defect to fix, not noise.

**Don't:**
- `GET /users` (or any collection) with no `$select` — over-fetch by default.
- Pull a whole collection and filter it in application code when `$filter`/`$search` would do it server-side.
- Assume a default read returned every property — on directory objects it returned a subset.

## Edge cases / when the rule does NOT apply

A single-entity `GET` of a small fixed-shape resource where you genuinely use every property is defensible without `$select` (but it's cheap insurance to add it). Some relationships don't support `$expand` with `$select` on the expanded items, and on directoryObject resources `$expand` typically caps at ~20 items with **no** `nextLink` `[verify-at-build]` — so `$expand` is not a substitute for paging a large child collection. Not every property is `$filter`able server-side; where the engine can't, you may need [advanced query](./api-advanced-query-consistencylevel.md) or, as a last resort, a documented client-side narrowing.

## See also

- [`./api-advanced-query-consistencylevel.md`](./api-advanced-query-consistencylevel.md) — when `$filter`/`$search`/`$count` need `ConsistencyLevel: eventual`
- [`./api-page-to-exhaustion.md`](./api-page-to-exhaustion.md) — what to do with the narrowed-but-still-multi-page result
- [`../agents/graph-api-engineer.md`](../agents/graph-api-engineer.md) — owns query shaping
- [Customize Microsoft Graph responses with query parameters — `$select`](https://learn.microsoft.com/graph/query-parameters#select) — authoritative
- [Best practices for working with Microsoft Graph — Optimizations](https://learn.microsoft.com/graph/best-practices-concept#optimizations)

## Provenance

From the Microsoft Learn pages on query parameters and Graph best practices (retrieved 2026-05-30 via Microsoft Learn MCP), codifying team house opinion #3 ("select what you need; never `GET /users` bare"). The directory-object default-subset behavior is documented on the Azure-AD-Graph→Microsoft-Graph request-differences page. Default property sets and `$expand` item caps are version-sensitive — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
