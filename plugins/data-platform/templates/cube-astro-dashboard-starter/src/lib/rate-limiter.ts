// ---------------------------------------------------------------------------
// Shared per-process rate limiter — Astro-side twin of the Next.js starter's
// lib/rate-limiter.ts (factored out FORGE dashboard-top1pct P2-14,
// 2026-09-03, after security review found the export route had silently
// lost the limiter its cheaper sibling (cube-token) carries).
//
// Naive per-process limiter — fine for a single-instance dev/demo
// deployment, MUST be replaced with a shared store (Redis, etc.) before
// running more than one instance.
// ---------------------------------------------------------------------------

const DEFAULT_SWEEP_INTERVAL_MS = 5 * 60_000; // 5 min

export interface RateLimiter {
  isLimited(key: string): boolean;
}

/** Each call site gets its OWN limiter instance (its own Map, its own ceiling). */
export function createRateLimiter(
  maxRequests: number,
  windowMs: number,
  sweepIntervalMs: number = DEFAULT_SWEEP_INTERVAL_MS,
): RateLimiter {
  const requestLog = new Map<string, number[]>();
  let lastSweptAtMs = 0;

  function sweepStaleEntries(now: number): void {
    if (now - lastSweptAtMs < sweepIntervalMs) return;
    lastSweptAtMs = now;
    for (const [key, timestamps] of requestLog) {
      const fresh = timestamps.filter((t) => now - t < windowMs);
      if (fresh.length === 0) {
        requestLog.delete(key);
      } else if (fresh.length !== timestamps.length) {
        requestLog.set(key, fresh);
      }
    }
  }

  return {
    isLimited(key: string): boolean {
      const now = Date.now();
      sweepStaleEntries(now);
      const timestamps = (requestLog.get(key) ?? []).filter((t) => now - t < windowMs);
      if (timestamps.length > maxRequests) {
        requestLog.set(key, timestamps);
        return true;
      }
      timestamps.push(now);
      requestLog.set(key, timestamps);
      return timestamps.length > maxRequests;
    },
  };
}
