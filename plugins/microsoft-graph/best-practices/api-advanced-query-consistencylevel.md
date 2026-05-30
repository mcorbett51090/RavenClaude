# Advanced query — ConsistencyLevel: eventual + $count, deliberately

**Status:** Primary diagnostic — when a directory-object `$count`/`$search`/`$orderby`/`ne`/`endsWith` query errors or silently ignores `$count`, the advanced-query headers are missing.

**Domain:** Web API / OData query shaping

**Applies to:** `microsoft-graph`

---

## Why this exists

Graph fulfills queries from an index store. Some capabilities on Microsoft Entra **directory objects** (`user`, `group`, `application`, `device`, `orgContact`, and others deriving from `directoryObject`) are served from a *separate* index and are off by default: `$count`, `$search`, `$orderby` combined with `$filter`, and operators like `ne`, `not`, `endsWith`, plus `startswith` on some properties. To opt in you must set the **ConsistencyLevel: eventual** header **and** (except for bare `$search`) include `$count=true`. Omit them and the request either returns an error (e.g. on the `/$count` segment) or **silently ignores** `?$count=true` — a subtle failure that looks like "the filter just doesn't work."

## How to apply

Add the header and the `$count` parameter together when the operator/parameter requires it.

```http
GET https://graph.microsoft.com/v1.0/users?$filter=endsWith(mail,'@contoso.com')&$count=true&$orderby=displayName
ConsistencyLevel: eventual
```

```csharp
// Microsoft.Graph (.NET v5+) — count + advanced filter on a directory collection
var page = await graphClient.Users.GetAsync(rc =>
{
    rc.QueryParameters.Filter  = "endsWith(mail,'@contoso.com')";
    rc.QueryParameters.Count   = true;                  // adds $count=true
    rc.QueryParameters.Orderby = new[] { "displayName" };
    rc.Headers.Add("ConsistencyLevel", "eventual");     // required
});
```

**Do:**
- Set `ConsistencyLevel: eventual` **and** `$count=true` together for advanced directory-object queries (`$count=true` is not needed for a bare `$search`, but the header still is).
- Re-send `ConsistencyLevel` on **every page** — it is not carried into `@odata.nextLink` requests automatically.
- Read `@odata.count` from the **first page only** — it isn't repeated on later pages.

**Don't:**
- Expect `?$count=true` to work without the header — it's silently dropped, so the result looks wrong with no error.
- Use advanced query where the default engine already handles it (e.g. `$filter=accountEnabled eq false` works by default — don't add ceremony you don't need).
- Treat advanced-query results as strongly consistent — "eventual" means a recent write may not be reflected yet.

## Edge cases / when the rule does NOT apply

Non-directory resources (mail messages, calendar events, drive items) have their own `$search`/`$filter` rules and generally do **not** use this header — advanced query is a *directory-object* mechanism. `$search` on directory objects is limited to specific properties (e.g. `displayName`/`description` on groups; other fields fall back to `startsWith`). Because results are eventually consistent, designs that immediately read-after-write should account for replication lag. Exactly which operators require advanced query is per-property and version-sensitive — `[verify-at-build]`.

## See also

- [`./api-select-only-what-you-need.md`](./api-select-only-what-you-need.md) — `$select` first; reach for advanced query only when needed
- [`./api-page-to-exhaustion.md`](./api-page-to-exhaustion.md) — re-send `ConsistencyLevel` on each page
- [`../knowledge/api-query-decision-trees.md`](../knowledge/api-query-decision-trees.md) — advanced-query-vs-default tree
- [`../agents/graph-api-engineer.md`](../agents/graph-api-engineer.md) — owns query shaping
- [Advanced query capabilities on Microsoft Entra ID objects](https://learn.microsoft.com/graph/aad-advanced-queries) — authoritative

## Provenance

From the Microsoft Learn "Advanced query capabilities on directory objects" and "$search query parameter" pages plus the per-resource list-method docs (retrieved 2026-05-30 via Microsoft Learn MCP), codifying team house opinion #3. The exact operators/properties gated behind advanced query are version-sensitive — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
