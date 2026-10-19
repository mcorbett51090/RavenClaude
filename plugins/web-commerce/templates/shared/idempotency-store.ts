/**
 * Exactly-once webhook handling. Providers retry deliveries and do NOT
 * guarantee ordering (CLAUDE.md §2 #4), so every track de-duplicates by
 * provider event id BEFORE running side effects.
 *
 * Static-tier note (CLAUDE.md §2 #3): a static site has no server to hold this
 * state. The static templates back this interface with an EXTERNAL KV
 * (Upstash / Vercel KV) reached from a thin serverless function — never
 * browser state and never a process-memory Set, which a recycled serverless
 * invocation would lose (re-processing the event, double-charging or
 * double-decrementing inventory).
 *
 * Handlers use the claim lifecycle, never check-then-mark:
 *
 *   if (!(await store.claim(id))) return 200;      // duplicate or in flight
 *   try { await sideEffects(); await store.remember(id); }
 *   catch (e) { await store.release(id); throw e; } // provider retries -> runs again
 *
 * `seen()` then `remember()` BEFORE the side effects lost the event when the
 * side effect threw (the retry found it "seen" and was acknowledged without
 * the work), and two concurrent deliveries could both pass `seen()` and both
 * run the side effects. `claim()` is one atomic set-if-absent, so exactly one
 * delivery wins; `release()` lets the retry of a failed one run again.
 */
export interface IdempotencyStore {
  /** True if this event id is claimed (in flight) or already processed. */
  seen(eventId: string): Promise<boolean>;
  /**
   * Mark an event id processed (the "done" marker). Called AFTER the side
   * effects succeed; it replaces the shorter-lived claim from `claim()`.
   */
  remember(eventId: string, ttlSeconds?: number): Promise<void>;
  /**
   * Atomically claim an event id for processing (set-if-absent). Resolves true
   * when THIS caller won the claim and must do the work, false when the id is
   * already claimed or done (acknowledge without re-running side effects).
   * A KV-backed claim is a lease (`leaseSeconds`) so a worker that crashes
   * mid-flight does not hold the event forever: once the lease lapses, the
   * provider's next retry can claim it.
   */
  claim(eventId: string, leaseSeconds?: number): Promise<boolean>;
  /** Drop a claim whose side effects failed, so the provider's retry runs them again. */
  release(eventId: string): Promise<void>;
}

/**
 * Reference in-memory implementation — for LOCAL TESTS ONLY. Do not ship this
 * to production: a serverless function can be recycled between invocations,
 * losing the Set and re-processing events. Production tiers use a KV-backed
 * IdempotencyStore implementing the same interface.
 *
 * `claim()` is atomic here because the check and the insert run with no
 * `await` between them (one JS turn). Leases are not modelled: a claim stays
 * until `remember()` or `release()`.
 */
export class InMemoryIdempotencyStore implements IdempotencyStore {
  private readonly ids = new Set<string>();

  async seen(eventId: string): Promise<boolean> {
    return this.ids.has(eventId);
  }

  async remember(eventId: string): Promise<void> {
    this.ids.add(eventId);
  }

  async claim(eventId: string): Promise<boolean> {
    if (this.ids.has(eventId)) return false;
    this.ids.add(eventId);
    return true;
  }

  async release(eventId: string): Promise<void> {
    this.ids.delete(eventId);
  }
}
