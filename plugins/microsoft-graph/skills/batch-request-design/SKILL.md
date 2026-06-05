---
name: batch-request-design
description: "Playbook for consolidating multiple Microsoft Graph API calls into a single $batch request — request shaping, dependency ordering, error handling per-response, and the throttling interaction that makes batching both necessary and tricky. Owned by graph-api-engineer."
---

# Batch Request Design

## When to invoke

- Making N independent Graph calls per user/item in a loop (the classic N+1 pattern).
- Hitting throttling limits from parallel per-item requests.
- Needing to execute a set of Graph mutations transactionally (within batch limits).
- Consolidating startup requests (get user + get mailboxSettings + get manager) into one round-trip.

## The $batch contract

A single `POST https://graph.microsoft.com/v1.0/$batch` can contain **up to 20 requests**. Each request in the body is a JSON object with `id`, `method`, `url`, and optionally `headers`, `body`, and `dependsOn`.

```http
POST https://graph.microsoft.com/v1.0/$batch
Content-Type: application/json
Authorization: Bearer {token}

{
  "requests": [
    {
      "id": "1",
      "method": "GET",
      "url": "/me?$select=id,displayName,mail"
    },
    {
      "id": "2",
      "method": "GET",
      "url": "/me/mailboxSettings"
    },
    {
      "id": "3",
      "method": "GET",
      "url": "/me/manager?$select=id,displayName"
    }
  ]
}
```

The response contains a `responses` array — one entry per request, keyed by `id`. Responses may arrive out-of-order.

## Handling batch responses

```python
def execute_batch(requests: list[dict], token: str) -> dict[str, dict]:
    """Returns {id: response_body} for each request."""
    resp = httpx.post(
        "https://graph.microsoft.com/v1.0/$batch",
        headers={"Authorization": f"Bearer {token}"},
        json={"requests": requests}
    )
    resp.raise_for_status()
    results = {}
    for r in resp.json()["responses"]:
        results[r["id"]] = r
        if r["status"] >= 400:
            # Handle per-request errors without failing the whole batch
            handle_batch_error(r)
    return results

def handle_batch_error(response: dict):
    status = response["status"]
    body = response.get("body", {})
    if status == 429:
        retry_after = response.get("headers", {}).get("Retry-After", "30")
        # Retry this specific sub-request after retry_after seconds
        ...
    elif status == 404:
        # Resource doesn't exist — not a fatal error for the batch
        ...
    else:
        raise GraphBatchError(f"Sub-request {response['id']} failed: {status} {body}")
```

**Critical:** a `429 Too Many Requests` on a sub-request within a batch means that specific sub-request was throttled — the other sub-requests in the batch may have succeeded. Process each response independently.

## Dependency ordering

Use `dependsOn` when a later request needs the result of an earlier one:

```json
{
  "requests": [
    {"id": "1", "method": "POST", "url": "/me/messages", "body": {...}},
    {"id": "2", "method": "POST", "url": "/me/messages/{id}/send",
     "dependsOn": ["1"]}
  ]
}
```

`dependsOn` makes the requests sequential within the batch. Without it, all requests execute in parallel — if request 2 needs the ID from request 1's response, use `dependsOn`.

## Chunking for > 20 requests

Split into batches of 20:

```python
def chunk_batch(requests: list[dict], size: int = 20):
    for i in range(0, len(requests), size):
        yield requests[i:i+size]

all_results = {}
for chunk in chunk_batch(all_requests):
    chunk_results = execute_batch(chunk, token)
    all_results.update(chunk_results)
```

Run chunks sequentially if you're near throttling limits. Run in parallel (with `asyncio.gather`) for higher-throughput pipelines, but track the per-resource throttle budget.

## Throttling interaction

Batching reduces round-trips but **does not reduce the throttle cost** — each sub-request consumes throttle units as if it were a standalone request. A 20-request batch consumes 20 throttle units in the same window.

Correct approach:
1. Batch to reduce round-trips and latency.
2. Honour `Retry-After` on any `429` — for a batch `429`, the `Retry-After` is on the batch response itself (not a sub-request).
3. Do not batch 20 write requests in parallel in a tight loop — you will hit aggregate throttle limits faster than 20 serial calls.

## What cannot go in a batch

- Requests to the `$batch` endpoint itself (no nested batching).
- Requests that require multipart MIME bodies (large file upload sessions — use `/createUploadSession` separately).
- Cross-version requests (all sub-requests in one batch must use the same Graph version prefix).

## Pitfalls

- Treating the batch as atomic — it is not. Each sub-request can fail independently; a partial batch success is common.
- Not setting request `id` values — Graph requires unique `id` per sub-request; auto-incrementing integers work.
- Using `dependsOn` on every request "just in case" — this serialises the entire batch, eliminating the performance benefit.
- Forgetting to handle `429` at the sub-request level — a 429 in one sub-request body does NOT surface as an HTTP 429 on the overall batch response (the batch itself returns 200).
