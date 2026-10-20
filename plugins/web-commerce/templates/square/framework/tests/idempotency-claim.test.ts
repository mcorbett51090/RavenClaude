import { test } from "node:test";
import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import { InMemoryIdempotencyStore } from "../../../shared/idempotency-store.ts";
import { handleSquareWebhookRequest } from "../webhook.ts";
import type { SquareInventoryCountPayload } from "../webhook.ts";

// domainplugins-10 (repo-review 2026-10-19): the handler used to remember the
// event BEFORE its side effects, so a throw followed by Square's retry was
// acknowledged without the work, and two concurrent deliveries could both pass
// seen() and both run it. The atomic claim lifecycle fixes both.

const SIGNATURE_KEY = "test-signature-key";
const NOTIFICATION_URL = "https://example.test/api/webhooks/square";

function inventoryDelivery(eventId: string): Request {
  const rawBody = JSON.stringify({
    merchant_id: "M",
    type: "inventory.count.updated",
    event_id: eventId,
    created_at: "2026-10-19T10:00:00Z",
    data: {
      type: "inventory",
      id: "inv",
      object: {
        inventory_counts: [
          {
            catalog_object_id: "A",
            location_id: "L",
            state: "IN_STOCK",
            quantity: "3",
            calculated_at: "2026-10-19T10:00:00Z",
          },
        ],
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

function env() {
  process.env.SQUARE_WEBHOOK_SIGNATURE_KEY = SIGNATURE_KEY;
  process.env.SQUARE_WEBHOOK_NOTIFICATION_URL = NOTIFICATION_URL;
}

test("a side effect that throws is retried on redelivery, and runs exactly once overall", async () => {
  env();
  const store = new InMemoryIdempotencyStore();
  let attempts = 0;
  let applied = 0;
  const onCounts = async (_counts: SquareInventoryCountPayload[]) => {
    attempts += 1;
    if (attempts === 1) throw new Error("db down");
    applied += 1;
  };

  const first = await handleSquareWebhookRequest(inventoryDelivery("evt_t1"), store, onCounts);
  assert.equal(first.status, 500, "a failed side effect must not be acknowledged with 2xx");
  assert.equal(await store.seen("evt_t1"), false, "the failed claim must be released");

  const retry = await handleSquareWebhookRequest(inventoryDelivery("evt_t1"), store, onCounts);
  assert.equal(retry.status, 200);
  const again = await handleSquareWebhookRequest(inventoryDelivery("evt_t1"), store, onCounts);
  assert.equal(again.status, 200);
  assert.equal(applied, 1, "the work runs once: on the retry, never on the later duplicate");
});

test("two concurrent deliveries of one event run the side effect once", async () => {
  env();
  const store = new InMemoryIdempotencyStore();
  let applied = 0;
  let unblock: () => void = () => {};
  const gate = new Promise<void>((resolve) => {
    unblock = resolve;
  });
  const onCounts = async () => {
    applied += 1;
    await gate; // hold the first delivery in flight while the second arrives
  };

  const a = handleSquareWebhookRequest(inventoryDelivery("evt_c1"), store, onCounts);
  const b = handleSquareWebhookRequest(inventoryDelivery("evt_c1"), store, onCounts);
  // The duplicate must answer while the first is still in flight. Bounded, so
  // an implementation that lets both deliveries into the side effect fails
  // here instead of hanging on the gate.
  const early = await Promise.race([
    b,
    new Promise<"timeout">((resolve) => setTimeout(() => resolve("timeout"), 2000)),
  ]);
  unblock();
  const first = await a;
  const second = early === "timeout" ? await b : early;

  assert.notEqual(early, "timeout", "the duplicate must not wait on the in-flight side effect");
  assert.equal(first.status, 200);
  assert.equal(second.status, 200);
  assert.equal(applied, 1, "only the delivery that won the claim runs the side effect");
});

test("InMemoryIdempotencyStore.claim is set-if-absent and release re-opens it", async () => {
  const store = new InMemoryIdempotencyStore();
  assert.equal(await store.claim("e"), true);
  assert.equal(await store.claim("e"), false);
  await store.release("e");
  assert.equal(await store.claim("e"), true);
  await store.remember("e");
  assert.equal(await store.claim("e"), false);
});
