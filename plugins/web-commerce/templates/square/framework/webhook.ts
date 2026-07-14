import { createHmac } from "node:crypto";
import { safeSignatureEqual } from "../../shared/webhook-verify.ts";
import type { WebhookRequest } from "../../shared/payment-provider.ts";
import type { CommerceEvent, CommerceEventType } from "../../shared/commerce-types.ts";
import type { IdempotencyStore } from "../../shared/idempotency-store.ts";

export interface SquareInventoryCountPayload {
  catalog_object_id: string;
  catalog_object_type?: string;
  state: string; // e.g. "IN_STOCK"
  location_id: string;
  quantity: string; // Square sends quantity as a decimal string
  calculated_at: string; // ISO 8601 -- Square's authoritative ordering signal
}

export interface SquareWebhookEnvelope {
  merchant_id: string;
  type: string;
  event_id: string;
  created_at: string;
  data: {
    type: string;
    id: string;
    object: Record<string, unknown>;
  };
}

/**
 * Square signs `signatureKey + notificationUrl + rawBody` with HMAC-SHA256
 * and base64-encodes it into the `x-square-hmacsha256-signature` header.
 * MUST verify (constant-time) before any `JSON.parse` of the body (CLAUDE.md
 * §2 #4, rubric #2). Source: knowledge/provider-tracks-2026.md §3
 * (developer.squareup.com/docs/webhooks/overview, retrieved 2026-07-13).
 */
export function verifySquareSignature(
  rawBody: string | Buffer,
  headers: Record<string, string | undefined>,
  signatureKey: string,
  notificationUrl: string,
): boolean {
  const provided = headers["x-square-hmacsha256-signature"];
  if (!provided) return false;

  const bodyString = typeof rawBody === "string" ? rawBody : rawBody.toString("utf8");
  const computed = createHmac("sha256", signatureKey)
    .update(notificationUrl + bodyString)
    .digest("base64");

  return safeSignatureEqual(computed, provided);
}

function mapEventType(squareType: string, paymentStatus?: string): CommerceEventType {
  switch (squareType) {
    case "payment.created":
    case "payment.updated":
      if (paymentStatus === "COMPLETED") return "payment.succeeded";
      if (paymentStatus === "FAILED" || paymentStatus === "CANCELED") return "payment.failed";
      return "unknown";
    case "refund.created":
    case "refund.updated":
      return "payment.refunded";
    case "order.created":
    case "order.updated":
      return "checkout.completed";
    case "inventory.count.updated":
      return "inventory.updated";
    case "catalog.version.updated":
      return "catalog.updated";
    default:
      return "unknown";
  }
}

interface SquarePaymentObject {
  id?: string;
  status?: string;
  order_id?: string;
  amount_money?: { amount: number; currency: string };
}

interface SquareRefundObject {
  payment_id?: string;
  amount_money?: { amount: number; currency: string };
}

/**
 * Verify, de-dupe, and normalize an inbound Square webhook.
 *
 * Throws when the signature fails verification -- callers MUST reject the
 * request (4xx) and never fall through to processing (rubric #2).
 *
 * When the event id has already been processed, returns a `type: "unknown"`
 * event carrying the same id and raw envelope rather than re-running side
 * effects -- Square retries webhook deliveries and does not guarantee
 * exactly-once delivery, so the caller can safely no-op and still answer 2xx
 * (rubric #3). `pos-reconciliation.ts` does its OWN event-id de-dup on top
 * of this (defense in depth for the inventory-specific path).
 */
export async function verifyAndParseSquareWebhook(
  req: WebhookRequest,
  idempotency: IdempotencyStore,
): Promise<CommerceEvent> {
  const signatureKey = process.env.SQUARE_WEBHOOK_SIGNATURE_KEY;
  const notificationUrl = process.env.SQUARE_WEBHOOK_NOTIFICATION_URL;
  if (!signatureKey || !notificationUrl) {
    throw new Error(
      "SQUARE_WEBHOOK_SIGNATURE_KEY / SQUARE_WEBHOOK_NOTIFICATION_URL not set -- see .env.example",
    );
  }

  if (!verifySquareSignature(req.rawBody, req.headers, signatureKey, notificationUrl)) {
    throw new Error("Square webhook signature verification failed");
  }

  const bodyString = typeof req.rawBody === "string" ? req.rawBody : req.rawBody.toString("utf8");
  const envelope = JSON.parse(bodyString) as SquareWebhookEnvelope;

  if (await idempotency.seen(envelope.event_id)) {
    return { id: envelope.event_id, type: "unknown", provider: "square", raw: envelope };
  }
  await idempotency.remember(envelope.event_id);

  const object = envelope.data?.object ?? {};
  const payment = (object as { payment?: SquarePaymentObject }).payment;
  const refund = (object as { refund?: SquareRefundObject }).refund;

  return {
    id: envelope.event_id,
    type: mapEventType(envelope.type, payment?.status),
    provider: "square",
    amount: payment?.amount_money ?? refund?.amount_money,
    reference: payment?.id ?? refund?.payment_id,
    raw: envelope,
  };
}

/**
 * Pull the normalized inventory counts out of a verified `inventory.count.
 * updated` envelope, for `pos-reconciliation.ts` to apply. Returns `[]` for
 * any other event type or a malformed payload -- callers should treat that
 * as "nothing to reconcile," not an error.
 */
export function extractInventoryCounts(
  envelope: SquareWebhookEnvelope,
): SquareInventoryCountPayload[] {
  if (envelope.type !== "inventory.count.updated") return [];
  const counts = (envelope.data?.object as { inventory_counts?: unknown } | undefined)
    ?.inventory_counts;
  return Array.isArray(counts) ? (counts as SquareInventoryCountPayload[]) : [];
}

/**
 * The framework tier's webhook route handler. Adapt the Request/Response
 * shapes here to your framework's route-handler convention (Next.js Route
 * Handler, Astro API route, Express middleware, ...) -- they are Fetch-API
 * standard so the adaptation is thin either way.
 */
export async function handleSquareWebhookRequest(
  request: Request,
  idempotency: IdempotencyStore,
  onInventoryCounts?: (counts: SquareInventoryCountPayload[], eventId: string) => Promise<void>,
): Promise<Response> {
  const rawBody = await request.text();
  const headers: Record<string, string | undefined> = {};
  request.headers.forEach((value, key) => {
    headers[key.toLowerCase()] = value;
  });

  try {
    const event = await verifyAndParseSquareWebhook({ rawBody, headers }, idempotency);
    if (event.type === "inventory.updated" && onInventoryCounts) {
      const envelope = event.raw as SquareWebhookEnvelope;
      await onInventoryCounts(extractInventoryCounts(envelope), event.id);
    }
    return new Response(JSON.stringify({ received: true, eventId: event.id }), {
      status: 200,
      headers: { "content-type": "application/json" },
    });
  } catch {
    // Never leak signature/verification internals in the response body.
    return new Response(JSON.stringify({ error: "invalid webhook" }), {
      status: 400,
      headers: { "content-type": "application/json" },
    });
  }
}
