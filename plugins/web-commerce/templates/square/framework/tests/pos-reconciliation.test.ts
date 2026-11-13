import { test } from "node:test";
import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import { InMemoryIdempotencyStore } from "../../../shared/idempotency-store.ts";
import { PosReconciler } from "../pos-reconciliation.ts";
import { verifyAndParseSquareWebhook } from "../webhook.ts";
import type { SquareWebhookEnvelope } from "../webhook.ts";

const SIGNATURE_KEY = "test-signature-key";
const NOTIFICATION_URL = "https://example.test/api/webhooks/square";

/** A signed `catalog.version.updated` delivery, as Square sends it. */
function signedCatalogDelivery(eventId: string) {
  const rawBody = JSON.stringify({
    merchant_id: "M",
    type: "catalog.version.updated",
    event_id: eventId,
    created_at: "2026-10-19T10:00:00Z",
    data: { type: "catalog_version", id: "", object: { catalog_version: { updated_at: "x" } } },
  });
  const signature = createHmac("sha256", SIGNATURE_KEY)
    .update(NOTIFICATION_URL + rawBody)
    .digest("base64");
  return { rawBody, headers: { "x-square-hmacsha256-signature": signature } };
}

/** Build a minimal verified `inventory.count.updated` envelope for one catalog object. */
function inventoryEvent(
  eventId: string,
  count: { quantity: string; calculatedAt: string },
): SquareWebhookEnvelope {
  return {
    merchant_id: "M",
    type: "inventory.count.updated",
    event_id: eventId,
    created_at: count.calculatedAt,
    data: {
      type: "inventory",
      id: "inv",
      object: {
        inventory_counts: [
          {
            catalog_object_id: "A",
            location_id: "L",
            state: "IN_STOCK",
            quantity: count.quantity,
            calculated_at: count.calculatedAt,
          },
        ],
      },
    },
  };
}

// Rubric #3 / CLAUDE.md §2 #4 — Square retries webhook deliveries and does not
// guarantee exactly-once. A replayed event id MUST NOT re-apply the decrement.
test("a duplicate inventory webhook does not double-decrement stock", async () => {
  const reconciler = new PosReconciler(new InMemoryIdempotencyStore());

  await reconciler.applyInventoryEvent(
    inventoryEvent("e1", { quantity: "10", calculatedAt: "2026-07-13T10:00:00Z" }),
  );
  await reconciler.applyInventoryEvent(
    inventoryEvent("e2", { quantity: "7", calculatedAt: "2026-07-13T10:05:00Z" }),
  );

  assert.equal(reconciler.getQuantity("A", "L"), 7);
  assert.equal(reconciler.decrementedUnits, 3);

  // Replay e2 — must be a no-op, NOT a second decrement to 4.
  await reconciler.applyInventoryEvent(
    inventoryEvent("e2", { quantity: "7", calculatedAt: "2026-07-13T10:05:00Z" }),
  );

  assert.equal(reconciler.getQuantity("A", "L"), 7);
  assert.equal(reconciler.decrementedUnits, 3);
});

// Square does not guarantee delivery order. An older `calculated_at` arriving
// late MUST NOT regress the mirror — it converges on Square's newest state.
test("out-of-order delivery converges on the newest calculated_at", async () => {
  const reconciler = new PosReconciler(new InMemoryIdempotencyStore());

  // The newer count (qty 5 @ 10:05) arrives first...
  await reconciler.applyInventoryEvent(
    inventoryEvent("e2", { quantity: "5", calculatedAt: "2026-07-13T10:05:00Z" }),
  );
  // ...then an older count (qty 9 @ 10:00) arrives late — it must be ignored.
  await reconciler.applyInventoryEvent(
    inventoryEvent("e1", { quantity: "9", calculatedAt: "2026-07-13T10:00:00Z" }),
  );

  assert.equal(reconciler.getQuantity("A", "L"), 5);
});

// domainplugins-3 (repo-review 2026-10-19): the class doc says the reconciler's
// store may be the SAME instance the webhook layer uses. The webhook layer
// claims the raw event_id first, so the catalog path must dedupe on its own
// namespaced key or it returns before the pull, every time.
test("catalog.version.updated runs the pull when the webhook layer shares the store", async () => {
  process.env.SQUARE_WEBHOOK_SIGNATURE_KEY = SIGNATURE_KEY;
  process.env.SQUARE_WEBHOOK_NOTIFICATION_URL = NOTIFICATION_URL;
  const store = new InMemoryIdempotencyStore();
  const reconciler = new PosReconciler(store);
  let fetches = 0;
  const fetchChanged = async () => {
    fetches += 1;
    return [{ id: "obj" }];
  };

  const event = await verifyAndParseSquareWebhook(signedCatalogDelivery("evt_cat_1"), store);
  assert.equal(event.type, "catalog.updated");
  const envelope = event.raw as SquareWebhookEnvelope;
  await reconciler.applyCatalogVersionEvent(envelope, undefined, fetchChanged, () => {});
  assert.equal(fetches, 1, "the catalog pull must run once for a fresh event");

  // Square redelivers the same event: the reconciler's own dedup skips it.
  await reconciler.applyCatalogVersionEvent(envelope, undefined, fetchChanged, () => {});
  assert.equal(fetches, 1, "a redelivery must not pull again");
});

test("a failed catalog pull is not remembered, so the redelivery retries it", async () => {
  const store = new InMemoryIdempotencyStore();
  const reconciler = new PosReconciler(store);
  const envelope: SquareWebhookEnvelope = {
    merchant_id: "M",
    type: "catalog.version.updated",
    event_id: "evt_cat_2",
    created_at: "2026-10-19T10:00:00Z",
    data: { type: "catalog_version", id: "", object: {} },
  };
  let fetches = 0;
  const flaky = async () => {
    fetches += 1;
    if (fetches === 1) throw new Error("transient Catalog API error");
    return [];
  };

  await assert.rejects(() =>
    reconciler.applyCatalogVersionEvent(envelope, undefined, flaky, () => {}),
  );
  await reconciler.applyCatalogVersionEvent(envelope, undefined, flaky, () => {});
  assert.equal(fetches, 2, "the redelivery must retry the pull after a failure");
});
