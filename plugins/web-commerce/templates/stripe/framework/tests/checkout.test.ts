/**
 * Price-integrity tests for the Stripe FRAMEWORK tier checkout route.
 * Run with: npx tsx --test templates/stripe/framework/tests/checkout.test.ts
 *
 * The route must charge the SERVER's catalog price x quantity, never a
 * price the browser sends. These tests use the template's example
 * PRICE_CATALOG entry in ../checkout.ts — update EXAMPLE_SKU and
 * EXAMPLE_UNIT_PRICE here when you replace that catalog with your own.
 *
 * No network calls: the Stripe SDK's `paymentIntents.create` is stubbed on
 * its resource prototype, and `https.request` is a tripwire that throws, so
 * a stub that stopped matching the SDK fails the test instead of reaching
 * api.stripe.com.
 */

import { test, mock, beforeEach } from "node:test";
import assert from "node:assert/strict";
import https from "node:https";
import Stripe from "stripe";
import { POST } from "../checkout";
import { StripeFrameworkProvider } from "../provider";

const EXAMPLE_SKU = "estate-reserve-750ml";
const EXAMPLE_UNIT_PRICE = 4800;

const SECRET_KEY = "sk_test_not_a_real_key_00000000000000000000000000";
const PUBLISHABLE_KEY = "pk_test_not_a_real_key_0000000000000000000000000";
const WEBHOOK_SECRET = "whsec_test_secret_not_real_00000000000000000000";

process.env.STRIPE_SECRET_KEY = SECRET_KEY;
process.env.STRIPE_PUBLISHABLE_KEY = PUBLISHABLE_KEY;
process.env.STRIPE_WEBHOOK_SECRET = WEBHOOK_SECRET;

const created: Array<{ amount: number; currency: string }> = [];
const paymentIntentsProto = Object.getPrototypeOf(new Stripe(SECRET_KEY).paymentIntents);
mock.method(paymentIntentsProto, "create", async (params: { amount: number; currency: string }) => {
  created.push(params);
  return { client_secret: "pi_test_1_secret_test" };
});
mock.method(https, "request", () => {
  throw new Error("network blocked in test: the Stripe SDK stub did not intercept the call");
});

beforeEach(() => {
  created.length = 0;
});

function checkoutRequest(body: unknown): Request {
  return new Request("https://shop.example/api/checkout", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

test("a tampered client price is ignored: the PaymentIntent is catalog price x quantity", async () => {
  const res = await POST(
    checkoutRequest({
      items: [{ sku: EXAMPLE_SKU, quantity: 2, amount: { amount: 1, currency: "USD" } }],
      // The pre-fix request shape, carrying an attacker-chosen price.
      lineItems: [{ name: "Estate Reserve", amount: { amount: 1, currency: "USD" }, quantity: 1 }],
    }),
  );
  assert.equal(res.status, 200);
  assert.equal(created.length, 1);
  assert.equal(created[0].amount, EXAMPLE_UNIT_PRICE * 2);
  assert.equal(created[0].currency, "usd");
});

test("an unknown sku is a 400 and creates no PaymentIntent", async () => {
  for (const sku of ["no-such-sku", "__proto__", "constructor", "toString"]) {
    const res = await POST(checkoutRequest({ items: [{ sku, quantity: 1 }] }));
    assert.equal(res.status, 400, `sku ${sku}`);
  }
  assert.equal(created.length, 0);
});

test("a quantity that is not a positive integer under the cap is a 400", async () => {
  for (const quantity of [-1, 0, 1.5, "2", null, 1e9, Number.MAX_SAFE_INTEGER + 2]) {
    const res = await POST(checkoutRequest({ items: [{ sku: EXAMPLE_SKU, quantity }] }));
    assert.equal(res.status, 400, `quantity ${String(quantity)}`);
  }
  assert.equal(created.length, 0);
});

test("a malformed body is a 400, not a 500", async () => {
  for (const body of [null, [], {}, { items: [] }, { items: "x" }, { items: [null] }]) {
    const res = await POST(checkoutRequest(body));
    assert.equal(res.status, 400, `body ${JSON.stringify(body)}`);
  }
  assert.equal(created.length, 0);
});

test("the provider rejects non-integer or non-positive amounts and quantities", async () => {
  const provider = new StripeFrameworkProvider({
    secretKey: SECRET_KEY,
    publishableKey: PUBLISHABLE_KEY,
    webhookSecret: WEBHOOK_SECRET,
  });
  const bad: Array<{ amount: number; quantity: number }> = [
    { amount: 4800, quantity: -1 },
    { amount: 4800, quantity: 0 },
    { amount: 4800, quantity: 1.5 },
    { amount: -4800, quantity: 1 },
    { amount: 0, quantity: 1 },
    { amount: 48.5, quantity: 1 },
  ];
  for (const { amount, quantity } of bad) {
    await assert.rejects(
      provider.createCheckout({
        lineItems: [
          { name: "A", amount: { amount: 4800, currency: "USD" }, quantity: 1 },
          { name: "B", amount: { amount, currency: "USD" }, quantity },
        ],
        idempotencyKey: "idem-test-1",
      }),
      /must be a positive integer/,
      `amount ${amount} quantity ${quantity}`,
    );
  }
  assert.equal(created.length, 0);
});
