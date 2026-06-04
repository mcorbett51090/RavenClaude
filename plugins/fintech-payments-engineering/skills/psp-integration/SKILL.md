---
name: psp-integration
description: "Integrate a PSP correctly: idempotency key on every money operation (charge/refund/payout), verify webhook signatures and handle them idempotently + out-of-order, model the charge state machine explicitly, and handle 3DS/SCA and hard-vs-soft declines."
---

# PSP Integration

## Idempotency everywhere
**Idempotency key** on create-charge, refund, payout. A retry without it **double-bills** — the cardinal sin.

## Webhooks
**Verify the signature** (public, untrusted endpoint). Handle **idempotently** (dedupe by event id) and **out-of-order** (at-least-once). Drive the state machine from verified webhooks.

## State machine
Model requires_action -> processing -> succeeded/failed + refunds/disputes explicitly. Don't infer state from scattered flags.

## SCA + declines
Handle **3DS/SCA** (`requires_action` is normal). Hard declines: don't retry; soft: backoff + dunning.
