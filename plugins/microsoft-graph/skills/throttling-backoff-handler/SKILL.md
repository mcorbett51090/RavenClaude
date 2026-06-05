---
name: throttling-backoff-handler
description: "Playbook for designing a correct Graph API throttling (HTTP 429) response handler: reading Retry-After, exponential backoff with jitter, per-resource throttle budgets, and the SDK built-in retry middleware that makes hand-rolling unnecessary for most cases. Owned by graph-api-engineer."
---

# Throttling Backoff Handler

## When to invoke

- A Graph integration is receiving `429 Too Many Requests` responses.
- Designing a new high-volume Graph integration and want to build throttle-handling in from the start.
- Evaluating whether to use SDK retry middleware or hand-roll backoff.
- A batch request returns 429 on some sub-requests.

## The Graph throttling contract

Graph throttles per application, per tenant, per resource type, per time window (`[verify-at-build]` — limits change; see [Microsoft Graph throttling guidance](https://learn.microsoft.com/en-us/graph/throttling)). When throttled:

- HTTP status: `429 Too Many Requests`
- Header: `Retry-After: <seconds>` (always present; always honour it)
- You MUST wait at least `Retry-After` seconds before retrying — not "a few seconds."

**Do not retry immediately.** An immediate retry on a 429 consumes another throttle unit and restarts the window. This is the single most common cause of a 429 cascade.

## Step 1 — Use the SDK's built-in retry handler

Before hand-rolling backoff, check whether the SDK handles it:

| SDK | Built-in retry middleware |
|---|---|
| Microsoft Graph Python SDK (`msgraph-sdk`) | Yes — `RetryHandler` is included by default in `GraphServiceClient` |
| Microsoft Graph JS/TS SDK (`@microsoft/microsoft-graph-client`) | Yes — `RetryHandlerOptions` middleware |
| Microsoft Graph .NET SDK | Yes — `RetryHandler` in `GraphClientFactory.CreateDefaultHttpHandlers()` |

If you are using the official SDK, enable the retry handler and configure its options:

```python
from msgraph import GraphServiceClient
from msgraph.core import GraphClientFactory
from kiota_http.middleware import RetryHandler, RetryHandlerOption

retry_options = RetryHandlerOption(max_retries=5, retry_time_limit=180)
# The SDK's default client already includes RetryHandler — verify version-specific docs
client = GraphServiceClient(credential, ["https://graph.microsoft.com/.default"])
```

If the SDK does not provide a retry handler, or you are calling the REST API directly, implement the pattern below.

## Step 2 — Correct exponential backoff with jitter

```python
import time, random, httpx

def graph_get_with_retry(url: str, headers: dict, max_retries: int = 5) -> dict:
    attempt = 0
    while attempt <= max_retries:
        resp = httpx.get(url, headers=headers)

        if resp.status_code == 200:
            return resp.json()

        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 30))
            # Exponential backoff: max(Retry-After, 2^attempt) + jitter
            wait = max(retry_after, (2 ** attempt)) + random.uniform(0, 1)
            print(f"Throttled. Waiting {wait:.1f}s (attempt {attempt+1}/{max_retries})")
            time.sleep(wait)
            attempt += 1
            continue

        if resp.status_code in (500, 502, 503, 504):
            # Transient server errors — retry with backoff
            wait = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait)
            attempt += 1
            continue

        # Non-retriable error
        resp.raise_for_status()

    raise RuntimeError(f"Max retries exceeded for {url}")
```

Key points:
- **Always honour `Retry-After` as the floor** — don't backoff less than what Graph specified.
- **Add jitter** (random offset) to prevent thundering-herd if multiple workers are throttled simultaneously.
- **Cap retries** — infinite retry loops can hold threads indefinitely and mask bugs.
- **Log the wait** — silent retries hide throttling from monitoring.

## Step 3 — Per-resource throttle budgets

Different Graph resources have different throttle budgets (all `[verify-at-build]`):

| Resource | Approximate limit | Notes |
|---|---|---|
| Users, Groups (directory) | 12 000 req / 10 min per app per tenant | Higher for read-only |
| Mail, Calendar (Exchange Online) | 10 000 req / 10 min per app | Per-mailbox sublimits apply |
| Files / SharePoint | 1 200 req / min per app | Per-site sublimits |
| Teams | 15 req / sec per app | Real-time messaging is especially tight |

Do not treat all 429s the same — a Teams throttle and a directory throttle have different windows. Log the resource path alongside the 429 to identify which budget is exhausted.

## Step 4 — Proactive throttle avoidance

| Technique | Effect |
|---|---|
| `$batch` 20 requests per round-trip | Reduces round-trips; **does not** reduce throttle-unit consumption |
| `$select` explicit fields | Lighter responses; slightly lower service cost per request |
| Delta queries for "what changed" | Replaces N per-item polls with one differential query |
| Stagger workers with `asyncio.sleep(0.1)` between calls | Spreads load across the throttle window |
| Off-peak batch jobs | Avoid the 9 AM–12 PM usage spike when other apps share the tenant budget |

## Batch-level vs sub-request 429

When a `$batch` call has sub-requests that are throttled:

- The overall batch response is HTTP **200** (the batch call itself succeeded).
- Individual throttled sub-requests have status `429` in the `responses` array.
- Extract the `Retry-After` from the sub-request's `headers` object (not the top-level HTTP headers).
- Re-issue only the throttled sub-requests after the delay — do not re-send the whole batch.

## Pitfalls

- Retrying on 429 immediately — the most common mistake; always sleep `Retry-After` seconds minimum.
- Treating `Retry-After` as advisory — it is a contract; Graph's throttling window does not reset until the specified time.
- Using a fixed sleep (e.g., `time.sleep(1)`) instead of reading `Retry-After` — under-waits on long throttle windows, over-waits when `Retry-After` is small.
- Not logging 429s — silent retries hide a growing throttle problem until it becomes a production incident.
- Using `max_retries=0` to "fail fast" in a batch pipeline — one throttled call aborts the entire job; a few retries with correct backoff are almost always correct.
