import test from "node:test";
import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import { KvIdempotencyStore } from "../kv-idempotency-store.ts";
import type { EdgeKv } from "../kv-idempotency-store.ts";
import { handleSquareWebhookRequest } from "../webhook.ts";

// domainplugins-10 (repo-review 2026-10-19): claim -> work -> remember, with a
// release when the work throws, over the KV store the static tier ships.

const SIGNATURE_KEY = "test-signature-key";
const NOTIFICATION_URL = "https://example.test/api/webhooks/square";

/** An in-memory EdgeKv whose setIfAbsent is atomic (one JS turn), like Redis SET NX. */
class FakeKv implements EdgeKv {
  readonly data = new Map<string, string>();
  async get(key: string) {
    return this.data.get(key) ?? null;
  }
  async set(key: string, value: string) {
    this.data.set(key, value);
  }
  async setIfAbsent(key: string, value: string) {
    if (this.data.has(key)) return false;
    this.data.set(key, value);
    return true;
  }
  async delete(key: string) {
    this.data.delete(key);
  }
}

function paymentDelivery(eventId: string): Request {
  const rawBody = JSON.stringify({
    merchant_id: "M",
    type: "payment.updated",
    event_id: eventId,
    created_at: "2026-10-19T10:00:00Z",
    data: {
      type: "payment",
      id: "p",
      object: {
        payment: {
          id: "pay_1",
          status: "COMPLETED",
          amount_money: { amount: 100, currency: "USD" },
        },
      },
    },
  });
  const signature = createHmac("sha256", SIGNATURE_KEY)
    .update(NOTIFICATION_URL + rawBody)
    .digest("base64");
  return new Request(NOTIFICATION_URL, {
    method: "POST",
    headers: { "x-square-hmacsha256-signature": signature },
    body: rawBody,
  });
}

test("KV store: a thrown side effect releases the claim, the retry runs it once", async () => {
  process.env.SQUARE_WEBHOOK_SIGNATURE_KEY = SIGNATURE_KEY;
  process.env.SQUARE_WEBHOOK_NOTIFICATION_URL = NOTIFICATION_URL;
  const kv = new FakeKv();
  const store = new KvIdempotencyStore(kv);
  let attempts = 0;
  let fulfilled = 0;
  const onEvent = async () => {
    attempts += 1;
    if (attempts === 1) throw new Error("fulfilment failed");
    fulfilled += 1;
  };

  assert.equal(
    (await handleSquareWebhookRequest(paymentDelivery("evt_s1"), store, onEvent)).status,
    500,
  );
  assert.equal(await store.seen("evt_s1"), false);
  assert.equal(
    (await handleSquareWebhookRequest(paymentDelivery("evt_s1"), store, onEvent)).status,
    200,
  );
  assert.equal(
    (await handleSquareWebhookRequest(paymentDelivery("evt_s1"), store, onEvent)).status,
    200,
  );
  assert.equal(fulfilled, 1);
  assert.equal(kv.data.get("square:webhook-event:evt_s1"), "done");
});

test("KV store: concurrent deliveries of one event fulfil once", async () => {
  process.env.SQUARE_WEBHOOK_SIGNATURE_KEY = SIGNATURE_KEY;
  process.env.SQUARE_WEBHOOK_NOTIFICATION_URL = NOTIFICATION_URL;
  const store = new KvIdempotencyStore(new FakeKv());
  let fulfilled = 0;
  const onEvent = async () => {
    fulfilled += 1;
  };
  const results = await Promise.all([
    handleSquareWebhookRequest(paymentDelivery("evt_s2"), store, onEvent),
    handleSquareWebhookRequest(paymentDelivery("evt_s2"), store, onEvent),
  ]);
  assert.deepEqual(
    results.map((r) => r.status),
    [200, 200],
  );
  assert.equal(fulfilled, 1);
});
