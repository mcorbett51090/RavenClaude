import type { IdempotencyStore } from "../../shared/idempotency-store.ts";

/**
 * The minimal surface every popular edge KV exposes (Cloudflare Workers KV,
 * Upstash Redis REST client, `@vercel/kv`) -- get/set with an optional TTL.
 * Bind your platform's client to this shape rather than importing it
 * directly here, so this file carries zero runtime dependencies.
 */
export interface EdgeKv {
  get(key: string): Promise<string | null>;
  set(key: string, value: string, ttlSeconds?: number): Promise<void>;
}

const EVENT_KEY_PREFIX = "square:webhook-event:";

const SEVEN_DAYS_SECONDS = 60 * 60 * 24 * 7;

/**
 * KV-backed IdempotencyStore for the static tier's serverless webhook
 * function. A truly static site has no long-lived process, so a
 * process-memory Set would be wiped on the next cold start and every event
 * would look "new" again -- this is the external state a static tier
 * genuinely needs (CLAUDE.md §2 #3).
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
    await this.kv.set(EVENT_KEY_PREFIX + eventId, "1", ttlSeconds ?? this.defaultTtlSeconds);
  }
}
