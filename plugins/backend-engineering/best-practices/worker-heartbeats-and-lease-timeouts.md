# Use heartbeats and lease timeouts for long-running workers

**Status:** Absolute rule
**Domain:** Background jobs / async workers
**Applies to:** `backend-engineering`

---

## Why this exists

A worker that crashes or hangs without renewing a lease leaves its job stuck in an "in-progress" state forever — the job is never retried and the work is silently lost. Heartbeats (periodic lease renewals) combined with a lease timeout that expires if the heartbeat stops are the mechanism that makes stuck jobs visible and restartable. Without them, a fleet of workers can silently accumulate "in-progress" jobs that no one is actually processing.

## How to apply

When a worker claims a job, it takes a lease (a timeout). It must renew the lease at an interval shorter than the timeout. If the worker dies, the lease expires and another worker can pick it up.

```python
# Pseudo-code: worker lease renewal
def process_job(job_id: str):
    lease_ttl_seconds = 30
    heartbeat_interval = 10   # renew before the TTL expires

    with claim_job(job_id, ttl=lease_ttl_seconds) as lease:
        heartbeat_thread = start_heartbeat(lease, interval=heartbeat_interval)
        try:
            do_work(job_id)          # actual processing
            mark_complete(job_id)
        except Exception as e:
            mark_failed(job_id, error=e)
        finally:
            heartbeat_thread.stop()
```

**Do:**
- Set the lease timeout to 2–3× the expected job duration plus network jitter headroom.
- Make heartbeat failures observable — log a WARN and increment a metric when a heartbeat misses.
- Design the job handler to be idempotent — a lease expiry may cause the same job to be retried on another worker.
- Fence out stale workers: include a `lease_token` in the completion write; reject completions with an expired token.

**Don't:**
- Use a single non-renewable timeout (a "visibility timeout") for jobs that can take variable time.
- Let workers run indefinitely without a lease — a hanging worker blocks a slot and hides a bug.
- Forget to stop the heartbeat thread on completion; a stale heartbeat holding a dead job's lease wastes capacity.

## Edge cases / when the rule does NOT apply

Very short jobs (sub-second, batch of small units) that complete before any timeout window can use simpler at-most-once or at-least-once delivery without heartbeats. In-process background work with no external state (fire-and-forget side effects with no claimed lease) also doesn't need this pattern.

## See also

- [`../agents/backend-reliability-engineer.md`](../agents/backend-reliability-engineer.md) — owns background-job and worker design.
- [`./queues-need-backpressure-and-a-dlq.md`](./queues-need-backpressure-and-a-dlq.md) — pairs with heartbeats: expired leases requeue jobs; without a DLQ, poison jobs bounce indefinitely.

## Provenance

Standard distributed job-queue design (AWS SQS visibility timeout + heartbeat renewal pattern, Postgres advisory locks, Sidekiq unique locks). Codifies `backend-reliability-engineer`'s background-job reliability requirements.

---

_Last reviewed: 2026-06-05 by `claude`_
