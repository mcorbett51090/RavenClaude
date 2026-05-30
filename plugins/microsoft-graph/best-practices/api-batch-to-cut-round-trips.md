# Batch to cut round-trips — combine independent calls into one $batch

**Status:** Pattern — when you have several independent Graph calls, `$batch` them; deviate only with a reason.

**Domain:** Web API / resilience

**Applies to:** `microsoft-graph`

---

## Why this exists

Every Graph call is a network round-trip with latency. A view that needs a user's profile, their calendar for today, and a group's membership is three serial round-trips — or one `$batch` POST carrying all three. JSON batching combines up to 20 requests into a single HTTP call, cutting latency and connection overhead, and doubles as a workaround for URLs too long for a client's limits (a complex `$filter` becomes part of the request body). Fewer round-trips also means fewer chances to trip a per-request throttle from connection churn.

## How to apply

POST to `/$batch` with a `requests` array; each item has an `id`, `method`, and **relative** `url`. Use `dependsOn` only when one request must follow another.

```http
POST https://graph.microsoft.com/v1.0/$batch
Content-Type: application/json

{
  "requests": [
    { "id": "1", "method": "GET", "url": "/me" },
    { "id": "2", "method": "GET", "url": "/me/calendarView?startDateTime=2026-05-30T00:00:00Z&endDateTime=2026-05-31T00:00:00Z" },
    { "id": "3", "method": "GET", "url": "/groups/{id}/members?$select=id,displayName" }
  ]
}
```

```csharp
// Microsoft.Graph (.NET v5+) — the SDK auto-splits batches over 20 requests
var batch = new BatchRequestContentCollection(graphClient);
var meId   = await batch.AddBatchRequestStepAsync(graphClient.Me.ToGetRequestInformation());
var resp   = await graphClient.Batch.PostAsync(batch);
var me     = await resp.GetResponseByIdAsync<User>(meId);
```

**Do:**
- Group **independent** reads/writes; let the service run them in the most efficient order.
- Correlate responses by `id` — responses can come back in a different order than the requests.
- Inspect **each** sub-response's `status` — a `200` on the batch envelope says nothing about the parts.

**Don't:**
- Exceed 20 requests per batch (the SDK auto-splits; raw HTTP does not — you'll get a 400).
- Use `dependsOn` for unrelated requests — keep a batch either fully parallel or fully sequential (a failed dependency cascades `424 Failed Dependency`).
- Assume the SDK retried a throttled sub-request — it didn't (see the throttling caveat).

## Edge cases / when the rule does NOT apply

A `200` batch can carry `429`s inside it, and batched sub-requests are **not** auto-retried by the SDK — retry the failed ones yourself, ideally in a new batch after the longest `Retry-After`. Each sub-request is metered individually against throttling limits, so a 20-request batch is not "one request" for quota purposes. Sub-request dependencies are limited to one of three shapes (all-parallel, all-serial, or all-depend-on-the-same-one) `[verify-at-build]`. Outlook caps the parallelism of unordered same-mailbox batch items (~4 at a time) — sequence with `dependsOn` if ordering matters there.

## See also

- [`./api-honor-throttling-and-retry-after.md`](./api-honor-throttling-and-retry-after.md) — the per-sub-request 429 handling
- [`./api-select-only-what-you-need.md`](./api-select-only-what-you-need.md) — shape each sub-request too
- [`../agents/graph-api-engineer.md`](../agents/graph-api-engineer.md) — owns batching
- [Combine multiple HTTP requests using JSON batching](https://learn.microsoft.com/graph/json-batching) — authoritative
- [Use the Microsoft Graph SDKs to batch requests](https://learn.microsoft.com/graph/sdks/batch-requests)

## Provenance

From the Microsoft Learn "JSON batching" and "SDKs to batch requests" pages plus the throttling-and-batching section (retrieved 2026-05-30 via Microsoft Learn MCP), codifying team house opinion #5. The 20-request limit and the `dependsOn` pattern restrictions are documented but evolving ("as JSON batching matures, these limitations will be removed") — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
