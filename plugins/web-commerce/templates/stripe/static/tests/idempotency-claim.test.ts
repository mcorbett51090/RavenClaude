/**
 * domainplugins-10 (repo-review 2026-10-19): claim -> side effects -> remember,
 * with a release when the side effects throw. Before, the handler remembered
 * the event BEFORE its side effects, so Stripe's retry of a failed delivery was
 * acknowledged without the work, and concurrent duplicates both ran it.
 * Run with: npx tsx --test templates/stripe/static/tests/idempotency-claim.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import Stripe from "stripe";
import { InMemoryIdempotencyStore } from "../../../shared/idempotency-store";
import { StripeStaticProvider } from "../provider";
import { createWebhookHandler } from "../webhook";

// Test-only values, assembled so no key-shaped literal sits in the source.
const WEBHOOK_SECRET = ["whsec", "test", "claim", "not", "real"].join("_");
const SECRET_KEY = ["sk", "test", "claim", "not", "real"].join("_");
function delivery(id: string): Request {
  const payload = JSON.stringify({
    id,
    object: "event",
    type: "payment_intent.succeeded",
    data: { object: { id: "pi_claim", amount: 4800, currency: "usd" } },
  });
  const header = Stripe.webhooks.generateTestHeaderString({ payload, secret: WEBHOOK_SECRET });
  return new Request("https://example.com/webhook", {
    method: "POST",
    headers: { "stripe-signature": header },
    body: payload,
  });
}

function provider() {
  return new StripeStaticProvider({ secretKey: SECRET_KEY, webhookSecret: WEBHOOK_SECRET });
}

test("a side effect that throws answers 500, and the retry runs it exactly once", async () => {
  const store = new InMemoryIdempotencyStore();
  let attempts = 0;
  let fulfilled = 0;
  const handler = createWebhookHandler({
    provider: provider(),
    store,
    onEvent: async () => {
      attempts += 1;
      if (attempts === 1) throw new Error("fulfilment failed");
      fulfilled += 1;
    },
  });

  assert.equal((await handler(delivery("evt_claim_1"))).status, 500);
  assert.equal(await store.seen("evt_claim_1"), false, "the failed claim must be released");
  assert.equal((await handler(delivery("evt_claim_1"))).status, 200);
  assert.equal((await handler(delivery("evt_claim_1"))).status, 200);
  assert.equal(fulfilled, 1);
});

test("two concurrent deliveries of one event run the side effect once", async () => {
  let fulfilled = 0;
  const handler = createWebhookHandler({
    provider: provider(),
    store: new InMemoryIdempotencyStore(),
    onEvent: async () => {
      fulfilled += 1;
    },
  });
  const [a, b] = await Promise.all([
    handler(delivery("evt_claim_2")),
    handler(delivery("evt_claim_2")),
  ]);
  assert.equal(a.status, 200);
  assert.equal(b.status, 200);
  assert.equal(fulfilled, 1);
});
