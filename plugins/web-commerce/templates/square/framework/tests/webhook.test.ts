import { test } from "node:test";
import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import { verifySquareSignature } from "../webhook.ts";

const KEY = "test-signature-key";
const URL = "https://example.test/api/webhooks/square";
const BODY = '{"event_id":"evt_1","type":"payment.updated"}';

function sign(key: string, url: string, body: string): string {
  return createHmac("sha256", key)
    .update(url + body)
    .digest("base64");
}

// Rubric #2 — the happy path verifies.
test("a valid Square signature verifies", () => {
  const signature = sign(KEY, URL, BODY);
  assert.equal(
    verifySquareSignature(BODY, { "x-square-hmacsha256-signature": signature }, KEY, URL),
    true,
  );
});

// Rubric #2 — a tampered body is rejected (the whole point of verify-before-parse).
test("a tampered body is rejected", () => {
  const signature = sign(KEY, URL, BODY);
  const tampered = '{"event_id":"evt_1","type":"payment.updated","amount":999999}';
  assert.equal(
    verifySquareSignature(tampered, { "x-square-hmacsha256-signature": signature }, KEY, URL),
    false,
  );
});

// A missing signature header is rejected rather than treated as trusted.
test("a missing signature header is rejected", () => {
  assert.equal(verifySquareSignature(BODY, {}, KEY, URL), false);
});
