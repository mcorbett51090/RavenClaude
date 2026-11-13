/**
 * Stripe STATIC tier — the thin serverless webhook receiver.
 *
 * A literally-static site has no origin server to verify a webhook or hold
 * idempotency state — "static" describes the frontend rendering model, NOT
 * "zero server-side compute" (CLAUDE.md §2 #3). This function is the one
 * piece of server-side compute the static tier requires. It runs unmodified
 * on any platform that speaks the standard Fetch API:
 *
 *   - Vercel:    api/webhook.ts, `export const config = { runtime: "edge" }`
 *   - Netlify:   netlify/edge-functions/webhook.ts
 *   - Cloudflare Workers: src/index.ts, `export default { fetch: handler }`
 *
 * Order of operations (CLAUDE.md §2 #4, non-negotiable):
 *   1. Read the RAW body (never parsed first — parsing breaks the signature).
 *   2. Verify (constant-time, via provider.handleWebhook -> StripeWebhookVerifier).
 *   3. De-dupe by event id BEFORE any side effect.
 *   4. Only THEN process + return 2xx.
 */

import type { CommerceEvent } from "../../shared/commerce-types";
import type { IdempotencyStore } from "../../shared/idempotency-store";
import { StripeStaticProvider } from "./provider";
import { createKvIdempotencyStoreFromEnv } from "./kv-idempotency-store";

export interface WebhookHandlerDeps {
  provider: StripeStaticProvider;
  store: IdempotencyStore;
  /**
   * Your side effects for a verified, first-seen event (order fulfillment,
   * inventory, email receipt). If it throws, the claim is released and the
   * handler answers 500, so Stripe retries the delivery.
   */
  onEvent?: (event: CommerceEvent) => Promise<void>;
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

    // Atomic claim, not seen()-then-remember(): marking the event seen before
    // the side effects made a retry of a failed delivery look done, and two
    // concurrent deliveries could both pass seen() and both run them.
    if (!(await deps.store.claim(event.id))) {
      // Stripe retries deliveries; a replayed (or in-flight) event id is a no-op, not an error.
      return new Response(null, { status: 200 });
    }

    try {
      // --- Side effects go here (order fulfillment, inventory, email receipt) ---
      // Kept out of scope for this template: this is the seam where the
      // consumer's order-management code plugs in, keyed off `event.type` /
      // `event.reference`.
      if (deps.onEvent) await deps.onEvent(event);
      await deps.store.remember(event.id);
    } catch {
      // Drop the claim so Stripe's retry runs the side effects again.
      await deps.store.release(event.id);
      return new Response(null, { status: 500 });
    }

    return new Response(null, { status: 200 });
  };
}

function buildProductionDeps(): WebhookHandlerDeps {
  const secretKey = process.env.STRIPE_SECRET_KEY;
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
  if (!secretKey || !webhookSecret) {
    throw new Error("STRIPE_SECRET_KEY and STRIPE_WEBHOOK_SECRET must be set.");
  }
  return {
    provider: new StripeStaticProvider({ secretKey, webhookSecret }),
    store: createKvIdempotencyStoreFromEnv(),
  };
}

// Platform entry point. Lazily builds prod deps on first request so that
// merely importing this module (e.g. from a test) never requires env vars.
let handler: ReturnType<typeof createWebhookHandler> | undefined;

export default async function webhook(request: Request): Promise<Response> {
  handler ??= createWebhookHandler(buildProductionDeps());
  return handler(request);
}
