# Define and implement a degraded mode for every critical dependency

**Status:** Pattern
**Domain:** Backend resilience
**Applies to:** `backend-engineering`

---

## Why this exists

When a downstream dependency is unavailable, the default behavior of most services is to propagate the error up until the entire user-facing action fails. Graceful degradation says: decide in advance what a partial result looks like, and serve that instead. A product page that loads without a recommendation widget is far better than a blank 500 for all users while the recommendation service is restarting. Degradation is a design decision, not an accident of error handling.

## How to apply

For every outbound call, define the three-state contract: full response, degraded fallback, or hard fail. Implement the fallback before shipping; "we'll add it later" does not survive an incident.

```typescript
async function getProductPageData(productId: string): Promise<ProductPage> {
  const [product, recommendations] = await Promise.allSettled([
    productService.get(productId),      // required — fail hard if unavailable
    recommendationService.get(productId) // optional — degrade if unavailable
  ]);

  if (product.status === 'rejected') throw product.reason; // hard dependency

  return {
    product: product.value,
    recommendations: recommendations.status === 'fulfilled'
      ? recommendations.value
      : []   // degraded: empty, not an error
  };
}
```

**Do:**
- Classify every dependency as *required* (fail the request) or *optional* (degrade).
- Return a usable (not empty-shell) response for degraded cases — document what is absent.
- Pair degradation with circuit breakers so a known-down dependency is not called on every request.
- Log degraded responses at WARN with the dependency name so operations knows the scope.

**Don't:**
- Silently omit required data without indicating to the caller that something is missing.
- Treat all dependencies as required — that's the default no-degradation behavior you're replacing.
- Return stale cached data as a degraded response without labeling it as such.

## Edge cases / when the rule does NOT apply

Payment processing, identity verification, and data-mutation endpoints typically cannot degrade — a partial result is worse than a clear error. Degrade only where a partial result is genuinely acceptable to the user.

## See also

- [`../agents/backend-reliability-engineer.md`](../agents/backend-reliability-engineer.md) — owns the resilience posture.
- [`./use-circuit-breakers-for-downstream-dependencies.md`](./use-circuit-breakers-for-downstream-dependencies.md) — circuit breakers detect the "down" state that triggers degradation.

## Provenance

Standard distributed-systems design principle (Michael Nygard's _Release It!_, Netflix Hystrix fallback design). Codifies the `backend-reliability-engineer` responsibility for defined degraded modes.

---

_Last reviewed: 2026-06-05 by `claude`_
