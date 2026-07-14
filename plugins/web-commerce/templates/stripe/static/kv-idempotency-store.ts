/**
 * KV-backed IdempotencyStore for the Stripe STATIC tier.
 *
 * A literally-static site's webhook receiver is a serverless function that
 * can be recycled (or run as a fresh cold start) between deliveries — an
 * in-process Set (see ../../shared/idempotency-store's InMemoryIdempotencyStore)
 * would silently lose state and re-run side effects on a Stripe retry
 * (CLAUDE.md §2 #3). This file backs the shared IdempotencyStore interface
 * with an EXTERNAL key-value store reached over HTTP.
 *
 * KV OPTIONS (pick one, both expose the same REST-over-HTTP shape used below):
 *   - Upstash Redis  — https://upstash.com/docs/redis/features/restapi (2026-07-13)
 *     env: UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN
 *   - Vercel KV      — Vercel-managed Upstash; same REST API, different env
 *     var names (KV_REST_API_URL, KV_REST_API_TOKEN) — see
 *     https://vercel.com/docs/storage/vercel-kv (2026-07-13)
 *
 * This file talks to Upstash's REST API directly via `fetch` — no SDK
 * dependency, so it works unmodified in a Cloudflare Worker, a Vercel Edge
 * Function, or a Netlify Edge Function. Point `KV_REST_API_URL` /
 * `KV_REST_API_TOKEN` at either provider; the wire protocol is identical.
 */

import type { IdempotencyStore } from "../../shared/idempotency-store";

const DEFAULT_TTL_SECONDS = 60 * 60 * 24; // 24h — comfortably beyond Stripe's retry window.

export interface KvClientConfig {
  /** REST endpoint base URL, e.g. UPSTASH_REDIS_REST_URL or KV_REST_API_URL. */
  restUrl: string;
  /** Bearer token, e.g. UPSTASH_REDIS_REST_TOKEN or KV_REST_API_TOKEN. */
  restToken: string;
}

export class KvIdempotencyStore implements IdempotencyStore {
  constructor(private readonly config: KvClientConfig) {}

  async seen(eventId: string): Promise<boolean> {
    const res = await this.request(["GET", this.key(eventId)]);
    return res.result !== null;
  }

  async remember(eventId: string, ttlSeconds: number = DEFAULT_TTL_SECONDS): Promise<void> {
    // SET key value EX ttl — a plain SET, not SETNX: the caller is expected to
    // call seen() first (see webhook.ts's dedup-then-remember order). A race
    // between two concurrent deliveries of the SAME event is rare (Stripe
    // de-dupes on its side too) and merely re-runs remember(), which is
    // harmless — it is the SIDE EFFECT re-run that dedup guards against.
    await this.request(["SET", this.key(eventId), "1", "EX", String(ttlSeconds)]);
  }

  private key(eventId: string): string {
    return `stripe:webhook-event:${eventId}`;
  }

  private async request(command: string[]): Promise<{ result: unknown }> {
    const response = await fetch(this.config.restUrl, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.config.restToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(command),
    });
    if (!response.ok) {
      throw new Error(`KV request failed: ${response.status} ${await response.text()}`);
    }
    return response.json() as Promise<{ result: unknown }>;
  }
}

/**
 * Build a KvIdempotencyStore from env vars, accepting either the Upstash or
 * the Vercel KV naming convention (same REST wire protocol either way).
 */
export function createKvIdempotencyStoreFromEnv(): KvIdempotencyStore {
  const restUrl = process.env.UPSTASH_REDIS_REST_URL ?? process.env.KV_REST_API_URL;
  const restToken = process.env.UPSTASH_REDIS_REST_TOKEN ?? process.env.KV_REST_API_TOKEN;
  if (!restUrl || !restToken) {
    throw new Error(
      "Missing KV credentials: set UPSTASH_REDIS_REST_URL/UPSTASH_REDIS_REST_TOKEN " +
        "(or KV_REST_API_URL/KV_REST_API_TOKEN for Vercel KV).",
    );
  }
  return new KvIdempotencyStore({ restUrl, restToken });
}
