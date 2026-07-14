/**
 * Thin serverless Shopify webhook receiver — static tier.
 *
 * A literally-static site has no server of its own to verify a webhook
 * signature or hold idempotency state (CLAUDE.md §2 #3), so this file is
 * meant to be deployed as a small standalone function (Cloudflare Worker,
 * Vercel/Netlify Edge Function, Deno Deploy) backed by an EXTERNAL KV
 * (Upstash / Vercel KV) for the IdempotencyStore — never in-memory, which a
 * recycled invocation would silently lose (re-processing an event = a
 * double-decremented inventory count or a double-fulfilled order).
 *
 * Uses the standard Fetch API `Request`/`Response` shape so it drops into
 * any of the above runtimes with a one-line adapter — see README.md.
 */
import { createHmac } from "node:crypto";
import { safeSignatureEqual } from "../../shared/webhook-verify";
import type { WebhookVerifier } from "../../shared/webhook-verify";
import type { IdempotencyStore } from "../../shared/idempotency-store";
import type { CommerceEvent, CommerceEventType } from "../../shared/commerce-types";

/**
 * Verifies Shopify's `X-Shopify-Hmac-Sha256` header: base64 HMAC-SHA256 over
 * the RAW (unparsed) request body, keyed with the webhook signing secret from
 * the Shopify admin (Settings > Notifications > Webhooks) — NOT the
 * Storefront API token used by cart.ts. Constant-time compare via
 * `safeSignatureEqual` (CLAUDE.md §2 #4). Verification MUST happen before the
 * body is parsed as JSON — parsing first (or re-serializing) can change
 * whitespace and silently break the signature.
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
 * add topics your integration subscribes to in the Shopify admin/CLI. Any
 * unmapped topic normalizes to "unknown" rather than guessing.
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
 * CommerceEvent shape. The event id used for de-duplication is the
 * `X-Shopify-Webhook-Id` header — a unique id per delivery attempt that
 * Shopify sends on every webhook (confirmed against
 * https://shopify.dev/docs/apps/build/webhooks, 2026-07) — NOT a field
 * inside the JSON payload, whose shape and presence of `id` varies by topic.
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
 * -> de-duplicate by event id -> normalize. Returns a `Response` so the same
 * function works unmodified as a Cloudflare Worker `fetch` export, a Vercel
 * Edge Function default export, or a Netlify Edge Function.
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
      // Already processed this delivery — acknowledge without re-running side effects.
      return new Response("ok (duplicate)", { status: 200 });
    }
    await deps.store.remember(event.id);

    // TODO(consumer): dispatch `event` to your order-fulfillment / inventory
    // logic here. Keep it fast — Shopify expects a 2xx within a few seconds
    // and retries on timeout, which is exactly what the dedup above protects
    // against re-running.

    return new Response("ok", { status: 200 });
  };
}
