import { test } from "node:test";
import assert from "node:assert/strict";
import { InMemoryIdempotencyStore } from "../../../shared/idempotency-store.ts";
import { PosReconciler } from "../pos-reconciliation.ts";
import type { SquareWebhookEnvelope } from "../webhook.ts";

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
