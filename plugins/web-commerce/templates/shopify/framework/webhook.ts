/**
 * Shopify webhook receiver — framework tier (Next.js Route Handler / Astro
 * API endpoint). Both frameworks' server routes speak the standard Fetch API
 * `Request`/`Response`, so this handler drops in unmodified:
 *
 *   // Next.js: app/api/webhooks/shopify/route.ts
 *   export const POST = createShopifyWebhookHandler({ verifier, store });
 *
 *   // Astro: src/pages/api/webhooks/shopify.ts
 *   export const POST: APIRoute = ({ request }) =>
 *     createShopifyWebhookHandler({ verifier, store })(request);
 *
 * The IdempotencyStore MUST be backed by an external store (Upstash / Vercel
 * KV / your DB) — a serverless function instance is not guaranteed to
 * survive between invocations, so process memory would silently lose
 * dedup state and re-run side effects on a Shopify retry.
 */
import { createHmac } from "node:crypto";
import { safeSignatureEqual } from "../../shared/webhook-verify";
import type { WebhookVerifier } from "../../shared/webhook-verify";
import type { IdempotencyStore } from "../../shared/idempotency-store";
import type { CommerceEvent, CommerceEventType } from "../../shared/commerce-types";

/**
 * Verifies Shopify's `X-Shopify-Hmac-Sha256` header: base64 HMAC-SHA256 over
 * the RAW (unparsed) request body, keyed with the webhook signing secret
 * (Shopify admin > Settings > Notifications > Webhooks) — NOT the Storefront
 * API token used by cart.ts. Constant-time compare via `safeSignatureEqual`
 * (CLAUDE.md §2 #4). Verify BEFORE parsing — a framework's body-parsing
 * middleware that runs ahead of this handler can reformat whitespace and
 * silently break the signature, so read the raw text yourself.
 */
export class ShopifyWebhookVerifier implements WebhookVerifier {
  constructor(private readonly webhookSecret: string) {}

  verify(rawBody: string | Buffer, headers: Record<string, string | undefined>): boolean {
    const signature = headers["x-shopify-hmac-sha256"] ?? headers["X-Shopify-Hmac-Sha256"];
    if (!signature) return false;
    const digest = createHmac("sha256", this.webhookSecret).update(rawBody).digest("base64");
    return safeSignatureEqual(digest, signature);
  }
}

/**
 * Shopify webhook topic → normalized CommerceEvent type. Not exhaustive —
 * add topics your integration subscribes to. Any unmapped topic normalizes
 * to "unknown" rather than guessing.
 */
const TOPIC_MAP: Record<string, CommerceEventType> = {
  "orders/create": "checkout.completed",
  "orders/paid": "payment.succeeded",
  "refunds/create": "payment.refunded",
  "inventory_levels/update": "inventory.updated",
  "products/update": "catalog.updated",
};

interface ShopifyWebhookPayload {
  id?: number | string;
  total_price?: string;
  currency?: string;
  [key: string]: unknown;
}

/**
 * Normalize an ALREADY-VERIFIED Shopify webhook body into the shared
 * CommerceEvent shape. The dedup key is the `X-Shopify-Webhook-Id` header —
 * a unique id per delivery attempt sent on every Shopify webhook (confirmed
 * against https://shopify.dev/docs/apps/build/webhooks, 2026-07) — not a
 * field inside the JSON payload, whose shape varies by topic.
 */
export function normalizeShopifyEvent(
  rawBody: string | Buffer,
  headers: Record<string, string | undefined>,
): CommerceEvent {
  const webhookId = headers["x-shopify-webhook-id"] ?? headers["X-Shopify-Webhook-Id"];
  const topic = headers["x-shopify-topic"] ?? headers["X-Shopify-Topic"] ?? "";
  if (!webhookId) {
    throw new Error("Shopify webhook missing X-Shopify-Webhook-Id header");
  }

  const payload = JSON.parse(rawBody.toString()) as ShopifyWebhookPayload;
  const type = TOPIC_MAP[topic] ?? "unknown";

  return {
    id: webhookId,
    type,
    provider: "shopify",
    amount:
      payload.total_price && payload.currency
        ? {
            amount: Math.round(Number(payload.total_price) * 100),
            currency: payload.currency.toUpperCase(),
          }
        : undefined,
    reference: payload.id !== undefined ? String(payload.id) : undefined,
    raw: payload,
  };
}

export interface ShopifyWebhookHandlerDeps {
  verifier: WebhookVerifier;
  store: IdempotencyStore;
}

/**
 * Build the deployable request handler: verify (constant-time, before parse)
 * -> de-duplicate by event id -> normalize. Returns a `Response`, matching
 * both Next.js Route Handlers and Astro `APIRoute` return types.
 */
export function createShopifyWebhookHandler(
  deps: ShopifyWebhookHandlerDeps,
): (request: Request) => Promise<Response> {
  return async function handleShopifyWebhook(request: Request): Promise<Response> {
    const rawBody = await request.text();
    const headers: Record<string, string | undefined> = {};
    request.headers.forEach((value, key) => {
      headers[key.toLowerCase()] = value;
    });

    if (!deps.verifier.verify(rawBody, headers)) {
      return new Response("invalid signature", { status: 401 });
    }

    let event: CommerceEvent;
    try {
      event = normalizeShopifyEvent(rawBody, headers);
    } catch (err) {
      return new Response(err instanceof Error ? err.message : "malformed webhook body", {
        status: 400,
      });
    }

    if (await deps.store.seen(event.id)) {
      return new Response("ok (duplicate)", { status: 200 });
    }
    await deps.store.remember(event.id);

    // TODO(consumer): dispatch `event` to your order-fulfillment / inventory
    // logic here. Keep it fast — Shopify expects a 2xx within a few seconds
    // and retries on timeout, which the dedup above protects against.

    return new Response("ok", { status: 200 });
  };
}
