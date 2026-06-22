# Object-cache the expensive queries

**Status:** Pattern
**Domain:** Performance / caching
**Applies to:** `wordpress-cms-engineering`

---

## Why this exists

Repeating an expensive query or computation on every request wastes the database and PHP time. A **persistent** object cache (Redis/Memcached behind `wp_cache_*` and transients) stores the result and serves it from memory. Note: without a persistent backend, the default object cache is non-persistent and won't survive the request — so the first job is wiring a real backend.

## How to apply

```php
function myplugin_top_authors() {
    $key   = 'myplugin_top_authors';
    $value = wp_cache_get( $key, 'myplugin' );
    if ( false === $value ) {
        $value = myplugin_compute_top_authors(); // the expensive query
        wp_cache_set( $key, $value, 'myplugin', 5 * MINUTE_IN_SECONDS );
    }
    return $value;
}
// Cross-request, DB-backed when no object cache: set_transient / get_transient.
```

**Do:**
- Cache expensive query results with a sensible TTL; invalidate on write.
- Use a persistent backend (Redis/Memcached); watch the hit rate.
- Bound `WP_Query` (no reflexive `posts_per_page = -1`).

**Don't:**
- Cache to mask an unbounded or un-indexed query — fix the query too.
- Cache user-specific data under a shared key (data leak).

## Edge cases / when the rule does NOT apply

Cheap, already-cached core calls (`get_option`, `get_post`) don't need re-wrapping. Highly volatile data with no tolerance for staleness may not be cacheable.

## See also

- [`./enqueue-scripts-with-versioned-handles.md`](./enqueue-scripts-with-versioned-handles.md)
- [`../skills/performance-and-caching/SKILL.md`](../skills/performance-and-caching/SKILL.md)

## Provenance

WordPress Plugin Handbook (Transients / Object Cache). Codifies `wordpress-ops-engineer` house opinion ("a persistent object cache is the highest-leverage win").

---

_Last reviewed: 2026-06-22 by `claude`_
