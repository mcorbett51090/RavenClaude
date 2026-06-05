---
scenario_id: 2026-06-05-idempotent-payments-endpoint
contributed_at: 2026-06-05
plugin: backend-engineering
product: generic
product_version: "unknown"
scope: likely-general
tags: [idempotency, payments, retries, dedup-key, race, postgres]
confidence: high
reviewed: false
---

## Problem

A `POST /charges` endpoint double-charged customers under retry. The mobile client retried on a 5xx **and** on a network timeout where the original request had actually completed server-side — so a single user tap produced two `charge` rows and two calls to the payment processor. The endpoint was "idempotent" in the sense that the team had added an `Idempotency-Key` header check, but it still double-charged about 1 in 400 requests under load.

## Constraints context

- A synchronous charge call to an external processor (Stripe-style) that is itself non-idempotent unless you pass *its* idempotency key through.
- Postgres as the system of record; the service ran 6 replicas behind a load balancer, so two retries of the same key could land on two different instances **concurrently**.
- The original "idempotency" was a read-then-write: `SELECT` the key, if absent do the work and `INSERT` the key. Classic check-then-act race.

## Attempts

- Tried: the read-then-write key check (`SELECT` then conditional `INSERT`). Failed under concurrency — two requests both `SELECT` "not found", both proceed, both charge. The window is small but non-zero, and a retrying client maximizes the odds of hitting it.
- Tried: an application-level mutex (in-process lock). Failed — the lock is per-instance, and the two retries were on different replicas. Distributed problem, local lock.
- Tried: a `SELECT ... FOR UPDATE` on a parent row. Worked but serialized far more than the single key and hurt throughput.
- Tried: a unique constraint on `idempotency_key` plus inserting the key row **first, in the same transaction as the charge**, and treating a unique-violation as "already processed → replay the stored response." This worked and is the resolution.

## Resolution

**Make the database enforce uniqueness; don't check-then-act in app code.** The reliable shape:

1. `CREATE UNIQUE INDEX` on `idempotency_key`. The DB, not the app, is the arbiter of "seen this key."
2. In **one** transaction: `INSERT` the idempotency row (key, request fingerprint, status=`in_progress`) → do the work → `UPDATE` the row to `completed` with the stored response body. A concurrent duplicate hits the unique violation on the `INSERT` and knows another request owns the key.
3. On a unique violation: if the existing row is `completed`, return its **stored response** verbatim (a true no-op replay). If it's still `in_progress`, return `409` (or a retry-after) — don't run the work twice and don't block.
4. **Fingerprint the request** (hash of the semantically-meaningful body fields) and store it on the key row. If the same key arrives with a *different* body, that's a client bug — return `422`, never silently serve the first response to a different request.
5. **Pass an idempotency key through to the external processor too.** The DB protects *your* state; only the processor's own idempotency key protects against a double *charge* when your call to it is the thing that gets retried mid-flight. Derive it deterministically from the inbound key so a retry reproduces it.

The mental model: the inbound `Idempotency-Key` is a *promise of safe retry* that you can only keep if every layer it touches (your DB write, your external call) is itself deduplicated. A unique index is the cheapest correct primitive; a `SELECT`-first check is the most common wrong one.

**Action for the next engineer:** if an "idempotent" endpoint still duplicates, the first thing to check is whether the dedup is a check-then-act (`SELECT` then `INSERT`) rather than an insert-and-catch-unique-violation. The race is invisible in single-threaded tests and only shows up under concurrent retries.

Cross-reference: complements [`../knowledge/backend-engineering-decision-trees.md`](../knowledge/backend-engineering-decision-trees.md) and the [`idempotency-and-outbox`](../templates/idempotency-and-outbox.md) template, and [`../best-practices/idempotency-for-retried-operations.md`](../best-practices/idempotency-for-retried-operations.md).
