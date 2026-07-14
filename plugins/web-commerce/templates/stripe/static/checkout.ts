/**
 * Stripe STATIC tier — checkout entry: Payment Link generation.
 *
 * A static site cannot call the Stripe API per-request (there is no
 * request-time server), so the checkout entry point here is a build-/setup-
 * time SCRIPT: run it once whenever your products or prices change, then
 * paste the resulting URL into your site as a plain, accessible link —
 * no client-side Stripe code, no card field, ever, on your own origin.
 *
 *   <a href="https://buy.stripe.com/xxxxx" class="buy-button">
 *     Buy the Estate Reserve — $48.00
 *   </a>
 *
 * A real semantic `<a>` element is already keyboard-and-screen-reader
 * accessible; do not replace it with a non-focusable `<div onClick>`
 * (CLAUDE.md §4 dimension 7).
 *
 * Usage:
 *   STRIPE_SECRET_KEY=sk_test_xxx npx tsx checkout.ts
 */

import { randomUUID } from "node:crypto";
import type { CreateCheckoutInput } from "../../shared/payment-provider";
import type { CheckoutHandle } from "../../shared/commerce-types";
import { StripeStaticProvider } from "./provider";

export async function generatePaymentLink(input: CreateCheckoutInput): Promise<CheckoutHandle> {
  const secretKey = process.env.STRIPE_SECRET_KEY;
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET ?? "whsec_placeholder_not_used_here";
  if (!secretKey) {
    throw new Error("STRIPE_SECRET_KEY must be set to generate a Payment Link.");
  }
  const provider = new StripeStaticProvider({ secretKey, webhookSecret });
  return provider.createCheckout(input);
}

// --- Example config: replace with your real catalog before running. ---
const EXAMPLE_LINE_ITEMS: CreateCheckoutInput["lineItems"] = [
  { name: "Estate Reserve — 750ml", amount: { amount: 4800, currency: "USD" }, quantity: 1 },
];

async function main(): Promise<void> {
  const handle = await generatePaymentLink({
    lineItems: EXAMPLE_LINE_ITEMS,
    returnUrl: process.env.STRIPE_RETURN_URL,
    idempotencyKey: randomUUID(),
  });
  if (handle.mode !== "hosted") {
    throw new Error("Expected a hosted Payment Link handle.");
  }
  // eslint-disable-next-line no-console -- this IS the tool's output.
  console.log(handle.url);
}

// Run only when invoked directly (`npx tsx checkout.ts`), not on import —
// tests and other modules import generatePaymentLink() without side effects.
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((err) => {
    console.error(err);
    process.exitCode = 1;
  });
}
