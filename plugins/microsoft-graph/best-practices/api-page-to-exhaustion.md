# Page to exhaustion — a first page is not "all results"

**Status:** Absolute rule — code that reads `value` once and stops has shipped a silent sampling bug.

**Domain:** Web API / OData paging

**Applies to:** `microsoft-graph`

---

## Why this exists

Many Graph collection reads are paged: `GET /users` returns 100 by default, and the response carries an `@odata.nextLink` whenever more data exists. Code that consumes only the first `value` array looks correct in dev (small tenant, one page) and quietly drops records in production (large tenant, many pages). The failure is invisible — no error, no 4xx, just *fewer rows than reality*. The fix is mechanical and non-negotiable: follow `@odata.nextLink` until it is absent.

## How to apply

Loop on `@odata.nextLink`, using the **entire URL verbatim**. Don't extract `$skiptoken`/`$skip` and rebuild a request — the token is opaque and encodes the original query parameters. Prefer the SDK `PageIterator`, which handles the loop and re-applies headers for you.

```http
GET https://graph.microsoft.com/v1.0/users?$select=id,displayName&$top=999
# response → "value":[...], "@odata.nextLink":"https://graph.microsoft.com/v1.0/users?$skiptoken=..."
GET <the @odata.nextLink URL, unchanged>   # repeat until no @odata.nextLink
```

```csharp
// Microsoft.Graph (.NET v5+) — PageIterator drains every page
var first = await graphClient.Users.GetAsync(rc =>
    rc.QueryParameters.Select = new[] { "id", "displayName" });

var all = new List<User>();
var iterator = PageIterator<User, UserCollectionResponse>
    .CreatePageIterator(graphClient, first, u => { all.Add(u); return true; });
await iterator.IterateAsync();
```

**Do:**
- Treat the presence of `@odata.nextLink` as the only signal "there's more" — keep going until it's gone.
- Use the nextLink URL exactly as returned; re-send custom headers (e.g. `ConsistencyLevel`) on each page — they are **not** carried over automatically.
- Raise `$top` (up to the API max, often 999) to cut the number of round-trips.

**Don't:**
- Read `value` once and assume completeness.
- Parse out `$skiptoken`/`$skip` and craft your own next request.
- Assume a page is non-empty — a page can be empty **and still** carry a `@odata.nextLink` (especially in delta).

## Edge cases / when the rule does NOT apply

A `GET` of a single entity (`/users/{id}`) doesn't page. Some resources don't support paging at all — e.g. `directoryRole` and its members `[verify-at-build]` — so there's no nextLink to follow. When using `$count=true` against directory objects, `@odata.count` appears **only on the first page**, so capture it there. Different APIs treat an over-max `$top` differently (clamp, ignore, or 400) — don't assume your requested page size was honored.

## See also

- [`./api-select-only-what-you-need.md`](./api-select-only-what-you-need.md) — shape the query before you page it
- [`./api-delta-for-what-changed.md`](./api-delta-for-what-changed.md) — delta paging ends on `@odata.deltaLink`, not absence of nextLink
- [`./api-use-the-sdk-not-raw-http-for-resilience.md`](./api-use-the-sdk-not-raw-http-for-resilience.md) — `PageIterator` does this loop for you
- [`../agents/graph-api-engineer.md`](../agents/graph-api-engineer.md) — owns paging
- [Paging Microsoft Graph data in your app](https://learn.microsoft.com/graph/paging) — authoritative

## Provenance

From the Microsoft Learn "Paging Microsoft Graph data" and "Page through a collection using the SDKs" pages (retrieved 2026-05-30 via Microsoft Learn MCP), codifying team house opinion #4 ("page everything; assume more than one page"). Default/maximum page sizes and the no-paging resource list are version-sensitive — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
