# Encode performance budgets as tests that fail on regressions

**Status:** Pattern
**Domain:** Test strategy / performance
**Applies to:** `qa-test-automation`

---

## Why this exists

Performance regressions are invisible without a test: an API endpoint that degrades from 50ms to 800ms over ten incremental commits is never caught because no individual commit is obviously the culprit and no CI gate was watching the metric. By the time a user complains or a latency SLO burns, the root cause is buried. A performance budget test — a test that fails if the P95 response time, bundle size, memory footprint, or startup time exceeds a threshold — makes performance a first-class gate just like a functional assertion.

## How to apply

Define the performance budget for the most critical operations and encode it as a passing/failing assertion in the test suite.

```typescript
// Playwright: page performance budget test
test('homepage loads within performance budget', async ({ page }) => {
  const response = await page.goto('/');
  const timing = await page.evaluate(() => {
    const nav = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    return {
      ttfb: nav.responseStart - nav.requestStart,
      domInteractive: nav.domInteractive,
      fullyLoaded: nav.loadEventEnd,
    };
  });

  // Performance budgets — fail the test if exceeded
  expect(timing.ttfb).toBeLessThan(200);           // 200ms TTFB
  expect(timing.domInteractive).toBeLessThan(1000); // 1s DOM interactive
  expect(timing.fullyLoaded).toBeLessThan(3000);    // 3s fully loaded
});
```

```python
# API: assert response time budget in integration test
def test_product_search_responds_within_budget(client):
    import time
    start = time.monotonic()
    response = client.get("/search?q=laptop")
    elapsed_ms = (time.monotonic() - start) * 1000

    assert response.status_code == 200
    assert elapsed_ms < 300, f"Search took {elapsed_ms:.0f}ms — budget is 300ms"
```

```yaml
# CI: bundle size budget (Next.js / Webpack)
# next.config.js
experimental:
  bundlePagesExternals: true
# Or use bundlewatch in CI:
# bundlewatch --config bundlewatch.config.json
# bundlewatch.config.json: { "files": [{"path": ".next/static/chunks/**.js", "maxSize": "250kB"}] }
```

**Do:**
- Set budgets based on user-experience research (Core Web Vitals, SLO latency targets) not arbitrary numbers.
- Run performance budget tests on a dedicated, quiet CI runner to reduce variance.
- Add a comment explaining the budget origin ("P95 from SLO target; agreed with product on 2026-Q1 planning").

**Don't:**
- Set budgets so tight that they flap on every run; use P95 thresholds, not absolute minimums.
- Run performance assertions in the same CI job as unit tests without isolating them from resource contention.
- Use performance tests as a substitute for SLOs — they catch regressions in CI; SLOs catch drift in production.

## Edge cases / when the rule does NOT apply

Services that are intentionally slow (batch jobs, report generation) should use throughput and completion-time budgets rather than latency budgets. The same principle applies — encode the expected behavior and fail on regression.

## See also

- [`../agents/test-strategy-architect.md`](../agents/test-strategy-architect.md) — owns the test strategy and performance-budget tier selection.
- [`./risk-based-test-prioritization.md`](./risk-based-test-prioritization.md) — performance budget tests apply to high-risk, user-facing paths first.

## Provenance

Codifies the Web Performance Budget concept (web.dev/performance-budgets) and the Playwright performance testing patterns. Aligned with the observability-sre SLO approach applied to CI.

---

_Last reviewed: 2026-06-05 by `claude`_
