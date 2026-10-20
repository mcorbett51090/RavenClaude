import type { IdempotencyStore } from "../../shared/idempotency-store.ts";

/**
 * The minimal surface the idempotency store needs from an edge KV: get/set
 * with an optional TTL, an ATOMIC set-if-absent, and delete. Bind your
 * platform's client to this shape rather than importing it directly here, so
 * this file carries zero runtime dependencies.
 *
 * `setIfAbsent` must be atomic, or two concurrent deliveries of one event can
 * both win the claim and both run the side effects:
 *   - Upstash Redis REST: `SET key value NX EX ttl` (reply "OK" when written,
 *     null when the key exists) [verify-at-use].
 *   - `@vercel/kv`: `kv.set(key, value, { nx: true, ex: ttl })` resolves "OK"
 *     when written, null otherwise [verify-at-use].
 *   - Cloudflare Workers KV is eventually consistent and has no atomic
 *     set-if-absent; back the claim with a Durable Object or D1 there.
 */
export interface EdgeKv {
  get(key: string): Promise<string | null>;
  set(key: string, value: string, ttlSeconds?: number): Promise<void>;
  /** Write `key` only if it does not exist; resolve true when this call wrote it. */
  setIfAbsent(key: string, value: string, ttlSeconds?: number): Promise<boolean>;
  delete(key: string): Promise<void>;
}

const EVENT_KEY_PREFIX = "square:webhook-event:";

const SEVEN_DAYS_SECONDS = 60 * 60 * 24 * 7;

/** How long an in-flight claim holds before a crashed worker's event can be retried. */
const DEFAULT_LEASE_SECONDS = 60 * 10;

/**
 * KV-backed IdempotencyStore for the static tier's serverless webhook
 * function. A truly static site has no long-lived process, so a
 * process-memory Set would be wiped on the next cold start and every event
 * would look "new" again -- this is the external state a static tier
 * genuinely needs (CLAUDE.md §2 #3).
 *
 * The dedup decision is `claim()` (one atomic set-if-absent), never a
 * get-then-set; `remember()` overwrites the claim with the long-lived "done"
 * marker once the side effects succeed, and `release()` deletes a claim whose
 * side effects failed so Square's retry runs them again.
 */
export class KvIdempotencyStore implements IdempotencyStore {
  private readonly kv: EdgeKv;
  private readonly defaultTtlSeconds: number;

  constructor(kv: EdgeKv, defaultTtlSeconds: number = SEVEN_DAYS_SECONDS) {
    this.kv = kv;
    this.defaultTtlSeconds = defaultTtlSeconds;
  }

  async seen(eventId: string): Promise<boolean> {
    return (await this.kv.get(EVENT_KEY_PREFIX + eventId)) !== null;
  }

  async remember(eventId: string, ttlSeconds?: number): Promise<void> {
    await this.kv.set(EVENT_KEY_PREFIX + eventId, "done", ttlSeconds ?? this.defaultTtlSeconds);
  }

  async claim(eventId: string, leaseSeconds: number = DEFAULT_LEASE_SECONDS): Promise<boolean> {
    return this.kv.setIfAbsent(EVENT_KEY_PREFIX + eventId, "processing", leaseSeconds);
  }

  async release(eventId: string): Promise<void> {
    await this.kv.delete(EVENT_KEY_PREFIX + eventId);
  }
}
