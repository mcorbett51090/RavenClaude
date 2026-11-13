import { createHmac } from "node:crypto";
import { describe, expect, it } from "vitest";
import { ShopifyWebhookVerifier, createShopifyWebhookHandler } from "../webhook";
import { InMemoryIdempotencyStore } from "../../../shared/idempotency-store";

// domainplugins-10 (repo-review 2026-10-19): claim -> side effects -> remember,
// with a release when the side effects throw. Before, the handler remembered
// the event BEFORE its side effects, so Shopify's retry of a failed delivery
// was acknowledged without the work, and concurrent duplicates both ran it.

const SECRET = "test-webhook-secret";

function delivery(webhookId: string): Request {
  const body = JSON.stringify({ id: 7, total_price: "10.00", currency: "usd" });
  return new Request("https://example.com/webhooks/shopify", {
    method: "POST",
    headers: {
      "X-Shopify-Hmac-Sha256": createHmac("sha256", SECRET).update(body).digest("base64"),
      "X-Shopify-Webhook-Id": webhookId,
      "X-Shopify-Topic": "orders/paid",
    },
    body,
  });
}

describe("claim lifecycle", () => {
  it("answers 500 when the side effect throws, and the retry runs it exactly once", async () => {
    const store = new InMemoryIdempotencyStore();
    let attempts = 0;
    let fulfilled = 0;
    const handler = createShopifyWebhookHandler({
      verifier: new ShopifyWebhookVerifier(SECRET),
      store,
      onEvent: async () => {
        attempts += 1;
        if (attempts === 1) throw new Error("fulfilment failed");
        fulfilled += 1;
      },
    });

    expect((await handler(delivery("wh-claim-1"))).status).toBe(500);
    expect(await store.seen("wh-claim-1")).toBe(false);
    expect((await handler(delivery("wh-claim-1"))).status).toBe(200);
    expect((await handler(delivery("wh-claim-1"))).status).toBe(200);
    expect(fulfilled).toBe(1);
  });

  it("runs the side effect once for two concurrent deliveries of one event", async () => {
    let fulfilled = 0;
    const handler = createShopifyWebhookHandler({
      verifier: new ShopifyWebhookVerifier(SECRET),
      store: new InMemoryIdempotencyStore(),
      onEvent: async () => {
        fulfilled += 1;
      },
    });
    const [a, b] = await Promise.all([
      handler(delivery("wh-claim-2")),
      handler(delivery("wh-claim-2")),
    ]);
    expect(a.status).toBe(200);
    expect(b.status).toBe(200);
    expect(fulfilled).toBe(1);
  });
});
