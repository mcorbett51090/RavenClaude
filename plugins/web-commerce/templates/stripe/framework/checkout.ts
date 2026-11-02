/**
 * Stripe FRAMEWORK tier — checkout entry: creates the PaymentIntent server-side.
 *
 * A Next.js App Router Route Handler (drop at app/api/checkout/route.ts) or
 * an Astro API endpoint (drop at src/pages/api/checkout.ts, export `POST`
 * the same way) — both speak the standard Fetch API Request/Response, so
 * this file is portable between the two with no changes.
 *
 * The secret key NEVER leaves this file. The browser receives only the
 * `clientSecret` + `publishableKey` pair returned here, which is exactly
 * what Stripe.js needs to mount the Payment Element (payment-element.tsx).
 *
 * Prices are NEVER taken from the request. The browser sends only
 * `{ items: [{ sku, quantity }] }`; every unit price is resolved here,
 * server-side, from PRICE_CATALOG below. This route is unauthenticated, so
 * a client-supplied amount would let anyone pay whatever they like. Put
 * your own auth / rate limit in front of it as your app requires.
 */

import { randomUUID } from "node:crypto";
import type { Money } from "../../shared/commerce-types";
import type { CreateCheckoutInput } from "../../shared/payment-provider";
import { StripeFrameworkProvider } from "./provider";

interface CheckoutRequestItem {
  sku: string;
  quantity: number;
}

/**
 * SEAM — replace with your real catalog (database, CMS, or Stripe Price
 * objects). Keys are your SKUs; amounts are integer minor units in ONE
 * currency (a single PaymentIntent cannot mix currencies).
 */
const PRICE_CATALOG: ReadonlyMap<string, { name: string; unitPrice: Money }> = new Map([
  [
    "estate-reserve-750ml",
    { name: "Estate Reserve — 750ml", unitPrice: { amount: 4800, currency: "USD" } },
  ],
]);

/** Largest quantity accepted for one line; raise it if your store sells in bulk. */
const MAX_QUANTITY_PER_ITEM = 100;
/** Largest number of lines accepted in one checkout. */
const MAX_LINE_ITEMS = 50;

/** The one place a unit price comes from. `undefined` means the sku is unknown. */
function lookupCatalogPrice(sku: string): { name: string; unitPrice: Money } | undefined {
  return PRICE_CATALOG.get(sku);
}

/** Validates the request shape and resolves prices server-side, or returns a 400 message. */
function resolveLineItems(body: unknown): CreateCheckoutInput["lineItems"] | string {
  const items = (body as { items?: unknown } | null)?.items;
  if (!Array.isArray(items) || items.length === 0 || items.length > MAX_LINE_ITEMS) {
    return `items is required: a non-empty array of at most ${MAX_LINE_ITEMS} { sku, quantity } entries.`;
  }
  const lineItems: CreateCheckoutInput["lineItems"] = [];
  for (const raw of items as Array<Partial<CheckoutRequestItem> | null>) {
    const sku = raw?.sku;
    const quantity = raw?.quantity;
    if (typeof sku !== "string") {
      return "Each item needs a string sku.";
    }
    if (
      typeof quantity !== "number" ||
      !Number.isInteger(quantity) ||
      quantity < 1 ||
      quantity > MAX_QUANTITY_PER_ITEM
    ) {
      return `Each item needs an integer quantity from 1 to ${MAX_QUANTITY_PER_ITEM}.`;
    }
    const entry = lookupCatalogPrice(sku);
    if (!entry) {
      return "Unknown sku.";
    }
    lineItems.push({ name: entry.name, amount: entry.unitPrice, quantity });
  }
  return lineItems;
}

function buildProvider(): StripeFrameworkProvider {
  const secretKey = process.env.STRIPE_SECRET_KEY;
  const publishableKey = process.env.STRIPE_PUBLISHABLE_KEY;
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
  if (!secretKey || !publishableKey || !webhookSecret) {
    throw new Error(
      "STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, and STRIPE_WEBHOOK_SECRET must be set.",
    );
  }
  return new StripeFrameworkProvider({ secretKey, publishableKey, webhookSecret });
}

/**
 * App Router / Astro convention: a named export matching the HTTP method.
 * Rename to `export const POST` if your framework expects a `const` rather
 * than a `function` (both are valid Next.js Route Handler shapes).
 */
export async function POST(request: Request): Promise<Response> {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: "Invalid JSON body." }, { status: 400 });
  }

  const lineItems = resolveLineItems(body);
  if (typeof lineItems === "string") {
    return Response.json({ error: lineItems }, { status: 400 });
  }
  const returnUrl = (body as { returnUrl?: unknown }).returnUrl;

  try {
    const provider = buildProvider();
    // Generated server-side per request — never trust a client-supplied
    // idempotency key from an unauthenticated checkout endpoint, which would
    // let a caller force key collisions across unrelated carts.
    const handle = await provider.createCheckout({
      lineItems,
      returnUrl: typeof returnUrl === "string" ? returnUrl : undefined,
      idempotencyKey: randomUUID(),
    });

    if (handle.mode !== "embedded") {
      throw new Error("Expected an embedded checkout handle from the framework provider.");
    }

    return Response.json({
      clientSecret: handle.clientSecret,
      publishableKey: handle.publishableKey,
    });
  } catch (err) {
    // Never leak Stripe's raw error (may echo request internals) to the client.
    console.error("Stripe checkout creation failed:", err);
    return Response.json({ error: "Could not start checkout. Please try again." }, { status: 502 });
  }
}
