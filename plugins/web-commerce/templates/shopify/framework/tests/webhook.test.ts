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

  return new Request("https://example.com/api/webhooks/shopify", {
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
    const verifier = new ShopifyWebhookVerifier(SECRET);
    expect(verifier.verify(JSON.stringify({ id: 1 }), { "x-shopify-hmac-sha256": "bogus" })).toBe(
      false,
    );
  });

  it("rejects when the header carries a different (but well-formed) HMAC", () => {
    const body = JSON.stringify({ id: 1 });
    const wrongSecretDigest = createHmac("sha256", "a-different-secret")
      .update(body)
      .digest("base64");
    const verifier = new ShopifyWebhookVerifier(SECRET);
    expect(verifier.verify(body, { "x-shopify-hmac-sha256": wrongSecretDigest })).toBe(false);
  });
});

describe("normalizeShopifyEvent", () => {
  it("uses X-Shopify-Webhook-Id as the CommerceEvent id", () => {
    const body = JSON.stringify({ id: 7, total_price: "12.34", currency: "cad" });
    const event = normalizeShopifyEvent(body, {
      "x-shopify-webhook-id": "delivery-xyz",
      "x-shopify-topic": "orders/paid",
    });
    expect(event.id).toBe("delivery-xyz");
    expect(event.amount).toEqual({ amount: 1234, currency: "CAD" });
  });

  it("throws when the webhook id header is absent", () => {
    expect(() => normalizeShopifyEvent("{}", { "x-shopify-topic": "orders/paid" })).toThrow(
      /X-Shopify-Webhook-Id/,
    );
  });
});

describe("createShopifyWebhookHandler", () => {
  it("rejects a tampered signature with 401 and never records it as seen", async () => {
    const store = new InMemoryIdempotencyStore();
    const handler = createShopifyWebhookHandler({
      verifier: new ShopifyWebhookVerifier(SECRET),
      store,
    });
    const res = await handler(signedRequest(JSON.stringify({ id: 1 }), { badSignature: true }));
    expect(res.status).toBe(401);
    expect(await store.seen("wh-1")).toBe(false);
  });

  it("de-duplicates a replayed delivery by event id", async () => {
    const store = new InMemoryIdempotencyStore();
    const handler = createShopifyWebhookHandler({
      verifier: new ShopifyWebhookVerifier(SECRET),
      store,
    });
    const body = JSON.stringify({ id: 42, total_price: "5.00", currency: "usd" });

    const first = await handler(signedRequest(body, { webhookId: "wh-dup" }));
    const replay = await handler(signedRequest(body, { webhookId: "wh-dup" }));

    expect(first.status).toBe(200);
    expect(await first.text()).toBe("ok");
    expect(replay.status).toBe(200);
    expect(await replay.text()).toBe("ok (duplicate)");
  });

  it("returns 400 on a malformed body without throwing out of the handler", async () => {
    const store = new InMemoryIdempotencyStore();
    const handler = createShopifyWebhookHandler({
      verifier: new ShopifyWebhookVerifier(SECRET),
      store,
    });
    const res = await handler(signedRequest("not json", { webhookId: "wh-bad-json" }));
    expect(res.status).toBe(400);
  });
});
