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
 */
export interface IdempotencyStore {
  /** True if this event id was already processed and should be skipped. */
  seen(eventId: string): Promise<boolean>;
  /** Mark an event id processed. Prefer an atomic set-if-absent where the backend allows. */
  remember(eventId: string, ttlSeconds?: number): Promise<void>;
}

/**
 * Reference in-memory implementation — for LOCAL TESTS ONLY. Do not ship this
 * to production: a serverless function can be recycled between invocations,
 * losing the Set and re-processing events. Production tiers use a KV-backed
 * IdempotencyStore implementing the same interface.
 */
export class InMemoryIdempotencyStore implements IdempotencyStore {
  private readonly ids = new Set<string>();

  async seen(eventId: string): Promise<boolean> {
    return this.ids.has(eventId);
  }

  async remember(eventId: string): Promise<void> {
    this.ids.add(eventId);
  }
}
