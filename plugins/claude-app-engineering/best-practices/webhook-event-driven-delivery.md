# Drive async Claude results through events, not polling

**Status:** Pattern
**Domain:** Reliability / async architecture
**Applies to:** `claude-app-engineering`

---

## Why this exists

Batch API and long-running agentic tasks produce results asynchronously. Teams
that poll a job-status endpoint in a tight loop (or hold an HTTP connection open
for minutes) waste compute, hit rate limits, and build fragile clients. Event-
driven delivery (webhook callback + idempotent handler) decouples the producer
from the consumer, survives client restarts, and scales to thousands of
concurrent jobs without a thundering-herd on a single endpoint.

## How to apply

1. Submit a Batch API job or a long async task and record the job id.
2. Register a webhook URL for completion events (or use a queue / pub-sub topic
   if you control the delivery infrastructure).
3. Implement an idempotent event handler: deduplicate by job id, process exactly
   once, then acknowledge.

```python
from flask import Flask, request, jsonify
import hmac, hashlib, os

app = Flask(__name__)
processed_jobs: set[str] = set()  # replace with a durable store in production

@app.post("/claude-batch-callback")
def handle_batch_result():
    # 1. Verify the signature (treat as untrusted input — house opinion #7)
    sig = request.headers.get("X-Anthropic-Signature", "")
    expected = hmac.new(
        os.environ["ANTHROPIC_WEBHOOK_SECRET"].encode(),
        request.data, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return "Unauthorized", 401

    event = request.json
    job_id = event["batch_id"]

    # 2. Deduplicate — at-least-once delivery
    if job_id in processed_jobs:
        return jsonify({"status": "duplicate"}), 200
    processed_jobs.add(job_id)

    # 3. Process
    process_batch_results(event["results"])
    return jsonify({"status": "ok"}), 200
```

**Do:**
- Verify the webhook signature before processing (same discipline as payment
  webhooks — it's an untrusted public endpoint).
- Deduplicate by job id; Anthropic may deliver the same event more than once.
- Acknowledge with a `200` quickly; do heavy processing in a background job.

**Don't:**
- Poll a status endpoint more than once per 30 seconds for long-running jobs —
  it adds latency, wastes quota, and is against the grain of the Batch API.
- Hold an HTTP connection open waiting for a result longer than your load
  balancer's timeout; use async delivery instead.
- Process webhook payloads without signature verification.

## Edge cases / when the rule does NOT apply

- Interactive / streaming real-time tasks where the user is waiting for the
  response: use streaming SSE, not webhooks.
- Very short async tasks (< 2 seconds): a single await is fine; the webhook
  overhead isn't worth it.

## See also

- [`../agents/claude-app-ops-engineer.md`](../agents/claude-app-ops-engineer.md) — owns reliability + async patterns
- [`./untrusted-content-stays-untrusted.md`](./untrusted-content-stays-untrusted.md) — webhook payloads are untrusted input
- [`./tool-idempotency-for-effects.md`](./tool-idempotency-for-effects.md) — idempotency discipline applies to event handlers too

## Provenance

Codifies the async-delivery pattern from
`knowledge/claude-app-finops-reliability-and-security.md` (retrieved 2026-05-28)
and standard event-driven architecture practice applied to Batch API jobs.

---

_Last reviewed: 2026-06-05 by `claude`_
