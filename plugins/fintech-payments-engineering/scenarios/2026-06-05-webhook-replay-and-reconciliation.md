---
scenario_id: 2026-06-05-webhook-replay-and-reconciliation
contributed_at: 2026-06-05
plugin: fintech-payments-engineering
product: stripe
product_version: "unknown"
scope: likely-general
tags: [webhook, signature, replay, dedup, reconciliation, out-of-order]
confidence: high
reviewed: false
---

## Problem

A nightly reconciliation showed the internal ledger crediting some accounts **twice** and, separately, a handful of paid invoices stuck in `pending`. Root cause was two distinct webhook bugs feeding the same symptom. First, the handler trusted the payload without verifying the provider signature and **without deduping by event id**, so the PSP's at-least-once redelivery of a `payment_intent.succeeded` re-ran the ledger credit. Second, events arrived **out of order** — a `payment_intent.succeeded` sometimes landed before the `payment_intent.created` the handler expected, and the handler dropped the "early" success, leaving the invoice never marked paid. The reconciliation diff is what surfaced both; nothing failed loudly at handle time.

## Constraints context

- Webhooks hit a **public** endpoint — anyone who knows the URL can POST to it, so the signature is the only thing separating a real money instruction from a forged one.
- Delivery is **at-least-once and not ordered**: the PSP retries on any non-2xx (and on its own timeouts), and there is no guarantee `created` precedes `succeeded` at your endpoint `[verify-at-use — confirm your PSP's delivery + ordering guarantees and signature scheme]`.
- The ledger was append-only and reconciled to the PSP nightly, so a double-credit was caught within a day — but a day of wrong balances is still a real defect.

## Attempts

- Tried: handling the webhook idempotently in app code by checking "did I already process this event id?" with a `SELECT` then `INSERT`. Same check-then-act race as the charge path — two redeliveries arriving close together both passed the check. Failed.
- Tried: relying on the synchronous API response to set state and treating webhooks as "nice to have." Failed the out-of-order case — the sync path didn't cover async state transitions (disputes, delayed-settlement methods) that *only* arrive by webhook.
- Tried (the move that worked): (1) **verify the signature first** and reject any payload that fails — before any parsing or DB work; (2) **dedupe on a unique index over the provider event id** (insert-and-catch, not check-then-act); (3) make every handler a **state-machine transition that is safe to apply in any order** — a `succeeded` event sets terminal-paid regardless of whether `created` was seen, and a late/duplicate `created` for an already-paid intent is a no-op.

## Resolution

**Treat the webhook endpoint as an untrusted, at-least-once, out-of-order channel and design for all three properties at once:**

1. **Verify the signature before trusting anything** — it is a public endpoint; an unverified webhook is a spoofable instruction to mark an invoice paid.
2. **Dedupe by event id with a unique index** (insert-and-catch-unique-violation), not a `SELECT`-first check.
3. **Make handlers order-independent state transitions.** Drive the charge/invoice as a state machine where each event moves it toward a terminal state and applying the same or an out-of-order event again is a no-op. Don't assume `created` precedes `succeeded`.
4. **Reconcile continuously** — the nightly ledger-vs-PSP diff is what caught both bugs; treat any non-zero discrepancy as a defect with an owner. See the Reconciliation-discrepancy-triage tree in `../knowledge/fintech-payments-engineering-decision-trees.md`.

**Action for the next engineer:** when reconciliation shows double-credits or stuck-pending, check the webhook handler for the trio — signature verified *first*, dedupe via unique index (not check-then-act), and handlers that don't assume event order. The `recon_diff.py` helper under `../scripts/` mechanizes the ledger-vs-PSP diff that surfaces these.

Cross-reference: canonical guidance is `../best-practices/verify-and-dedupe-webhooks.md` and `../best-practices/reconcile-continuously.md`; the charge-flow + reconciliation trees in `../knowledge/fintech-payments-engineering-decision-trees.md`; templates `../templates/webhook-handler.md` and `../templates/charge-state-machine.md`.
