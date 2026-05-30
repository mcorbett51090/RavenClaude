# Use the Graph SDK, not raw HTTP, for resilience

**Status:** Pattern

**Domain:** API / Resilience

**Applies to:** microsoft-graph

---

## Why this exists

Hand-rolled `HttpClient` calls to Graph re-implement — usually badly — the things the official SDKs already do correctly: paging, `429`/`Retry-After` retry with backoff, large-file upload sessions, `$batch` assembly, and token attachment via MSAL. Teams that "just call the REST endpoint" ship the same throttling and paging bugs the SDK was built to prevent. The SDK is the grounded default; raw HTTP is the exception you justify.

## How to apply

Use the Graph SDK + its auth provider so retry, paging, and token handling come for free.

```csharp
// .NET — GraphServiceClient with a credential; retry + paging handled by the SDK
var credential = new ClientCertificateCredential(tenantId, clientId, cert);
var graph = new GraphServiceClient(credential, new[] { "https://graph.microsoft.com/.default" });

// Paging: PageIterator walks @odata.nextLink to exhaustion — you don't hand-loop
var page = await graph.Users.GetAsync(r => r.QueryParameters.Select = new[] { "id", "mail" });
var all = new List<User>();
var it = PageIterator<User, UserCollectionResponse>.CreatePageIterator(graph, page, u => { all.Add(u); return true; });
await it.IterateAsync();
```

**Do:**

- Use the maintained SDK for your language (.NET / JS / Python / Java) and its MSAL-backed auth provider.
- Lean on `PageIterator` (or the JS `PageIterator`) for paging and the SDK's built-in retry handler for `429`.

**Don't:**

- Re-implement `@odata.nextLink` loops, `Retry-After` math, or upload-session chunking by hand.
- Attach tokens manually when the SDK's credential/auth provider does it (and caches them).

## Edge cases / when the rule does NOT apply

- A tiny one-off script or a language with no SDK may justify raw HTTP — then you **own** paging + retry + token handling explicitly (see [`api-page-to-exhaustion.md`](./api-page-to-exhaustion.md), [`api-honor-throttling-and-retry-after.md`](./api-honor-throttling-and-retry-after.md)).
- A brand-new beta endpoint the SDK hasn't modeled yet may need a raw request via the SDK's `WithUrl`/request-builder escape hatch — still inside the SDK's pipeline.

## See also

- [`api-honor-throttling-and-retry-after.md`](./api-honor-throttling-and-retry-after.md) · [`api-page-to-exhaustion.md`](./api-page-to-exhaustion.md) · [`api-batch-to-cut-round-trips.md`](./api-batch-to-cut-round-trips.md)
- [`../agents/graph-api-engineer.md`](../agents/graph-api-engineer.md)

## Provenance

Distilled from the Graph API team constitution ([`../CLAUDE.md`](../CLAUDE.md) §3) and the SDK resilience features (retry handler, `PageIterator`, upload sessions). SDK method names/signatures are version-specific — `[verify-at-build]` against your SDK version.

---

_Last reviewed: 2026-05-30 by `claude`_
