# Never cache without an invalidation story

Before adding a cache, decide what is cacheable, the invalidation trigger (what write makes it stale), the TTL safety net, and the stampede protection for hot keys. A cache with no invalidation plan silently serves stale data and turns a correctness question into an intermittent, hard-to-reproduce bug. The invalidation design is the cache design.
