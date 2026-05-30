# Honor throttling as a contract — wait Retry-After, then back off with jitter

**Status:** Absolute rule — ignoring `Retry-After` or hammering after a `429` makes throttling worse, not better.

**Domain:** Web API / resilience

**Applies to:** `microsoft-graph`

---

## Why this exists

When a tenant or app exceeds a Graph service limit, Graph returns `429 Too Many Requests` (and sometimes `503`) with a `Retry-After` header telling you exactly how many seconds to wait. Microsoft Learn is explicit that honoring `Retry-After` is the **fastest** way to recover, because Graph keeps metering your resource usage while you're throttled — every premature retry accrues against the limit and *extends* the penalty. Aggressive retry loops are therefore self-defeating: they fail, still count, and push recovery further out.

## How to apply

Detect `429`, read `Retry-After`, sleep that long, retry. If no `Retry-After` is present, fall back to exponential backoff **with jitter** (jitter prevents a thundering-herd retry storm).

```text
on 429 (or 503):
  if response has Retry-After:  wait(Retry-After seconds)
  else:                         wait(min(base * 2^attempt, cap) + random_jitter)
  retry the SAME request; repeat until success or max attempts
```

```python
# python (raw httpx illustration — prefer the SDK's built-in handler in real code)
import httpx, time, random
def get_with_retry(client, url, headers, attempt=0, max_attempts=5):
    r = client.get(url, headers=headers)
    if r.status_code in (429, 503) and attempt < max_attempts:
        ra = r.headers.get("Retry-After")
        delay = int(ra) if ra else min(2 ** attempt, 60) + random.uniform(0, 1)
        time.sleep(delay)
        return get_with_retry(client, url, headers, attempt + 1, max_attempts)
    r.raise_for_status()
    return r
```

**Do:**
- Honor the `Retry-After` value verbatim — it's the service's computed recovery time.
- Add jitter to any backoff fallback so concurrent clients don't re-collide.
- Reduce the *cause*: fewer operations per request, lower call frequency, and `$batch` to cut round-trips.

**Don't:**
- Retry immediately on `429` — the failed call still accrues against your limit.
- Treat `429` as a fatal error to surface to the user; it's a "wait" instruction.
- Assume every resource returns `Retry-After` — some (e.g. certain reporting/identity-protection endpoints) do **not**, so your backoff fallback must exist.

## Edge cases / when the rule does NOT apply

**Batched requests are the trap:** a `$batch` returns `200` even when individual sub-requests inside it are `429`, and the SDK auto-retry does **not** re-run batched sub-requests automatically — you must inspect each sub-response's status and `Retry-After` and retry the failed ones yourself (often as a new batch after the longest `Retry-After`). Some service-specific limits also publish IETF `RateLimit-*` headers (preview) giving early warning before the throttle — use them to slow down proactively. A persistent `429` despite correct backoff means the design is over-asking (poll → switch to delta; serial → batch).

## See also

- [`./api-batch-to-cut-round-trips.md`](./api-batch-to-cut-round-trips.md) — and the per-sub-request 429 caveat
- [`./api-delta-for-what-changed.md`](./api-delta-for-what-changed.md) — the fix when throttling is self-inflicted polling
- [`./api-use-the-sdk-not-raw-http-for-resilience.md`](./api-use-the-sdk-not-raw-http-for-resilience.md) — the SDK ships this retry handler
- [`../agents/graph-api-engineer.md`](../agents/graph-api-engineer.md) — owns throttling resilience
- [Microsoft Graph throttling guidance](https://learn.microsoft.com/graph/throttling) — authoritative

## Provenance

From the Microsoft Learn "Microsoft Graph throttling guidance" page and the "throttling and batching" + "service-specific limits" sections (retrieved 2026-05-30 via Microsoft Learn MCP), codifying team house opinion #5. The set of resources that omit `Retry-After` and the exact per-service limit numbers are volatile — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
