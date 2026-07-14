---
name: payment-lifecycle-contract
description: "Understand and extend the thin shared contract every provider track implements — the payment-lifecycle interface plus advertised capabilities. Use when adding a provider, wiring a track to the contract, or deciding what belongs in the shared seam vs a track. The ONLY cross-provider abstraction; catalog/cart/inventory are track-specific."
---

# The Payment-Lifecycle Contract

The single cross-provider abstraction in `web-commerce`. It exists because Stripe/Square/Shopify sit at different layers — a unified "commerce" interface leaks (Vercel deleted ~145K LOC learning this). The seam is deliberately **thin**: only what all three genuinely share. It is modeled on Medusa's `AbstractPaymentProvider` + Saleor's advertised-capabilities pattern.

## What's in the contract (`templates/shared/`)

- **`PaymentProvider`** (`payment-provider.ts`) — `id`, `capabilities`, `createCheckout()`, `handleWebhook()`, and the **capability-gated** `authorize/capture/refund/cancel` (present only when the provider supports them).
- **`ProviderCapabilities`** (`capabilities.ts`) — what a track can honestly do, so callers never assume a uniform set. Shopify declares `checkout:'hosted'`, `authorizeCapture:false` and omits the gated methods.
- **`CommerceEvent`, `CheckoutHandle`, `Money`, `PaymentStatus`** (`commerce-types.ts`) — the shared value types.
- **`safeSignatureEqual`, `WebhookVerifier`** (`webhook-verify.ts`) and **`IdempotencyStore`** (`idempotency-store.ts`).

## What is NOT in the contract (by design)

Catalog, cart, inventory, and order shapes. These differ fundamentally per provider (Shopify owns the catalog; Stripe has none; Square couples it to POS). They live in each track with shared *conventions*, not shared *code*.

## The three capability profiles

| | checkout | authorizeCapture | refunds | catalogSourceOfTruth | posReconciliation |
|---|---|---|---|---|---|
| **Stripe** | both | true | true | app | false |
| **Square** | both | true | true | provider | true |
| **Shopify** | hosted | false | false | provider | false |

## Adding a new provider (the extension recipe)

1. Implement `PaymentProvider` with an honest `capabilities` object.
2. Implement `createCheckout` returning a `CheckoutHandle` (`hosted` url or `embedded` clientSecret).
3. Implement `handleWebhook` — verify constant-time BEFORE parse, normalize to `CommerceEvent` (see [`webhook-hardening`](../webhook-hardening/SKILL.md)).
4. Add the capability-gated methods ONLY if the provider truly supports them; otherwise omit and let `assertCapability` guard callers.
5. Keep catalog/cart/inventory in the new track, not in `shared/`.

## Anti-pattern

Widening the shared contract to hold catalog/cart/checkout "so all providers share it." That is the exact regression the three-track design exists to prevent.
