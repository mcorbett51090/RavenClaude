---
name: performance-and-caching
description: "Make WordPress fast with layered caching: a full-page cache for anonymous traffic, a persistent object cache (Redis/Memcached behind wp_cache_*/transients) for dynamic work, expensive queries cached, plus profiling to find the real bottleneck before adding layers."
---

# Performance and Caching

Cache in layers, and measure before you add one.

## The caching layers
| Layer | Serves | How |
|---|---|---|
| **Page cache** | Anonymous full-page HTML, before PHP runs | Host/CDN page cache, a caching plugin, or a reverse proxy |
| **Object cache (persistent)** | Repeated DB work for logged-in/dynamic requests | Redis/Memcached behind `wp_cache_*` + transients |
| **Fragment / transient** | Specific expensive computations | `set_transient` / `wp_cache_set` with a sane TTL |
| **Browser/CDN asset cache** | Static assets | Versioned handles ([`../../best-practices/enqueue-scripts-with-versioned-handles.md`](../../best-practices/enqueue-scripts-with-versioned-handles.md)) + far-future headers |

The default object cache is **non-persistent** — it doesn't survive the request. A real persistent backend (Redis/Memcached) is the highest-leverage win for anything dynamic.

## Cache the expensive queries
- Identify slow/repeated queries (slow query log, a profiler), then cache their results in the object cache rather than recomputing per request — see [`../../best-practices/object-cache-for-expensive-queries.md`](../../best-practices/object-cache-for-expensive-queries.md).
- Bound `WP_Query` results; avoid `posts_per_page = -1` and meta N+1.

## Measure first
- Profile to find the **actual** bottleneck (DB? PHP? assets? external API?) before adding a layer or a plugin. The measurement selects the fix.
- Watch the object-cache **hit rate** — a low rate means the cache isn't doing its job.

## Anti-patterns
- Stacking caching plugins hoping one sticks (they conflict).
- A page cache that caches logged-in/personalized responses (leaks data).
- Adding caching to mask an unbounded query instead of fixing the query.

Traverse the caching-layer tree in [`../../knowledge/wordpress-decision-trees.md`](../../knowledge/wordpress-decision-trees.md). Infra-level budget (CDN, host sizing, load tests) is a `performance-engineering` seam.
