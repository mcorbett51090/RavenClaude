# Build rate-limit-aware retry into every connector from day one

**Status:** Absolute rule
**Domain:** ELT / connector engineering
**Applies to:** `data-platform`

---

## Why this exists

SaaS APIs enforce per-realm, per-minute rate limits that are hit in production but invisible in development (small accounts, low concurrency). QuickBooks Online caps at 10 req/s per realm-ID; HubSpot's Search API caps at 4 req/s; Salesforce Bulk 2.0 caps at 150M records/day. A connector that does not honor `Retry-After` headers and back off on 429s will loop-fail, exhaust its quota window, and leave the pipeline stuck for minutes to hours. Worse, on Fivetran's 2026 billing model, a retry-storm on a high-volume source can push rows re-examined into MAR, inflating costs unpredictably.

## How to apply

Wrap every API call in a retry decorator that:

1. Detects `HTTP 429` and `HTTP 503` responses.
2. Reads `Retry-After` (seconds or HTTP-date) from the response header if present; otherwise uses exponential back-off with jitter.
3. Lowers concurrency (reduce parallel workers) before re-queuing rather than immediately retrying at full concurrency.
4. Records the retry event in connector logs with the source name, endpoint, and wait duration.

```python
import time, random, requests

def call_with_retry(url, headers, max_retries=5):
    for attempt in range(max_retries):
        resp = requests.get(url, headers=headers)
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 2 ** attempt + random.random()))
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"Gave up after {max_retries} retries: {url}")
```

Per-source limits to hard-code as guard rails:

| Source | Limit |
|---|---|
| QuickBooks Online | 10 req/s per realm-ID |
| HubSpot Search API | 4 req/s (not the 110/10s OAuth ceiling) |
| Salesforce Bulk 2.0 | 150M records/day; 15k batches/24h |
| Shopify GraphQL | 1000 cost-units/s (leaky bucket) |
| GA4 Data API | 200k requests/day per property |

**Do:**
- Read `Retry-After` before computing a wait time — the source knows when its window resets.
- Use exponential back-off with jitter to avoid thundering-herd retries across parallel workers.
- Decrement the concurrency level on a 429 before retrying.
- Log every retry with the wait duration for post-incident diagnosis.

**Don't:**
- Retry immediately at full concurrency on a 429 — this makes the quota exhaustion worse.
- Treat a 429 as a failure; it is a pacing signal from the source.
- Full-refresh after a rate-limit failure — resume from the last cursor (Fivetran MAR risk).
- Hard-code sleep(1) universally — each source has a different window shape.

## Edge cases / when the rule does NOT apply

Internal/private APIs with no published rate limits still benefit from retry logic (transient failures), but the limit-aware back-off tuning can't be pre-configured — instrument and observe before setting guard rails. Webhook consumers (Stripe, Shopify events) are push-based and do not generate outbound API calls, so this rule is not applicable to that leg of the hybrid pipeline.

## See also

- [`../agents/etl-pipeline-engineer.md`](../agents/etl-pipeline-engineer.md) — primary agent who configures connectors and must enforce this rule on every source
- [`./connector-incremental-with-backfill.md`](./connector-incremental-with-backfill.md) — the cursor strategy that makes a rate-limit-safe resume possible

## Provenance

Codifies the QBO 10 req/s per realm-ID and HubSpot 4/s Search API limits documented in `CLAUDE.md` §3 anti-patterns, `knowledge/quickbooks-online-integration.md`, and `knowledge/hubspot-integration.md`; the Salesforce and Shopify limits are from `knowledge/salesforce-integration.md` and `knowledge/shopify-integration.md`. Retry-After handling is standard HTTP practice (RFC 6585 §4).

---

_Last reviewed: 2026-06-05 by `claude`_
