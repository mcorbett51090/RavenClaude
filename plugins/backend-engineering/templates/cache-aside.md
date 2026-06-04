# Cache-aside (pattern)

```
get(key):
  v = cache.get(key)
  if v is not None: return v
  with single_flight(key):           # stampede protection
    v = cache.get(key)
    if v is None:
      v = db.load(key)
      cache.set(key, v, ttl=SAFETY_TTL)
  return v

write(key, val):
  db.save(key, val)
  cache.delete(key)                  # invalidation trigger
```
