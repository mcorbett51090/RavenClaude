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
 */

import { randomUUID } from "node:crypto";
import type { CreateCheckoutInput } from "../../shared/payment-provider";
import { StripeFrameworkProvider } from "./provider";

interface CheckoutRequestBody {
  lineItems: CreateCheckoutInput["lineItems"];
  returnUrl?: string;
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
  let body: CheckoutRequestBody;
  try {
    body = (await request.json()) as CheckoutRequestBody;
  } catch {
    return Response.json({ error: "Invalid JSON body." }, { status: 400 });
  }

  if (!Array.isArray(body.lineItems) || body.lineItems.length === 0) {
    return Response.json(
      { error: "lineItems is required and must be non-empty." },
      { status: 400 },
    );
  }

  try {
    const provider = buildProvider();
    // Generated server-side per request — never trust a client-supplied
    // idempotency key from an unauthenticated checkout endpoint, which would
    // let a caller force key collisions across unrelated carts.
    const handle = await provider.createCheckout({
      lineItems: body.lineItems,
      returnUrl: body.returnUrl,
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
