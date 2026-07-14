import test from "node:test";
import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import { verifySquareSignature, verifyAndParseSquareWebhook } from "../webhook.ts";
import { InMemoryIdempotencyStore } from "../../../shared/idempotency-store.ts";

const SIGNATURE_KEY = "test-signature-key";
const NOTIFICATION_URL = "https://example.test/api/webhooks/square";

function sign(rawBody: string): string {
  return createHmac("sha256", SIGNATURE_KEY)
    .update(NOTIFICATION_URL + rawBody)
    .digest("base64");
}

function samplePaymentEvent(eventId: string) {
  return JSON.stringify({
    merchant_id: "MERCHANT1",
    type: "payment.updated",
    event_id: eventId,
    created_at: "2026-07-13T00:00:00Z",
    data: {
      type: "payment",
      id: "payment-object-id",
      object: {
        payment: {
          id: "pay_123",
          status: "COMPLETED",
          order_id: "order_123",
          amount_money: { amount: 1999, currency: "USD" },
        },
      },
    },
  });
}

test("verifySquareSignature accepts a correctly signed body", () => {
  const rawBody = samplePaymentEvent("evt_1");
  const signature = sign(rawBody);
  assert.equal(
    verifySquareSignature(
      rawBody,
      { "x-square-hmacsha256-signature": signature },
      SIGNATURE_KEY,
      NOTIFICATION_URL,
    ),
    true,
  );
});

test("verifySquareSignature rejects a tampered body (rubric #2)", () => {
  const rawBody = samplePaymentEvent("evt_1");
  const signature = sign(rawBody);
  const tamperedBody = rawBody.replace("1999", "1"); // attacker lowers the charged amount
  assert.equal(
    verifySquareSignature(
      tamperedBody,
      { "x-square-hmacsha256-signature": signature },
      SIGNATURE_KEY,
      NOTIFICATION_URL,
    ),
    false,
  );
});

test("verifySquareSignature rejects a forged/mismatched signature", () => {
  const rawBody = samplePaymentEvent("evt_1");
  assert.equal(
    verifySquareSignature(
      rawBody,
      { "x-square-hmacsha256-signature": "not-a-real-signature==" },
      SIGNATURE_KEY,
      NOTIFICATION_URL,
    ),
    false,
  );
});

test("verifySquareSignature rejects a missing signature header", () => {
  const rawBody = samplePaymentEvent("evt_1");
  assert.equal(verifySquareSignature(rawBody, {}, SIGNATURE_KEY, NOTIFICATION_URL), false);
});

test("verifyAndParseSquareWebhook throws on tampered payload (never falls through to processing)", async () => {
  process.env.SQUARE_WEBHOOK_SIGNATURE_KEY = SIGNATURE_KEY;
  process.env.SQUARE_WEBHOOK_NOTIFICATION_URL = NOTIFICATION_URL;

  const rawBody = samplePaymentEvent("evt_2");
  const signature = sign(rawBody);
  const tamperedBody = rawBody.replace("1999", "1");

  await assert.rejects(
    () =>
      verifyAndParseSquareWebhook(
        { rawBody: tamperedBody, headers: { "x-square-hmacsha256-signature": signature } },
        new InMemoryIdempotencyStore(),
      ),
    /signature verification failed/,
  );
});

test("verifyAndParseSquareWebhook normalizes a verified payment.updated event", async () => {
  process.env.SQUARE_WEBHOOK_SIGNATURE_KEY = SIGNATURE_KEY;
  process.env.SQUARE_WEBHOOK_NOTIFICATION_URL = NOTIFICATION_URL;

  const rawBody = samplePaymentEvent("evt_3");
  const signature = sign(rawBody);

  const event = await verifyAndParseSquareWebhook(
    { rawBody, headers: { "x-square-hmacsha256-signature": signature } },
    new InMemoryIdempotencyStore(),
  );

  assert.equal(event.id, "evt_3");
  assert.equal(event.type, "payment.succeeded");
  assert.equal(event.provider, "square");
  assert.equal(event.reference, "pay_123");
  assert.deepEqual(event.amount, { amount: 1999, currency: "USD" });
});

test("verifyAndParseSquareWebhook: a replayed event_id is a no-op (rubric #3)", async () => {
  process.env.SQUARE_WEBHOOK_SIGNATURE_KEY = SIGNATURE_KEY;
  process.env.SQUARE_WEBHOOK_NOTIFICATION_URL = NOTIFICATION_URL;

  const store = new InMemoryIdempotencyStore();
  const rawBody = samplePaymentEvent("evt_replay");
  const signature = sign(rawBody);
  const req = { rawBody, headers: { "x-square-hmacsha256-signature": signature } };

  const first = await verifyAndParseSquareWebhook(req, store);
  assert.equal(first.type, "payment.succeeded");

  // Square retries webhook deliveries -- the exact same event_id arrives again.
  const second = await verifyAndParseSquareWebhook(req, store);
  assert.equal(second.id, "evt_replay");
  assert.equal(second.type, "unknown"); // no-op marker, not re-processed as a fresh payment.succeeded
});
