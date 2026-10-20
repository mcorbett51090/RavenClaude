import { createHmac } from "node:crypto";
import { safeSignatureEqual } from "../../shared/webhook-verify.ts";
import type { WebhookRequest } from "../../shared/payment-provider.ts";
import type { CommerceEvent, CommerceEventType } from "../../shared/commerce-types.ts";
import type { IdempotencyStore } from "../../shared/idempotency-store.ts";

interface SquareWebhookEnvelope {
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
      // Square refund status lifecycle is PENDING -> COMPLETED|REJECTED|FAILED
      // (developer.squareup.com/docs/refunds-api/overview). Only a COMPLETED
      // refund is actually "payment.refunded" -- a pending/rejected/failed
      // refund must not be reported as complete to callers keying side
      // effects off event.type.
      if (paymentStatus === "COMPLETED") return "payment.refunded";
      return "unknown";
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
  status?: string;
  amount_money?: { amount: number; currency: string };
}

const DUPLICATE_DELIVERIES = new WeakSet<CommerceEvent>();

/**
 * True for the no-op event `verifyAndParseSquareWebhook` returns when the
 * event id was already claimed or processed. Distinguishes a duplicate from a
 * fresh event whose type merely maps to "unknown"; only a fresh event's claim
 * may be completed (`remember`) or dropped (`release`) by the caller.
 */
export function isDuplicateDelivery(event: CommerceEvent): boolean {
  return DUPLICATE_DELIVERIES.has(event);
}

/**
 * Verify, de-dupe, and normalize an inbound Square webhook.
 *
 * Throws when the signature fails verification -- callers MUST reject the
 * request (4xx) and never fall through to processing (rubric #2).
 *
 * De-dupes with the store's atomic `claim()`. When the event id is already
 * claimed or processed, returns a `type: "unknown"` event carrying the same id
 * (and `isDuplicateDelivery(event)` is true) rather than re-running side
 * effects -- Square retries webhook deliveries and does not guarantee
 * exactly-once delivery, so the caller can safely no-op and still answer 2xx
 * (rubric #3).
 *
 * A fresh event comes back CLAIMED, not done: the caller owns the claim and
 * must call `idempotency.remember(event.id)` once its side effects succeed,
 * or `idempotency.release(event.id)` when they fail, so Square's retry runs
 * them again. `handleSquareWebhookRequest` below does exactly that.
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

  if (!(await idempotency.claim(envelope.event_id))) {
    const duplicate: CommerceEvent = {
      id: envelope.event_id,
      type: "unknown",
      provider: "square",
      raw: envelope,
    };
    DUPLICATE_DELIVERIES.add(duplicate);
    return duplicate;
  }

  const object = envelope.data?.object ?? {};
  const payment = (object as { payment?: SquarePaymentObject }).payment;
  const refund = (object as { refund?: SquareRefundObject }).refund;

  return {
    id: envelope.event_id,
    type: mapEventType(envelope.type, payment?.status ?? refund?.status),
    provider: "square",
    amount: payment?.amount_money ?? refund?.amount_money,
    reference: payment?.id ?? refund?.payment_id,
    raw: envelope,
  };
}

/**
 * The thin serverless entrypoint (CLAUDE.md §2 #3). A truly static site has
 * no server to verify a webhook or hold idempotency state on -- this
 * function is meant to be deployed as a small Cloudflare Worker / Vercel or
 * Netlify Function, backed by the KV-based `IdempotencyStore` in
 * `./kv-idempotency-store.ts`. The Request/Response types here are
 * Fetch-API standard, so they map directly onto every one of those
 * platforms' handler signatures.
 *
 * `onEvent` is the seam for your side effects (order fulfillment, inventory
 * pull, notifications, ...), keyed off `event.type`. If it throws, the claim
 * is released and the function answers 500, so Square retries the delivery.
 */
export async function handleSquareWebhookRequest(
  request: Request,
  idempotency: IdempotencyStore,
  onEvent?: (event: CommerceEvent) => Promise<void>,
): Promise<Response> {
  const rawBody = await request.text();
  const headers: Record<string, string | undefined> = {};
  request.headers.forEach((value, key) => {
    headers[key.toLowerCase()] = value;
  });

  let event: CommerceEvent;
  try {
    event = await verifyAndParseSquareWebhook({ rawBody, headers }, idempotency);
  } catch {
    // Never leak signature/verification internals in the response body.
    return new Response(JSON.stringify({ error: "invalid webhook" }), {
      status: 400,
      headers: { "content-type": "application/json" },
    });
  }

  if (!isDuplicateDelivery(event)) {
    // This delivery holds the claim: complete it on success, drop it on
    // failure so Square's retry runs the side effects again.
    try {
      if (onEvent) await onEvent(event);
      await idempotency.remember(event.id);
    } catch {
      await idempotency.release(event.id);
      return new Response(JSON.stringify({ error: "processing failed" }), {
        status: 500,
        headers: { "content-type": "application/json" },
      });
    }
  }

  return new Response(JSON.stringify({ received: true, eventId: event.id }), {
    status: 200,
    headers: { "content-type": "application/json" },
  });
}
