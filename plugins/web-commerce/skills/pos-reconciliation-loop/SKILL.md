---
name: pos-reconciliation-loop
description: "Reconcile online inventory/catalog with an in-store POS (Square), keeping the POS as the source of truth. Use when a storefront's online store must mirror in-store stock. One-way sync driven by catalog/inventory webhooks, de-duped by event id — never bidirectional. Square-specific; Shopify inverts and Stripe has no catalog."
---

# POS Reconciliation Loop

For storefronts whose **in-store POS is the source of truth** and whose website must mirror it. This is the **Square** track's distinctive capability (`posReconciliation: true`). Shopify inverts the model (Shopify is the truth); Stripe has no catalog to reconcile.

## The core rule: one-way, POS-as-truth

Square **explicitly warns that bidirectional sync is unsafe** (concurrency, merge, duplicate, and delete hazards). So:

- Pick **one** master — the POS (Square) — and sync **one way** to the online surface.
- Never push online edits back into the POS ledger as an authoritative write.

## The loop

1. **Subscribe** to `catalog.version.updated` and inventory webhooks.
2. **Verify** the webhook (constant-time HMAC — see [`webhook-hardening`](../webhook-hardening/SKILL.md)).
3. **De-dupe** by `event_id` (retries + out-of-order delivery are expected) BEFORE applying any change.
4. **Pull only what changed** — `SearchCatalogObjects` with `begin_time`, or the changed objects the event names — not a full re-sync.
5. **Apply** to the online catalog/inventory projection, storing cross-reference IDs as custom attributes.
6. Surface sold-out via the inventory count (e.g. `location_override.sold_out`).

## The correctness tests (the track must pass these)

- **A duplicate inventory webhook does NOT double-decrement stock** (idempotency by `event_id`).
- **Convergence holds under out-of-order delivery** — applying events in a shuffled order lands on the same final stock as in-order.

## Anti-patterns

- Bidirectional sync (Square warns against it).
- Full catalog re-sync on every webhook (use `begin_time` / changed-object deltas).
- Treating the website as a second source of truth (it is a projection of the POS).
