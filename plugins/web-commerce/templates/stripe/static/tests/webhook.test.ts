/**
 * Static-checkable tests for the Stripe STATIC tier webhook path.
 * Run with: npx tsx --test templates/stripe/static/tests/webhook.test.ts
 * (or wire into your framework's runner — Vitest/Jest accept the same
 * `node:test`-shaped assertions with minimal adaptation).
 *
 * No network calls: `Stripe.webhooks.generateTestHeaderString` is a pure,
 * local HMAC helper (same algorithm this template hand-rolls in
 * ../stripe-signature.ts), so these tests validate against Stripe's actual
 * documented scheme without hitting the Stripe API.
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import Stripe from "stripe";
import { InMemoryIdempotencyStore } from "../../../shared/idempotency-store";
import { StripeStaticProvider } from "../provider";
import { createWebhookHandler } from "../webhook";

const WEBHOOK_SECRET = "whsec_test_secret_not_real_00000000000000000000";
const SECRET_KEY = "sk_test_not_a_real_key_00000000000000000000000000";

function samplePayload(id = "evt_test_1"): string {
  return JSON.stringify({
    id,
    object: "event",
    type: "payment_intent.succeeded",
    data: { object: { id: "pi_test_1", amount: 4800, currency: "usd" } },
  });
}

function signedHeaders(payload: string, secret = WEBHOOK_SECRET): Record<string, string> {
  const header = Stripe.webhooks.generateTestHeaderString({ payload, secret });
  return { "stripe-signature": header };
}

function buildDeps() {
  const provider = new StripeStaticProvider({
    secretKey: SECRET_KEY,
    webhookSecret: WEBHOOK_SECRET,
  });
  const store = new InMemoryIdempotencyStore();
  return { provider, store };
}

test("a tampered-signature payload is rejected with 400, not processed", async () => {
  const deps = buildDeps();
  const handler = createWebhookHandler(deps);
  const payload = samplePayload();
  const headers = signedHeaders(payload);

  // Tamper the body AFTER signing — the signature no longer matches it.
  const tamperedPayload = payload.replace('"amount":4800', '"amount":100');
  const request = new Request("https://example.com/webhook", {
    method: "POST",
    headers,
    body: tamperedPayload,
  });

  const response = await handler(request);
  assert.equal(response.status, 400);
  assert.equal(
    await deps.store.seen("evt_test_1"),
    false,
    "a rejected event must never be marked seen",
  );
});

test("a replayed event id is a no-op on the second delivery", async () => {
  const deps = buildDeps();
  const handler = createWebhookHandler(deps);
  const payload = samplePayload("evt_replay_1");
  const headers = signedHeaders(payload);

  const first = await handler(
    new Request("https://example.com/webhook", { method: "POST", headers, body: payload }),
  );
  assert.equal(first.status, 200);
  assert.equal(await deps.store.seen("evt_replay_1"), true);

  // Same event, delivered again (Stripe retries do not guarantee once-only delivery).
  const second = await handler(
    new Request("https://example.com/webhook", { method: "POST", headers, body: payload }),
  );
  assert.equal(second.status, 200, "a replay must still 2xx so Stripe stops retrying");
});

test("a missing signature header is rejected", async () => {
  const deps = buildDeps();
  const handler = createWebhookHandler(deps);
  const payload = samplePayload("evt_no_sig");

  const response = await handler(
    new Request("https://example.com/webhook", { method: "POST", body: payload }),
  );
  assert.equal(response.status, 400);
});

test("a stale timestamp outside the tolerance window is rejected", async () => {
  const deps = buildDeps();
  const handler = createWebhookHandler(deps);
  const payload = samplePayload("evt_stale");
  const staleTimestamp = Math.floor(Date.now() / 1000) - 60 * 60; // 1h old
  const header = Stripe.webhooks.generateTestHeaderString({
    payload,
    secret: WEBHOOK_SECRET,
    timestamp: staleTimestamp,
  });

  const response = await handler(
    new Request("https://example.com/webhook", {
      method: "POST",
      headers: { "stripe-signature": header },
      body: payload,
    }),
  );
  assert.equal(response.status, 400);
});
