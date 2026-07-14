/**
 * Shared value types for the web-commerce payment-lifecycle contract.
 *
 * These are the ONLY types shared across provider tracks. Catalog, cart,
 * inventory, and order shapes are deliberately track-specific (CLAUDE.md
 * §2 #1) — forcing them into a shared type is the leaky-adapter trap.
 */

/** An amount in the smallest currency unit (e.g. cents) plus an ISO-4217 code. */
export interface Money {
  /** Integer minor units — 500 = $5.00. Never a float (rounding bugs, card declines). */
  amount: number;
  /** ISO-4217, uppercase — "USD". */
  currency: string;
}

/**
 * How the buyer will pay, returned by PaymentProvider.createCheckout().
 * A hosted handle is a redirect URL; an embedded handle carries the client
 * secret + publishable key the frontend SDK needs. Card data never rides here.
 */
export type CheckoutHandle =
  | { mode: "hosted"; url: string }
  | { mode: "embedded"; clientSecret: string; publishableKey: string };

export type PaymentStatus =
  "requires_payment" | "authorized" | "captured" | "refunded" | "canceled" | "failed";

export type CommerceEventType =
  | "payment.succeeded"
  | "payment.failed"
  | "payment.refunded"
  | "checkout.completed"
  | "inventory.updated"
  | "catalog.updated"
  | "unknown";

/**
 * A provider-agnostic event, normalized from a VERIFIED provider webhook.
 * Its `id` is the idempotency key used to de-duplicate retried deliveries.
 */
export interface CommerceEvent {
  /** Provider event id — the de-duplication key (Stripe event.id, Square event_id). */
  id: string;
  type: CommerceEventType;
  provider: "stripe" | "square" | "shopify";
  /** Minor-unit amount, where the event carries one. */
  amount?: Money;
  /** Provider payment/order reference, where the event carries one. */
  reference?: string;
  /** The verified raw payload, for track-specific handling. */
  raw: unknown;
}
