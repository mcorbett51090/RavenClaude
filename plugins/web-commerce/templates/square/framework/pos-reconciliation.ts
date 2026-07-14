import type { IdempotencyStore } from "../../shared/idempotency-store.ts";
import type { SquareInventoryCountPayload, SquareWebhookEnvelope } from "./webhook.ts";
import { extractInventoryCounts } from "./webhook.ts";

export interface StockRecord {
  quantity: number;
  /** Square's `calculated_at` for this record -- the authoritative ordering signal. */
  calculatedAt: string;
}

/**
 * A read-only local mirror of Square's inventory ledger. Square is the
 * ONLY source of truth for catalog + inventory on this track
 * (`capabilities.catalogSourceOfTruth === 'provider'`) -- this reconciler
 * NEVER writes back to Square. Square explicitly warns that bidirectional
 * sync between an external system and Square's catalog is risky
 * (concurrency, merge conflicts, duplicates, deletes) and out of scope; see
 * knowledge/provider-tracks-2026.md §4
 * (developer.squareup.com/docs/catalog-api/sync-with-external-system,
 * retrieved 2026-07-13).
 *
 * Square's webhooks guarantee neither exactly-once delivery nor delivery
 * order, so this class enforces both correctness properties itself:
 *
 *   1. **Exactly-once** -- every apply path de-dupes by `event_id` via the
 *      shared `IdempotencyStore` before touching the ledger. A replayed
 *      delivery of the same event is a no-op.
 *   2. **Convergence under out-of-order delivery** -- per catalog-object /
 *      location / state key, an incoming count whose `calculated_at` is
 *      OLDER than the last-applied one for that key is ignored rather than
 *      regressing the local mirror. The mirror always converges on
 *      Square's most recent known state, regardless of the order webhooks
 *      happen to arrive in.
 */
export class PosReconciler {
  private readonly stock = new Map<string, StockRecord>();
  private readonly idempotency: IdempotencyStore;
  private totalDecrementedUnits = 0;

  constructor(idempotency: IdempotencyStore) {
    this.idempotency = idempotency;
  }

  private key(catalogObjectId: string, locationId: string, state: string): string {
    return `${catalogObjectId}::${locationId}::${state}`;
  }

  /** Current known quantity for a catalog object at a location/state, or `undefined` if never reconciled. */
  getQuantity(catalogObjectId: string, locationId: string, state = "IN_STOCK"): number | undefined {
    return this.stock.get(this.key(catalogObjectId, locationId, state))?.quantity;
  }

  /** Cumulative units decremented across every count applied so far -- exposed for tests/observability, never double-counted on a replay. */
  get decrementedUnits(): number {
    return this.totalDecrementedUnits;
  }

  /**
   * Apply ONE verified `inventory.count.updated` webhook envelope.
   * De-dupes by `event_id` first; only on a fresh event does it walk the
   * envelope's inventory counts and reconcile the local mirror.
   */
  async applyInventoryEvent(envelope: SquareWebhookEnvelope): Promise<void> {
    if (await this.idempotency.seen(envelope.event_id)) {
      return; // exact-duplicate delivery -- no-op, never re-applied
    }
    await this.idempotency.remember(envelope.event_id);

    for (const count of extractInventoryCounts(envelope)) {
      this.applyCount(count);
    }
  }

  /**
   * Reconcile a single Square inventory count into the local mirror.
   * Exposed separately from `applyInventoryEvent` so `catalog.version.
   * updated` handling (which PULLS current counts via the Catalog/Inventory
   * API rather than reading them off a webhook body) can feed the same
   * convergence logic.
   */
  applyCount(count: SquareInventoryCountPayload): void {
    const k = this.key(count.catalog_object_id, count.location_id, count.state);
    const existing = this.stock.get(k);
    const quantity = Number.parseFloat(count.quantity);

    if (existing && existing.calculatedAt > count.calculated_at) {
      // Stale/out-of-order delivery for this key: a newer count already
      // landed locally. Converge on the newer value -- do not regress.
      return;
    }

    if (existing && quantity < existing.quantity) {
      this.totalDecrementedUnits += existing.quantity - quantity;
    }

    this.stock.set(k, { quantity, calculatedAt: count.calculated_at });
  }

  /**
   * Reconcile on `catalog.version.updated`. That event's payload carries no
   * object data -- only the fact that the catalog version changed -- so the
   * correct response is to PULL just the changed objects (Square's
   * `SearchCatalogObjects` with `begin_time`/a version cursor) and apply
   * them locally; this reconciler never pushes local edits back (one-way
   * sync, per the class doc comment above).
   *
   * The actual Catalog API call is passed in as `fetchChangedObjects` so
   * this module has zero network dependency and stays unit-testable; a
   * production wiring calls Square's Catalog API here.
   */
  async applyCatalogVersionEvent(
    envelope: SquareWebhookEnvelope,
    lastKnownVersion: string | undefined,
    fetchChangedObjects: (sinceVersion: string | undefined) => Promise<unknown[]>,
    applyChangedObjects: (objects: unknown[]) => void,
  ): Promise<void> {
    if (await this.idempotency.seen(envelope.event_id)) {
      return;
    }
    await this.idempotency.remember(envelope.event_id);

    const changed = await fetchChangedObjects(lastKnownVersion);
    applyChangedObjects(changed);
  }
}
