// ---------------------------------------------------------------------------
// Shared per-process rate limiter (factored out FORGE dashboard-top1pct
// P2-14, 2026-09-03, after security review found the export route had
// silently lost the limiter its cheaper sibling (cube-token) carries —
// see best-practices/export-runs-under-the-viewer-scope-never-a-service-
// identity.md's sibling finding). Previously this exact logic was
// hand-duplicated per route; every future fix (the P0-5 sweep/early-return
// fixes) now needs to land in ONE file, not N.
//
// Naive per-process limiter — fine for a single-instance dev/demo
// deployment, MUST be replaced with a shared store (Redis, etc.) before
// running more than one instance, since each instance would otherwise
// track its own independent counter. Same caveat every consumer of this
// module already carried individually.
// ---------------------------------------------------------------------------

const DEFAULT_SWEEP_INTERVAL_MS = 5 * 60_000; // 5 min

export interface RateLimiter {
  /** Records this call against `key` and returns true if `key` is over the ceiling. */
  isLimited(key: string): boolean;
}

/**
 * Each call site gets its OWN limiter instance (its own Map, its own
 * ceiling) — the export route intentionally uses a tighter ceiling than
 * the token route, since an export is not a per-widget operation.
 */
export function createRateLimiter(
  maxRequests: number,
  windowMs: number,
  sweepIntervalMs: number = DEFAULT_SWEEP_INTERVAL_MS,
): RateLimiter {
  const requestLog = new Map<string, number[]>();
  let lastSweptAtMs = 0;

  // Bounded eviction (FORGE dashboard-top1pct P0-5): requestLog grew one
  // entry per distinct key, forever, with no eviction — a slow memory leak.
  // Every call opportunistically sweeps stale keys (an empty timestamps
  // array after the window filter) at most once per sweepIntervalMs, so the
  // map's size tracks active keys in the current window, not total keys
  // ever seen.
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
      // Return BEFORE pushing once already over the limit (P0-5 fix): the
      // sweep bounds the number of KEYS, but a caller already past the
      // ceiling kept appending to its OWN array for the rest of the window
      // while receiving 429s — those entries are fresh, not stale, so the
      // sweep can't reclaim them. Returning early here caps each key's
      // array at maxRequests + 1 regardless of how many more requests
      // arrive.
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
