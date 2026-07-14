/**
 * Stripe FRAMEWORK tier — the webhook Route Handler.
 *
 * Drop at app/api/stripe/webhook/route.ts (Next.js App Router) or
 * src/pages/api/stripe/webhook.ts (Astro) — export `POST` the same way
 * either framework expects; both speak the standard Fetch API
 * Request/Response, so this file needs no adaptation between them.
 *
 * IMPORTANT — Next.js only: the App Router does NOT parse the body for you
 * on this route by default, but if your project has body parsing middleware
 * enabled globally, exclude this route from it. Signature verification
 * needs the untouched raw bytes; `await request.text()` below must return
 * exactly what Stripe sent, byte for byte.
 *
 * Order of operations (CLAUDE.md §2 #4, non-negotiable):
 *   1. Read the RAW body (never parsed first — parsing breaks the signature).
 *   2. Verify (constant-time, via provider.handleWebhook -> StripeWebhookVerifier).
 *   3. De-dupe by event id BEFORE any side effect.
 *   4. Only THEN process + return 2xx.
 */

import type { IdempotencyStore } from "../../shared/idempotency-store";
import { StripeFrameworkProvider } from "./provider";
import { createKvIdempotencyStoreFromEnv } from "./kv-idempotency-store";

export interface WebhookHandlerDeps {
  provider: StripeFrameworkProvider;
  store: IdempotencyStore;
}

/**
 * Factory, not a bare handler — so tests can inject an in-memory store and a
 * test-keyed provider instead of hitting real KV / requiring live Stripe env
 * vars. Production wiring is the default export below.
 */
export function createWebhookHandler(deps: WebhookHandlerDeps) {
  return async function handleStripeWebhook(request: Request): Promise<Response> {
    const rawBody = await request.text();
    const headers: Record<string, string | undefined> = {
      "stripe-signature": request.headers.get("stripe-signature") ?? undefined,
    };

    let event;
    try {
      event = await deps.provider.handleWebhook({ rawBody, headers });
    } catch {
      // Signature invalid / malformed payload — reject, do not process.
      return new Response("Webhook signature verification failed.", { status: 400 });
    }

    if (await deps.store.seen(event.id)) {
      // Stripe retries deliveries; a replayed event id is a no-op, not an error.
      return new Response(null, { status: 200 });
    }
    await deps.store.remember(event.id);

    // --- Side effects go here (order fulfillment, inventory, email receipt) ---
    // Kept out of scope for this template: this is the seam where the
    // consumer's order-management code (often a direct DB call, since a
    // framework app usually already has one) plugs in, keyed off
    // `event.type` / `event.reference`.

    return new Response(null, { status: 200 });
  };
}

function buildProductionDeps(): WebhookHandlerDeps {
  const secretKey = process.env.STRIPE_SECRET_KEY;
  const publishableKey = process.env.STRIPE_PUBLISHABLE_KEY;
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
  if (!secretKey || !publishableKey || !webhookSecret) {
    throw new Error(
      "STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, and STRIPE_WEBHOOK_SECRET must be set.",
    );
  }
  return {
    provider: new StripeFrameworkProvider({ secretKey, publishableKey, webhookSecret }),
    store: createKvIdempotencyStoreFromEnv(),
  };
}

// Route-handler entry point. Lazily builds prod deps on first request so
// merely importing this module (e.g. from a test) never requires env vars.
let handler: ReturnType<typeof createWebhookHandler> | undefined;

export async function POST(request: Request): Promise<Response> {
  handler ??= createWebhookHandler(buildProductionDeps());
  return handler(request);
}
