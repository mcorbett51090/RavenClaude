---
scenario_id: 2026-06-05-idempotency-key-double-charge
contributed_at: 2026-06-05
plugin: fintech-payments-engineering
product: stripe
product_version: "unknown"
scope: likely-general
tags: [idempotency, double-charge, retries, dedup-key, psp-key, race]
confidence: high
reviewed: false
---

## Problem

A checkout flow charged some customers twice for one order. The mobile client retried a `POST /checkout` on a network timeout, but on the server the original request had already created a PaymentIntent and confirmed it — so the retry created and confirmed a **second** PaymentIntent against the same card. The team had set their own `Idempotency-Key` table to dedupe the inbound request, but they were **not** passing an idempotency key through to the PSP, and their own dedupe was a `SELECT`-then-`INSERT` check that raced under concurrent retries. Net effect: roughly 1 in ~300 checkouts under load produced two real charges, two support tickets, and a manual refund.

## Constraints context

- PSP is Stripe-style: a `POST` to create a PaymentIntent is **only** idempotent if you send Stripe's `Idempotency-Key` header; without it, two creates = two intents = two charges `[verify-at-use — confirm your PSP's idempotency-key semantics and retention window]`.
- The service ran multiple replicas behind a load balancer, so two retries of the same logical request could land on two instances concurrently — a check-then-act race window that single-threaded tests never hit.
- Money had to move at most once; a refund is a poor substitute (it costs a support touch, a customer-trust hit, and sometimes a dispute).

## Attempts

- Tried: the inbound `SELECT idempotency_key … if absent INSERT and proceed` guard. Failed under concurrency — two retries both read "not found," both proceeded, both charged. Classic check-then-act.
- Tried: an in-process lock around the charge. Failed — the lock is per-replica; the two retries were on different replicas. Local lock, distributed problem.
- Tried (the move that worked): a **unique index** on the inbound idempotency key, `INSERT`-first in the same transaction as the charge intent (status `in_progress` → `completed` with the stored response), treat a unique-violation as "another request owns this key → replay the stored response or return `409` if still in flight," **and** derive the **PSP idempotency key deterministically from the inbound key** so a retried call to Stripe reproduces the same key and the PSP dedupes its own create.

## Resolution

**Idempotency only holds if every layer the request touches is deduplicated — your DB write AND your outbound PSP call.** The reliable shape:

1. **DB is the arbiter, not app code.** `CREATE UNIQUE INDEX` on the inbound idempotency key; `INSERT` it first, catch the unique violation — never `SELECT`-then-`INSERT`.
2. **Pass a PSP idempotency key on every money op** (create/confirm intent, refund, payout), derived deterministically from the inbound key so a mid-flight retry reproduces it. The PSP's own idempotency layer is what protects against a double *charge* when *your call to it* is the thing that gets retried.
3. **Fingerprint the request body** on the key row; a same-key/different-body arrival is a client bug → `422`, never silently serve the first response to a different request.
4. **Drive the final charge state from a verified webhook**, not the synchronous create/confirm response — the sync call can time out *after* the charge succeeded (exactly the failure here). See the charge-flow tree in `../knowledge/fintech-payments-engineering-decision-trees.md`.

**Action for the next engineer:** if an "idempotent" charge still double-bills, check two things in order — (a) is the inbound dedupe a check-then-act (`SELECT` then `INSERT`) instead of insert-and-catch-unique-violation, and (b) are you actually passing an idempotency key **through to the PSP**, or only deduping your own table? The second is the one teams miss, because their local dedupe looks correct in isolation.

Cross-reference: canonical guidance is `../best-practices/every-money-operation-is-idempotent.md` and the Charge-flow-correctness tree in `../knowledge/fintech-payments-engineering-decision-trees.md`; the helper `../scripts/recon_diff.py` is unrelated, but `../templates/charge-state-machine.md` and `../templates/webhook-handler.md` show the verified-webhook half.
