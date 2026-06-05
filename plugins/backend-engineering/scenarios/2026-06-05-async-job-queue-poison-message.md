---
scenario_id: 2026-06-05-async-job-queue-poison-message
contributed_at: 2026-06-05
plugin: backend-engineering
product: rabbitmq
product_version: "unknown"
scope: likely-general
tags: [queue, dlq, idempotent-consumer, poison-message, backpressure, retry]
confidence: medium
reviewed: false
---

## Problem

A background worker pool that processed "send-invoice" jobs got wedged: one malformed job (a payload that threw on deserialization) was redelivered forever. Because the broker requeued on `nack`, the poison message went to the front of the line, the worker picked it up, threw, `nack`ed, and got it back — a tight loop. Throughput collapsed, the queue depth climbed without bound, and a downstream side effect (the invoice email) fired multiple times for the jobs that *did* succeed before the wedge, because a redelivery after a partial success re-ran the whole handler.

## Constraints context

- At-least-once delivery broker (RabbitMQ-style; the same shape applies to SQS, Kafka-consumer, Sidekiq, etc.). Redelivery is guaranteed, exactly-once is not.
- The handler did several things in sequence: charge bookkeeping → send email → mark done. No step was individually idempotent, and there was no dedup key.
- No dead-letter destination configured; a `nack` with `requeue=true` was the only failure path.

## Attempts

- Tried: catching the deserialization error and `nack` with `requeue=true`. Made it worse — that *is* the poison loop. The message is broken; requeueing it just feeds the loop.
- Tried: catching and `ack`ing the broken message (drop it). Stopped the loop but **silently lost** the job, and didn't address the duplicate-email problem on the jobs that succeeded.
- Tried: a real dead-letter queue + a bounded retry count + an idempotent handler keyed on a job id. This is the resolution — the loop stops, nothing is silently lost, and redelivery of a partially-succeeded job no longer double-sends.

## Resolution

**At-least-once delivery has two non-negotiables: a DLQ for messages that can't succeed, and an idempotent handler for messages that get redelivered.** Both, not either.

1. **Dead-letter after bounded retries.** Configure a DLQ and a max delivery count (e.g. 5). A message that fails N times routes to the DLQ instead of requeueing forever. The DLQ is an inbox for a human/alert, not a black hole — alert on DLQ depth.
2. **Distinguish poison from transient.** A *deserialization*/validation failure will never succeed on retry → dead-letter immediately (retrying is pure waste). A *transient* failure (downstream timeout) → retry with backoff up to the limit, then dead-letter. Same handler, different disposition by error class.
3. **Make the handler idempotent.** Key the side effects on a stable job/message id. "Send email" checks a `sent_emails(job_id)` row first; "charge bookkeeping" is keyed the same way. Then a redelivery after a partial success is a safe no-op for the already-done steps. Redelivery *will* happen — design for it, don't hope against it.
4. **Order the steps so the riskiest external effect is last and guarded.** Do the reversible/internal work first; do the irreversible external send last and behind its own dedup check, so a crash mid-handler doesn't strand you having sent the email but not recorded it.
5. **Bound the queue / apply backpressure** so a producer surge doesn't grow the queue until workers OOM — shed, throttle, or reject at the producer rather than failing late.

The two failure modes are mirror images: no DLQ → a poison message wedges the pool; no idempotency → a redelivered good message double-acts. Fixing one without the other just moves the bug.

**Action for the next engineer:** if a worker pool is wedged, look for a redelivery loop first (same message id reappearing) — that's a missing DLQ/retry-limit. If a job's side effect fired twice, look for a non-idempotent handler under at-least-once delivery. They co-occur because both come from treating an at-least-once queue as if it were exactly-once.

Cross-reference: complements [`../best-practices/queues-need-backpressure-and-a-dlq.md`](../best-practices/queues-need-backpressure-and-a-dlq.md), [`../best-practices/idempotency-for-retried-operations.md`](../best-practices/idempotency-for-retried-operations.md), and the [`backend-resilience`](../skills/backend-resilience/SKILL.md) skill. The broker/infra itself → the cloud plugin; the SLOs these protect → `observability-sre`.
