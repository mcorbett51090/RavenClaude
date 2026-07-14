import { createHmac } from "node:crypto";
import { describe, expect, it } from "vitest";
import {
  ShopifyWebhookVerifier,
  createShopifyWebhookHandler,
  normalizeShopifyEvent,
} from "../webhook";
import { InMemoryIdempotencyStore } from "../../../shared/idempotency-store";

const SECRET = "test-webhook-secret";

function signedRequest(
  body: string,
  opts: { webhookId?: string; topic?: string; badSignature?: boolean } = {},
) {
  const signature = opts.badSignature
    ? "tampered-signature-not-a-real-hmac"
    : createHmac("sha256", SECRET).update(body).digest("base64");

  return new Request("https://example.com/webhooks/shopify", {
    method: "POST",
    headers: {
      "X-Shopify-Hmac-Sha256": signature,
      "X-Shopify-Webhook-Id": opts.webhookId ?? "wh-1",
      "X-Shopify-Topic": opts.topic ?? "orders/paid",
    },
    body,
  });
}

describe("ShopifyWebhookVerifier", () => {
  it("accepts a correctly signed body", () => {
    const body = JSON.stringify({ id: 1, total_price: "10.00", currency: "usd" });
    const signature = createHmac("sha256", SECRET).update(body).digest("base64");
    const verifier = new ShopifyWebhookVerifier(SECRET);
    expect(verifier.verify(body, { "x-shopify-hmac-sha256": signature })).toBe(true);
  });

  it("rejects a tampered signature", () => {
    const body = JSON.stringify({ id: 1 });
    const verifier = new ShopifyWebhookVerifier(SECRET);
    expect(verifier.verify(body, { "x-shopify-hmac-sha256": "not-the-real-hmac" })).toBe(false);
  });

  it("rejects a body that was mutated after signing (signature no longer matches)", () => {
    const original = JSON.stringify({ id: 1, total_price: "10.00" });
    const signature = createHmac("sha256", SECRET).update(original).digest("base64");
    const mutated = JSON.stringify({ id: 1, total_price: "999.00" });
    const verifier = new ShopifyWebhookVerifier(SECRET);
    expect(verifier.verify(mutated, { "x-shopify-hmac-sha256": signature })).toBe(false);
  });

  it("rejects when the signature header is missing", () => {
    const verifier = new ShopifyWebhookVerifier(SECRET);
    expect(verifier.verify("{}", {})).toBe(false);
  });
});

describe("normalizeShopifyEvent", () => {
  it("uses X-Shopify-Webhook-Id as the CommerceEvent id, not a payload field", () => {
    const body = JSON.stringify({ id: 999999, total_price: "42.50", currency: "usd" });
    const event = normalizeShopifyEvent(body, {
      "x-shopify-webhook-id": "delivery-abc-123",
      "x-shopify-topic": "orders/paid",
    });
    expect(event.id).toBe("delivery-abc-123");
    expect(event.type).toBe("payment.succeeded");
    expect(event.provider).toBe("shopify");
    expect(event.reference).toBe("999999");
    expect(event.amount).toEqual({ amount: 4250, currency: "USD" });
  });

  it("maps an unrecognized topic to 'unknown' rather than guessing", () => {
    const event = normalizeShopifyEvent(JSON.stringify({}), {
      "x-shopify-webhook-id": "delivery-2",
      "x-shopify-topic": "some/future-topic",
    });
    expect(event.type).toBe("unknown");
  });

  it("throws when the webhook id header is absent", () => {
    expect(() => normalizeShopifyEvent("{}", { "x-shopify-topic": "orders/paid" })).toThrow(
      /X-Shopify-Webhook-Id/,
    );
  });
});

describe("createShopifyWebhookHandler", () => {
  it("rejects a tampered signature with 401 and never invokes the store", async () => {
    const store = new InMemoryIdempotencyStore();
    const handler = createShopifyWebhookHandler({
      verifier: new ShopifyWebhookVerifier(SECRET),
      store,
    });
    const body = JSON.stringify({ id: 1 });
    const res = await handler(signedRequest(body, { badSignature: true }));
    expect(res.status).toBe(401);
    expect(await store.seen("wh-1")).toBe(false);
  });

  it("processes a valid event exactly once, then no-ops on replay", async () => {
    const store = new InMemoryIdempotencyStore();
    const handler = createShopifyWebhookHandler({
      verifier: new ShopifyWebhookVerifier(SECRET),
      store,
    });
    const body = JSON.stringify({ id: 42, total_price: "5.00", currency: "usd" });

    const first = await handler(signedRequest(body, { webhookId: "wh-dup", topic: "orders/paid" }));
    expect(first.status).toBe(200);
    expect(await first.text()).toBe("ok");

    const replay = await handler(
      signedRequest(body, { webhookId: "wh-dup", topic: "orders/paid" }),
    );
    expect(replay.status).toBe(200);
    expect(await replay.text()).toBe("ok (duplicate)");
  });

  it("returns 400 on a malformed body without throwing", async () => {
    const store = new InMemoryIdempotencyStore();
    const handler = createShopifyWebhookHandler({
      verifier: new ShopifyWebhookVerifier(SECRET),
      store,
    });
    const res = await handler(signedRequest("not json", { webhookId: "wh-bad-json" }));
    expect(res.status).toBe(400);
  });
});
